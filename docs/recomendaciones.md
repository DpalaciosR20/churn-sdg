### 6. Del driver a la recomendación

Una importancia no es una recomendación. Para cada driver, completa esta cadena:

```
Driver → Evidencia (EDA + SHAP) → Hipótesis del porqué → Acción → Cómo medir si funcionó
```

Y clasifica cada driver:

* **Accionable:** negocio puede intervenir (ofrecer un teléfono nuevo).
* **No accionable, pero útil como disparador:** no puedes cambiar la antigüedad del cliente, pero sí usarla para saber **cuándo** actuar.

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
* Modelo: months es la segunda variable más importante según SHAP. Su contribución negativa aumenta justo en los meses 11-12.

**Hiótesis:** Al acercarse al año, suponiendo un contrato inicial de un año, el contrato del servicio está próximo a vencer y esto aumenta el riesgo de que el cliente se vaya.

**Acción:** Contactar al cliente al acercarse la fecha límite de vigencia del contrato (mes 10) para ofrecerle renovarlo y, posiblemente, ofrecer alguna promoción para buscar convenserlo en caso de que en un inicio se muestre desinteresado.

**Cómo medirlo:** Experimento con grupo de control. De los clientes elegibles, ofrecer la renovación de contrato a una mitad elegida al azar y no contactar a la otra. Comparar la tasa de churn de ambos grupos entre 31 y 60 días después. Solo si la diferencia es clara se escala la 
campaña.

**Precaución:** el riesgo aquí es contactar a un usuario que no se iba a ir y aún así ofrecerle una promoción, invirtiendo así en un cliente que de todas maneras no se iba a ir. Sin embargo, considero que esto sigue siendo mejor a una cancelación. El negocio deberá encontrar una promoción que pueda costear para este tipo de casos.


## R3. Caída de uso
**Driver:** `change_mou`,`mou_Mean`

**Tipo:** Disparado de alerta temprana.

**Evidecncia:**
- EDA: Se encontró que conforme los clientes iban reduciendo su uso de minutos mensual, el reiesgo de que se fueran aumentaba.
- Modelo: `mou_Mean` y  `change_mou` son la segunda y cuarta variable, respectivamente, más importante según SHAP. Su contribución es positiva (aumenta el riesgo) a menor número de minutos usados (cero) y va aumentando hacía el lado positivo conforme mayor es el uso.

**Hipótesis:** Cuanto menor es el número de minutos de uso que tiene el cliente mayor es su riesgo. Y cuando el cambio, respecto al promedio de los últimos 3 meses, es negativo, también aumenta el riesgo de irse.

**Acción:** Si al momento de la observación se tiene un bajo numero de uso y/o su cambio de uso es negativo, contactar al cliente para aplicar la campaña de retención.

**Precaución:** Este caso también puede que trate de un abandono silencioso, probablemente el cliente ya dejó de usar la línea y solo falta la contratación formal, por lo que gastar presupuesto en él es desperdiciarlo, aunque el modelo acierte, ya que este cliente tiene riesgo altísimo y recuperabilidad casi nula. Aquí es importante usar la tabla de prioridar para cachar a los clientes de mayor valor para que en esos sean en los que se aplique la campaña.

## R4. A quién contactar primero
**Driver:** Matriz de riesgo contra valor

**Tipo:** Accionable

**Evidencia:** Se realizó una matriz que crusaba el riesgo calculado del cliente y su valor (rev_Mean) para de esta clasificar a estos cleintes de acuerdo a su riesgo y valor.

**Hipótesis:** Como se vió en el punto anterior, no se puede tomar simplemente al 20% de los clientes de mayor riesgo porque puede que muchos de ellos sean abandonos silenciosos y que por lo tanto aplicar una campaña resulte en un desperdicio. Para eso, la matris de riesgo contra valor ayuda a priorizar el cuadrante con más ingreso en juego por cliente.

**Acción:** Identificar al 20% de los clientes de mayor riesgo y, de estos, únicamente aplicar la campaña de retención, que corresponda, a aquellos que tienen un rev_Mean por encima de la media.

**Precaución:** Puede que aún usando este criterio se contacten a clientes que decidan no quedarse o se dejen fuera a clientes que sí se hubieran quedado, pero esto va más allá de las predicciones del modelo.

## R5. Método: medir antes de escalar

**Driver:** -

**Tipo:** Método

**Hipótesis:** Para saber qué tan efectiva es la campaña y para tener datos con los cuales se pueda reentrenar al modelo sin que sean alterados por intervención, es importante tener un grupo de control en toda la campaña.

**Acción:** Tener un grupo de control (la mitad, al azar, del grupo seleccionado como de mayor riesgo y valor) a los que sí se les aplique la campaña y medir las diferencias contra los que no se les aplicó.