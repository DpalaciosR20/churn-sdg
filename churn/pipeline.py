import json
import logging
import pickle
from pathlib import Path
import pandas as pd
from churn import config
from churn.datos import cargar_datos
from churn.modelo import dividir_datos, construir_modelo
from churn.metricas import precision_at_k, lift_at_k
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score


log = logging.getLogger(__name__)


def preparar(ruta_csv: Path = config.DATA_DIR / "dataset.csv",
             dir_salida: Path = config.DATA_DIR) -> dict:
    """Carga el CSV, separa train y test, y los guarda en Parquet. Regresa las rutas."""
    log.info(f"Iniciando preparación de datos. Cargando CSV desde: {ruta_csv}")
    df = cargar_datos(ruta_csv)

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

def entrenar(ruta_train, ruta_modelo_pkl) -> str:
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

def evaluar(ruta_modelo_pkl, ruta_test) -> dict:
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

    datos_evaluacion = {
        "AUC": f"{roc_auc_score(y_test, scores):.3f}",
        "precision@10%": f"{precision_at_k(y_test, scores,k_10):.0%}",
        "lift@10%": f"{lift_at_k(y_test, scores,k_10):.3}",
        "precision@20%": f"{precision_at_k(y_test, scores,k_20):.0%}",
    }

    df_evaluacion = pd.DataFrame(datos_evaluacion, index=[0])
    log.info(f"\n{df_evaluacion.to_string(index=False)}")

    json_file = Path_ruta_modelo_pkl.parent / "metricas.json"
    
    log.info(f"Guardando métricas en formato JSON en: {json_file}")
    with open(json_file, "w", encoding="utf-8") as archivo:
        json.dump(datos_evaluacion, archivo, indent=4, ensure_ascii=False)

    return str(json_file)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    rutas = preparar()
    ruta_modelo_pkl = config.BASE_DIR / "models" /"modelo_LightGBM.pkl"
    evaluar(entrenar(rutas["train"],ruta_modelo_pkl), rutas["test"])