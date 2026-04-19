def _int_to_bin64(value: int) -> str:
    """Entero → cadena binaria de 64 bits (complemento a 2)."""
    return format(value & 0xFFFFFFFFFFFFFFFF, "064b")
