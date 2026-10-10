-- Clientes y tasa real de churn por grupo de riesgo
SELECT
    grupo_riesgo,
    COUNT(*) AS total_clientes,
    AVG(churn_real) AS tasa_churn
FROM predicciones
GROUP BY grupo_riesgo
ORDER BY grupo_riesgo ASC;

-- Los 10 clientes de mayor riesgo, con sus tres factores
SELECT
    "Customer_ID",
    riesgo,
    factor_1,
    factor_2,
    factor_3
FROM predicciones
ORDER BY riesgo DESC
LIMIT 10;

-- Frecuencia de variables como factor principal
SELECT
    factor_1,
    COUNT(*) AS apariciones
FROM predicciones
GROUP BY factor_1
HAVING COUNT(*) > 500
ORDER BY apariciones DESC;

-- Ingreso promedio por grupo de riesgo
SELECT
    p.grupo_riesgo,
    AVG(c."rev_Mean") AS ingreso_promedio
FROM predicciones p
JOIN clientes c ON p."Customer_ID" = c."Customer_ID"
GROUP BY p.grupo_riesgo
ORDER BY p.grupo_riesgo ASC;

-- Historial de AUC por corrida
SELECT 
    run_id, 
    fecha, 
    auc 
FROM metricas_modelo
ORDER BY fecha DESC;