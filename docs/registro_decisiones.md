## D-001 - Pandas o Polars
Fecha: 29/09/2026
Contexto: Qué herramienta para la manipulación de datos usaré?
Opciones consideradas: Polars (lo conozco, más rápido), Pandas (estándar en la industria).
Decisión: Pandas
Justificación: scikit-learn, SHAP y la mayoría de la documentación y ejemplos asumen pandas; con 100k de filas el rendimiento de Polars no es necesario; además, pandas es el que más se usa en la industria.
Consecuencias / riesgos: curva de aprendizaje -> mi lógica de Poalrs se transfiere casi directo (Agrupar, agregar, filtrar); si una opereación se vuelve lenta, se puede optimizar después.

## D-002 - Alcance del MVP
Fecha: 29/09/2026
Opciones: (A) solo lo que pide el PDF · (B) PDF más extensiones seleccionadas · (C) todas las extensiones.
Decisión: B. Lo que entra es la lista Must de la sección 8.
Justificación: el PDF exige el DAG y el análisis; la entrevista pidió una interfaz web; PostgreSQL alimenta esa interfaz. Todo lo demás no cabe con calidad en el tiempo disponible.
Riesgos y mitigación: que la solución parezca básica → presentar explícitamente la sección Won't como hoja de ruta (el PDF valora proponer lo que se haría con más tiempo).

## D-003 - Plan de estudio y punto de revisión
Fecha: 29/09/2026
Contexto:voy uns 3 días atrás del calendario original.
Opciones: (A) plan comprimido desde ya · (B) mantener el alcance original con horas extra y un punto de revisión.
Decisión: B, con revisión el domingo 4 de octubre por la noche.
Criterio: si Airflow corre y el EDA está terminado, se mantiene el alcance; si no, pasamos al plan comprimido y MLflow sale.

## D-004 - Versión de Apache Airflow
Fecha: 03/10/2026
Contexto: El PDF muestra Airflow 2.2.5, pero la versión estable actual es la 3.3.2, con cambios importantes (api-server en lugar de webserver, dag-processor separado, imports desde airflow.sdk).
Opciones consideradas: (A) Airflow 2.x, como en el PDF, (B) Airflow 3.x usando la URL "stable", (C) Airflow 3.3.2 fijo.
Decisión: (C) Airflow 3.3.2 fijo.
Justificación: Usar la versión actual me ayudaa a adaptarme a una tecnología nueva. Fijar la versión garantiza reproducibilidad: "stable" cambia con el tiempo y una actualización podría romper el proyecto antes de la presentación.
Consecuencias / riesgos: La documentación y los tutoriales de Airflow 2 no aplican tal cual. Se mitiga usando la documentación oficial de la 3.3.2.

## D-005 - Cómo accede Airflow al paquete churn
Fecha: 03/10/2026
Contexto: Al intentar usar un módulo del paquete churn/ en un DAG, apareció un error de importación (ModuleNotFoundError: No module named 'churn') indicando que no se encontraba el módulo. El error era que el contendor no estaba viendo la ruta de churn/ y, además, había un problema con dónde busca Python los paquetes, no estaba ahí en el syspath la ruta del paquete churn/.
Opciones consideradas: (A) Copiar el código del paquete dentro de dags/, (B) Moverlo a plugins/, que Airflow agrega a sys.path automáticamente, (C) montar churn/ como volumen y declarar PYTHONPATH, (D) Construir una imagen propia Airflow con el paquete instalado.
Decisión: (C) montar churn/ como volumen y declarar PYTHONPATH. El volumen ./churn:/opt/airflow/churn y PYTHONPATH=/opt/airflow, ambos en el bloque compartido x-airflow-common
Justificación: Este mismo paquete de churn/ lo usan mis tests así que, para no tener código duplicado, ayuda tenerlo en una misma carpeta, además, tenerlo en un volumen, ayuda a que los cambios se vean al instante sin reconstruir nada así que eso ahorra tiempo. plugins/ es una carpeta para extender Airflow, no para la lógica de negocio; los tests tendrías que iportar desde una carpeta de Airflow.Usar ina imagen propia es la opción correcta para producción, pero en desarrollo obliga a reconstruir la imagen con cada cambio.
Riesgos: Al estar trabajando con ramas en git para el control de versiones, si cambio de rama y la carpeta se borra y se recrea, se perderá visibilidad de este paquete; para esto deberé hacer 'docker compose down' y 'up -d' después de cambiar de rama. En un entorno real, sin carpetas compartidas, este enfoque no ayudaría porque no se tendría la visibilidad de manera directa, sin reconstruir, de este paquete; ahí se usaría la opción D (imagen con el paquete instalado).Esta solución aplica para el contexto del proyecto actual.

