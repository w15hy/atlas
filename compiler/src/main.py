import os
import sys

from toolchain.compiler.lexical_analysis.lexer import lexer_output
from toolchain.compiler.semantic_analysis.analyzer import analyze_and_generate
from toolchain.compiler.syntax_analysis.parser import parse
from toolchain.preprocessor.preprocessor import preprocessor
from ui.app import start
from utils.utils import ofile, ofilelines, wfilelines

# ------------------ ARCHIVO ------------------
file = sys.argv[1] if len(sys.argv) > 1 else "main.atl"
entry = ofilelines("./compiler/programs/" + file)

# ------------------ TABLAS ------------------
symbol_table = {}  # IDs / variables
number_table = []  # literales numéricos
string_table = []  # literales string
tokens = []  # tokens


def main():

    basename = file.split(".")[0]

    # Make the build dir
    if os.path.isdir(f"./compiler/programs/.build_{basename}"):
        print(f"Compilando en carpeta ya existente ./programs/.build_{file}")
    else:
        os.mkdir(path=f"./compiler/programs/.build_{basename}")

    # ---------------------- Preprocessor ----------------------

    pre = preprocessor(entry)
    wfilelines(f"./compiler/programs/.build_{basename}/{basename}.pre", pre)

    # ---------------------- Compilador ----------------------

    # Lexer

    lines = ofile(f"./compiler/programs/.build_{basename}/{basename}.pre")
    tokens, symbol_table, number_table, string_table = lexer_output(lines)
    wfilelines(f"./compiler/programs/.build_{basename}/{basename}.tokens", tokens)

    # Parser
    source = ofile(f"./compiler/programs/.build_{basename}/{basename}.pre")
    ast, errors = parse(source)

    if errors:
        print("\n===== ERRORS =====")
        for e in errors:
            print(e)
        return

    print("===== AST =====")
    print(ast)

    # ---------------------- Análisis semántico + Codegen ----------------------
    result = analyze_and_generate(ast)

    if result["errors"]:
        print("\n===== SEMANTIC ERRORS =====")
        for e in result["errors"]:
            print(e)
        return

    asm_path = f"./compiler/programs/.build_{basename}/{basename}.asm"
    wfilelines(asm_path, result["asm"])
    print(f"\n===== ASM generado en {asm_path} =====")


if __name__ == "__main__":
    main()
