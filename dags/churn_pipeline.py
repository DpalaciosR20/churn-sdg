import logging
import pendulum
from airflow.sdk import dag, task, get_current_context

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
        return pipeline.entrenar(ruta_train)
    
    @task
    def evaluar_modelo(ruta_test:str, ruta_modelo:str) -> dict:
        from churn import pipeline
        from airflow.sdk import get_current_context
        run_id = get_current_context()["run_id"]
        return pipeline.evaluar(ruta_test, ruta_modelo, run_id)

    @task
    def generar_predicciones(ruta_test:str, ruta_modelo:str):
        from churn import pipeline
        pipeline.predecir(ruta_test, ruta_modelo)
    
    datos = preparar_datos()
    ruta_modelo = entrenar_modelo(datos["train"])
    evaluacion = evaluar_modelo(datos["test"], ruta_modelo)
    predicciones = generar_predicciones(datos["test"], ruta_modelo)
    evaluacion >> predicciones

churn_pipeline()                           # registra el DAG