import pandas as pd
import numpy as np

def precision_at_k(y_true: list[int], scores: list[float], k: int) -> float:
    """Ordena los clientes por score de mayor a menor, toma los k primeros y calcula qué proporción era realmente churn"""
    if not len(y_true) == len(scores):
        raise ValueError("Las listas 'y_true' y 'scores' son de distinto tamaño.")
    if k<=0 or k>len(y_true):
        raise ValueError("el valor de 'k' es incorrecto.")
    combinado = sorted(zip(scores, y_true), key=lambda x: x[0], reverse=True)
    _, y_true_ordenado = zip(*combinado)
    return sum(y_true_ordenado[:k]) / k

def lift_at_k(y_true: list[int], scores: list[float], k: int) -> float:
    """Calcula el Lift en los top k comparando la precisión del modelo contra la tasa base."""
    tasa_base = sum(y_true) / len(y_true)

    if tasa_base == 0: return 0.0

    prec_k = precision_at_k(y_true, scores, k)

    return prec_k / tasa_base

def tabla_ganancias(y_true: list[int], scores: list[int], n_grupos: int=10) -> pd.DataFrame:
    tasa_base = np.mean(y_true)
    total_churners = np.sum(y_true)
    
    df = pd.DataFrame({
        'score': scores,
        'churn': y_true
    }).sort_values('score', ascending=False)

    df['grupo'] = pd.qcut(np.arange(len(df)), q=n_grupos, labels=range(1, n_grupos + 1))
    
    resumen = df.groupby('grupo', observed=True).agg(
        n_clientes=('churn', 'count'),
        churners=('churn', 'sum'),
        tasa_churn=('churn', 'mean'),
        score_promedio=('score', 'mean')
    )

    resumen['lift'] = resumen['tasa_churn'] / tasa_base
    resumen['captura_acumulada'] = resumen['churners'].cumsum() / total_churners

    return resumen




if __name__ == "__main__":
    y_true=[1,0,1,1,0,0,1,0]
    scores=[0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2]
    print(f"{precision_at_k(y_true, scores, k=3):.2f}")   # 0.67

    y_true=[0,1,1,0]
    scores=[0.1,0.9,0.4,0.8]
    print(f"{precision_at_k(y_true, scores, k=2):.2f}")     # 0.50
    
    print(f"{precision_at_k([1, 0, 0], [0.9, 0.9, 0.1], k=2):.2f}")     # 0.50