"""
instructions.py — Implementación de instrucciones (versión con FPU)
=====================================================================
Novedad FPU (F5):
  • Nuevo prefijo 0100, opcode de 10 bits
  • Layout F5: [ pre(4) ][ opcode(10) ][ modo(6) ][ rd(4) ][ r1(4) ][ r2(4) ][ inm_bits(32) ]
  • Los registros generales almacenan el patrón de bits IEEE 754 de 32 bits
  • Instrucciones: fmov, fadd, fsub, fmul, fdiv, fcmp, fabs, fneg, fsqrt, fi2f, ff2i
  • fmov rd, <float>  — carga un inmediato flotante en rd  (IEEE 754 bits → registro)
  • fadd rd, r1       — rd = float(rd) + float(r1)
  • fsub rd, r1       — rd = float(rd) - float(r1)
  • fmul rd, r1       — rd = float(rd) * float(r1)
  • fdiv rd, r1       — rd = float(rd) / float(r1)  (divisor=0.0 → NaN)
  • fcmp rd, r1       — actualiza flags Z/N según float(rd) - float(r1)
  • fabs rd           — rd = |float(rd)|
  • fneg rd           — rd = -float(rd)
  • fsqrt rd          — rd = sqrt(float(rd))
  • fi2f rd           — convierte entero en rd a float IEEE 754
  • ff2i rd           — convierte float en rd a entero truncado
Cambios respecto a la versión original:
  • store : convierte int→string de 8 bits antes de escribir en RAM
  • push  : usa write_block de 8 bytes; SP -= 8
  • pop   : usa read_block de 8 bytes; SP += 8
  • call  : guarda PC+8 (dirección de retorno real) en 8 bytes del stack
  • ret   : restaura PC desde 8 bytes del stack  (NUEVO — F4 opcode 3)
  • iret  : idéntico a ret para interrupciones    (NUEVO — F4 opcode 4)
  • inti  : corregido (guarda PC+8 en stack como string binario)

Layouts de instrucción (todos 64 bits):

F1  [ pre(4) ][ opcode(10) ][ modo(6) ][ rd(4) ][ r1(4) ][ r2(4) ][ inm(32) ]
F2  [ pre(4) ][ opcode(8)  ][ modo(6) ][ r1(4) ][ base(4) ][ index(4) ][ scale(2) ][ offset(32) ]
F3  [ pre(4) ][ opcode(10) ][ modo(6) ][ r1(4) ][ r2(4) ][ offset(32) ][ flags(4) ]
F4  [ pre(4) ][ opcode(6)  ][ modo(6) ][ inm32(32) ][ padding(16) ]
"""

import math
import struct

ADDR_MASK = (1 << 32) - 1


def _parse_fmt1(registros):
    ir   = registros.IR
    modo = int(ir[14:20], 2)
    rd   = int(ir[20:24], 2)
    r1   = int(ir[24:28], 2)
    r2   = int(ir[28:32], 2)
    inm  = int(ir[32:64], 2)
    return modo, rd, r1, r2, inm


def _parse_fmt2(registros):
    ir     = registros.IR
    modo   = int(ir[12:18], 2)
    r1     = int(ir[18:22], 2)
    base   = int(ir[22:26], 2)
    index  = int(ir[26:30], 2)
    scale  = int(ir[30:32], 2)
    offset = int(ir[32:64], 2)
    return modo, r1, base, index, scale, offset


def _parse_fmt3(registros):
    ir     = registros.IR
    modo   = int(ir[14:20], 2)
    r1     = int(ir[20:24], 2)
    r2     = int(ir[24:28], 2)
    offset = int(ir[28:60], 2)
    flags  = int(ir[60:64], 2)
    return modo, r1, r2, offset, flags


def _parse_fmt4(registros):
    ir    = registros.IR
    modo  = int(ir[10:16], 2)
    inm32 = int(ir[16:48], 2)
    return modo, inm32


def _int_to_bin64(value: int) -> str:
    """Entero → cadena binaria de 64 bits (complemento a 2)."""
    return format(value & 0xFFFFFFFFFFFFFFFF, '064b')


