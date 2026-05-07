# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..536)  data=[536..584)  strings=[584..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion fast_pow(base, exp) ---
fast_pow:
    storew R0, 536    # parametro base
    storew R1, 544    # parametro exp
    mov R6, 1
    storew R6, 552    # result = ...
while_start_1:
    loadw R7, 544    # exp
    mov R8, 0
    cmp R7, R8
    jg sk_3
    jmp while_end_2
sk_3:
    loadw R9, 544    # exp
    loadw R10, 544    # exp
    mov R11, 2
    div R10, R11
    mov R12, 2
    mul R10, R12
    sub R9, R10
    storew R9, 560    # bit = ...
    loadw R13, 560    # bit
    mov R6, 0
    cmp R13, R6
    jz if_next_5
    loadw R7, 552    # result
    loadw R8, 536    # base
    mul R7, R8
    storew R7, 552    # result = ...
    jmp if_end_4
if_next_5:
if_end_4:
    loadw R11, 536    # base
    loadw R12, 536    # base
    mul R11, R12
    storew R11, 536    # base = ...
    loadw R10, 544    # exp
    mov R9, 2
    div R10, R9
    storew R10, 544    # exp = ...
    jmp while_start_1
while_end_2:
    loadw R13, 552    # result
    mov R0, R13    # valor de retorno
    ret
# 
# --- funcion main() ---
main:
    mov R6, 2
    push R6    # spill arg para fast_pow
    mov R8, 10
    push R8    # spill arg para fast_pow
    pop R1    # arg2
    pop R0    # arg1
    call fast_pow
    mov R7, R0    # retorno de fast_pow
    storew R7, 568    # r1 = ...
    loadw R12, 568    # r1
    out R12    # print
    mov R11, 0
    mov R9, 3
    push R9    # spill arg para fast_pow
    mov R10, 7
    push R10    # spill arg para fast_pow
    pop R1    # arg2
    pop R0    # arg1
    call fast_pow
    mov R13, R0    # retorno de fast_pow
    storew R13, 576    # r2 = ...
    loadw R6, 576    # r2
    out R6    # print
    mov R8, 0
    mov R7, 0
    mov R0, R7    # valor de retorno
    ret

# ------------------------------------------------------------------------
#  Sección de datos (variables)  [536..584)
# ------------------------------------------------------------------------
    .fill 48
