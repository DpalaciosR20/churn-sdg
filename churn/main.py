from mini_churn import metricas, preprocesamiento

if __name__ == "__main__":
    y_true_r1=[1,0,1,1,0,0,1,0]
    scores_r1=[0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2]
    r1 = metricas.precision_at_k(
        y_true=y_true_r1,
        scores=scores_r1,
        k=3
    )
    y_true_r2=[1,0,1,1,0,0,1,0]
    scores_r2=[0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2]
    r2 = metricas.precision_at_k(
        y_true=y_true_r2,
        scores=scores_r2,
        k=4
    )
    y_true_r3=[0,1,1,0]
    scores_r3=[0.1,0.9,0.4,0.8]
    print("y_true_r3 antes:", y_true_r3)
    print("scores_r3 antes:", scores_r3)
    r3 = metricas.precision_at_k(
        y_true_r3,
        scores_r3,
        k=2
    )
    print(f"""- Pruebas de metricas.py:
        1) {r1:.3f}
        2) {r2:.2f}
        3) {r3:.1f}
        """
    )
    print("y_true_r3 después:", y_true_r3)
    print("scores_r3 después:", scores_r3)

    mean_imputer = preprocesamiento.MeanImputer()
    mean_imputer.fit([10, None, 30])
    r1_imputer = mean_imputer.transform([None, 5])
    print(f"""- Pruebas de preprocesamiento.py
        1) {r1_imputer}
    """)