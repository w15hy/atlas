import re

from toolchain.preprocessor.includes import include
from toolchain.preprocessor.macros import (
    define_macros,
    dict_macros,
    expandir_macro_con_parametros,
)
from utils.utils import ofilelines

file = "main.atl"
lines = ofilelines("./compiler/programs/" + file)


def main():
    preprocessor(lines)


def preprocessor(lines):

    # ---------------- INCLUDE ----------------
    lines = include(lines, base_dir="./programs/")
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


if __name__ == "__main__":
    main()
