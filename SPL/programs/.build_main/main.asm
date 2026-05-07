# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..7528)  data=[7528..8328)  strings=[8328..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion vec_init(v, n) ---
vec_init:
    storew R0, 7528    # parametro v
    storew R1, 7536    # parametro n
    mov R6, 0
    loadw R7, 7536    # n
    muli R6, 8    # idx * word
    loadw R8, 7528    # base de v (ptr)
    add R6, R8    # idx*word + base
    storew R7, R6    # v[idx] = ...
    ret
# 
# --- funcion vec_len(v) ---
vec_len:
    storew R0, 7544    # parametro v
    mov R9, 0
    muli R9, 8
    loadw R10, 7544    # base de v (ptr)
    add R9, R10
    loadw R11, R9    # v[idx]
    mov R0, R11    # valor de retorno
    ret
# 
# --- funcion vec_get(v, i) ---
vec_get:
    storew R0, 7552    # parametro v
    storew R1, 7560    # parametro i
    loadw R12, 7560    # i
    mov R13, 1
    add R12, R13
    muli R12, 8
    loadw R8, 7552    # base de v (ptr)
    add R12, R8
    loadw R6, R12    # v[idx]
    mov R0, R6    # valor de retorno
    ret
# 
# --- funcion vec_set(v, i, val) ---
vec_set:
    storew R0, 7568    # parametro v
    storew R1, 7576    # parametro i
    storew R2, 7584    # parametro val
    loadw R7, 7576    # i
    mov R10, 1
    add R7, R10
    loadw R9, 7584    # val
    muli R7, 8    # idx * word
    loadw R11, 7568    # base de v (ptr)
    add R7, R11    # idx*word + base
    storew R9, R7    # v[idx] = ...
    ret
# 
# --- funcion vec_fill(v, val) ---
vec_fill:
    storew R0, 7592    # parametro v
    storew R1, 7600    # parametro val
    mov R13, 0
    muli R13, 8
    loadw R8, 7592    # base de v (ptr)
    add R13, R8
    loadw R12, R13    # v[idx]
    storew R12, 7608    # n = ...
    mov R6, 0
    storew R6, 7616    # i = ...
while_start_1:
    loadw R10, 7616    # i
    loadw R11, 7608    # n
    cmp R10, R11
    jge while_end_2
    loadw R7, 7616    # i
    mov R9, 1
    add R7, R9
    loadw R8, 7600    # val
    muli R7, 8    # idx * word
    loadw R13, 7592    # base de v (ptr)
    add R7, R13    # idx*word + base
    storew R8, R7    # v[idx] = ...
    loadw R12, 7616    # i
    mov R6, 1
    add R12, R6
    storew R12, 7616    # i = ...
    jmp while_start_1
while_end_2:
    ret
# 
# --- funcion vec_sum(v) ---
vec_sum:
    storew R0, 7624    # parametro v
    mov R10, 0
    muli R10, 8
    loadw R11, 7624    # base de v (ptr)
    add R10, R11
    loadw R9, R10    # v[idx]
    storew R9, 7632    # n = ...
    mov R13, 0
    storew R13, 7640    # s = ...
    mov R7, 0
    storew R7, 7648    # i = ...
while_start_3:
    loadw R8, 7648    # i
    loadw R6, 7632    # n
    cmp R8, R6
    jge while_end_4
    loadw R12, 7640    # s
    loadw R11, 7648    # i
    mov R10, 1
    add R11, R10
    muli R11, 8
    loadw R9, 7624    # base de v (ptr)
    add R11, R9
    loadw R13, R11    # v[idx]
    add R12, R13
    storew R12, 7640    # s = ...
    loadw R7, 7648    # i
    mov R8, 1
    add R7, R8
    storew R7, 7648    # i = ...
    jmp while_start_3
while_end_4:
    loadw R6, 7640    # s
    mov R0, R6    # valor de retorno
    ret
