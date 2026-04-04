"""
linker_loader.py — Enlazador-Cargador con análisis léxico (PLY/lex) para sy_00
================================================================================
Módulo que completa el pipeline:

    .asm -> [PREPROCESADOR] -> [LEXER/ENSAMBLADOR] -> .obj -> [LINKER-LOADER] -> .bin

Recibe uno o más archivos fuente (.asm), los ensambla individualmente en
módulos objeto, luego enlaza (resuelve símbolos y reubicaciones) y genera
un único archivo binario listo para cargar en la RAM de la máquina sy_00.

Pipeline completo:
  1. PREPROCESADOR  — expande #include y #define  (assembly_lex.preprocesar)
  2. LEXER (PLY)    — tokeniza cada línea          (assembly_lex.tokenizar_linea)
  3. ENSAMBLADOR    — dos pasadas por módulo        (assembly_lex.primera/segunda_pasada)
  4. ENLAZADOR      — resuelve símbolos globales y reubica direcciones
  5. CARGADOR       — escribe el binario final (.bin) con 1 byte por línea

Directivas nuevas reconocidas por el lexer:
  .global NOMBRE   — Exporta un símbolo para que otros módulos lo vean
  .extern NOMBRE   — Declara un símbolo definido en otro módulo

Uso:
    python linker_loader.py mod1.asm mod2.asm [mod3.asm ...] -o salida.bin
    python linker_loader.py mod1.asm mod2.asm --lexico
    python linker_loader.py mod1.asm mod2.asm --mapa
"""

import os
import re
import sys
import json
import struct
import copy

import ply.lex as lex

# Importar componentes del ensamblador existente
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assembly_lex import (
    INSTR_DICT, PRE_INSTR, MNEMONICS, ENCODERS,
    preprocesar, tokenizar_linea, zfill_bin,
    encode_f1, encode_f2, encode_f3, encode_f4, encode_f5,
)


# =============================================================================
# CONSTANTES DEL ENLAZADOR
# =============================================================================

INSTR_SIZE       = 8        # 8 bytes (64 bits) por instrucción
TEXT_BASE        = 0x0000   # Sección .text empieza en dirección 0
DATA_BASE        = 0x2000   # Sección .data  (reservado para uso futuro)

# Tipos de binding de símbolos
SYM_LOCAL   = 0   # Solo visible dentro de su módulo
SYM_GLOBAL  = 1   # Exportado, visible desde otros módulos
SYM_EXTERN  = 2   # Referencia externa (definido en otro módulo)

# Tipos de reubicación
REL_ABS     = 0   # Dirección absoluta (32 bits en campo offset/inmediato)
REL_REL     = 1   # Dirección relativa al PC


# =============================================================================
# LEXER EXTENDIDO — agrega .global y .extern como tokens
# =============================================================================

tokens = (
    'INSTRUCCION',
    'REGISTRO',
    'NUMERO_HEX',
    'NUMERO_BIN',
    'NUMERO_FLOAT',
    'NUMERO_INT',
    'ETIQUETA_DEF',
    'IDENTIFICADOR',
    'DIRECTIVA',
    'DIR_GLOBAL',      # .global
    'DIR_EXTERN',      # .extern
    'COMA',
    'NEWLINE',
)


def t_COMENTARIO(t):
    r'\#(?!include|define)[^\n]*'
    pass

def t_DIRECTIVA(t):
    r'\#include\s+[<"][^>"]+[>"]|\#define\s+\w+\s+.*'
    return t

def t_DIR_GLOBAL(t):
    r'\.global'
    return t

def t_DIR_EXTERN(t):
    r'\.extern'
    return t

def t_NUMERO_HEX(t):
    r'-?0[xX][0-9A-Fa-f]+'
    t.value = int(t.value, 16)
    return t

def t_NUMERO_BIN(t):
    r'-?0[bB][01]+'
    t.value = int(t.value, 2)
    return t

