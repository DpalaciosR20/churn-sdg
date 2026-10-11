# Registro de decisiones

Este documento registra las decisiones técnicas y de producto del proyecto.

## D-001 — Pandas o Polars

**Fecha:** 29/09/2026

**Contexto:** ¿Qué herramienta usar para la manipulación de datos?

**Opciones consideradas:**

- Polars, que ya conozco y es más rápido.
- Pandas, estándar en la industria.

**Decisión:** Usar Pandas.

**Justificación:** Scikit-learn, SHAP y la mayoría de la documentación y los ejemplos asumen Pandas. Con 100 mil filas no se necesita el rendimiento de Polars; además, Pandas es la herramienta más usada en la industria.

**Consecuencias y riesgos:** Hay una curva de aprendizaje, pero la lógica de Polars se transfiere casi directamente (agrupar, agregar y filtrar). Si alguna operación se vuelve lenta, se puede optimizar después.

## D-002 — Alcance del MVP

**Fecha:** 29/09/2026

**Opciones consideradas:**

- **A.** Solo lo que pide el PDF.
- **B.** El PDF más extensiones seleccionadas.
- **C.** Todas las extensiones.

**Decisión:** Elegir la opción B. El alcance incluye los elementos de la lista Must de la sección 8.

**Justificación:** El PDF exige el DAG y el análisis; la entrevista pidió una interfaz web y PostgreSQL alimenta esa interfaz. El tiempo disponible no alcanza para implementar con calidad todo lo demás.

**Riesgos y mitigación:** La solución podría parecer básica. Para mitigarlo, presentar explícitamente la sección Won't como hoja de ruta; el PDF valora proponer qué se haría con más tiempo.

## D-003 — Plan de estudio y punto de revisión

**Fecha:** 29/09/2026

**Contexto:** El avance está unos tres días atrás del calendario original.

**Opciones consideradas:**

- **A.** Comprimir el plan desde ese momento.
- **B.** Mantener el alcance original con horas extra y un punto de revisión.

**Decisión:** Elegir la opción B, con revisión el domingo 4 de octubre por la noche.

**Criterio de revisión:** Si Airflow está funcionando y el EDA está terminado, se mantiene el alcance; de lo contrario, se pasa al plan comprimido y MLflow queda fuera.

**Actualización (05/10/2026):** Airflow está funcionando y el EDA está terminado.

## D-004 — Versión de Apache Airflow

**Fecha:** 03/10/2026

**Contexto:** El PDF muestra Airflow 2.2.5, pero la versión estable actual es la 3.3.2, que incluye cambios importantes, como `api-server` en lugar de `webserver`, `dag-processor` separado e imports desde `airflow.sdk`.

**Opciones consideradas:**

- **A.** Airflow 2.x, como en el PDF.
- **B.** Airflow 3.x usando la etiqueta `stable`.
- **C.** Fijar Airflow 3.3.2.

**Decisión:** Elegir la opción C y fijar Airflow 3.3.2.

**Justificación:** Usar la versión actual ayuda a adaptarme a una tecnología nueva. Fijar la versión garantiza reproducibilidad: `stable` cambia con el tiempo y una actualización podría romper el proyecto antes de la presentación.

**Consecuencias y riesgos:** La documentación y los tutoriales de Airflow 2 no aplican tal cual. Se mitiga usando la documentación oficial de la versión 3.3.2.

## D-005 — Cómo accede Airflow al paquete `churn`

**Fecha:** 03/10/2026

**Contexto:** Al intentar usar un módulo del paquete `churn/` en un DAG, apareció un error `ModuleNotFoundError: No module named 'churn'`. El contenedor no veía la ruta de `churn/` y Python no tenía la ruta del paquete en `sys.path`.

**Opciones consideradas:**

- **A.** Copiar el código del paquete dentro de `dags/`.
- **B.** Moverlo a `plugins/`, que Airflow agrega a `sys.path` automáticamente.
- **C.** Montar `churn/` como volumen y declarar `PYTHONPATH`.
- **D.** Construir una imagen propia de Airflow con el paquete instalado.

**Decisión:** Elegir la opción C: montar `churn/` como volumen y declarar `PYTHONPATH`. Se usan el volumen `./churn:/opt/airflow/churn` y `PYTHONPATH=/opt/airflow`, ambos en el bloque compartido `x-airflow-common`.

