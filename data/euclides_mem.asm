# ============================================================================
# Programa A — Algoritmo de Euclides (MCD / GCD)
# ============================================================================
# Operando A en memoria posición 375
# Operando B en memoria posición 1535
# Resultado  en memoria posición 7478
# Código binario a partir de posición 2500
# Salida por dispositivo de salida (instrucción out)
# ============================================================================
.org 2500

# ── Inicializar operandos en memoria ──────────────────────────────────────
    mov R0, 48              # operando A = 48
    storew R0, 375          # guardar A en dirección 375
    mov R0, 18              # operando B = 18
    storew R0, 1535         # guardar B en dirección 1535

# ── Cargar operandos desde memoria ────────────────────────────────────────
    loadw R0, 375           # R0 = A (48)
    loadw R1, 1535          # R1 = B (18)

# ── Algoritmo de Euclides por restas sucesivas ───────────────────────────
GCD_LOOP:
    cmp R0, R1              # comparar A y B
    jz GCD_DONE             # si A == B, terminamos
    jg A_MAYOR              # si A > B, restar B de A
    sub R1, R0              # B = B - A  (B > A)
    jmp GCD_LOOP
A_MAYOR:
    sub R0, R1              # A = A - B  (A > B)
    jmp GCD_LOOP

GCD_DONE:
    storew R0, 7478         # guardar resultado en dirección 7478
    out R0                  # mostrar resultado por dispositivo de salida
    halt
