# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..10304)  data=[10304..11288)  strings=[11288..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion vec_init(v, n) ---
vec_init:
    storew R0, 10304    # parametro v
    storew R1, 10312    # parametro n
    mov R6, 0
    loadw R7, 10312    # n
    muli R6, 8    # idx * word
    loadw R8, 10304    # base de v (ptr)
    add R6, R8    # idx*word + base
    storew R7, R6    # v[idx] = ...
    ret
# 
# --- funcion vec_len(v) ---
vec_len:
    storew R0, 10320    # parametro v
    mov R9, 0
    muli R9, 8
    loadw R10, 10320    # base de v (ptr)
    add R9, R10
    loadw R11, R9    # v[idx]
    mov R0, R11    # valor de retorno
    ret
# 
# --- funcion vec_get(v, i) ---
vec_get:
    storew R0, 10328    # parametro v
    storew R1, 10336    # parametro i
    loadw R12, 10336    # i
    mov R13, 1
    add R12, R13
    muli R12, 8
    loadw R8, 10328    # base de v (ptr)
    add R12, R8
    loadw R6, R12    # v[idx]
    mov R0, R6    # valor de retorno
    ret
# 
# --- funcion vec_set(v, i, val) ---
vec_set:
    storew R0, 10344    # parametro v
    storew R1, 10352    # parametro i
    storew R2, 10360    # parametro val
    loadw R7, 10352    # i
    mov R10, 1
    add R7, R10
    loadw R9, 10360    # val
    muli R7, 8    # idx * word
    loadw R11, 10344    # base de v (ptr)
    add R7, R11    # idx*word + base
    storew R9, R7    # v[idx] = ...
    ret
# 
# --- funcion vec_fill(v, val) ---
vec_fill:
    storew R0, 10368    # parametro v
    storew R1, 10376    # parametro val
    mov R13, 0
    muli R13, 8
    loadw R8, 10368    # base de v (ptr)
    add R13, R8
    loadw R12, R13    # v[idx]
    storew R12, 10384    # n = ...
    mov R6, 0
    storew R6, 10392    # i = ...
while_start_1:
    loadw R10, 10392    # i
    loadw R11, 10384    # n
    cmp R10, R11
    jge while_end_2
    loadw R7, 10392    # i
    mov R9, 1
    add R7, R9
    loadw R8, 10376    # val
    muli R7, 8    # idx * word
    loadw R13, 10368    # base de v (ptr)
    add R7, R13    # idx*word + base
    storew R8, R7    # v[idx] = ...
    loadw R12, 10392    # i
    mov R6, 1
    add R12, R6
    storew R12, 10392    # i = ...
    jmp while_start_1
while_end_2:
    ret
# 
# --- funcion vec_sum(v) ---
vec_sum:
    storew R0, 10400    # parametro v
    mov R10, 0
    muli R10, 8
    loadw R11, 10400    # base de v (ptr)
    add R10, R11
    loadw R9, R10    # v[idx]
    storew R9, 10408    # n = ...
    mov R13, 0
    storew R13, 10416    # s = ...
    mov R7, 0
    storew R7, 10424    # i = ...
while_start_3:
    loadw R8, 10424    # i
    loadw R6, 10408    # n
    cmp R8, R6
    jge while_end_4
    loadw R12, 10416    # s
    loadw R11, 10424    # i
    mov R10, 1
    add R11, R10
    muli R11, 8
    loadw R9, 10400    # base de v (ptr)
    add R11, R9
    loadw R13, R11    # v[idx]
    add R12, R13
    storew R12, 10416    # s = ...
    loadw R7, 10424    # i
    mov R8, 1
    add R7, R8
    storew R7, 10424    # i = ...
    jmp while_start_3
while_end_4:
    loadw R6, 10416    # s
    mov R0, R6    # valor de retorno
    ret
# 
# --- funcion vec_dot(a, b) ---
vec_dot:
    storew R0, 10432    # parametro a
    storew R1, 10440    # parametro b
    mov R10, 0
    muli R10, 8
    loadw R9, 10432    # base de a (ptr)
    add R10, R9
    loadw R11, R10    # a[idx]
    storew R11, 10448    # n = ...
    mov R13, 0
    storew R13, 10456    # s = ...
    mov R12, 0
    storew R12, 10464    # i = ...
while_start_5:
    loadw R8, 10464    # i
    loadw R7, 10448    # n
    cmp R8, R7
    jge while_end_6
    loadw R6, 10456    # s
    loadw R9, 10464    # i
    mov R10, 1
    add R9, R10
    muli R9, 8
    loadw R11, 10432    # base de a (ptr)
    add R9, R11
    loadw R13, R9    # a[idx]
    loadw R12, 10464    # i
    mov R8, 1
    add R12, R8
    muli R12, 8
    loadw R7, 10440    # base de b (ptr)
    add R12, R7
    loadw R10, R12    # b[idx]
    mul R13, R10
    add R6, R13
    storew R6, 10456    # s = ...
    loadw R11, 10464    # i
    mov R9, 1
    add R11, R9
    storew R11, 10464    # i = ...
    jmp while_start_5
