import ply.lex as lex
from ply.lex import TOKEN

from utils import ofile

# ------------------ TABLAS ------------------
symbol_table = {}
number_table = []
string_table = []
errors = []

# ------------------ PALABRAS RESERVADAS ------------------
reserved = {
    # CONDICIONALES
    "if": "IF",
    "else": "ELSE",
    "elif": "ELIF",
    # BUCLES
    "while": "WHILE",
    "for": "FOR",
    "break": "BREAK",
    "continue": "CONTINUE",
    # FUNCIONES
    "void": "VOID",  # ← reemplaza "def"
    "return": "RETURN",
    # TIPOS
    "int": "INT",
    "float": "FLOAT",
    "string": "STRING_TYPE",
    # ABSTRACTO
    "struct": "STRUCT",
    # OPERADORES LÓGICOS TEXTUALES
    "and": "AND",
    "or": "OR",
    "not": "NOT",
}

# ------------------ TOKENS ------------------
tokens = [
    "ID",
    "NUMBER",
    "STRLIT",
    "ASSIGN",
    "RELOP",
    "LOGOP",
    "LPAREN",
    "RPAREN",
    "LBRACKET",
    "RBRACKET",
    "LBRACE",
    "RBRACE",
    "SEMI",
    "COMA",
    "DOT",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
] + list(set(reserved.values()))

# ------------------ REGEX BASE ------------------
digit = r"[0-9]"
letter = r"[A-Za-z_]"
identifier = letter + r"(" + letter + r"|" + digit + r")*"

# ------------------ REGLAS SIMPLES ------------------
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_SEMI = r";"
t_COMA = r","

t_ignore = " \t"
t_ignore_COMMENT = r"\#.*"

# ------------------ REGLAS FUNCIÓN ------------------


@TOKEN(identifier)
def t_ID(t):
    t.type = reserved.get(t.value, "ID")
    if t.type == "ID" and t.value not in symbol_table:
        symbol_table[t.value] = {"type": "unknown", "value": None}
    return t


def t_NUMBER(t):
    r"(\d+\.\d*|\.\d+|\d+)([eE][+-]?\d+)?"
    val = float(t.value) if ("." in t.value or "e" in t.value.lower()) else int(t.value)
    t.value = val
    if val not in number_table:
        number_table.append(val)
    return t


def t_STRLIT(t):
    r"\"([^\\\n]|(\\.))*?\""
    t.value = t.value[1:-1]
    if t.value not in string_table:
        string_table.append(t.value)
    return t


def t_RELOP(t):
    r"<=|>=|==|!=|<|>"
    return t


def t_LOGOP(t):
    r"&&|\|\||!"
    return t


def t_ASSIGN(t):
    r"="
    return t


def t_DOT(t):
    r"\."
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    errors.append(
        f"\033[31mLEXER:\033[0m Illegal character '{t.value[0]}' at line {t.lineno}"
    )
    t.lexer.skip(1)


# ------------------ INSTANCIA ------------------
lexer = lex.lex()


# ------------------ API PÚBLICA ------------------
def lexer_output(source: str):
    tokens_list = []
    lexer.input(source)
    for tok in lexer:
        tokens_list.append(f"{tok}\n")
    return "".join(tokens_list), symbol_table, number_table, string_table


def main():
    file = "main.pre"
    data = ofile("programs/.build_main/" + file)
    lexer.input(data)
    for tok in lexer:
        print(tok)
    print("\n===== SYMBOL TABLE =====")
    print(list(symbol_table.keys()))
    print("\n===== NUMBER TABLE =====")
    print(number_table)
    print("\n===== STRING TABLE =====")
    print(string_table)
    if errors:
        print("\n===== ERRORS =====")
        for err in errors:
            print(err)


if __name__ == "__main__":
    main()