**Justificación:** El mismo paquete `churn/` también lo usan las pruebas, así que mantenerlo en una sola carpeta evita duplicar código. Montarlo como volumen permite que los cambios se reflejen al instante, sin reconstruir la imagen. `plugins/` es una carpeta para extender Airflow, no para alojar lógica de negocio; además, las pruebas tendrían que importar desde una carpeta de Airflow. Una imagen propia es la opción correcta para producción, pero durante el desarrollo obliga a reconstruir la imagen después de cada cambio.

**Riesgos y mitigación:** Al cambiar de rama en Git, la carpeta puede borrarse y recrearse, lo que afecta su visibilidad desde los contenedores. Para resolverlo, ejecutar `docker compose down` y luego `docker compose up -d` después de cambiar de rama. En un entorno real sin carpetas compartidas, se usaría la opción D, con el paquete instalado en una imagen propia. Esta solución aplica al contexto actual del proyecto.

## D-006 — Cómo leer el CSV con Pandas

**Fecha:** 04/10/2026

**Contexto:** Al procesar el CSV con `pd.read_csv` y la lectura predeterminada de valores `NaN`, desaparecía un grupo de la columna `hnd_webcap`.

**Decisión:** Leer el conjunto de datos con `keep_default_na=False` y `na_values=[""]`, para conservar esa categoría y considerar como `NaN` solamente los campos vacíos.

**Riesgos:** Si el archivo tuviera otras formas de marcar valores faltantes (por ejemplo, `"NULL"` o `"N/A"`), ya no se detectarían. Se comparó la carga cruda con la normal y solo `"NA"` presentaba este comportamiento.

## D-007 — Tratamiento de nulos al calcular tasas por decil

**Fecha:** 04/10/2026

**Contexto:** Al calcular un ranking de señal (rango de la tasa entre deciles) para las variables numéricas, excluyendo `churn` y `Customer_ID`, se observó que usar `dropna=False` agregaba un grupo adicional: los clientes sin valor para la variable. Una tasa calculada con un solo cliente no es representativa, y los valores máximo y mínimo son muy sensibles a esos grupos.

**Opciones consideradas:**

- **A.** Ignorar el grupo de nulos para el ranking y analizarlos por separado.
- **B.** Ignorar cualquier grupo con menos de cierto número de clientes (por ejemplo, 100) al calcular el máximo y el mínimo.

**Decisión:** Elegir la opción A: ignorar el grupo de nulos para el ranking y analizarlos por separado.

**Justificación:** Ignorar cualquier grupo con menos de cierto número de clientes requiere decidir cuál es el umbral ideal. Excluir los nulos del ranking resuelve el problema actual y permite seguir analizándolos por separado en otras tareas. Se agregó una variable auxiliar a la función para indicar si se usa `dropna=False` o `dropna=True`.

## D-008 — Selección de variables y prevención de multicolinealidad

**Fecha:** 04/10/2026

**Contexto:** El dataset presenta alta redundancia entre variables (pares con correlación Spearman > 0.9, por ejemplo, minutos y conteo de llamadas) y variables acumuladas (`totmou`, `adjrev`) que esconden la antigüedad del cliente al mezclar el gasto con la duración del servicio y ser redundantes con `months`.

**Opciones consideradas:**

- **1.** Mantener todas las columnas y confiar en los árboles del modelo.
- **2.** Quedarse con las variables de mayor señal estadística plana (totales y ajustadas).
- **3.** Elegir un representante por familia de comportamiento, priorizando métricas mensuales, nivel de señal, ausencia de nulos y explicabilidad de negocio.

**Decisión:** Seleccionar métricas promedio o mensuales por familia (`rev_Mean`, `mou_Mean`, `ovrrev_Mean`, `comp_dat_Mean`, `custcare_Mean`, `phones`), descartando la familia de conteo de llamadas —por redundancia con minutos— y todas las métricas acumuladas. Se conservan las variables independientes o «huérfanas» (`months`, `change_mou`, etc.). `uniqsubs` y `actvsubs` pertenecen a la misma familia y generan multicolinealidad; se conserva `uniqsubs`, ya que aumenta el riesgo de forma consistente.

**Justificación:** Las variables acumuladas inflan su importancia porque contienen implícitamente la antigüedad del cliente, el principal factor de supervivencia. Eliminar la multicolinealidad y preferir promedios mensuales facilita que el negocio interprete el modelo de forma directa («cuánto paga o habla al mes el cliente») y evita que SHAP diluya la importancia entre variables redundantes.