while_end_6:
    loadw R8, 10456    # s
    mov R0, R8    # valor de retorno
    ret
# 
# --- funcion vec_add(a, b) ---
vec_add:
    storew R0, 10472    # parametro a
    storew R1, 10480    # parametro b
    mov R7, 0
    muli R7, 8
    loadw R12, 10472    # base de a (ptr)
    add R7, R12
    loadw R10, R7    # a[idx]
    storew R10, 10488    # n = ...
    mov R13, 0
    storew R13, 10496    # i = ...
while_start_7:
    loadw R6, 10496    # i
    loadw R9, 10488    # n
    cmp R6, R9
    jge while_end_8
    loadw R11, 10496    # i
    mov R8, 1
    add R11, R8
    loadw R12, 10496    # i
    mov R7, 1
    add R12, R7
    muli R12, 8
    loadw R10, 10472    # base de a (ptr)
    add R12, R10
    loadw R13, R12    # a[idx]
    loadw R6, 10496    # i
    mov R9, 1
    add R6, R9
    muli R6, 8
    loadw R8, 10480    # base de b (ptr)
    add R6, R8
    loadw R7, R6    # b[idx]
    add R13, R7
    muli R11, 8    # idx * word
    loadw R10, 10472    # base de a (ptr)
    add R11, R10    # idx*word + base
    storew R13, R11    # a[idx] = ...
    loadw R12, 10496    # i
    mov R9, 1
    add R12, R9
    storew R12, 10496    # i = ...
    jmp while_start_7
while_end_8:
    ret
# 
# --- funcion vec_sub(a, b) ---
vec_sub:
    storew R0, 10504    # parametro a
    storew R1, 10512    # parametro b
    mov R8, 0
    muli R8, 8
    loadw R6, 10504    # base de a (ptr)
    add R8, R6
    loadw R7, R8    # a[idx]
    storew R7, 10520    # n = ...
    mov R10, 0
    storew R10, 10528    # i = ...
while_start_9:
    loadw R11, 10528    # i
    loadw R13, 10520    # n
    cmp R11, R13
    jge while_end_10
    loadw R9, 10528    # i
    mov R12, 1
    add R9, R12
    loadw R6, 10528    # i
    mov R8, 1
    add R6, R8
    muli R6, 8
    loadw R7, 10504    # base de a (ptr)
    add R6, R7
    loadw R10, R6    # a[idx]
    loadw R11, 10528    # i
    mov R13, 1
    add R11, R13
    muli R11, 8
    loadw R12, 10512    # base de b (ptr)
    add R11, R12
    loadw R8, R11    # b[idx]
    sub R10, R8
    muli R9, 8    # idx * word
    loadw R7, 10504    # base de a (ptr)
    add R9, R7    # idx*word + base
    storew R10, R9    # a[idx] = ...
    loadw R6, 10528    # i
    mov R13, 1
    add R6, R13
    storew R6, 10528    # i = ...
    jmp while_start_9
while_end_10:
    ret
# 
# --- funcion vec_scale(v, k) ---
vec_scale:
    storew R0, 10536    # parametro v
    storew R1, 10544    # parametro k
    mov R12, 0
    muli R12, 8
    loadw R11, 10536    # base de v (ptr)
    add R12, R11
    loadw R8, R12    # v[idx]
    storew R8, 10552    # n = ...
    mov R7, 0
    storew R7, 10560    # i = ...
while_start_11:
    loadw R9, 10560    # i
    loadw R10, 10552    # n
    cmp R9, R10
    jge while_end_12
    loadw R13, 10560    # i
    mov R6, 1
    add R13, R6
    loadw R11, 10560    # i
    mov R12, 1
    add R11, R12
    muli R11, 8
    loadw R8, 10536    # base de v (ptr)
    add R11, R8
    loadw R7, R11    # v[idx]
    loadw R9, 10544    # k
    mul R7, R9
    muli R13, 8    # idx * word
    loadw R10, 10536    # base de v (ptr)
    add R13, R10    # idx*word + base
    storew R7, R13    # v[idx] = ...
    loadw R6, 10560    # i
    mov R12, 1
    add R6, R12
    storew R6, 10560    # i = ...
    jmp while_start_11
while_end_12:
    ret
# 
# --- funcion vec_max(v) ---
vec_max:
    storew R0, 10568    # parametro v
    mov R8, 0
    muli R8, 8
    loadw R11, 10568    # base de v (ptr)
    add R8, R11
    loadw R9, R8    # v[idx]
    storew R9, 10576    # n = ...
    mov R10, 1
    muli R10, 8
    loadw R13, 10568    # base de v (ptr)
    add R10, R13
    loadw R7, R10    # v[idx]
    storew R7, 10584    # m = ...
    mov R12, 1
    storew R12, 10592    # i = ...
while_start_13:
    loadw R6, 10592    # i
    loadw R11, 10576    # n
    cmp R6, R11
    jge while_end_14
    loadw R8, 10592    # i
    mov R9, 1
    add R8, R9
    muli R8, 8
    loadw R13, 10568    # base de v (ptr)
    add R8, R13
    loadw R10, R8    # v[idx]
    loadw R7, 10584    # m
    cmp R10, R7
    jg sk_17
    jmp if_next_16
