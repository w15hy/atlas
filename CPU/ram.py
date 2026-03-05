"""
ram.py - Módulo de Memoria RAM
Arquitectura Von Neumann - Memoria direccionable por byte
Cada celda almacena 1 byte (8 bits) representado como string binario de 8 caracteres
"""

import unittest


class RAMError(Exception):
    """Excepción personalizada para errores de la RAM"""
    pass


class RAM:
    """
    Clase que simula una memoria RAM para la arquitectura Von Neumann.

    La memoria es direccionable por byte. Cada celda contiene 8 bits
    representados como un string binario (ej: '10110010').

    Parámetros:
        size (int): Cantidad de bytes de la RAM. Por defecto 256.
    """

    CELL_SIZE = 8  # bits por celda (1 byte)

    def __init__(self, size: int = 256):
        if size <= 0:
            raise RAMError(f"El tamaño de la RAM debe ser mayor a 0, se recibió: {size}")
        self.size = size
        # Memoria inicializada en 0 (cada celda es '00000000')
        self._memory = ['00000000'] * size

    # ------------------------------------------------------------------
    # Lectura
    # ------------------------------------------------------------------




    def read(self, address: int) -> str:
        """
        Lee 1 byte (8 bits) de la dirección indicada.

        Parámetros:
            address (int): Dirección de memoria a leer.

        Retorna:
            str: String de 8 bits. Ej: '10110010'
        """
        self._validate_address(address)
        return self._memory[address]

    def read_bits(self, address: int, offset: int, length: int) -> str:
        """
        Lee una cantidad específica de bits dentro de una celda.

        Parámetros:
            address (int): Dirección de la celda.
            offset (int): Bit inicial (0 = MSB).
            length (int): Cantidad de bits a leer.

        Retorna:
            str: String con los bits leídos.
        """
        self._validate_address(address)
        self._validate_bit_range(offset, length)
        byte = self._memory[address]
        return byte[offset: offset + length]

    def read_bit(self, address: int, bit_index: int) -> str:
        """
        Lee un único bit de una celda.

        Parámetros:
            address  (int): Dirección de la celda.
            bit_index (int): Índice del bit (0 = MSB, 7 = LSB).

        Retorna:
            str: '0' o '1'
        """
        return self.read_bits(address, bit_index, 1)

    def read_block(self, address: int, num_bytes: int) -> str:
        """
        Lee un bloque contiguo de bytes y los devuelve como un único string binario.
        Útil para leer instrucciones + parámetros completos.

        Parámetros:
            address   (int): Dirección inicial.
            num_bytes (int): Cantidad de bytes a leer.

        Retorna:
            str: Concatenación de todos los bytes leídos.
        """
        if num_bytes <= 0:
            raise RAMError("num_bytes debe ser mayor a 0")
        self._validate_address(address)
        self._validate_address(address + num_bytes - 1)
        return ''.join(self._memory[address: address + num_bytes])

    # ------------------------------------------------------------------
    # Escritura
    # ------------------------------------------------------------------

    def write(self, address: int, value: str):
        """
        Escribe 1 byte en la dirección indicada.

        Parámetros:
            address (int): Dirección de memoria.
            value   (str): String de exactamente 8 bits. Ej: '10110010'
        """
        self._validate_address(address)
        self._validate_byte(value)
        self._memory[address] = value

    def write_bit(self, address: int, bit_index: int, bit_value: str):
        """
        Escribe un único bit dentro de una celda sin modificar el resto.

        Parámetros:
            address   (int): Dirección de la celda.
            bit_index (int): Índice del bit a modificar (0 = MSB, 7 = LSB).
            bit_value (str): '0' o '1'
        """
        self._validate_address(address)
        if bit_index < 0 or bit_index >= self.CELL_SIZE:
            raise RAMError(f"bit_index debe estar entre 0 y {self.CELL_SIZE - 1}, se recibió: {bit_index}")
        if bit_value not in ('0', '1'):
            raise RAMError(f"bit_value debe ser '0' o '1', se recibió: '{bit_value}'")
        byte = list(self._memory[address])
        byte[bit_index] = bit_value
        self._memory[address] = ''.join(byte)

    def write_block(self, address: int, binary_string: str):
        """
        Escribe un bloque de bytes a partir de un string binario largo.
        El string debe tener longitud múltiplo de 8.

        Parámetros:
            address       (int): Dirección de inicio en la RAM.
            binary_string (str): String binario (múltiplo de 8 bits).
        """
        # Limpiar espacios (compatible con el formato de file.txt)
        binary_string = binary_string.replace(' ', '')

        if len(binary_string) % self.CELL_SIZE != 0:
            raise RAMError(
                f"El string binario debe tener longitud múltiplo de 8. "
                f"Longitud recibida: {len(binary_string)}"
            )

        num_bytes = len(binary_string) // self.CELL_SIZE
        self._validate_address(address)
        self._validate_address(address + num_bytes - 1)

        for i in range(num_bytes):
            byte = binary_string[i * self.CELL_SIZE: (i + 1) * self.CELL_SIZE]
            self._validate_byte(byte)
            self._memory[address + i] = byte

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    def clear(self):
        """Reinicia toda la memoria a ceros."""
        self._memory = ['00000000'] * self.size

    def display(self, start: int = 0, end: int = None, bytes_per_row: int = 8):
        """
        Muestra una región de la memoria en formato tabla.

        Parámetros:
            start        (int): Dirección inicial (inclusive). Por defecto 0.
            end          (int): Dirección final (exclusive). Por defecto: fin de la RAM.
            bytes_per_row (int): Bytes mostrados por fila. Por defecto 8.
        """
        if end is None:
            end = self.size
        self._validate_address(start)
        if end > self.size:
            raise RAMError(f"end ({end}) supera el tamaño de la RAM ({self.size})")
        if start >= end:
            raise RAMError("start debe ser menor que end")

        col_width = self.CELL_SIZE
        header_width = 6  # ancho de la columna de dirección

        # Encabezado
        print(f"\n{'RAM - Mapa de Memoria':^{header_width + bytes_per_row * (col_width + 1)}}")
        print(f"{'Dirección':<{header_width}} | " + ' '.join(f"[+{i}]".center(col_width) for i in range(bytes_per_row)))
        print('-' * (header_width + 3 + bytes_per_row * (col_width + 1)))

        row_start = start
        while row_start < end:
            row_end = min(row_start + bytes_per_row, end)
            cells = []
            for addr in range(row_start, row_end):
                cells.append(self._memory[addr])
            # Rellenar fila incompleta
            cells += ['        '] * (bytes_per_row - len(cells))
            addr_label = f"0x{row_start:04X}"
            print(f"{addr_label:<{header_width}} | " + ' '.join(cells))
            row_start += bytes_per_row

        print()

    # ------------------------------------------------------------------
    # Validaciones internas
    # ------------------------------------------------------------------

    def _validate_address(self, address: int):
        if not isinstance(address, int):
            raise RAMError(f"La dirección debe ser un entero, se recibió: {type(address)}")
        if address < 0 or address >= self.size:
            raise RAMError(
                f"Dirección fuera de rango: {address}. "
                f"Rango válido: 0 - {self.size - 1}"
            )

    def _validate_byte(self, value: str):
        if not isinstance(value, str):
            raise RAMError(f"El valor debe ser un string binario, se recibió: {type(value)}")
        if len(value) != self.CELL_SIZE:
            raise RAMError(
                f"El byte debe tener exactamente {self.CELL_SIZE} bits, "
                f"se recibió: '{value}' ({len(value)} bits)"
            )
        if not all(b in '01' for b in value):
            raise RAMError(f"El byte solo puede contener '0' y '1', se recibió: '{value}'")

    def _validate_bit_range(self, offset: int, length: int):
        if offset < 0 or length <= 0 or offset + length > self.CELL_SIZE:
            raise RAMError(
                f"Rango de bits inválido: offset={offset}, length={length}. "
                f"Debe cumplir: 0 <= offset y length > 0 y offset+length <= {self.CELL_SIZE}"
            )

    def __len__(self):
        return self.size

    def __repr__(self):
        return f"RAM(size={self.size} bytes)"