def t_NUMERO_FLOAT(t):
    r'-?[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?|-?[0-9]+[eE][+-]?[0-9]+'
    t.value = float(t.value)
    return t

def t_REGISTRO(t):
    r'[rR](1[0-5]|[0-9])(?!\w)'
    t.value = int(t.value[1:])
    return t

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

def t_NUMERO_INT(t):
    r'-?[0-9]+'
    t.value = int(t.value)
    return t

t_COMA   = r','
t_ignore = ' \t\r'

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

def t_error(t):
    print(f"  [LEX-LINK] Carácter no reconocido '{t.value[0]}' en línea {t.lexer.lineno}")
    t.lexer.skip(1)

linker_lexer = lex.lex(debug=False, errorlog=lex.NullLogger(), outputdir='/tmp')


def tokenizar_linea_linker(texto):
    """Tokeniza una línea usando el lexer extendido con .global/.extern."""
    linker_lexer.input(texto)
    toks = []
    while True:
        tok = linker_lexer.token()
        if tok is None:
            break
        if tok.type == 'NEWLINE':
            continue
        toks.append(tok)
    return toks


# =============================================================================
# MÓDULO OBJETO — representación intermedia de un archivo ensamblado
# =============================================================================

class ObjectModule:
    """
    Resultado de ensamblar un solo archivo .asm.

    Atributos:
        nombre      — nombre del archivo fuente
        code        — lista de strings binarios de 64 bits (una por instrucción)
        symbols     — dict {nombre: {address, binding, section}}
        relocations — lista de {offset, symbol, rel_type, instr_index, formato}
        size        — tamaño total del código en bytes
    """
    def __init__(self, nombre):
        self.nombre      = nombre
        self.code        = []     # ["0001...", "0011...", ...]
        self.symbols     = {}     # {name: {address, binding}}
        self.relocations = []     # [{offset, symbol, rel_type, instr_index, formato}]
        self.size        = 0      # total bytes

    def to_dict(self):
        return {
            "nombre":      self.nombre,
            "code":        self.code,
            "symbols":     self.symbols,
            "relocations": self.relocations,
            "size":        self.size,
        }


# =============================================================================
# FASE 1 — ENSAMBLAR UN MÓDULO (preprocesar + lexer + dos pasadas)
# =============================================================================

def _extraer_directivas(lineas):
    """
    Recorre las líneas buscando .global y .extern.
    Retorna:
        globals_set  — set de nombres exportados
        externs_set  — set de nombres importados
        lineas_clean — líneas sin las directivas .global/.extern
    """
    globals_set  = set()
    externs_set  = set()
    lineas_clean = []

    for linea in lineas:
        s = linea.strip()
        if not s:
            lineas_clean.append(linea)
            continue

        toks = tokenizar_linea_linker(s)
        if not toks:
            lineas_clean.append(linea)
            continue

        if toks[0].type == 'DIR_GLOBAL':
            for t in toks[1:]:
                if t.type == 'IDENTIFICADOR':
                    globals_set.add(t.value)
            continue
        elif toks[0].type == 'DIR_EXTERN':
            for t in toks[1:]:
                if t.type == 'IDENTIFICADOR':
                    externs_set.add(t.value)
            continue

        lineas_clean.append(linea)

    return globals_set, externs_set, lineas_clean


def _primera_pasada_modulo(lineas):
    """
    Pasada 1: construye tabla de símbolos locales (etiqueta -> dirección relativa).
    Cada instrucción ocupa 8 bytes.
    """
    tabla     = {}
    direccion = 0

    for linea in lineas:
        s = linea.strip()
        if not s:
            continue
        toks = tokenizar_linea(s)
        if not toks:
            continue

        tiene_instr = any(t.type == 'INSTRUCCION' for t in toks)

        for tok in toks:
            if tok.type == 'ETIQUETA_DEF':
                if tok.value in tabla:
                    print(f"  [WARN] etiqueta duplicada '{tok.value}'")
                tabla[tok.value] = direccion

        if tiene_instr:
            direccion += INSTR_SIZE

    return tabla


