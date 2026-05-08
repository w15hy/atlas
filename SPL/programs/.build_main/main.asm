# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..7576)  data=[7576..8376)  strings=[8376..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion vec_init(v, n) ---
vec_init:
    storew R0, 7576    # parametro v
    storew R1, 7584    # parametro n
    mov R6, 0
    loadw R7, 7584    # n
    muli R6, 8    # idx * word
    loadw R8, 7576    # base de v (ptr)
    add R6, R8    # idx*word + base
    storew R7, R6    # v[idx] = ...
    ret
# 
# --- funcion vec_len(v) ---
vec_len:
    storew R0, 7592    # parametro v
    mov R9, 0
    muli R9, 8
    loadw R10, 7592    # base de v (ptr)
    add R9, R10
    loadw R11, R9    # v[idx]
    mov R0, R11    # valor de retorno
    ret
# 
# --- funcion vec_get(v, i) ---
vec_get:
    storew R0, 7600    # parametro v
    storew R1, 7608    # parametro i
    loadw R12, 7608    # i
    mov R13, 1
    add R12, R13
    muli R12, 8
    loadw R8, 7600    # base de v (ptr)
    add R12, R8
    loadw R6, R12    # v[idx]
    mov R0, R6    # valor de retorno
    ret
# 
# --- funcion vec_set(v, i, val) ---
vec_set:
    storew R0, 7616    # parametro v
    storew R1, 7624    # parametro i
    storew R2, 7632    # parametro val
    loadw R7, 7624    # i
    mov R10, 1
    add R7, R10
    loadw R9, 7632    # val
    muli R7, 8    # idx * word
    loadw R11, 7616    # base de v (ptr)
    add R7, R11    # idx*word + base
    storew R9, R7    # v[idx] = ...
    ret
# 
# --- funcion vec_fill(v, val) ---
vec_fill:
    storew R0, 7640    # parametro v
    storew R1, 7648    # parametro val
    mov R13, 0
    muli R13, 8
    loadw R8, 7640    # base de v (ptr)
    add R13, R8
    loadw R12, R13    # v[idx]
    storew R12, 7656    # n = ...
    mov R6, 0
    storew R6, 7664    # i = ...
while_start_1:
    loadw R10, 7664    # i
    loadw R11, 7656    # n
    cmp R10, R11
    jge while_end_2
    loadw R7, 7664    # i
    mov R9, 1
    add R7, R9
    loadw R8, 7648    # val
    muli R7, 8    # idx * word
    loadw R13, 7640    # base de v (ptr)
    add R7, R13    # idx*word + base
    storew R8, R7    # v[idx] = ...
    loadw R12, 7664    # i
    mov R6, 1
    add R12, R6
    storew R12, 7664    # i = ...
    jmp while_start_1
while_end_2:
    ret
# 
# --- funcion vec_sum(v) ---
vec_sum:
    storew R0, 7672    # parametro v
    mov R10, 0
    muli R10, 8
    loadw R11, 7672    # base de v (ptr)
    add R10, R11
    loadw R9, R10    # v[idx]
    storew R9, 7680    # n = ...
    mov R13, 0
    storew R13, 7688    # s = ...
    mov R7, 0
    storew R7, 7696    # i = ...
while_start_3:
    loadw R8, 7696    # i
    loadw R6, 7680    # n
    cmp R8, R6
    jge while_end_4
    loadw R12, 7688    # s
    loadw R11, 7696    # i
    mov R10, 1
    add R11, R10
    muli R11, 8
    loadw R9, 7672    # base de v (ptr)
    add R11, R9
    loadw R13, R11    # v[idx]
    add R12, R13
    storew R12, 7688    # s = ...
    loadw R7, 7696    # i
    mov R8, 1
    add R7, R8
    storew R7, 7696    # i = ...
    jmp while_start_3
while_end_4:
    loadw R6, 7688    # s
    mov R0, R6    # valor de retorno
    ret
