# ── Constantes de arquitectura ──────────────────────────────────────────
REG_BITS = 8
ADDR_BITS = 32
NUM_REGS = 16
SP_INIT = (1 << ADDR_BITS) - 1

REG_MASK = (1 << REG_BITS) - 1
ADDR_MASK = (1 << ADDR_BITS) - 1


class Registers:
    def __init__(self, sp_init: int = SP_INIT):
        self._general: list = [0] * NUM_REGS
        self._PC: int = 0
        self._IR: str = "00000000"  # opcode nulo por defecto
        self._SP: int = sp_init & ADDR_MASK
        self._flag_Z = self._flag_C = self._flag_N = self._flag_V = False

    # ── Validaciones ────────────────────────────────────────────────────

    @staticmethod
    def _chk_reg(i):
        if not (0 <= i < NUM_REGS):
            raise IndexError(
                f"Índice de registro inválido: {i}. Rango: 0..{NUM_REGS - 1}"
            )

    @staticmethod
    def _chk_bin(s, name="valor"):
        if not isinstance(s, str) or not all(c in "01" for c in s):
            raise ValueError(f"{name} debe ser cadena de '0'/'1'. Recibido: {s!r}")

    # ── Registros generales ─────────────────────────────────────────────

    def get_reg(self, index: int) -> int:
        self._chk_reg(index)
        return self._general[index]

    def get_reg_bin(self, index: int) -> str:
        """Valor del registro como cadena de 8 bits."""
        self._chk_reg(index)
        return format(self._general[index], "08b")

    def set_reg(self, index: int, value) -> None:
        """Acepta int o cadena binaria; trunca a 8 bits."""
        self._chk_reg(index)
        if isinstance(value, str):
            self._chk_bin(value, f"R{index}")
            value = int(value, 2)
        self._general[index] = int(value) & REG_MASK

    # ── PC ──────────────────────────────────────────────────────────────

    @property
    def PC(self) -> int:
        return self._PC

    @PC.setter
    def PC(self, value) -> None:
        if isinstance(value, str):
            self._chk_bin(value, "PC")
            value = int(value, 2)
        self._PC = int(value) & ADDR_MASK

    def PC_bin(self, width: int = ADDR_BITS) -> str:
        return format(self._PC, f"0{width}b")

    def increment_PC(self, step: int = 1) -> None:
        """Avanza el PC `step` posiciones (con wrap-around)."""
        self._PC = (self._PC + step) & ADDR_MASK

    @property
    def IR(self) -> str:
        return self._IR

    @IR.setter
    def IR(self, value: str) -> None:
        self._chk_bin(value, "IR")
        self._IR = value

    def IR_opcode(self) -> str:
        """Extrae los primeros 8 bits (opcode)."""
        return self._IR[:8]

    def IR_params(self) -> str:
        """Extrae todo lo que sigue al opcode (parámetros crudos)."""
        return self._IR[8:]

    @property
    def SP(self) -> int:
        return self._SP

    @SP.setter
    def SP(self, value) -> None:
        if isinstance(value, str):
            self._chk_bin(value, "SP")
            value = int(value, 2)
        self._SP = int(value) & ADDR_MASK

    def SP_bin(self, width: int = ADDR_BITS) -> str:
        return format(self._SP, f"0{width}b")

    def push_SP(self, step: int = 1) -> None:
        self._SP = (self._SP - step) & ADDR_MASK

    def pop_SP(self, step: int = 1) -> None:
        self._SP = (self._SP + step) & ADDR_MASK

    @property
    def flag_Z(self) -> bool:
        return self._flag_Z

    @flag_Z.setter
    def flag_Z(self, v):
        self._flag_Z = bool(v)

    @property
    def flag_C(self) -> bool:
        return self._flag_C

    @flag_C.setter
    def flag_C(self, v):
        self._flag_C = bool(v)

    @property
    def flag_N(self) -> bool:
        return self._flag_N

    @flag_N.setter
    def flag_N(self, v):
        self._flag_N = bool(v)

    @property
    def flag_V(self) -> bool:
        return self._flag_V

    @flag_V.setter
    def flag_V(self, v):
        self._flag_V = bool(v)

    def update_flags(
        self,
        result_raw: int,
        operand_a: int = 0,
        operand_b: int = 0,
        operation: str = "add",
    ) -> None:

        r8 = result_raw & REG_MASK
        msb = 1 << (REG_BITS - 1)  # 0x80

        self._flag_Z = r8 == 0
        self._flag_N = bool(r8 & msb)

        if operation == "add":
            self._flag_C = result_raw > REG_MASK
            sa, sb, sr = bool(operand_a & msb), bool(operand_b & msb), bool(r8 & msb)
            self._flag_V = (sa == sb) and (sa != sr)

        elif operation == "sub":
            self._flag_C = result_raw < 0
            sa, sb, sr = bool(operand_a & msb), bool(operand_b & msb), bool(r8 & msb)
            self._flag_V = (sa != sb) and (sb == sr)

        else:  # logic / shift
            self._flag_C = False
            self._flag_V = False

    def get_flags(self) -> dict:
        return {
            "Z": self._flag_Z,
            "C": self._flag_C,
            "N": self._flag_N,
            "V": self._flag_V,
        }

    def set_flags_from_dict(self, d: dict) -> None:
        """Permite actualizar flags desde un dict (lo usa el módulo execute)."""
        if "Z" in d:
            self._flag_Z = bool(d["Z"])
        if "C" in d:
            self._flag_C = bool(d["C"])
        if "N" in d:
            self._flag_N = bool(d["N"])
        if "V" in d:
            self._flag_V = bool(d["V"])

    def clear_flags(self) -> None:
        self._flag_Z = self._flag_C = self._flag_N = self._flag_V = False

    # ── Reset ────────────────────────────────────────────────────────────

    def reset(self, sp_init: int = SP_INIT) -> None:
        """Reinicia todos los registros y banderas al estado inicial."""
        self._general = [0] * NUM_REGS
        self._PC = 0
        self._IR = "00000000"
        self._SP = sp_init & ADDR_MASK
        self.clear_flags()

    # ── Visualización ────────────────────────────────────────────────────

    def show(self) -> None:
        W = 60
        print("=" * W)
        print("  ESTADO DE REGISTROS Y FLAGS")
        print("=" * W)
        for i, v in enumerate(self._general):
            print(f"  R{i}  = 0x{v:02X}  ({v:3d})  [{v:08b}]")
        print("-" * W)
        print(f"  PC   = 0x{self._PC:08X}  ({self._PC})")
        print(f"  IR   = {self._IR}")
        print(
            f"         opcode={self.IR_opcode()}  params={self.IR_params() or '(ninguno)'}"
        )
        print(f"  SP   = 0x{self._SP:08X}  ({self._SP})")
        print("-" * W)
        f = self.get_flags()
        print("  FLAGS: " + "  ".join(f"{k}={'1' if v else '0'}" for k, v in f.items()))
        print("=" * W)

    def __repr__(self) -> str:
        regs = ", ".join(f"R{i}=0x{v:02X}" for i, v in enumerate(self._general))
        f = self.get_flags()
        fs = "".join(k if v else k.lower() for k, v in f.items())
        ir_short = self._IR[:16] + ("..." if len(self._IR) > 16 else "")
        return (
            f"Registers({regs}, PC=0x{self._PC:X}, "
            f"IR={ir_short}, SP=0x{self._SP:X}, FLAGS={fs})"
        )