def _jump_target(registros, modo, r1, r2, offset):
    if modo == 0:
        return offset & ADDR_MASK
    elif modo == 1:
        return (registros.PC + offset) & ADDR_MASK
    elif modo == 2:
        return registros.get_reg(r1) & ADDR_MASK
    elif modo == 3:
        return (registros.PC + offset) & ADDR_MASK
    elif modo == 4:
        return (registros.get_reg(r1) + registros.get_reg(r2)) & ADDR_MASK
    return offset & ADDR_MASK


# ---------------------------------------------------------------------------
# F4 — Control
# ---------------------------------------------------------------------------

def nop(cpu, registros, ram):
    return False














# ---------------------------------------------------------------------------
# F5 — Unidad de Punto Flotante (FPU)
# ---------------------------------------------------------------------------
# Los registros generales guardan el patrón de 32 bits IEEE 754.
# Se usan los 32 bits bajos del registro (compatible con REG_MASK de 64 bits).

def _bits_to_float(bits32: int) -> float:
    """Convierte un entero de 32 bits (patrón IEEE 754) a float Python."""
    bits32 = bits32 & 0xFFFFFFFF
    return struct.unpack('>f', bits32.to_bytes(4, 'big'))[0]


def _float_to_bits(f: float) -> int:
    """Convierte un float Python a su patrón de bits IEEE 754 de 32 bits."""
    return struct.unpack('>I', struct.pack('>f', f))[0]


def _parse_fmt5(registros):
    """
    F5 comparte el mismo layout que F1:
    [ pre(4) ][ opcode(10) ][ modo(6) ][ rd(4) ][ r1(4) ][ r2(4) ][ inm(32) ]
    """
    ir    = registros.IR
    modo  = int(ir[14:20], 2)
    rd    = int(ir[20:24], 2)
    r1    = int(ir[24:28], 2)
    r2    = int(ir[28:32], 2)
    inm   = int(ir[32:64], 2)
    return modo, rd, r1, r2, inm


def fmov(cpu, registros, ram):


    """
    fmov rd, <float_imm>
    Carga un inmediato flotante (ya codificado como bits IEEE 754) en rd.
    Modo 1 = inmediato (el campo inm32 ya contiene los bits IEEE 754).
    """
    modo, rd, r1, _, inm = _parse_fmt5(registros)
    if modo == 1:
        # inm contiene los bits IEEE 754; guardarlo directo en el registro
        registros.set_reg(rd, inm & 0xFFFFFFFF)
    else:
        # registro a registro
        registros.set_reg(rd, registros.get_reg(r1) & 0xFFFFFFFF)

    return False




def fadd(cpu, registros, ram):
    """fadd rd, r1  →  rd = float(rd) + float(r1)"""
    _, rd, r1, _, _ = _parse_fmt5(registros)
    a = _bits_to_float(registros.get_reg(rd))
    b = _bits_to_float(registros.get_reg(r1))
    result = a + b
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = (result == 0.0)
    registros.flag_N = (result < 0.0)
    registros.flag_C = False
    return False


def fsub(cpu, registros, ram):
    """fsub rd, r1  →  rd = float(rd) - float(r1)"""
    _, rd, r1, _, _ = _parse_fmt5(registros)
    a = _bits_to_float(registros.get_reg(rd))
    b = _bits_to_float(registros.get_reg(r1))
    result = a - b
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = (result == 0.0)
    registros.flag_N = (result < 0.0)
    registros.flag_C = False
    return False


def fmul(cpu, registros, ram):
    """fmul rd, r1  →  rd = float(rd) * float(r1)"""
    _, rd, r1, _, _ = _parse_fmt5(registros)
    a = _bits_to_float(registros.get_reg(rd))
    b = _bits_to_float(registros.get_reg(r1))
    result = a * b
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = (result == 0.0)
    registros.flag_N = (result < 0.0)
    registros.flag_C = False
    return False


