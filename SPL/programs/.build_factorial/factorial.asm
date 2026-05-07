# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..264)  data=[264..288)  strings=[288..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion factorial(n) ---
factorial:
    storew R0, 264    # parametro n
    mov R6, 1
    storew R6, 272    # acc = ...
while_start_1:
    loadw R7, 264    # n
    mov R8, 1
    cmp R7, R8
    jg sk_3
    jmp while_end_2
sk_3:
    loadw R9, 272    # acc
    loadw R10, 264    # n
    mul R9, R10
    storew R9, 272    # acc = ...
    loadw R11, 264    # n
    mov R12, 1
    sub R11, R12
    storew R11, 264    # n = ...
    jmp while_start_1
while_end_2:
    loadw R13, 272    # acc
    mov R0, R13    # valor de retorno
    ret
# 
# --- funcion main() ---
main:
    mov R6, 5
    mov R0, R6    # arg1
    call factorial
    mov R7, R0    # retorno de factorial
    storew R7, 280    # result = ...
    loadw R8, 280    # result
    out R8    # print
    mov R10, 0
    mov R9, 0
    mov R0, R9    # valor de retorno
    ret

# ------------------------------------------------------------------------
#  Sección de datos (variables)  [264..288)
# ------------------------------------------------------------------------
    .fill 24