sk_17:
    loadw R12, 10592    # i
    mov R6, 1
    add R12, R6
    muli R12, 8
    loadw R11, 10568    # base de v (ptr)
    add R12, R11
    loadw R9, R12    # v[idx]
    storew R9, 10584    # m = ...
    jmp if_end_15
if_next_16:
if_end_15:
    loadw R13, 10592    # i
    mov R8, 1
    add R13, R8
    storew R13, 10592    # i = ...
    jmp while_start_13
while_end_14:
    loadw R10, 10584    # m
    mov R0, R10    # valor de retorno
    ret
# 
# --- funcion vec_min(v) ---
vec_min:
    storew R0, 10600    # parametro v
    mov R7, 0
    muli R7, 8
    loadw R6, 10600    # base de v (ptr)
    add R7, R6
    loadw R11, R7    # v[idx]
    storew R11, 10608    # n = ...
    mov R12, 1
    muli R12, 8
    loadw R9, 10600    # base de v (ptr)
    add R12, R9
    loadw R8, R12    # v[idx]
    storew R8, 10616    # m = ...
    mov R13, 1
    storew R13, 10624    # i = ...
while_start_18:
    loadw R10, 10624    # i
    loadw R6, 10608    # n
    cmp R10, R6
    jge while_end_19
    loadw R7, 10624    # i
    mov R11, 1
    add R7, R11
    muli R7, 8
    loadw R9, 10600    # base de v (ptr)
    add R7, R9
    loadw R12, R7    # v[idx]
    loadw R8, 10616    # m
    cmp R12, R8
    jge if_next_21
    loadw R13, 10624    # i
    mov R10, 1
    add R13, R10
    muli R13, 8
    loadw R6, 10600    # base de v (ptr)
    add R13, R6
    loadw R11, R13    # v[idx]
    storew R11, 10616    # m = ...
    jmp if_end_20
if_next_21:
if_end_20:
    loadw R9, 10624    # i
    mov R7, 1
    add R9, R7
    storew R9, 10624    # i = ...
    jmp while_start_18
while_end_19:
    loadw R12, 10616    # m
    mov R0, R12    # valor de retorno
    ret
# 
# --- funcion vec_copy(dst, src) ---
vec_copy:
    storew R0, 10632    # parametro dst
    storew R1, 10640    # parametro src
    mov R8, 0
    muli R8, 8
    loadw R10, 10640    # base de src (ptr)
    add R8, R10
    loadw R6, R8    # src[idx]
    storew R6, 10648    # n = ...
    mov R13, 0
    loadw R11, 10648    # n
    muli R13, 8    # idx * word
    loadw R7, 10632    # base de dst (ptr)
    add R13, R7    # idx*word + base
    storew R11, R13    # dst[idx] = ...
    mov R9, 0
    storew R9, 10656    # i = ...
while_start_22:
    loadw R12, 10656    # i
    loadw R10, 10648    # n
    cmp R12, R10
    jge while_end_23
    loadw R8, 10656    # i
    mov R6, 1
    add R8, R6
    loadw R7, 10656    # i
    mov R13, 1
    add R7, R13
    muli R7, 8
    loadw R11, 10640    # base de src (ptr)
    add R7, R11
    loadw R9, R7    # src[idx]
    muli R8, 8    # idx * word
    loadw R12, 10632    # base de dst (ptr)
    add R8, R12    # idx*word + base
    storew R9, R8    # dst[idx] = ...
    loadw R10, 10656    # i
    mov R6, 1
    add R10, R6
    storew R10, 10656    # i = ...
    jmp while_start_22
while_end_23:
    ret
# 
# --- funcion vec_print(v) ---
vec_print:
    storew R0, 10664    # parametro v
    mov R13, 0
    muli R13, 8
    loadw R11, 10664    # base de v (ptr)
    add R13, R11
    loadw R7, R13    # v[idx]
    storew R7, 10672    # n = ...
    mov R12, 0
    storew R12, 10680    # i = ...
while_start_24:
    loadw R8, 10680    # i
    loadw R9, 10672    # n
    cmp R8, R9
    jge while_end_25
    loadw R6, 10680    # i
    mov R10, 1
    add R6, R10
    muli R6, 8
    loadw R11, 10664    # base de v (ptr)
    add R6, R11
    loadw R13, R6    # v[idx]
    out R13    # print
    mov R7, 0
    loadw R12, 10680    # i
    mov R8, 1
    add R12, R8
    storew R12, 10680    # i = ...
    jmp while_start_24
while_end_25:
    ret
# 
# --- funcion mat_init(m, rows, cols) ---
mat_init:
    storew R0, 10688    # parametro m
    storew R1, 10696    # parametro rows
    storew R2, 10704    # parametro cols
    mov R9, 0
    loadw R10, 10696    # rows
    muli R9, 8    # idx * word
    loadw R11, 10688    # base de m (ptr)
    add R9, R11    # idx*word + base
    storew R10, R9    # m[idx] = ...
    mov R6, 1
    loadw R13, 10704    # cols
    muli R6, 8    # idx * word
    loadw R7, 10688    # base de m (ptr)
    add R6, R7    # idx*word + base
    storew R13, R6    # m[idx] = ...
    ret
