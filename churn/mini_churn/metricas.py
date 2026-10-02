def precision_at_k(y_true: list[int], scores: list[float], k: int) -> float:
    """Ordena los clientes por score de mayor a menor, toma los k primeros y calcula qué proporción era realmente churn"""
    if not len(y_true) == len(scores):
        raise ValueError("Las listas 'y_true' y 'scores' son de distinto tamaño.")
    if k<=0 or k>len(y_true):
        raise ValueError("el valor de 'k' es incorrecto.")
    combinado = sorted(zip(scores, y_true), key=lambda x: x[0], reverse=True)
    _, y_true_ordenado = zip(*combinado)
    return sum(y_true_ordenado[:k]) / k

if __name__ == "__main__":
    y_true=[1,0,1,1,0,0,1,0]
    scores=[0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2]
    print(f"{precision_at_k(y_true, scores, k=3):.2f}")   # 0.67

    y_true=[0,1,1,0]
    scores=[0.1,0.9,0.4,0.8]
    print(f"{precision_at_k(y_true, scores, k=2):.2f}")     # 0.50
    
    print(f"{precision_at_k([1, 0, 0], [0.9, 0.9, 0.1], k=2):.2f}")     # 0.50