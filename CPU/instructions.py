import math

from .formats import _parse_fmt1, _parse_fmt2, _parse_fmt3, _parse_fmt4
from .futils.futils import _bits_to_float, _float_to_bits
from .utils.utils import _int_to_bin64

ADDR_MASK = (1 << 32) - 1


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
    # Usa update_flags para que flag_N se derive del bit de signo (MSB)
    # del resultado truncado a REG_BITS, no de Python int. Antes flag_N se
    # calculaba como (result < 0) sobre valores unsigned, lo que rompía
    # comparaciones con negativos (e.g., x < 0 era siempre falso).
    registros.update_flags(result, operand_a=vd, operand_b=v1, operation="sub")
    return False


def test(cpu, registros, ram):
    _, rd, r1, _, _ = _parse_fmt1(registros)
    vd, v1 = registros.get_reg(rd), registros.get_reg(r1)
    result = vd & v1
    registros.update_flags(result, operand_a=vd, operand_b=v1, operation="logic")
    return False


def out_(cpu, registros, ram):
    """out rd — muestra el valor del registro rd por el dispositivo de salida.
    Si el bit de signo (MSB) está puesto, se imprime como entero con signo de
    64 bits (two's complement); en otro caso, como entero sin signo.
    """
    _, rd, _, _, _ = _parse_fmt1(registros)
    val = registros.get_reg(rd)
    if val >> 63:
        val = val - (1 << 64)
    print(f"[OUT] R{rd} = {val}")
    return False


def outs(cpu, registros, ram):
    """outs rd — imprime la cadena ASCII almacenada en RAM a partir de la
    dirección contenida en rd, hasta encontrar un byte 0 (null terminator).
    """
    _, rd, _, _, _ = _parse_fmt1(registros)
    addr = registros.get_reg(rd) & ADDR_MASK
    chars = []
    # Cap defensivo para evitar bucles infinitos si la cadena no está
    # null-terminada (la región de strings se zero-rellena, así que esto
    # solo activa si el puntero está fuera del pool de strings).
    for _ in range(4096):
        byte_str = ram.read(addr)
        val = int(byte_str, 2)
        if val == 0:
            break
        chars.append(chr(val))
        addr += 1
    print(f"[OUT] \"{''.join(chars)}\"")
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
    addr = _f2_addr(registros, modo, base, index, scale, offset)
    byte_str = ram.read(addr)  # string '01001010'
    registros.set_reg(r1, int(byte_str, 2))
    return False


def store(cpu, registros, ram):
    """Almacena 1 byte del registro en la RAM."""
    modo, r1, base, index, scale, offset = _parse_fmt2(registros)
    addr = _f2_addr(registros, modo, base, index, scale, offset)
    val = registros.get_reg(r1) & 0xFF  # tomar solo los 8 bits bajos
    ram.write(addr, format(val, "08b"))  # '01001010'
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
    ram.write_block(addr, format(val & 0xFFFFFFFFFFFFFFFF, "064b"))
    return False


# ---------------------------------------------------------------------------
# F3 — Saltos
# ---------------------------------------------------------------------------


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
jzr = jz
jnzr = jnz
jcr = jc
jnr = jn


def call(cpu, registros, ram):
    """
    Llamada a subrutina:
      1. Guarda PC+8 en el stack (8 bytes; SP -= 8)
      2. Salta al destino
    CORRECCIÓN: guardaba PC (no PC+8) y usaba ram.write (1 byte).
    """
    modo, r1, r2, offset, _ = _parse_fmt3(registros)
    ret_addr = registros.PC + 8  # instrucción siguiente al call
    registros.SP -= 8
    ram.write_block(registros.SP, _int_to_bin64(ret_addr))
    registros.PC = _jump_target(registros, modo, r1, r2, offset)
    return True


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


def fmov(cpu, registros, ram):
    """
    fmov rd, <float_imm>
    Carga un inmediato flotante (ya codificado como bits IEEE 754) en rd.
    Modo 1 = inmediato (el campo inm32 ya contiene los bits IEEE 754).
    """
    modo, rd, r1, _, inm = _parse_fmt1(registros)
    if modo == 1:
        # inm contiene los bits IEEE 754; guardarlo directo en el registro
        registros.set_reg(rd, inm & 0xFFFFFFFF)
    else:
        # registro a registro
        registros.set_reg(rd, registros.get_reg(r1) & 0xFFFFFFFF)

    return False


def fadd(cpu, registros, ram):
    """fadd rd, r1  →  rd = float(rd) + float(r1)"""
    _, rd, r1, _, _ = _parse_fmt1(registros)
    a = _bits_to_float(registros.get_reg(rd))
    b = _bits_to_float(registros.get_reg(r1))
    result = a + b
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = result == 0.0
    registros.flag_N = result < 0.0
    registros.flag_C = False
    return False


def fsub(cpu, registros, ram):
    """fsub rd, r1  →  rd = float(rd) - float(r1)"""
    _, rd, r1, _, _ = _parse_fmt1(registros)
    a = _bits_to_float(registros.get_reg(rd))
    b = _bits_to_float(registros.get_reg(r1))
    result = a - b
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = result == 0.0
    registros.flag_N = result < 0.0
    registros.flag_C = False
    return False


