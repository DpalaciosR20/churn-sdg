# Recomendaciones

## R1. Renovación proactiva del teléfono antes de los 10 meses
**Driver:** antigüedad y gama del teléfono (`eqpdays`, `hnd_price`, `hnd_webcap`).

**Tipo:** accionable. El negocio puede ofrecer un equipo nuevo.

**Evidencia:**
- EDA: la tasa de churn pasa de ~37 % a ~61 % cuando el teléfono supera los ~300 días de antigüedad, y se mantiene por encima del promedio (49.6 %) de ahí en adelante.
- EDA: los grupos con teléfonos más baratos con los de mayor churn: `hnd_webcap` NA (59.2 %) y WC (56.3 %), con un precio mediano de ~$30, contra ~$130 en WCMB (47.1 %).
- Modelo: `eqpdays` es la variable más importante según SHAP. Su contribución es negativa (baja el riesgo) hasta ~300 días y positiva después: el modelo encontró el mismo umbral que el EDA.

**Hipótesis:** alrededor de los 10 meses el cliente termina de pagar su equipo o este empieza a quedar obsoleto. Si quiere uno nuevo y no recibe una oferta, compara con la competencia.
No está verificado: el dataset no indica si el teléfono se adquirió con el contrato.

**Acción:** contactar a los clientes cuyo teléfono cumple 9 meses con una oferta de renovación de equipo, priorizando a los de riesgo alto y valor alto (matriz de riesgo contra valor).

**Cómo medirlo:** experimento con grupo de control. De los clientes elegibles, ofrecer la renovación a una mitad elegida al azar y no contactar a la otra. Comparar la tasa de churn de ambos grupos entre 31 y 60 días después. Solo si la diferencia es clara se escala la campaña.

**Precaución:** el análisis muestra asociación, no causalidad. Que los clientes con teléfono viejo se vayan más no prueba que darles uno nuevo los retenga. Además, la renovación tiene un costo que debe compararse con el ingreso que se conserva.

## R2. Fin de contrato
**Driver:** Cantidad de meses del cliente en el servicio, `months`.

**Tipo:** Disparador. El negocio puede usar esta variable para saber en qué momento actuar.

**Evidencia:** 
* EDA: la tasa de churn tiene un pico de 61.9% en los meses 11-12.
* Modelo: months es la seguntercerada variable más importante según SHAP. Su contribución es negativa entre 6 y 9 meses y salta a positiva (+0.5) en los meses 11 y 12.

**Hiótesis:** Al acercarse al año, suponiendo un contrato inicial de un año, el contrato del servicio está próximo a vencer y esto aumenta el riesgo de que el cliente se vaya.

**Acción:** Contactar al cliente al acercarse la fecha límite de vigencia del contrato (mes 10) para ofrecerle renovarlo y, posiblemente, ofrecer alguna promoción para buscar convenserlo en caso de que en un inicio se muestre desinteresado.

**Cómo medirlo:** Experimento con grupo de control. De los clientes elegibles, ofrecer la renovación de contrato a una mitad elegida al azar y no contactar a la otra. Comparar la tasa de churn de ambos grupos entre 31 y 60 días después. Solo si la diferencia es clara se escala la 
campaña.

**Precaución:** el riesgo aquí es contactar a un usuario que no se iba a ir y aún así ofrecerle una promoción, invirtiendo así en un cliente que de todas maneras no se iba a ir. Sin embargo, considero que esto sigue siendo mejor a una cancelación. El negocio deberá encontrar una promoción que pueda costear para este tipo de casos.


## R3. Caída de uso
**Driver:** `change_mou`,`mou_Mean`

**Tipo:** Disparado de alerta temprana.

**Evidecncia:**
- EDA: Se encontró que conforme los clientes iban reduciendo su uso de minutos mensual, el reiesgo de que se fueran aumentaba. Entre los minutos 0 y 48 el riesgo era de casi el 60% pasando a ~52% en los minutos 48-115 y de ahí en adelante continúa bajando.
- Modelo: `mou_Mean` y  `change_mou` son la segunda y cuarta variable, respectivamente, más importante según SHAP. Su contribución es positiva (sube el riesgo) con poco uso y se vuelve negativa conforme aumenta el uso.

**Hipótesis:** El cliente ya usa otra línea o ya decidió irse