# 
# --- funcion vec_dot(a, b) ---
vec_dot:
    storew R0, 7704    # parametro a
    storew R1, 7712    # parametro b
    mov R10, 0
    muli R10, 8
    loadw R9, 7704    # base de a (ptr)
    add R10, R9
    loadw R11, R10    # a[idx]
    storew R11, 7720    # n = ...
    mov R13, 0
    storew R13, 7728    # s = ...
    mov R12, 0
    storew R12, 7736    # i = ...
while_start_5:
    loadw R8, 7736    # i
    loadw R7, 7720    # n
    cmp R8, R7
    jge while_end_6
    loadw R6, 7728    # s
    loadw R9, 7736    # i
    mov R10, 1
    add R9, R10
    muli R9, 8
    loadw R11, 7704    # base de a (ptr)
    add R9, R11
    loadw R13, R9    # a[idx]
    loadw R12, 7736    # i
    mov R8, 1
    add R12, R8
    muli R12, 8
    loadw R7, 7712    # base de b (ptr)
    add R12, R7
    loadw R10, R12    # b[idx]
    mul R13, R10
    add R6, R13
    storew R6, 7728    # s = ...
    loadw R11, 7736    # i
    mov R9, 1
    add R11, R9
    storew R11, 7736    # i = ...
    jmp while_start_5
while_end_6:
    loadw R8, 7728    # s
    mov R0, R8    # valor de retorno
    ret
# 
# --- funcion vec_add(a, b) ---
vec_add:
    storew R0, 7744    # parametro a
    storew R1, 7752    # parametro b
    mov R7, 0
    muli R7, 8
    loadw R12, 7744    # base de a (ptr)
    add R7, R12
    loadw R10, R7    # a[idx]
    storew R10, 7760    # n = ...
    mov R13, 0
    storew R13, 7768    # i = ...
while_start_7:
    loadw R6, 7768    # i
    loadw R9, 7760    # n
    cmp R6, R9
    jge while_end_8
    loadw R11, 7768    # i
    mov R8, 1
    add R11, R8
    loadw R12, 7768    # i
    mov R7, 1
    add R12, R7
    muli R12, 8
    loadw R10, 7744    # base de a (ptr)
    add R12, R10
    loadw R13, R12    # a[idx]
    loadw R6, 7768    # i
    mov R9, 1
    add R6, R9
    muli R6, 8
    loadw R8, 7752    # base de b (ptr)
    add R6, R8
    loadw R7, R6    # b[idx]
    add R13, R7
    muli R11, 8    # idx * word
    loadw R10, 7744    # base de a (ptr)
    add R11, R10    # idx*word + base
    storew R13, R11    # a[idx] = ...
    loadw R12, 7768    # i
    mov R9, 1
    add R12, R9
    storew R12, 7768    # i = ...
    jmp while_start_7
while_end_8:
    ret
# 
# --- funcion vec_sub(a, b) ---
vec_sub:
    storew R0, 7776    # parametro a
    storew R1, 7784    # parametro b
    mov R8, 0
    muli R8, 8
    loadw R6, 7776    # base de a (ptr)
    add R8, R6
    loadw R7, R8    # a[idx]
    storew R7, 7792    # n = ...
    mov R10, 0
    storew R10, 7800    # i = ...
while_start_9:
    loadw R11, 7800    # i
    loadw R13, 7792    # n
    cmp R11, R13
    jge while_end_10
    loadw R9, 7800    # i
    mov R12, 1
    add R9, R12
    loadw R6, 7800    # i
    mov R8, 1
    add R6, R8
    muli R6, 8
    loadw R7, 7776    # base de a (ptr)
    add R6, R7
    loadw R10, R6    # a[idx]
    loadw R11, 7800    # i
    mov R13, 1
    add R11, R13
    muli R11, 8
    loadw R12, 7784    # base de b (ptr)
    add R11, R12
    loadw R8, R11    # b[idx]
    sub R10, R8
    muli R9, 8    # idx * word
    loadw R7, 7776    # base de a (ptr)
    add R9, R7    # idx*word + base
    storew R10, R9    # a[idx] = ...
    loadw R6, 7800    # i
    mov R13, 1
    add R6, R13
    storew R6, 7800    # i = ...
    jmp while_start_9
while_end_10:
    ret
