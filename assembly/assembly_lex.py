"""
assembler_lex.py — Ensamblador con análisis léxico (PLY/lex) para la máquina sy_00
===================================================================================
Taller #01 — Análisis léxico LEX
Implementa: PREPROCESADOR + ANALIZADOR LÉXICO + ENSAMBLADOR DE DOS PASADAS

Requisito:  pip install ply
Uso:        python assembler_lex.py <archivo.asm> [salida.bin]

Categorías léxicas reconocidas:
  INSTRUCCION   — mnemonics de las instrucciones (mov, add, jmp, etc.)
  REGISTRO      — r0 … r15
  NUMERO_HEX    — 0x1A3F
  NUMERO_BIN    — 0b1010
  NUMERO_FLOAT  — 3.14, -2.5e10
  NUMERO_INT    — 42, -7
  ETIQUETA_DEF  — identificador seguido de ':'
  IDENTIFICADOR — nombres de etiquetas en uso (destinos de salto, etc.)
  DIRECTIVA     — #include
  COMA          — ,
  COMENTARIO    — # ... (descartado)
  NEWLINE       — saltos de línea (manejo de líneas)
"""

import os
import re
import sys
import struct

import ply.lex as lex

INSTR_DICT = {
    # FORMATO 1  pre=0001  opcode=10 bits
    "mov":  {"opcode": 0,  "formato": 1},
    "push": {"opcode": 1,  "formato": 1},
    "pop":  {"opcode": 2,  "formato": 1},
    "xchg": {"opcode": 3,  "formato": 1},
    "add":  {"opcode": 4,  "formato": 1},
    "addi": {"opcode": 5,  "formato": 1},
    "sub":  {"opcode": 6,  "formato": 1},
    "subi": {"opcode": 7,  "formato": 1},
    "mul":  {"opcode": 8,  "formato": 1},
    "muli": {"opcode": 9,  "formato": 1},
    "div":  {"opcode": 10, "formato": 1},
    "divi": {"opcode": 11, "formato": 1},
    "inc":  {"opcode": 12, "formato": 1},
    "dec":  {"opcode": 13, "formato": 1},
    "neg":  {"opcode": 14, "formato": 1},
    "and":  {"opcode": 15, "formato": 1},
    "or":   {"opcode": 16, "formato": 1},
    "xor":  {"opcode": 17, "formato": 1},
    "not":  {"opcode": 18, "formato": 1},
    "shl":  {"opcode": 19, "formato": 1},
    "shr":  {"opcode": 20, "formato": 1},
    "rol":  {"opcode": 21, "formato": 1},
    "ror":  {"opcode": 22, "formato": 1},
    "cmp":  {"opcode": 23, "formato": 1},
    "test": {"opcode": 24, "formato": 1},
    "mod":  {"opcode": 25, "formato": 1},
    "modi": {"opcode": 26, "formato": 1},
    # FORMATO 2  pre=0010  opcode=8 bits
    "load":  {"opcode": 0, "formato": 2},
    "store": {"opcode": 1, "formato": 2},
    "lea":   {"opcode": 2, "formato": 2},
    # FORMATO 3  pre=0011  opcode=10 bits
    "jmp":  {"opcode": 0,  "formato": 3},
    "jz":   {"opcode": 1,  "formato": 3},
    "jnz":  {"opcode": 2,  "formato": 3},
    "jc":   {"opcode": 3,  "formato": 3},
    "jn":   {"opcode": 4,  "formato": 3},
    "jmpr": {"opcode": 5,  "formato": 3},
    "jzr":  {"opcode": 6,  "formato": 3},
    "jnzr": {"opcode": 7,  "formato": 3},
    "jcr":  {"opcode": 8,  "formato": 3},
    "jnr":  {"opcode": 9,  "formato": 3},
    "call": {"opcode": 10, "formato": 3},
    "jg":   {"opcode": 11, "formato": 3},
    "jge":  {"opcode": 12, "formato": 3},
    "jne":  {"opcode": 13, "formato": 3},
    # FORMATO 4  pre=0000  opcode=6 bits
    "nop":  {"opcode": 0, "formato": 4},
    "halt": {"opcode": 1, "formato": 4},
    "inti": {"opcode": 2, "formato": 4},
    "ret":  {"opcode": 3, "formato": 4},
    "iret": {"opcode": 4, "formato": 4},
    # FORMATO 5  pre=0100  opcode=10 bits  FPU
    "fmov":  {"opcode": 0,  "formato": 5},
    "fadd":  {"opcode": 1,  "formato": 5},
    "fsub":  {"opcode": 2,  "formato": 5},
    "fmul":  {"opcode": 3,  "formato": 5},
    "fdiv":  {"opcode": 4,  "formato": 5},
    "fcmp":  {"opcode": 5,  "formato": 5},
    "fabs":  {"opcode": 6,  "formato": 5},
    "fneg":  {"opcode": 7,  "formato": 5},
    "fsqrt": {"opcode": 8,  "formato": 5},
    "fi2f":  {"opcode": 9,  "formato": 5},
    "ff2i":  {"opcode": 10, "formato": 5},
}

