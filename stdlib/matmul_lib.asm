# ============================================================================
# stdlib/matmul_lib.asm — Multiplicación de matrices (enteros, row-major)
# ============================================================================
# Entrada (valores en registros, no en stack):
#   R10 = dirección base de A
#   R11 = dirección base de B
#   R12 = dirección base de C (resultado)
#   R13 = ROWS_A
#   R14 = COLS_A (= ROWS_B)
#   R15 = COLS_B
#
# Salida:  C[i][j] escrito a partir de dirección R12
#          Cada elemento es de 8 bytes (64 bits)
# Modifica: R0-R9
# Para uso con #include (no requiere .global/.extern)
# ============================================================================
MATMUL:
    push R10
    push R11
    push R12
    push R13
    push R14
    push R15

    mov R0, 0               # i = 0
MATMUL_I:
    cmp R0, R13             # i < ROWS_A?
    jge MATMUL_DONE

    mov R1, 0               # j = 0
MATMUL_J:
    cmp R1, R15             # j < COLS_B?
    jge MATMUL_NEXT_I

    mov R3, 0               # acumulador = 0
    mov R2, 0               # k = 0
MATMUL_K:
    cmp R2, R14             # k < COLS_A?
    jge MATMUL_STORE

    # addr_A = R10 + (i * COLS_A + k) * 8
    mov R4, R0
    mul R4, R14
    add R4, R2
    mov R5, 8
    mul R4, R5
    add R4, R10
    loadw R6, R4            # R6 = A[i][k]

    # addr_B = R11 + (k * COLS_B + j) * 8
    mov R4, R2
    mul R4, R15
    add R4, R1
    mul R4, R5
    add R4, R11
    loadw R7, R4            # R7 = B[k][j]

    mul R6, R7
    add R3, R6              # acum += A[i][k] * B[k][j]

    inc R2
    jmp MATMUL_K

MATMUL_STORE:
    # addr_C = R12 + (i * COLS_B + j) * 8
    mov R4, R0
    mul R4, R15
    add R4, R1
    mov R5, 8
    mul R4, R5
    add R4, R12
    storew R3, R4           # C[i][j] = acum

    inc R1
    jmp MATMUL_J

MATMUL_NEXT_I:
    inc R0
    jmp MATMUL_I

MATMUL_DONE:
    pop R15
    pop R14
    pop R13
    pop R12
    pop R11
    pop R10
    ret
