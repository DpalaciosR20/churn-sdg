import pytest

from churn.etiquetas import COLUMNAS_FACTOR, ETIQUETAS, columna_factor, etiqueta


@pytest.mark.parametrize(("factor", "texto"), ETIQUETAS.items())
def test_etiqueta_traduce_factores_frecuentes(factor, texto):
    assert etiqueta(factor) == texto


def test_etiqueta_devuelve_el_nombre_original_si_no_lo_conoce():
    assert etiqueta("variable_nueva") == "variable_nueva"


@pytest.mark.parametrize(("factor", "columna"), COLUMNAS_FACTOR.items())
def test_columna_factor_devuelve_la_columna_original(factor, columna):
    assert columna_factor(factor) == columna


def test_columna_factor_desconocido_conserva_el_nombre():
    assert columna_factor("variable_nueva") == "variable_nueva"