def _segunda_pasada_modulo(lineas, tabla_simbolos, externs_set):
    """
    Pasada 2: ensambla instrucciones y registra las reubicaciones necesarias
    para símbolos externos o etiquetas que necesitan dirección final.

    Retorna:
        code         — lista de cadenas binarias de 64 bits
        relocations  — lista de dicts con info de reubicación
    """
    code        = []
    relocations = []
    direccion   = 0

    for num_linea, linea in enumerate(lineas, 1):
        toks = tokenizar_linea(linea)
        if not toks:
            continue

        instr_toks = [t for t in toks if t.type == 'INSTRUCCION']
        if not instr_toks:
            continue

        instr   = instr_toks[0].value
        info    = INSTR_DICT[instr]
        formato = info["formato"]
        opcode  = info["opcode"]

        # Extraer operandos
        operandos = []
        sym_refs  = []   # símbolos referenciados en esta instrucción
        for t in toks:
            if t.type == 'REGISTRO':
                operandos.append(f"r{t.value}")
            elif t.type in ('NUMERO_HEX', 'NUMERO_BIN', 'NUMERO_INT'):
                operandos.append(t.value)
            elif t.type == 'NUMERO_FLOAT':
                operandos.append(t.value)
            elif t.type == 'IDENTIFICADOR':
                sym_refs.append(t.value)
                operandos.append(t.value)

        # Detectar si hay referencias a símbolos que necesitan reubicación
        for sym in sym_refs:
            if sym in externs_set:
                # Símbolo externo -> reubicación absoluta obligatoria
                is_relative = (formato == 3 and opcode in range(5, 10))
                relocations.append({
                    "offset":      direccion,
                    "symbol":      sym,
                    "rel_type":    REL_REL if is_relative else REL_ABS,
                    "instr_index": len(code),
                    "formato":     formato,
                    "opcode":      opcode,
                })
            elif sym in tabla_simbolos:
                # Símbolo local resuelto: registrarlo igualmente para reubicación
                # cuando se enlacen módulos (la dirección base cambiará)
                is_relative = (formato == 3 and opcode in range(5, 10))
                relocations.append({
                    "offset":      direccion,
                    "symbol":      sym,
                    "rel_type":    REL_REL if is_relative else REL_ABS,
                    "instr_index": len(code),
                    "formato":     formato,
                    "opcode":      opcode,
                })

        # Codificar la instrucción
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

        code.append(bits)
        direccion += INSTR_SIZE

    return code, relocations


def ensamblar_modulo(filepath):
    """
    Ensambla un archivo .asm completo y retorna un ObjectModule.

    Pipeline para un solo archivo:
      1. Leer archivo fuente
      2. Preprocesar (#include, #define)
      3. Extraer directivas .global / .extern
      4. Pasada 1: tabla de símbolos locales
      5. Pasada 2: codificación + reubicaciones
    """
    print(f"\n{'='*60}")
    print(f"  ENSAMBLANDO MÓDULO: {filepath}")
    print(f"{'='*60}")

    base_dir = os.path.dirname(os.path.abspath(filepath))

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lineas_raw = f.readlines()
    except FileNotFoundError:
        print(f"  ERROR: archivo '{filepath}' no encontrado")
        return None

    # 1. Preprocesar
    lineas = preprocesar(lineas_raw, base_dir=base_dir)
    print(f"  -> {len(lineas)} líneas tras preprocesar")

    # 2. Extraer .global / .extern
    globals_set, externs_set, lineas_clean = _extraer_directivas(lineas)
    if globals_set:
        print(f"  -> Símbolos exportados (.global): {globals_set}")
    if externs_set:
        print(f"  -> Símbolos externos  (.extern):  {externs_set}")

    # 3. Pasada 1
    tabla_local = _primera_pasada_modulo(lineas_clean)
    print(f"  -> Tabla de símbolos local:")
    for nombre, dir_ in tabla_local.items():
        binding = "GLOBAL" if nombre in globals_set else "LOCAL"
        print(f"      {nombre:25} -> 0x{dir_:04X}  [{binding}]")

    # 4. Pasada 2
    code, relocs = _segunda_pasada_modulo(lineas_clean, tabla_local, externs_set)
    print(f"  -> {len(code)} instrucciones ensambladas")
    print(f"  -> {len(relocs)} reubicaciones registradas")

    # 5. Construir ObjectModule
    obj          = ObjectModule(os.path.basename(filepath))
    obj.code     = code
    obj.size     = len(code) * INSTR_SIZE

    for nombre, dir_ in tabla_local.items():
        binding = SYM_GLOBAL if nombre in globals_set else SYM_LOCAL
        obj.symbols[nombre] = {"address": dir_, "binding": binding}

    for sym in externs_set:
        if sym not in obj.symbols:
            obj.symbols[sym] = {"address": 0, "binding": SYM_EXTERN}

    obj.relocations = relocs
    return obj


