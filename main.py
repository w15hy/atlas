import sys

from CPU.cpu import CPU
from CPU.ram import RAM


def load_instructions(filepath: str):
    """
    Lee un archivo .bin con un byte (8 bits) por línea.
    Ignora líneas vacías y comentarios que empiecen con '#'.
    Si la primera línea no vacía es @<dirección>, la usa como base de carga.

    Retorna:
        (list[str], int): Lista de strings binarios de 8 bits y dirección base.
    """
    instrucciones = []
    base_addr = 0
    with open(filepath, "r") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            if linea.startswith("@"):
                base_addr = int(linea[1:])
                continue
            instrucciones.append(linea)
    return instrucciones, base_addr


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

    filepath = sys.argv[1] if len(sys.argv) > 1 else "data/brun.bin"

    ram = RAM(65536)
    cpu = CPU(ram)

    instrucciones, base_addr = load_instructions(filepath)

    print(f"\n[+] {len(instrucciones)} bytes cargados desde {filepath}")
    if base_addr:
        print(f"[+] Dirección base de carga: {base_addr} (0x{base_addr:04X})")

    print(f"[+] Cargando instrucciones en RAM desde dirección 0x{base_addr:04X}...")
    for i, byte in enumerate(instrucciones):
        ram.write(base_addr + i, byte)

    cpu.reg.PC = base_addr

    print(f"\n[+] Mapa de memoria (desde 0x{base_addr:04X}, 6 filas):")
    ram.display(base_addr, base_addr + 48)

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

    # ── Inspector de memoria interactivo ──────────────────────────────────
    print("\n" + "=" * 70)
    print("  INSPECTOR DE MEMORIA")
    print("=" * 70)
    print("  Escribe una dirección para ver su contenido.")
    print("  Formatos aceptados: 0x400, 1024, 0b10000000000")
    print("  Agrega +N para ver N bytes (ej: 0x400+16)")
    print("  Escribe 'q' para salir.\n")

    while True:
        try:
            entrada = input("  mem> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not entrada or entrada.lower() == "q":
            break

        try:
            # Parsear dirección y cantidad opcional
            n_bytes = 1
            if "+" in entrada:
                parts = entrada.split("+", 1)
                addr = int(parts[0].strip(), 0)
                n_bytes = int(parts[1].strip(), 0)
            else:
                addr = int(entrada, 0)

            if n_bytes < 1:
                n_bytes = 1
            if n_bytes > 64:
                n_bytes = 64

            # Mostrar como byte(s)
            bloque = ram.read_block(addr, n_bytes)
            valor_int = int(bloque, 2)

            if n_bytes == 1:
                byte_str = ram.read(addr)
                print(
                    f"  [{addr} / 0x{addr:04X}]  bin={byte_str}  "
                    f"dec={int(byte_str, 2)}  hex=0x{int(byte_str, 2):02X}"
                )
            else:
                print(
                    f"  [{addr} / 0x{addr:04X}] .. "
                    f"[{addr + n_bytes - 1} / 0x{addr + n_bytes - 1:04X}]  "
                    f"({n_bytes} bytes)"
                )
                # Mostrar fila por fila de 8 bytes
                for off in range(0, n_bytes, 8):
                    chunk = min(8, n_bytes - off)
                    bytes_str = " ".join(ram.read(addr + off + b) for b in range(chunk))
                    dec_vals = " ".join(
                        f"{int(ram.read(addr + off + b), 2):3d}" for b in range(chunk)
                    )
                    print(f"    0x{addr + off:04X} | {bytes_str}")
                    print(f"           dec: {dec_vals}")
                # Si cabe en 64 bits, mostrar valor entero
                if n_bytes <= 8:
                    print(
                        f"    -> valor entero ({n_bytes * 8} bits): "
                        f"{valor_int}  (0x{valor_int:X})"
                    )

        except Exception as e:
            print(f"  [!] Error: {e}")


if __name__ == "__main__":
    main()
