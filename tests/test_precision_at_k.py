# tests/test_precision_at_k.py
import pytest
from churn.metricas import precision_at_k

def test_casos_originales():
    t1 = precision_at_k(
        y_true=[1,0,1,1,0,0,1,0],
        scores=[0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2],
        k=3
    )
    t2 = precision_at_k(
        y_true=[1,0,1,1,0,0,1,0],
        scores=[0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2],
        k=4
    )
    t3 = precision_at_k(
        y_true=[0,1,1,0],
        scores=[0.1,0.9,0.4,0.8],
        k=2
    )
    assert t1  == pytest.approx(2 / 3)
    assert t2  == pytest.approx(0.75)
    assert t3  == pytest.approx(0.5)

def test_empates():
    t1 = precision_at_k([1, 0, 0], [0.9, 0.9, 0.1], k=2)
    t2 = precision_at_k([0, 1], [0.9, 0.9], k=1)
    t3 = precision_at_k([1, 0], [0.9, 0.9], k=1)
    assert t1  == pytest.approx(0.5)
    assert t2  == pytest.approx(0.0)
    assert t3  == pytest.approx(1.0)

def test_entradas_originales():
    i1 = [0,1,1,0]
    i2 = [0.1,0.9,0.4,0.8]
    precision_at_k(
        y_true=i1,
        scores=i2,
        k=2
    )
    assert i1 == [0,1,1,0]
    assert i2 == [0.1,0.9,0.4,0.8]

def test_ValueError():
    with pytest.raises(ValueError): precision_at_k([0,1],[0.9],1)       # Largo distinto
    with pytest.raises(ValueError): precision_at_k([0],[0.9,0.8],1)     # Largo distinto
    with pytest.raises(ValueError): precision_at_k([0,1],[0.9,0.8],0)   # k=0
    with pytest.raises(ValueError): precision_at_k([0,1],[0.9,0.8],4)   # k demasiado grande
    with pytest.raises(ValueError): precision_at_k([0,1],[0.9,0.8],-4)   # k demasiado bajo