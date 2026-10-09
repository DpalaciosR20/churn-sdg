import pytest
import pandas as pd
from pathlib import Path
from churn.pipeline import preparar

def test_preparar(tmp_path):
    df_prueba = pd.DataFrame({
        "Customer_ID": range(10),
        "da_Mean": range(10),
        "eqpdays": range(10),
        "hnd_webcap": [str(x) for x in range(10)],
        "refurb_new": [str(x) for x in range(10)],
        "churn": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    })
    ruta_csv_tmp = tmp_path / "dataset_test.csv"
    df_prueba.to_csv(ruta_csv_tmp, index=False, sep=";", decimal=",")

    dir_salida_tmp = tmp_path
    rutas_generadas = preparar(ruta_csv=ruta_csv_tmp, dir_salida=dir_salida_tmp)

    ruta_train = Path(rutas_generadas["train"])
    ruta_test = Path(rutas_generadas["test"])

    assert ruta_train.exists()
    assert ruta_test.exists()

    train_df = pd.read_parquet(ruta_train)
    test_df = pd.read_parquet(ruta_test)

    indices_train = set(train_df.index)
    indices_test = set(test_df.index)

    assert len(indices_train.intersection(indices_test)) == 0
    assert len(train_df) + len(test_df) == 10