def fdiv(cpu, registros, ram):
    """fdiv rd, r1  →  rd = float(rd) / float(r1)  (0.0/0.0 → NaN en IEEE 754)"""
    _, rd, r1, _, _ = _parse_fmt5(registros)
    a = _bits_to_float(registros.get_reg(rd))
    b = _bits_to_float(registros.get_reg(r1))
    if b == 0.0:
        result = float('nan')
    else:
        result = a / b
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = (result == 0.0) if not math.isnan(result) else False
    registros.flag_N = (result < 0.0)  if not math.isnan(result) else False
    registros.flag_C = False
    return False


def fcmp(cpu, registros, ram):
    """fcmp rd, r1  →  actualiza flags según float(rd) - float(r1), no modifica registros"""
    _, rd, r1, _, _ = _parse_fmt5(registros)
    a = _bits_to_float(registros.get_reg(rd))
    b = _bits_to_float(registros.get_reg(r1))
    diff = a - b
    registros.flag_Z = (diff == 0.0)
    registros.flag_N = (diff < 0.0)
    registros.flag_C = False
    return False


def fabs(cpu, registros, ram):
    """fabs rd  →  rd = |float(rd)|"""
    _, rd, _, _, _ = _parse_fmt5(registros)
    a = _bits_to_float(registros.get_reg(rd))
    result = abs(a)
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = (result == 0.0)
    registros.flag_N = False
    return False


def fneg(cpu, registros, ram):
    """fneg rd  →  rd = -float(rd)"""
    _, rd, _, _, _ = _parse_fmt5(registros)
    a = _bits_to_float(registros.get_reg(rd))
    result = -a
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = (result == 0.0)
    registros.flag_N = (result < 0.0)
    return False


def fsqrt(cpu, registros, ram):
    """fsqrt rd  →  rd = sqrt(float(rd))  (negativo → NaN)"""
    _, rd, _, _, _ = _parse_fmt5(registros)
    a = _bits_to_float(registros.get_reg(rd))
    result = math.sqrt(a) if a >= 0.0 else float('nan')
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = (result == 0.0) if not math.isnan(result) else False
    registros.flag_N = False
    return False


def fi2f(cpu, registros, ram):
    """fi2f rd  →  interpreta rd como entero con signo de 32 bits y convierte a float IEEE 754"""
    _, rd, _, _, _ = _parse_fmt5(registros)
    raw = registros.get_reg(rd) & 0xFFFFFFFF
    # signo extendido de 32 bits
    signed = raw if raw < 0x80000000 else raw - 0x100000000
    result = float(signed)
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = (result == 0.0)
    registros.flag_N = (result < 0.0)
    return False


def ff2i(cpu, registros, ram):
    """ff2i rd  →  convierte float IEEE 754 en rd a entero (truncado), guarda en rd"""
    _, rd, _, _, _ = _parse_fmt5(registros)
    a = _bits_to_float(registros.get_reg(rd))
    result = int(a) if not math.isnan(a) else 0
    registros.set_reg(rd, result & 0xFFFFFFFF)
    registros.flag_Z = (result == 0)
    registros.flag_N = (result < 0)
    return False





def halt(cpu, registros, ram):
    print(_bits_to_float(registros.get_reg(14)))
    cpu.running = False
    return False


def inti(cpu, registros, ram):
    _, inm32 = _parse_fmt4(registros)
    ret_addr = registros.PC + 8
    registros.SP -= 8
    ram.write_block(registros.SP, _int_to_bin64(ret_addr))
    registros.PC = cpu.interrupt_table.get(inm32, registros.PC)
    return True


def ret(cpu, registros, ram):
    """
    Retorna de subrutina: lee 8 bytes del stack → PC; SP += 8.
    NUEVO — F4 opcode 3.
    """
    data = ram.read_block(registros.SP, 8)
    registros.SP += 8
    registros.PC = int(data, 2) & ADDR_MASK
    return True


def iret(cpu, registros, ram):
    """Retorno de interrupción (igual a ret). NUEVO — F4 opcode 4."""
    return ret(cpu, registros, ram)


# ---------------------------------------------------------------------------
# F1 — Registro / Inmediato
# ---------------------------------------------------------------------------