# 
# --- funcion mat_rows(m) ---
mat_rows:
    storew R0, 10712    # parametro m
    mov R8, 0
    muli R8, 8
    loadw R12, 10712    # base de m (ptr)
    add R8, R12
    loadw R11, R8    # m[idx]
    mov R0, R11    # valor de retorno
    ret
# 
# --- funcion mat_cols(m) ---
mat_cols:
    storew R0, 10720    # parametro m
    mov R9, 1
    muli R9, 8
    loadw R10, 10720    # base de m (ptr)
    add R9, R10
    loadw R7, R9    # m[idx]
    mov R0, R7    # valor de retorno
    ret
# 
# --- funcion mat_get(m, i, j) ---
mat_get:
    storew R0, 10728    # parametro m
    storew R1, 10736    # parametro i
    storew R2, 10744    # parametro j
    mov R6, 1
    muli R6, 8
    loadw R13, 10728    # base de m (ptr)
    add R6, R13
    loadw R12, R6    # m[idx]
    storew R12, 10752    # cols = ...
    loadw R8, 10736    # i
    loadw R11, 10752    # cols
    mul R8, R11
    loadw R10, 10744    # j
    add R8, R10
    mov R9, 2
    add R8, R9
    muli R8, 8
    loadw R7, 10728    # base de m (ptr)
    add R8, R7
    loadw R13, R8    # m[idx]
    mov R0, R13    # valor de retorno
    ret
# 
# --- funcion mat_set(m, i, j, val) ---
mat_set:
    storew R0, 10760    # parametro m
    storew R1, 10768    # parametro i
    storew R2, 10776    # parametro j
    storew R3, 10784    # parametro val
    mov R6, 1
    muli R6, 8
    loadw R12, 10760    # base de m (ptr)
    add R6, R12
    loadw R11, R6    # m[idx]
    storew R11, 10792    # cols = ...
    loadw R10, 10768    # i
    loadw R9, 10792    # cols
    mul R10, R9
    loadw R7, 10776    # j
    add R10, R7
    mov R8, 2
    add R10, R8
    loadw R13, 10784    # val
    muli R10, 8    # idx * word
    loadw R12, 10760    # base de m (ptr)
    add R10, R12    # idx*word + base
    storew R13, R10    # m[idx] = ...
    ret
# 
# --- funcion mat_fill(m, val) ---
mat_fill:
    storew R0, 10800    # parametro m
    storew R1, 10808    # parametro val
    mov R6, 0
    muli R6, 8
    loadw R11, 10800    # base de m (ptr)
    add R6, R11
    loadw R9, R6    # m[idx]
    storew R9, 10816    # rows = ...
    mov R7, 1
    muli R7, 8
    loadw R8, 10800    # base de m (ptr)
    add R7, R8
    loadw R12, R7    # m[idx]
    storew R12, 10824    # cols = ...
    loadw R10, 10816    # rows
    loadw R13, 10824    # cols
    mul R10, R13
    storew R10, 10832    # total = ...
    mov R11, 0
    storew R11, 10840    # k = ...
while_start_26:
    loadw R6, 10840    # k
    loadw R9, 10832    # total
    cmp R6, R9
    jge while_end_27
    loadw R8, 10840    # k
    mov R7, 2
    add R8, R7
    loadw R12, 10808    # val
    muli R8, 8    # idx * word
    loadw R13, 10800    # base de m (ptr)
    add R8, R13    # idx*word + base
    storew R12, R8    # m[idx] = ...
    loadw R10, 10840    # k
    mov R11, 1
    add R10, R11
    storew R10, 10840    # k = ...
    jmp while_start_26
while_end_27:
    ret
# 
# --- funcion mat_mul(a, b, c) ---
mat_mul:
    storew R0, 10848    # parametro a
    storew R1, 10856    # parametro b
    storew R2, 10864    # parametro c
    mov R6, 0
    muli R6, 8
    loadw R9, 10848    # base de a (ptr)
    add R6, R9
    loadw R7, R6    # a[idx]
    storew R7, 10872    # ar = ...
    mov R13, 1
    muli R13, 8
    loadw R8, 10848    # base de a (ptr)
    add R13, R8
    loadw R12, R13    # a[idx]
    storew R12, 10880    # ac = ...
    mov R11, 1
    muli R11, 8
    loadw R10, 10856    # base de b (ptr)
    add R11, R10
    loadw R9, R11    # b[idx]
    storew R9, 10888    # bc = ...
    mov R6, 0
    loadw R7, 10872    # ar
    muli R6, 8    # idx * word
    loadw R8, 10864    # base de c (ptr)
    add R6, R8    # idx*word + base
    storew R7, R6    # c[idx] = ...
    mov R13, 1
    loadw R12, 10888    # bc
    muli R13, 8    # idx * word
    loadw R10, 10864    # base de c (ptr)
    add R13, R10    # idx*word + base
    storew R12, R13    # c[idx] = ...
    mov R11, 0
    storew R11, 10896    # i = ...
