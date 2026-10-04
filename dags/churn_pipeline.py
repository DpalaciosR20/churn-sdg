import logging
import pendulum
from airflow.sdk import dag, task

log = logging.getLogger(__name__)

@dag(
    schedule="@weekly",                     # Se ejecuta de forma semanal
    start_date=pendulum.datetime(2026, 10, 3, tz="America/Mexico_City"),
    catchup=False,                     # no "recuperar" ejecuciones pasadas desde start_date
    tags=["churn"],
    default_args={
        "retries": 2,
        "retry_delay": pendulum.duration(seconds=10)
    }
)
def churn_pipeline():

    @task
    def preparar_datos() -> dict:
        datos = {
            "train": "data/train.parquet",
            "test": "data/test.parquet"
        }
        return datos                 # el valor de retorno viaja por XCom

    @task
    def entrenar_modelo(datos: dict) -> str:
        ruta_modelo = "models/modelo.pkl"
        return ruta_modelo
    
    @task
    def evaluar_modelo(datos: dict, ruta_modelo:str) -> None:
        from churn.metricas import precision_at_k
        t1 = precision_at_k(
            y_true=[1,0,1,1,0,0,1,0],
            scores=[0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2],
            k=3
        )
        log.info(f"precision_at_k(t1) = {t1:.2f}")
        t2 = precision_at_k(
            y_true=[1,0,1,1,0,0,1,0],
            scores=[0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2],
            k=4
        )
        log.info(f"precision_at_k(t2) = {t2:.2f}")
        t3 = precision_at_k(
            y_true=[0,1,1,0],
            scores=[0.1,0.9,0.4,0.8],
            k=2
        )
        log.info(f"precision_at_k(t3) = {t3:.2f}")

    datos = preparar_datos()
    evaluar_modelo(datos,entrenar_modelo(datos))

churn_pipeline()                           # registra el DAG