# 
# --- funcion vec_scale(v, k) ---
vec_scale:
    storew R0, 7808    # parametro v
    storew R1, 7816    # parametro k
    mov R12, 0
    muli R12, 8
    loadw R11, 7808    # base de v (ptr)
    add R12, R11
    loadw R8, R12    # v[idx]
    storew R8, 7824    # n = ...
    mov R7, 0
    storew R7, 7832    # i = ...
while_start_11:
    loadw R9, 7832    # i
    loadw R10, 7824    # n
    cmp R9, R10
    jge while_end_12
    loadw R13, 7832    # i
    mov R6, 1
    add R13, R6
    loadw R11, 7832    # i
    mov R12, 1
    add R11, R12
    muli R11, 8
    loadw R8, 7808    # base de v (ptr)
    add R11, R8
    loadw R7, R11    # v[idx]
    loadw R9, 7816    # k
    mul R7, R9
    muli R13, 8    # idx * word
    loadw R10, 7808    # base de v (ptr)
    add R13, R10    # idx*word + base
    storew R7, R13    # v[idx] = ...
    loadw R6, 7832    # i
    mov R12, 1
    add R6, R12
    storew R6, 7832    # i = ...
    jmp while_start_11
while_end_12:
    ret
# 
# --- funcion vec_max(v) ---
vec_max:
    storew R0, 7840    # parametro v
    mov R8, 0
    muli R8, 8
    loadw R11, 7840    # base de v (ptr)
    add R8, R11
    loadw R9, R8    # v[idx]
    storew R9, 7848    # n = ...
    mov R10, 1
    muli R10, 8
    loadw R13, 7840    # base de v (ptr)
    add R10, R13
    loadw R7, R10    # v[idx]
    storew R7, 7856    # m = ...
    mov R12, 1
    storew R12, 7864    # i = ...
while_start_13:
    loadw R6, 7864    # i
    loadw R11, 7848    # n
    cmp R6, R11
    jge while_end_14
    loadw R8, 7864    # i
    mov R9, 1
    add R8, R9
    muli R8, 8
    loadw R13, 7840    # base de v (ptr)
    add R8, R13
    loadw R10, R8    # v[idx]
    loadw R7, 7856    # m
    cmp R10, R7
    jg sk_17
    jmp if_next_16
sk_17:
    loadw R12, 7864    # i
    mov R6, 1
    add R12, R6
    muli R12, 8
    loadw R11, 7840    # base de v (ptr)
    add R12, R11
    loadw R9, R12    # v[idx]
    storew R9, 7856    # m = ...
    jmp if_end_15
if_next_16:
if_end_15:
    loadw R13, 7864    # i
    mov R8, 1
    add R13, R8
    storew R13, 7864    # i = ...
    jmp while_start_13
while_end_14:
    loadw R10, 7856    # m
    mov R0, R10    # valor de retorno
    ret
# 
# --- funcion vec_min(v) ---
vec_min:
    storew R0, 7872    # parametro v
    mov R7, 0
    muli R7, 8
    loadw R6, 7872    # base de v (ptr)
    add R7, R6
    loadw R11, R7    # v[idx]
    storew R11, 7880    # n = ...
    mov R12, 1
    muli R12, 8
    loadw R9, 7872    # base de v (ptr)
    add R12, R9
    loadw R8, R12    # v[idx]
    storew R8, 7888    # m = ...
    mov R13, 1
    storew R13, 7896    # i = ...
while_start_18:
    loadw R10, 7896    # i
    loadw R6, 7880    # n
    cmp R10, R6
    jge while_end_19
    loadw R7, 7896    # i
    mov R11, 1
    add R7, R11
    muli R7, 8
    loadw R9, 7872    # base de v (ptr)
    add R7, R9
    loadw R12, R7    # v[idx]
    loadw R8, 7888    # m
    cmp R12, R8
    jge if_next_21
    loadw R13, 7896    # i
    mov R10, 1
    add R13, R10
    muli R13, 8
    loadw R6, 7872    # base de v (ptr)
    add R13, R6
    loadw R11, R13    # v[idx]
    storew R11, 7888    # m = ...
    jmp if_end_20