while_start_28:
    loadw R9, 10896    # i
    loadw R8, 10872    # ar
    cmp R9, R8
    jge while_end_29
    mov R6, 0
    storew R6, 10904    # j = ...
while_start_30:
    loadw R7, 10904    # j
    loadw R10, 10888    # bc
    cmp R7, R10
    jge while_end_31
    mov R13, 0
    storew R13, 10912    # acc = ...
    mov R12, 0
    storew R12, 10920    # k = ...
while_start_32:
    loadw R11, 10920    # k
    loadw R9, 10880    # ac
    cmp R11, R9
    jge while_end_33
    loadw R8, 10912    # acc
    loadw R6, 10896    # i
    loadw R7, 10880    # ac
    mul R6, R7
    loadw R10, 10920    # k
    add R6, R10
    mov R13, 2
    add R6, R13
    muli R6, 8
    loadw R12, 10848    # base de a (ptr)
    add R6, R12
    loadw R11, R6    # a[idx]
    loadw R9, 10920    # k
    loadw R7, 10888    # bc
    mul R9, R7
    loadw R10, 10904    # j
    add R9, R10
    mov R13, 2
    add R9, R13
    muli R9, 8
    loadw R12, 10856    # base de b (ptr)
    add R9, R12
    loadw R6, R9    # b[idx]
    mul R11, R6
    add R8, R11
    storew R8, 10912    # acc = ...
    loadw R7, 10920    # k
    mov R10, 1
    add R7, R10
    storew R7, 10920    # k = ...
    jmp while_start_32
while_end_33:
    loadw R13, 10896    # i
    loadw R12, 10888    # bc
    mul R13, R12
    loadw R9, 10904    # j
    add R13, R9
    mov R6, 2
    add R13, R6
    loadw R11, 10912    # acc
    muli R13, 8    # idx * word
    loadw R8, 10864    # base de c (ptr)
    add R13, R8    # idx*word + base
    storew R11, R13    # c[idx] = ...
    loadw R10, 10904    # j
    mov R7, 1
    add R10, R7
    storew R10, 10904    # j = ...
    jmp while_start_30
while_end_31:
    loadw R12, 10896    # i
    mov R9, 1
    add R12, R9
    storew R12, 10896    # i = ...
    jmp while_start_28
while_end_29:
    ret
# 
# --- funcion mat_print(m) ---
mat_print:
    storew R0, 10928    # parametro m
    mov R6, 0
    muli R6, 8
    loadw R8, 10928    # base de m (ptr)
    add R6, R8
    loadw R13, R6    # m[idx]
    storew R13, 10936    # rows = ...
    mov R11, 1
    muli R11, 8
    loadw R7, 10928    # base de m (ptr)
    add R11, R7
    loadw R10, R11    # m[idx]
    storew R10, 10944    # cols = ...
    mov R9, 0
    storew R9, 10952    # i = ...
while_start_34:
    loadw R12, 10952    # i
    loadw R8, 10936    # rows
    cmp R12, R8
    jge while_end_35
    mov R6, 0
    storew R6, 10960    # j = ...
while_start_36:
    loadw R13, 10960    # j
    loadw R7, 10944    # cols
    cmp R13, R7
    jge while_end_37
    loadw R11, 10952    # i
    loadw R10, 10944    # cols
    mul R11, R10
    loadw R9, 10960    # j
    add R11, R9
    mov R12, 2
    add R11, R12
    muli R11, 8
    loadw R8, 10928    # base de m (ptr)
    add R11, R8
    loadw R6, R11    # m[idx]
    out R6    # print
    mov R13, 0
    loadw R7, 10960    # j
    mov R10, 1
    add R7, R10
    storew R7, 10960    # j = ...
    jmp while_start_36
while_end_37:
    loadw R9, 10952    # i
    mov R12, 1
    add R9, R12
    storew R9, 10952    # i = ...
    jmp while_start_34
while_end_35:
    ret
