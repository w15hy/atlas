"""
instructions.py — Implementación de instrucciones (versión corregida)
=====================================================================
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


def halt(cpu, registros, ram):
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


# ---------------------------------------------------------------------------
# F2 — Memoria
# ---------------------------------------------------------------------------

def load(cpu, registros, ram):
    """Carga 1 byte de la RAM al registro (bits[7:0])."""
    _, r1, base, index, scale, offset = _parse_fmt2(registros)
    addr     = registros.get_reg(base) + registros.get_reg(index) * scale + offset
    byte_str = ram.read(addr)           # string '01001010'
    registros.set_reg(r1, int(byte_str, 2))
    return False


def store(cpu, registros, ram):
    """
    Almacena 1 byte del registro en la RAM.
    CORRECCIÓN: el original pasaba un int a ram.write(), que requiere
    string binario de exactamente 8 bits.
    """
    _, r1, base, index, scale, offset = _parse_fmt2(registros)
    addr = registros.get_reg(base) + registros.get_reg(index) * scale + offset
    val  = registros.get_reg(r1) & 0xFF        # tomar solo los 8 bits bajos
    ram.write(addr, format(val, '08b'))         # '01001010'
    return False


def lea(cpu, registros, ram):
    """Load Effective Address: r1 = base + index*scale + offset."""
    _, r1, base, index, scale, offset = _parse_fmt2(registros)
    addr = registros.get_reg(base) + registros.get_reg(index) * scale + offset
    registros.set_reg(r1, addr)
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
    if not registros.flag_Z:
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
}

_F2 = {0: load, 1: store, 2: lea}

_F3 = {
    0: jmp,  1: jz,   2: jnz,  3: jc,   4: jn,
    5: jmpr, 6: jzr,  7: jnzr, 8: jcr,  9: jnr,
    10: call,
}

_F4 = {
    0: nop,
    1: halt,
    2: inti,
    3: ret,    # ← NUEVO
    4: iret,   # ← NUEVO
}

DECODE_TABLE = {
    "0000": (6,  _F4),
    "0001": (10, _F1),
    "0010": (8,  _F2),
    "0011": (10, _F3),
}


def decode(ir: str):
    pre              = ir[0:4]
    opcode_bits, tabla = DECODE_TABLE[pre]
    opcode           = int(ir[4: 4 + opcode_bits], 2)
    return tabla[opcode]


def params_format_1(ir: str):
    return (ir[0:4], ir[4:14], ir[14:20], ir[20:24], ir[24:28], ir[28:32], ir[32:64])
