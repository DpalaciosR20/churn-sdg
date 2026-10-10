import json
import logging
import pickle
import shap
import pandas as pd
import numpy as np
from pathlib import Path
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score
from datetime import datetime
from churn import config
from churn.datos import cargar_datos
from churn.modelo import dividir_datos, construir_modelo
from churn.metricas import precision_at_k, lift_at_k, captura_at_k
from churn.explicacion import calcular_shap, limpiar_nombre
from churn.db import obtener_engine, guardar_tabla, reemplazar_corrida


log = logging.getLogger(__name__)


def preparar(ruta_csv: Path = config.DATA_DIR / "dataset.csv",
             dir_salida: Path = config.DATA_DIR,
             engine=None) -> dict:
    """Carga el CSV, separa train y test, y los guarda en Parquet. Regresa las rutas."""
    log.info(f"Iniciando preparación de datos. Cargando CSV desde: {ruta_csv}")
    df = cargar_datos(ruta_csv)

    engine = engine or obtener_engine()
    guardar_tabla(df, "clientes", engine, modo="replace", index=True)

    log.debug(f"CSV cargado exitosamente. Dimensiones originales: {df.shape}")
    
    X_train, X_test, y_train, y_test = dividir_datos(
        df, test_size=config.TEST_SIZE, semilla=config.SEMILLA
    )

    rutas = {"train": dir_salida / "train.parquet", "test": dir_salida / "test.parquet"}

    dir_salida.mkdir(parents=True, exist_ok=True)

    X_train.assign(churn=y_train).to_parquet(rutas["train"])        # X e y juntos en un archivo
    X_test.assign(churn=y_test).to_parquet(rutas["test"])
    
    log.info(f"Datos preparados y guardados en '{dir_salida}': {len(X_train)} filas de train, {len(X_test)} de test")

    return {nombre: str(ruta) for nombre, ruta in rutas.items()}    # texto: XCom no acepta Path

def entrenar(ruta_train, ruta_modelo_pkl = config.RUTA_MODELO) -> str:
    """Lee el parquet, separa X e y, construye el pipeline con config, lo ajusta, lo guarda con pickle (crea la carpeta models/ si no existe) y regresa la ruta"""
    
    Path_ruta_train = Path(ruta_train)
    log.info(f"Iniciando fase de entrenamiento. Leyendo datos desde {Path_ruta_train}")
    train_parquet = pd.read_parquet(Path_ruta_train)
    X_train = train_parquet.drop(columns=["churn"])
    y_train = train_parquet["churn"]

    log.debug(f"Datos preparados. Dimensiones X_train: {X_train.shape}, y_train: {y_train.shape}")

    log.info("Construyendo y ajustando el pipeline de LightGBM...")
    pipeline_modelo = construir_modelo(
        config.NUM_COLS, config.CAT_COLS,
        estimador=LGBMClassifier(**config.HIPERPARAMETROS),
        escalar=False
    )

    pipeline_modelo.fit(X_train, y_train)
    log.debug("Entrenamiento del modelo completado.")

    Path_ruta_modelo = Path(ruta_modelo_pkl)
    Path_ruta_modelo.parent.mkdir(parents=True, exist_ok=True)

    log.info(f"Guardando modelo serializado en {Path_ruta_modelo}")
    with open(Path_ruta_modelo, "wb") as f:     # "wb": escritura binaria
        pickle.dump(pipeline_modelo, f)

    return str(Path_ruta_modelo)

