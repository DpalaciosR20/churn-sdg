## D-000 · Plantilla
Fecha:
Contexto: ¿qué problema o pregunta obligó a decidir?
Opciones consideradas: A, B, C
Decisión:
Justificación: ¿por qué esta y no las otras?
Consecuencias / riesgos:

## D-001 · Pandas o Polars
Fecha: 29/09/2026
Contexto: Qué herramienta para la manipulación de datos usaré?
Opciones consideradas: Polars (lo conozco, más rápido), Pandas (estándar en la industria).
Decisión: Pandas
Justificación: scikit-learn, SHAP y la mayoría de la documentación y ejemplos asumen pandas; con 100k de filas el rendimiento de Polars no es necesario; además, pandas es el que más se usa en la industria.
Consecuencias / riesgos: curva de aprendizaje -> mi lógica de Poalrs se transfiere casi directo (Agrupar, agregar, filtrar); si una opereación se vuelve lenta, se puede optimizar después.

## D-002 · Alcance del MVP
Fecha: 29/09/2026
Opciones: (A) solo lo que pide el PDF · (B) PDF más extensiones seleccionadas · (C) todas las extensiones.
Decisión: B. Lo que entra es la lista Must de la sección 8.
Justificación: el PDF exige el DAG y el análisis; la entrevista pidió una interfaz web; PostgreSQL alimenta esa interfaz. Todo lo demás no cabe con calidad en el tiempo disponible.
Riesgos y mitigación: que la solución parezca básica → presentar explícitamente la sección Won't como hoja de ruta (el PDF valora proponer lo que se haría con más tiempo).

## D-003 · Plan de estudio y punto de revisión
Fecha: 29/09/2026
Contexto:voy uns 3 días atrás del calendario original.
Opciones: (A) plan comprimido desde ya · (B) mantener el alcance original con horas extra y un punto de revisión.
Decisión: B, con revisión el domingo 4 de octubre por la noche.
Criterio: si Airflow corre y el EDA está terminado, se mantiene el alcance; si no, pasamos al plan comprimido y MLflow sale.