# 
# --- funcion main() ---
main:
# ; arreglo v base=10968
    mov R8, 10968    # &v
    push R8    # spill arg para vec_init
    mov R11, 5
    push R11    # spill arg para vec_init
    pop R1    # arg2
    pop R0    # arg1
    call vec_init
    mov R6, R0    # retorno de vec_init
    mov R13, 10968    # &v
    push R13    # spill arg para vec_fill
    mov R10, 0
    push R10    # spill arg para vec_fill
    pop R1    # arg2
    pop R0    # arg1
    call vec_fill
    mov R7, R0    # retorno de vec_fill
    mov R12, 10968    # &v
    push R12    # spill arg para vec_len
    pop R0    # arg1
    call vec_len
    mov R9, R0    # retorno de vec_len
    out R9    # print
    mov R8, 0
    mov R11, 10968    # &v
    push R11    # spill arg para vec_set
    mov R6, 0
    push R6    # spill arg para vec_set
    mov R13, 10
    push R13    # spill arg para vec_set
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call vec_set
    mov R10, R0    # retorno de vec_set
    mov R7, 10968    # &v
    push R7    # spill arg para vec_set
    mov R12, 1
    push R12    # spill arg para vec_set
    mov R9, 20
    push R9    # spill arg para vec_set
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call vec_set
    mov R8, R0    # retorno de vec_set
    mov R11, 10968    # &v
    push R11    # spill arg para vec_set
    mov R6, 2
    push R6    # spill arg para vec_set
    mov R13, 30
    push R13    # spill arg para vec_set
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call vec_set
    mov R10, R0    # retorno de vec_set
    mov R7, 10968    # &v
    push R7    # spill arg para vec_set
    mov R12, 3
    push R12    # spill arg para vec_set
    mov R9, 40
    push R9    # spill arg para vec_set
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call vec_set
    mov R8, R0    # retorno de vec_set
    mov R11, 10968    # &v
    push R11    # spill arg para vec_set
    mov R6, 4
    push R6    # spill arg para vec_set
    mov R13, 50
    push R13    # spill arg para vec_set
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call vec_set
    mov R10, R0    # retorno de vec_set
    mov R7, 10968    # &v
    push R7    # spill arg para vec_get
    mov R12, 0
    push R12    # spill arg para vec_get
    pop R1    # arg2
    pop R0    # arg1
    call vec_get
    mov R9, R0    # retorno de vec_get
    out R9    # print
    mov R8, 0
    mov R11, 10968    # &v
    push R11    # spill arg para vec_get
    mov R6, 4
    push R6    # spill arg para vec_get
    pop R1    # arg2
    pop R0    # arg1
    call vec_get
    mov R13, R0    # retorno de vec_get
    out R13    # print
    mov R10, 0
    mov R7, 10968    # &v
    push R7    # spill arg para vec_sum
    pop R0    # arg1
    call vec_sum
    mov R12, R0    # retorno de vec_sum
    out R12    # print
    mov R9, 0
    mov R8, 10968    # &v
    push R8    # spill arg para vec_max
    pop R0    # arg1
    call vec_max
    mov R11, R0    # retorno de vec_max
    out R11    # print
    mov R6, 0
    mov R13, 10968    # &v
    push R13    # spill arg para vec_min
    pop R0    # arg1
    call vec_min
    mov R10, R0    # retorno de vec_min
    out R10    # print
    mov R7, 0
# ; arreglo w base=11016
    mov R12, 11016    # &w
    push R12    # spill arg para vec_copy
    mov R9, 10968    # &v
    push R9    # spill arg para vec_copy
    pop R1    # arg2
    pop R0    # arg1
    call vec_copy
    mov R8, R0    # retorno de vec_copy
    mov R11, 11016    # &w
    push R11    # spill arg para vec_len
    pop R0    # arg1
    call vec_len
    mov R6, R0    # retorno de vec_len
    out R6    # print
    mov R13, 0
    mov R10, 11016    # &w
    push R10    # spill arg para vec_sum
    pop R0    # arg1
    call vec_sum
    mov R7, R0    # retorno de vec_sum
    out R7    # print
    mov R12, 0
    mov R9, 11016    # &w
    push R9    # spill arg para vec_scale
    mov R8, 2
    push R8    # spill arg para vec_scale
    pop R1    # arg2
    pop R0    # arg1
    call vec_scale
    mov R11, R0    # retorno de vec_scale
    mov R6, 11016    # &w
    push R6    # spill arg para vec_get
    mov R13, 0
    push R13    # spill arg para vec_get
    pop R1    # arg2
    pop R0    # arg1
    call vec_get
    mov R10, R0    # retorno de vec_get
    out R10    # print
    mov R7, 0
    mov R12, 11016    # &w
    push R12    # spill arg para vec_get
    mov R9, 4
    push R9    # spill arg para vec_get
    pop R1    # arg2
    pop R0    # arg1
    call vec_get
    mov R8, R0    # retorno de vec_get
    out R8    # print
    mov R11, 0
    mov R6, 11016    # &w
    push R6    # spill arg para vec_sum
    pop R0    # arg1
    call vec_sum
    mov R13, R0    # retorno de vec_sum
    out R13    # print
    mov R10, 0
    mov R7, 10968    # &v
    push R7    # spill arg para vec_dot
    mov R12, 10968    # &v
    push R12    # spill arg para vec_dot
    pop R1    # arg2
    pop R0    # arg1
    call vec_dot
    mov R9, R0    # retorno de vec_dot
    out R9    # print
    mov R8, 0
    mov R11, 10968    # &v
    push R11    # spill arg para vec_add
    mov R6, 10968    # &v
    push R6    # spill arg para vec_add
    pop R1    # arg2
    pop R0    # arg1
    call vec_add
    mov R13, R0    # retorno de vec_add
    mov R10, 10968    # &v
    push R10    # spill arg para vec_get
    mov R7, 0
    push R7    # spill arg para vec_get
    pop R1    # arg2
    pop R0    # arg1
    call vec_get
    mov R12, R0    # retorno de vec_get
    out R12    # print
    mov R9, 0
    mov R8, 10968    # &v
    push R8    # spill arg para vec_get
    mov R11, 4
    push R11    # spill arg para vec_get
    pop R1    # arg2
    pop R0    # arg1
    call vec_get
    mov R6, R0    # retorno de vec_get
    out R6    # print
    mov R13, 0
    mov R10, 10968    # &v
    push R10    # spill arg para vec_sum
    pop R0    # arg1
    call vec_sum
    mov R7, R0    # retorno de vec_sum
    out R7    # print
    mov R12, 0
    mov R9, 10968    # &v
    push R9    # spill arg para vec_sub
    mov R8, 11016    # &w
    push R8    # spill arg para vec_sub
    pop R1    # arg2
    pop R0    # arg1
    call vec_sub
    mov R11, R0    # retorno de vec_sub
    mov R6, 10968    # &v
    push R6    # spill arg para vec_sum
    pop R0    # arg1
    call vec_sum
    mov R13, R0    # retorno de vec_sum
    out R13    # print
    mov R10, 0