def mov(cpu, registros, ram):
    modo, rd, r1, r2, inm = _parse_fmt1(registros)
    if modo == 1:
        registros.set_reg(rd, inm)
    else:
        registros.set_reg(rd, registros.get_reg(r1))
    return False


def push(cpu, registros, ram):
    """Apila 8 bytes (valor de 64 bits); SP -= 8. CORRECCIÓN: usaba 1 byte."""
    _, rd, _, _, _ = _parse_fmt1(registros)
    val = registros.get_reg(rd)
    registros.SP -= 8
    ram.write_block(registros.SP, _int_to_bin64(val))
    return False


def pop(cpu, registros, ram):
    """Desapila 8 bytes del stack al registro; SP += 8. CORRECCIÓN: usaba 1 byte."""
    _, rd, _, _, _ = _parse_fmt1(registros)
    data = ram.read_block(registros.SP, 8)
    registros.SP += 8
    registros.set_reg(rd, int(data, 2))
    return False


def xchg(cpu, registros, ram):
    _, rd, r1, _, _ = _parse_fmt1(registros)
    vd, v1 = registros.get_reg(rd), registros.get_reg(r1)
    registros.set_reg(rd, v1)
    registros.set_reg(r1, vd)
    return False


def add(cpu, registros, ram):
    _, rd, r1, _, _ = _parse_fmt1(registros)
    vd, v1 = registros.get_reg(rd), registros.get_reg(r1)
    result = vd + v1
    registros.update_flags(result, operand_a=vd, operand_b=v1, operation="add")
    registros.set_reg(rd, result)
    return False


def addi(cpu, registros, ram):
    _, rd, _, _, inm = _parse_fmt1(registros)
    vd = registros.get_reg(rd)
    result = vd + inm
    registros.update_flags(result, operand_a=vd, operand_b=inm, operation="add")
    registros.set_reg(rd, result)
    return False


def sub(cpu, registros, ram):
    _, rd, r1, _, _ = _parse_fmt1(registros)
    vd, v1 = registros.get_reg(rd), registros.get_reg(r1)
    result = vd - v1
    registros.update_flags(result, operand_a=vd, operand_b=v1, operation="sub")
    registros.set_reg(rd, result)
    return False


def subi(cpu, registros, ram):
    _, rd, _, _, inm = _parse_fmt1(registros)
    vd = registros.get_reg(rd)
    result = vd - inm
    registros.update_flags(result, operand_a=vd, operand_b=inm, operation="sub")
    registros.set_reg(rd, result)
    return False


def mul(cpu, registros, ram):
    _, rd, r1, _, _ = _parse_fmt1(registros)
    vd, v1 = registros.get_reg(rd), registros.get_reg(r1)
    result = vd * v1
    registros.update_flags(result, operand_a=vd, operand_b=v1, operation="mul")
    registros.set_reg(rd, result)
    return False


def muli(cpu, registros, ram):
    _, rd, _, _, inm = _parse_fmt1(registros)
    vd = registros.get_reg(rd)
    result = vd * inm
    registros.update_flags(result, operand_a=vd, operand_b=inm, operation="mul")
    registros.set_reg(rd, result)
    return False


def div(cpu, registros, ram):
    _, rd, r1, _, _ = _parse_fmt1(registros)
    vd, v1 = registros.get_reg(rd), registros.get_reg(r1)
    if v1 == 0:
        return False
    result = vd // v1
    registros.update_flags(result, operand_a=vd, operand_b=v1, operation="div")
    registros.set_reg(rd, result)
    return False


def divi(cpu, registros, ram):
    _, rd, _, _, inm = _parse_fmt1(registros)
    if inm == 0:
        return False
    vd = registros.get_reg(rd)
    result = vd // inm
    registros.update_flags(result, operand_a=vd, operand_b=inm, operation="div")
    registros.set_reg(rd, result)
    return False

def mod(cpu, registros, ram):
    """mod rd, r1  →  rd = rd % r1  (módulo entero, divisor=0 → no-op)"""
    _, rd, r1, _, _ = _parse_fmt1(registros)
    vd, v1 = registros.get_reg(rd), registros.get_reg(r1)
    if v1 == 0:
        return False
    result = vd % v1
    registros.update_flags(result, operand_a=vd, operand_b=v1, operation="div")
    registros.set_reg(rd, result)
    return False


