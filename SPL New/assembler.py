import os
import re
import struct
import sys


INSTR_DICT = {
    "mov": {"opcode": 0, "formato": 1},
    "push": {"opcode": 1, "formato": 1},
    "pop": {"opcode": 2, "formato": 1},
    "xchg": {"opcode": 3, "formato": 1},
    "add": {"opcode": 4, "formato": 1},
    "addi": {"opcode": 5, "formato": 1},
    "sub": {"opcode": 6, "formato": 1},
    "subi": {"opcode": 7, "formato": 1},
    "mul": {"opcode": 8, "formato": 1},
    "muli": {"opcode": 9, "formato": 1},
    "div": {"opcode": 10, "formato": 1},
    "divi": {"opcode": 11, "formato": 1},
    "inc": {"opcode": 12, "formato": 1},
    "dec": {"opcode": 13, "formato": 1},
    "neg": {"opcode": 14, "formato": 1},
    "and": {"opcode": 15, "formato": 1},
    "or": {"opcode": 16, "formato": 1},
    "xor": {"opcode": 17, "formato": 1},
    "not": {"opcode": 18, "formato": 1},
    "shl": {"opcode": 19, "formato": 1},
    "shr": {"opcode": 20, "formato": 1},
    "rol": {"opcode": 21, "formato": 1},
    "ror": {"opcode": 22, "formato": 1},
    "cmp": {"opcode": 23, "formato": 1},
    "test": {"opcode": 24, "formato": 1},
    "mod": {"opcode": 25, "formato": 1},
    "modi": {"opcode": 26, "formato": 1},
    "out": {"opcode": 27, "formato": 1},
    "load": {"opcode": 0, "formato": 2},
    "store": {"opcode": 1, "formato": 2},
    "lea": {"opcode": 2, "formato": 2},
    "loadw": {"opcode": 3, "formato": 2},
    "storew": {"opcode": 4, "formato": 2},
    "jmp": {"opcode": 0, "formato": 3},
    "jz": {"opcode": 1, "formato": 3},
    "jnz": {"opcode": 2, "formato": 3},
    "jc": {"opcode": 3, "formato": 3},
    "jn": {"opcode": 4, "formato": 3},
    "jmpr": {"opcode": 5, "formato": 3},
    "jzr": {"opcode": 6, "formato": 3},
    "jnzr": {"opcode": 7, "formato": 3},
    "jcr": {"opcode": 8, "formato": 3},
    "jnr": {"opcode": 9, "formato": 3},
    "call": {"opcode": 10, "formato": 3},
    "jg": {"opcode": 11, "formato": 3},
    "jge": {"opcode": 12, "formato": 3},
    "jne": {"opcode": 13, "formato": 3},
    "nop": {"opcode": 0, "formato": 4},
    "halt": {"opcode": 1, "formato": 4},
    "inti": {"opcode": 2, "formato": 4},
    "ret": {"opcode": 3, "formato": 4},
    "iret": {"opcode": 4, "formato": 4},
    "fmov": {"opcode": 0, "formato": 5},
    "fadd": {"opcode": 1, "formato": 5},
    "fsub": {"opcode": 2, "formato": 5},
    "fmul": {"opcode": 3, "formato": 5},
    "fdiv": {"opcode": 4, "formato": 5},
    "fcmp": {"opcode": 5, "formato": 5},
    "fabs": {"opcode": 6, "formato": 5},
    "fneg": {"opcode": 7, "formato": 5},
    "fsqrt": {"opcode": 8, "formato": 5},
    "fi2f": {"opcode": 9, "formato": 5},
    "ff2i": {"opcode": 10, "formato": 5},
}

PRE_INSTR = {
    1: {"pre": "0001", "opcode_bits": 10},
    2: {"pre": "0010", "opcode_bits": 8},
    3: {"pre": "0011", "opcode_bits": 10},
    4: {"pre": "0000", "opcode_bits": 6},
    5: {"pre": "0100", "opcode_bits": 10},
}

FIELD_RANGES = {
    1: (32, 64),
    2: (32, 64),
    3: (28, 60),
    4: (16, 48),
    5: (32, 64),
}

RELATIVE_F3_OPCODES = {5, 6, 7, 8, 9}

INCLUDE_RE = re.compile(r'^\s*#include\s+[<"]([^>"]+)[>"]\s*$')
DEFINE_RE = re.compile(r'^\s*#define\s+(\w+)\s+(.*?)\s*$')
ORG_RE = re.compile(r'^\s*\.org\s+(\d+)\s*(?:#.*)?$', re.IGNORECASE)
FLOAT_RE = re.compile(
    r'^-?[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?$|^-?[0-9]+[eE][+-]?[0-9]+$'
)
REGISTER_RE = re.compile(r'^[rR](1[0-5]|[0-9])$')


