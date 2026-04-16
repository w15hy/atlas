# ============================================================================
# Programa B (preprocesador) — Matmul 3×2 × 2×4 con #define y #include
# ============================================================================
# Usa stdlib/vecmat.asm (MAT_INIT, MAT_SET, MAT_MUL, MAT_GET)
# Demuestra uso de #define para constantes y #include para bibliotecas
# ============================================================================
.org 3700

#define ROWS_A    3
#define COLS_A    2
#define COLS_B    4
#define BASE_A    1028
#define BASE_B    1036
#define BASE_C    20455

    jmp MAIN

#include <stdlib/vecmat.asm>

MAIN:
    # ── Inicializar A (3×2) ──────────────────────────────────────────
    mov R0, BASE_A
    mov R1, ROWS_A
    mov R2, COLS_A
    call MAT_INIT

    # A[0][0]=1  A[0][1]=2  A[1][0]=3  A[1][1]=4  A[2][0]=5  A[2][1]=6
    mov R0, BASE_A
    mov R1, 0
    mov R2, 0
    mov R3, 1
    call MAT_SET
    mov R0, BASE_A
    mov R1, 0
    mov R2, 1
    mov R3, 2
    call MAT_SET
    mov R0, BASE_A
    mov R1, 1
    mov R2, 0
    mov R3, 3
    call MAT_SET
    mov R0, BASE_A
    mov R1, 1
    mov R2, 1
    mov R3, 4
    call MAT_SET
    mov R0, BASE_A
    mov R1, 2
    mov R2, 0
    mov R3, 5
    call MAT_SET
    mov R0, BASE_A
    mov R1, 2
    mov R2, 1
    mov R3, 6
    call MAT_SET

    # ── Inicializar B (2×4) ──────────────────────────────────────────
    mov R0, BASE_B
    mov R1, COLS_A
    mov R2, COLS_B
    call MAT_INIT

    mov R0, BASE_B
    mov R1, 0
    mov R2, 0
    mov R3, 1
    call MAT_SET
    mov R0, BASE_B
    mov R1, 0
    mov R2, 1
    mov R3, 2
    call MAT_SET
    mov R0, BASE_B
    mov R1, 0
    mov R2, 2
    mov R3, 3
    call MAT_SET
    mov R0, BASE_B
    mov R1, 0
    mov R2, 3
    mov R3, 4
    call MAT_SET
    mov R0, BASE_B
    mov R1, 1
    mov R2, 0
    mov R3, 5
    call MAT_SET
    mov R0, BASE_B
    mov R1, 1
    mov R2, 1
    mov R3, 6
    call MAT_SET
    mov R0, BASE_B
    mov R1, 1
    mov R2, 2
    mov R3, 7
    call MAT_SET
    mov R0, BASE_B
    mov R1, 1
    mov R2, 3
    mov R3, 8
    call MAT_SET

    # ── Multiplicar C = A × B ────────────────────────────────────────
    mov R0, BASE_A
    mov R1, BASE_B
    mov R2, BASE_C
    call MAT_MUL

    # ── Imprimir resultado ───────────────────────────────────────────
    mov R8, 0
    mov R9, ROWS_A
PRINT_I:
    cmp R8, R9
    jge DONE
    mov R10, 0
    mov R11, COLS_B
PRINT_J:
    cmp R10, R11
    jge PRINT_NEXT_I
    mov R0, BASE_C
    mov R1, R8
    mov R2, R10
    call MAT_GET
    out R0
    inc R10
    jmp PRINT_J
PRINT_NEXT_I:
    inc R8
    jmp PRINT_I

DONE:
    halt