def modi(cpu, registros, ram):
    """modi rd, inm  →  rd = rd % inm  (módulo con inmediato, divisor=0 → no-op)"""
    _, rd, _, _, inm = _parse_fmt1(registros)
    if inm == 0:
        return False
    vd = registros.get_reg(rd)
    result = vd % inm
    registros.update_flags(result, operand_a=vd, operand_b=inm, operation="div")
    registros.set_reg(rd, result)
    return False

def inc(cpu, registros, ram):
    _, rd, _, _, _ = _parse_fmt1(registros)
    vd = registros.get_reg(rd)
    result = vd + 1
    registros.update_flags(result, operand_a=vd, operand_b=1, operation="add")
    registros.set_reg(rd, result)
    return False


def dec(cpu, registros, ram):
    _, rd, _, _, _ = _parse_fmt1(registros)
    vd = registros.get_reg(rd)
    result = vd - 1
    registros.update_flags(result, operand_a=vd, operand_b=1, operation="sub")
    registros.set_reg(rd, result)
    return False


def neg(cpu, registros, ram):
    _, rd, _, _, _ = _parse_fmt1(registros)
    vd = registros.get_reg(rd)
    result = -vd
    registros.update_flags(result, operand_a=0, operand_b=vd, operation="sub")
    registros.set_reg(rd, result)
    return False


def and_(cpu, registros, ram):
    _, rd, r1, _, _ = _parse_fmt1(registros)
    vd, v1 = registros.get_reg(rd), registros.get_reg(r1)
    result = vd & v1
    registros.update_flags(result, operand_a=vd, operand_b=v1, operation="logic")
    registros.set_reg(rd, result)
    return False


def or_(cpu, registros, ram):
    _, rd, r1, _, _ = _parse_fmt1(registros)
    vd, v1 = registros.get_reg(rd), registros.get_reg(r1)
    result = vd | v1
    registros.update_flags(result, operand_a=vd, operand_b=v1, operation="logic")
    registros.set_reg(rd, result)
    return False


def xor(cpu, registros, ram):
    _, rd, r1, _, _ = _parse_fmt1(registros)
    vd, v1 = registros.get_reg(rd), registros.get_reg(r1)
    result = vd ^ v1
    registros.update_flags(result, operand_a=vd, operand_b=v1, operation="logic")
    registros.set_reg(rd, result)
    return False


def not_(cpu, registros, ram):
    _, rd, _, _, _ = _parse_fmt1(registros)
    vd = registros.get_reg(rd)
    result = (~vd) & 0xFFFFFFFF
    registros.update_flags(result, operand_a=vd, operand_b=0, operation="logic")
    registros.set_reg(rd, result)
    return False


def shl(cpu, registros, ram):
    _, rd, _, _, _ = _parse_fmt1(registros)
    vd = registros.get_reg(rd)
    result = (vd << 1) & 0xFFFFFFFF
    registros.update_flags(result, operand_a=vd, operand_b=0, operation="logic")
    registros.set_reg(rd, result)
    return False


def shr(cpu, registros, ram):
    _, rd, _, _, _ = _parse_fmt1(registros)
    vd = registros.get_reg(rd)
    result = vd >> 1
    registros.update_flags(result, operand_a=vd, operand_b=0, operation="logic")
    registros.set_reg(rd, result)
    return False


def rol(cpu, registros, ram):
    _, rd, _, _, _ = _parse_fmt1(registros)
    vd = registros.get_reg(rd)
    result = ((vd << 1) | (vd >> 31)) & 0xFFFFFFFF
    registros.update_flags(result, operand_a=vd, operand_b=0, operation="logic")
    registros.set_reg(rd, result)
    return False


def ror(cpu, registros, ram):
    _, rd, _, _, _ = _parse_fmt1(registros)
    vd = registros.get_reg(rd)
    result = ((vd >> 1) | (vd << 31)) & 0xFFFFFFFF
    registros.update_flags(result, operand_a=vd, operand_b=0, operation="logic")
    registros.set_reg(rd, result)
    return False


