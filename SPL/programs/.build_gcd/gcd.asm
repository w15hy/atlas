# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..328)  data=[328..352)  strings=[352..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion gcd(a, b) ---
gcd:
    storew R0, 328    # parametro a
    storew R1, 336    # parametro b
while_start_1:
    loadw R6, 328    # a
    loadw R7, 336    # b
    cmp R6, R7
    jz while_end_2
    loadw R8, 328    # a
    loadw R9, 336    # b
    cmp R8, R9
    jg sk_5
    jmp if_next_4
sk_5:
    loadw R10, 328    # a
    loadw R11, 336    # b
    sub R10, R11
    storew R10, 328    # a = ...
    jmp if_end_3
if_next_4:
    loadw R12, 336    # b
    loadw R13, 328    # a
    sub R12, R13
    storew R12, 336    # b = ...
if_end_3:
    jmp while_start_1
while_end_2:
    loadw R6, 328    # a
    mov R0, R6    # valor de retorno
    ret
# 
# --- funcion main() ---
main:
    mov R7, 48
    push R7    # spill arg para gcd
    mov R8, 18
    push R8    # spill arg para gcd
    pop R1    # arg2
    pop R0    # arg1
    call gcd
    mov R9, R0    # retorno de gcd
    storew R9, 344    # result = ...
    loadw R11, 344    # result
    out R11    # print
    mov R10, 0
    mov R13, 0
    mov R0, R13    # valor de retorno
    ret

# ------------------------------------------------------------------------
#  Sección de datos (variables)  [328..352)
# ------------------------------------------------------------------------
    .fill 24
