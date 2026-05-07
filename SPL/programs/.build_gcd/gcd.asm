# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..312)  data=[312..336)  strings=[336..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion gcd(a, b) ---
gcd:
    storew R0, 312    # parametro a
    storew R1, 320    # parametro b
while_start_1:
    loadw R6, 312    # a
    loadw R7, 320    # b
    cmp R6, R7
    jz while_end_2
    loadw R8, 312    # a
    loadw R9, 320    # b
    cmp R8, R9
    jg sk_5
    jmp if_next_4
sk_5:
    loadw R10, 312    # a
    loadw R11, 320    # b
    sub R10, R11
    storew R10, 312    # a = ...
    jmp if_end_3
if_next_4:
    loadw R12, 320    # b
    loadw R13, 312    # a
    sub R12, R13
    storew R12, 320    # b = ...
if_end_3:
    jmp while_start_1
while_end_2:
    loadw R6, 312    # a
    mov R0, R6    # valor de retorno
    ret
# 
# --- funcion main() ---
main:
    mov R7, 48
    mov R8, 18
    mov R0, R7    # arg1
    mov R1, R8    # arg2
    call gcd
    mov R9, R0    # retorno de gcd
    storew R9, 328    # result = ...
    loadw R11, 328    # result
    out R11    # print
    mov R10, 0
    mov R13, 0
    mov R0, R13    # valor de retorno
    ret

# ------------------------------------------------------------------------
#  Sección de datos (variables)  [312..336)
# ------------------------------------------------------------------------
    .fill 24