if_next_21:
if_end_20:
    loadw R9, 7896    # i
    mov R7, 1
    add R9, R7
    storew R9, 7896    # i = ...
    jmp while_start_18
while_end_19:
    loadw R12, 7888    # m
    mov R0, R12    # valor de retorno
    ret
# 
# --- funcion vec_copy(dst, src) ---
vec_copy:
    storew R0, 7904    # parametro dst
    storew R1, 7912    # parametro src
    mov R8, 0
    muli R8, 8
    loadw R10, 7912    # base de src (ptr)
    add R8, R10
    loadw R6, R8    # src[idx]
    storew R6, 7920    # n = ...
    mov R13, 0
    loadw R11, 7920    # n
    muli R13, 8    # idx * word
    loadw R7, 7904    # base de dst (ptr)
    add R13, R7    # idx*word + base
    storew R11, R13    # dst[idx] = ...
    mov R9, 0
    storew R9, 7928    # i = ...
while_start_22:
    loadw R12, 7928    # i
    loadw R10, 7920    # n
    cmp R12, R10
    jge while_end_23
    loadw R8, 7928    # i
    mov R6, 1
    add R8, R6
    loadw R7, 7928    # i
    mov R13, 1
    add R7, R13
    muli R7, 8
    loadw R11, 7912    # base de src (ptr)
    add R7, R11
    loadw R9, R7    # src[idx]
    muli R8, 8    # idx * word
    loadw R12, 7904    # base de dst (ptr)
    add R8, R12    # idx*word + base
    storew R9, R8    # dst[idx] = ...
    loadw R10, 7928    # i
    mov R6, 1
    add R10, R6
    storew R10, 7928    # i = ...
    jmp while_start_22
while_end_23:
    ret
# 
# --- funcion vec_print(v) ---
vec_print:
    storew R0, 7936    # parametro v
    mov R13, 0
    muli R13, 8
    loadw R11, 7936    # base de v (ptr)
    add R13, R11
    loadw R7, R13    # v[idx]
    storew R7, 7944    # n = ...
    mov R12, 0
    storew R12, 7952    # i = ...
while_start_24:
    loadw R8, 7952    # i
    loadw R9, 7944    # n
    cmp R8, R9
    jge while_end_25
    loadw R6, 7952    # i
    mov R10, 1
    add R6, R10
    muli R6, 8
    loadw R11, 7936    # base de v (ptr)
    add R6, R11
    loadw R13, R6    # v[idx]
    out R13    # print
    mov R7, 0
    loadw R12, 7952    # i
    mov R8, 1
    add R12, R8
    storew R12, 7952    # i = ...
    jmp while_start_24
while_end_25:
    ret
# 
# --- funcion mat_init(m, rows, cols) ---
mat_init:
    storew R0, 7960    # parametro m
    storew R1, 7968    # parametro rows
    storew R2, 7976    # parametro cols
    mov R9, 0
    loadw R10, 7968    # rows
    muli R9, 8    # idx * word
    loadw R11, 7960    # base de m (ptr)
    add R9, R11    # idx*word + base
    storew R10, R9    # m[idx] = ...
    mov R6, 1
    loadw R13, 7976    # cols
    muli R6, 8    # idx * word
    loadw R7, 7960    # base de m (ptr)
    add R6, R7    # idx*word + base
    storew R13, R6    # m[idx] = ...
    ret
# 
# --- funcion mat_rows(m) ---
mat_rows:
    storew R0, 7984    # parametro m
    mov R8, 0
    muli R8, 8
    loadw R12, 7984    # base de m (ptr)
    add R8, R12
    loadw R11, R8    # m[idx]
    mov R0, R11    # valor de retorno
    ret
# 
# --- funcion mat_cols(m) ---
mat_cols:
    storew R0, 7992    # parametro m
    mov R9, 1
    muli R9, 8
    loadw R10, 7992    # base de m (ptr)
    add R9, R10
    loadw R7, R9    # m[idx]
    mov R0, R7    # valor de retorno
    ret
