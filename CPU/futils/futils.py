import struct


def _bits_to_float(bits32: int) -> float:
    """Convierte un entero de 32 bits (patrón IEEE 754) a float Python."""
    bits32 = bits32 & 0xFFFFFFFF
    return struct.unpack(">f", bits32.to_bytes(4, "big"))[0]


def _float_to_bits(f: float) -> int:
    """Convierte un float Python a su patrón de bits IEEE 754 de 32 bits."""
    return struct.unpack(">I", struct.pack(">f", f))[0]
