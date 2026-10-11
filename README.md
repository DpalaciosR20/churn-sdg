# Predicción de churn de clientes

Proyecto de prueba técnica para estimar qué clientes podrían cancelar su servicio. El pipeline prepara los datos, entrena y evalúa un modelo LightGBM, genera predicciones y persiste los resultados en PostgreSQL. Airflow orquesta el pipeline y una aplicación Streamlit permite explorar sus resultados.

La aplicación estima el riesgo de cancelación entre 31 y 60 días después de la fecha de observación. Está pensada como una herramienta de priorización y análisis, no como una decisión automática sobre clientes.

## Resultados principales

En el conjunto de prueba, el modelo LightGBM obtuvo **AUC 0.68** y **78 % de precision@10%**: entre los clientes del decil de mayor riesgo, 78 de cada 100 cancelaron. La comparación fue **58 %** con la regla basada en antigüedad del teléfono y **50 %** al azar. El conjunto usado está balanceado; estas tasas no deben interpretarse como prevalencia ni precisión esperada en producción.

Hallazgos exploratorios principales:

- **Antigüedad del teléfono:** la tasa observada de churn sube de ~37 % a ~61 % cuando el equipo supera unos 300 días.
- **Antigüedad del cliente:** los meses 11–12 muestran un pico de churn de 61.9 %.
- **Uso de minutos:** los clientes con 0–48 minutos mensuales tienen casi 60 % de churn observado; la tasa baja a ~52 % entre 48–115 minutos.

Son asociaciones en estos datos, no evidencia de que renovar un teléfono, contactar en el mes 10 o aumentar el uso cause una reducción del churn. Las recomendaciones proponen validar acciones mediante experimentos con grupo de control.

## Arquitectura

![Diagrama de arquitectura: pipeline de churn con Airflow, PostgreSQL y Streamlit](docs/arquitectura.svg)

## Estructura del repositorio

| Ruta | Contenido |
| --- | --- |
| [`churn/`](churn/) | Paquete Python con preparación de datos, preprocesamiento, entrenamiento, evaluación, métricas, explicabilidad y acceso a PostgreSQL. |
| [`dags/`](dags/) | DAG `churn_pipeline`, que orquesta preparación, entrenamiento, evaluación y generación de predicciones en Airflow. |
| [`app/`](app/) | Aplicación Streamlit para consultar métricas, priorizar clientes y explorar predicciones y factores. |
| [`notebooks/`](notebooks/) | Análisis exploratorio, calidad de datos, baselines, modelo final y explicabilidad. |
| [`tests/`](tests/) | Pruebas unitarias y de integración para los componentes del paquete. |
| [`docs/`](docs/) | Consultas SQL, decisiones de arquitectura y producto, recomendaciones de negocio y diagrama. |

## Documentación del proyecto

- [Registro de decisiones](docs/registro_decisiones.md): alternativas consideradas, decisiones técnicas, métricas del modelo y limitaciones conocidas.
- [Recomendaciones de negocio](docs/recomendaciones.md): hipótesis de retención, evidencia exploratoria, acciones propuestas y cómo medirlas.
- [Consultas SQL](docs/consultas.sql): ejemplos para explorar los datos persistidos.

## Servicios

| Servicio | Uso | Dirección local |
| --- | --- | --- |
| Airflow | Ejecutar y monitorear el pipeline | <http://localhost:8080> |
| Adminer | Explorar las bases de datos | <http://localhost:8081> |
| Streamlit | Consultar métricas, clientes y factores asociados | <http://localhost:8501> |

## Requisitos

- Docker y Docker Compose.
- Al menos 4 GB de memoria disponibles para Docker; Airflow puede requerir más según los recursos de la máquina.

## Pruebas y ejecución local

Con Python 3.12 y las dependencias instaladas, ejecuta las pruebas desde la raíz del repositorio:

```bash
pip install -r requirements.txt
PYTHONPATH=. pytest -q
```

Para ejecutar el pipeline directamente, sin el orquestador Airflow:

```bash
mkdir -p data models logs
# Coloca el archivo de entrada en data/dataset.csv
docker compose up -d churn-db
set -a
. ./.env
set +a
export CHURN_DB_URL="postgresql+psycopg2://${CHURN_DB_USER}:${CHURN_DB_PASSWORD}@localhost:5433/${CHURN_DB}"
PYTHONPATH=. python -m churn.pipeline
```

Este modo requiere que hayas creado `.env` siguiendo los pasos de inicio rápido, que PostgreSQL esté disponible en `localhost:5433` y que las credenciales permitan crear o reemplazar las tablas de resultados. Para esta forma de cargar `.env` en la terminal, usa valores compatibles con asignaciones de shell y una contraseña segura sin caracteres reservados de URL (o codifica esos caracteres antes de construir `CHURN_DB_URL`). Ejecuta el pipeline contra una base de desarrollo: reemplaza tablas de resultados y genera artefactos en `data/` y `models/`.