# 
# --- funcion mat_get(m, i, j) ---
mat_get:
    storew R0, 8000    # parametro m
    storew R1, 8008    # parametro i
    storew R2, 8016    # parametro j
    mov R6, 1
    muli R6, 8
    loadw R13, 8000    # base de m (ptr)
    add R6, R13
    loadw R12, R6    # m[idx]
    storew R12, 8024    # cols = ...
    loadw R8, 8008    # i
    loadw R11, 8024    # cols
    mul R8, R11
    loadw R10, 8016    # j
    add R8, R10
    mov R9, 2
    add R8, R9
    muli R8, 8
    loadw R7, 8000    # base de m (ptr)
    add R8, R7
    loadw R13, R8    # m[idx]
    mov R0, R13    # valor de retorno
    ret
# 
# --- funcion mat_set(m, i, j, val) ---
mat_set:
    storew R0, 8032    # parametro m
    storew R1, 8040    # parametro i
    storew R2, 8048    # parametro j
    storew R3, 8056    # parametro val
    mov R6, 1
    muli R6, 8
    loadw R12, 8032    # base de m (ptr)
    add R6, R12
    loadw R11, R6    # m[idx]
    storew R11, 8064    # cols = ...
    loadw R10, 8040    # i
    loadw R9, 8064    # cols
    mul R10, R9
    loadw R7, 8048    # j
    add R10, R7
    mov R8, 2
    add R10, R8
    loadw R13, 8056    # val
    muli R10, 8    # idx * word
    loadw R12, 8032    # base de m (ptr)
    add R10, R12    # idx*word + base
    storew R13, R10    # m[idx] = ...
    ret
# 
# --- funcion mat_fill(m, val) ---
mat_fill:
    storew R0, 8072    # parametro m
    storew R1, 8080    # parametro val
    mov R6, 0
    muli R6, 8
    loadw R11, 8072    # base de m (ptr)
    add R6, R11
    loadw R9, R6    # m[idx]
    storew R9, 8088    # rows = ...
    mov R7, 1
    muli R7, 8
    loadw R8, 8072    # base de m (ptr)
    add R7, R8
    loadw R12, R7    # m[idx]
    storew R12, 8096    # cols = ...
    loadw R10, 8088    # rows
    loadw R13, 8096    # cols
    mul R10, R13
    storew R10, 8104    # total = ...
    mov R11, 0
    storew R11, 8112    # k = ...
while_start_26:
    loadw R6, 8112    # k
    loadw R9, 8104    # total
    cmp R6, R9
    jge while_end_27
    loadw R8, 8112    # k
    mov R7, 2
    add R8, R7
    loadw R12, 8080    # val
    muli R8, 8    # idx * word
    loadw R13, 8072    # base de m (ptr)
    add R8, R13    # idx*word + base
    storew R12, R8    # m[idx] = ...
    loadw R10, 8112    # k
    mov R11, 1
    add R10, R11
    storew R10, 8112    # k = ...
    jmp while_start_26
while_end_27:
    ret
# 
# --- funcion mat_mul(a, b, c) ---
mat_mul:
    storew R0, 8120    # parametro a
    storew R1, 8128    # parametro b
    storew R2, 8136    # parametro c
    mov R6, 0
    muli R6, 8
    loadw R9, 8120    # base de a (ptr)
    add R6, R9
    loadw R7, R6    # a[idx]
    storew R7, 8144    # ar = ...
    mov R13, 1
    muli R13, 8
    loadw R8, 8120    # base de a (ptr)
    add R13, R8
    loadw R12, R13    # a[idx]
    storew R12, 8152    # ac = ...
    mov R11, 1
    muli R11, 8
    loadw R10, 8128    # base de b (ptr)
    add R11, R10
    loadw R9, R11    # b[idx]
    storew R9, 8160    # bc = ...
    mov R6, 0
    loadw R7, 8144    # ar
    muli R6, 8    # idx * word
    loadw R8, 8136    # base de c (ptr)
    add R6, R8    # idx*word + base
    storew R7, R6    # c[idx] = ...
    mov R13, 1
    loadw R12, 8160    # bc
    muli R13, 8    # idx * word
    loadw R10, 8136    # base de c (ptr)
    add R13, R10    # idx*word + base
    storew R12, R13    # c[idx] = ...
    mov R11, 0
    storew R11, 8168    # i = ...
