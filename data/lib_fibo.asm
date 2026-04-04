# =============================================================================
# lib_fibo.asm — Fibonacci iterativo
# =============================================================================
# Entrada:  R0 = n
# Salida:   R0 = fib(n)
# Scratch:  R1, R2, R3, R4
# =============================================================================

.global FIBONACCI

FIBONACCI:
    mov  R1, 0          # F(0)
    mov  R2, 1          # F(1)
    mov  R4, 0          # constante 0
    cmp  R0, R4         # n == 0?
    jz   FIB_END
FIB_LOOP:
    mov  R3, R2         # temp = F(i+1)
    add  R2, R1         # F(i+2) = F(i+1) + F(i)
    mov  R1, R3         # F(i) = viejo F(i+1)
    dec  R0
    cmp  R0, R4         # n == 0?
    jne  FIB_LOOP
FIB_END:
    mov  R0, R1         # resultado en R0
    ret
