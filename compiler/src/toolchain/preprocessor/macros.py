import re

dict_macros = {}
lines = []

def parse_define(line):
    if re.search(r"#define\s+[A-Za-z_]\w*\s*\(", line):
        definir_con_parametros(line)
    else:
        definir_simple(line)


def definir_simple(line):
    expr = line.split()
    nombre = expr[1]
    valor = " ".join(expr[2:])
    dict_macros[nombre] = valor


def get_params(line):
    m = re.search(r"([A-Za-z_]\w*)\s*\(", line)
    if not m:
        return "", []

    p = line.find("(", m.start())
    level = 1
    i = p + 1

    while i < len(line):
        if line[i] == "(":
            level += 1
        elif line[i] == ")":
            level -= 1
            if level == 0:
                return m.group(1), line[p + 1 : i].split(",")
        i += 1

    return "", []


def definir_con_parametros(line):
    p = line.find("(")
    if p == -1:
        return

    q = line.find(")", p)
    if q == -1:
        return

    header = line[: q + 1]
    body = line[q + 1 :].strip()

    if not body:
        return

    expr = header.split()
    macro = expr[1]

    name, params = get_params(macro)

    dict_macros[name] = {"params": [p.strip() for p in params], "replace": body}


def define_macros(input_lines):
    global lines
    lines = input_lines

    for idx, line in enumerate(lines):
        if line.strip().startswith("#define"):
            parse_define(line)
            lines[idx] = ""
        elif not line.strip():
            lines[idx] = ""


def expandir_macro_con_parametros(linea, key, value):
    if key + "(" not in linea:
        return linea

    inicio = linea.find(key)
    llamada = linea[inicio:]

    _, args = get_params(llamada)

    if len(args) != len(value["params"]):
        return linea

    resultado = value["replace"]

    for param, arg in zip(value["params"], args):
        resultado = re.sub(r"\b" + re.escape(param) + r"\b", arg.strip(), resultado)

    for key, value in dict_macros.items():
        if isinstance(value, str):
            resultado = re.sub(r"\b" + re.escape(key) + r"\b", value, resultado) 

    fin = linea.find(")", inicio) + 1

    return linea[:inicio] + resultado + linea[fin:]