while_start_28:
    loadw R9, 8168    # i
    loadw R8, 8144    # ar
    cmp R9, R8
    jge while_end_29
    mov R6, 0
    storew R6, 8176    # j = ...
while_start_30:
    loadw R7, 8176    # j
    loadw R10, 8160    # bc
    cmp R7, R10
    jge while_end_31
    mov R13, 0
    storew R13, 8184    # acc = ...
    mov R12, 0
    storew R12, 8192    # k = ...
while_start_32:
    loadw R11, 8192    # k
    loadw R9, 8152    # ac
    cmp R11, R9
    jge while_end_33
    loadw R8, 8184    # acc
    loadw R6, 8168    # i
    loadw R7, 8152    # ac
    mul R6, R7
    loadw R10, 8192    # k
    add R6, R10
    mov R13, 2
    add R6, R13
    muli R6, 8
    loadw R12, 8120    # base de a (ptr)
    add R6, R12
    loadw R11, R6    # a[idx]
    loadw R9, 8192    # k
    loadw R7, 8160    # bc
    mul R9, R7
    loadw R10, 8176    # j
    add R9, R10
    mov R13, 2
    add R9, R13
    muli R9, 8
    loadw R12, 8128    # base de b (ptr)
    add R9, R12
    loadw R6, R9    # b[idx]
    mul R11, R6
    add R8, R11
    storew R8, 8184    # acc = ...
    loadw R7, 8192    # k
    mov R10, 1
    add R7, R10
    storew R7, 8192    # k = ...
    jmp while_start_32
while_end_33:
    loadw R13, 8168    # i
    loadw R12, 8160    # bc
    mul R13, R12
    loadw R9, 8176    # j
    add R13, R9
    mov R6, 2
    add R13, R6
    loadw R11, 8184    # acc
    muli R13, 8    # idx * word
    loadw R8, 8136    # base de c (ptr)
    add R13, R8    # idx*word + base
    storew R11, R13    # c[idx] = ...
    loadw R10, 8176    # j
    mov R7, 1
    add R10, R7
    storew R10, 8176    # j = ...
    jmp while_start_30
while_end_31:
    loadw R12, 8168    # i
    mov R9, 1
    add R12, R9
    storew R12, 8168    # i = ...
    jmp while_start_28
while_end_29:
    ret
# 
# --- funcion mat_print(m) ---
mat_print:
    storew R0, 8200    # parametro m
    mov R6, 0
    muli R6, 8
    loadw R8, 8200    # base de m (ptr)
    add R6, R8
    loadw R13, R6    # m[idx]
    storew R13, 8208    # rows = ...
    mov R11, 1
    muli R11, 8
    loadw R7, 8200    # base de m (ptr)
    add R11, R7
    loadw R10, R11    # m[idx]
    storew R10, 8216    # cols = ...
    mov R9, 0
    storew R9, 8224    # i = ...
while_start_34:
    loadw R12, 8224    # i
    loadw R8, 8208    # rows
    cmp R12, R8
    jge while_end_35
    mov R6, 0
    storew R6, 8232    # j = ...
while_start_36:
    loadw R13, 8232    # j
    loadw R7, 8216    # cols
    cmp R13, R7
    jge while_end_37
    loadw R11, 8224    # i
    loadw R10, 8216    # cols
    mul R11, R10
    loadw R9, 8232    # j
    add R11, R9
    mov R12, 2
    add R11, R12
    muli R11, 8
    loadw R8, 8200    # base de m (ptr)
    add R11, R8
    loadw R6, R11    # m[idx]
    out R6    # print
    mov R13, 0
    loadw R7, 8232    # j
    mov R10, 1
    add R7, R10
    storew R7, 8232    # j = ...
    jmp while_start_36
while_end_37:
    loadw R9, 8224    # i
    mov R12, 1
    add R9, R12
    storew R9, 8224    # i = ...
    jmp while_start_34
while_end_35:
    ret
# 
# --- funcion sum(a, b) ---
sum:
    storew R0, 8240    # parametro a
    storew R1, 8248    # parametro b
    loadw R8, 8240    # a
    loadw R11, 8248    # b
    add R8, R11
    mov R0, R8    # valor de retorno
    ret
