# app/app.py
import streamlit as st
import plotly.express as px
from sqlalchemy import inspect

from churn.db import obtener_engine, leer_sql

st.set_page_config(page_title="Retención de clientes", layout="wide")


@st.cache_resource
def engine():
    return obtener_engine()


@st.cache_data(ttl=300)
def consultar(sql: str, parametros: dict | None = None):
    return leer_sql(sql, engine(), parametros)


st.title("Retención de clientes")
st.caption("Riesgo de cancelación entre 31 y 60 días después de la fecha de observación.")

tab_resumen, tab_contactar, tab_ficha, tab_drivers = st.tabs(
    ["Resumen", "A quién contactar", "Ficha del cliente", "Qué mueve el churn"]
)

with tab_resumen:
    tablas_requeridas = {"metricas_modelo", "predicciones"}
    tablas_disponibles = set(inspect(engine()).get_table_names())
    tablas_faltantes = tablas_requeridas - tablas_disponibles

    if tablas_faltantes:
        st.info("Aún no hay resultados; ejecuta el DAG `churn_pipeline`.")
        st.stop()

    metricas = consultar(
        "SELECT * FROM metricas_modelo ORDER BY fecha DESC LIMIT 1"
    )
    tasa_general = consultar(
        "SELECT AVG(churn_real) AS tasa_churn FROM predicciones"
    )
    ganancias = consultar("""
        SELECT grupo_riesgo, COUNT(*) AS clientes, AVG(churn_real) AS tasa_churn
        FROM predicciones
        GROUP BY grupo_riesgo
        ORDER BY grupo_riesgo
    """)
    historial_auc = consultar("""
        SELECT run_id, fecha, auc
        FROM metricas_modelo
        ORDER BY fecha ASC
    """)

    if metricas.empty or ganancias.empty or tasa_general.empty or historial_auc.empty:
        st.info("Aún no hay resultados; ejecuta el DAG `churn_pipeline`.")
        st.stop()

    m = metricas.iloc[0]
    promedio_churn = tasa_general.loc[0, "tasa_churn"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientes evaluados", f"{int(m['n_clientes']):,}")
    c2.metric("Aciertos en el 10% de mayor riesgo", f"{m['precision_at_10']:.0%}")
    c3.metric("Veces mejor que al azar", f"{m['lift_at_10']:.2f}x")
    c4.metric("AUC", f"{m['auc']:.0}")

    st.info(
        f"Si contactamos al 10% de clientes con mayor riesgo, "
        f"{m['precision_at_10'] * 100:.0f} de cada 100 realmente se iban, "
        f"contra {promedio_churn:.0%} al azar."
    )

    st.subheader("El modelo ordena a los clientes por riesgo")
    fig_ganancias = px.bar(
        ganancias,
        x="grupo_riesgo",
        y="tasa_churn",
        labels={
            "grupo_riesgo": "Grupo de riesgo (1 = mayor riesgo)",
            "tasa_churn": "Tasa de cancelación",
        },
        hover_data=["clientes"],
    )
    fig_ganancias.add_hline(
        y=promedio_churn,
        line_dash="dash",
        annotation_text=f"Promedio general: {promedio_churn:.1%}",
    )
    fig_ganancias.update_yaxes(tickformat=".0%", range=[0, 1])
    st.plotly_chart(fig_ganancias, use_container_width=True)

    st.subheader("Historial de AUC por corrida")
    fig_historial = px.line(
        historial_auc,
        x="fecha",
        y="auc",
        markers=True,
        hover_data=["run_id"],
        labels={"fecha": "Fecha", "auc": "AUC"},
    )
    fig_historial.update_yaxes(tickformat=".3f", range=[0, 1])
    st.plotly_chart(fig_historial, use_container_width=True)

