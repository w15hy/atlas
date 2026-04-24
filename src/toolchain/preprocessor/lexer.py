import ply.lex as lex
from ply.lex import TOKEN

from utils.utils import ofile

#  _____ _____ _   __ _____ _   _  _____
# |_   _|  _  | | / /|  ___| \ | |/  ___|
#   | | | | | | |/ / | |__ |  \| |\ `--.
#   | | | | | |    \ |  __|| . ` | `--. \
#   | | \ \_/ / |\  \| |___| |\  |/\__/ /
#   \_/  \___/\_| \_/\____/\_| \_/\____/

# Errors
errors = []


# Regular expression rules for simple tokens
digit = r"([0-9])"
letter = r"([A-Za-z])"
identifier = letter + r"(" + letter + r"|" + digit + r"|_)*"
number = (
    r"-?(("
    + digit
    + r"+(\."
    + digit
    + r"*)?"
    + r")|(\."
    + digit
    + r"+))([eE][-+]?"
    + digit
    + r"+)?"
)

reserved = {
    "if": "KW",
    "then": "KW",
    "else": "KW",
    "while": "KW",
    "int": "KW",
    "float": "KW",
    "switch": "KW",
    "case": "KW",
    "default": "KW",
    "for": "KW",
    "return": "KW",
    "break": "KW",
    "pass": "KW",
    "continue": "KW",
    "include": "KW",
    "define": "KW",
    "elif": "KW",
    "def": "KW",
    "do": "KW",
}

delimiters = {
    "(": "DEL",
    ")": "DEL",
    "{": "DEL",
    "}": "DEL",
    "[": "DEL",
    "]": "DEL",
}

tokens = ["KW", "ID", "NUMBER", "RELOP", "ASSIGN", "TYPE", "DEL"]
literals = ["+", "-", "*", "/", ","]


@TOKEN(identifier)
def t_ID(t):
    t.type = reserved.get(t.value, "ID")
    return t


@TOKEN(number)
def t_NUMBER(t):
    t.value = float(t.value) if (c in t.value.lower() for c in ".e") else int(t.value)
    return t


def t_RELOP(t):
    r"<=|>=|<|>|==|!="
    return t


def t_DEL(t):
    r"[\(\)\{\}\[\]]"
    return t


def t_ASSIGN(t):
    r"="
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = " \t"

# Ignore comments
t_ignore_COMMENT = r"\#.*"


# Error handling rule
def t_error(t):
    errors.append(
        f"\033[31mLEXER: \033[0mIllegal character '{t.value[0]}' at line {t.lineno}"
    )
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

# Test it out
file = "main.atl"
data = ofile("programs/" + file)


def main():
    # Give the lexer some input
    lexer.input(data)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        print(tok)

    for err in errors:
        print(err)