**Acción:** Si al momento de la observación se tiene un bajo numero de uso y/o su cambio de uso es negativo, contactar al cliente para aplicar la campaña de retención.

**Cómo medirlo:** Dividir al segmento de alto riesgo en un grupo de tratamiento (contactado) y un grupo de control aislado (no contactado). Comparar la tasa de fuga entre ambos grupos para calcular el uplift (retención neta generada exclusivamente por la campaña). Medir la tasa de aceptación real de la oferta para confirmar si el supuesto de negocio inicial era el correcto. Calcular el ROI y monitorear si contactar clientes por error aumenta su fuga para evitar despertar usuarios que no pensaban cancelar.

**Precaución:** Este caso también puede que trate de un abandono silencioso, probablemente el cliente ya dejó de usar la línea y solo falta la cancelación formal, por lo que gastar presupuesto en él es desperdiciarlo, aunque el modelo acierte, ya que este cliente tiene riesgo altísimo y recuperabilidad casi nula. Aquí es importante usar la tabla de prioridar para cachar a los clientes de mayor valor para que en esos sean en los que se aplique la campaña.

## R4. A quién contactar primero
**Driver:** Matriz de riesgo contra valor

**Tipo:** Accionable

**Evidencia:** Se realizó una matriz que cruza el riesgo calculado del cliente y su valor (rev_Mean) para de esta clasificar a estos cleintes de acuerdo a su riesgo y valor.  El cuadrante de riesgo alto y valor bajo tiene la tasa de churn más alta de todas (74%). Un cliente de riesgo bajo y valor alto tiene más ingreso en juego ($36.8) que uno de riesgo alto y valor bajo ($22.0). Es decir, el valor del cliente pesa tanto como su riesgo. Ordenar solo por riesgo mandaría el presupuesto al cuadrante de $22 antes que al de $37.

**Hipótesis:** Como se vió en el punto anterior, no se puede tomar simplemente al 20% de los clientes de mayor riesgo porque puede que muchos de ellos sean abandonos silenciosos y que por lo tanto aplicar una campaña resulte en un desperdicio. Para eso, la matris de riesgo contra valor ayuda a priorizar el cuadrante con más ingreso en juego por cliente.

**Acción:** Identificar al 20% de los clientes de mayor riesgo y, de estos, únicamente aplicar la campaña de retención, que corresponda, a aquellos que tienen un rev_Mean por encima de la mediana.

**Precaución:** Puede que aún usando este criterio se contacten a clientes que decidan no quedarse o se dejen fuera a clientes que sí se hubieran quedado, pero esto va más allá de las predicciones del modelo.

## R5. Método: medir antes de escalar

**Driver:** -

**Tipo:** Métodológico. Práctica de experimentación continua.

**Evidencia:** Si se contacta a todos los clientes marcados en riesgo y estos no se van, el negocio no sabrá si fue por el éxito de la campaña o porque el modelo arrojó falsos positivos. Además, reentrenar un modelo con datos donde hubo intervención contamina las etiquetas (sesgo de intervención) y destruye la capacidad predictiva futura.

**Hipótesis:** Reservar un grupo de control universal (no contactado) resuelve dos problemas críticos simultáneamente: cuantifica el impacto real y el ROI de las acciones de retención (uplift), y genera un historial de datos puros y sin sesgo para mantener el modelo calibrado a largo plazo.

**Acción:** Separar aleatoriamente entre el 10 % y 20 % de los clientes elegibles para la campaña de retención y designarlos como "grupo de control" estricto (no contactarlos). Aplicar la campaña únicamente al 80 % o 90 % restante (grupo de tratamiento).

**Cómo medirlo:** Comparar la tasa de churn del grupo de tratamiento frente a la del grupo de control entre 31 y 60 días después de la campaña. La diferencia entre ambos indica el uplift neto de retención. Multiplicar esos clientes netos salvados por su rev_Mean y restar el costo de contacto de todo el grupo de tratamiento para obtener el ROI real.

**Precaución:** Es fundamental que las áreas operativas y de marketing respeten el aislamiento del grupo de control. Si estos clientes terminan recibiendo la oferta por otras vías (por ejemplo, un envío masivo de correos no coordinado), el experimento se invalida, impidiendo medir el éxito real y arruinando los datos para el reentrenamiento.