## Inicio rápido

1. Clona el repositorio y entra en la carpeta:

   ```bash
   git clone https://github.com/DpalaciosR20/churn-sdg.git
   cd churn-sdg
   ```

2. Crea las carpetas que usa Docker para datos, modelos y logs:

   ```bash
   mkdir -p data models logs
   ```

   Se crean antes de iniciar los contenedores para que los archivos montados no queden como propiedad de `root`.

3. Coloca el archivo de datos **`dataset.csv`** dentro de la carpeta **`data/`** del proyecto. La ruta completa debe ser `data/dataset.csv`. Este archivo no está incluido en el repositorio; obtén el CSV de datos proporcionado para el proyecto y cópialo ahí.

4. Crea tu archivo local de configuración a partir de la plantilla:

   ```bash
   cp .env.example .env
   ```

   Edita `.env` y reemplaza los valores de ejemplo:

   ```bash
   id -u
   ```

   Copia el número que imprime `id -u` en `AIRFLOW_UID`. Elige los valores de `CHURN_DB_USER`, `CHURN_DB_PASSWORD` y `CHURN_DB`: son las credenciales y el nombre de la base de datos del proyecto, y puedes elegirlos libremente. Usa los mismos valores en cada variable correspondiente. No compartas ni subas `.env`, porque contiene credenciales.

5. Construye las imágenes e inicia los servicios:

   ```bash
   docker compose up -d --build
   ```

6. Revisa el estado:

   ```bash
   docker compose ps
   ```

7. Abre Airflow en <http://localhost:8080> e inicia sesión con `airflow` / `airflow` (valores locales predeterminados). En la lista de DAGs, busca **`churn_pipeline`** y activa su interruptor: los DAGs nuevos nacen en pausa. Después, ejecútalo con el botón de iniciar/trigger y espera a que termine correctamente.

8. Abre Streamlit en <http://localhost:8501>. La app lee los resultados que el DAG guardó en PostgreSQL; no ejecuta el entrenamiento al abrir cada página.

### Conectarse con Adminer

Abre <http://localhost:8081> y completa el formulario de inicio de sesión:

- **Sistema:** PostgreSQL
- **Servidor:** `churn-db`
- **Usuario:** el valor de `CHURN_DB_USER` en `.env`
- **Contraseña:** el valor de `CHURN_DB_PASSWORD` en `.env`
- **Base de datos:** el valor de `CHURN_DB` en `.env`

El servidor `churn-db` es el nombre del servicio dentro de la red de Docker Compose. Desde tu computadora, la base de datos se publica en `localhost:5433`.

## Cómo explorar la aplicación

- **Resumen:** revisa el volumen evaluado, AUC y desempeño en el 10 % de mayor riesgo. Las métricas y la tasa de cancelación observada corresponden al conjunto de prueba; no necesariamente representan la prevalencia de churn en producción.
- **A quién contactar:** el porcentaje de presupuesto selecciona primero a los clientes de mayor riesgo. Los filtros de ingreso y de uso se aplican después. La suma de ingreso mostrada es ingreso mensual asociado a los clientes seleccionados, no un monto que una campaña vaya a recuperar.
- **Ficha del cliente:** consulta riesgo y factores principales para clientes entre los 200 de mayor riesgo. El churn real solo se muestra porque los registros disponibles pertenecen al conjunto de prueba; en una campaña real ese resultado futuro aún no se conocería.
- **Qué mueve el churn:** compara factores SHAP y tasas observadas por grupos de variables. Las relaciones son asociaciones, no causas; una acción de retención debe evaluarse con un grupo de control antes de escalarse.

## Comandos útiles

```bash
# Ver todos los servicios
docker compose ps

# Ver logs de la aplicación
docker compose logs -f app

# Ver logs de una tarea de Airflow
docker compose logs -f airflow-scheduler

# Detener los servicios sin borrar los datos persistidos
docker compose down
```

Los datos de PostgreSQL viven en volúmenes de Docker y permanecen al detener los servicios con `docker compose down`.

## Limitaciones y siguientes pasos

- **Dataset balanceado:** la evaluación usa una muestra con 50 % de churn. En producción, donde la tasa base de cancelación probablemente sea menor, la precision observada puede bajar; se necesitarían datos representativos y calibración de probabilidades.
- **Split aleatorio:** train y test se separan aleatoriamente. Para estimar mejor el desempeño futuro, conviene evaluar también con una separación temporal que simule predecir periodos posteriores.
- **Sin MLflow:** el seguimiento de experimentos, parámetros, artefactos y versiones de modelos todavía no está integrado.
- **Sin monitoreo en producción:** faltan seguimiento de calidad y deriva de datos, desempeño con resultados reales, alertas y un proceso formal de recalibración o reentrenamiento.
- **Acciones aún no validadas:** las recomendaciones son hipótesis basadas en asociaciones observadas. Antes de escalar campañas, medir el efecto causal con grupos de control y evaluar el ROI.