def evaluar(ruta_test, ruta_modelo_pkl = config.RUTA_MODELO, run_id="local", engine=None) -> dict:
    """
    Carga el picle, predice probabilidades, calcula AUC,
    precision@10%, lift@10% y captura@20%
    """
    Path_ruta_modelo_pkl = Path(ruta_modelo_pkl)

    log.info(f"Cargando modelo serializado desde: {Path_ruta_modelo_pkl}")
    with open(Path_ruta_modelo_pkl, "rb") as f:      # "rb": lectura binaria
        modelo = pickle.load(f)

    Path_ruta_test = Path(ruta_test)
    log.info(f"Iniciando fase de evaluacion. Leyendo datos desde {Path_ruta_test}")
    test_parquet = pd.read_parquet(Path_ruta_test)
    X_test = test_parquet.drop(columns=["churn"])
    y_test = test_parquet["churn"]

    log.debug(f"Datos preparados. Dimensiones X_test: {X_test.shape}, y_test: {y_test.shape}")

    log.info("Generando predicciones y calculando métricas de negocio...")
    scores = modelo.predict_proba(X_test)[:, 1]

    k_10 = int(0.10 * len(y_test))
    k_20 = int(0.20 * len(y_test))

    auc_score = roc_auc_score(y_test, scores)

    metricas = {
        "run_id": run_id,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "n_clientes": len(X_test),
        "auc": auc_score,
        "precision_at_10": precision_at_k(y_test, scores,k_10),
        "lift_at_10": lift_at_k(y_test, scores,k_10),
        "precision_at_20": precision_at_k(y_test, scores,k_20),
        "captura_at_20": captura_at_k(y_test, scores, k_20)
    }

    log.info(
        "AUC=%.3f | precision@10%%=%.1f%% | lift@10%%=%.2f | precision@20%%=%.1f%%  | captura@20%%=%.1f%%",
        metricas["auc"],
        metricas["precision_at_10"] * 100,
        metricas["lift_at_10"],
        metricas["precision_at_20"] * 100,
        metricas["captura_at_20"] * 100,
    )

    # --- Control de Calidad ---
    if auc_score < config.AUC_MINIMO:
        raise ValueError(f"El modelo no cumple con la calidad mínima. AUC obtenido: {auc_score:.3f}, Mínimo requerido: {config.AUC_MINIMO}")
    # --------------------------

    engine = engine or obtener_engine()
    df_metricas = pd.DataFrame([metricas])
    reemplazar_corrida(df_metricas, "metricas_modelo", run_id, engine, index=False)

    json_file = Path_ruta_modelo_pkl.parent / "metricas.json"
    
    log.info(f"Guardando métricas en formato JSON en: {json_file}")
    with open(json_file, "w", encoding="utf-8") as archivo:
        json.dump(metricas, archivo, indent=4, ensure_ascii=False)

    return metricas

def predecir(ruta_test, ruta_modelo_pkl, engine=None):
    """Genera predicciones, grupos de riesgo y extrae factores SHAP."""
    log.info("Iniciando generación de predicciones y explicabilidad...")

    test_parquet = pd.read_parquet(ruta_test)
    X_test = test_parquet.drop(columns=["churn"])
    y_test = test_parquet["churn"]

    with open(ruta_modelo_pkl, "rb") as f:
        modelo = pickle.load(f)

    riesgo = modelo.predict_proba(X_test)[:, 1]
    riesgo_series = pd.Series(riesgo, index=X_test.index)

    grupo_riesgo_series = pd.qcut(riesgo_series.rank(method="first"), q=10, labels=[10,9,8,7,6,5,4,3,2,1])

    X_muestra, explicacion = calcular_shap(modelo, X_test, n_muestra=None)

    valores_shap = explicacion.values
    if len(valores_shap.shape) == 3:
        valores_shap = valores_shap[:, :, 1]

    nombres = np.array([limpiar_nombre(n) for n in explicacion.feature_names])
    orden = np.argsort(-valores_shap, axis=1)[:, :3] 
    factores = nombres[orden]

    predicciones = pd.DataFrame({
        "riesgo": riesgo_series.loc[X_muestra.index].astype('float32'),
        "grupo_riesgo": grupo_riesgo_series.loc[X_muestra.index].astype('int16'),
        "churn_real": y_test.loc[X_muestra.index].astype('int16'),
        "factor_1": factores[:, 0],
        "factor_2": factores[:, 1],
        "factor_3": factores[:, 2],
    }, index=X_muestra.index)

    importancia_global = np.abs(valores_shap).mean(axis=0)
    importancia_variables = pd.DataFrame({
        "variable": nombres,
        "importancia": importancia_global
    }).sort_values(by="importancia", ascending=False)

    engine = engine or obtener_engine()
    guardar_tabla(predicciones, "predicciones", engine, modo="replace", index=True)
    guardar_tabla(importancia_variables, "importancia_variables", engine, modo="replace", index=False)

    log.info("Predicciones e importancias guardadas en PostgreSQL exitosamente.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    rutas = preparar()
    ruta_modelo = entrenar(rutas["train"])
    evaluar(rutas["test"], ruta_modelo)
    predecir(rutas["test"], ruta_modelo)