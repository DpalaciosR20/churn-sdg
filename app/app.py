# app/app.py
import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import inspect

from churn import config
from churn.db import obtener_engine, leer_sql
from churn.etiquetas import columna_factor, etiqueta
from churn.eda import tasa_por_decil

st.set_page_config(page_title="Retención de clientes", layout="wide")


@st.cache_resource
def engine():
    return obtener_engine()


@st.cache_data(ttl=300)
def consultar(sql: str, parametros: dict | None = None):
    return leer_sql(sql, engine(), parametros)


@st.cache_data(ttl=300)
def consultar_tasa_por_decil(variable: str) -> pd.DataFrame:
    if variable not in config.NUM_COLS:
        raise ValueError(f"Variable no permitida para el análisis por deciles: {variable}")

    datos = consultar(f'SELECT "{variable}", churn FROM clientes')
    return tasa_por_decil(datos, variable)


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

with tab_ficha:
    st.subheader("Ficha individual del cliente")

    clientes_ficha = consultar("""
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
            c.change_mou,
            c.hnd_price,
            c."ovrrev_Mean",
            c.uniqsubs,
            c."drop_vce_Mean",
            c."totmrc_Mean",
            c.change_rev,
            c.infobase,
            c.phones,
            c.asl_flag,
            c."drop_blk_Mean"
        FROM predicciones AS p
        JOIN clientes AS c ON p."Customer_ID" = c."Customer_ID"
        ORDER BY p.riesgo DESC, p."Customer_ID"
        LIMIT 200
    """)

    if clientes_ficha.empty:
        st.info("Aún no hay clientes con predicciones; ejecuta el DAG `churn_pipeline`.")
    else:
        customer_id = st.selectbox(
            "Selecciona un cliente entre los 200 de mayor riesgo",
            options=clientes_ficha["Customer_ID"].tolist(),
            format_func=lambda customer: (
                f"{customer} — riesgo "
                f"{clientes_ficha.loc[clientes_ficha['Customer_ID'] == customer, 'riesgo'].iloc[0]:.1%}"
            ),
        )
        cliente = clientes_ficha.loc[
            clientes_ficha["Customer_ID"] == customer_id
        ].iloc[0]

        riesgo = float(cliente["riesgo"])
        cancelado = "Sí" if int(cliente["churn_real"]) == 1 else "No"
        c1, c2, c3 = st.columns(3)
        c1.metric("Riesgo estimado", f"{riesgo:.1%}")
        c2.metric("Grupo de riesgo", f"{int(cliente['grupo_riesgo'])} de 10")
        c3.metric("Canceló (conjunto de prueba)", cancelado)
        st.caption(
            "El resultado real solo está disponible porque esta ficha usa el conjunto "
            "de prueba. En una campaña real todavía no se conocería."
        )

        factores = [str(cliente[f"factor_{numero}"]) for numero in range(1, 4)]
        nombres_factores = [etiqueta(factor) for factor in factores]

        st.markdown("**Factores principales y valores del cliente**")
        for factor, nombre in zip(factores, nombres_factores):
            columna = columna_factor(factor)
            valor = cliente.get(columna)

            if pd.isna(valor):
                valor_texto = "Sin dato"
            elif columna == "eqpdays":
                valor_texto = f"{float(valor):,.0f} días"
            elif columna == "months":
                valor_texto = f"{int(valor)} meses"
            elif columna in {"rev_Mean", "hnd_price", "ovrrev_Mean", "totmrc_Mean"}:
                valor_texto = f"${float(valor):,.2f}"
            elif columna == "mou_Mean":
                valor_texto = f"{float(valor):,.1f} minutos al mes"
            else:
                valor_texto = str(valor)

            if columna != factor:
                categoria = factor.removeprefix(f"{columna}_")
                valor_texto = f"{valor_texto} (factor asociado a «{categoria}»)"

            st.write(f"- **{nombre}:** {valor_texto}")

        explicacion = ", ".join(nombres_factores)
        st.info(
            f"Este cliente tiene un riesgo de {riesgo:.0%}, "
            f"principalmente por: {explicacion}."
        )

        if cliente["mou_Mean"] == 0:
            st.warning(
                "Posible abandono silencioso: el uso mensual de minutos es cero. "
                "El modelo estima riesgo, pero este cliente quizá ya dejó de usar el servicio."
            )

with tab_drivers:
    st.subheader("Qué mueve el churn")
    st.warning(
        "Estas relaciones muestran asociación, no causa. Antes de escalar una acción, "
        "hay que medirla con un grupo de control."
    )

    if not inspect(engine()).has_table("importancia_variables"):
        st.info("Aún no hay resultados; ejecuta el DAG `churn_pipeline`.")
    else:
        importancia = consultar("""
            SELECT variable, importancia
            FROM importancia_variables
            ORDER BY importancia DESC
            LIMIT 10
        """)

        if importancia.empty:
            st.info("Aún no hay importancias calculadas; ejecuta el DAG `churn_pipeline`.")
        else:
            importancia["etiqueta"] = importancia["variable"].map(etiqueta)
            importancia = importancia.sort_values("importancia", ascending=True)
            fig_importancia = px.bar(
                importancia,
                x="importancia",
                y="etiqueta",
                orientation="h",
                labels={
                    "importancia": "Importancia media SHAP",
                    "etiqueta": "Factor",
                },
                hover_data={"variable": True, "importancia": ":.3f"},
            )
            fig_importancia.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_importancia, use_container_width=True)

            variable = st.selectbox(
                "Explora la tasa de churn por decil",
                options=config.NUM_COLS,
                format_func=etiqueta,
            )
            tabla_deciles = consultar_tasa_por_decil(variable).reset_index()
            nombre_intervalo = tabla_deciles.columns[0]
            tabla_deciles["grupo"] = tabla_deciles[nombre_intervalo].map(
                lambda intervalo: (
                    "Sin dato"
                    if pd.isna(intervalo)
                    else f"{intervalo.left:,.2f} a {intervalo.right:,.2f}"
                )
            )
            tasa_general_clientes = consultar(
                "SELECT AVG(churn) AS tasa_churn FROM clientes"
            ).loc[0, "tasa_churn"]

            fig_deciles = px.bar(
                tabla_deciles,
                x="grupo",
                y="tasa_churn",
                error_y="margen_ic",
                custom_data=["n_clientes"],
                labels={
                    "grupo": etiqueta(variable),
                    "tasa_churn": "Tasa de cancelación",
                },
            )
            fig_deciles.update_traces(
                hovertemplate=(
                    "%{x}<br>Tasa de cancelación: %{y:.1%}"
                    "<br>Clientes: %{customdata[0]:,}<extra></extra>"
                )
            )
            fig_deciles.add_hline(
                y=tasa_general_clientes,
                line_dash="dash",
                annotation_text=f"Promedio general: {tasa_general_clientes:.1%}",
            )
            fig_deciles.update_yaxes(tickformat=".0%", range=[0, 1])
            fig_deciles.update_xaxes(tickangle=-35)
            st.plotly_chart(fig_deciles, use_container_width=True)
            st.caption(
                "Los grupos se forman con los valores disponibles de la variable. "
                "Si hay muchos valores repetidos, pueden resultar menos de diez deciles; "
                "los datos faltantes aparecen como «Sin dato»."
            )
