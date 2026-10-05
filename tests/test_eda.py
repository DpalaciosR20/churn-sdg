import pytest
from churn.eda import margen_ic

def test_funcion_margen_ic():
    assert margen_ic(0.5, 100) == pytest.approx(0.098)