# ============================================================================
# stdlib/power_lib.asm — Exponenciación rápida (power by squaring)
# ============================================================================
# Entrada: R0 = base,  R1 = exponente
# Salida:  R0 = base^exponente
# Modifica: R0, R1, R2, R3, R4, R5
# Para uso con #include (no requiere .global/.extern)
# ============================================================================
FAST_POWER:
    mov R2, 1               # resultado = 1
    mov R4, 0               # constante 0
    mov R5, 1               # constante 1
FPOWER_LOOP:
    cmp R1, R4              # exp == 0?
    jz FPOWER_END
    mov R3, R1
    and R3, R5              # R3 = exp & 1
    cmp R3, R4
    jz FPOWER_SQUARE
    mul R2, R0              # resultado *= base
FPOWER_SQUARE:
    mul R0, R0              # base *= base
    shr R1                  # exp >>= 1
    jmp FPOWER_LOOP
FPOWER_END:
    mov R0, R2              # resultado en R0
    ret
