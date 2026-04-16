# ============================================================================
# Programa A (preprocesador) — Euclides GCD con #define y #include
# ============================================================================
# Demuestra uso de #define para constantes y #include para bibliotecas
# ============================================================================
.org 2500

#define OP_A      48
#define OP_B      18
#define ADDR_A    375
#define ADDR_B    1535
#define ADDR_RES  7478

    jmp MAIN

#include <stdlib/gcd_lib.asm>

MAIN:
    # Inicializar operandos en memoria
    mov R0, OP_A
    storew R0, ADDR_A
    mov R0, OP_B
    storew R0, ADDR_B

    # Cargar operandos desde memoria
    loadw R0, ADDR_A
    loadw R1, ADDR_B

    # Calcular GCD usando la biblioteca
    call GCD

    # Almacenar y mostrar resultado
    storew R0, ADDR_RES
    out R0
    halt
