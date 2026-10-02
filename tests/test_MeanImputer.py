# tests/test_MeanImputer.py
import pytest
from churn.preprocesamiento import MeanImputer


# Caso Base
def test_caso_base():
    scaler = MeanImputer()
    assert scaler.fit([10, None, 30]).mean_ == pytest.approx(20.0)      
    assert scaler.transform([None, 5]) == [20.0, 5]
    
# Ceros en fit y en transform
def test_ceros():
    scaler = MeanImputer()
    assert scaler.fit([0, None, 10]).mean_ == pytest.approx(5.0)
    assert scaler.transform([0, None]) == [0, 5.0]

# Todo None
def test_None():
    scaler = MeanImputer()
    with pytest.raises(ValueError): scaler.fit([None, None, None])

# transform sin fit
def test_transform_no_fit():
    scaler = MeanImputer()
    with pytest.raises(ValueError): scaler.transform([0.1, 0.2, 0.3])

# Entrada no se modifica
def test_entrada_intacta():
    entrada_fit = [10, None, 30]
    entrada_transform = [None, 5]
    
    scaler = MeanImputer()
    scaler.fit(entrada_fit)
    scaler.transform(entrada_transform)
    
    assert entrada_fit == [10, None, 30]
    assert entrada_transform == [None, 5]
    