# 
# --- funcion main() ---
main:
    mov R6, 10
    storew R6, 8256    # x = ...
    mov R13, 20
    storew R13, 8264    # y = ...
    fmov R10, 3.14    # literal float
    storew R10, 8272    # z = ...
    mov R7, 8376    # &"full coverage test"
    storew R7, 8280    # msg = ...
    loadw R12, 8256    # x
    storew R12, 8288    # n.id = ...
    loadw R9, 8272    # z
    storew R9, 8296    # n.value = ...
    mov R11, 8400    # &"node"
    storew R11, 8304    # n.name = ...
# ; arreglo arr base=8312
    mov R8, 8312    # &arr
    push R8    # spill arg para vec_init
    mov R6, 5
    push R6    # spill arg para vec_init
    pop R1    # arg2
    pop R0    # arg1
    call vec_init
    mov R13, R0    # retorno de vec_init
    mov R10, 8312    # &arr
    push R10    # spill arg para vec_fill
    mov R7, 0
    push R7    # spill arg para vec_fill
    pop R1    # arg2
    pop R0    # arg1
    call vec_fill
    mov R12, R0    # retorno de vec_fill
    mov R9, 8312    # &arr
    push R9    # spill arg para vec_set
    mov R11, 0
    push R11    # spill arg para vec_set
    loadw R8, 8256    # x
    push R8    # spill arg para vec_set
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call vec_set
    mov R6, R0    # retorno de vec_set
    mov R13, 8312    # &arr
    push R13    # spill arg para vec_set
    mov R10, 1
    push R10    # spill arg para vec_set
    loadw R7, 8264    # y
    push R7    # spill arg para vec_set
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call vec_set
    mov R12, R0    # retorno de vec_set
    mov R9, 8312    # &arr
    push R9    # spill arg para vec_set
    mov R11, 2
    push R11    # spill arg para vec_set
    loadw R8, 8256    # x
    push R8    # spill arg para sum
    loadw R6, 8264    # y
    push R6    # spill arg para sum
    pop R1    # arg2
    pop R0    # arg1
    call sum
    mov R13, R0    # retorno de sum
    push R13    # spill arg para vec_set
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call vec_set
    mov R10, R0    # retorno de vec_set
    mov R7, 8312    # &arr
    push R7    # spill arg para vec_set
    mov R12, 3
    push R12    # spill arg para vec_set
    loadw R9, 8256    # x
    mov R11, 2
    mul R9, R11
    push R9    # spill arg para vec_set
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call vec_set
    mov R8, R0    # retorno de vec_set
    mov R6, 8312    # &arr
    push R6    # spill arg para vec_set
    mov R13, 4
    push R13    # spill arg para vec_set
    loadw R10, 8264    # y
    mov R7, 2
    mul R10, R7
    push R10    # spill arg para vec_set
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call vec_set
    mov R12, R0    # retorno de vec_set
    mov R11, 8312    # &arr
    push R11    # spill arg para vec_len
    pop R0    # arg1
    call vec_len
    mov R9, R0    # retorno de vec_len
    out R9    # print
    mov R8, 0
    mov R6, 8312    # &arr
    push R6    # spill arg para vec_get
    mov R13, 0
    push R13    # spill arg para vec_get
    pop R1    # arg2
    pop R0    # arg1
    call vec_get
    mov R7, R0    # retorno de vec_get
    out R7    # print
    mov R10, 0
    mov R12, 8312    # &arr
    push R12    # spill arg para vec_get
    mov R11, 1
    push R11    # spill arg para vec_get
    pop R1    # arg2
    pop R0    # arg1
    call vec_get
    mov R9, R0    # retorno de vec_get
    out R9    # print
    mov R8, 0
    mov R6, 8312    # &arr
    push R6    # spill arg para vec_sum
    pop R0    # arg1
    call vec_sum
    mov R13, R0    # retorno de vec_sum
    out R13    # print
    mov R7, 0
    mov R10, 8312    # &arr
    push R10    # spill arg para vec_max
    pop R0    # arg1
    call vec_max
    mov R12, R0    # retorno de vec_max
    out R12    # print
    mov R11, 0
    mov R9, 8312    # &arr
    push R9    # spill arg para vec_min
    pop R0    # arg1
    call vec_min
    mov R8, R0    # retorno de vec_min
    out R8    # print
    mov R6, 0
    loadw R13, 8256    # x
    loadw R7, 8264    # y
    cmp R13, R7
    jg sk_40
    jmp if_next_39
