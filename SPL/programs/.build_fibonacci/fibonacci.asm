# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..376)  data=[376..416)  strings=[416..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion fibonacci(n) ---
fibonacci:
    storew R0, 376    # parametro n
    loadw R6, 376    # n
    mov R7, 0
    cmp R6, R7
    jne if_next_2
    mov R8, 0
    mov R0, R8    # valor de retorno
    ret
    jmp if_end_1
if_next_2:
if_end_1:
    mov R9, 0
    storew R9, 384    # a = ...
    mov R10, 1
    storew R10, 392    # b = ...
while_start_3:
    loadw R11, 376    # n
    mov R12, 1
    cmp R11, R12
    jg sk_5
    jmp while_end_4
sk_5:
    loadw R13, 392    # b
    storew R13, 400    # temp = ...
    loadw R6, 392    # b
    loadw R7, 384    # a
    add R6, R7
    storew R6, 392    # b = ...
    loadw R8, 400    # temp
    storew R8, 384    # a = ...
    loadw R9, 376    # n
    mov R10, 1
    sub R9, R10
    storew R9, 376    # n = ...
    jmp while_start_3
while_end_4:
    loadw R11, 392    # b
    mov R0, R11    # valor de retorno
    ret
# 
# --- funcion main() ---
main:
    mov R12, 7
    mov R0, R12    # arg1
    call fibonacci
    mov R13, R0    # retorno de fibonacci
    storew R13, 408    # result = ...
    loadw R7, 408    # result
    out R7    # print
    mov R6, 0
    mov R8, 0
    mov R0, R8    # valor de retorno
    ret

# ------------------------------------------------------------------------
#  Sección de datos (variables)  [376..416)
# ------------------------------------------------------------------------
    .fill 40