**Consecuencias y riesgos:** Se descartan columnas altamente correlacionadas entre sí, lo que podría reducir muy marginalmente el poder predictivo bruto.

## D-009 — Tratamiento de valores negativos

**Fecha:** 04/10/2026

**Contexto:** Durante la exploración se encontraron valores numéricos que violan las reglas de negocio: días de antigüedad del equipo (`eqpdays`) por debajo de cero e ingresos y cargos (`rev_Mean`, `totmrc_Mean`, `avg6rev`) negativos.

**Opciones consideradas:**

- **1.** Transformar todos los negativos en nulos (`NaN`) para imputación algorítmica.
- **2.** Llevarlos a cero.
- **3.** Eliminar las filas.

**Decisión:** Aplicar un límite inferior de cero a `eqpdays` y transformar en nulos (`NaN`) los negativos en ingresos y egresos para su imputación algorítmica.

**Justificación:** En `eqpdays`, los negativos son pocos y cercanos a cero; se asume que representan equipos adquiridos o registrados justo antes de la activación de la línea. Convertirlos a cero corrige el error lógico y preserva la fila. En ingresos y cargos, representan un ajuste o error de facturación que afecta a menos del 0.01 % de los registros; al ser una fracción irrelevante, la imputación limpia el ruido.

**Consecuencias y riesgos:** La distribución base se altera mínimamente en el día cero para los equipos y en los ingresos mensuales.

## D-010 — Tratamiento de variables sensibles

**Fecha:** 05/10/2026

**Contexto:** El dataset tiene variables sensibles, como `ethnic`, `marital`, variables relacionadas con hijos, `area`, `prizm_social_one` y `crlscod` (que refleja la situación financiera del cliente). Algunas parecen variar entre grupos con respecto a la tasa de churn.

**Opciones consideradas:**

- **1.** Considerar las variables sensibles con gran variabilidad entre grupos.
- **2.** No considerarlas.

**Decisión:** Elegir la opción 2 y no incluirlas, para dar prioridad ética a entrenar un buen modelo que no termine sesgado por cuestiones como la etnia, la localidad o si una persona posee una casa grande. Por la misma razón, también se excluyeron las variables numéricas `adults`, `income`, `numbcars`, `forgntvl`, `truck`, `rv` y `lor`.

**Justificación:** Se excluyen por razones éticas y legales: las decisiones sobre los clientes (por ejemplo, a quién se ofrece un beneficio) no deben depender del origen étnico, el estado civil o la composición familiar.

**Riesgos:** El modelo puede perder algo de desempeño. Además, otras variables podrían seguir actuando como proxies de datos sensibles; en producción habría que auditar las predicciones por grupo.

## D-011 — Elección del modelo final

**Fecha:** 05/10/2026

**Contexto:** La regresión logística (baseline) obtuvo un AUC de validación de 0.610 y mostró subajuste: los resultados de entrenamiento y validación fueron casi iguales, y cambiar `C` no modificaba el resultado. El modelo lineal no puede representar relaciones como la de `months`, que tiene un pico cerca del año; hacía falta un modelo no lineal.

**Opciones consideradas:** Validación cruzada de 5 pliegues sobre train, con ROC-AUC como métrica.

| Modelo | Train | Validación | Brecha |
| --- | ---: | ---: | ---: |
| Regla `eqpdays` | — | 0.575 | — |
| Regresión logística | 0.612 | 0.610 | 0.002 |
| Árbol de decisión sin límite | 1.000 | 0.548 | 0.452 |
| Random Forest | 0.739 | 0.667 | 0.072 |
| LightGBM por defecto | 0.739 | 0.680 | 0.059 |
| LightGBM `cfg_2` | 0.729 | 0.683 | 0.046 |
| LightGBM `cfg_3` (sin restricciones) | 0.988 | 0.662 | 0.326 |
| LightGBM «regularizada» | 0.715 | 0.680 | 0.035 |
| LightGBM «profunda» | 0.778 | 0.683 | 0.095 |
| LightGBM `dart` | 0.715 | 0.679 | 0.036 |

**Decisión:** Usar LightGBM con la configuración «regularizada».

**Justificación:**

