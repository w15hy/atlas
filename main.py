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


def show_menu():
    """Muestra el menú de modos de ejecución"""
    print("\n" + "=" * 70)
    print("  MODOS DE EJECUCIÓN DE LA MÁQUINA VIRTUAL")
    print("=" * 70)
    print("\n  [1] Ejecución Completa")
    print("      Ejecuta todo el programa de una sola vez sin interrupciones.")
    print("\n  [2] Paso a Paso Manual")
    print("      Ejecuta una instrucción por entrada del usuario.")
    print("      Muestra memoria, registros y flags después de cada paso.")
    print("\n  [3] Paso a Paso con Delay")
    print("      Ejecuta automáticamente con un delay entre instrucciones.")
    print("      Muestra memoria, registros y flags después de cada paso.")
    print("\n" + "=" * 70)
    return input("\nSelecciona un modo (1, 2 o 3): ").strip()


def main():

    ram = RAM(6048)
    cpu = CPU(ram)

    instrucciones = load_instructions("data/PRUEBITA.bin")

    print(
        f"\n[+] {len(instrucciones)} bytes cargados desde PRUEBITA.bin: {instrucciones}"
    )

    print("[+] Cargando instrucciones en RAM desde dirección 0x0000...")
    for i, byte in enumerate(instrucciones):
        ram.write(i, byte)

    print("\n[+] Mapa de memoria (primeras 6 filas):")
    ram.display(0, 48)

    # Menú de selección de modo
    modo = show_menu()

    if modo == "1":
        # Modo 1: Ejecución completa
        cpu.run_all()
    elif modo == "2":
        # Modo 2: Paso a paso manual
        cpu.run_step_manual()

    elif modo == "3":
        # Modo 3: Paso a paso con delay
        try:
            delay_input = input(
                "\n¿Cuál es el delay entre instrucciones (en segundos)? [1.0]: "
            ).strip()
            delay = float(delay_input) if delay_input else 1.0

            if delay < 0:
                print("[!] El delay no puede ser negativo. Usando 1.0 segundos.")
                delay = 1.0

            cpu.run_step_timed(delay)
        except ValueError:
            print("[!] Entrada inválida. Usando delay de 1.0 segundo.")
            cpu.run_step_timed(1.0)

    else:
        print("[!] Opción no reconocida. Usando ejecución completa.")
        cpu.run_all()


if __name__ == "__main__":
    main()