# =============================================================================
# FASE 2 — ENLAZADOR: combinar módulos, resolver símbolos, reubicar
# =============================================================================

def enlazar(modulos):
    """
    Enlaza una lista de ObjectModule en un único binario.

    Pasos:
      1. Asignar dirección base a cada módulo (layout secuencial)
      2. Construir tabla de símbolos global
      3. Resolver referencias externas
      4. Aplicar reubicaciones (parchear instrucciones con direcciones finales)
      5. Concatenar código final

    Retorna:
        code_final — lista de cadenas binarias de 64 bits, en orden
        mapa       — dict con info del enlace (para depuración/mapa)
    """
    print(f"\n{'='*60}")
    print(f"  ENLAZANDO {len(modulos)} MÓDULO(S)")
    print(f"{'='*60}")

    # ── Paso 1: Layout — asignar dirección base a cada módulo ─────────────
    base_addr = TEXT_BASE
    layout    = []   # [(módulo, base_addr)]

    for mod in modulos:
        layout.append((mod, base_addr))
        print(f"  {mod.nombre:30} base=0x{base_addr:04X}  tamaño={mod.size} bytes  "
              f"({len(mod.code)} instrucciones)")
        base_addr += mod.size

    total_size = base_addr
    print(f"  -> Tamaño total del binario: {total_size} bytes "
          f"({total_size // INSTR_SIZE} instrucciones)")

    # ── Paso 2: Tabla de símbolos global ─────────────────────────────────────
    tabla_global = {}   # {nombre: dirección_absoluta}
    errores      = []

    for mod, base in layout:
        for nombre, info in mod.symbols.items():
            if info["binding"] == SYM_EXTERN:
                continue   # se resuelve después

            dir_absoluta = base + info["address"]

            if info["binding"] == SYM_GLOBAL:
                if nombre in tabla_global:
                    errores.append(
                        f"Símbolo global '{nombre}' definido en múltiples módulos: "
                        f"{mod.nombre} y otro anterior"
                    )
                tabla_global[nombre] = dir_absoluta
            else:
                # Símbolo local: prefijado con nombre del módulo para evitar colisiones
                clave_local = f"{mod.nombre}::{nombre}"
                tabla_global[clave_local] = dir_absoluta
                # También guardar sin prefijo si no colisiona con un global
                if nombre not in tabla_global:
                    tabla_global[nombre] = dir_absoluta

    if errores:
        for e in errores:
            print(f"  [ERROR] {e}")
        return None, None

    print(f"\n  Tabla de símbolos global ({len(tabla_global)} entradas):")
    for nombre, addr in sorted(tabla_global.items(), key=lambda x: x[1]):
        if '::' not in nombre:   # solo mostrar nombres limpios
            print(f"      {nombre:30} -> 0x{addr:04X}")

    # ── Paso 3: Verificar que todos los extern están resueltos ───────────────
    for mod, base in layout:
        for nombre, info in mod.symbols.items():
            if info["binding"] == SYM_EXTERN:
                if nombre not in tabla_global:
                    errores.append(
                        f"Símbolo externo '{nombre}' (requerido por {mod.nombre}) "
                        f"no definido en ningún módulo"
                    )

    if errores:
        for e in errores:
            print(f"  [ERROR-LINK] {e}")
        return None, None

    # ── Paso 4: Aplicar reubicaciones ────────────────────────────────────────
    print(f"\n  Aplicando reubicaciones...")
    code_final = []

    for mod, base in layout:
        # Copiar código del módulo (deep copy para no mutar el original)
        mod_code = list(mod.code)

        for reloc in mod.relocations:
            sym_name    = reloc["symbol"]
            instr_idx   = reloc["instr_index"]
            rel_type    = reloc["rel_type"]
            formato     = reloc["formato"]
            opcode      = reloc["opcode"]
            instr_offset = reloc["offset"]   # dirección relativa dentro del módulo

            # Dirección absoluta del símbolo destino
            if sym_name in tabla_global:
                sym_addr = tabla_global[sym_name]
            else:
                # Buscar como símbolo local del mismo módulo
                clave = f"{mod.nombre}::{sym_name}"
                if clave in tabla_global:
                    sym_addr = tabla_global[clave]
                else:
                    print(f"  [ERROR] Símbolo '{sym_name}' no resuelto en {mod.nombre}")
                    continue

            # Dirección absoluta de esta instrucción
            instr_abs_addr = base + instr_offset

            # Calcular valor a parchear
            if rel_type == REL_REL:
                patch_value = sym_addr - instr_abs_addr
            else:
                patch_value = sym_addr

            # Parchear la instrucción según su formato
            old_bits = mod_code[instr_idx]
            new_bits = _parchear_instruccion(old_bits, formato, patch_value)

            if new_bits:
                mod_code[instr_idx] = new_bits
                print(f"    [{mod.nombre}] 0x{instr_abs_addr:04X}: "
                      f"{sym_name} -> 0x{sym_addr:04X} "
                      f"({'REL' if rel_type == REL_REL else 'ABS'} "
                      f"patch={patch_value})")

        code_final.extend(mod_code)

    # ── Mapa de memoria ──────────────────────────────────────────────────────
    mapa = {
        "total_size":    total_size,
        "n_instrucciones": len(code_final),
        "modulos":       [],
        "simbolos":      tabla_global,
    }
    for mod, base in layout:
        mapa["modulos"].append({
            "nombre": mod.nombre,
            "base":   base,
            "size":   mod.size,
        })

    print(f"\n  [OK] Enlace exitoso: {len(code_final)} instrucciones totales")
    return code_final, mapa