# Pruebas unitarias básicas para validar el funcionamiento de la clase Registers.
def _run_tests():
    passed = failed = 0

    def test(name, cond):
        nonlocal passed, failed
        symbol = "[PASS]" if cond else "[FAIL]"
        print(f"  {symbol} {name}")
        if cond:
            passed += 1
        else:
            failed += 1

    print("\n─── Pruebas unitarias de registers.py ───\n")
    r = Registers()

    # ── Registros generales ──────────────────────────────────────────
    r.set_reg(0, 0x10)
    test("set/get R0 = 0x10", r.get_reg(0) == 0x10)

    r.set_reg(1, "11001100")
    test("set_reg desde binario R1 = 0xCC", r.get_reg(1) == 0xCC)
    test("get_reg_bin R1 = '11001100'", r.get_reg_bin(1) == "11001100")

    r.set_reg(2, 0x1FF)
    test("Truncado 0x1FF → 0xFF", r.get_reg(2) == 0xFF)

    try:
        r.set_reg(8, 0)
        test("Índice 8 lanza IndexError", False)
    except IndexError:
        test("Índice 8 lanza IndexError", True)

    # ── PC ───────────────────────────────────────────────────────────
    r.PC = 0x20
    test("PC = 0x20", r.PC == 0x20)
    r.increment_PC(3)
    test("increment_PC(3) → 0x23", r.PC == 0x23)
    r.PC = ADDR_MASK
    r.increment_PC()
    test("PC wrap-around → 0", r.PC == 0)
    r.PC = "000000000000000000000000000000000000000000101010"
    test("PC desde cadena binaria = 42", r.PC == 42)

    # ── IR ───────────────────────────────────────────────────────────
    instr = "00001111" + "00000001" + "00000010"  # ADD R1, R2 (formato 1)
    r.IR = instr
    test("IR guarda instrucción completa", r.IR == instr)
    test("IR_opcode() = '00001111'", r.IR_opcode() == "00001111")
    test("IR_params() = parámetros sin opcode", r.IR_params() == "0000000100000010")

    try:
        r.IR = "00X1"
        test("IR inválido lanza ValueError", False)
    except ValueError:
        test("IR inválido lanza ValueError", True)

    # Instrucción formato 5 (JMP con dirección de 48 bits)
    addr48 = format(0xABCDEF012345, "048b")
    r.IR = "00100011" + addr48
    test("IR formato 5: 56 bits totales", len(r.IR) == 56)
    test("IR_params() devuelve 48 bits de dirección", r.IR_params() == addr48)

    # ── Compatibilidad con get_params() del compañero ────────────────
    # Formato 1: slices (0,8) y (8,None) sobre IR_params()
    r.IR = "00000101" + "00000011" + "00000101"  # MOV R3, R5
    p = r.IR_params()
    test("get_params fmt1: p[0:8]='00000011'", p[0:8] == "00000011")
    test("get_params fmt1: p[8:]='00000101'", p[8:] == "00000101")

    # Formato 4: slice (0,8) sobre IR_params()
    r.IR = "00010100" + "00000010"  # INC R2
    p = r.IR_params()
    test("get_params fmt4: p[0:8]='00000010'", p[0:8] == "00000010")

    # ── SP ───────────────────────────────────────────────────────────
    r2 = Registers(sp_init=0x10)
    test("SP init = 0x10", r2.SP == 0x10)
    r2.push_SP()
    test("push_SP 0x10→0x0F", r2.SP == 0x0F)
    r2.pop_SP()
    test("pop_SP  0x0F→0x10", r2.SP == 0x10)

    # ── FLAGS ────────────────────────────────────────────────────────
    r3 = Registers()
    r3.update_flags(0x05, 0x03, 0x02, "add")
    test("ADD 3+2: Z=0 C=0 N=0", not r3.flag_Z and not r3.flag_C and not r3.flag_N)

    r3.update_flags(0x100, 0xFF, 0x01, "add")
    test("ADD FF+01: Carry=1", r3.flag_C)
    test("ADD FF+01: Zero=1", r3.flag_Z)

    r3.update_flags(0x80, 0x40, 0x40, "add")
    test("ADD 40+40: Overflow=1", r3.flag_V)
    test("ADD 40+40: Negative=1", r3.flag_N)

    r3.update_flags(0, 5, 5, "sub")
    test("SUB 5-5: Zero=1", r3.flag_Z)

    r3.update_flags(-1, 0, 1, "sub")
    test("SUB 0-1: Carry=1", r3.flag_C)

    r3.update_flags(0, operation="logic")
    test("Logic 0: Z=1 C=0 V=0", r3.flag_Z and not r3.flag_C and not r3.flag_V)

    r3.set_flags_from_dict({"Z": False, "C": True})
    test("set_flags_from_dict Z=0 C=1", not r3.flag_Z and r3.flag_C)

    r3.clear_flags()
    test("clear_flags: todos False", not any(r3.get_flags().values()))

    # ── Reset ────────────────────────────────────────────────────────
    r4 = Registers()
    r4.set_reg(3, 99)
    r4.PC = 0x50
    r4.flag_Z = True
    r4.reset()
    test("reset R3=0", r4.get_reg(3) == 0)
    test("reset PC=0", r4.PC == 0)
    test("reset Z=False", not r4.flag_Z)
    test("reset SP=SP_INIT", r4.SP == SP_INIT)

    # ── Visual ───────────────────────────────────────────────────────
    print("\nPrueba visual show():")
    demo = Registers()
    demo.set_reg(0, 42)
    demo.PC = 0x1A
    demo.IR = "00001111" + "00000001" + "00000010"
    demo.SP = SP_INIT - 1
    demo.flag_Z = True
    demo.flag_C = True
    demo.show()

    print(f"\nResultado: {passed} pasadas | {failed} fallidas.")
    return failed == 0


if __name__ == "__main__":
    ok = _run_tests()
    raise SystemExit(0 if ok else 1)