# 
# --- funcion vec_dot(a, b) ---
vec_dot:
    storew R0, 7656    # parametro a
    storew R1, 7664    # parametro b
    mov R10, 0
    muli R10, 8
    loadw R9, 7656    # base de a (ptr)
    add R10, R9
    loadw R11, R10    # a[idx]
    storew R11, 7672    # n = ...
    mov R13, 0
    storew R13, 7680    # s = ...
    mov R12, 0
    storew R12, 7688    # i = ...
while_start_5:
    loadw R8, 7688    # i
    loadw R7, 7672    # n
    cmp R8, R7
    jge while_end_6
    loadw R6, 7680    # s
    loadw R9, 7688    # i
    mov R10, 1
    add R9, R10
    muli R9, 8
    loadw R11, 7656    # base de a (ptr)
    add R9, R11
    loadw R13, R9    # a[idx]
    loadw R12, 7688    # i
    mov R8, 1
    add R12, R8
    muli R12, 8
    loadw R7, 7664    # base de b (ptr)
    add R12, R7
    loadw R10, R12    # b[idx]
    mul R13, R10
    add R6, R13
    storew R6, 7680    # s = ...
    loadw R11, 7688    # i
    mov R9, 1
    add R11, R9
    storew R11, 7688    # i = ...
    jmp while_start_5
while_end_6:
    loadw R8, 7680    # s
    mov R0, R8    # valor de retorno
    ret
# 
# --- funcion vec_add(a, b) ---
vec_add:
    storew R0, 7696    # parametro a
    storew R1, 7704    # parametro b
    mov R7, 0
    muli R7, 8
    loadw R12, 7696    # base de a (ptr)
    add R7, R12
    loadw R10, R7    # a[idx]
    storew R10, 7712    # n = ...
    mov R13, 0
    storew R13, 7720    # i = ...
while_start_7:
    loadw R6, 7720    # i
    loadw R9, 7712    # n
    cmp R6, R9
    jge while_end_8
    loadw R11, 7720    # i
    mov R8, 1
    add R11, R8
    loadw R12, 7720    # i
    mov R7, 1
    add R12, R7
    muli R12, 8
    loadw R10, 7696    # base de a (ptr)
    add R12, R10
    loadw R13, R12    # a[idx]
    loadw R6, 7720    # i
    mov R9, 1
    add R6, R9
    muli R6, 8
    loadw R8, 7704    # base de b (ptr)
    add R6, R8
    loadw R7, R6    # b[idx]
    add R13, R7
    muli R11, 8    # idx * word
    loadw R10, 7696    # base de a (ptr)
    add R11, R10    # idx*word + base
    storew R13, R11    # a[idx] = ...
    loadw R12, 7720    # i
    mov R9, 1
    add R12, R9
    storew R12, 7720    # i = ...
    jmp while_start_7
while_end_8:
    ret
# 
# --- funcion vec_sub(a, b) ---
vec_sub:
    storew R0, 7728    # parametro a
    storew R1, 7736    # parametro b
    mov R8, 0
    muli R8, 8
    loadw R6, 7728    # base de a (ptr)
    add R8, R6
    loadw R7, R8    # a[idx]
    storew R7, 7744    # n = ...
    mov R10, 0
    storew R10, 7752    # i = ...
while_start_9:
    loadw R11, 7752    # i
    loadw R13, 7744    # n
    cmp R11, R13
    jge while_end_10
    loadw R9, 7752    # i
    mov R12, 1
    add R9, R12
    loadw R6, 7752    # i
    mov R8, 1
    add R6, R8
    muli R6, 8
    loadw R7, 7728    # base de a (ptr)
    add R6, R7
    loadw R10, R6    # a[idx]
    loadw R11, 7752    # i
    mov R13, 1
    add R11, R13
    muli R11, 8
    loadw R12, 7736    # base de b (ptr)
    add R11, R12
    loadw R8, R11    # b[idx]
    sub R10, R8
    muli R9, 8    # idx * word
    loadw R7, 7728    # base de a (ptr)
    add R9, R7    # idx*word + base
    storew R10, R9    # a[idx] = ...
    loadw R6, 7752    # i
    mov R13, 1
    add R6, R13
    storew R6, 7752    # i = ...
    jmp while_start_9
