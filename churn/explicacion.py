import shap
import pandas as pd

def calcular_shap(modelo, X, n_muestra=2000,semilla=42) -> tuple:
    """Regresa (X_muestra, valores): los clientes muestrados y su explicación SHAP, alineados."""
    X_muestra = X.sample(n=min(n_muestra, len(X)), random_state=semilla)
    
    preprocesamiento = modelo[:-1]  # todos los pasos menos el clasificador
    clasificador = modelo [-1]      # el LGBMClassifier ya entrenado

    nombres = preprocesamiento.get_feature_names_out()
    X_transformado = pd.DataFrame(
        preprocesamiento.transform(X_muestra),
        columns=nombres, index=X_muestra.index,
    )

    valores = shap.TreeExplainer(modelo[-1])(X_transformado) # objeto Explanation: .values, .base_values, .data

    return X_muestra, valores
