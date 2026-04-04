# =============================================================================
# lib_euclides.asm — GCD por restas sucesivas (Euclides)
# =============================================================================
# Entrada:  R0 = a, R1 = b
# Salida:   R0 = gcd(a, b)
# =============================================================================

.global GCD

GCD:
GCD_LOOP:
    cmp  R0, R1
    jz   GCD_END
    jn   GCD_B_MAYOR
GCD_A_MAYOR:
    sub  R0, R1
    jmp  GCD_LOOP
GCD_B_MAYOR:
    sub  R1, R0
    jmp  GCD_LOOP
GCD_END:
    ret