sk_40:
    mov R10, 8408    # &"x greater"
    storew R10, 8280    # msg = ...
    jmp if_end_38
if_next_39:
    loadw R12, 8256    # x
    loadw R11, 8264    # y
    cmp R12, R11
    jne if_next_41
    mov R9, 8424    # &"equal"
    storew R9, 8280    # msg = ...
    jmp if_end_38
if_next_41:
    mov R8, 8432    # &"y greater"
    storew R8, 8280    # msg = ...
if_end_38:
    loadw R6, 8280    # msg
    outs R6    # print string
    mov R13, 0
while_start_42:
    loadw R7, 8256    # x
    mov R10, 0
    cmp R7, R10
    jz while_end_43
    loadw R12, 8256    # x
    mov R11, 1
    sub R12, R11
    storew R12, 8256    # x = ...
    loadw R9, 8256    # x
    mov R8, 5
    cmp R9, R8
    jg if_next_45
    jmp while_end_43    # break
    jmp if_end_44
if_next_45:
if_end_44:
    jmp while_start_42
while_end_43:
    mov R6, 0
    storew R6, 8360    # i = ...
for_start_46:
    loadw R13, 8360    # i
    mov R7, 10
    cmp R13, R7
    jge for_end_48
    loadw R10, 8272    # z
    fmov R11, 0.5    # literal float
    fadd R10, R11
    storew R10, 8272    # z = ...
    jmp for_update_47    # continue
for_update_47:
    loadw R12, 8360    # i
    mov R9, 1
    add R12, R9
    storew R12, 8360    # i = ...
    jmp for_start_46
for_end_48:
    loadw R8, 8272    # z
    mov R6, 2
    fi2f R6    # promote int->float
    fadd R8, R6
    fout R8    # print float
    mov R13, 0
    mov R7, 5
    mov R11, 3
    add R7, R11
    mov R10, 2
    mov R9, 4
    mul R10, R9
    mov R12, 2
    div R10, R12
    sub R7, R10
    storew R7, 8368    # a = ...
    loadw R6, 8368    # a
    mov R8, 0
    cmp R6, R8
    jge cmp_t_51
    mov R6, 0
    jmp cmp_e_52
cmp_t_51:
    mov R6, 1
cmp_e_52:
    mov R13, 0
    cmp R6, R13
    jz sc_short_53
    loadw R11, 8368    # a
    mov R9, 100
    cmp R11, R9
    jn cmp_t_55
    mov R11, 0
    jmp cmp_e_56
cmp_t_55:
    mov R11, 1
cmp_e_56:
    mov R6, R11
    jmp sc_end_54
sc_short_53:
    mov R6, 0
sc_end_54:
    mov R12, 0
    cmp R6, R12
    jz if_next_50
    mov R10, 8448    # &"range"
    storew R10, 8280    # msg = ...
    jmp if_end_49
if_next_50:
if_end_49:
    loadw R7, 8280    # msg
    outs R7    # print string
    mov R8, 0
    mov R13, 0
    mov R0, R13    # valor de retorno
    ret

# ------------------------------------------------------------------------
#  Sección de datos (variables)  [7576..8376)
# ------------------------------------------------------------------------
    .fill 800

# ------------------------------------------------------------------------
#  Sección de strings  [8376..)
# ------------------------------------------------------------------------
#   [8376] = 'full coverage test'
    .string "full coverage test"
#   [8400] = 'node'
    .string "node"
#   [8408] = 'x greater'
    .string "x greater"
#   [8424] = 'equal'
    .string "equal"
#   [8432] = 'y greater'
    .string "y greater"
#   [8448] = 'range'
    .string "range"
