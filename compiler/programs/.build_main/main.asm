# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..960)  data=[960..1088)  strings=[1088..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion sum(a, b) ---
sum:
    storew R0, 960    # parametro a
    storew R1, 968    # parametro b
    loadw R6, 960    # a
    loadw R7, 968    # b
    add R6, R7
    mov R0, R6    # valor de retorno
    ret
# 
# --- funcion main() ---
main:
    mov R8, 10
    storew R8, 976    # x = ...
    mov R9, 20
    storew R9, 984    # y = ...
    fmov R10, 3.14    # literal float
    storew R10, 992    # z = ...
    mov R11, 1088    # &"full coverage test"
    storew R11, 1000    # msg = ...
    loadw R12, 976    # x
    storew R12, 1008    # n.id = ...
    loadw R13, 992    # z
    storew R13, 1016    # n.value = ...
    mov R7, 1112    # &"node"
    storew R7, 1024    # n.name = ...
# ; arreglo arr base=1032
    mov R6, 0
    loadw R8, 976    # x
    muli R6, 8    # idx * word
    addi R6, 1032    # +base de arr
    storew R8, R6    # arr[idx] = ...
    mov R9, 1
    loadw R10, 984    # y
    muli R9, 8    # idx * word
    addi R9, 1032    # +base de arr
    storew R10, R9    # arr[idx] = ...
    loadw R11, 976    # x
    loadw R12, 984    # y
    cmp R11, R12
    jg sk_3
    jmp if_next_2
sk_3:
    mov R13, 1120    # &"x greater"
    storew R13, 1000    # msg = ...
    jmp if_end_1
if_next_2:
    loadw R7, 976    # x
    loadw R6, 984    # y
    cmp R7, R6
    jne if_next_4
    mov R8, 1136    # &"equal"
    storew R8, 1000    # msg = ...
    jmp if_end_1
if_next_4:
    mov R9, 1144    # &"y greater"
    storew R9, 1000    # msg = ...
if_end_1:
while_start_5:
    loadw R10, 976    # x
    mov R11, 0
    cmp R10, R11
    jz while_end_6
    loadw R12, 976    # x
    mov R13, 1
    sub R12, R13
    storew R12, 976    # x = ...
    loadw R7, 976    # x
    mov R6, 5
    cmp R7, R6
    jg if_next_8
    jmp while_end_6    # break
    jmp if_end_7
if_next_8:
if_end_7:
    jmp while_start_5
while_end_6:
    mov R8, 0
    storew R8, 1072    # i = ...
for_start_9:
    loadw R9, 1072    # i
    mov R10, 10
    cmp R9, R10
    jge for_end_11
    loadw R11, 992    # z
    fmov R13, 0.5    # literal float
    fadd R11, R13
    storew R11, 992    # z = ...
    jmp for_update_10    # continue
for_update_10:
    loadw R12, 1072    # i
    mov R7, 1
    add R12, R7
    storew R12, 1072    # i = ...
    jmp for_start_9
for_end_11:
    mov R6, 5
    mov R8, 3
    add R6, R8
    mov R9, 2
    mov R10, 4
    mul R9, R10
    mov R13, 2
    div R9, R13
    sub R6, R9
    storew R6, 1080    # a = ...
    loadw R11, 1080    # a
    mov R7, 0
    cmp R11, R7
    jge cmp_t_14
    mov R11, 0
    jmp cmp_e_15
cmp_t_14:
    mov R11, 1
cmp_e_15:
    mov R12, 0
    cmp R11, R12
    jz sc_short_16
    loadw R8, 1080    # a
    mov R10, 100
    cmp R8, R10
    jn cmp_t_18
    mov R8, 0
    jmp cmp_e_19
cmp_t_18:
    mov R8, 1
cmp_e_19:
    mov R11, R8
    jmp sc_end_17
sc_short_16:
    mov R11, 0
sc_end_17:
    mov R13, 0
    cmp R11, R13
    jz if_next_13
    mov R9, 1160    # &"range"
    storew R9, 1000    # msg = ...
    jmp if_end_12
if_next_13:
if_end_12:
    mov R6, 0
    mov R0, R6    # valor de retorno
    ret
# 
# ------------------------------------------------------------------------
#  Tabla de strings (direcciones absolutas)
# ------------------------------------------------------------------------
#   [1088] = 'full coverage test'
#   [1112] = 'node'
#   [1120] = 'x greater'
#   [1136] = 'equal'
#   [1144] = 'y greater'
#   [1160] = 'range'
