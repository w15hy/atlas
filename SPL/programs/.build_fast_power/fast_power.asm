# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..504)  data=[504..552)  strings=[552..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion fast_pow(base, exp) ---
fast_pow:
    storew R0, 504    # parametro base
    storew R1, 512    # parametro exp
    mov R6, 1
    storew R6, 520    # result = ...
while_start_1:
    loadw R7, 512    # exp
    mov R8, 0
    cmp R7, R8
    jg sk_3
    jmp while_end_2
sk_3:
    loadw R9, 512    # exp
    loadw R10, 512    # exp
    mov R11, 2
    div R10, R11
    mov R12, 2
    mul R10, R12
    sub R9, R10
    storew R9, 528    # bit = ...
    loadw R13, 528    # bit
    mov R6, 0
    cmp R13, R6
    jz if_next_5
    loadw R7, 520    # result
    loadw R8, 504    # base
    mul R7, R8
    storew R7, 520    # result = ...
    jmp if_end_4
if_next_5:
if_end_4:
    loadw R11, 504    # base
    loadw R12, 504    # base
    mul R11, R12
    storew R11, 504    # base = ...
    loadw R10, 512    # exp
    mov R9, 2
    div R10, R9
    storew R10, 512    # exp = ...
    jmp while_start_1
while_end_2:
    loadw R13, 520    # result
    mov R0, R13    # valor de retorno
    ret
# 
# --- funcion main() ---
main:
    mov R6, 2
    mov R8, 10
    mov R0, R6    # arg1
    mov R1, R8    # arg2
    call fast_pow
    mov R7, R0    # retorno de fast_pow
    storew R7, 536    # r1 = ...
    loadw R12, 536    # r1
    out R12    # print
    mov R11, 0
    mov R9, 3
    mov R10, 7
    mov R0, R9    # arg1
    mov R1, R10    # arg2
    call fast_pow
    mov R13, R0    # retorno de fast_pow
    storew R13, 544    # r2 = ...
    loadw R6, 544    # r2
    out R6    # print
    mov R8, 0
    mov R7, 0
    mov R0, R7    # valor de retorno
    ret

# ------------------------------------------------------------------------
#  Sección de datos (variables)  [504..552)
# ------------------------------------------------------------------------
    .fill 48
