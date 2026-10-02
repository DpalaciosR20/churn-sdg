class MeanImputer:
    """Imputa el valor medio obtenido del conjunto de entrenamiento a valores None del conjunto a transformar"""

    def __init__(self):
        self.mean_ = None      # atributos "aprendidos": convención de sklearn, con _ al final
        self.n_ = None
        self.sum_ = None

    def fit(self, valores: list[float]) -> "MeanImputer":
        self.sum_ = 0
        self.n_ = 0
        for valor in valores:
            if valor is not None:
                self.sum_+=valor
                self.n_+=1
        if not self.n_: raise ValueError("Todos los valores del conjunto de entrenamiento son None")
        self.mean_ = self.sum_/self.n_
        return self           # permite encadenar: MeanImputer().fit(x).transform(x)

    def transform(self, valores: list[float]) -> list[float]:
        if self.mean_ is None:
            raise ValueError("Llama a fit() antes de transform()")
        return [valor if (valor is not None) else self.mean_ for valor in valores]   # lista NUEVA: no muta la entrada

class MinMaxScaler:
    """Escala valores al rango [0, 1] con el mínimo y máximo aprendidos en fit()."""

    def __init__(self):
        self.min_ = None      # atributos "aprendidos": convención de sklearn, con _ al final
        self.max_ = None

    def fit(self, valores: list[float]) -> "MinMaxScaler":
        self.min_ = min(valores)
        self.max_ = max(valores)
        return self           # permite encadenar: MinMaxScaler().fit(x).transform(x)

    def transform(self, valores: list[float]) -> list[float]:
        if self.min_ is None:
            raise ValueError("Llama a fit() antes de transform()")
        rango = self.max_ - self.min_ # 0 si todos los valores son iguales

        return [((v - self.min_) / rango if rango != 0 else 0.0) for v in valores]   # lista NUEVA: no muta la entrada

if __name__ == "__main__":
    scaler = MeanImputer()          # crea una instancia; Python ejecuta __init__
    scaler.fit([None, None, None])        
    print(scaler.transform([0, None])) 
    # scaler = MinMaxScaler()          # crea una instancia; Python ejecuta __init__
    # scaler.fit([10, 20, 30]) 
    # print(scaler.transform([20, 40]))
    # scaler.fit([10, 10, 10])
    # print(scaler.transform([20, 40])) 