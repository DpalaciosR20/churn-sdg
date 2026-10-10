# tests/test_pipeline.py

import pickle
import numpy as np
import pandas as pd
import pytest
import shap
from lightgbm import LGBMClassifier
from sqlalchemy import create_engine, Engine
from pathlib import Path

from churn.db import leer_sql
from churn.modelo import construir_modelo
from churn.explicacion import limpiar_nombre
from churn.pipeline import preparar, predecir, evaluar

NUM_COLS = ["eqpdays", "rev_Mean", "totmrc_Mean", "avg6rev"]
CAT_COLS = ["plan"]

@pytest.fixture
def engine_sqlite() -> Engine:
    """Fixture que crea una base de datos temporal en memoria para los tests."""
    return create_engine("sqlite://")

@pytest.fixture
def df_prueba() -> pd.DataFrame:
    """Fixture con datos de prueba sencillos."""
    return pd.DataFrame({
        "Customer_ID": range(10),
        "da_Mean": range(10),
        "eqpdays": range(10),
        "hnd_webcap": [str(x) for x in range(10)],
        "refurb_new": [str(x) for x in range(10)],
        "churn": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    })

@pytest.fixture
def escenario(tmp_path):
    rng = np.random.default_rng(42)
    n = 300
    X = pd.DataFrame({
        "eqpdays": rng.integers(0, 800, n).astype(float),
        "rev_Mean": rng.normal(50, 15, n),
        "totmrc_Mean": rng.normal(40, 10, n),
        "avg6rev": rng.normal(50, 15, n),
        "plan": rng.choice(["A", "B", "C"], n),
    }, index=pd.Index(range(1000, 1000 + n), name="Customer_ID"))   # IDs que NO empiezan en 0
    # Target con ruido: depende de dos variables, para que los riesgos sean variados
    y = ((X["eqpdays"] / 800 + X["rev_Mean"] / 100 + rng.normal(0, 0.3, n)) > 1.0).astype(int)

    modelo = construir_modelo(
        NUM_COLS, CAT_COLS,
        LGBMClassifier(n_estimators=30, random_state=42, verbose=-1),
        escalar=False,
    ).fit(X, y)

    ruta_modelo = tmp_path / "modelo.pkl"
    with open(ruta_modelo, "wb") as f:
        pickle.dump(modelo, f)

    ruta_test = tmp_path / "test.parquet"
    X.assign(churn=y).to_parquet(ruta_test)

    return {"X": X, "y": y, "modelo": modelo, "ruta_modelo": ruta_modelo,
            "ruta_test": ruta_test, "engine": create_engine("sqlite://")}

def test_preparar(df_prueba, tmp_path, engine_sqlite):
    ruta_csv_tmp = tmp_path / "dataset_test.csv"
    df_prueba.to_csv(ruta_csv_tmp, index=False, sep=";", decimal=",")

    dir_salida_tmp = tmp_path
    rutas_generadas = preparar(ruta_csv=ruta_csv_tmp, dir_salida=dir_salida_tmp, engine=engine_sqlite)

    ruta_train = Path(rutas_generadas["train"])
    ruta_test = Path(rutas_generadas["test"])

    assert ruta_train.exists()
    assert ruta_test.exists()

    train_df = pd.read_parquet(ruta_train)
    test_df = pd.read_parquet(ruta_test)

    indices_train = set(train_df.index)
    indices_test = set(test_df.index)

    assert len(indices_train.intersection(indices_test)) == 0
    assert len(train_df) + len(test_df) == 10

    clientes_db = pd.read_sql("SELECT * FROM clientes", engine_sqlite)
    assert len(clientes_db) == len(df_prueba)

def test_factores_corresponden_a_cada_cliente(escenario):
    e = escenario
    predecir(e["ruta_test"], e["ruta_modelo"], engine=e["engine"])
    guardado = leer_sql("SELECT * FROM predicciones", e["engine"]).set_index("Customer_ID")

    pre = e["modelo"][:-1]
    X_t = pd.DataFrame(pre.transform(e["X"]),
                       columns=pre.get_feature_names_out(), index=e["X"].index)
    valores = shap.TreeExplainer(e["modelo"][-1])(X_t).values
    if len(valores.shape) == 3:
        valores = valores[:, :, 1]
    nombres_limpios = np.array([limpiar_nombre(n) for n in pre.get_feature_names_out()])

    idx_factor_1 = np.argsort(-valores, axis=1)[:, 0]
    factor_esperado = pd.Series(nombres_limpios[idx_factor_1], index=e["X"].index)

    assert (guardado["factor_1"] == factor_esperado.loc[guardado.index]).all()

def test_predecir_riesgo_y_dimensiones(escenario):
    """Riesgo de cada cliente coincide con predict_proba y dimensiones correctas."""
    e = escenario
    predecir(e["ruta_test"], e["ruta_modelo"], engine=e["engine"])
    guardado = pd.read_sql("SELECT * FROM predicciones", e["engine"])
    
    # La tabla tiene tantas filas como el test y ningún Customer_ID repetido
    assert len(guardado) == len(e["X"])
    assert guardado["Customer_ID"].nunique() == len(guardado)
    
    # Validación del riesgo (alineado por Customer_ID)
    guardado = guardado.set_index("Customer_ID")
    riesgo_real = e["modelo"].predict_proba(e["X"])[:, 1]
    riesgo_esperado = pd.Series(riesgo_real, index=e["X"].index)
    
    np.testing.assert_allclose(
        guardado["riesgo"], 
        riesgo_esperado.loc[guardado.index], 
        rtol=1e-5
    )

def test_predecir_dos_veces_no_duplica(escenario):
    """Ejecutar predecir dos veces no duplica filas (idempotencia de replace)."""
    e = escenario
    predecir(e["ruta_test"], e["ruta_modelo"], engine=e["engine"])
    predecir(e["ruta_test"], e["ruta_modelo"], engine=e["engine"])
    
    guardado = pd.read_sql("SELECT * FROM predicciones", e["engine"])
    assert len(guardado) == len(e["X"])

def test_evaluar_mismo_run_id_no_duplica(escenario):
    """Con el mismo run_id dos veces queda una fila en metricas_modelo."""
    e = escenario
    run_id = "dag_run_id_prueba"
    
    evaluar(e["ruta_test"], e["ruta_modelo"], run_id=run_id, engine=e["engine"])
    evaluar(e["ruta_test"], e["ruta_modelo"], run_id=run_id, engine=e["engine"])
    
    metricas = pd.read_sql("SELECT * FROM metricas_modelo", e["engine"])
    assert len(metricas) == 1
    assert metricas.iloc[0]["run_id"] == run_id