def cmp(cpu, registros, ram):
    _, rd, r1, _, _ = _parse_fmt1(registros)
    vd, v1 = registros.get_reg(rd), registros.get_reg(r1)
    result = vd - v1
    registros.flag_Z = (result == 0)
    registros.flag_N = (result < 0)
    registros.flag_C = (vd < v1)
    return False


def test(cpu, registros, ram):
    _, rd, r1, _, _ = _parse_fmt1(registros)
    vd, v1 = registros.get_reg(rd), registros.get_reg(r1)
    result = vd & v1
    registros.update_flags(result, operand_a=vd, operand_b=v1, operation="logic")
    return False


def out_(cpu, registros, ram):
    """out rd — muestra el valor del registro rd por el dispositivo de salida."""
    _, rd, _, _, _ = _parse_fmt1(registros)
    val = registros.get_reg(rd)
    print(f"[OUT] R{rd} = {val}")
    return False


# ---------------------------------------------------------------------------
# F2 — Memoria
# ---------------------------------------------------------------------------

def _f2_addr(registros, modo, base, index, scale, offset):
    """Calcula dirección efectiva según el modo de direccionamiento F2.
    modo=0: completo   addr = R[base] + R[index]*scale + offset
    modo=1: absoluto   addr = offset
    modo=2: base+off   addr = R[base] + offset
    """
    if modo == 1:
        return offset
    elif modo == 2:
        return registros.get_reg(base) + offset
    else:
        return registros.get_reg(base) + registros.get_reg(index) * scale + offset


def load(cpu, registros, ram):
    """Carga 1 byte de la RAM al registro (bits[7:0])."""
    modo, r1, base, index, scale, offset = _parse_fmt2(registros)
    addr     = _f2_addr(registros, modo, base, index, scale, offset)
    byte_str = ram.read(addr)           # string '01001010'
    registros.set_reg(r1, int(byte_str, 2))
    return False


def store(cpu, registros, ram):
    """Almacena 1 byte del registro en la RAM."""
    modo, r1, base, index, scale, offset = _parse_fmt2(registros)
    addr = _f2_addr(registros, modo, base, index, scale, offset)
    val  = registros.get_reg(r1) & 0xFF        # tomar solo los 8 bits bajos
    ram.write(addr, format(val, '08b'))         # '01001010'
    return False


def lea(cpu, registros, ram):
    """Load Effective Address: r1 = dirección efectiva calculada."""
    modo, r1, base, index, scale, offset = _parse_fmt2(registros)
    addr = _f2_addr(registros, modo, base, index, scale, offset)
    registros.set_reg(r1, addr)
    return False


def loadw(cpu, registros, ram):
    """Carga 8 bytes (64 bits / 1 palabra) de la RAM al registro."""
    modo, r1, base, index, scale, offset = _parse_fmt2(registros)
    addr = _f2_addr(registros, modo, base, index, scale, offset)
    data = ram.read_block(addr, 8)
    registros.set_reg(r1, int(data, 2))
    return False


def storew(cpu, registros, ram):
    """Almacena 8 bytes (64 bits / 1 palabra) del registro en la RAM."""
    modo, r1, base, index, scale, offset = _parse_fmt2(registros)
    addr = _f2_addr(registros, modo, base, index, scale, offset)
    val = registros.get_reg(r1)
    ram.write_block(addr, format(val & 0xFFFFFFFFFFFFFFFF, '064b'))
    return False


# ---------------------------------------------------------------------------
# F3 — Saltos
# ---------------------------------------------------------------------------

def jmp(cpu, registros, ram):
    modo, r1, r2, offset, _ = _parse_fmt3(registros)
    registros.PC = _jump_target(registros, modo, r1, r2, offset)
    return True


def jz(cpu, registros, ram):
    if registros.flag_Z:
        modo, r1, r2, offset, _ = _parse_fmt3(registros)
        registros.PC = _jump_target(registros, modo, r1, r2, offset)
        return True
    return False