while_end_10:
    ret
# 
# --- funcion vec_scale(v, k) ---
vec_scale:
    storew R0, 7760    # parametro v
    storew R1, 7768    # parametro k
    mov R12, 0
    muli R12, 8
    loadw R11, 7760    # base de v (ptr)
    add R12, R11
    loadw R8, R12    # v[idx]
    storew R8, 7776    # n = ...
    mov R7, 0
    storew R7, 7784    # i = ...
while_start_11:
    loadw R9, 7784    # i
    loadw R10, 7776    # n
    cmp R9, R10
    jge while_end_12
    loadw R13, 7784    # i
    mov R6, 1
    add R13, R6
    loadw R11, 7784    # i
    mov R12, 1
    add R11, R12
    muli R11, 8
    loadw R8, 7760    # base de v (ptr)
    add R11, R8
    loadw R7, R11    # v[idx]
    loadw R9, 7768    # k
    mul R7, R9
    muli R13, 8    # idx * word
    loadw R10, 7760    # base de v (ptr)
    add R13, R10    # idx*word + base
    storew R7, R13    # v[idx] = ...
    loadw R6, 7784    # i
    mov R12, 1
    add R6, R12
    storew R6, 7784    # i = ...
    jmp while_start_11
while_end_12:
    ret
# 
# --- funcion vec_max(v) ---
vec_max:
    storew R0, 7792    # parametro v
    mov R8, 0
    muli R8, 8
    loadw R11, 7792    # base de v (ptr)
    add R8, R11
    loadw R9, R8    # v[idx]
    storew R9, 7800    # n = ...
    mov R10, 1
    muli R10, 8
    loadw R13, 7792    # base de v (ptr)
    add R10, R13
    loadw R7, R10    # v[idx]
    storew R7, 7808    # m = ...
    mov R12, 1
    storew R12, 7816    # i = ...
while_start_13:
    loadw R6, 7816    # i
    loadw R11, 7800    # n
    cmp R6, R11
    jge while_end_14
    loadw R8, 7816    # i
    mov R9, 1
    add R8, R9
    muli R8, 8
    loadw R13, 7792    # base de v (ptr)
    add R8, R13
    loadw R10, R8    # v[idx]
    loadw R7, 7808    # m
    cmp R10, R7
    jg sk_17
    jmp if_next_16
sk_17:
    loadw R12, 7816    # i
    mov R6, 1
    add R12, R6
    muli R12, 8
    loadw R11, 7792    # base de v (ptr)
    add R12, R11
    loadw R9, R12    # v[idx]
    storew R9, 7808    # m = ...
    jmp if_end_15
if_next_16:
if_end_15:
    loadw R13, 7816    # i
    mov R8, 1
    add R13, R8
    storew R13, 7816    # i = ...
    jmp while_start_13
while_end_14:
    loadw R10, 7808    # m
    mov R0, R10    # valor de retorno
    ret
# 
# --- funcion vec_min(v) ---
vec_min:
    storew R0, 7824    # parametro v
    mov R7, 0
    muli R7, 8
    loadw R6, 7824    # base de v (ptr)
    add R7, R6
    loadw R11, R7    # v[idx]
    storew R11, 7832    # n = ...
    mov R12, 1
    muli R12, 8
    loadw R9, 7824    # base de v (ptr)
    add R12, R9
    loadw R8, R12    # v[idx]
    storew R8, 7840    # m = ...
    mov R13, 1
    storew R13, 7848    # i = ...
while_start_18:
    loadw R10, 7848    # i
    loadw R6, 7832    # n
    cmp R10, R6
    jge while_end_19
    loadw R7, 7848    # i
    mov R11, 1
    add R7, R11
    muli R7, 8
    loadw R9, 7824    # base de v (ptr)
    add R7, R9
    loadw R12, R7    # v[idx]
    loadw R8, 7840    # m
    cmp R12, R8
    jge if_next_21
    loadw R13, 7848    # i
    mov R10, 1
    add R13, R10
    muli R13, 8
    loadw R6, 7824    # base de v (ptr)
    add R13, R6
    loadw R11, R13    # v[idx]
    storew R11, 7840    # m = ...
    jmp if_end_20
