# ============================================================================
# stdlib/gcd_lib.asm — Subrutina GCD por restas sucesivas
# ============================================================================
# Entrada: R0 = a,  R1 = b
# Salida:  R0 = gcd(a, b)
# Para uso con #include (no requiere .global/.extern)
# ============================================================================
GCD:
GCD_LOOP:
    cmp R0, R1
    jz GCD_END
    jg GCD_A_MAYOR
    sub R1, R0              # B > A: B = B - A
    jmp GCD_LOOP
GCD_A_MAYOR:
    sub R0, R1              # A > B: A = A - B
    jmp GCD_LOOP
GCD_END:
    ret
