# Predicción de churn de clientes

Proyecto de prueba técnica para estimar qué clientes podrían cancelar su servicio. El pipeline prepara los datos, entrena y evalúa un modelo LightGBM, genera predicciones y persiste los resultados en PostgreSQL. Airflow orquesta el pipeline y una aplicación Streamlit permite explorar sus resultados.

La aplicación estima el riesgo de cancelación entre 31 y 60 días después de la fecha de observación. Está pensada como una herramienta de priorización y análisis, no como una decisión automática sobre clientes.

## Servicios

| Servicio | Uso | Dirección local |
| --- | --- | --- |
| Airflow | Ejecutar y monitorear el pipeline | <http://localhost:8080> |
| Adminer | Explorar las bases de datos | <http://localhost:8081> |
| Streamlit | Consultar métricas, clientes y factores asociados | <http://localhost:8501> |

## Requisitos

- Docker y Docker Compose.
- Al menos 4 GB de memoria disponibles para Docker; Airflow puede requerir más según los recursos de la máquina.

## Inicio rápido

1. Clona el repositorio y entra en la carpeta:

   ```bash
   git clone https://github.com/DpalaciosR20/churn-sdg.git
   cd churn-sdg
   ```

2. Crea tu archivo local de configuración a partir de la plantilla:

   ```bash
   cp .env.example .env
   ```

   Edita `.env` y reemplaza los valores de ejemplo para `AIRFLOW_UID`, `CHURN_DB_USER`, `CHURN_DB_PASSWORD` y `CHURN_DB`. No compartas ni subas este archivo: puede contener credenciales. Para un entorno persistente, configura también una `FERNET_KEY` única para Airflow.

3. Construye las imágenes e inicia los servicios:

   ```bash
   docker compose up -d --build
   ```

4. Revisa el estado:

   ```bash
   docker compose ps
   ```

5. Abre Streamlit en <http://localhost:8501>. Para generar o actualizar los datos que consume la app, abre Airflow en <http://localhost:8080>, inicia el DAG del proyecto y espera a que termine correctamente. La app lee los datos persistidos en PostgreSQL; no ejecuta el entrenamiento al abrir cada página.

Airflow usa por defecto el usuario y contraseña `airflow` / `airflow` en este Compose local; puedes cambiarlos con `_AIRFLOW_WWW_USER_USERNAME` y `_AIRFLOW_WWW_USER_PASSWORD` en `.env`.

## Cómo explorar la aplicación

- **Resumen:** revisa el volumen evaluado, AUC y desempeño en el 10 % de mayor riesgo. Las métricas y la tasa de cancelación observada corresponden al conjunto de prueba; no necesariamente representan la prevalencia de churn en producción.
- **A quién contactar:** el porcentaje de presupuesto selecciona primero a los clientes de mayor riesgo. Los filtros de ingreso y de uso se aplican después. La suma de ingreso mostrada es ingreso mensual asociado a los clientes seleccionados, no un monto que una campaña vaya a recuperar.
- **Ficha del cliente:** consulta riesgo y factores principales para clientes entre los 200 de mayor riesgo. El churn real solo se muestra porque los registros disponibles pertenecen al conjunto de prueba; en una campaña real ese resultado futuro aún no se conocería.
- **Qué mueve el churn:** compara factores SHAP y tasas observadas por grupos de variables. Las relaciones son asociaciones, no causas; una acción de retención debe evaluarse con un grupo de control antes de escalarse.

## Comandos útiles

```bash
# Ver logs de la aplicación
docker compose logs -f app

# Detener los servicios sin borrar los datos persistidos
docker compose down
```

Los datos de PostgreSQL viven en volúmenes de Docker y permanecen al detener los servicios con `docker compose down`.