if_next_21:
if_end_20:
    loadw R9, 7848    # i
    mov R7, 1
    add R9, R7
    storew R9, 7848    # i = ...
    jmp while_start_18
while_end_19:
    loadw R12, 7840    # m
    mov R0, R12    # valor de retorno
    ret
# 
# --- funcion vec_copy(dst, src) ---
vec_copy:
    storew R0, 7856    # parametro dst
    storew R1, 7864    # parametro src
    mov R8, 0
    muli R8, 8
    loadw R10, 7864    # base de src (ptr)
    add R8, R10
    loadw R6, R8    # src[idx]
    storew R6, 7872    # n = ...
    mov R13, 0
    loadw R11, 7872    # n
    muli R13, 8    # idx * word
    loadw R7, 7856    # base de dst (ptr)
    add R13, R7    # idx*word + base
    storew R11, R13    # dst[idx] = ...
    mov R9, 0
    storew R9, 7880    # i = ...
while_start_22:
    loadw R12, 7880    # i
    loadw R10, 7872    # n
    cmp R12, R10
    jge while_end_23
    loadw R8, 7880    # i
    mov R6, 1
    add R8, R6
    loadw R7, 7880    # i
    mov R13, 1
    add R7, R13
    muli R7, 8
    loadw R11, 7864    # base de src (ptr)
    add R7, R11
    loadw R9, R7    # src[idx]
    muli R8, 8    # idx * word
    loadw R12, 7856    # base de dst (ptr)
    add R8, R12    # idx*word + base
    storew R9, R8    # dst[idx] = ...
    loadw R10, 7880    # i
    mov R6, 1
    add R10, R6
    storew R10, 7880    # i = ...
    jmp while_start_22
while_end_23:
    ret
# 
# --- funcion vec_print(v) ---
vec_print:
    storew R0, 7888    # parametro v
    mov R13, 0
    muli R13, 8
    loadw R11, 7888    # base de v (ptr)
    add R13, R11
    loadw R7, R13    # v[idx]
    storew R7, 7896    # n = ...
    mov R12, 0
    storew R12, 7904    # i = ...
while_start_24:
    loadw R8, 7904    # i
    loadw R9, 7896    # n
    cmp R8, R9
    jge while_end_25
    loadw R6, 7904    # i
    mov R10, 1
    add R6, R10
    muli R6, 8
    loadw R11, 7888    # base de v (ptr)
    add R6, R11
    loadw R13, R6    # v[idx]
    out R13    # print
    mov R7, 0
    loadw R12, 7904    # i
    mov R8, 1
    add R12, R8
    storew R12, 7904    # i = ...
    jmp while_start_24
while_end_25:
    ret
# 
# --- funcion mat_init(m, rows, cols) ---
mat_init:
    storew R0, 7912    # parametro m
    storew R1, 7920    # parametro rows
    storew R2, 7928    # parametro cols
    mov R9, 0
    loadw R10, 7920    # rows
    muli R9, 8    # idx * word
    loadw R11, 7912    # base de m (ptr)
    add R9, R11    # idx*word + base
    storew R10, R9    # m[idx] = ...
    mov R6, 1
    loadw R13, 7928    # cols
    muli R6, 8    # idx * word
    loadw R7, 7912    # base de m (ptr)
    add R6, R7    # idx*word + base
    storew R13, R6    # m[idx] = ...
    ret
# 
# --- funcion mat_rows(m) ---
mat_rows:
    storew R0, 7936    # parametro m
    mov R8, 0
    muli R8, 8
    loadw R12, 7936    # base de m (ptr)
    add R8, R12
    loadw R11, R8    # m[idx]
    mov R0, R11    # valor de retorno
    ret
# 
# --- funcion mat_cols(m) ---
mat_cols:
    storew R0, 7944    # parametro m
    mov R9, 1
    muli R9, 8
    loadw R10, 7944    # base de m (ptr)
    add R9, R10
    loadw R7, R9    # m[idx]
    mov R0, R7    # valor de retorno
    ret
