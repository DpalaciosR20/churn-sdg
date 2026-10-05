import pandas as pd

def cargar_datos(ruta: str) -> pd.DataFrame:
    """
    Carga los datos desde un archivo CSV y devuelve un DataFrame de pandas.

    Args:
        ruta (str): La ruta del archivo CSV a cargar.

    Returns:
        pd.DataFrame: Un DataFrame que contiene los datos cargados.
    """
    df = pd.read_csv(
        ruta,
        sep=';',
        decimal=',',
        keep_default_na=False,
        na_values=['']
    )
    return df

def reporte_calidad(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un reporte de calidad de los datos en el DataFrame.

    Args:
        df (pd.DataFrame): El DataFrame a analizar.

    Returns:
        pd.DataFrame: Un DataFrame que contiene el reporte de calidad.
    """

    # Reporte de calidad de los datos. Una fila por cada columna del DataFrame.
    reporte = pd.DataFrame({
        'dtype': df.dtypes,
        'pct_nulos': df.isna().mean() * 100,
        'n_unicos': df.nunique(),
        'ejemplo': df.apply(lambda x: x.dropna().iloc[0] if x.dropna().nunique() > 0 else [])
    }).sort_values(by='pct_nulos', ascending=False)
    return reporte

def tasa_por_grupo(df: pd.DataFrame, grupo: pd.Series) -> pd.DataFrame:
    """Calcula el número de clientes y la tasa de churn por grupo"""
    return df.groupby(grupo, dropna=False).agg(
        n_clientes=('churn', 'count'),
        tasa_churn=('churn', 'mean')
    ).sort_values(by='tasa_churn', ascending=False)