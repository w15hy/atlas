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

    instrucciones = load_instructions("data/test_totales.txt")

    print(
        f"\n[+] {len(instrucciones)} bytes cargados desde test_totales.txt: {instrucciones}"
    )

    print("[+] Cargando instrucciones en RAM desde dirección 0x0000...")
    for i, byte in enumerate(instrucciones):
        ram.write(i, byte)

    print("\n[+] Mapa de memoria (primeras 6 filas):")
    ram.display(0, 48)

    while cpu.running:
        cpu.step()


if __name__ == "__main__":
    main()
