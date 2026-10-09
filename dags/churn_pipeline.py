import logging
import pendulum
from airflow.sdk import dag, task

log = logging.getLogger(__name__)

@dag(
    schedule="@weekly",                     # Se ejecuta de forma semanal
    start_date=pendulum.datetime(2026, 10, 9, tz="America/Mexico_City"),
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
        from churn import pipeline
        return pipeline.preparar()                 # el valor de retorno viaja por XCom

    @task
    def entrenar_modelo(ruta_train: str) -> str:
        from churn import pipeline
        ruta_modelo = "models/modelo.pkl"
        return pipeline.entrenar(ruta_train, ruta_modelo)
    
    @task
    def evaluar_modelo(ruta_modelo: str, ruta_test:str) -> None:
        from churn import pipeline
        pipeline.evaluar(ruta_modelo, ruta_test)

    datos = preparar_datos()
    evaluar_modelo(entrenar_modelo(datos["train"]), datos["test"])

churn_pipeline()                           # registra el DAG