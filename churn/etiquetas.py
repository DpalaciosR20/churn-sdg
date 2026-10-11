ETIQUETAS = {
    "eqpdays": "Antigüedad del teléfono (días)",
    "mou_Mean": "Minutos de uso mensual",
    "months": "Antigüedad como cliente (meses)",
    "change_mou": "Cambio reciente en minutos de uso",
    "hnd_price": "Precio del teléfono",
    "ovrrev_Mean": "Cargos por exceder el plan",
    "uniqsubs": "Número de líneas en el hogar",
    "drop_vce_Mean": "Llamadas de voz interrumpidas",
    "totmrc_Mean": "Cargo recurrente mensual",
    "change_rev": "Cambio reciente en facturación",
    "infobase_Sin dato": "Información de InfoBase no disponible",
    "phones": "Teléfonos asociados a la cuenta",
    "rev_Mean": "Ingreso mensual promedio",
    "asl_flag_N": "Cuenta sin límite de gasto",
    "drop_blk_Mean": "Llamadas bloqueadas o interrumpidas",
}

COLUMNAS_FACTOR = {
    "eqpdays": "eqpdays",
    "mou_Mean": "mou_Mean",
    "months": "months",
    "change_mou": "change_mou",
    "hnd_price": "hnd_price",
    "ovrrev_Mean": "ovrrev_Mean",
    "uniqsubs": "uniqsubs",
    "drop_vce_Mean": "drop_vce_Mean",
    "totmrc_Mean": "totmrc_Mean",
    "change_rev": "change_rev",
    "infobase_Sin dato": "infobase",
    "phones": "phones",
    "rev_Mean": "rev_Mean",
    "asl_flag_N": "asl_flag",
    "drop_blk_Mean": "drop_blk_Mean",
}


def etiqueta(factor: str) -> str:
    """Traduce un factor del modelo a lenguaje de negocio."""
    return ETIQUETAS.get(factor, factor)


def columna_factor(factor: str) -> str:
    """Devuelve la columna original de clientes asociada con un factor."""
    return COLUMNAS_FACTOR.get(factor, factor)
