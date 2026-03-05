def nop(cpu, registros, ram):
    pass


def mov1(cpu, registros, ram):
    pass


def mov2(cpu, registros, ram):
    pass


def mov3(cpu, registros, ram):
    pass


def halt(cpu, registros, ram):
    cpu.running = False


def ret(cpu, registros, ram):
    pass


def iret(cpu, registros, ram):
    pass


def int_(cpu, registros, ram):
    pass


def push(cpu, registros, ram):
    pass


def pop(cpu, registros, ram):
    pass


def load(cpu, registros, ram):
    pass


def store(cpu, registros, ram):
    pass


def xchg(cpu, registros, ram):
    pass


def lea(cpu, registros, ram):
    pass


def movi(cpu, registros, ram):
    pass


def add(cpu, registros, ram):
    pass


def addi(cpu, registros, ram):
    pass


def sub(cpu, registros, ram):
    pass


def mul(cpu, registros, ram):
    pass


def div(cpu, registros, ram):
    pass


def inc(cpu, registros, ram):
    pass


def dec(cpu, registros, ram):
    pass


def neg(cpu, registros, ram):
    pass


def adc(cpu, registros, ram):
    pass


def sbb(cpu, registros, ram):
    pass


def and_(cpu, registros, ram):
    pass


def or_(cpu, registros, ram):
    pass


def xor(cpu, registros, ram):
    pass


def not_(cpu, registros, ram):
    pass


def shl(cpu, registros, ram):
    pass


def rol(cpu, registros, ram):
    pass


def shr(cpu, registros, ram):
    pass


def ror(cpu, registros, ram):
    pass


def cmp(cpu, registros, ram):

    # Extraer parámetros desde IR
    params = registros.IR_params()

    reg1_bin = params[0:8]
    reg2_bin = params[8:16]

    r1 = int(reg1_bin, 2)
    r2 = int(reg2_bin, 2)

    val1 = registros.get_reg(r1)
    val2 = registros.get_reg(r2)

    # Resta cruda
    result_raw = val1 - val2

    # Actualizar flags
    registros.update_flags(result_raw, operand_a=val1, operand_b=val2, operation="sub")

    return False


def test(cpu, registros, ram):
    pass


def jmp(cpu, registros, ram):
    pass


def jz(cpu, registros, ram):

    if registros.flag_Z:
        direccion = int(registros.IR_params(), 2)
        registros.PC = direccion
        return True

    return False


def jnz(cpu, registros, ram):
    pass


def jc(cpu, registros, ram):
    pass


def call(cpu, registros, ram):
    pass


def jn(cpu, registros, ram):
    pass


instr_dict = {
    # 0x00: (nop, 0),
    0x01: (halt, 1),
    # 0x02: (ret, 0),
    # 0x03: (iret, 0),
    # 0x04: (int_, 4),
    # 0x05: (mov1, 1),
    # 0x06: (mov2, 3),
    # 0x07: (mov3, 2),
    # 0x08: (push, 4),
    # 0x09: (pop, 4),
    # 0x0A: (load, 3),
    # 0x0B: (store, 3),
    # 0x0C: (xchg, 1),
    # 0x0D: (lea, 3),
    # 0x0E: (movi, 1),
    # 0x0F: (add, 1),
    # 0x10: (addi, 1),
    # 0x11: (sub, 1),
    # 0x12: (mul, 1),
    # 0x13: (div, 1),
    # 0x14: (inc, 4),
    # 0x15: (dec, 4),
    # 0x16: (neg, 4),
    # 0x17: (adc, 1),
    # 0x18: (sbb, 1),
    # 0x19: (and_, 1),
    # 0x1A: (or_, 1),
    # 0x1B: (xor, 1),
    # 0x1C: (not_, 4),
    # 0x1D: (shl, 4),
    # 0x1E: (rol, 4),
    # 0x1F: (shr, 4),
    # 0x20: (ror, 4),
    0x21: (cmp, 3),
    # 0x22: (test, 1),
    # 0x23: (jmp, 5),
    0x24: (jz, 5),
    # 0x25: (jnz, 5),
    # 0x26: (jc, 5),
    # 0x27: (call, 5),
    # 0x28: (jn, 5),
}


def r_m(IR):
    if len(IR) == 24:
        return (IR[8:16], IR[16:])
