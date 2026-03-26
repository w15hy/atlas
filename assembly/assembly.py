import re
import sys

instr_dict = {
    # ===== FORMATO 1  pre=0001  opcode=10 bits =====
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

    # ===== FORMATO 4  pre=0000  opcode=6 bits =====
    "nop":  {"opcode": 0, "formato": 4},
    "halt": {"opcode": 1, "formato": 4},
    "inti": {"opcode": 2, "formato": 4},
}

# pre(4) → opcode_bits
# Estos son los prefijos reales en binario y cuántos bits tiene el opcode
pre_instr = {
    1: {"pre": "0001", "opcode_bits": 10},  # F1: reg/inm
    2: {"pre": "0010", "opcode_bits": 8},   # F2: memoria
    3: {"pre": "0011", "opcode_bits": 10},  # F3: saltos
    4: {"pre": "0000", "opcode_bits": 6},   # F4: control
}

# Modos F1
MODOS_F1 = {
    "registro":                    0,
    "registro - inmediato":        1,
    "registro - registro":         2,
    "registro - registro - inmediato":        3,
    "registro - registro - registro":         4,
    "registro - registro - registro - inmediato": 5,
}

def zfill_bin(num, bits):
    return bin(num)[2:].zfill(bits)

def encode_f1(opcode, keywords):
    """
    [ pre(4) ][ opcode(10) ][ modo(6) ][ rd(4) ][ r1(4) ][ r2(4) ][ inm(32) ]
    = 64 bits
    """
    pre        = pre_instr[1]["pre"]
    opcode_bin = zfill_bin(opcode, 10)
    modo       = 0
    rd = r1 = r2 = 0
    inm        = 0

    regs = []
    inm_val = None

    for kw in keywords:
        kl = kw.lower()
        if kl.startswith("r") and kl[1:].isdigit() and int(kl[1:]) <= 15:
            regs.append(int(kl[1:]))
        else:
            inm_val = int(kw, 0)  # acepta 0x... o decimal

    n_regs = len(regs)
    has_inm = inm_val is not None

    if n_regs == 1 and not has_inm:
        modo = 0          # registro
        rd   = regs[0]
    elif n_regs == 1 and has_inm:
        modo = 1          # registro - inmediato
        rd   = regs[0]
        inm  = inm_val
    elif n_regs == 2 and not has_inm:
        modo = 2          # registro - registro
        rd, r1 = regs[0], regs[1]
    elif n_regs == 2 and has_inm:
        modo = 3          # registro - registro - inmediato
        rd, r1 = regs[0], regs[1]
        inm  = inm_val
    elif n_regs == 3 and not has_inm:
        modo = 4          # registro - registro - registro
        rd, r1, r2 = regs[0], regs[1], regs[2]
    elif n_regs == 3 and has_inm:
        modo = 5          # registro - registro - registro - inmediato
        rd, r1, r2 = regs[0], regs[1], regs[2]
        inm  = inm_val

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
    modo       = 0
    r1 = base = index = 0
    scale = 0
    offset = 0

    # Sintaxis esperada:
    #   load  rd, base, index, scale, offset
    #   store r1, base, index, scale, offset
    # (los campos que falten quedan en 0)
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

    # modo 0 = reg→mem (store), modo 1 = mem→reg (load/lea)
    # El assembler lo decide por la instrucción: load/lea = 1, store = 0
    # Aquí lo dejamos en 0; quien llama puede ajustarlo si hace falta.

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

def encode_f3(opcode, keywords):
    """
    [ pre(4) ][ opcode(10) ][ modo(6) ][ r1(4) ][ r2(4) ][ offset(32) ][ flags(4) ]
    = 64 bits
    """
    pre        = pre_instr[3]["pre"]
    opcode_bin = zfill_bin(opcode, 10)
    modo       = 0
    r1 = r2    = 0
    offset     = 0
    flags      = 0

    regs = []
    literals = []
    for kw in keywords:
        kl = kw.lower()
        if kl.startswith("r") and kl[1:].isdigit() and int(kl[1:]) <= 15:
            regs.append(int(kl[1:]))
        else:
            literals.append(int(kw, 0))

    if len(regs) > 0: r1 = regs[0]
    if len(regs) > 1: r2 = regs[1]
    if len(literals) > 0: offset = literals[0]

    # Inferir modo a partir del opcode original:
    # jmpr/jzr/jnzr/jcr/jnr (opcodes 5-9) → modo por registro (2)
    # el resto → absoluto (0)
    if opcode in range(5, 10):
        modo = 2
    else:
        modo = 0

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
    modo       = 0
    inm32      = 0

    literals = []
    for kw in keywords:
        kl = kw.lower()
        if not (kl.startswith("r") and kl[1:].isdigit()):
            literals.append(int(kw, 0))

    if len(literals) > 0:
        inm32 = literals[0]
        modo  = 1

    bits = (
        pre
        + opcode_bin
        + zfill_bin(modo,    6)
        + zfill_bin(inm32,  32)
        + zfill_bin(0,      16)   # padding
    )
    assert len(bits) == 64, f"F4 debe ser 64 bits, got {len(bits)}"
    return bits

ENCODERS = {1: encode_f1, 2: encode_f2, 3: encode_f3, 4: encode_f4}


def main():
    if len(sys.argv) < 2:
        print("Uso: python assembly.py <archivo_asm> [archivo_salida]")
        print()
        print("Argumentos:")
        print("  archivo_asm   : Archivo con instrucciones (una por línea)")
        print("  archivo_salida: Archivo para guardar bytecode (opcional)")
        print()
        print("Ejemplo:")
        print("  python assembly.py programa.asm")
        print("  python assembly.py programa.asm programa.bin")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        with open(input_file, 'r') as f:
            lineas = f.readlines()
    except FileNotFoundError:
        print(f"error: archivo '{input_file}' no encontrado")
        sys.exit(1)
    except Exception as e:
        print(f"error al leer '{input_file}': {e}")
        sys.exit(1)
    
    # Procesar instrucciones
    resultados = []
    for num_linea, linea in enumerate(lineas, 1):
        if linea.startswith("#") or linea.strip() == "":
            continue

        partes   = re.split(r"[ ,]+", linea.strip())
        instr    = partes[0].lower()
        keywords = [p for p in partes[1:] if p]

        if instr not in instr_dict:
            print(f"[Línea {num_linea}] error: instrucción desconocida '{instr}'")
            continue

        info    = instr_dict[instr]
        formato = info["formato"]
        opcode  = info["opcode"]

        encoder = ENCODERS[formato]
        bits    = encoder(opcode, keywords)

        resultado = f"{instr:6}  {bits}"
        resultados.append(resultado)
        print(resultado)
    
    # Guardar en archivo si se especificó
    if output_file:
        try:
            with open(output_file, 'w') as f:
                for resultado in resultados:
                    # Extraer solo los bits (después del nombre de instrucción)
                    bits = resultado.split()[-1]
                    # Escribir byte por byte (8 bits por línea)
                    for i in range(0, len(bits), 8):
                        f.write(bits[i:i+8] + '\n')
            print(f"\n✓ Bytecode guardado en '{output_file}'")
        except Exception as e:
            print(f"\nerror al escribir '{output_file}': {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
