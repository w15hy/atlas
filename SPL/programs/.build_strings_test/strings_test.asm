# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..184)  data=[184..208)  strings=[208..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion main() ---
main:
    mov R6, 208    # &"Hola, Atlas!"
    storew R6, 184    # greeting = ...
    mov R7, 224    # &"Atlas SPL"
    storew R7, 192    # lang = ...
    loadw R8, 184    # greeting
    outs R8    # print string
    mov R9, 0
    loadw R10, 192    # lang
    outs R10    # print string
    mov R11, 0
    mov R12, 240    # &"literal anonimo"
    outs R12    # print string
    mov R13, 0
    mov R6, 42
    storew R6, 200    # x = ...
    loadw R7, 200    # x
    out R7    # print
    mov R8, 0
    mov R9, 0
    mov R0, R9    # valor de retorno
    ret

# ------------------------------------------------------------------------
#  Sección de datos (variables)  [184..208)
# ------------------------------------------------------------------------
    .fill 24

# ------------------------------------------------------------------------
#  Sección de strings  [208..)
# ------------------------------------------------------------------------
#   [208] = 'Hola, Atlas!'
    .string "Hola, Atlas!"
#   [224] = 'Atlas SPL'
    .string "Atlas SPL"
#   [240] = 'literal anonimo'
    .string "literal anonimo"
