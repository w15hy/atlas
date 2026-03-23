import time

from CPU.instructions import decode, params_format_1
from CPU.ram import RAM
from CPU.registers import Registers

# pre(4 bits) → cuántos bits tiene el opcode
_PRE_OPCODE_BITS = {
    "0000": 6,   # F4 control
    "0001": 10,  # F1 reg/inm
    "0010": 8,   # F2 memoria
    "0011": 10,  # F3 saltos
}


class CPU:
    def __init__(self, ram, interrupt_table=None):
        self.ram             = ram
        self.reg             = Registers()
        self.running         = True
        self.step_count      = 0
        self.interrupt_table = interrupt_table or {}

    # ------------------------------------------------------------------
    # Ciclo fetch → decode → execute → update PC
    # ------------------------------------------------------------------

    def step(self):
        # FETCH — siempre 64 bits (8 bytes)
        instr      = self.ram.read_block(self.reg.PC, 8)
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
    # Display de estado
    # ------------------------------------------------------------------

    def _instr_name(self):
        """Nombre legible de la instrucción en IR."""
        from CPU.instructions import DECODE_TABLE
        ir  = self.reg.IR
        pre = ir[0:4]
        if pre not in DECODE_TABLE:
            return f"UNKNOWN(pre={pre})"
        opcode_bits, tabla = DECODE_TABLE[pre]
        opcode = int(ir[4: 4 + opcode_bits], 2)
        func   = tabla.get(opcode)
        return func.__name__.upper() if func else f"UNKNOWN(op={opcode})"

    def display_state(self):
        print("\n" + "=" * 80)
        print(
            f"  PASO #{self.step_count}  |  PC = 0x{self.reg.PC:08X}  |  IR = {self.reg.IR}"
        )
        print(f"  INSTRUCCION: {self._instr_name()}")
        print("=" * 80)

        print("\n  REGISTROS GENERALES:")
        for i in range(16):
            val = self.reg.get_reg(i)
            print(f"    R{i:2d} = 0x{val:08X}  ({val:10d})  [{val:032b}]")

        print("\n  REGISTROS ESPECIALES:")
        print(f"    PC = 0x{self.reg.PC:08X}  ({self.reg.PC})")
        print(f"    SP = 0x{self.reg.SP:08X}  ({self.reg.SP})")

        flags     = self.reg.get_flags()
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