PRE_INSTR = {
    1: {"pre": "0001", "opcode_bits": 10},
    2: {"pre": "0010", "opcode_bits": 8},
    3: {"pre": "0011", "opcode_bits": 10},
    4: {"pre": "0000", "opcode_bits": 6},
    5: {"pre": "0100", "opcode_bits": 10},
}

# Conjunto de mnemonics para uso rápido en el lexer
MNEMONICS = set(INSTR_DICT.keys())


# =============================================================================
# ANÁLISIS LÉXICO — PLY/lex
# =============================================================================

# ─── Categorías léxicas ───────────────────────────────────────────────────────
tokens = (
    'INSTRUCCION',    # mnemonics  (mov, add, jmp…)
    'REGISTRO',       # r0 … r15
    'NUMERO_HEX',     # 0x1A3F
    'NUMERO_BIN',     # 0b1010
    'NUMERO_FLOAT',   # 3.14  -2.5e10
    'NUMERO_INT',     # 42  -7
    'ETIQUETA_DEF',   # nombre:
    'IDENTIFICADOR',  # destinos de salto / nombres genéricos
    'DIRECTIVA',      # #include
    'COMA',           # ,
    'NEWLINE',        # \n
)

# ─── Reglas de tokens ────────────────────────────────────────────────────────

# Comentario: descarta todo lo que sigue a '#' (excepto directivas)
def t_COMENTARIO(t):
    r'\#(?!include)[^\n]*'
    pass  # descartado — no devuelve token

# Directiva #include
def t_DIRECTIVA(t):
    r'\#include\s+[<"][^>"]+[>"]'
    return t

# Número hexadecimal: 0x...  (debe ir ANTES de NUMERO_INT)
def t_NUMERO_HEX(t):
    r'-?0[xX][0-9A-Fa-f]+'
    t.value = int(t.value, 16)
    return t

# Número binario: 0b...
def t_NUMERO_BIN(t):
    r'-?0[bB][01]+'
    t.value = int(t.value, 2)
    return t

# Número flotante: debe ir ANTES que NUMERO_INT para capturar el punto
def t_NUMERO_FLOAT(t):
    r'-?[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?|-?[0-9]+[eE][+-]?[0-9]+'
    t.value = float(t.value)
    return t

# Registro r0…r15
def t_REGISTRO(t):
    r'[rR](1[0-5]|[0-9])(?!\w)'
    t.value = int(t.value[1:])   # valor numérico 0-15
    return t

# Identificador / instrucción / etiqueta-def
def t_ETIQUETA_DEF(t):
    r'[A-Za-z_]\w*\s*:'
    t.value = t.value.rstrip(':').strip()
    return t

def t_INSTRUCCION_O_ID(t):
    r'[A-Za-z_]\w*'
    lower = t.value.lower()
    if lower in MNEMONICS:
        t.type  = 'INSTRUCCION'
        t.value = lower
    else:
        t.type  = 'IDENTIFICADOR'
    return t

# Número entero con signo opcional
def t_NUMERO_INT(t):
    r'-?[0-9]+'
    t.value = int(t.value)
    return t

t_COMA    = r','
t_ignore  = ' \t\r'   # espacios y tabulaciones ignorados

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

def t_error(t):
    print(f"  [LEX] Carácter no reconocido '{t.value[0]}' en línea {t.lexer.lineno}")
    t.lexer.skip(1)


# Construir el lexer (outputdir evita escribir en disco de solo lectura)
lexer = lex.lex(debug=False, errorlog=lex.NullLogger(), outputdir='/tmp')


# =============================================================================
# PREPROCESADOR — expande #include <archivo>  y  #define NOMBRE VALOR
# =============================================================================

_INCLUDE_RE = re.compile(r'^\s*#include\s+[<"]([^>"]+)[>"]\s*$')
_DEFINE_RE  = re.compile(r'^\s*#define\s+(\w+)\s+(.*?)\s*$')


