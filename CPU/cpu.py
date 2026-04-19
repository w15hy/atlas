import time

from CPU.buses import BusInterface
from CPU.instructions import decode
from CPU.ram import RAM
from CPU.registers import Registers

# pre(4 bits) → cuántos bits tiene el opcode
_PRE_OPCODE_BITS = {
    "0000": 6,  # F4 control
    "0001": 10,  # F1 reg/inm
    "0010": 8,  # F2 memoria
    "0011": 10,  # F3 saltos
}


class CPU:
    def __init__(self, ram, interrupt_table=None):
        self.ram = ram
        self.reg = Registers()
        self.buses = BusInterface()  # ← BUSES EXPLÍCITOS
        self.running = True
        self.step_count = 0
        self.interrupt_table = interrupt_table or {}

    # ------------------------------------------------------------------
    # Ciclo fetch → decode → execute → update PC
    # ------------------------------------------------------------------

    def step(self):
        # FETCH — siempre 64 bits (8 bytes) usando BUSES EXPLÍCITOS
        # 1️⃣ Coloca PC en AddressBus
        self.buses.address_bus.set_address(self.reg.PC)

        # 2️⃣ Activa READ en ControlBus
        self.buses.control_bus.set_read(True)
        self.buses.control_bus.set_enable(True)

        # 3️⃣ Lee 8 bytes de memoria a través del DataBus
        instr = self.ram.read_block(self.reg.PC, 8)
        self.buses.data_bus.write_data(int(instr, 2))  # Dato ahora está en DataBus

        # 4️⃣ Desactiva READ (ciclo de lectura completo)
        self.buses.control_bus.set_read(False)

        # Carga en IR
        self.reg.IR = instr

        # DECODE
        func = decode(instr)

        # EXECUTE
        # Si la función devuelve True ya actualizó el PC (salto)
        jumped = func(self, self.reg, self.ram)

        # UPDATE PC
        if not jumped:
            self.reg.increment_PC(8)

        self.step_count += 1

    # ------------------------------------------------------------------
    # Acceso explícito a memoria a través de BUSES
    # ------------------------------------------------------------------

    def read_memory_via_bus(self, address: int, num_bytes: int = 8) -> str:
        """
        Lee datos de memoria usando BUSES explícitos.

        Ciclo de lectura:
        1. Coloca dirección en AddressBus
        2. Activa READ en ControlBus
        3. Lee datos de DataBus
        """
        # 1️⃣ Poner dirección en AddressBus
        self.buses.address_bus.set_address(address)

        # 2️⃣ Activar READ en ControlBus
        self.buses.control_bus.set_read(True)
        self.buses.control_bus.set_enable(True)

        # 3️⃣ Leer de RAM
        data = self.ram.read_block(address, num_bytes)

        # 4️⃣ Poner dato en DataBus
        self.buses.data_bus.write_data(int(data, 2))

        # 5️⃣ Desactivar READ
        self.buses.control_bus.set_read(False)

        return data

    def write_memory_via_bus(self, address: int, data: str) -> None:
        """
        Escribe datos en memoria usando BUSES explícitos.

        Ciclo de escritura:
        1. Coloca dirección en AddressBus
        2. Coloca datos en DataBus
        3. Activa WRITE en ControlBus
        """
        # 1️⃣ Poner dirección en AddressBus
        self.buses.address_bus.set_address(address)

        # 2️⃣ Poner dato en DataBus
        self.buses.data_bus.write_data(int(data, 2))

        # 3️⃣ Activar WRITE en ControlBus
        self.buses.control_bus.set_write(True)
        self.buses.control_bus.set_enable(True)

        # 4️⃣ Escribir en RAM
        self.ram.write(address, data)

        # 5️⃣ Desactivar WRITE
        self.buses.control_bus.set_write(False)

    # ------------------------------------------------------------------
    # Display de estado
    # ------------------------------------------------------------------

    def _instr_name(self):
        """Nombre legible de la instrucción en IR."""
        from CPU.instructions import DECODE_TABLE

        ir = self.reg.IR
        pre = ir[0:4]
        if pre not in DECODE_TABLE:
            return f"UNKNOWN(pre={pre})"
        opcode_bits, tabla = DECODE_TABLE[pre]
        opcode = int(ir[4 : 4 + opcode_bits], 2)
        func = tabla.get(opcode)
        return func.__name__.upper() if func else f"UNKNOWN(op={opcode})"

    def display_state(self):
        print("\n" + "=" * 80)
        print(
            f"  PASO #{self.step_count}  |  PC = 0x{self.reg.PC:08X}  |  IR = {self.reg.IR}"
        )
        print(f"  INSTRUCCION: {self._instr_name()}")
        print("=" * 80)

        # 🚌 ESTADO DE LOS BUSES
        print("\n  BUSES (Address | Data | Control):")
        print(f"    Address Bus: 0x{self.buses.address_bus.get_address():08X}")
        print(f"    Data Bus:    0x{self.buses.data_bus.read_data():016X}")
        signals = self.buses.control_bus.get_signals()
        signals_str = " | ".join(f"{k}={'1' if v else '0'}" for k, v in signals.items())
        print(f"    Control Bus: [{signals_str}]")

        print("\n  REGISTROS GENERALES:")
        for i in range(16):
            val = self.reg.get_reg(i)
            print(f"    R{i:2d} = 0x{val:08X}  ({val:10d})  [{val:032b}]")

        print("\n  REGISTROS ESPECIALES:")
        print(f"    PC = 0x{self.reg.PC:08X}  ({self.reg.PC})")
        print(f"    SP = 0x{self.reg.SP:08X}  ({self.reg.SP})")

        flags = self.reg.get_flags()
        flags_str = " | ".join(f"{k}={'1' if v else '0'}" for k, v in flags.items())
        print(f"\n  FLAGS: {flags_str}")

        print("\n  MEMORIA (primeras 8 palabras desde 0):")
        self.ram.display(0, 64)
        print("=" * 80 + "\n")

    # ------------------------------------------------------------------
    # Modos de ejecución
    # ------------------------------------------------------------------

    def run_all(self):
        """Ejecuta el programa completo sin parar."""
        print("\n[*] Modo EJECUCIÓN COMPLETA\n")
        self.step_count = 0
        while self.running:
            self.step()
        self.reg.show()
        print(f"\n[OK] Terminado tras {self.step_count} instrucciones.")

    def run_step_manual(self):
        """Paso a paso manual (Enter = siguiente, q = salir)."""
        print("\n[*] Modo DEBUG — PASO A PASO MANUAL")
        print("[*] Enter = siguiente paso | q = salir\n")
        self.step_count = 0
        while self.running:
            self.display_state()
            cmd = input("[DEBUG] > ").strip().lower()
            if cmd == "q":
                print("[*] Ejecución pausada.")
                break
            self.step()
        self.reg.show()
        print(f"\n[OK] {self.step_count} instrucciones ejecutadas.")

    def run_step_timed(self, delay: float = 1.0):
        """Paso a paso automático con delay configurable."""
        print(f"\n[*] Modo DEBUG — TIMED  (delay={delay}s)\n")
        self.step_count = 0
        while self.running:
            self.display_state()
            try:
                time.sleep(delay)
            except KeyboardInterrupt:
                print("\n[*] Interrumpido por el usuario.")
                break
            self.step()
        print(f"\n[OK] {self.step_count} instrucciones ejecutadas.")
