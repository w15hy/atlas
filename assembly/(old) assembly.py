"""
assembly.py — Ensamblador de dos pasadas para la máquina sy_00
==============================================================
Novedad v2:
  • Directiva  #include <archivo>  (preprocesador)
  • Instrucción  ret  (F4 opcode 3)
  • Instrucción  iret (F4 opcode 4)
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# Tabla de instrucciones
# ---------------------------------------------------------------------------

instr_dict = {
    # ===== FORMATO 1  pre=0001  opcode=10 bits =====
    "mov":  {"opcode": 0,  "formato": 1},
    "push": {"opcode": 1,  "formato": 1},
    "pop":  {"opcode": 2,  "formato": 1},
    "xchg": {"opcode": 3,  "formato": 1},
    "add":  {"opcode": 4,  "formato": 1},
    "addi": {"opcode": 5,  "formato": 1},
    "sub":  {"opcode": 6,  "formato": 1},
    "subi": {"opcode": 7
             ,  "formato": 1},
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
    "mod": {"opcode":  25, "formato": 1},
    "modi": {"opcode": 26, "formato": 1},

    # ===== FORMATO 2  pre=0010  opcode=8 bits =====
    "load":  {"opcode": 0, "formato": 2},
    "store": {"opcode": 1, "formato": 2},
    "lea":   {"opcode": 2, "formato": 2},

    # ===== FORMATO 3  pre=0011  opcode=10 bits =====
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

    # ===== FORMATO 4  pre=0000  opcode=6 bits =====
    "nop":  {"opcode": 0, "formato": 4},
    "halt": {"opcode": 1, "formato": 4},
    "inti": {"opcode": 2, "formato": 4},
    "ret":  {"opcode": 3, "formato": 4},   # ← NUEVO
    "iret": {"opcode": 4, "formato": 4},   # ← NUEVO

    # ===== FORMATO 5  pre=0100  opcode=10 bits  FPU =====
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

# pre(4) → opcode_bits
pre_instr = {
    1: {"pre": "0001", "opcode_bits": 10},  # F1: reg/inm
    2: {"pre": "0010", "opcode_bits": 8},   # F2: memoria
    3: {"pre": "0011", "opcode_bits": 10},  # F3: saltos
    4: {"pre": "0000", "opcode_bits": 6},   # F4: control
    5: {"pre": "0100", "opcode_bits": 10},  # F5: FPU
}

# Modos F1
MODOS_F1 = {
    "registro":                                   0,
    "registro - inmediato":                       1,
    "registro - registro":                        2,
    "registro - registro - inmediato":            3,
    "registro - registro - registro":             4,
    "registro - registro - registro - inmediato": 5,
}


def zfill_bin(num, bits):
    """Convierte entero a binario de ancho fijo; maneja negativos en C2."""
    if num < 0:
        num = num & ((1 << bits) - 1)
    return bin(num)[2:].zfill(bits)[-bits:]


# ---------------------------------------------------------------------------
# PREPROCESADOR — expande directivas  #include <archivo>
# ---------------------------------------------------------------------------

_INCLUDE_RE = re.compile(r'^\s*#include\s+[<"]([^>"]+)[>"]\s*$')


def preprocesar(lineas, base_dir='.', _depth=0):
    """
    Expande directivas  #include <ruta>  o  #include "ruta"
    de forma recursiva hasta una profundidad máxima de 10 niveles.

    Parámetros:
        lineas   : list[str]  líneas del archivo fuente
        base_dir : str        directorio desde donde resolver rutas relativas
        _depth   : int        nivel de recursión actual (uso interno)

    Retorna:
        list[str]  con todas las líneas ya expandidas
    """
    if _depth > 10:
        raise RecursionError(
            "Demasiados niveles de #include (¿inclusión circular?)"
        )

    resultado = []
    for linea in lineas:
        m = _INCLUDE_RE.match(linea)
        if m:
            ruta = m.group(1)
            if not os.path.isabs(ruta):
                ruta = os.path.join(base_dir, ruta)

            raw = m.group(1)
            candidatos = [ruta, os.path.join(os.getcwd(), raw)]
            incluido = False
            for c in candidatos:
                try:
                    with open(c, 'r', encoding='utf-8') as f:
                        incluidas = f.readlines()
                    abs_c = os.path.abspath(c)
                    print(f"  [include] {abs_c}  ({len(incluidas)} líneas)")
                    resultado.extend(preprocesar(incluidas, os.path.dirname(abs_c), _depth + 1))
                    incluido = True
                    break
                except FileNotFoundError:
                    continue
            if not incluido:
                print(f"  error: #include — '{raw}' no encontrado")
        else:
            resultado.append(linea)

    return resultado


# ---------------------------------------------------------------------------
# PASADA 1: construir tabla de símbolos
# ---------------------------------------------------------------------------

def primera_pasada(lineas):
    """
    Asigna a cada etiqueta su dirección en bytes.
    Cada instrucción ocupa 8 bytes (64 bits).
    Retorna  { "loop": 8, "fin": 40, ... }
    """
    tabla = {}
    direccion = 0

    for linea in lineas:
        linea_limpia = linea.strip()

        if not linea_limpia or linea_limpia.startswith("#"):
            continue

        if "#" in linea_limpia:
            linea_limpia = linea_limpia[:linea_limpia.index("#")].strip()
        if not linea_limpia:
            continue

        # Etiqueta sola:  "loop:"
        if linea_limpia.endswith(":") and " " not in linea_limpia:
            nombre = linea_limpia[:-1]
            if nombre in tabla:
                print(f"  advertencia: etiqueta '{nombre}' duplicada")
            tabla[nombre] = direccion
            continue

        # Etiqueta + instrucción:  "fin: halt"
        if ":" in linea_limpia:
            partes = linea_limpia.split(":", 1)
            nombre = partes[0].strip()
            if re.match(r'^[A-Za-z_]\w*$', nombre):
                if nombre in tabla:
                    print(f"  advertencia: etiqueta '{nombre}' duplicada")
                tabla[nombre] = direccion
            resto = partes[1].strip()
            if resto and not resto.startswith("#"):
                direccion += 8
            continue

        # Línea de instrucción normal
        direccion += 8

    return tabla


# ---------------------------------------------------------------------------
# Encoders
# ---------------------------------------------------------------------------

def encode_f1(opcode, keywords):
    """
    [ pre(4) ][ opcode(10) ][ modo(6) ][ rd(4) ][ r1(4) ][ r2(4) ][ inm(32) ]
    = 64 bits
    """
    pre        = pre_instr[1]["pre"]
    opcode_bin = zfill_bin(opcode, 10)
    modo = rd = r1 = r2 = 0
    inm_val = None
    regs = []

    for kw in keywords:
        kl = kw.lower()
        if kl.startswith("r") and kl[1:].isdigit() and int(kl[1:]) <= 15:
            regs.append(int(kl[1:]))
        else:
            inm_val = int(kw, 0)

    n_regs  = len(regs)
    has_inm = inm_val is not None
    inm     = inm_val if has_inm else 0

    if   n_regs == 1 and not has_inm: modo = 0; rd = regs[0]
    elif n_regs == 1 and     has_inm: modo = 1; rd = regs[0]
    elif n_regs == 2 and not has_inm: modo = 2; rd, r1 = regs[0], regs[1]
    elif n_regs == 2 and     has_inm: modo = 3; rd, r1 = regs[0], regs[1]
    elif n_regs == 3 and not has_inm: modo = 4; rd, r1, r2 = regs
    elif n_regs == 3 and     has_inm: modo = 5; rd, r1, r2 = regs

    bits = (
        pre
        + opcode_bin
        + zfill_bin(modo, 6)
        + zfill_bin(rd,   4)
        + zfill_bin(r1,   4)
        + zfill_bin(r2,   4)
        + zfill_bin(inm, 32)
    )
    assert len(bits) == 64, f"F1 debe ser 64 bits, got {len(bits)}"
    return bits


def encode_f2(opcode, keywords):
    """
    [ pre(4) ][ opcode(8) ][ modo(6) ][ r1(4) ][ base(4) ][ index(4) ][ scale(2) ][ offset(32) ]
    = 64 bits
    """
    pre        = pre_instr[2]["pre"]
    opcode_bin = zfill_bin(opcode, 8)
    modo = r1 = base = index = 0
    scale = offset = 0
    regs = []
    literals = []

    for kw in keywords:
        kl = kw.lower()
        if kl.startswith("r") and kl[1:].isdigit() and int(kl[1:]) <= 15:
            regs.append(int(kl[1:]))
        else:
            literals.append(int(kw, 0))

    if len(regs) > 0: r1    = regs[0]
    if len(regs) > 1: base  = regs[1]
    if len(regs) > 2: index = regs[2]
    if len(literals) > 0: scale  = literals[0]
    if len(literals) > 1: offset = literals[1]

    bits = (
        pre
        + opcode_bin
        + zfill_bin(modo,   6)
        + zfill_bin(r1,     4)
        + zfill_bin(base,   4)
        + zfill_bin(index,  4)
        + zfill_bin(scale,  2)
        + zfill_bin(offset, 32)
    )
    assert len(bits) == 64, f"F2 debe ser 64 bits, got {len(bits)}"
    return bits


def encode_f3(opcode, keywords, tabla_simbolos=None, dir_actual=0):
    """
    [ pre(4) ][ opcode(10) ][ modo(6) ][ r1(4) ][ r2(4) ][ offset(32) ][ flags(4) ]
    = 64 bits

    Resolución de etiquetas:
      - jmpr/jzr/jnzr/jcr/jnr (opcodes 5-9) → salto relativo
      - resto                                 → salto absoluto
    """
    pre        = pre_instr[3]["pre"]
    opcode_bin = zfill_bin(opcode, 10)
    modo = r1 = r2 = 0
    offset = flags = 0
    regs = []
    literals = []

    for kw in keywords:
        kl = kw.lower()
        if kl.startswith("r") and kl[1:].isdigit() and int(kl[1:]) <= 15:
            regs.append(int(kl[1:]))
        elif tabla_simbolos and kw in tabla_simbolos:
            dir_destino = tabla_simbolos[kw]
            if opcode in range(5, 10):      # saltos relativos
                offset = dir_destino - dir_actual
                modo   = 2
            else:                           # saltos absolutos
                offset = dir_destino
                modo   = 0
        else:
            try:
                literals.append(int(kw, 0))
            except ValueError:
                print(f"  advertencia: símbolo '{kw}' no encontrado")

    if len(regs) > 0: r1 = regs[0]
    if len(regs) > 1: r2 = regs[1]
    if literals:      offset = literals[0]

    if modo == 0 and opcode in range(5, 10):
        modo = 2

    bits = (
        pre
        + opcode_bin
        + zfill_bin(modo,   6)
        + zfill_bin(r1,     4)
        + zfill_bin(r2,     4)
        + zfill_bin(offset, 32)
        + zfill_bin(flags,  4)
    )
    assert len(bits) == 64, f"F3 debe ser 64 bits, got {len(bits)}"
    return bits


def encode_f4(opcode, keywords):
    """
    [ pre(4) ][ opcode(6) ][ modo(6) ][ inm32(32) ][ padding(16) ]
    = 64 bits
    """
    pre        = pre_instr[4]["pre"]
    opcode_bin = zfill_bin(opcode, 6)
    modo  = 0
    inm32 = 0

    for kw in keywords:
        kl = kw.lower()
        if not (kl.startswith("r") and kl[1:].isdigit()):
            inm32 = int(kw, 0)
            modo  = 1

    bits = (
        pre
        + opcode_bin
        + zfill_bin(modo,   6)
        + zfill_bin(inm32, 32)
        + zfill_bin(0,     16)   # padding
    )
    assert len(bits) == 64, f"F4 debe ser 64 bits, got {len(bits)}"
    return bits


def encode_f5(opcode, keywords):
    """
    F5 — FPU  (mismo layout que F1)
    [ pre(4) ][ opcode(10) ][ modo(6) ][ rd(4) ][ r1(4) ][ r2(4) ][ inm(32) ]
    = 64 bits

    El inmediato puede ser:
      • float literal  (3.14, -2.5, 100.0) → se convierte a bits IEEE 754 de 32 bits
      • int literal    (0xFF, 42)           → se usa directamente (raw bits)
    """
    import struct as _struct
    pre        = pre_instr[5]["pre"]
    opcode_bin = zfill_bin(opcode, 10)
    modo = rd = r1 = r2 = 0
    inm_val = None
    regs = []

    for kw in keywords:
        kl = kw.lower()
        if kl.startswith("r") and kl[1:].isdigit() and int(kl[1:]) <= 15:
            regs.append(int(kl[1:]))
        else:
            # Float si tiene '.' o 'e' y no empieza con 0x
            is_float = ('.' in kw or 'e' in kw.lower()) and not kw.lower().startswith('0x')
            if is_float:
                f = float(kw)
                inm_val = _struct.unpack('>I', _struct.pack('>f', f))[0]
            else:
                inm_val = int(kw, 0)

    n_regs  = len(regs)
    has_inm = inm_val is not None
    inm     = inm_val if has_inm else 0

    if   n_regs == 1 and not has_inm: modo = 0; rd = regs[0]
    elif n_regs == 1 and     has_inm: modo = 1; rd = regs[0]
    elif n_regs == 2 and not has_inm: modo = 2; rd, r1 = regs[0], regs[1]
    elif n_regs == 2 and     has_inm: modo = 3; rd, r1 = regs[0], regs[1]

    bits = (
        pre
        + opcode_bin
        + zfill_bin(modo, 6)
        + zfill_bin(rd,   4)
        + zfill_bin(r1,   4)
        + zfill_bin(r2,   4)
        + zfill_bin(inm, 32)
    )
    assert len(bits) == 64, f"F5 debe ser 64 bits, got {len(bits)}"
    return bits


ENCODERS = {1: encode_f1, 2: encode_f2, 3: encode_f3, 4: encode_f4, 5: encode_f5}


# ---------------------------------------------------------------------------
# Utilidad: normalizar una línea
# ---------------------------------------------------------------------------

def limpiar_linea(linea):
    """
    Devuelve (instruccion_str | None).
    Elimina comentarios inline, etiquetas y líneas vacías.
    """
    s = linea.strip()
    if not s or s.startswith("#"):
        return None
    if "#" in s:
        s = s[:s.index("#")].strip()
    if not s:
        return None
    # Etiqueta sola
    if s.endswith(":") and " " not in s:
        return None
    # Etiqueta + instrucción → solo instrucción
    if ":" in s:
        partes = s.split(":", 1)
        if re.match(r'^[A-Za-z_]\w*$', partes[0].strip()):
            s = partes[1].strip()
    return s if s else None


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Uso: python assembly.py <archivo.asm> [salida.bin]")
        print()
        print("Directivas del preprocesador:")
        print("  #include <stdlib/vecmat.asm>   # incluye biblioteca")
        print("  #include \"mi_modulo.asm\"")
        print()
        print("Etiquetas:")
        print("  loop:          # etiqueta sola")
        print("  fin: halt      # etiqueta + instrucción")
        print()
        print("Ejemplo:")
        print("  python assembly.py programa.asm programa.bin")
        sys.exit(1)

    input_file  = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    base_dir    = os.path.dirname(os.path.abspath(input_file))

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
    except FileNotFoundError:
        print(f"error: archivo '{input_file}' no encontrado")
        sys.exit(1)

    # ── PREPROCESADOR (#include) ────────────────────────────────────────────
    print(f"\n[1/3] Preprocesando '{input_file}'...")
    lineas = preprocesar(lineas, base_dir=base_dir)
    print(f"  → {len(lineas)} líneas tras expandir includes")

    # ── PASADA 1: tabla de símbolos ─────────────────────────────────────────
    print("\n[2/3] Pasada 1 — tabla de símbolos:")
    tabla_simbolos = primera_pasada(lineas)

    if tabla_simbolos:
        for nombre, dir_ in tabla_simbolos.items():
            print(f"  {nombre:25} → 0x{dir_:04X}  ({dir_} bytes)")
    else:
        print("  (sin etiquetas)")

    # ── PASADA 2: ensamblado ────────────────────────────────────────────────
    print("\n[3/3] Pasada 2 — ensamblado:")
    resultados = []
    direccion  = 0

    for num_linea, linea in enumerate(lineas, 1):
        instr_str = limpiar_linea(linea)
        if instr_str is None:
            continue

        partes   = re.split(r"[ ,]+", instr_str)
        instr    = partes[0].lower()
        keywords = [p for p in partes[1:] if p]

        if instr not in instr_dict:
            print(f"  [L{num_linea}] error: instrucción desconocida '{instr}'")
            continue

        info    = instr_dict[instr]
        formato = info["formato"]
        opcode  = info["opcode"]

        try:
            if formato == 3:
                bits = encode_f3(opcode, keywords,
                                 tabla_simbolos=tabla_simbolos,
                                 dir_actual=direccion)
            else:
                bits = ENCODERS[formato](opcode, keywords)
        except Exception as e:
            print(f"  [L{num_linea}] error al codificar '{instr_str}': {e}")
            continue

        resultado = f"  0x{direccion:04X}  {instr:6}  {bits}"
        resultados.append((direccion, bits, resultado))
        print(resultado)
        direccion += 8

    # ── Guardar en archivo ──────────────────────────────────────────────────
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
            print(f"\nerror al escribir '{output_file}': {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