def preprocesar(lineas, base_dir='.', _depth=0, _defines=None):
    """
    Expande:
      #include <ruta> / #include "ruta"   → inserta el archivo referenciado
      #define NOMBRE VALOR                → sustituye ocurrencias en el texto
    Retorna list[str] con todas las líneas ya expandidas.
    """
    if _depth > 10:
        raise RecursionError("Demasiados niveles de #include (¿inclusión circular?)")

    if _defines is None:
        _defines = {}

    resultado = []
    for linea in lineas:
        # ── #define ──────────────────────────────────────────────────────────
        m_def = _DEFINE_RE.match(linea)
        if m_def:
            _defines[m_def.group(1)] = m_def.group(2)
            continue

        # ── #include ─────────────────────────────────────────────────────────
        m_inc = _INCLUDE_RE.match(linea)
        if m_inc:
            raw  = m_inc.group(1)
            ruta = raw if os.path.isabs(raw) else os.path.join(base_dir, raw)
            candidatos = [ruta, os.path.join(os.getcwd(), raw)]
            incluido = False
            for c in candidatos:
                try:
                    with open(c, 'r', encoding='utf-8') as f:
                        sub = f.readlines()
                    abs_c = os.path.abspath(c)
                    print(f"  [include] {abs_c}  ({len(sub)} líneas)")
                    resultado.extend(
                        preprocesar(sub, os.path.dirname(abs_c), _depth + 1, _defines)
                    )
                    incluido = True
                    break
                except FileNotFoundError:
                    continue
            if not incluido:
                print(f"  [WARN] #include '{raw}' no encontrado")
            continue

        # ── Sustitución de macros #define ─────────────────────────────────────
        for nombre, valor in _defines.items():
            linea = re.sub(r'\b' + re.escape(nombre) + r'\b', valor, linea)

        resultado.append(linea)

    return resultado


# =============================================================================
# TOKENIZACIÓN DE UNA LÍNEA (usando el lexer PLY)
# =============================================================================

def tokenizar_linea(texto):
    """
    Devuelve lista de tokens PLY de una sola línea de ensamblador.
    Útil para depuración o etapa de análisis léxico aislada.
    """
    lexer.input(texto)
    tokens_out = []
    while True:
        tok = lexer.token()
        if tok is None:
            break
        if tok.type == 'NEWLINE':
            continue
        tokens_out.append(tok)
    return tokens_out


# =============================================================================
# UTILIDADES DE CODIFICACIÓN
# =============================================================================

def zfill_bin(num, bits):
    """Entero → binario de ancho fijo; negativos en complemento a 2."""
    if num < 0:
        num = num & ((1 << bits) - 1)
    return bin(num)[2:].zfill(bits)[-bits:]


# ─── Encode F1: reg/inmediato ─────────────────────────────────────────────────
def encode_f1(opcode, keywords):
    """
    Layout: [ pre(4) ][ opcode(10) ][ modo(6) ][ rd(4) ][ r1(4) ][ r2(4) ][ inm(32) ]
    """
    pre        = PRE_INSTR[1]["pre"]
    opcode_bin = zfill_bin(opcode, 10)
    modo = rd = r1 = r2 = 0
    inm_val = None
    regs = []

    for kw in keywords:
        kl = str(kw).lower()
        if kl.startswith("r") and kl[1:].isdigit() and int(kl[1:]) <= 15:
            regs.append(int(kl[1:]))
        else:
            try:
                inm_val = int(kw, 0) if isinstance(kw, str) else int(kw)
            except (ValueError, TypeError):
                pass

    n_regs  = len(regs)
    has_inm = inm_val is not None
    inm     = inm_val if has_inm else 0

    if   n_regs == 1 and not has_inm: modo = 0; rd = regs[0]
    elif n_regs == 1 and     has_inm: modo = 1; rd = regs[0]
    elif n_regs == 2 and not has_inm: modo = 2; rd, r1 = regs[0], regs[1]
    elif n_regs == 2 and     has_inm: modo = 3; rd, r1 = regs[0], regs[1]
    elif n_regs == 3 and not has_inm: modo = 4; rd, r1, r2 = regs
    elif n_regs == 3 and     has_inm: modo = 5; rd, r1, r2 = regs

    bits = (pre + opcode_bin
            + zfill_bin(modo, 6) + zfill_bin(rd, 4)
            + zfill_bin(r1, 4)   + zfill_bin(r2, 4)
            + zfill_bin(inm, 32))
    assert len(bits) == 64, f"F1 debe ser 64 bits, got {len(bits)}"
    return bits