# 
# --- funcion mat_get(m, i, j) ---
mat_get:
    storew R0, 7952    # parametro m
    storew R1, 7960    # parametro i
    storew R2, 7968    # parametro j
    mov R6, 1
    muli R6, 8
    loadw R13, 7952    # base de m (ptr)
    add R6, R13
    loadw R12, R6    # m[idx]
    storew R12, 7976    # cols = ...
    loadw R8, 7960    # i
    loadw R11, 7976    # cols
    mul R8, R11
    loadw R10, 7968    # j
    add R8, R10
    mov R9, 2
    add R8, R9
    muli R8, 8
    loadw R7, 7952    # base de m (ptr)
    add R8, R7
    loadw R13, R8    # m[idx]
    mov R0, R13    # valor de retorno
    ret
# 
# --- funcion mat_set(m, i, j, val) ---
mat_set:
    storew R0, 7984    # parametro m
    storew R1, 7992    # parametro i
    storew R2, 8000    # parametro j
    storew R3, 8008    # parametro val
    mov R6, 1
    muli R6, 8
    loadw R12, 7984    # base de m (ptr)
    add R6, R12
    loadw R11, R6    # m[idx]
    storew R11, 8016    # cols = ...
    loadw R10, 7992    # i
    loadw R9, 8016    # cols
    mul R10, R9
    loadw R7, 8000    # j
    add R10, R7
    mov R8, 2
    add R10, R8
    loadw R13, 8008    # val
    muli R10, 8    # idx * word
    loadw R12, 7984    # base de m (ptr)
    add R10, R12    # idx*word + base
    storew R13, R10    # m[idx] = ...
    ret
# 
# --- funcion mat_fill(m, val) ---
mat_fill:
    storew R0, 8024    # parametro m
    storew R1, 8032    # parametro val
    mov R6, 0
    muli R6, 8
    loadw R11, 8024    # base de m (ptr)
    add R6, R11
    loadw R9, R6    # m[idx]
    storew R9, 8040    # rows = ...
    mov R7, 1
    muli R7, 8
    loadw R8, 8024    # base de m (ptr)
    add R7, R8
    loadw R12, R7    # m[idx]
    storew R12, 8048    # cols = ...
    loadw R10, 8040    # rows
    loadw R13, 8048    # cols
    mul R10, R13
    storew R10, 8056    # total = ...
    mov R11, 0
    storew R11, 8064    # k = ...
while_start_26:
    loadw R6, 8064    # k
    loadw R9, 8056    # total
    cmp R6, R9
    jge while_end_27
    loadw R8, 8064    # k
    mov R7, 2
    add R8, R7
    loadw R12, 8032    # val
    muli R8, 8    # idx * word
    loadw R13, 8024    # base de m (ptr)
    add R8, R13    # idx*word + base
    storew R12, R8    # m[idx] = ...
    loadw R10, 8064    # k
    mov R11, 1
    add R10, R11
    storew R10, 8064    # k = ...
    jmp while_start_26
while_end_27:
    ret
# 
# --- funcion mat_mul(a, b, c) ---
mat_mul:
    storew R0, 8072    # parametro a
    storew R1, 8080    # parametro b
    storew R2, 8088    # parametro c
    mov R6, 0
    muli R6, 8
    loadw R9, 8072    # base de a (ptr)
    add R6, R9
    loadw R7, R6    # a[idx]
    storew R7, 8096    # ar = ...
    mov R13, 1
    muli R13, 8
    loadw R8, 8072    # base de a (ptr)
    add R13, R8
    loadw R12, R13    # a[idx]
    storew R12, 8104    # ac = ...
    mov R11, 1
    muli R11, 8
    loadw R10, 8080    # base de b (ptr)
    add R11, R10
    loadw R9, R11    # b[idx]
    storew R9, 8112    # bc = ...
    mov R6, 0
    loadw R7, 8096    # ar
    muli R6, 8    # idx * word
    loadw R8, 8088    # base de c (ptr)
    add R6, R8    # idx*word + base
    storew R7, R6    # c[idx] = ...
    mov R13, 1
    loadw R12, 8112    # bc
    muli R13, 8    # idx * word
    loadw R10, 8088    # base de c (ptr)
    add R13, R10    # idx*word + base
    storew R12, R13    # c[idx] = ...
    mov R11, 0
    storew R11, 8120    # i = ...
