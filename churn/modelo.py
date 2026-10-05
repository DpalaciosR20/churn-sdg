import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer
from sklearn.linear_model import LogisticRegression

def dividir_datos(
        df: pd.DataFrame,
        target: str = "churn",
        test_size: float = 0.2,
        semilla: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Divide el dataset en entrenamiento y prueba manteniendo la proporción de la variable objetivo."""
    # Se excluye Customer_ID ya que no es una variable que demuestre el comportamiento real del cliente y un ID muy alto o muy bajo podría sesgar el modelo en su entrenamiento.
    X = df.drop(columns=[target, 'Customer_ID'])
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=semilla,
        stratify=y
    )

    return X_train, X_test, y_train, y_test

def limpiar_negativos(X: pd.DataFrame) -> pd.DataFrame:
    """eqpdays negativo pasa a 0, y los ingresos y cargos negativos pasan a NaN"""
    X = X.copy()

    X['eqpdays'] = X['eqpdays'].clip(lower=0)
    X.loc[X['rev_Mean'] < 0, 'rev_Mean'] = np.nan
    X.loc[X['totmrc_Mean'] < 0, 'totmrc_Mean'] = np.nan
    X.loc[X['avg6rev'] < 0, 'avg6rev'] = np.nan

    return X

def construir_preprocesador(num_cols, cat_los):
    preprocesador = FunctionTransformer(limpiar_negativos())