def zfill_bin(number, bits):
    """Convert an integer to fixed-width binary using two's complement."""
    if number < 0:
        number &= (1 << bits) - 1
    return bin(number)[2:].zfill(bits)[-bits:]


def is_register(token):
    return bool(REGISTER_RE.fullmatch(str(token)))


def is_float_token(token):
    return bool(FLOAT_RE.fullmatch(str(token)))


def parse_int_value(token):
    return int(str(token), 0)


def include_search_paths(raw_path, base_dir):
    """Search includes from the current folder up through its ancestors."""
    if os.path.isabs(raw_path):
        return [raw_path]

    candidates = []
    seen = set()
    current_dir = os.path.abspath(base_dir)

    while True:
        candidate = os.path.join(current_dir, raw_path)
        if candidate not in seen:
            candidates.append(candidate)
            seen.add(candidate)

        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            break
        current_dir = parent_dir

    cwd_candidate = os.path.join(os.getcwd(), raw_path)
    if cwd_candidate not in seen:
        candidates.append(cwd_candidate)

    return candidates


def preprocess(lines, base_dir='.', depth=0, defines=None):
    """Expand #include and #define using only the standard library."""
    if depth > 10:
        raise RecursionError('Too many nested #include directives')

    if defines is None:
        defines = {}

    expanded = []
    for line in lines:
        define_match = DEFINE_RE.match(line)
        if define_match:
            defines[define_match.group(1)] = define_match.group(2)
            continue

        include_match = INCLUDE_RE.match(line)
        if include_match:
            raw_path = include_match.group(1)
            search_paths = include_search_paths(raw_path, base_dir)

            for path in search_paths:
                if not os.path.exists(path):
                    continue

                with open(path, 'r', encoding='utf-8') as handle:
                    expanded.extend(
                        preprocess(
                            handle.readlines(),
                            base_dir=os.path.dirname(os.path.abspath(path)),
                            depth=depth + 1,
                            defines=defines,
                        )
                    )
                break
            else:
                raise FileNotFoundError(f"#include target not found: {raw_path}")

            continue

        for name, value in defines.items():
            line = re.sub(r'\b' + re.escape(name) + r'\b', value, line)

        expanded.append(line)

    return expanded


def extract_org(lines):
    """Remove a .org directive while preserving the requested base address."""
    base_address = 0
    cleaned = []

    for line in lines:
        match = ORG_RE.match(line.strip())
        if match:
            base_address = int(match.group(1))
            continue
        cleaned.append(line)

    return base_address, cleaned


def clean_instruction_line(line):
    """Drop comments, blank lines, and label-only lines."""
    stripped = line.strip()
    if not stripped or stripped.startswith('#'):
        return None

    if '#' in stripped:
        stripped = stripped.split('#', 1)[0].strip()
    if not stripped or ORG_RE.match(stripped):
        return None

    if stripped.endswith(':') and ' ' not in stripped:
        return None

    if ':' in stripped:
        label_name, remainder = stripped.split(':', 1)
        if re.fullmatch(r'[A-Za-z_]\w*', label_name.strip()):
            stripped = remainder.strip()

    return stripped or None


def first_pass(lines):
    """Map labels to byte addresses because the VM PC advances 8 bytes per instruction."""
    labels = {}
    current_address = 0

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        if '#' in stripped:
            stripped = stripped.split('#', 1)[0].strip()
        if not stripped or ORG_RE.match(stripped):
            continue

        if stripped.endswith(':') and ' ' not in stripped:
            label_name = stripped[:-1].strip()
            if label_name in labels:
                raise ValueError(f"Duplicate label: {label_name}")
            labels[label_name] = current_address
            continue

        if ':' in stripped:
            label_name, remainder = stripped.split(':', 1)
            label_name = label_name.strip()
            if re.fullmatch(r'[A-Za-z_]\w*', label_name):
                if label_name in labels:
                    raise ValueError(f"Duplicate label: {label_name}")
                labels[label_name] = current_address
                stripped = remainder.strip()
                if not stripped:
                    continue

        current_address += 8

    return labels


def encode_f1(opcode, operands):
    """Encode register/immediate instructions."""
    pre = PRE_INSTR[1]['pre']
    opcode_bin = zfill_bin(opcode, 10)
    mode = rd = r1 = r2 = 0
    immediate_value = None
    registers = []

    for operand in operands:
        if is_register(operand):
            registers.append(int(str(operand)[1:]))
        else:
            immediate_value = parse_int_value(operand)

    register_count = len(registers)
    has_immediate = immediate_value is not None
    immediate = immediate_value if has_immediate else 0

    if register_count == 1 and not has_immediate:
        mode, rd = 0, registers[0]
    elif register_count == 1 and has_immediate:
        mode, rd = 1, registers[0]
    elif register_count == 2 and not has_immediate:
        mode, rd, r1 = 2, registers[0], registers[1]
    elif register_count == 2 and has_immediate:
        mode, rd, r1 = 3, registers[0], registers[1]
    elif register_count == 3 and not has_immediate:
        mode, rd, r1, r2 = 4, registers[0], registers[1], registers[2]
    elif register_count == 3 and has_immediate:
        mode, rd, r1, r2 = 5, registers[0], registers[1], registers[2]

    bits = (
        pre
        + opcode_bin
        + zfill_bin(mode, 6)
        + zfill_bin(rd, 4)
        + zfill_bin(r1, 4)
        + zfill_bin(r2, 4)
        + zfill_bin(immediate, 32)
    )
    assert len(bits) == 64
    return bits


