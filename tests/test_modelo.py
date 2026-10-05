# tests/test_modelo.py
import pandas as pd
import pathlib
import pytest
from churn.datos import cargar_datos
from churn.modelo import limpiar_negativos

CONTENT = """
id;rev_Mean;totmrc_Mean;avg6rev;eqpdays;churn
1;0,2475;0,2475;0,2475;0,2475;1
2;0;0;0;0;1
3;-0,40;-0,30;-0,20;-0,07;0
3;;30;;30;0
"""
@pytest.fixture
def datos(tmp_path: pathlib.Path) -> pathlib.Path:
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test.csv"
    p.write_text(CONTENT)
    return p

def test_correccion_de_negativos(datos: pathlib.Path):
    df = limpiar_negativos(cargar_datos(datos))
    assert pd.isna(df.loc[2, 'rev_Mean'])
    assert pd.isna(df.loc[2, 'totmrc_Mean'])
    assert pd.isna(df.loc[2, 'avg6rev'])
    assert df.loc[2, 'eqpdays'] == pytest.approx(0.0)

def test_no_modifica_entrada(datos: pathlib.Path):
    df = cargar_datos(datos)
    limpiar_negativos(df)

    assert df.loc[2, 'rev_Mean'] == pytest.approx(-0.40)
    assert df.loc[2, 'totmrc_Mean'] == pytest.approx(-0.30)
    assert df.loc[2, 'avg6rev'] == pytest.approx(-0.20)
    assert df.loc[2, 'eqpdays'] == pytest.approx(-0.07)
