# tests/test_MeanImputer.py
import pytest
from churn.preprocesamiento import MeanImputer


# Caso Base
def test_caso_base():
    imputer = MeanImputer()
    assert imputer.fit([10, None, 30]).mean_ == pytest.approx(20.0)      
    assert imputer.transform([None, 5]) == [20.0, 5]
    
# Ceros en fit y en transform
def test_manejo_de_ceros_en_fit_y_transform():
    imputer = MeanImputer()
    assert imputer.fit([0, None, 10]).mean_ == pytest.approx(5.0)
    assert imputer.transform([0, None]) == [0, 5.0]

# Todo None
def test_fit_None_lanza_error():
    imputer = MeanImputer()
    with pytest.raises(ValueError): imputer.fit([None, None, None])

# transform sin fit
def test_transform_sin_fit_lanza_error():
    imputer = MeanImputer()
    with pytest.raises(ValueError): imputer.transform([0.1, 0.2, 0.3])

# Entrada no se modifica
def test_entrada_intacta():
    entrada_fit = [10, None, 30]
    entrada_transform = [None, 5]
    
    imputer = MeanImputer()
    imputer.fit(entrada_fit)
    imputer.transform(entrada_transform)
    
    assert entrada_fit == [10, None, 30]
    assert entrada_transform == [None, 5]
    