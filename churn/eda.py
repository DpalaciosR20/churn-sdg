import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

def margen_ic(p: float, n: int) -> float:
    z = 1.96  # Valor crítico para un intervalo de confianza del 95%
    margen = z * (p * (1 - p) / n) ** 0.5

    return margen


def tasa_por_decil(df, columna, q=10) -> pd.DataFrame:
    """
    Regresa una DataFrame con el número de clientes, tasa de churn y el margen del intervalo de confianza, por decil
    """
    deciles = pd.qcut(df[columna], q=q, duplicates="drop")
    resumen = df.groupby(deciles, observed=True, dropna=False).agg(
        n_clientes=('churn', 'count'),
        tasa_churn=('churn', 'mean')
    )
    resumen['margen_ic'] = margen_ic(resumen['tasa_churn'], resumen['n_clientes'])
    
    return resumen

def graficar_tasa(tabla: pd.DataFrame, titulo: str, promedio: float) -> Figure:
    """tabla: resultado de un groupby con la columna 'tasa_churn'."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(tabla.index.astype(str), tabla["tasa_churn"], color="#4C72B0")
    ax.axhline(promedio, color="gray", linestyle="--", label=f"Promedio {promedio:.1%}")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))   # 0.53 → 53%
    ax.set_title(titulo, loc="left", fontweight="bold")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    return fig