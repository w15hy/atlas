"""
Layouts de instrucción (todos 64 bits):

F1  [ pre(4) ][ opcode(10) ][ modo(6) ][ rd(4) ][ r1(4) ][ r2(4) ][ inm(32) ]
     0        4             14         20        24        28        32        64

F2  [ pre(4) ][ opcode(8)  ][ modo(6) ][ r1(4) ][ base(4) ][ index(4) ][ scale(2) ][ offset(32) ]
     0        4             12         18        22          26           30           32           64

F3  [ pre(4) ][ opcode(10) ][ modo(6) ][ r1(4) ][ r2(4) ][ offset(32) ][ flags(4) ]
     0        4             14         20        24        28             60          64

F4  [ pre(4) ][ opcode(6)  ][ modo(6) ][ inm32(32) ][ padding(16) ]
     0        4             10         16             48             64
"""


# ---------------------------------------------------------------------------
# Helpers de parseo
# ---------------------------------------------------------------------------

def _parse_fmt1(registros):
    """
    F1: [ pre(4) ][ opcode(10) ][ modo(6) ][ rd(4) ][ r1(4) ][ r2(4) ][ inm(32) ]
    Retorna (modo, rd, r1, r2, inm)
    """
    ir   = registros.IR
    modo = int(ir[14:20], 2)
    rd   = int(ir[20:24], 2)
    r1   = int(ir[24:28], 2)
    r2   = int(ir[28:32], 2)
    inm  = int(ir[32:64], 2)
    return modo, rd, r1, r2, inm


def _parse_fmt2(registros):
    """
    F2: [ pre(4) ][ opcode(8) ][ modo(6) ][ r1(4) ][ base(4) ][ index(4) ][ scale(2) ][ offset(32) ]
    Retorna (modo, r1, base, index, scale, offset)
    """
    ir     = registros.IR
    modo   = int(ir[12:18], 2)
    r1     = int(ir[18:22], 2)
    base   = int(ir[22:26], 2)
    index  = int(ir[26:30], 2)
    scale  = int(ir[30:32], 2)
    offset = int(ir[32:64], 2)
    return modo, r1, base, index, scale, offset


def _parse_fmt3(registros):
    """
    F3: [ pre(4) ][ opcode(10) ][ modo(6) ][ r1(4) ][ r2(4) ][ offset(32) ][ flags(4) ]
    Retorna (modo, r1, r2, offset, flags)
    """
    ir     = registros.IR
    modo   = int(ir[14:20], 2)
    r1     = int(ir[20:24], 2)
    r2     = int(ir[24:28], 2)
    offset = int(ir[28:60], 2)
    flags  = int(ir[60:64], 2)
    return modo, r1, r2, offset, flags


def _parse_fmt4(registros):
    """
    F4: [ pre(4) ][ opcode(6) ][ modo(6) ][ inm32(32) ][ padding(16) ]
    Retorna (modo, inm32)
    """
    ir    = registros.IR
    modo  = int(ir[10:16], 2)
    inm32 = int(ir[16:48], 2)
    return modo, inm32


# ---------------------------------------------------------------------------
# Cálculo de dirección de salto (F3)
# ---------------------------------------------------------------------------

def _jump_target(registros, modo, r1, r2, offset):
    """
    modo 0 → absoluto   (offset es la dirección)
    modo 1 → relativo   (PC + offset con signo)
    modo 2 → por registro r1
    modo 3 → branch     (PC + offset, igual que relativo por ahora)
    modo 4 → branch con dos registros (r1 + r2)
    """
    if modo == 0:
        return offset
    elif modo == 1:
        return registros.PC + offset
    elif modo == 2:
        return registros.get_reg(r1)
    elif modo == 3:
        return registros.PC + offset
    elif modo == 4:
        return registros.get_reg(r1) + registros.get_reg(r2)
    return offset


# ---------------------------------------------------------------------------
# Instrucciones F4 — control
# ---------------------------------------------------------------------------

def nop(cpu, registros, ram):
    pass


def halt(cpu, registros, ram):
    cpu.running = False


def inti(cpu, registros, ram):
    _, inm32 = _parse_fmt4(registros)
    registros.SP -= 1
    ram.write(registros.SP, registros.PC)
    registros.PC = cpu.interrupt_table[inm32]
    return True


# ---------------------------------------------------------------------------
# Instrucciones F1 — registro / inmediato
# ---------------------------------------------------------------------------

def mov(cpu, registros, ram):
    modo, rd, r1, r2, inm = _parse_fmt1(registros)
    if modo == 1:                              # registro - inmediato
        registros.set_reg(rd, inm)
    else:                                      # registro - registro (modo 2)
        registros.set_reg(rd, registros.get_reg(r1))
    return False


def push(cpu, registros, ram):
    _, rd, _, _, _ = _parse_fmt1(registros)
    val = registros.get_reg(rd)
    registros.SP -= 1
    ram.write(registros.SP, val)
    return False


