# =============================================================================
# main_test_link.asm — Programa principal: prueba EUCLIDES + MERGESORT
# =============================================================================
# Enlazar con:
#   python linker_loader.py main_test_link.asm lib_euclides.asm mod_mergesort.asm -o test_link.bin
#
# PRUEBA 1 — Euclides:
#   gcd(48, 18) = 6     -> R8
#   gcd(100, 75) = 25   -> R9
#
# PRUEBA 2 — MergeSort:
#   [5, 3, 8, 1, 9, 2, 7, 4] -> [1, 2, 3, 4, 5, 7, 8, 9]
#   Resultado en R10..R15 (primeros 6 elementos) y memoria
# =============================================================================

.extern GCD
.extern MERGESORT

MAIN:
    # ── PRUEBA 1a: gcd(48, 18) = 6 ─────────────────────────
    mov  R0, 48
    mov  R1, 18
    call GCD
    mov  R8, R0             # R8 = 6

    # ── PRUEBA 1b: gcd(100, 75) = 25 ───────────────────────
    mov  R0, 100
    mov  R1, 75
    call GCD
    mov  R9, R0             # R9 = 25

    # ── PRUEBA 2: MergeSort [5,3,8,1,9,2,7,4] ─────────────
    push R8                 # salvar resultados de euclides
    push R9

    mov  R0, 2000           # ARR_BASE
    mov  R1, 8              # N = 8
    mov  R2, 2100           # TMP_BASE

    # Cargar arreglo inicial en memoria
    mov  R10, 5
    store R10, R0, 0, 0     # arr[0]=5
    mov  R10, 3
    store R10, R0, 0, 1     # arr[1]=3
    mov  R10, 8
    store R10, R0, 0, 2     # arr[2]=8
    mov  R10, 1
    store R10, R0, 0, 3     # arr[3]=1
    mov  R10, 9
    store R10, R0, 0, 4     # arr[4]=9
    mov  R10, 2
    store R10, R0, 0, 5     # arr[5]=2
    mov  R10, 7
    store R10, R0, 0, 6     # arr[6]=7
    mov  R10, 4
    store R10, R0, 0, 7     # arr[7]=4

    call  MERGESORT

    pop  R9                 # restaurar resultados de euclides
    pop  R8

    # Leer resultado ordenado
    load  R10, R0, 0, 0     # arr[0] = 1
    load  R11, R0, 0, 1     # arr[1] = 2
    load  R12, R0, 0, 2     # arr[2] = 3
    load  R13, R0, 0, 3     # arr[3] = 4
    load  R14, R0, 0, 4     # arr[4] = 5
    load  R15, R0, 0, 5     # arr[5] = 7

    halt
