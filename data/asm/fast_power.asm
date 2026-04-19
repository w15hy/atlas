# ============================================================================
# Programa C — Exponenciación rápida (Fast Power / Power by Squaring)
# ============================================================================
# Calcula base^exp en O(log exp) multiplicaciones.
# Algoritmo clásico que demuestra manipulación de bits, bucles y
# la capacidad computacional de la máquina.
#
# Datos de entrada en memoria 100 y 108:
#   [100] = base,  [108] = exponente
# Resultado en memoria 200:
#   [200] = base^exp
#
# Ejemplo: 2^10 = 1024,  3^7 = 2187
# Código binario a partir de posición 5000
# ============================================================================
.org 5000

# ── Inicializar datos de entrada ─────────────────────────────────────────
    mov R0, 2
    storew R0, 100          # base = 2
    mov R0, 10
    storew R0, 108          # exp  = 10

# ── Cargar operandos desde memoria ───────────────────────────────────────
    loadw R0, 100           # R0 = base
    loadw R1, 108           # R1 = exp

# ── Exponenciación rápida ────────────────────────────────────────────────
# R0 = base (se va elevando al cuadrado)
# R1 = exp  (se va dividiendo entre 2)
# R2 = resultado (acumulador)
# R3 = temp para AND (bit menos significativo)
# R4 = constante 0
# R5 = constante 1

    mov R2, 1               # resultado = 1
    mov R4, 0               # constante 0
    mov R5, 1               # constante 1

POWER_LOOP:
    cmp R1, R4              # exp == 0?
    jz POWER_DONE

    # Verificar si exp es impar (bit LSB)
    mov R3, R1              # R3 = exp
    and R3, R5              # R3 = exp & 1
    cmp R3, R4              # ¿bit 0 es 0? (¿es par?)
    jz POWER_SQUARE         # si es par, solo elevar al cuadrado

    # exp es impar: resultado *= base
    mul R2, R0

POWER_SQUARE:
    # base = base * base (elevar al cuadrado)
    mul R0, R0

    # exp = exp >> 1 (dividir entre 2)
    shr R1

    jmp POWER_LOOP

POWER_DONE:
    # Guardar resultado
    storew R2, 200          # resultado en dirección 200
    mov R0, R2              # copiar para out
    out R0                  # mostrar resultado: debe ser 1024
    halt
