# =============================================================================
# main_tres.asm — Programa principal que usa las 3 librerías
# =============================================================================
# Enlazar con:
#   python linker_loader.py main_tres.asm lib_euclides.asm lib_factorial.asm lib_fibo.asm -o tres.bin
#
# Resultados esperados:
#   R8  = gcd(48, 18)    = 6
#   R9  = gcd(100, 75)   = 25
#   R10 = 5!             = 120
#   R11 = 7!             = 5040
#   R12 = fib(7)         = 13
#   R13 = fib(10)        = 55
# =============================================================================

.extern GCD
.extern FACTORIAL
.extern FIBONACCI

MAIN:
    # ── EUCLIDES: gcd(48, 18) = 6 ──────────────────────────
    mov  R0, 48
    mov  R1, 18
    call GCD
    mov  R8, R0             # R8 = 6

    # ── EUCLIDES: gcd(100, 75) = 25 ────────────────────────
    mov  R0, 100
    mov  R1, 75
    call GCD
    mov  R9, R0             # R9 = 25

    # ── FACTORIAL: 5! = 120 ────────────────────────────────
    mov  R0, 5
    call FACTORIAL
    mov  R10, R0            # R10 = 120

    # ── FACTORIAL: 7! = 5040 ───────────────────────────────
    mov  R0, 7
    call FACTORIAL
    mov  R11, R0            # R11 = 5040

    # ── FIBONACCI: fib(7) = 13 ─────────────────────────────
    mov  R0, 7
    call FIBONACCI
    mov  R12, R0            # R12 = 13

    # ── FIBONACCI: fib(10) = 55 ────────────────────────────
    mov  R0, 10
    call FIBONACCI
    mov  R13, R0            # R13 = 55

    halt
