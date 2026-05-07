# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..384)  data=[384..424)  strings=[424..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion fibonacci(n) ---
fibonacci:
    storew R0, 384    # parametro n
    loadw R6, 384    # n
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
    storew R9, 392    # a = ...
    mov R10, 1
    storew R10, 400    # b = ...
while_start_3:
    loadw R11, 384    # n
    mov R12, 1
    cmp R11, R12
    jg sk_5
    jmp while_end_4
sk_5:
    loadw R13, 400    # b
    storew R13, 408    # temp = ...
    loadw R6, 400    # b
    loadw R7, 392    # a
    add R6, R7
    storew R6, 400    # b = ...
    loadw R8, 408    # temp
    storew R8, 392    # a = ...
    loadw R9, 384    # n
    mov R10, 1
    sub R9, R10
    storew R9, 384    # n = ...
    jmp while_start_3
while_end_4:
    loadw R11, 400    # b
    mov R0, R11    # valor de retorno
    ret
# 
# --- funcion main() ---
main:
    mov R12, 7
    push R12    # spill arg para fibonacci
    pop R0    # arg1
    call fibonacci
    mov R13, R0    # retorno de fibonacci
    storew R13, 416    # result = ...
    loadw R7, 416    # result
    out R7    # print
    mov R6, 0
    mov R8, 0
    mov R0, R8    # valor de retorno
    ret

# ------------------------------------------------------------------------
#  Sección de datos (variables)  [384..424)
# ------------------------------------------------------------------------
    .fill 40
