# ============================================================================
# Programa D — Demostración integral: GCD + Fast Power + Matrix Multiply
# ============================================================================
# Usa las 3 bibliotecas existentes mediante #include:
#   - stdlib/gcd_lib.asm      (GCD por restas sucesivas)
#   - stdlib/power_lib.asm    (Exponenciación rápida)
#   - stdlib/vecmat.asm       (Vectores + Matrices, con MAT_MUL)
#
# Cálculos:
#   1) GCD(252, 105) = 21                       → resultado en [500]
#   2) 3^5 = 243                                → resultado en [508]
#   3) Matriz A(3×2) × B(2×4) = C(3×4)          → resultado en 670
#      A = [[1,2],[3,4],[5,6]]
#      B = [[1,2,3,4],[5,6,7,8]]
#      C esperado: [[11,14,17,20],[23,30,37,44],[35,46,57,68]]
#
# Código desde posición 8000
# ============================================================================
.org 8000

#define ADDR_GCD_RES   500
#define ADDR_POW_RES   508
#define BASE_MA        550
#define BASE_MB        558
#define BASE_MC        670

    jmp MAIN

#include <stdlib/gcd_lib.asm>
#include <stdlib/power_lib.asm>
#include <stdlib/vecmat.asm>

MAIN:
# ── 1) GCD(252, 105) ─────────────────────────────────────────────────
    mov R0, 252
    mov R1, 105
    call GCD
    out R0                      # [OUT] = 21
    storew R0, ADDR_GCD_RES     # guardar en memoria

# ── 2) 3^5 = 243 ─────────────────────────────────────────────────────
    mov R0, 3
    mov R1, 5
    call FAST_POWER
    out R0                      # [OUT] = 243
    storew R0, ADDR_POW_RES     # guardar en memoria

# ── 3) Multiplicación de matrices 3×2 × 2×4 ──────────────────────────
    # A = [[1,2],[3,4],[5,6]]  en BASE_MA (550), 2+6=8 bytes
    mov R0, BASE_MA
    mov R1, 3
    mov R2, 2
    call MAT_INIT

    mov R0, BASE_MA
    mov R1, 0
    mov R2, 0
    mov R3, 1
    call MAT_SET
    mov R0, BASE_MA
    mov R1, 0
    mov R2, 1
    mov R3, 2
    call MAT_SET
    mov R0, BASE_MA
    mov R1, 1
    mov R2, 0
    mov R3, 3
    call MAT_SET
    mov R0, BASE_MA
    mov R1, 1
    mov R2, 1
    mov R3, 4
    call MAT_SET
    mov R0, BASE_MA
    mov R1, 2
    mov R2, 0
    mov R3, 5
    call MAT_SET
    mov R0, BASE_MA
    mov R1, 2
    mov R2, 1
    mov R3, 6
    call MAT_SET

    # B = [[1,2,3,4],[5,6,7,8]]  en BASE_MB (558), 2+8=10 bytes
    mov R0, BASE_MB
    mov R1, 2
    mov R2, 4
    call MAT_INIT

    mov R0, BASE_MB
    mov R1, 0
    mov R2, 0
    mov R3, 1
    call MAT_SET
    mov R0, BASE_MB
    mov R1, 0
    mov R2, 1
    mov R3, 2
    call MAT_SET
    mov R0, BASE_MB
    mov R1, 0
    mov R2, 2
    mov R3, 3
    call MAT_SET
    mov R0, BASE_MB
    mov R1, 0
    mov R2, 3
    mov R3, 4
    call MAT_SET
    mov R0, BASE_MB
    mov R1, 1
    mov R2, 0
    mov R3, 5
    call MAT_SET
    mov R0, BASE_MB
    mov R1, 1
    mov R2, 1
    mov R3, 6
    call MAT_SET
    mov R0, BASE_MB
    mov R1, 1
    mov R2, 2
    mov R3, 7
    call MAT_SET
    mov R0, BASE_MB
    mov R1, 1
    mov R2, 3
    mov R3, 8
    call MAT_SET

    # C = A × B  en BASE_MC (670)
    mov R0, BASE_MA
    mov R1, BASE_MB
    mov R2, BASE_MC
    call MAT_MUL

    # Imprimir resultado C(3×4): 12 elementos
    # Fila 0: 11, 14, 17, 20
    mov R0, BASE_MC
    mov R1, 0
    mov R2, 0
    call MAT_GET
    out R0
    mov R0, BASE_MC
    mov R1, 0
    mov R2, 1
    call MAT_GET
    out R0
    mov R0, BASE_MC
    mov R1, 0
    mov R2, 2
    call MAT_GET
    out R0
    mov R0, BASE_MC
    mov R1, 0
    mov R2, 3
    call MAT_GET
    out R0

    # Fila 1: 23, 30, 37, 44
    mov R0, BASE_MC
    mov R1, 1
    mov R2, 0
    call MAT_GET
    out R0
    mov R0, BASE_MC
    mov R1, 1
    mov R2, 1
    call MAT_GET
    out R0
    mov R0, BASE_MC
    mov R1, 1
    mov R2, 2
    call MAT_GET
    out R0
    mov R0, BASE_MC
    mov R1, 1
    mov R2, 3
    call MAT_GET
    out R0

    # Fila 2: 35, 46, 57, 68
    mov R0, BASE_MC
    mov R1, 2
    mov R2, 0
    call MAT_GET
    out R0
    mov R0, BASE_MC
    mov R1, 2
    mov R2, 1
    call MAT_GET
    out R0
    mov R0, BASE_MC
    mov R1, 2
    mov R2, 2
    call MAT_GET
    out R0
    mov R0, BASE_MC
    mov R1, 2
    mov R2, 3
    call MAT_GET
    out R0

    halt
