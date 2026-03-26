# ============================================================
# test_vecmat.asm — Demostración de stdlib/vecmat
# ============================================================
#
# IMPORTANTE — Arquitectura Von Neumann:
#   Código y datos comparten la MISMA memoria RAM.
#   El programa ocupa 0x0000 .. 0x04CF (1232 bytes).
#   Los datos deben ir en direcciones >= 0x04D0 (1232 en decimal).
#
#   Zona de datos usada aquí:
#     vecA en 1300  (vector de 3 elementos)
#     vecB en 1400  (vector de 3 elementos, relleno con 1)
#     vecC en 1500  (copia de vecA)
#     matM en 1600  (matriz 2×3)
# ============================================================

    jmp MAIN
    #include <stdlib/vecmat.asm>

# ============================================================
MAIN:
# ============================================================

# ─────────────────────────────────────────────────────────────
# VECTOR  vecA = [10, 20, 30]   base = 1300 (0x0514)
# ─────────────────────────────────────────────────────────────

    # Inicializar: mem[1300] = 3
    mov  R0, 1300
    mov  R1, 3
    call VEC_INIT

    # vecA[0] = 10
    mov  R0, 1300
    mov  R1, 0
    mov  R2, 10
    call VEC_SET

    # vecA[1] = 20
    mov  R0, 1300
    mov  R1, 1
    mov  R2, 20
    call VEC_SET

    # vecA[2] = 30
    mov  R0, 1300
    mov  R1, 2
    mov  R2, 30
    call VEC_SET

    # Leer vecA[1]  →  R8 debe ser 20
    mov  R0, 1300
    mov  R1, 1
    call VEC_GET
    mov  R8, R0

    # Suma de vecA  →  R9 debe ser 60
    mov  R0, 1300
    call VEC_SUM
    mov  R9, R0

# ─────────────────────────────────────────────────────────────
# VECTOR vecB = [1, 1, 1]  base = 1400
# VEC_ADD:  vecA[i] += vecB[i]  →  vecA = [11, 21, 31]
# ─────────────────────────────────────────────────────────────

    # Inicializar vecB con longitud 3
    mov  R0, 1400
    mov  R1, 3
    call VEC_INIT

    # Rellenar todos los elementos con 1
    mov  R0, 1400
    mov  R1, 1
    call VEC_FILL

    # Sumar vecB a vecA
    mov  R0, 1300
    mov  R1, 1400
    call VEC_ADD

    # Verificar vecA[0] = 11
    mov  R0, 1300
    mov  R1, 0
    call VEC_GET
    mov  R10, R0

# ─────────────────────────────────────────────────────────────
# COPIA: vecA → vecC   base = 1500
# ─────────────────────────────────────────────────────────────

    mov  R0, 1300
    mov  R1, 1500
    call VEC_COPY

    # Longitud de la copia → R11 debe ser 3
    mov  R0, 1500
    call VEC_LEN
    mov  R11, R0

# ─────────────────────────────────────────────────────────────
# MATRIZ  M[2][3]   base = 1600
# ─────────────────────────────────────────────────────────────

    mov  R0, 1600
    mov  R1, 2
    mov  R2, 3
    call MAT_INIT

    # Rellenar toda la matriz con 7
    mov  R0, 1600
    mov  R1, 7
    call MAT_FILL

    # Escribir M[1][2] = 42
    mov  R0, 1600
    mov  R1, 1
    mov  R2, 2
    mov  R3, 42
    call MAT_SET

    # Leer M[1][2]  →  R12 debe ser 42
    mov  R0, 1600
    mov  R1, 1
    mov  R2, 2
    call MAT_GET
    mov  R12, R0

    # Leer M[0][0]  →  R13 debe ser 7
    mov  R0, 1600
    mov  R1, 0
    mov  R2, 0
    call MAT_GET
    mov  R13, R0

# ─────────────────────────────────────────────────────────────
# FIN — Resultado esperado en registros:
#   R8  = 20     (vecA[1])
#   R9  = 60     (suma de [10,20,30])
#   R10 = 11     (vecA[0] tras VEC_ADD)
#   R11 = 3      (len de la copia)
#   R12 = 42     (M[1][2])
#   R13 = 7      (M[0][0] tras MAT_FILL)
# ─────────────────────────────────────────────────────────────
    halt