def _parchear_instruccion(bits, formato, valor):
    """
    Reemplaza el campo de dirección/offset dentro de una instrucción de 64 bits.

    Cada formato tiene el offset/inmediato en una posición diferente:
      F1: bits[32:64]  — inmediato de 32 bits
      F2: bits[32:64]  — offset de 32 bits
      F3: bits[28:60]  — offset de 32 bits
      F4: bits[16:48]  — inmediato de 32 bits
      F5: bits[32:64]  — inmediato de 32 bits
    """
    bits_list = list(bits)
    val_bin   = zfill_bin(valor, 32)

    if formato == 1:
        # F1: [pre(4)][opcode(10)][modo(6)][rd(4)][r1(4)][r2(4)][inm(32)]
        for i, b in enumerate(val_bin):
            bits_list[32 + i] = b
    elif formato == 2:
        # F2: [pre(4)][opcode(8)][modo(6)][r1(4)][base(4)][index(4)][scale(2)][offset(32)]
        for i, b in enumerate(val_bin):
            bits_list[32 + i] = b
    elif formato == 3:
        # F3: [pre(4)][opcode(10)][modo(6)][r1(4)][r2(4)][offset(32)][flags(4)]
        for i, b in enumerate(val_bin):
            bits_list[28 + i] = b
    elif formato == 4:
        # F4: [pre(4)][opcode(6)][modo(6)][inm32(32)][padding(16)]
        for i, b in enumerate(val_bin):
            bits_list[16 + i] = b
    elif formato == 5:
        # F5: igual que F1
        for i, b in enumerate(val_bin):
            bits_list[32 + i] = b
    else:
        return None

    return ''.join(bits_list)