while_start_28:
    loadw R9, 8120    # i
    loadw R8, 8096    # ar
    cmp R9, R8
    jge while_end_29
    mov R6, 0
    storew R6, 8128    # j = ...
while_start_30:
    loadw R7, 8128    # j
    loadw R10, 8112    # bc
    cmp R7, R10
    jge while_end_31
    mov R13, 0
    storew R13, 8136    # acc = ...
    mov R12, 0
    storew R12, 8144    # k = ...
while_start_32:
    loadw R11, 8144    # k
    loadw R9, 8104    # ac
    cmp R11, R9
    jge while_end_33
    loadw R8, 8136    # acc
    loadw R6, 8120    # i
    loadw R7, 8104    # ac
    mul R6, R7
    loadw R10, 8144    # k
    add R6, R10
    mov R13, 2
    add R6, R13
    muli R6, 8
    loadw R12, 8072    # base de a (ptr)
    add R6, R12
    loadw R11, R6    # a[idx]
    loadw R9, 8144    # k
    loadw R7, 8112    # bc
    mul R9, R7
    loadw R10, 8128    # j
    add R9, R10
    mov R13, 2
    add R9, R13
    muli R9, 8
    loadw R12, 8080    # base de b (ptr)
    add R9, R12
    loadw R6, R9    # b[idx]
    mul R11, R6
    add R8, R11
    storew R8, 8136    # acc = ...
    loadw R7, 8144    # k
    mov R10, 1
    add R7, R10
    storew R7, 8144    # k = ...
    jmp while_start_32
while_end_33:
    loadw R13, 8120    # i
    loadw R12, 8112    # bc
    mul R13, R12
    loadw R9, 8128    # j
    add R13, R9
    mov R6, 2
    add R13, R6
    loadw R11, 8136    # acc
    muli R13, 8    # idx * word
    loadw R8, 8088    # base de c (ptr)
    add R13, R8    # idx*word + base
    storew R11, R13    # c[idx] = ...
    loadw R10, 8128    # j
    mov R7, 1
    add R10, R7
    storew R10, 8128    # j = ...
    jmp while_start_30
while_end_31:
    loadw R12, 8120    # i
    mov R9, 1
    add R12, R9
    storew R12, 8120    # i = ...
    jmp while_start_28
while_end_29:
    ret
# 
# --- funcion mat_print(m) ---
mat_print:
    storew R0, 8152    # parametro m
    mov R6, 0
    muli R6, 8
    loadw R8, 8152    # base de m (ptr)
    add R6, R8
    loadw R13, R6    # m[idx]
    storew R13, 8160    # rows = ...
    mov R11, 1
    muli R11, 8
    loadw R7, 8152    # base de m (ptr)
    add R11, R7
    loadw R10, R11    # m[idx]
    storew R10, 8168    # cols = ...
    mov R9, 0
    storew R9, 8176    # i = ...
while_start_34:
    loadw R12, 8176    # i
    loadw R8, 8160    # rows
    cmp R12, R8
    jge while_end_35
    mov R6, 0
    storew R6, 8184    # j = ...
while_start_36:
    loadw R13, 8184    # j
    loadw R7, 8168    # cols
    cmp R13, R7
    jge while_end_37
    loadw R11, 8176    # i
    loadw R10, 8168    # cols
    mul R11, R10
    loadw R9, 8184    # j
    add R11, R9
    mov R12, 2
    add R11, R12
    muli R11, 8
    loadw R8, 8152    # base de m (ptr)
    add R11, R8
    loadw R6, R11    # m[idx]
    out R6    # print
    mov R13, 0
    loadw R7, 8184    # j
    mov R10, 1
    add R7, R10
    storew R7, 8184    # j = ...
    jmp while_start_36
