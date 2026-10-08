import numpy as np
import pandas as pd
import pytest
from lightgbm import LGBMClassifier
from churn.modelo import construir_modelo
from churn.explicacion import calcular_shap

NUM_COLS = ["eqpdays", "rev_Mean", "totmrc_Mean", "avg6rev"]
CAT_COLS = ["plan"]

@pytest.fixture(scope="module")         # se crea una vez para todos los tests del archivo (modulo)
def modelo_y_datos():
    rng = np.random.default_rng(42)     # generador aleatorio con semillaa: datos reproducibles
    n = 400
    X = pd.DataFrame({
        "eqpdays": rng.integers(0, 800, n).astype(float),
        "rev_Mean": rng.normal(50, 15, n),
        "totmrc_Mean": rng.normal(40, 10, n),
        "avg6rev": rng.normal(50, 15, n),
        "plan": rng.choice(["A", "B", "C"], n),
    })
    y = (X["eqpdays"] > 400).astype(int)    # un target que el modelo SÍ pueda aprender

    modelo = construir_modelo(
        NUM_COLS, CAT_COLS,
        LGBMClassifier(n_estimators=20, random_state=42, verbose=-1),
        escalar=False,
    ).fit(X, y)
    return modelo, X

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def test_shap_reconstruye_la_probabilidad(modelo_y_datos):
    """
    Verifica que la suma de valores SHAP + base_value reconstruya la probabilidad.
    """
    modelo, X = modelo_y_datos
    X_muestra, valores = calcular_shap(modelo, X, n_muestra=50)

    prob_shap = sigmoid(valores.base_values + valores.values.sum(axis=1))       # un valor por cliente
    prob_modelo = modelo.predict_proba(X_muestra)[:, 1]

    assert np.allclose(prob_shap, prob_modelo, atol=1e-6)
    
def cantidad_de_valores_shap_igual_a_n_muestra(modelo_y_datos):
    """
    Verifica que valores.values tenga tantas filas como n_muestra
    """
    modelo, X = modelo_y_datos
    n = 50
    _, valores = calcular_shap(modelo, X, n_muestra=n)

    assert len(valores.values) == n

def calcular_shap_no_falla_con_n_mayor_a_filas(modelo_y_datos):
    """
    Verifica que la función calcular_shap no falle si se piden más filas de las que hay (n_muestra=10_000 con 400 datos)
    """
    modelo, X = modelo_y_datos
    filas_max = len(X)
    
    assert calcular_shap(modelo, X, n_muestra=(filas_max*2))

def X_muestra_y_valores_alineados(modelo_y_datos):
    modelo, X = modelo_y_datos
    X_muestra, valores = calcular_shap(modelo, X, n_muestra=50)

    assert len(X_muestra) == len(valores)