# ==========================================================================
# Pruebas unitarias
# ==========================================================================

class TestRAM(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada prueba: crea una RAM de 64 bytes."""
        self.ram = RAM(64)

    # --- Inicialización ---

    def test_init_default_size(self):
        r = RAM()
        self.assertEqual(len(r), 256)

    def test_init_custom_size(self):
        r = RAM(128)
        self.assertEqual(len(r), 128)

    def test_init_all_zeros(self):
        for i in range(len(self.ram)):
            self.assertEqual(self.ram.read(i), '00000000')

    def test_init_invalid_size(self):
        with self.assertRaises(RAMError):
            RAM(0)
        with self.assertRaises(RAMError):
            RAM(-10)

    # --- Escritura y lectura de byte ---

    def test_write_and_read(self):
        self.ram.write(0, '10110010')
        self.assertEqual(self.ram.read(0), '10110010')

    def test_write_various_addresses(self):
        data = [('00000001', 10), ('11111111', 31), ('01010101', 63)]
        for val, addr in data:
            self.ram.write(addr, val)
        for val, addr in data:
            self.assertEqual(self.ram.read(addr), val)

    def test_overwrite(self):
        self.ram.write(5, '11111111')
        self.ram.write(5, '00000000')
        self.assertEqual(self.ram.read(5), '00000000')

    # --- Validación de límites ---

    def test_read_out_of_bounds(self):
        with self.assertRaises(RAMError):
            self.ram.read(64)
        with self.assertRaises(RAMError):
            self.ram.read(-1)

    def test_write_out_of_bounds(self):
        with self.assertRaises(RAMError):
            self.ram.write(64, '00000000')
        with self.assertRaises(RAMError):
            self.ram.write(-1, '00000000')

    def test_write_invalid_byte_length(self):
        with self.assertRaises(RAMError):
            self.ram.write(0, '1011')      # muy corto
        with self.assertRaises(RAMError):
            self.ram.write(0, '101100101') # muy largo

    def test_write_invalid_byte_chars(self):
        with self.assertRaises(RAMError):
            self.ram.write(0, '1011X010')

    # --- Escritura y lectura por bit ---

    def test_write_bit(self):
        self.ram.write(0, '00000000')
        self.ram.write_bit(0, 3, '1')
        self.assertEqual(self.ram.read(0), '00010000')

    def test_read_bit(self):
        self.ram.write(0, '10110010')
        self.assertEqual(self.ram.read_bit(0, 0), '1')
        self.assertEqual(self.ram.read_bit(0, 1), '0')
        self.assertEqual(self.ram.read_bit(0, 7), '0')

    def test_write_bit_invalid_index(self):
        with self.assertRaises(RAMError):
            self.ram.write_bit(0, 8, '1')
        with self.assertRaises(RAMError):
            self.ram.write_bit(0, -1, '1')

    def test_write_bit_invalid_value(self):
        with self.assertRaises(RAMError):
            self.ram.write_bit(0, 0, '2')

    # --- Lectura de bits parciales ---

    def test_read_bits(self):
        self.ram.write(0, '10110010')
        self.assertEqual(self.ram.read_bits(0, 0, 4), '1011')
        self.assertEqual(self.ram.read_bits(0, 4, 4), '0010')

    def test_read_bits_invalid_range(self):
        with self.assertRaises(RAMError):
            self.ram.read_bits(0, 6, 4)  # 6+4=10 > 8

    # --- Bloque de escritura/lectura ---

    def test_write_and_read_block(self):
        # Simula cargar una instrucción: opcode (8 bits) + parámetro (8 bits)
        self.ram.write_block(0, '0000010110100011')
        self.assertEqual(self.ram.read(0), '00000101')
        self.assertEqual(self.ram.read(1), '10100011')

    def test_write_block_with_spaces(self):
        self.ram.write_block(0, '0000 0101 1010 0011')
        self.assertEqual(self.ram.read(0), '00000101')
        self.assertEqual(self.ram.read(1), '10100011')

    def test_read_block(self):
        self.ram.write(10, '11001100')
        self.ram.write(11, '00110011')
        self.assertEqual(self.ram.read_block(10, 2), '1100110000110011')

    def test_write_block_invalid_length(self):
        with self.assertRaises(RAMError):
            self.ram.write_block(0, '10110')  # no múltiplo de 8

    def test_write_block_out_of_bounds(self):
        with self.assertRaises(RAMError):
            self.ram.write_block(60, '00000000' * 8)  # excede tamaño

    # --- Clear ---

    def test_clear(self):
        self.ram.write(0, '11111111')
        self.ram.write(10, '10101010')
        self.ram.clear()
        self.assertEqual(self.ram.read(0), '00000000')
        self.assertEqual(self.ram.read(10), '00000000')

    # --- repr ---

    def test_repr(self):
        self.assertIn('64', repr(self.ram))


# ==========================================================================
# Demo rápida
# ==========================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("  DEMO - Módulo RAM")
    print("=" * 60)

    # Crear RAM de 32 bytes
    ram = RAM(32)
    print(repr(ram))

    # Cargar instrucciones desde instructions.txt
    def load_instructions(filepath: str) -> list:
        """
        Lee un archivo .txt con un byte (8 bits) por línea.
        Ignora líneas vacías y comentarios que empiecen con '#'.

        Retorna:
            list[str]: Lista de strings binarios de 8 bits.
        """
        instrucciones = []
        with open(filepath, 'r') as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith('#'):  # ignorar vacías y comentarios
                    continue
                instrucciones.append(linea)
        return instrucciones

    instrucciones = load_instructions('data/instructions.txt')
    print(f"\n[+] {len(instrucciones)} bytes cargados desde instructions.txt: {instrucciones}")

    print("[+] Cargando instrucciones en RAM desde dirección 0x0000...")
    for i, byte in enumerate(instrucciones):
        ram.write(i, byte)

    print(f"\n[+] Lectura 0x0010: {ram.read(16)}")
    print(f"[+] Bit 0 de 0x0000: {ram.read_bit(0, 0)}")
    print(f"[+] Bits [0:4] de 0x0000: {ram.read_bits(0, 0, 4)}")
    print(f"[+] Bloque 0x0000-0x0002 (3 bytes): {ram.read_block(0, 3)}")

    print("\n[+] Mapa de memoria (primeras 2 filas):")
    ram.display(0, 32)

    print("\n" + "=" * 60)
    print("  EJECUTANDO PRUEBAS UNITARIAS")
    print("=" * 60)
    unittest.main(argv=[''], verbosity=2, exit=False)
