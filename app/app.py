# app/app.py
import streamlit as st
import plotly.express as px
from sqlalchemy import inspect

from churn.db import obtener_engine, leer_sql
from churn.etiquetas import etiqueta

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
    tablas_requeridas = {"metricas_modelo", "predicciones", "clientes"}
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
    c4.metric("AUC", f"{m['auc']:.3f}")

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

with tab_contactar:
    st.subheader("Prioriza a quién contactar")
    st.caption(
        "El presupuesto selecciona primero a los clientes con mayor riesgo. "
        "El filtro de ingreso y la exclusión de bajo uso se aplican después."
    )

    col_presupuesto, col_ingreso = st.columns(2)
    with col_presupuesto:
        presupuesto_pct = st.slider(
            "Presupuesto: contactar al X% de mayor riesgo",
            min_value=5,
            max_value=100,
            value=20,
            step=5,
        )
    with col_ingreso:
        ingreso_minimo = st.number_input(
            "Ingreso mensual mínimo (rev_Mean)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            format="%.2f",
        )

    excluir_silenciosos = st.checkbox(
        "Excluir posibles abandonos silenciosos (mou_Mean = 0)",
        value=False,
    )

    clientes_priorizados = consultar(
        """
        WITH clientes_ordenados AS (
            SELECT
                p."Customer_ID",
                p.riesgo,
                p.grupo_riesgo,
                p.churn_real,
                p.factor_1,
                p.factor_2,
                p.factor_3,
                c."rev_Mean",
                c.months,
                c.eqpdays,
                c."mou_Mean",
                ROW_NUMBER() OVER (
                    ORDER BY p.riesgo DESC, p."Customer_ID"
                ) AS posicion_riesgo,
                COUNT(*) OVER () AS total_clientes
            FROM predicciones AS p
            JOIN clientes AS c ON p."Customer_ID" = c."Customer_ID"
        )
        SELECT
            "Customer_ID",
            riesgo,
            grupo_riesgo,
            churn_real,
            factor_1,
            factor_2,
            factor_3,
            "rev_Mean",
            months,
            eqpdays,
            "mou_Mean"
        FROM clientes_ordenados
        WHERE posicion_riesgo <= CEIL(total_clientes * :presupuesto_pct / 100.0)
          AND "rev_Mean" >= :ingreso_minimo
          AND (
              :excluir_silenciosos = FALSE
              OR "mou_Mean" <> 0
              OR "mou_Mean" IS NULL
          )
        ORDER BY posicion_riesgo
        """,
        {
            "presupuesto_pct": presupuesto_pct,
            "ingreso_minimo": ingreso_minimo,
            "excluir_silenciosos": excluir_silenciosos,
        },
    )

    clientes_seleccionados = len(clientes_priorizados)
    churners_seleccionados = int(clientes_priorizados["churn_real"].sum())
    ingreso_en_juego = clientes_priorizados["rev_Mean"].fillna(0).sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Clientes seleccionados", f"{clientes_seleccionados:,}")
    c2.metric("Cancelaron (conjunto de prueba)", f"{churners_seleccionados:,}")
    c3.metric("Ingreso mensual en juego", f"${ingreso_en_juego:,.2f}")
    st.caption(
        "El ingreso en juego es la suma de rev_Mean de los clientes seleccionados; "
        "no equivale a ingreso que una campaña vaya a recuperar. "
        "El dato de cancelación solo se conoce aquí porque son datos de prueba."
    )

    if clientes_priorizados.empty:
        st.info("No hay clientes que cumplan estos filtros.")
    else:
        tabla_contacto = clientes_priorizados.copy()
        tabla_contacto["Motivo principal"] = tabla_contacto["factor_1"].map(etiqueta)
        tabla_contacto["Motivo 2"] = tabla_contacto["factor_2"].map(etiqueta)
        tabla_contacto["Motivo 3"] = tabla_contacto["factor_3"].map(etiqueta)
        tabla_contacto["Señal de uso"] = tabla_contacto["mou_Mean"].map(
            lambda minutos: (
                "Posible abandono silencioso"
                if minutos == 0
                else "Sin señal de uso nulo"
            )
        )
        tabla_contacto["Canceló (prueba)"] = tabla_contacto["churn_real"].map(
            {1: "Sí", 0: "No"}
        )
        tabla_contacto = tabla_contacto.rename(
            columns={
                "Customer_ID": "Customer ID",
                "riesgo": "Riesgo",
                "grupo_riesgo": "Grupo de riesgo",
                "rev_Mean": "Ingreso mensual promedio",
                "months": "Meses como cliente",
                "eqpdays": "Días con el teléfono actual",
                "mou_Mean": "Minutos de uso mensual",
            }
        )
        columnas = [
            "Customer ID",
            "Riesgo",
            "Grupo de riesgo",
            "Canceló (prueba)",
            "Ingreso mensual promedio",
            "Meses como cliente",
            "Días con el teléfono actual",
            "Minutos de uso mensual",
            "Señal de uso",
            "Motivo principal",
            "Motivo 2",
            "Motivo 3",
        ]
        tabla_contacto = tabla_contacto[columnas]

        st.dataframe(
            tabla_contacto,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Riesgo": st.column_config.ProgressColumn(
                    "Riesgo de cancelación",
                    format="percent",
                    min_value=0.0,
                    max_value=1.0,
                ),
                "Ingreso mensual promedio": st.column_config.NumberColumn(
                    format="$%.2f"
                ),
            },
        )
        st.download_button(
            "Descargar lista en CSV",
            data=tabla_contacto.to_csv(index=False, sep=";").encode("utf-8-sig"),
            file_name="clientes_priorizados.csv",
            mime="text/csv",
        )