# ─── Encode F2: memoria ────────────────────────────────────────────────────────
def encode_f2(opcode, keywords):
    """
    Layout: [ pre(4) ][ opcode(8) ][ modo(6) ][ r1(4) ][ base(4) ][ index(4) ][ scale(2) ][ offset(32) ]
    """
    pre        = PRE_INSTR[2]["pre"]
    opcode_bin = zfill_bin(opcode, 8)
    modo = r1 = base = index = 0
    scale = offset = 0
    regs = []
    literals = []

    for kw in keywords:
        kl = str(kw).lower()
        if kl.startswith("r") and kl[1:].isdigit() and int(kl[1:]) <= 15:
            regs.append(int(kl[1:]))
        else:
            try:
                literals.append(int(kw, 0) if isinstance(kw, str) else int(kw))
            except (ValueError, TypeError):
                pass

    if len(regs) > 0: r1    = regs[0]
    if len(regs) > 1: base  = regs[1]
    if len(regs) > 2: index = regs[2]
    if len(literals) > 0: scale  = literals[0]
    if len(literals) > 1: offset = literals[1]

    bits = (pre + opcode_bin
            + zfill_bin(modo, 6)   + zfill_bin(r1, 4)
            + zfill_bin(base, 4)   + zfill_bin(index, 4)
            + zfill_bin(scale, 2)  + zfill_bin(offset, 32))
    assert len(bits) == 64, f"F2 debe ser 64 bits, got {len(bits)}"
    return bits


# ─── Encode F3: saltos ────────────────────────────────────────────────────────
def encode_f3(opcode, keywords, tabla_simbolos=None, dir_actual=0):
    """
    Layout: [ pre(4) ][ opcode(10) ][ modo(6) ][ r1(4) ][ r2(4) ][ offset(32) ][ flags(4) ]
    """
    pre        = PRE_INSTR[3]["pre"]
    opcode_bin = zfill_bin(opcode, 10)
    modo = r1 = r2 = 0
    offset = flags = 0
    regs = []
    literals = []

    for kw in keywords:
        kl = str(kw).lower()
        if kl.startswith("r") and kl[1:].isdigit() and int(kl[1:]) <= 15:
            regs.append(int(kl[1:]))
        elif tabla_simbolos and kw in tabla_simbolos:
            dir_destino = tabla_simbolos[kw]
            if opcode in range(5, 10):      # relativos: jmpr, jzr, jnzr, jcr, jnr
                offset = dir_destino - dir_actual
                modo   = 2
            else:                           # absolutos
                offset = dir_destino
                modo   = 0
        else:
            try:
                literals.append(int(kw, 0) if isinstance(kw, str) else int(kw))
            except (ValueError, TypeError):
                print(f"  [WARN] símbolo '{kw}' no encontrado")

    if len(regs) > 0: r1 = regs[0]
    if len(regs) > 1: r2 = regs[1]
    if literals:      offset = literals[0]

    if modo == 0 and opcode in range(5, 10):
        modo = 2

    bits = (pre + opcode_bin
            + zfill_bin(modo, 6)   + zfill_bin(r1, 4)
            + zfill_bin(r2, 4)     + zfill_bin(offset, 32)
            + zfill_bin(flags, 4))
    assert len(bits) == 64, f"F3 debe ser 64 bits, got {len(bits)}"
    return bits


# ─── Encode F4: control ───────────────────────────────────────────────────────
def encode_f4(opcode, keywords):
    """
    Layout: [ pre(4) ][ opcode(6) ][ modo(6) ][ inm32(32) ][ padding(16) ]
    """
    pre        = PRE_INSTR[4]["pre"]
    opcode_bin = zfill_bin(opcode, 6)
    modo  = 0
    inm32 = 0

    for kw in keywords:
        kl = str(kw).lower()
        if not (kl.startswith("r") and kl[1:].isdigit()):
            try:
                inm32 = int(kw, 0) if isinstance(kw, str) else int(kw)
                modo  = 1
            except (ValueError, TypeError):
                pass

    bits = (pre + opcode_bin
            + zfill_bin(modo, 6)
            + zfill_bin(inm32, 32)
            + zfill_bin(0, 16))
    assert len(bits) == 64, f"F4 debe ser 64 bits, got {len(bits)}"
    return bits