def encode_f2(opcode, operands):
    """Encode memory instructions, including shorthand absolute forms."""
    pre = PRE_INSTR[2]['pre']
    opcode_bin = zfill_bin(opcode, 8)
    mode = r1 = base = index = 0
    scale = offset = 0
    registers = []
    literals = []

    for operand in operands:
        if is_register(operand):
            registers.append(int(str(operand)[1:]))
        else:
            literals.append(parse_int_value(operand))

    register_count = len(registers)
    if register_count > 0:
        r1 = registers[0]
    if register_count > 1:
        base = registers[1]
    if register_count > 2:
        index = registers[2]

    if register_count <= 1:
        mode = 1
        if literals:
            offset = literals[0]
    elif register_count == 2:
        if len(literals) >= 2:
            mode = 0
            scale = literals[0]
            offset = literals[1]
        else:
            mode = 2
            if literals:
                offset = literals[0]
    else:
        mode = 0
        if len(literals) > 0:
            scale = literals[0]
        if len(literals) > 1:
            offset = literals[1]

    bits = (
        pre
        + opcode_bin
        + zfill_bin(mode, 6)
        + zfill_bin(r1, 4)
        + zfill_bin(base, 4)
        + zfill_bin(index, 4)
        + zfill_bin(scale, 2)
        + zfill_bin(offset, 32)
    )
    assert len(bits) == 64
    return bits


def encode_f3(opcode, operands):
    """Encode jump and call instructions."""
    pre = PRE_INSTR[3]['pre']
    opcode_bin = zfill_bin(opcode, 10)
    mode = r1 = r2 = 0
    offset = flags = 0
    registers = []
    literals = []

    for operand in operands:
        if is_register(operand):
            registers.append(int(str(operand)[1:]))
        else:
            literals.append(parse_int_value(operand))

    if registers:
        r1 = registers[0]
    if len(registers) > 1:
        r2 = registers[1]
    if literals:
        offset = literals[0]

    if opcode in RELATIVE_F3_OPCODES:
        mode = 2

    bits = (
        pre
        + opcode_bin
        + zfill_bin(mode, 6)
        + zfill_bin(r1, 4)
        + zfill_bin(r2, 4)
        + zfill_bin(offset, 32)
        + zfill_bin(flags, 4)
    )
    assert len(bits) == 64
    return bits


def encode_f4(opcode, operands):
    """Encode control instructions."""
    pre = PRE_INSTR[4]['pre']
    opcode_bin = zfill_bin(opcode, 6)
    mode = 0
    immediate = 0

    for operand in operands:
        if not is_register(operand):
            immediate = parse_int_value(operand)
            mode = 1

    bits = (
        pre
        + opcode_bin
        + zfill_bin(mode, 6)
        + zfill_bin(immediate, 32)
        + zfill_bin(0, 16)
    )
    assert len(bits) == 64
    return bits


def encode_f5(opcode, operands):
    """Encode floating-point instructions."""
    pre = PRE_INSTR[5]['pre']
    opcode_bin = zfill_bin(opcode, 10)
    mode = rd = r1 = r2 = 0
    immediate_value = None
    registers = []

    for operand in operands:
        if is_register(operand):
            registers.append(int(str(operand)[1:]))
            continue

        if is_float_token(operand):
            immediate_value = struct.unpack('>I', struct.pack('>f', float(operand)))[0]
        else:
            immediate_value = parse_int_value(operand)

    register_count = len(registers)
    has_immediate = immediate_value is not None
    immediate = immediate_value if has_immediate else 0

    if register_count == 1 and not has_immediate:
        mode, rd = 0, registers[0]
    elif register_count == 1 and has_immediate:
        mode, rd = 1, registers[0]
    elif register_count == 2 and not has_immediate:
        mode, rd, r1 = 2, registers[0], registers[1]
    elif register_count == 2 and has_immediate:
        mode, rd, r1 = 3, registers[0], registers[1]

    bits = (
        pre
        + opcode_bin
        + zfill_bin(mode, 6)
        + zfill_bin(rd, 4)
        + zfill_bin(r1, 4)
        + zfill_bin(r2, 4)
        + zfill_bin(immediate, 32)
    )
    assert len(bits) == 64
    return bits


