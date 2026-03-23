import CPU.registers as reg


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
    r = reg.Registers()

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
    r.PC = reg.ADDR_MASK
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
    r2 = reg.Registers(sp_init=0x10)
    test("SP init = 0x10", r2.SP == 0x10)
    r2.push_SP()
    test("push_SP 0x10→0x0F", r2.SP == 0x0F)
    r2.pop_SP()
    test("pop_SP  0x0F→0x10", r2.SP == 0x10)

    # ── FLAGS ────────────────────────────────────────────────────────
    r3 = reg.Registers()
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
    r4 = reg.Registers()
    r4.set_reg(3, 99)
    r4.PC = 0x50
    r4.flag_Z = True
    r4.reset()
    test("reset R3=0", r4.get_reg(3) == 0)
    test("reset PC=0", r4.PC == 0)
    test("reset Z=False", not r4.flag_Z)
    test("reset SP=SP_INIT", r4.SP == reg.SP_INIT)

    # ── Visual ───────────────────────────────────────────────────────
    print("\nPrueba visual show():")
    demo = reg.Registers()
    demo.set_reg(0, 42)
    demo.PC = 0x1A
    demo.IR = "00001111" + "00000001" + "00000010"
    demo.SP = reg.SP_INIT - 1
    demo.flag_Z = True
    demo.flag_C = True
    demo.show()

    print(f"\nResultado: {passed} pasadas | {failed} fallidas.")
    return failed == 0


if __name__ == "__main__":
    ok = _run_tests()
    raise SystemExit(0 if ok else 1)
