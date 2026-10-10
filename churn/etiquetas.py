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


def etiqueta(factor: str) -> str:
    """Traduce un factor del modelo a lenguaje de negocio."""
    return ETIQUETAS.get(factor, factor)