# ─── Encode F5: FPU ───────────────────────────────────────────────────────────
def encode_f5(opcode, keywords):
    """
    Layout: [ pre(4) ][ opcode(10) ][ modo(6) ][ rd(4) ][ r1(4) ][ r2(4) ][ inm(32) ]
    El inmediato puede ser float IEEE-754 o entero.
    """
    pre        = PRE_INSTR[5]["pre"]
    opcode_bin = zfill_bin(opcode, 10)
    modo = rd = r1 = r2 = 0
    inm_val = None
    regs = []

    for kw in keywords:
        kl = str(kw).lower()
        if kl.startswith("r") and kl[1:].isdigit() and int(kl[1:]) <= 15:
            regs.append(int(kl[1:]))
        else:
            is_float = isinstance(kw, float) or (
                isinstance(kw, str)
                and ('.' in kw or 'e' in kw.lower())
                and not kw.lower().startswith('0x')
            )
            if is_float:
                f = kw if isinstance(kw, float) else float(kw)
                inm_val = struct.unpack('>I', struct.pack('>f', f))[0]
            else:
                try:
                    inm_val = int(kw, 0) if isinstance(kw, str) else int(kw)
                except (ValueError, TypeError):
                    pass

    n_regs  = len(regs)
    has_inm = inm_val is not None
    inm     = inm_val if has_inm else 0

    if   n_regs == 1 and not has_inm: modo = 0; rd = regs[0]
    elif n_regs == 1 and     has_inm: modo = 1; rd = regs[0]
    elif n_regs == 2 and not has_inm: modo = 2; rd, r1 = regs[0], regs[1]
    elif n_regs == 2 and     has_inm: modo = 3; rd, r1 = regs[0], regs[1]

    bits = (pre + opcode_bin
            + zfill_bin(modo, 6) + zfill_bin(rd, 4)
            + zfill_bin(r1, 4)   + zfill_bin(r2, 4)
            + zfill_bin(inm, 32))
    assert len(bits) == 64, f"F5 debe ser 64 bits, got {len(bits)}"
    return bits


ENCODERS = {1: encode_f1, 2: encode_f2, 3: encode_f3, 4: encode_f4, 5: encode_f5}


# =============================================================================
# PASADA 1 — construir tabla de símbolos usando el lexer PLY
# =============================================================================

def primera_pasada(lineas):
    """
    Recorre las líneas usando el lexer léxico para identificar
    ETIQUETA_DEF e INSTRUCCION, y asigna la dirección de cada etiqueta.
    Cada instrucción ocupa 8 bytes (64 bits).
    """
    tabla     = {}
    direccion = 0

    for linea in lineas:
        linea_str = linea.strip()
        if not linea_str:
            continue

        toks = tokenizar_linea(linea_str)
        if not toks:
            continue

        tiene_instruccion = any(t.type == 'INSTRUCCION' for t in toks)

        for tok in toks:
            if tok.type == 'ETIQUETA_DEF':
                nombre = tok.value
                if nombre in tabla:
                    print(f"  [WARN] etiqueta duplicada '{nombre}'")
                tabla[nombre] = direccion

        if tiene_instruccion:
            direccion += 8

    return tabla


# =============================================================================
# PASADA 2 — ensamblado usando el lexer PLY
# =============================================================================

def segunda_pasada(lineas, tabla_simbolos):
    """
    Por cada línea:
      1. Tokeniza con PLY/lex
      2. Extrae la instrucción y sus operandos
      3. Codifica en 64 bits según el formato correspondiente
    """
    resultados = []
    direccion  = 0

    for num_linea, linea in enumerate(lineas, 1):
        toks = tokenizar_linea(linea)
        if not toks:
            continue

        # Extraer instrucción
        instr_toks = [t for t in toks if t.type == 'INSTRUCCION']
        if not instr_toks:
            continue

        instr   = instr_toks[0].value
        info    = INSTR_DICT[instr]
        formato = info["formato"]
        opcode  = info["opcode"]

        # Extraer operandos: registros, números, identificadores
        operandos = []
        for t in toks:
            if t.type == 'REGISTRO':
                operandos.append(f"r{t.value}")
            elif t.type in ('NUMERO_HEX', 'NUMERO_BIN', 'NUMERO_INT'):
                operandos.append(t.value)          # ya es int
            elif t.type == 'NUMERO_FLOAT':
                operandos.append(t.value)          # ya es float
            elif t.type == 'IDENTIFICADOR':
                operandos.append(t.value)          # etiqueta destino

        try:
            if formato == 3:
                bits = encode_f3(opcode, operandos,
                                 tabla_simbolos=tabla_simbolos,
                                 dir_actual=direccion)
            else:
                bits = ENCODERS[formato](opcode, operandos)
        except Exception as e:
            print(f"  [L{num_linea}] ERROR al codificar '{instr}': {e}")
            continue

        hex_word  = hex(int(bits, 2))
        resultado = f"  0x{direccion:04X}  {instr:6}  {bits}  ({hex_word})"
        resultados.append((direccion, bits, resultado))
        print(resultado)
        direccion += 8

    return resultados


