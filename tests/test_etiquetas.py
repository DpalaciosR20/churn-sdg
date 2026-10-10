import pytest

from churn.etiquetas import ETIQUETAS, etiqueta


@pytest.mark.parametrize(("factor", "texto"), ETIQUETAS.items())
def test_etiqueta_traduce_factores_frecuentes(factor, texto):
    assert etiqueta(factor) == texto


def test_etiqueta_devuelve_el_nombre_original_si_no_lo_conoce():
    assert etiqueta("variable_nueva") == "variable_nueva"
