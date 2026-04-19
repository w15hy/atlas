def _parse_fmt1(registros):
    ir = registros.IR
    modo = int(ir[14:20], 2)
    rd = int(ir[20:24], 2)
    r1 = int(ir[24:28], 2)
    r2 = int(ir[28:32], 2)
    inm = int(ir[32:64], 2)
    return modo, rd, r1, r2, inm


def _parse_fmt2(registros):
    ir = registros.IR
    modo = int(ir[12:18], 2)
    r1 = int(ir[18:22], 2)
    base = int(ir[22:26], 2)
    index = int(ir[26:30], 2)
    scale = int(ir[30:32], 2)
    offset = int(ir[32:64], 2)
    return modo, r1, base, index, scale, offset


def _parse_fmt3(registros):
    ir = registros.IR
    modo = int(ir[14:20], 2)
    r1 = int(ir[20:24], 2)
    r2 = int(ir[24:28], 2)
    offset = int(ir[28:60], 2)
    flags = int(ir[60:64], 2)
    return modo, r1, r2, offset, flags


def _parse_fmt4(registros):
    ir = registros.IR
    modo = int(ir[10:16], 2)
    inm32 = int(ir[16:48], 2)
    return modo, inm32


if __name__ == "__main__":
    pass
