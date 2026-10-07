import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from typing import Optional, Union

def margen_ic(p: float, n: int) -> float:
    """Regresa el margen de un intervalo de confianza del 95%"""
    margen = 1.96 * (p * (1 - p) / n) ** 0.5

    return margen


def tasa_por_decil(df: pd.DataFrame, columna: str, q:int=10, dropna: bool = False) -> pd.DataFrame:
    """
    Regresa una DataFrame con el número de clientes, tasa de churn y el margen del intervalo de confianza, por decil
    """
    deciles = pd.qcut(df[columna], q=q, duplicates="drop")
    resumen = df.groupby(deciles, observed=True, dropna=dropna).agg(
        n_clientes=('churn', 'count'),
        tasa_churn=('churn', 'mean')
    )
    resumen['margen_ic'] = margen_ic(resumen['tasa_churn'], resumen['n_clientes'])
    
    return resumen

def graficar_tasa(
        tabla: pd.DataFrame,
        titulo: str,
        promedio: float,
        ax: Optional[plt.Axes] = None
) -> Union[plt.Figure, plt.Axes]:
    """tabla: resultado de un groupby con la columna 'tasa_churn'."""
    retornar_fig = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 4))
        retornar_fig = True
    
    ax.bar(tabla.index.astype(str), tabla["tasa_churn"], color="#4C72B0")
    ax.axhline(promedio, color="gray", linestyle="--", label=f"Promedio {promedio:.1%}")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_title(titulo, loc="left", fontweight="bold", fontsize=10)
    ax.tick_params(axis="x", rotation=45, labelsize=8)
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)

    return ax.figure if retornar_fig else ax