# ============================================================================
# Programa B — Multiplicación de matrices 3×2 × 2×4  (usa stdlib/vecmat.asm)
# ============================================================================
# Matrices A(3×2) y B(2×4) almacenadas a partir de dirección 1028
# Matriz resultado C(3×4) almacenada a partir de dirección 20455
# Código binario a partir de posición 3700
# Elementos de 1 byte (layout vecmat: cabecera rows,cols + datos row-major)
# ============================================================================
# A = [[1,2],[3,4],[5,6]]         (cabecera 2 bytes + 6 elem en 1028..1035)
# B = [[1,2,3,4],[5,6,7,8]]      (cabecera 2 bytes + 8 elem en 1036..1045)
# C esperado:
#   [[11,14,17,20],[23,30,37,44],[35,46,57,68]]
# ============================================================================
.org 3700

    jmp START

#include <stdlib/vecmat.asm>

START:
# ── Inicializar matriz A (3×2) en 1028 ──────────────────────────────────
    mov R0, 1028
    mov R1, 3
    mov R2, 2
    call MAT_INIT               # cabecera A: rows=3, cols=2

    # A[0][0]=1  A[0][1]=2  A[1][0]=3  A[1][1]=4  A[2][0]=5  A[2][1]=6
    mov R0, 1028
    mov R1, 0
    mov R2, 0
    mov R3, 1
    call MAT_SET
    mov R0, 1028
    mov R1, 0
    mov R2, 1
    mov R3, 2
    call MAT_SET
    mov R0, 1028
    mov R1, 1
    mov R2, 0
    mov R3, 3
    call MAT_SET
    mov R0, 1028
    mov R1, 1
    mov R2, 1
    mov R3, 4
    call MAT_SET
    mov R0, 1028
    mov R1, 2
    mov R2, 0
    mov R3, 5
    call MAT_SET
    mov R0, 1028
    mov R1, 2
    mov R2, 1
    mov R3, 6
    call MAT_SET

# ── Inicializar matriz B (2×4) en 1036 ──────────────────────────────────
    mov R0, 1036
    mov R1, 2
    mov R2, 4
    call MAT_INIT               # cabecera B: rows=2, cols=4

    # B[0][0..3] = 1,2,3,4   B[1][0..3] = 5,6,7,8
    mov R0, 1036
    mov R1, 0
    mov R2, 0
    mov R3, 1
    call MAT_SET
    mov R0, 1036
    mov R1, 0
    mov R2, 1
    mov R3, 2
    call MAT_SET
    mov R0, 1036
    mov R1, 0
    mov R2, 2
    mov R3, 3
    call MAT_SET
    mov R0, 1036
    mov R1, 0
    mov R2, 3
    mov R3, 4
    call MAT_SET
    mov R0, 1036
    mov R1, 1
    mov R2, 0
    mov R3, 5
    call MAT_SET
    mov R0, 1036
    mov R1, 1
    mov R2, 1
    mov R3, 6
    call MAT_SET
    mov R0, 1036
    mov R1, 1
    mov R2, 2
    mov R3, 7
    call MAT_SET
    mov R0, 1036
    mov R1, 1
    mov R2, 3
    mov R3, 8
    call MAT_SET

# ── Multiplicar C = A × B ───────────────────────────────────────────────
    mov R0, 1028                # base_A
    mov R1, 1036                # base_B
    mov R2, 20455               # base_C
    call MAT_MUL

# ── Imprimir resultado: recorrer C ──────────────────────────────────────
    mov R8, 0                   # i = 0
    mov R9, 3                   # rows_C
PRINT_I:
    cmp R8, R9
    jge DONE
    mov R10, 0                  # j = 0
    mov R11, 4                  # cols_C
PRINT_J:
    cmp R10, R11
    jge PRINT_NEXT_I
    mov R0, 20455
    mov R1, R8
    mov R2, R10
    call MAT_GET                # R0 = C[i][j]
    out R0
    inc R10
    jmp PRINT_J
PRINT_NEXT_I:
    inc R8
    jmp PRINT_I

DONE:
    halt
