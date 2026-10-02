def segmento(meses: int) -> str:
    if meses < 0:
<<<<<<< HEAD
        raise ValueError("No se acepta valor negativo.")
=======
        raise ValueError("meses no puede ser negativo")
>>>>>>> feature/tests
    if meses >= 25:
        return "25+"
    if meses >= 12:
        return "12-24"
    return "0-11"