## D-006 - Cómo leer el CSV con pandas
Fecha: 04/10/2026
Contexto: Al procesar el CSV con pd.read_csv con la lectura de valores NaN por defecto, se observó que desaparecía un grupo de la columna `hnd_webcap`.
Decisión: Se optó por leer el conjunto de datos con keep_default_na=False y na_values=[""] para que no se perdiera esta categoría y sólo se consideraran los campos vacíos como NaN.
Riesgos: Si el archivo tuviera otras formas de marcar faltantes ("NULL", "N/A"), ya no se detectarían. Comparé la carga cruda contra la normal y solo "NA" estaba en ese caso.


## D-007 - Cómo corregir problema de grupo de nulos en churn.eda.tasa_por_decil()
Fecha: 04/10/2026
Contexto: Al querer sacar un ranking de señal (rango de la tasa entre deciles) entre las variables numéricas (excepto churn y Customer_ID) me encontré con que al usar dropna=False, eso hacía que se agregara un grupo más: el de los clientes con la variable vacía. Una tasa calculada con un cliente no significa nada, pero el máximo y el mínimo son muy sensibles a esos valores.
Opciones: (A) Para el ranking, ignorar el grupo de nulos y analizar los nulos por separado. (B) Ignorar cualquier grupo con menos de cierto número de clientes (por ejemplo, 100) al calcular máximo y mínimo.
Decisión: (A) Para el ranking, ignorar el grupo de nulos y analizar los nulos por separado.
Justificación: Ignorar cualquier grupo con menos de cierto número de clientes implica un riesgo de no saber exactamente qué número sería el ideal. Ignorar el grupo de nulos para el ranking soluciona el proble para este caso y deja abierto el poder seguir considerando nulos más adelante para otras tareas. Coloqué una variable auxiliar en la fucnión para psar si se usa dropna False o True.

## D-008 - Selección de variables por familia y prevención de multicolinealidad
Fecha: 04/10/2026
Contexto: El dataset presenta alta redundancia entre variables (pares con correlación Spearman > 0.9, ej. minutos vs. conteo de llamadas) y variables acumuladas (totmou, adjrev) que esconden la antigüedad del cliente. Mezclan el gasto con la antigüedad (confusión y redundancia con months)
Opciones consideradas: (1) Mantener todas las columnas y confiar en los árboles del modelo. (2) Quedarse con las variables de mayor señal estadística plana (totales y ajustadas). (3) Elegir un representante por familia de comportamiento priorizando métricas mensuales, nivel de señal, ausencia de nulos y explicabilidad de negocio.
Decisión: Seleccionar métricas promedio/mensuales por familia (rev_Mean, mou_Mean, ovrrev_Mean, comp_dat_Mean, custcare_Mean, phones), descartando la familia de conteo de llamadas (por redundancia con minutos) y todas las métricas acumuladas. Se conservan las variables independientes o "huérfanas" (months, change_mou, etc.).
Justificación: Las variables acumuladas inflan su importancia porque contienen implícitamente la antigüedad del cliente (el principal factor de supervivencia). Eliminar la multicolinealidad y preferir promedios mensuales garantiza que el negocio pueda interpretar el modelo de forma directa ("cuánto paga o habla al mes el cliente") y que la herramienta SHAP no diluya la importancia de las características entre variables redundantes.
Consecuencias / riesgos: Se descartan columnas altamente correlacionadas entre sí, lo que podría reducir muy marginalmente el poder predictivo bruto.

## D-009 - Tratamiento de valores negativos (imposibles)
Fecha: 04/10/2026
Contexto: Durante la exploración se encontraron valores numéricos que violan las reglas de negocio: días de edad del equipo (eqpdays) por debajo de cero e ingresos y cargos (rev_Mean, totmrc_Mean, avg6rev) negativos.
Opciones consideradas: (1) Transformar todos los negativos en nulos (NaN) para imputación algorítmica. (2) Llevarlos a 0. (3) Eliminar las filas.
Decisión: Aplicar un límite inferior de cero para la variable eqpdays y transformar todos los negativos en nulos (NaN) para imputación algorítmica en ingresos y egresos con negativos.
Justificación: En eqpdays, los negativos son pocos y cercanos a cero; se asume que representan equipos adquiridos o registrados justo antes de la activación de la línea, por lo que convertirlos a 0 corrige el error lógico preservando la fila. En ingresos y cargos, representan un ajuste o error de facturación que afecta a menos del 0.01% de los registros; al ser una fracción irrelevante, la imputación limpia el ruido.
Consecuencias / riesgos: Alteración mínima de la distribución base en el día 0 para los equipos y en los ingresos mensuales.