def fmul(cpu, registros, ram):
    """fmul rd, r1  →  rd = float(rd) * float(r1)"""
    _, rd, r1, _, _ = _parse_fmt1(registros)
    a = _bits_to_float(registros.get_reg(rd))
    b = _bits_to_float(registros.get_reg(r1))
    result = a * b
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = result == 0.0
    registros.flag_N = result < 0.0
    registros.flag_C = False
    return False


def fdiv(cpu, registros, ram):
    """fdiv rd, r1  →  rd = float(rd) / float(r1)  (0.0/0.0 → NaN en IEEE 754)"""
    _, rd, r1, _, _ = _parse_fmt1(registros)
    a = _bits_to_float(registros.get_reg(rd))
    b = _bits_to_float(registros.get_reg(r1))
    if b == 0.0:
        result = float("nan")
    else:
        result = a / b
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = (result == 0.0) if not math.isnan(result) else False
    registros.flag_N = (result < 0.0) if not math.isnan(result) else False
    registros.flag_C = False
    return False


def fcmp(cpu, registros, ram):
    """fcmp rd, r1  →  actualiza flags según float(rd) - float(r1), no modifica registros"""
    _, rd, r1, _, _ = _parse_fmt1(registros)
    a = _bits_to_float(registros.get_reg(rd))
    b = _bits_to_float(registros.get_reg(r1))
    diff = a - b
    registros.flag_Z = diff == 0.0
    registros.flag_N = diff < 0.0
    registros.flag_C = False
    return False


def fabs(cpu, registros, ram):
    """fabs rd  →  rd = |float(rd)|"""
    _, rd, _, _, _ = _parse_fmt1(registros)
    a = _bits_to_float(registros.get_reg(rd))
    result = abs(a)
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = result == 0.0
    registros.flag_N = False
    return False


def fneg(cpu, registros, ram):
    """fneg rd  →  rd = -float(rd)"""
    _, rd, _, _, _ = _parse_fmt1(registros)
    a = _bits_to_float(registros.get_reg(rd))
    result = -a
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = result == 0.0
    registros.flag_N = result < 0.0
    return False


def fsqrt(cpu, registros, ram):
    """fsqrt rd  →  rd = sqrt(float(rd))  (negativo → NaN)"""
    _, rd, _, _, _ = _parse_fmt1(registros)
    a = _bits_to_float(registros.get_reg(rd))
    result = math.sqrt(a) if a >= 0.0 else float("nan")
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = (result == 0.0) if not math.isnan(result) else False
    registros.flag_N = False
    return False


def fi2f(cpu, registros, ram):
    """fi2f rd  →  interpreta rd como entero con signo de 32 bits y convierte a float IEEE 754"""
    _, rd, _, _, _ = _parse_fmt1(registros)
    raw = registros.get_reg(rd) & 0xFFFFFFFF
    # signo extendido de 32 bits
    signed = raw if raw < 0x80000000 else raw - 0x100000000
    result = float(signed)
    registros.set_reg(rd, _float_to_bits(result))
    registros.flag_Z = result == 0.0
    registros.flag_N = result < 0.0
    return False


def ff2i(cpu, registros, ram):
    """ff2i rd  →  convierte float IEEE 754 en rd a entero (truncado), guarda en rd"""
    _, rd, _, _, _ = _parse_fmt1(registros)
    a = _bits_to_float(registros.get_reg(rd))
    result = int(a) if not math.isnan(a) else 0
    registros.set_reg(rd, result & 0xFFFFFFFF)
    registros.flag_Z = result == 0
    registros.flag_N = result < 0
    return False


def fout(cpu, registros, ram):
    """fout rd — imprime el contenido de rd interpretado como float IEEE 754 de 64 bits."""
    _, rd, _, _, _ = _parse_fmt1(registros)
    val = _bits_to_float(registros.get_reg(rd))
    print(f"[OUT] R{rd} = {val}")
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
# Tablas de decodificación
# ---------------------------------------------------------------------------

_F1 = {
    0: mov,
    1: push,
    2: pop,
    3: xchg,
    4: add,
    5: addi,
    6: sub,
    7: subi,
    8: mul,
    9: muli,
    10: div,
    11: divi,
    12: inc,
    13: dec,
    14: neg,
    15: and_,
    16: or_,
    17: xor,
    18: not_,
    19: shl,
    20: shr,
    21: rol,
    22: ror,
    23: cmp,
    24: test,
    25: mod,
    26: modi,
    27: out_,
    28: outs,
}

_F2 = {0: load, 1: store, 2: lea, 3: loadw, 4: storew}

_F3 = {
    0: jmp,
    1: jz,
    2: jnz,
    3: jc,
    4: jn,
    5: jmpr,
    6: jzr,
    7: jnzr,
    8: jcr,
    9: jnr,
    10: call,
    11: jg,
    12: jge,
    13: jne,
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
    11: fout,
}

DECODE_TABLE = {
    "0000": (6, _F4),
    "0001": (10, _F1),
    "0010": (8, _F2),
    "0011": (10, _F3),
    "0100": (10, _F5),  # ← FPU
}


def decode(ir: str):
    pre = ir[0:4]
    opcode_bits, tabla = DECODE_TABLE[pre]
    opcode = int(ir[4 : 4 + opcode_bits], 2)
    return tabla[opcode]
