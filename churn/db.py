import os
import pandas as pd
from sqlalchemy import create_engine, Engine, inspect, text

URL_LOCAL = "postgresql+psycopg2://churn:churn@localhost:5433/churn"

def obtener_engine() -> Engine:
    """Crea y regresa el engine de SQLAlchemy tomando la URL del entorno."""
    return create_engine(os.environ.get("CHURN_DB_URL", URL_LOCAL))

def guardar_tabla(df: pd.DataFrame, tabla: str, engine: Engine, modo: str="replace", index:bool =True) -> None:
    """Guarda un DataFrame completo en la base de datos."""
    df.to_sql(tabla, engine, if_exists=modo, index=index)

def reemplazar_corrida(df: pd.DataFrame, tabla:str, run_id:str, engine: Engine, index:bool = True) -> None:
    """Inserta las filas de una corrida; si esa corrida ya existía, la reemplaza dentro de una transacción."""
    with engine.begin() as conn:        # una transacción: todo o nada
        if inspect(conn).has_table(tabla):
            conn.execute(
                text(f"DELETE FROM {tabla} WHERE run_id = :run_id"),
                {"run_id": run_id},
            )
    
        df.assign(run_id=run_id).to_sql(tabla, conn, if_exists="append", index=index)    

def leer_sql(consulta: str, engine: Engine, parametros:dict=None) -> pd.DataFrame:
    """Ejecuta una consulta SQL de forma segura y regresa un DataFrame."""
    with engine.connect() as conn:
        return pd.read_sql(text(consulta), conn, params=parametros)