def jnz(cpu, registros, ram):
    if registros.flag_N or registros.flag_Z:
        modo, r1, r2, offset, _ = _parse_fmt3(registros)
        registros.PC = _jump_target(registros, modo, r1, r2, offset)
        return True
    return False


def jc(cpu, registros, ram):
    if registros.flag_C:
        modo, r1, r2, offset, _ = _parse_fmt3(registros)
        registros.PC = _jump_target(registros, modo, r1, r2, offset)
        return True
    return False


def jn(cpu, registros, ram):
    if registros.flag_N:
        modo, r1, r2, offset, _ = _parse_fmt3(registros)
        registros.PC = _jump_target(registros, modo, r1, r2, offset)
        return True
    return False

def jg(cpu, registros, ram):
    if not registros.flag_Z and not registros.flag_N:
        modo, r1, r2, offset, _ = _parse_fmt3(registros)
        registros.PC = _jump_target(registros, modo, r1, r2, offset)
        return True
    return False


def jne(cpu, registros, ram):
    if not registros.flag_Z:
        modo, r1, r2, offset, _ = _parse_fmt3(registros)
        registros.PC = _jump_target(registros, modo, r1, r2, offset)
        return True
    return False

def jge(cpu, registros, ram):
    if not registros.flag_N:
        modo, r1, r2, offset, _ = _parse_fmt3(registros)
        registros.PC = _jump_target(registros, modo, r1, r2, offset)
        return True
    return False



jmpr = jmp
jzr  = jz
jnzr = jnz
jcr  = jc
jnr  = jn


def call(cpu, registros, ram):
    """
    Llamada a subrutina:
      1. Guarda PC+8 en el stack (8 bytes; SP -= 8)
      2. Salta al destino
    CORRECCIÓN: guardaba PC (no PC+8) y usaba ram.write (1 byte).
    """
    modo, r1, r2, offset, _ = _parse_fmt3(registros)
    ret_addr = registros.PC + 8             # instrucción siguiente al call
    registros.SP -= 8
    ram.write_block(registros.SP, _int_to_bin64(ret_addr))
    registros.PC = _jump_target(registros, modo, r1, r2, offset)
    return True


# ---------------------------------------------------------------------------
# Tablas de decodificación
# ---------------------------------------------------------------------------

_F1 = {
    0: mov,  1: push,  2: pop,   3: xchg,  4: add,
    5: addi, 6: sub,   7: subi,  8: mul,   9: muli,
    10: div, 11: divi, 12: inc,  13: dec,  14: neg,
    15: and_,16: or_,  17: xor,  18: not_, 19: shl,
    20: shr, 21: rol,  22: ror,  23: cmp,  24: test,
    25: mod, 26: modi, 27: out_,
}

_F2 = {0: load, 1: store, 2: lea, 3: loadw, 4: storew}

_F3 = {
    0: jmp,  1: jz,   2: jnz,  3: jc,   4: jn,
    5: jmpr, 6: jzr,  7: jnzr, 8: jcr,  9: jnr,
    10: call, 11:jg, 12: jge, 13: jne
}

_F4 = {
    0: nop,
    1: halt,
    2: inti,
    3: ret,
    4: iret,
}




_F5 = {
    0: fmov,
    1: fadd,
    2: fsub,
    3: fmul,
    4: fdiv,
    5: fcmp,
    6: fabs,
    7: fneg,
    8: fsqrt,
    9: fi2f,
    10: ff2i,
}

DECODE_TABLE = {
    "0000": (6,  _F4),
    "0001": (10, _F1),
    "0010": (8,  _F2),
    "0011": (10, _F3),
    "0100": (10, _F5),   # ← FPU
}


def decode(ir: str):
    pre              = ir[0:4]
    opcode_bits, tabla = DECODE_TABLE[pre]
    opcode           = int(ir[4: 4 + opcode_bits], 2)
    return tabla[opcode]


def params_format_1(ir: str):
    return (ir[0:4], ir[4:14], ir[14:20], ir[20:24], ir[24:28], ir[28:32], ir[32:64])
