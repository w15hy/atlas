import os
import re
import sys


BASE_RE = re.compile(r'^\s*#BASE\s+(\d+)\s*$')
RELOC_RE = re.compile(r'^(\d+)(?:\s+(\d+))(?:\s+(\d+))?$')
PLACEHOLDER_RE = re.compile(r'\{[^}]+\}')

FIELD_RANGES = {
    1: (32, 64),
    2: (32, 64),
    3: (28, 60),
    4: (16, 48),
    5: (32, 64),
}


def parse(input_path):
    """Read a .binReloc file and split binary lines from relocation entries."""
    with open(input_path, 'r', encoding='utf-8') as handle:
        lines = handle.readlines()

    base_address = 0
    binary_lines = []
    relocations = []
    inside_relocation_table = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        base_match = BASE_RE.match(line)
        if base_match and not inside_relocation_table and not binary_lines:
            base_address = int(base_match.group(1))
            continue

        if line.startswith('#'):
            continue

        if line == '---RELOC---':
            inside_relocation_table = True
            continue

        if not inside_relocation_table:
            binary_lines.append(line)
            continue

        reloc_match = RELOC_RE.fullmatch(line)
        if reloc_match is None:
            raise ValueError(f'Invalid relocation entry: {line}')

        if reloc_match.group(2) is None:
            raise ValueError(
                'Relocation entries need both source and target indexes for linking'
            )

        relocations.append(
            {
                'source_index': int(reloc_match.group(1)),
                'target_index': int(reloc_match.group(2)),
                'format': int(reloc_match.group(3)) if reloc_match.group(3) else None,
            }
        )

    if not inside_relocation_table:
        raise ValueError('Missing ---RELOC--- separator')

    return {
        'base_address': base_address,
        'binary_lines': binary_lines,
        'relocations': relocations,
    }


def patch_instruction_bits(instruction_bits, instruction_format, absolute_address):
    """Patch the full relocatable field inside a 64-bit instruction."""
    if instruction_format not in FIELD_RANGES:
        raise ValueError(f'Unsupported relocation format: {instruction_format}')

    if len(instruction_bits) != 64:
        raise ValueError('Instructions must be 64 bits before relocation patching')

    field_start, field_end = FIELD_RANGES[instruction_format]
    field_width = field_end - field_start
    max_address = (1 << field_width) - 1
    if absolute_address < 0 or absolute_address > max_address:
        raise ValueError(
            f'Absolute address {absolute_address} does not fit in {field_width} bits'
        )

    replacement = format(absolute_address, f'0{field_width}b')
    return (
        instruction_bits[:field_start]
        + replacement
        + instruction_bits[field_end:]
    )


def translate(parsed_program):
    """Resolve each {dir} placeholder using the parsed relocation table."""
    linked_lines = list(parsed_program['binary_lines'])

    if linked_lines and all(len(line) == 8 for line in linked_lines):
        for relocation in parsed_program['relocations']:
            source_index = relocation['source_index']
            target_index = relocation['target_index']
            instruction_format = relocation['format']

            if source_index < 0 or source_index + 7 >= len(linked_lines):
                raise ValueError(f'Relocation source out of range: {source_index}')

            if instruction_format is None:
                raise ValueError('Byte-oriented .binReloc entries must include the format')

            absolute_address = parsed_program['base_address'] + target_index

            instruction_bits = ''.join(linked_lines[source_index:source_index + 8])
            instruction_bits = patch_instruction_bits(
                instruction_bits,
                instruction_format,
                absolute_address,
            )

            for byte_index in range(8):
                start = byte_index * 8
                linked_lines[source_index + byte_index] = instruction_bits[start:start + 8]

        return linked_lines

    for relocation in parsed_program['relocations']:
        source_index = relocation['source_index']
        target_index = relocation['target_index']
        instruction_format = relocation['format']

        if source_index < 0 or source_index >= len(linked_lines):
            raise ValueError(f'Relocation source out of range: {source_index}')

        absolute_address = parsed_program['base_address'] + target_index
        replacement = format(absolute_address, '032b')
        placeholder_match = PLACEHOLDER_RE.search(linked_lines[source_index])

        if placeholder_match is not None:
            linked_lines[source_index] = (
                linked_lines[source_index][:placeholder_match.start()]
                + replacement
                + linked_lines[source_index][placeholder_match.end():]
            )
            continue

        if instruction_format is not None and len(linked_lines[source_index]) == 64:
            linked_lines[source_index] = patch_instruction_bits(
                linked_lines[source_index],
                instruction_format,
                absolute_address,
            )
            continue

        raise ValueError(
            f'Relocation source {source_index} does not contain a visible placeholder'
        )

    for line_index, line in enumerate(linked_lines):
        if PLACEHOLDER_RE.search(line):
            raise ValueError(f'Unresolved relocation placeholder at line {line_index}')

    return linked_lines


def write_output(linked_lines, output_path, base_address=0):
    """Write the final binary as one 8-bit byte per line for atlas/main.py."""
    parent_dir = os.path.dirname(output_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as handle:
        if base_address:
            handle.write(f'@{base_address}\n')

        for line in linked_lines:
            if len(line) == 8:
                handle.write(line + '\n')
                continue

            if len(line) != 64:
                raise ValueError('Linked instructions must be 64 bits or 8-bit bytes')

            for start in range(0, 64, 8):
                handle.write(line[start:start + 8] + '\n')

    return output_path


def default_output_path(input_path):
    """Place linker output under outputs/linker by default."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    base_name = os.path.basename(input_path)
    if base_name.endswith('.binReloc'):
        base_name = base_name[:-9]
    else:
        base_name = os.path.splitext(base_name)[0]
    return os.path.join(root_dir, 'outputs', 'linker', f'{base_name}.bin')


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print('Usage: python linker.py <input.binReloc> [output.bin]')
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) == 3 else default_output_path(input_path)

    try:
        parsed_program = parse(input_path)
        linked_lines = translate(parsed_program)
        write_output(linked_lines, output_path, parsed_program['base_address'])
    except Exception as error:
        print(f'Linker error: {error}')
        sys.exit(1)

    print(output_path)


if __name__ == '__main__':
    main()