while_end_37:
    loadw R9, 8176    # i
    mov R12, 1
    add R9, R12
    storew R9, 8176    # i = ...
    jmp while_start_34
while_end_35:
    ret
# 
# --- funcion sum(a, b) ---
sum:
    storew R0, 8192    # parametro a
    storew R1, 8200    # parametro b
    loadw R8, 8192    # a
    loadw R11, 8200    # b
    add R8, R11
    mov R0, R8    # valor de retorno
    ret
# 
# --- funcion main() ---
main:
    mov R6, 10
    storew R6, 8208    # x = ...
    mov R13, 20
    storew R13, 8216    # y = ...
    fmov R10, 3.14    # literal float
    storew R10, 8224    # z = ...
    mov R7, 8328    # &"full coverage test"
    storew R7, 8232    # msg = ...
    loadw R12, 8208    # x
    storew R12, 8240    # n.id = ...
    loadw R9, 8224    # z
    storew R9, 8248    # n.value = ...
    mov R11, 8352    # &"node"
    storew R11, 8256    # n.name = ...
# ; arreglo arr base=8264
    mov R8, 8264    # &arr
    push R8    # spill arg para vec_init
    mov R6, 5
    push R6    # spill arg para vec_init
    pop R1    # arg2
    pop R0    # arg1
    call vec_init
    mov R13, R0    # retorno de vec_init
    mov R10, 8264    # &arr
    push R10    # spill arg para vec_fill
    mov R7, 0
    push R7    # spill arg para vec_fill
    pop R1    # arg2
    pop R0    # arg1
    call vec_fill
    mov R12, R0    # retorno de vec_fill
    mov R9, 8264    # &arr
    push R9    # spill arg para vec_set
    mov R11, 0
    push R11    # spill arg para vec_set
    loadw R8, 8208    # x
    push R8    # spill arg para vec_set
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call vec_set
    mov R6, R0    # retorno de vec_set
    mov R13, 8264    # &arr
    push R13    # spill arg para vec_set
    mov R10, 1
    push R10    # spill arg para vec_set
    loadw R7, 8216    # y
    push R7    # spill arg para vec_set
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call vec_set
    mov R12, R0    # retorno de vec_set
    mov R9, 8264    # &arr
    push R9    # spill arg para vec_set
    mov R11, 2
    push R11    # spill arg para vec_set
    loadw R8, 8208    # x
    push R8    # spill arg para sum
    loadw R6, 8216    # y
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
    mov R7, 8264    # &arr
    push R7    # spill arg para vec_set
    mov R12, 3
    push R12    # spill arg para vec_set
    loadw R9, 8208    # x
    mov R11, 2
    mul R9, R11
    push R9    # spill arg para vec_set
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call vec_set
    mov R8, R0    # retorno de vec_set
    mov R6, 8264    # &arr
    push R6    # spill arg para vec_set
    mov R13, 4
    push R13    # spill arg para vec_set
    loadw R10, 8216    # y
    mov R7, 2
    mul R10, R7
    push R10    # spill arg para vec_set
    pop R2    # arg3
    pop R1    # arg2
    pop R0    # arg1
    call vec_set
    mov R12, R0    # retorno de vec_set
    mov R11, 8264    # &arr
    push R11    # spill arg para vec_len
    pop R0    # arg1
    call vec_len
    mov R9, R0    # retorno de vec_len
    out R9    # print
    mov R8, 0
    mov R6, 8264    # &arr
    push R6    # spill arg para vec_get
    mov R13, 0
    push R13    # spill arg para vec_get
    pop R1    # arg2
    pop R0    # arg1
    call vec_get
    mov R7, R0    # retorno de vec_get
    out R7    # print
    mov R10, 0
    mov R12, 8264    # &arr
    push R12    # spill arg para vec_get
    mov R11, 1
    push R11    # spill arg para vec_get
    pop R1    # arg2
    pop R0    # arg1
    call vec_get
    mov R9, R0    # retorno de vec_get
    out R9    # print
    mov R8, 0
    mov R6, 8264    # &arr
    push R6    # spill arg para vec_sum
    pop R0    # arg1
    call vec_sum
    mov R13, R0    # retorno de vec_sum
    out R13    # print
    mov R7, 0
    mov R10, 8264    # &arr
    push R10    # spill arg para vec_max
    pop R0    # arg1
    call vec_max
    mov R12, R0    # retorno de vec_max
    out R12    # print
    mov R11, 0
    mov R9, 8264    # &arr
    push R9    # spill arg para vec_min
    pop R0    # arg1
    call vec_min
    mov R8, R0    # retorno de vec_min
    out R8    # print
    mov R6, 0
    loadw R13, 8208    # x
    loadw R7, 8216    # y
    cmp R13, R7
    jg sk_40
    jmp if_next_39
