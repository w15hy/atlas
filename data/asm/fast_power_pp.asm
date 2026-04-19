# ============================================================================
# Programa C (preprocesador) — Fast Power con #define y #include
# ============================================================================
# Demuestra uso de #define para constantes y #include para bibliotecas
# ============================================================================
.org 5000

#define BASE_VAL   2
#define EXP_VAL    10
#define ADDR_BASE  100
#define ADDR_EXP   108
#define ADDR_RES   200

    jmp MAIN

#include <stdlib/power_lib.asm>

MAIN:
    # Inicializar datos de entrada en memoria
    mov R0, BASE_VAL
    storew R0, ADDR_BASE
    mov R0, EXP_VAL
    storew R0, ADDR_EXP

    # Cargar operandos desde memoria
    loadw R0, ADDR_BASE
    loadw R1, ADDR_EXP

    # Calcular base^exp usando la biblioteca
    call FAST_POWER

    # Almacenar y mostrar resultado
    storew R0, ADDR_RES
    out R0                  # debe mostrar 1024
    halt