# =============================================================================
# MODO DEMO DE ANÁLISIS LÉXICO
# =============================================================================

def demo_lexico(lineas):
    """
    Muestra los tokens reconocidos por el analizador léxico para
    cada línea del programa fuente. Útil para depuración y documentación.
    """
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║         ANÁLISIS LÉXICO — TOKENS RECONOCIDOS                ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    cat_width = 15
    for num, linea in enumerate(lineas, 1):
        linea_str = linea.rstrip()
        if not linea_str.strip():
            continue
        toks = tokenizar_linea(linea_str)
        if not toks:
            continue
        print(f"\n  Línea {num:3}: {linea_str}")
        print(f"  {'─'*60}")
        print(f"  {'TIPO':<{cat_width}}  VALOR")
        print(f"  {'─'*cat_width}  {'─'*30}")
        for t in toks:
            print(f"  {t.type:<{cat_width}}  {repr(t.value)}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    if len(sys.argv) < 2:
        print("Uso: python assembler_lex.py <archivo.asm> [salida.bin] [--lexico]")
        print()
        print("Opciones:")
        print("  --lexico   Muestra todos los tokens reconocidos (modo demo)")
        print()
        print("Directivas del preprocesador:")
        print("  #include <archivo.asm>")
        print("  #include \"archivo.asm\"")
        print("  #define CONST_VALOR 42")
        print()
        print("Ejemplo:")
        print("  python assembler_lex.py programa.asm salida.bin")
        print("  python assembler_lex.py programa.asm --lexico")
        sys.exit(1)

    input_file  = sys.argv[1]
    output_file = None
    modo_lexico = '--lexico' in sys.argv

    for arg in sys.argv[2:]:
        if not arg.startswith('--'):
            output_file = arg

    base_dir = os.path.dirname(os.path.abspath(input_file))

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
    except FileNotFoundError:
        print(f"ERROR: archivo '{input_file}' no encontrado")
        sys.exit(1)

    # ── PREPROCESADOR ──────────────────────────────────────────────────────────
    print(f"\n[1/3] Preprocesando '{input_file}'...")
    lineas = preprocesar(lineas, base_dir=base_dir)
    print(f"  → {len(lineas)} líneas tras expandir directivas")

    # ── DEMO LÉXICO (opcional) ─────────────────────────────────────────────────
    if modo_lexico:
        demo_lexico(lineas)
        print()

    # ── PASADA 1: tabla de símbolos ────────────────────────────────────────────
    print("\n[2/3] Pasada 1 — tabla de símbolos (análisis léxico PLY):")
    tabla_simbolos = primera_pasada(lineas)

    if tabla_simbolos:
        for nombre, dir_ in tabla_simbolos.items():
            print(f"  {nombre:25} → 0x{dir_:04X}  ({dir_} bytes)")
    else:
        print("  (sin etiquetas)")

    # ── PASADA 2: ensamblado ───────────────────────────────────────────────────
    print("\n[3/3] Pasada 2 — ensamblado:")
    resultados = segunda_pasada(lineas, tabla_simbolos)

    # ── Guardar en archivo ─────────────────────────────────────────────────────
    if output_file:
        try:
            with open(output_file, 'w') as f:
                for _, bits, _ in resultados:
                    for i in range(0, len(bits), 8):
                        f.write(bits[i:i+8] + '\n')
            print(f"\n✓ Bytecode guardado en '{output_file}' "
                  f"({len(resultados)} instrucciones, "
                  f"{len(resultados)*8} bytes)")
        except Exception as e:
            print(f"\nERROR al escribir '{output_file}': {e}")
            sys.exit(1)
    else:
        print(f"\n✓ {len(resultados)} instrucciones ensambladas "
              "(usa un segundo argumento para guardar el binario)")


if __name__ == "__main__":
    main()