# =============================================================================
# FASE 3 — CARGADOR: generar binario de salida
# =============================================================================

def generar_binario(code_final, output_path):
    """
    Escribe el binario final en formato compatible con main.py:
    un byte (8 bits) por línea, texto plano.

    Cada instrucción de 64 bits se divide en 8 bytes.
    """
    with open(output_path, 'w') as f:
        for i, bits in enumerate(code_final):
            assert len(bits) == 64, f"Instrucción {i} tiene {len(bits)} bits, esperados 64"
            for byte_idx in range(0, 64, 8):
                f.write(bits[byte_idx : byte_idx + 8] + '\n')

    total_bytes = len(code_final) * INSTR_SIZE
    print(f"\n  [OK] Binario guardado en '{output_path}'")
    print(f"    {len(code_final)} instrucciones -> {total_bytes} bytes")
    return total_bytes


def guardar_mapa(mapa, output_path):
    """Guarda el mapa de enlace en formato JSON para depuración."""
    # Convertir valores no serializables
    mapa_serializable = copy.deepcopy(mapa)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mapa_serializable, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Mapa de enlace guardado en '{output_path}'")


# =============================================================================
# DEMO LÉXICO DEL LINKER
# =============================================================================

def demo_lexico_linker(archivos):
    """
    Muestra los tokens reconocidos por el lexer extendido (con .global/.extern)
    para cada archivo proporcionado.
    """
    print("\n" + "="*62)
    print("   ANALISIS LEXICO -- LINKER (tokens con .global/.extern)")
    print("="*62)

    for filepath in archivos:
        print(f"\n  -- Archivo: {filepath} --")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
        except FileNotFoundError:
            print(f"    ERROR: no encontrado")
            continue

        base_dir = os.path.dirname(os.path.abspath(filepath))
        lineas = preprocesar(lineas, base_dir=base_dir)

        cat_width = 15
        for num, linea in enumerate(lineas, 1):
            s = linea.rstrip()
            if not s.strip():
                continue
            toks = tokenizar_linea_linker(s)
            if not toks:
                continue
            print(f"\n    Linea {num:3}: {s}")
            print(f"    {'-'*55}")
            print(f"    {'TIPO':<{cat_width}}  VALOR")
            print(f"    {'-'*cat_width}  {'-'*30}")
            for t in toks:
                print(f"    {t.type:<{cat_width}}  {repr(t.value)}")


# =============================================================================
# MODO ARCHIVO ÚNICO (retrocompatible con assembly_lex.py)
# =============================================================================

def ensamblar_y_enlazar_uno(filepath, output_path=None):
    """
    Para un solo archivo: ensambla + enlaza (el enlace es trivial, solo ajusta
    las direcciones) y genera el binario. Equivalente a assembly_lex.py pero
    pasando por el pipeline completo.
    """
    mod = ensamblar_modulo(filepath)
    if mod is None:
        return

    # Todos los símbolos de un solo módulo son accesibles
    for nombre in mod.symbols:
        if mod.symbols[nombre]["binding"] == SYM_LOCAL:
            mod.symbols[nombre]["binding"] = SYM_GLOBAL

    code_final, mapa = enlazar([mod])
    if code_final is None:
        return

    if output_path:
        generar_binario(code_final, output_path)


