from CPU.cpu import CPU
from CPU.ram import RAM


def load_instructions(filepath: str) -> list:
    """
    Lee un archivo .txt con un byte (8 bits) por línea.
    Ignora líneas vacías y comentarios que empiecen con '#'.

    Retorna:
        list[str]: Lista de strings binarios de 8 bits.
    """
    instrucciones = []
    with open(filepath, "r") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):  # ignorar vacías y comentarios
                continue
            instrucciones.append(linea)
    return instrucciones


def main():

    ram = RAM(1024)
    cpu = CPU(ram)

    instrucciones = load_instructions("data/instructions.txt")

    print(
        f"\n[+] {len(instrucciones)} bytes cargados desde instructions.txt: {instrucciones}"
    )

    print("[+] Cargando instrucciones en RAM desde dirección 0x0000...")
    for i, byte in enumerate(instrucciones):
        ram.write(i, byte)

    print(f"\n[+] Lectura 0x0010: {ram.read(16)}")
    print(f"[+] Bit 0 de 0x0000: {ram.read_bit(0, 0)}")
    print(f"[+] Bits [0:4] de 0x0000: {ram.read_bits(0, 0, 4)}")
    print(f"[+] Bloque 0x0000-0x0002 (3 bytes): {ram.read_block(0, 3)}")

    print("\n[+] Mapa de memoria (primeras 2 filas):")
    ram.display(0, 32)

    while cpu.running:
        cpu.step()

    # lines = load_file()
    #
    # def fetch():
    #     for idx,line in enumerate(lines):
    #         instr = instr_dict[line[0:8]][0] # function
    #         param_sizes = instr_dict[line[0:8]][0] # function
    #         instr(line[9:],param_sizes) # exec function
    #
    # def binario_a_decimal(binario):
    #     return int(binario, 2)
    #
    # fetch()


if __name__ == "__main__":
    main()
