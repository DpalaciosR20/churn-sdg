def segmento(meses: int) -> str:
    if meses < 0:
        raise ValueError("meses no puede ser negativo")
    if meses >= 25:
        return "25+"
    if meses >= 12:
        return "12-24"
    return "0-11"