def pop(cpu, registros, ram):
    _, rd, _, _, _ = _parse_fmt1(registros)
    val = ram.read(registros.SP)
    registros.SP += 1
    registros.set_reg(rd, val)
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
    registros.flag_Z = result == 0
    registros.flag_N = result < 0
    registros.flag_C = vd < v1
    return False


def test(cpu, registros, ram):
    _, rd, r1, _, _ = _parse_fmt1(registros)
    vd, v1 = registros.get_reg(rd), registros.get_reg(r1)
    result = vd & v1
    registros.update_flags(result, operand_a=vd, operand_b=v1, operation="logic")
    return False


# ---------------------------------------------------------------------------
# Instrucciones F2 — memoria
# ---------------------------------------------------------------------------

def load(cpu, registros, ram):
    _, r1, base, index, scale, offset = _parse_fmt2(registros)
    addr = registros.get_reg(base) + registros.get_reg(index) * scale + offset
    registros.set_reg(r1, ram.read(addr))
    return False


def store(cpu, registros, ram):
    _, r1, base, index, scale, offset = _parse_fmt2(registros)
    addr = registros.get_reg(base) + registros.get_reg(index) * scale + offset
    ram.write(addr, registros.get_reg(r1))
    return False


def lea(cpu, registros, ram):
    _, r1, base, index, scale, offset = _parse_fmt2(registros)
    addr = registros.get_reg(base) + registros.get_reg(index) * scale + offset
    registros.set_reg(r1, addr)
    return False


# ---------------------------------------------------------------------------
# Instrucciones F3 — saltos
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


# jmpr/jzr/jnzr/jcr/jnr son los mismos saltos con modo=2 (por registro)
# El modo ya viene codificado en la instrucción, así que reusan la misma función
jmpr = jmp
jzr  = jz
jnzr = jnz
jcr  = jc
jnr  = jn


def call(cpu, registros, ram):
    modo, r1, r2, offset, _ = _parse_fmt3(registros)
    registros.SP -= 1
    ram.write(registros.SP, registros.PC)
    registros.PC = _jump_target(registros, modo, r1, r2, offset)
    return True


def ret(cpu, registros, ram):
    direccion = ram.read(registros.SP)
    registros.SP += 1
    registros.PC = direccion
    return True


def iret(cpu, registros, ram):
    direccion = ram.read(registros.SP)
    registros.SP += 1
    registros.PC = direccion
    return True


# ---------------------------------------------------------------------------
# Tabla de decodificación del CPU
#
# El CPU lee los primeros 4 bits (pre) para saber el formato y cuántos bits
# tiene el opcode, luego indexa aquí con el opcode dentro del formato.
#
# Pre → (opcode_bits, tabla)
# ---------------------------------------------------------------------------

# F1: pre=0001  opcode 10 bits  → opcodes 0-24
_F1 = {
    0:  mov,
    1:  push,
    2:  pop,
    3:  xchg,
    4:  add,
    5:  addi,
    6:  sub,
    7:  subi,
    8:  mul,
    9:  muli,
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
}

# F2: pre=0010  opcode 8 bits  → opcodes 0-2
_F2 = {
    0: load,
    1: store,
    2: lea,
}

# F3: pre=0011  opcode 10 bits  → opcodes 0-10
_F3 = {
    0:  jmp,
    1:  jz,
    2:  jnz,
    3:  jc,
    4:  jn,
    5:  jmpr,
    6:  jzr,
    7:  jnzr,
    8:  jcr,
    9:  jnr,
    10: call,
}

# F4: pre=0000  opcode 6 bits  → opcodes 0-2
_F4 = {
    0: nop,
    1: halt,
    2: inti,
}

# Mapa principal: pre binario → (opcode_bits, sub-tabla)
DECODE_TABLE = {
    "0000": (6,  _F4),
    "0001": (10, _F1),
    "0010": (8,  _F2),
    "0011": (10, _F3),
}


def decode(ir: str):
    """
    Recibe el IR completo (64 bits como str) y devuelve la función de ejecución.
    Lanza KeyError si el pre o el opcode son desconocidos.
    """
    pre          = ir[0:4]
    opcode_bits, tabla = DECODE_TABLE[pre]
    opcode       = int(ir[4: 4 + opcode_bits], 2)
    return tabla[opcode]


# ---------------------------------------------------------------------------
# Helpers de display (para cpu.py / depuración)
# ---------------------------------------------------------------------------

def params_format_1(ir: str):
    """Retorna (pre, opcode, modo, rd, r1, r2, inm) como strings binarios."""
    return (
        ir[0:4],    # pre
        ir[4:14],   # opcode (10 bits)
        ir[14:20],  # modo   (6 bits)
        ir[20:24],  # rd     (4 bits)
        ir[24:28],  # r1     (4 bits)
        ir[28:32],  # r2     (4 bits)
        ir[32:64],  # inm    (32 bits)
    )