sk_40:
    mov R10, 8360    # &"x greater"
    storew R10, 8232    # msg = ...
    jmp if_end_38
if_next_39:
    loadw R12, 8208    # x
    loadw R11, 8216    # y
    cmp R12, R11
    jne if_next_41
    mov R9, 8376    # &"equal"
    storew R9, 8232    # msg = ...
    jmp if_end_38
if_next_41:
    mov R8, 8384    # &"y greater"
    storew R8, 8232    # msg = ...
if_end_38:
    loadw R6, 8232    # msg
    outs R6    # print string
    mov R13, 0
while_start_42:
    loadw R7, 8208    # x
    mov R10, 0
    cmp R7, R10
    jz while_end_43
    loadw R12, 8208    # x
    mov R11, 1
    sub R12, R11
    storew R12, 8208    # x = ...
    loadw R9, 8208    # x
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
    storew R6, 8312    # i = ...
for_start_46:
    loadw R13, 8312    # i
    mov R7, 10
    cmp R13, R7
    jge for_end_48
    loadw R10, 8224    # z
    fmov R11, 0.5    # literal float
    fadd R10, R11
    storew R10, 8224    # z = ...
    jmp for_update_47    # continue
for_update_47:
    loadw R12, 8312    # i
    mov R9, 1
    add R12, R9
    storew R12, 8312    # i = ...
    jmp for_start_46
for_end_48:
    mov R8, 5
    mov R6, 3
    add R8, R6
    mov R13, 2
    mov R7, 4
    mul R13, R7
    mov R11, 2
    div R13, R11
    sub R8, R13
    storew R8, 8320    # a = ...
    loadw R10, 8320    # a
    mov R9, 0
    cmp R10, R9
    jge cmp_t_51
    mov R10, 0
    jmp cmp_e_52
cmp_t_51:
    mov R10, 1
cmp_e_52:
    mov R12, 0
    cmp R10, R12
    jz sc_short_53
    loadw R6, 8320    # a
    mov R7, 100
    cmp R6, R7
    jn cmp_t_55
    mov R6, 0
    jmp cmp_e_56
cmp_t_55:
    mov R6, 1
cmp_e_56:
    mov R10, R6
    jmp sc_end_54
sc_short_53:
    mov R10, 0
sc_end_54:
    mov R11, 0
    cmp R10, R11
    jz if_next_50
    mov R13, 8400    # &"range"
    storew R13, 8232    # msg = ...
    jmp if_end_49
if_next_50:
if_end_49:
    loadw R8, 8232    # msg
    outs R8    # print string
    mov R9, 0
    mov R12, 0
    mov R0, R12    # valor de retorno
    ret

# ------------------------------------------------------------------------
#  Sección de datos (variables)  [7528..8328)
# ------------------------------------------------------------------------
    .fill 800

# ------------------------------------------------------------------------
#  Sección de strings  [8328..)
# ------------------------------------------------------------------------
#   [8328] = 'full coverage test'
    .string "full coverage test"
#   [8352] = 'node'
    .string "node"
#   [8360] = 'x greater'
    .string "x greater"
#   [8376] = 'equal'
    .string "equal"
#   [8384] = 'y greater'
    .string "y greater"
#   [8400] = 'range'
    .string "range"
