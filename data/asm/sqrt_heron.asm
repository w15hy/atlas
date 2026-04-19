# =============================================================================
# sqrt_heron.asm
# =============================================================================
# Algoritmo de Herón:
#   x_{k+1} = (x_k + n / x_k) / 2
# Converge cuando |x_k - x_{k+1}| < tolerancia
#
# Asignación de registros:
#   R0  — x          (estimación actual, arranca en 10.0)
#   R1  — n          (constante: 10.0)
#   R2  — tmp        (n/x en cada iteración, luego x + n/x, luego x_next)
#   R3  — 0.5        (constante para el promedio)
#   R4  — tolerancia (constante: 1e-6)
#   R5  — diff       (|x - x_next|, para verificar convergencia)
#   R15 — resultado  (copia final de x al converger)
#
# Instrucciones FPU usadas (prefijo F5 = 0100):
#   fmov rd, <imm>   modo=1  — carga inmediato IEEE 754 en rd
#   fmov rd, r1      modo=0  — copia registro
#   fdiv rd, r1              — rd = float(rd) / float(r1)
#   fadd rd, r1              — rd = float(rd) + float(r1)
#   fmul rd, r1              — rd = float(rd) * float(r1)
#   fsub rd, r1              — rd = float(rd) - float(r1)
#   fabs rd                  — rd = |float(rd)|
#   fcmp rd, r1              — actualiza flags Z/N (no modifica registros)
# =============================================================================

# --- Inicialización de constantes -------------------------------------------

    fmov R0, 10.0       # R0 = x  (estimación inicial = n)
    fmov R1, 10.0       # R1 = n  (constante)
    fmov R3, 0.5        # R3 = 0.5
    fmov R4, 0.000001   # R4 = tolerancia (1e-6)

# --- Bucle de Herón ----------------------------------------------------------
# Cada iteración calcula:
#   R2 = R1           - R2 = n
#   R2 = R2 / R0      - R2 = n / x
#   R2 = R2 + R0      - R2 = x + n/x
#   R2 = R2 * R3      - R2 = (x + n/x) * 0.5  = x_next
#   R5 = R0           - R5 = x  (copia para calcular diff)
#   R5 = R5 - R2      - R5 = x - x_next
#   R5 = |R5|         - R5 = |x - x_next|
#   fcmp R5, R4       - compara diff con tolerancia
#   si R5 < R4 (flag_N=1 tras fcmp R5-R4) - salir del bucle
#   R0 = R2           - x = x_next, repetir

LOOP:
    fmov  R2, R1        # R2 = n  (copia fresca de la constante)
    fdiv  R2, R0        # R2 = n / x
    fadd  R2, R0        # R2 = x + n/x
    fmul  R2, R3        # R2 = (x + n/x) * 0.5  -  x_next

    fmov  R5, R0        # R5 = x  (para medir diferencia)
    fsub  R5, R2        # R5 = x - x_next
    fabs  R5            # R5 = |x - x_next|

    fcmp  R5, R4        # flags: N=1 si diff < tolerancia  (R5 - R4 < 0)
    jn    DONE          # si flag_N - convergió, salir

    fmov  R0, R2        # x = x_next
    jmp   LOOP          # siguiente iteración

# --- Resultado ---------------------------------------------------------------
DONE:
    fmov  R15, R2       # R15 = resultado final (x_next al converger)
    halt