ENCODERS = {
    1: encode_f1,
    2: encode_f2,
    3: encode_f3,
    4: encode_f4,
    5: encode_f5,
}


def inject_placeholder(bits, instruction_format):
    """Replace the low 8 bits of the relocatable field with {dir}."""
    field_start, field_end = FIELD_RANGES[instruction_format]
    placeholder_start = field_end - 8
    return bits[:placeholder_start] + '{dir}' + bits[field_end:]


def is_numeric_token(token):
    try:
        parse_int_value(token)
        return True
    except ValueError:
        return is_float_token(token)


def build_instruction(instruction, labels, instruction_index):
    """Encode one instruction and emit relocation metadata when needed."""
    mnemonic = instruction['mnemonic']
    operands = instruction['operands']
    info = INSTR_DICT[mnemonic]
    instruction_format = info['formato']
    opcode = info['opcode']
    current_address = instruction_index * 8

    prepared_operands = []
    relocation_target = None

    for operand in operands:
        if is_register(operand) or is_numeric_token(operand):
            prepared_operands.append(operand)
            continue

        if operand not in labels:
            raise ValueError(f"Unknown symbol: {operand}")

        if instruction_format == 3 and opcode in RELATIVE_F3_OPCODES:
            prepared_operands.append(str(labels[operand] - current_address))
            continue

        if relocation_target is not None:
            raise ValueError('Only one relocatable symbol is supported per instruction')

        relocation_target = labels[operand]
        prepared_operands.append('0')

    bits = ENCODERS[instruction_format](opcode, prepared_operands)
    relocation_entry = None

    if relocation_target is not None:
        relocation_entry = {
            'source_index': current_address,
            'target_index': relocation_target,
            'format': instruction_format,
        }

    return bits, relocation_entry


def parse(input_path):
    """Load source code, preprocess it, and collect instruction metadata."""
    with open(input_path, 'r', encoding='utf-8') as handle:
        source_lines = handle.readlines()

    expanded_lines = preprocess(
        source_lines,
        base_dir=os.path.dirname(os.path.abspath(input_path)) or '.',
    )
    base_address, expanded_lines = extract_org(expanded_lines)
    labels = first_pass(expanded_lines)

    instructions = []
    for line in expanded_lines:
        instruction_text = clean_instruction_line(line)
        if instruction_text is None:
            continue

        parts = [part for part in re.split(r'[\s,]+', instruction_text) if part]
        mnemonic = parts[0].lower()
        operands = parts[1:]

        if mnemonic not in INSTR_DICT:
            raise ValueError(f"Unknown instruction: {mnemonic}")

        instructions.append(
            {
                'mnemonic': mnemonic,
                'operands': operands,
                'raw': instruction_text,
            }
        )

    return {
        'input_path': input_path,
        'base_address': base_address,
        'labels': labels,
        'instructions': instructions,
    }


def translate(parsed_program):
    """Convert parsed instructions into binary text plus relocation entries."""
    binary_lines = []
    relocations = []

    for instruction_index, instruction in enumerate(parsed_program['instructions']):
        bits, relocation_entry = build_instruction(
            instruction,
            parsed_program['labels'],
            instruction_index,
        )
        binary_lines.append(bits)
        if relocation_entry is not None:
            relocations.append(relocation_entry)

    return {
        'base_address': parsed_program['base_address'],
        'binary_lines': binary_lines,
        'relocations': relocations,
    }


def write_output(translated_program, output_path):
    """Write the .binReloc file as one byte per line plus relocation metadata."""
    parent_dir = os.path.dirname(output_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as handle:
        if translated_program['base_address']:
            handle.write(f"#BASE {translated_program['base_address']}\n")

        for binary_line in translated_program['binary_lines']:
            if len(binary_line) != 64:
                raise ValueError('Assembler instructions must be 64 bits before byte splitting')

            for start in range(0, 64, 8):
                handle.write(binary_line[start:start + 8] + '\n')

        handle.write('---RELOC---\n')
        for relocation in translated_program['relocations']:
            handle.write(
                f"{relocation['source_index']} {relocation['target_index']} {relocation['format']}\n"
            )

    return output_path


def default_output_path(input_path):
    """Place assembler output under outputs/assembler by default."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    return os.path.join(root_dir, 'outputs', 'assembler', f'{base_name}.binReloc')


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print('Usage: python assembler.py <input.asm> [output.binReloc]')
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) == 3 else default_output_path(input_path)

    try:
        parsed_program = parse(input_path)
        translated_program = translate(parsed_program)
        write_output(translated_program, output_path)
    except Exception as error:
        print(f'Assembler error: {error}')
        sys.exit(1)

    print(output_path)


if __name__ == '__main__':
    main()