# ; arreglo A base=11064
    mov R7, 11064    # &A
    push R7    # spill arg para mat_init
    mov R12, 2
    push R12    # spill arg para mat_init
    mov R9, 3
    push R9    # spill arg para mat_init
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_init
    mov R8, R0    # retorno de mat_init
    mov R11, 11064    # &A
    push R11    # spill arg para mat_set
    mov R6, 0
    push R6    # spill arg para mat_set
    mov R13, 0
    push R13    # spill arg para mat_set
    mov R10, 1
    push R10    # spill arg para mat_set
    pop R3    # arg4
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_set
    mov R7, R0    # retorno de mat_set
    mov R12, 11064    # &A
    push R12    # spill arg para mat_set
    mov R9, 0
    push R9    # spill arg para mat_set
    mov R8, 1
    push R8    # spill arg para mat_set
    mov R11, 2
    push R11    # spill arg para mat_set
    pop R3    # arg4
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_set
    mov R6, R0    # retorno de mat_set
    mov R13, 11064    # &A
    push R13    # spill arg para mat_set
    mov R10, 0
    push R10    # spill arg para mat_set
    mov R7, 2
    push R7    # spill arg para mat_set
    mov R12, 3
    push R12    # spill arg para mat_set
    pop R3    # arg4
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_set
    mov R9, R0    # retorno de mat_set
    mov R8, 11064    # &A
    push R8    # spill arg para mat_set
    mov R11, 1
    push R11    # spill arg para mat_set
    mov R6, 0
    push R6    # spill arg para mat_set
    mov R13, 4
    push R13    # spill arg para mat_set
    pop R3    # arg4
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_set
    mov R10, R0    # retorno de mat_set
    mov R7, 11064    # &A
    push R7    # spill arg para mat_set
    mov R12, 1
    push R12    # spill arg para mat_set
    mov R9, 1
    push R9    # spill arg para mat_set
    mov R8, 5
    push R8    # spill arg para mat_set
    pop R3    # arg4
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_set
    mov R11, R0    # retorno de mat_set
    mov R6, 11064    # &A
    push R6    # spill arg para mat_set
    mov R13, 1
    push R13    # spill arg para mat_set
    mov R10, 2
    push R10    # spill arg para mat_set
    mov R7, 6
    push R7    # spill arg para mat_set
    pop R3    # arg4
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_set
    mov R12, R0    # retorno de mat_set
    mov R9, 11064    # &A
    push R9    # spill arg para mat_rows
    pop R0    # arg1
    call mat_rows
    mov R8, R0    # retorno de mat_rows
    out R8    # print
    mov R11, 0
    mov R6, 11064    # &A
    push R6    # spill arg para mat_cols
    pop R0    # arg1
    call mat_cols
    mov R13, R0    # retorno de mat_cols
    out R13    # print
    mov R10, 0
    mov R7, 11064    # &A
    push R7    # spill arg para mat_get
    mov R12, 0
    push R12    # spill arg para mat_get
    mov R9, 0
    push R9    # spill arg para mat_get
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_get
    mov R8, R0    # retorno de mat_get
    out R8    # print
    mov R11, 0
    mov R6, 11064    # &A
    push R6    # spill arg para mat_get
    mov R13, 1
    push R13    # spill arg para mat_get
    mov R10, 2
    push R10    # spill arg para mat_get
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_get
    mov R7, R0    # retorno de mat_get
    out R7    # print
    mov R12, 0
