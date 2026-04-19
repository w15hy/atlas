# =============================================================================
# lib_factorial.asm — Factorial iterativo
# =============================================================================
# Entrada:  R0 = n
# Salida:   R0 = n!
# Scratch:  R5 (acumulador), R2 (constante 1)
# =============================================================================

.global FACTORIAL

FACTORIAL:
    mov  R5, 1          # acumulador = 1
    mov  R2, 1          # constante 1
FACT_LOOP:
    cmp  R0, R2         # n == 1?
    jz   FACT_END
    mul  R5, R0         # acum *= n
    dec  R0             # n--
    jmp  FACT_LOOP
FACT_END:
    mov  R0, R5         # resultado en R0
    ret
