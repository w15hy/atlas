# ── Constantes de arquitectura ──────────────────────────────────────────
REG_BITS = 64
ADDR_BITS = 32
NUM_REGS = 16

SP_INIT = 60000  # Pila comienza en zona alta de RAM (RAM=65536 bytes)
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