- LightGBM supera a la regresión logística por 0.07 de AUC y a Random Forest por 0.013.
- Entre las configuraciones de LightGBM, `cfg_2` y «regularizada» tienen 0.002 más de AUC; esa diferencia es menor que la variación entre pliegues (~0.003), por lo que se consideran un empate. Entre los modelos empatados se eligió el de menor brecha entre train y validación, es decir, el que menos sobreajusta.
- La regresión logística es más interpretable, pero la diferencia de desempeño es grande; la interpretabilidad se recupera con SHAP.

**Hiperparámetros del modelo final:**

- `n_estimators=300` y `learning_rate=0.05`: 300 árboles con un aporte pequeño cada uno. Aprender en pasos pequeños generaliza mejor que usar pocos árboles con un aporte grande.
- `num_leaves=15`: máximo de grupos finales por árbol; limita la complejidad.
- `max_depth=5`: máximo de condiciones encadenadas; evita reglas demasiado específicas, porque LightGBM tiende a hacer crecer ramas muy profundas.
- `min_child_samples=50`: ninguna hoja tendrá menos de 50 clientes, para no aprender de grupos pequeños.
- `colsample_bytree=0.8`: cada árbol usa el 80 % de las columnas al azar. Esto hace que los árboles sean más distintos entre sí y ayuda con variables redundantes.
- `reg_lambda=0.5` y `reg_alpha=0.1`: penalizan los valores extremos de las hojas; su efecto no se midió por separado.

**Resultado en test:** Evaluación realizada una sola vez, con el modelo ya elegido.

| Modelo | AUC | Precision@10 % | Lift@10 % | Precision@20 % |
| --- | ---: | ---: | ---: | ---: |
| Regla `eqpdays` | 0.571 | 58 % | 1.18 | 56 % |
| Regresión logística | 0.607 | 64 % | 1.30 | 62 % |
| LightGBM | 0.680 | 78 % | 1.58 | 72 % |

**Riesgos y limitaciones:**

- El AUC de 0.68 indica una señal moderada: el modelo ordena a los clientes mejor que las alternativas, pero no identifica con certeza quién se irá.
- La búsqueda de hiperparámetros fue manual, con 6 configuraciones. Una búsqueda sistemática (por ejemplo, con Optuna) podría mejorar algo; queda como siguiente paso.
- El dataset está balanceado al 50 %. En producción, con el churn real, la precisión sería mucho menor y las probabilidades habría que recalibrarlas.

**Nota posterior:** Después de la evaluación en test se retiró `actvsubs` por su redundancia con `uniqsubs`; las métricas no cambiaron.

## D-012 — Imagen propia de Airflow y artefactos en volúmenes

**Fecha:** 08/10/2026

**Contexto:** Para ejecutar el DAG de punta a punta, el contenedor de Airflow necesita librerías que no vienen en su imagen oficial (`lightgbm` y `shap`) y un mecanismo para leer y guardar los archivos generados (como `dataset.csv`, `.parquet`, `.pkl` y `.json`).

**Opciones consideradas:**

- **A.** Usar la variable de entorno `_PIP_ADDITIONAL_REQUIREMENTS` para que el contenedor instale las dependencias al arrancar y guardar archivos directamente en su sistema efímero.
- **B.** Construir una imagen Docker propia (extendida) con `Dockerfile.airflow` y montar volúmenes locales para las carpetas `data/` y `models/`.

**Decisión:** Elegir la opción B: construir una imagen propia y montar las carpetas de artefactos como volúmenes (`./data:/opt/airflow/data` y `./models:/opt/airflow/models`).

**Justificación:** Usar `_PIP_ADDITIONAL_REQUIREMENTS` es una mala práctica para producción: descarga e instala las librerías cada vez que el contenedor arranca, lo que hace el proceso lento y frágil. Puede fallar por problemas de red o porque `pip` resuelva dependencias distintas. Cargar las librerías en una imagen propia asegura consistencia y rapidez de despliegue. Por otro lado, usar volúmenes para `/data` y `/models` garantiza que los datos y el modelo serializado sobrevivan si el contenedor se apaga, y permite inspeccionarlos o consumirlos desde la laptop sin entrar a la consola del contenedor.

**Riesgos y mitigación:** Cada vez que se agregue, actualice o elimine una librería en `requirements-airflow.txt`, será necesario reconstruir la imagen (`docker compose build`) antes de levantar el contenedor. La laptop y el contenedor comparten la carpeta `models/`, así que una ejecución local puede sobrescribir el artefacto de Airflow. Para la demo, el último que escriba el modelo debe ser el DAG.

## D-013 — Control de calidad del modelo mediante umbrales

