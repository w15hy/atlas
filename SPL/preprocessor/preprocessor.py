import re

from preprocessor.includes import include
from preprocessor.macros import (
    define_macros,
    dict_macros,
    expandir_macro_con_parametros,
)


def preprocessor(lines, base_dir=".", stdlib_dir=None):
    # Resetea el estado global de macros entre compilaciones.
    dict_macros.clear()

    # ---------------- INCLUDE ----------------
    lines = include(lines, base_dir=base_dir, stdlib_dir=stdlib_dir)
    # ---------------- MACROS ----------------
    define_macros(lines)

    for idx, linea in enumerate(lines):
        for key, value in dict_macros.items():
            if isinstance(value, str):
                linea = re.sub(r"\b" + re.escape(key) + r"\b", value, linea)

            elif isinstance(value, dict):
                linea = expandir_macro_con_parametros(linea, key, value)

        lines[idx] = linea

    return lines
