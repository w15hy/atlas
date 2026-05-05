"""Sistema de tipos del lenguaje Atlas.

Tipos soportados:
    - Primitivos: int, float, string, void
    - Compuestos: struct (definidos por el usuario), array (declarado con [])

Las reglas de promoción/compatibilidad se centralizan aquí para que el
analizador semántico no decida tipos por su cuenta.
"""

INT = "int"
FLOAT = "float"
STRING = "string"
VOID = "void"
BOOL = "int"  # No hay bool nativo: las comparaciones devuelven int (0/1)
UNKNOWN = "unknown"
# 'any' acepta el sintaxis 'def' que el parser propaga como type_spec genérico
# (las funciones declaradas con 'def fn(...)' no tienen tipo de retorno explícito).
ANY = "any"

PRIMITIVES = {INT, FLOAT, STRING, VOID}
NUMERIC = {INT, FLOAT}


class StructType:
    """Tipo struct: registra el nombre y el orden+tipo de sus campos."""

    def __init__(self, name, fields):
        self.name = name
        # fields = [(field_type, field_name), ...] preservando orden de declaración
        self.fields = fields
        self.field_map = {fname: ftype for ftype, fname in fields}

    def __repr__(self):
        return f"struct {self.name}"


class ArrayType:
    """Tipo arreglo: tipo de elemento + tamaño (None si no se conoce)."""

    def __init__(self, element_type, size=None):
        self.element_type = element_type
        self.size = size

    def __repr__(self):
        return f"{self.element_type}[{self.size if self.size is not None else ''}]"


def is_numeric(t):
    return t in NUMERIC


def common_numeric(a, b):
    """Tipo resultante de una operación numérica binaria (promoción int→float)."""
    if a == FLOAT or b == FLOAT:
        return FLOAT
    return INT


def is_assignable(target, source):
    """¿Se puede asignar un valor de tipo `source` a una variable de tipo `target`?"""
    if target == source:
        return True
    # Promoción int → float
    if target == FLOAT and source == INT:
        return True
    # 'any' es comodín bidireccional (entra cuando el tipo viene del 'def' implícito).
    if target == ANY or source == ANY:
        return True
    return False


def type_name(t):
    """Nombre legible para mensajes de error."""
    if isinstance(t, (StructType, ArrayType)):
        return repr(t)
    return str(t)