# =============================================================================
# MAIN — CLI del enlazador-cargador
# =============================================================================

def main():
    if len(sys.argv) < 2:
        print("+" + "="*62 + "+")
        print("|        ENLAZADOR-CARGADOR -- Maquina sy_00                  |")
        print("+" + "="*62 + "+")
        print()
        print("Uso:")
        print("  python linker_loader.py <arch1.asm> [arch2.asm ...] -o salida.bin")
        print()
        print("Opciones:")
        print("  -o <archivo>    Archivo binario de salida")
        print("  --lexico        Muestra tokens reconocidos (modo demo)")
        print("  --mapa          Genera archivo .map.json con info de enlace")
        print()
        print("Directivas del enlazador:")
        print("  .global NOMBRE  — Exporta un símbolo (visible para otros módulos)")
        print("  .extern NOMBRE  — Importa un símbolo definido en otro módulo")
        print()
        print("Pipeline completo:")
        print("  .asm -> [PREPROCESADOR] -> [LEXER PLY] -> [ENSAMBLADOR 2-pasadas]")
        print("       -> .obj (interno)  -> [ENLAZADOR]  -> [CARGADOR] -> .bin")
        print()
        print("Ejemplos:")
        print("  python linker_loader.py programa.asm -o programa.bin")
        print("  python linker_loader.py main.asm math.asm -o resultado.bin")
        print("  python linker_loader.py main.asm lib.asm --lexico --mapa -o out.bin")
        sys.exit(1)

    # ── Parsear argumentos ────────────────────────────────────────────────────
    archivos    = []
    output_file = None
    modo_lexico = False
    modo_mapa   = False

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '-o' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif arg == '--lexico':
            modo_lexico = True
            i += 1
        elif arg == '--mapa':
            modo_mapa = True
            i += 1
        else:
            archivos.append(arg)
            i += 1

    if not archivos:
        print("ERROR: debe proporcionar al menos un archivo .asm")
        sys.exit(1)

    # ── Demo léxico (opcional) ────────────────────────────────────────────────
    if modo_lexico:
        demo_lexico_linker(archivos)
        if not output_file:
            return

    # ── Ensamblar cada módulo ─────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  PIPELINE: {len(archivos)} archivo(s) -> enlazar -> binario")
    print(f"{'='*60}")

    modulos = []
    for filepath in archivos:
        mod = ensamblar_modulo(filepath)
        if mod is None:
            print(f"\n  ABORTANDO: error ensamblando '{filepath}'")
            sys.exit(1)
        modulos.append(mod)

    # Si solo hay un módulo, hacer todos los símbolos visibles
    if len(modulos) == 1:
        for nombre in modulos[0].symbols:
            if modulos[0].symbols[nombre]["binding"] == SYM_LOCAL:
                modulos[0].symbols[nombre]["binding"] = SYM_GLOBAL

    # ── Enlazar ───────────────────────────────────────────────────────────────
    code_final, mapa = enlazar(modulos)
    if code_final is None:
        print("\n  ABORTANDO: errores de enlace")
        sys.exit(1)

    # ── Generar binario ───────────────────────────────────────────────────────
    if output_file:
        generar_binario(code_final, output_file)
    else:
        # Sin archivo de salida: imprimir al stdout
        print("\n  Binario resultante (instrucciones):")
        for i, bits in enumerate(code_final):
            addr = i * INSTR_SIZE
            hex_word = hex(int(bits, 2))
            print(f"    0x{addr:04X}  {bits}  ({hex_word})")
        print(f"\n  (usa -o <archivo> para guardar el binario)")

    # ── Guardar mapa de enlace (opcional) ─────────────────────────────────────
    if modo_mapa and mapa:
        map_path = (output_file.rsplit('.', 1)[0] + '.map.json') if output_file else 'linker.map.json'
        guardar_mapa(mapa, map_path)

    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETADO EXITOSAMENTE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
