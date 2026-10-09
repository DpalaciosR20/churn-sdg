# tests/test_datos.py
import pathlib
import pytest
from churn.datos import cargar_datos
import pandas as pd

CONTENT = """
Customer_ID;da_Mean;eqpdays;hnd_webcap;refurb_new;churn
1;0,2475;10;;N;0
2;0,2475;20;WCMB;Y;1
3;0;30;WC;N;0
4;12,375;30;NA;N;0
"""
@pytest.fixture
def datos(tmp_path: pathlib.Path) -> pathlib.Path:
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test.csv"
    p.write_text(CONTENT)
    return p

def test_conserva_categoria_NA(datos: pathlib.Path):
    df = cargar_datos(datos)
    assert df.loc[4, 'hnd_webcap'] == "NA"

def test_decimales_con_coma(datos: pathlib.Path):
    df = cargar_datos(datos)
    
    assert df.loc[1, 'da_Mean'] == pytest.approx(0.2475)
    assert df.loc[2, 'da_Mean'] == pytest.approx(0.2475)
    assert df.loc[3, 'da_Mean'] == pytest.approx(0.0)
    assert df.loc[4, 'da_Mean'] == pytest.approx(12.375)

def test_celda_vacia_es_faltante(datos: pathlib.Path):
    df = cargar_datos(datos)
    
    assert pd.isna(df.loc[1, 'hnd_webcap'])