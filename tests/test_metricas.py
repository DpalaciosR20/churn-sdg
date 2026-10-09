import pytest
from churn.metricas import lift_at_k, tabla_ganancias, captura_at_k

@pytest.fixture
def datos_toy():
    """Fixture con 10 clientes, 4 churners (Tasa base = 0.4)"""
    scores = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
    # Los churners están en las posiciones 1, 2, 4 y 8 (ordenados por score)
    y_true = [1,   1,   0,   1,   0,   0,   0,   1,   0,   0]
    return y_true, scores

def test_lift_at_k(datos_toy):
    y_true, scores = datos_toy
    
    assert lift_at_k(y_true, scores, k=2) == pytest.approx(2.5)
    
    assert lift_at_k(y_true, scores, k=4) == pytest.approx(1.875)
    
    assert lift_at_k(y_true, scores, k=10) == pytest.approx(1.0)

def test_captura_at_k_logica_correcta():
    y_true = [1,   0,   1,   1,   0]
    scores = [0.9, 0.8, 0.7, 0.4, 0.1] 
    
    resultado_k2 = captura_at_k(y_true, scores, k=2)
    assert resultado_k2 == pytest.approx(1/3)
 
    resultado_k4 = captura_at_k(y_true, scores, k=4)
    assert resultado_k4 == 1.0

def test_captura_at_k_division_por_cero():
    y_true = [0, 0, 0]
    scores = [0.9, 0.5, 0.1]
    
    assert captura_at_k(y_true, scores, k=2) == 0.0

def test_captura_at_k_hereda_excepciones():
    y_true = [1, 0, 1]
    scores = [0.9, 0.8, 0.1]
    
    with pytest.raises(ValueError, match="el valor de 'k' es incorrecto"):
        captura_at_k(y_true, scores, k=5)


def test_tabla_ganancias(datos_toy):
    y_true, scores = datos_toy
    
    # Creamos 5 grupos. Como hay 10 clientes, cada grupo tendrá 2 clientes.
    df_resumen = tabla_ganancias(y_true, scores, n_grupos=5)
    
    # 1. Comprobar estructura general
    assert len(df_resumen) == 5
    assert df_resumen['n_clientes'].sum() == 10
    assert df_resumen['churners'].sum() == 4
    
    # 2. Comprobar Grupo 1 (Scores 0.9 y 0.8)
    grupo1 = df_resumen.loc[1]
    assert grupo1['n_clientes'] == 2
    assert grupo1['churners'] == 2
    assert grupo1['tasa_churn'] == pytest.approx(1.0)
    assert grupo1['lift'] == pytest.approx(2.5)            # 1.0 / 0.4
    assert grupo1['captura_acumulada'] == pytest.approx(0.5) # 2 de 4 churners totales
    
    # 3. Comprobar Grupo 2 (Scores 0.7 y 0.6)
    grupo2 = df_resumen.loc[2]
    assert grupo2['churners'] == 1
    assert grupo2['lift'] == pytest.approx(1.25)           # 0.5 / 0.4
    assert grupo2['captura_acumulada'] == pytest.approx(0.75) # 3 de 4 acumulados
    
    # 4. Comprobar Grupo final (Todo acumulado debe ser 100%)
    grupo5 = df_resumen.loc[5]
    assert grupo5['captura_acumulada'] == pytest.approx(1.0)# 4 de 4