import pytest
import pandas as pd
from sqlalchemy import create_engine, Engine
from churn.db import guardar_tabla, reemplazar_corrida, leer_sql

@pytest.fixture
def engine_sqlite() -> Engine:
    """Fixture que crea una base de datos temporal en memoria para los tests."""
    return create_engine("sqlite://")

@pytest.fixture
def df_prueba() -> pd.DataFrame:
    """Fixture con datos de prueba sencillos."""
    return pd.DataFrame({"col1": [1,2], "col2": ["A", "B"]})

def test_guardar_tabla_replace_no_duplica(engine_sqlite: Engine, df_prueba: pd.DataFrame):
    # Ejacutar dos veces simulando sobreescritura
    guardar_tabla(df_prueba, "tabla_test", engine_sqlite, modo="replace", index=False)
    guardar_tabla(df_prueba, "tabla_test", engine_sqlite, modo="replace", index=False)

    # Leer el resultado
    df_leido = leer_sql("SELECT * FROM tabla_test", engine_sqlite)
    assert len(df_leido) == 2 # No se duplicó, sigue teniendo exactamente 2 filas

def test_reemplazar_corrida_mismo_run_id_no_duplica(engine_sqlite: Engine, df_prueba: pd.DataFrame):
    run_id = "run_1"

    # Ejecutar dos veces simulando que Airflow reintentó la tarea
    reemplazar_corrida(df_prueba, "tabla_corrida", run_id, engine_sqlite, index=False)
    reemplazar_corrida(df_prueba, "tabla_corrida", run_id, engine_sqlite, index=False)

    df_leido = leer_sql("SELECT * FROM tabla_corrida", engine_sqlite)
    assert len(df_leido) == 2
    assert all(df_leido["run_id"] == "run_1")

def test_reemplazar_corrida_distintos_run_id_conserva_ambos(engine_sqlite: Engine, df_prueba: pd. DataFrame):
    # Ejecutar para dos corridas distintas
    reemplazar_corrida(df_prueba, "tabla_corrida", "run_1", engine_sqlite, index=False)
    reemplazar_corrida(df_prueba, "tabla_corrida", "run_2", engine_sqlite, index=False)

    df_leido = leer_sql("SELECT * FROM tabla_corrida", engine_sqlite)
    assert len(df_leido) == 4
    assert set(df_leido["run_id"]) == {"run_1", "run_2"}