# tests/test_segmento.py
import pytest
from churn.segmentos import segmento

def test_segmento_limite_inferior():
    assert segmento(11) == "0-11"
    assert segmento(12) == "12-24"

def test_segmento_rechaza_negativos():
    with pytest.raises(ValueError):      # el test pasa si se lanza ValueError
        segmento(-1)