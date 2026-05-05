import os

from toolchain.compiler.lexical_analysis.lexer import lexer_output
from toolchain.compiler.syntax_analysis.parser import parse
from toolchain.preprocessor.preprocessor import preprocessor
from ui.app import start
from utils.utils import ofile, ofilelines, wfilelines

# ------------------ ARCHIVO ------------------
file = "main.atl"
entry = ofilelines("programs/" + file)

# ------------------ TABLAS ------------------
symbol_table = {}  # IDs / variables
number_table = []  # literales numéricos
string_table = []  # literales string
tokens = []  # tokens


def main():

    basename = file.split(".")[0]

    # Make the build dir
    if os.path.isdir(f"./programs/.build_{basename}"):
        print(f"Compilando en carpeta ya existente ./programs/.build_{file}")
    else:
        os.mkdir(path=f"./programs/.build_{basename}")

    # ---------------------- Preprocessor ----------------------

    pre = preprocessor(entry)
    wfilelines(f"./programs/.build_{basename}/{basename}.pre", pre)

    # ---------------------- Compilador ----------------------

    # Lexer

    lines = ofile("programs/.build_main/" + basename + ".pre")
    tokens, symbol_table, number_table, string_table = lexer_output(lines)
    wfilelines(f"./programs/.build_{basename}/{basename}.tokens", tokens)

    # Parser
    source = ofile("programs/.build_main/main.pre")
    ast, errors = parse(source)

    if errors:
        print("\n===== ERRORS =====")
        for e in errors:
            print(e)
    else:
        print("===== AST =====")
        print(ast)
