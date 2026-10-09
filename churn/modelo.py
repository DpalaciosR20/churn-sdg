import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

def dividir_datos(
        df: pd.DataFrame,
        target: str = "churn",
        test_size: float = 0.2,
        semilla: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Divide el dataset en entrenamiento y prueba manteniendo la proporción de la variable objetivo."""
    X = df.drop(columns=[target])
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

def construir_preprocesador(num_cols: list[str], cat_cols: list[str], escalar=True) -> ColumnTransformer:
    """Imputa y escala las numéricas; imputa y codifica las categóricas."""
    numericas = make_pipeline(
        # Con add_indicator=True, se agrega un MissingIndicator transform a la salida de la imputación para mantener un indicador de cuáles fueron los valores que venían como NaN. Esto permite a un estimador predictivo contabilizar los NaN sin importar la imputación.
        # Durante el EDA se encontró que en las variables hnd_price y avg6rev, cuando no tienen valores su tasa de churn es de 36.7% y 40.2% que está 13 y 9 puntos por debajo aprox del promedio, respectivamente. Esos datos faltantes podrían ser igual información que se deba considerar.
        SimpleImputer(strategy="median", add_indicator=True),
        StandardScaler(),
    )
    categoricas = make_pipeline(
        SimpleImputer(strategy="constant", fill_value="Sin dato"),
        OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=100)
    )

    return ColumnTransformer([
        ("num", numericas if escalar else "passthrough", num_cols),
        ("cat", categoricas, cat_cols)
    ])

def construir_modelo(num_cols: list[str], cat_cols: list[str], estimador, escalar: bool=True) -> Pipeline:
    """Pipeline completo: limpieza -> preprocesamiento -> estimador."""
    return Pipeline([
        ("limpieza", FunctionTransformer(limpiar_negativos, feature_names_out="one-to-one")),
        ("pre", construir_preprocesador(num_cols, cat_cols, escalar)),
        ("clf", estimador),
    ])