# ; arreglo B base=11128
    mov R9, 11128    # &B
    push R9    # spill arg para mat_init
    mov R8, 3
    push R8    # spill arg para mat_init
    mov R11, 2
    push R11    # spill arg para mat_init
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_init
    mov R6, R0    # retorno de mat_init
    mov R13, 11128    # &B
    push R13    # spill arg para mat_set
    mov R10, 0
    push R10    # spill arg para mat_set
    mov R7, 0
    push R7    # spill arg para mat_set
    mov R12, 7
    push R12    # spill arg para mat_set
    pop R3    # arg4
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_set
    mov R9, R0    # retorno de mat_set
    mov R8, 11128    # &B
    push R8    # spill arg para mat_set
    mov R11, 0
    push R11    # spill arg para mat_set
    mov R6, 1
    push R6    # spill arg para mat_set
    mov R13, 8
    push R13    # spill arg para mat_set
    pop R3    # arg4
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_set
    mov R10, R0    # retorno de mat_set
    mov R7, 11128    # &B
    push R7    # spill arg para mat_set
    mov R12, 1
    push R12    # spill arg para mat_set
    mov R9, 0
    push R9    # spill arg para mat_set
    mov R8, 9
    push R8    # spill arg para mat_set
    pop R3    # arg4
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_set
    mov R11, R0    # retorno de mat_set
    mov R6, 11128    # &B
    push R6    # spill arg para mat_set
    mov R13, 1
    push R13    # spill arg para mat_set
    mov R10, 1
    push R10    # spill arg para mat_set
    mov R7, 10
    push R7    # spill arg para mat_set
    pop R3    # arg4
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_set
    mov R12, R0    # retorno de mat_set
    mov R9, 11128    # &B
    push R9    # spill arg para mat_set
    mov R8, 2
    push R8    # spill arg para mat_set
    mov R11, 0
    push R11    # spill arg para mat_set
    mov R6, 11
    push R6    # spill arg para mat_set
    pop R3    # arg4
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_set
    mov R13, R0    # retorno de mat_set
    mov R10, 11128    # &B
    push R10    # spill arg para mat_set
    mov R7, 2
    push R7    # spill arg para mat_set
    mov R12, 1
    push R12    # spill arg para mat_set
    mov R9, 12
    push R9    # spill arg para mat_set
    pop R3    # arg4
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_set
    mov R8, R0    # retorno de mat_set
# ; arreglo C base=11192
    mov R11, 11064    # &A
    push R11    # spill arg para mat_mul
    mov R6, 11128    # &B
    push R6    # spill arg para mat_mul
    mov R13, 11192    # &C
    push R13    # spill arg para mat_mul
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_mul
    mov R10, R0    # retorno de mat_mul
    mov R7, 11192    # &C
    push R7    # spill arg para mat_rows
    pop R0    # arg1
    call mat_rows
    mov R12, R0    # retorno de mat_rows
    out R12    # print
    mov R9, 0
    mov R8, 11192    # &C
    push R8    # spill arg para mat_cols
    pop R0    # arg1
    call mat_cols
    mov R11, R0    # retorno de mat_cols
    out R11    # print
    mov R6, 0
    mov R13, 11192    # &C
    push R13    # spill arg para mat_get
    mov R10, 0
    push R10    # spill arg para mat_get
    mov R7, 0
    push R7    # spill arg para mat_get
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_get
    mov R12, R0    # retorno de mat_get
    out R12    # print
    mov R9, 0
    mov R8, 11192    # &C
    push R8    # spill arg para mat_get
    mov R11, 0
    push R11    # spill arg para mat_get
    mov R6, 1
    push R6    # spill arg para mat_get
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_get
    mov R13, R0    # retorno de mat_get
    out R13    # print
    mov R10, 0
    mov R7, 11192    # &C
    push R7    # spill arg para mat_get
    mov R12, 1
    push R12    # spill arg para mat_get
    mov R9, 0
    push R9    # spill arg para mat_get
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_get
    mov R8, R0    # retorno de mat_get
    out R8    # print
    mov R11, 0
    mov R6, 11192    # &C
    push R6    # spill arg para mat_get
    mov R13, 1
    push R13    # spill arg para mat_get
    mov R10, 1
    push R10    # spill arg para mat_get
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_get
    mov R7, R0    # retorno de mat_get
    out R7    # print
    mov R12, 0
# ; arreglo F base=11240
    mov R9, 11240    # &F
    push R9    # spill arg para mat_init
    mov R8, 2
    push R8    # spill arg para mat_init
    mov R11, 2
    push R11    # spill arg para mat_init
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_init
    mov R6, R0    # retorno de mat_init
    mov R13, 11240    # &F
    push R13    # spill arg para mat_fill
    mov R10, 7
    push R10    # spill arg para mat_fill
    pop R1    # arg2
    pop R0    # arg1
    call mat_fill
    mov R7, R0    # retorno de mat_fill
    mov R12, 11240    # &F
    push R12    # spill arg para mat_get
    mov R9, 0
    push R9    # spill arg para mat_get
    mov R8, 0
    push R8    # spill arg para mat_get
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_get
    mov R11, R0    # retorno de mat_get
    out R11    # print
    mov R6, 0
    mov R13, 11240    # &F
    push R13    # spill arg para mat_get
    mov R10, 1
    push R10    # spill arg para mat_get
    mov R7, 1
    push R7    # spill arg para mat_get
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call mat_get
    mov R12, R0    # retorno de mat_get
    out R12    # print
    mov R9, 0
    mov R8, 0
    mov R0, R8    # valor de retorno
    ret

# ------------------------------------------------------------------------
#  Sección de datos (variables)  [10304..11288)
# ------------------------------------------------------------------------
    .fill 984