**Fecha:** 08/10/2026

**Contexto:** El pipeline de Airflow completaba la evaluación y terminaba su ejecución en verde, sin importar el rendimiento del modelo. Esto implicaba que un modelo con un rendimiento deficiente (por ejemplo, un AUC muy bajo) pasaría como exitoso y podría llegar a producción de forma silenciosa.

**Opciones consideradas:**

- **A.** Limitarse a registrar las métricas en los logs y en XCom, dejando que una persona revise si el modelo es suficientemente bueno después de cada ejecución.
- **B.** Configurar una regla estricta dentro del código que aborte la ejecución si no se cumple un estándar mínimo.

**Decisión:** Elegir la opción B: implementar una validación automática en la función `evaluar` que lance un `ValueError` si la métrica obtenida es inferior al umbral `AUC_MINIMO` definido en `config.py`.

**Justificación:** Un pipeline automatizado debe fallar rápido y de forma visible ante anomalías. Lanzar una excepción de Python provoca que la tarea de Airflow falle, deteniendo el flujo y evitando la entrega o el uso de un modelo que no cumple con el estándar de calidad del negocio. Mantener el valor en `config.py` centraliza el criterio y evita números mágicos dentro del código del pipeline.

**Riesgos:** El DAG se vuelve menos tolerante. Una fluctuación estadística mínima (por ejemplo, obtener un AUC de 0.649 cuando el mínimo exigido es 0.650) causará la falla total de la tarea, lo que podría requerir intervención humana frecuente si los hiperparámetros o los datos de entrada son muy inestables.

## D-014 — Base de datos propia y estrategias de escritura

**Fecha:** 09/10/2026

**Contexto:** Se requiere persistir los datos iniciales, las predicciones del modelo y el historial de métricas para que la aplicación Streamlit pueda consumirlos.

**Opciones consideradas:**

- **A.** Reutilizar la base de datos de metadatos de Airflow.
- **B.** Levantar un servicio de PostgreSQL independiente.

**Decisión:** Elegir la opción B: usar una base de datos propia (`churn-db`). Para las tablas de estado (`clientes`, `predicciones`, `importancia_variables`) se usa la estrategia de sobreescritura total (`replace`). Para el historial (`metricas_modelo`) se borran selectivamente los datos por `run_id` y se insertan las filas (`append`).

**Justificación:** Mezclar datos de negocio con la base de metadatos de Airflow es una mala práctica: acopla la aplicación al orquestador y pone los datos analíticos en riesgo si Airflow se reinicia o se destruyen sus volúmenes. Tener una base propia garantiza separación de responsabilidades.

**Riesgos:** Se deben gestionar correctamente las URL de conexión (una interna para Docker y otra expuesta para desarrollo local) mediante variables de entorno. También aumenta ligeramente el consumo de RAM y CPU local al mantener encendido un contenedor de base de datos adicional.

## D-015 — Aplicación de negocio con Streamlit y PostgreSQL

**Fecha:** 10/10/2026

**Contexto:** Se necesita una interfaz para que una persona de negocio consulte el desempeño del modelo, priorice clientes, entienda predicciones individuales y explore los factores asociados al churn.

**Opciones consideradas:**

- **A.** Cargar el modelo serializado y volver a calcular predicciones desde la interfaz cada vez que se consulta la app.
- **B.** Usar Streamlit como interfaz de lectura sobre los resultados que el pipeline ya persiste en PostgreSQL.

**Decisión:** Elegir la opción B: construir una aplicación Streamlit que consulta las tablas de PostgreSQL. Airflow y el pipeline son responsables de generar y persistir los datos; la interfaz no carga el archivo serializado ni entrena el modelo durante la navegación.

**Justificación:** Streamlit permite crear y compartir rápidamente una interfaz Python para este proyecto. Leer los resultados persistidos mantiene separadas la presentación y la ejecución del pipeline, evita repetir inferencias por cada interacción y permite mostrar también métricas históricas y explicaciones guardadas. La base de datos funciona como contrato entre productor y consumidor.

**Riesgos:** La aplicación depende de que PostgreSQL esté disponible y de que una corrida haya poblado las tablas. Si el pipeline no se ejecuta, la información puede estar vacía o desactualizada; por ello, la app debe comunicar estados vacíos y la operación debe verificar las corridas antes de usar los resultados. Las métricas del conjunto de prueba tampoco deben interpretarse como resultados garantizados en producción.
