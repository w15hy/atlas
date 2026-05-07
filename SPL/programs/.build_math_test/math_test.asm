# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..3800)  data=[3800..4064)  strings=[4064..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion abs(x) ---
abs:
    storew R0, 3800    # parametro x
    loadw R6, 3800    # x
    mov R7, 0
    cmp R6, R7
    jge if_next_2
    loadw R8, 3800    # x
    neg R8
    mov R0, R8    # valor de retorno
    ret
    jmp if_end_1
if_next_2:
if_end_1:
    loadw R9, 3800    # x
    mov R0, R9    # valor de retorno
    ret
# 
# --- funcion sign(x) ---
sign:
    storew R0, 3808    # parametro x
    loadw R10, 3808    # x
    mov R11, 0
    cmp R10, R11
    jg sk_5
    jmp if_next_4
sk_5:
    mov R12, 1
    mov R0, R12    # valor de retorno
    ret
    jmp if_end_3
if_next_4:
if_end_3:
    loadw R13, 3808    # x
    mov R6, 0
    cmp R13, R6
    jge if_next_7
    mov R7, 1
    neg R7
    mov R0, R7    # valor de retorno
    ret
    jmp if_end_6
if_next_7:
if_end_6:
    mov R8, 0
    mov R0, R8    # valor de retorno
    ret
# 
# --- funcion min(a, b) ---
min:
    storew R0, 3816    # parametro a
    storew R1, 3824    # parametro b
    loadw R9, 3816    # a
    loadw R10, 3824    # b
    cmp R9, R10
    jge if_next_9
    loadw R11, 3816    # a
    mov R0, R11    # valor de retorno
    ret
    jmp if_end_8
if_next_9:
if_end_8:
    loadw R12, 3824    # b
    mov R0, R12    # valor de retorno
    ret
# 
# --- funcion max(a, b) ---
max:
    storew R0, 3832    # parametro a
    storew R1, 3840    # parametro b
    loadw R13, 3832    # a
    loadw R6, 3840    # b
    cmp R13, R6
    jg sk_12
    jmp if_next_11
sk_12:
    loadw R7, 3832    # a
    mov R0, R7    # valor de retorno
    ret
    jmp if_end_10
if_next_11:
if_end_10:
    loadw R8, 3840    # b
    mov R0, R8    # valor de retorno
    ret
# 
# --- funcion clamp(x, lo, hi) ---
clamp:
    storew R0, 3848    # parametro x
    storew R1, 3856    # parametro lo
    storew R2, 3864    # parametro hi
    loadw R9, 3848    # x
    loadw R10, 3856    # lo
    cmp R9, R10
    jge if_next_14
    loadw R11, 3856    # lo
    mov R0, R11    # valor de retorno
    ret
    jmp if_end_13
if_next_14:
if_end_13:
    loadw R12, 3848    # x
    loadw R13, 3864    # hi
    cmp R12, R13
    jg sk_17
    jmp if_next_16
sk_17:
    loadw R6, 3864    # hi
    mov R0, R6    # valor de retorno
    ret
    jmp if_end_15
if_next_16:
if_end_15:
    loadw R7, 3848    # x
    mov R0, R7    # valor de retorno
    ret
# 
# --- funcion mod(a, b) ---
mod:
    storew R0, 3872    # parametro a
    storew R1, 3880    # parametro b
    loadw R8, 3880    # b
    mov R9, 0
    cmp R8, R9
    jne if_next_19
    mov R10, 0
    mov R0, R10    # valor de retorno
    ret
    jmp if_end_18
if_next_19:
if_end_18:
    loadw R11, 3872    # a
    loadw R12, 3872    # a
    loadw R13, 3880    # b
    div R12, R13
    loadw R6, 3880    # b
    mul R12, R6
    sub R11, R12
    mov R0, R11    # valor de retorno
    ret
# 
# --- funcion is_even(x) ---
is_even:
    storew R0, 3888    # parametro x
    loadw R7, 3888    # x
    mov R8, 2
    mov R0, R7    # arg1
    mov R1, R8    # arg2
    call mod
    mov R9, R0    # retorno de mod
    mov R10, 0
    cmp R9, R10
    jz cmp_t_20
    mov R9, 0
    jmp cmp_e_21
cmp_t_20:
    mov R9, 1
cmp_e_21:
    mov R0, R9    # valor de retorno
    ret
# 
# --- funcion is_odd(x) ---
is_odd:
    storew R0, 3896    # parametro x
    loadw R13, 3896    # x
    mov R6, 2
    mov R0, R13    # arg1
    mov R1, R6    # arg2
    call mod
    mov R12, R0    # retorno de mod
    mov R11, 0
    cmp R12, R11
    jne cmp_t_22
    mov R12, 0
    jmp cmp_e_23
cmp_t_22:
    mov R12, 1
cmp_e_23:
    mov R0, R12    # valor de retorno
    ret
# 
# --- funcion gcd(a, b) ---
gcd:
    storew R0, 3904    # parametro a
    storew R1, 3912    # parametro b
    loadw R7, 3904    # a
    storew R7, 3920    # x = ...
    loadw R8, 3912    # b
    storew R8, 3928    # y = ...
    loadw R10, 3920    # x
    mov R9, 0
    cmp R10, R9
    jge if_next_25
    loadw R13, 3920    # x
    neg R13
    storew R13, 3920    # x = ...
    jmp if_end_24
if_next_25:
if_end_24:
    loadw R6, 3928    # y
    mov R11, 0
    cmp R6, R11
    jge if_next_27
    loadw R12, 3928    # y
    neg R12
    storew R12, 3928    # y = ...
    jmp if_end_26
if_next_27:
if_end_26:
while_start_28:
    loadw R7, 3928    # y
    mov R8, 0
    cmp R7, R8
    jz while_end_29
    loadw R10, 3920    # x
    loadw R9, 3928    # y
    mov R0, R10    # arg1
    mov R1, R9    # arg2
    call mod
    mov R13, R0    # retorno de mod
    storew R13, 3936    # t = ...
    loadw R6, 3928    # y
    storew R6, 3920    # x = ...
    loadw R11, 3936    # t
    storew R11, 3928    # y = ...
    jmp while_start_28
while_end_29:
    loadw R12, 3920    # x
    mov R0, R12    # valor de retorno
    ret
# 
# --- funcion lcm(a, b) ---
lcm:
    storew R0, 3944    # parametro a
    storew R1, 3952    # parametro b
    loadw R7, 3944    # a
    mov R8, 0
    cmp R7, R8
    jz cmp_t_32
    mov R7, 0
    jmp cmp_e_33
cmp_t_32:
    mov R7, 1
cmp_e_33:
    mov R10, 0
    cmp R7, R10
    jne sc_short_34
    loadw R9, 3952    # b
    mov R13, 0
    cmp R9, R13
    jz cmp_t_36
    mov R9, 0
    jmp cmp_e_37
cmp_t_36:
    mov R9, 1
cmp_e_37:
    mov R7, R9
    jmp sc_end_35
sc_short_34:
    mov R7, 1
sc_end_35:
    mov R6, 0
    cmp R7, R6
    jz if_next_31
    mov R11, 0
    mov R0, R11    # valor de retorno
    ret
    jmp if_end_30
if_next_31:
if_end_30:
    loadw R12, 3944    # a
    loadw R8, 3952    # b
    mov R0, R12    # arg1
    mov R1, R8    # arg2
    call gcd
    mov R10, R0    # retorno de gcd
    storew R10, 3960    # g = ...
    loadw R13, 3944    # a
    loadw R9, 3952    # b
    mul R13, R9
    storew R13, 3968    # prod = ...
    loadw R6, 3968    # prod
    mov R7, 0
    cmp R6, R7
    jge if_next_39
    loadw R11, 3968    # prod
    neg R11
    storew R11, 3968    # prod = ...
    jmp if_end_38
if_next_39:
if_end_38:
    loadw R12, 3968    # prod
    loadw R8, 3960    # g
    div R12, R8
    mov R0, R12    # valor de retorno
    ret
# 
# --- funcion power(base, exp) ---
power:
    storew R0, 3976    # parametro base
    storew R1, 3984    # parametro exp
    loadw R10, 3984    # exp
    mov R9, 0
    cmp R10, R9
    jge if_next_41
    mov R13, 0
    mov R0, R13    # valor de retorno
    ret
    jmp if_end_40
if_next_41:
if_end_40:
    mov R6, 1
    storew R6, 3992    # result = ...
    loadw R7, 3976    # base
    storew R7, 4000    # b = ...
    loadw R11, 3984    # exp
    storew R11, 4008    # e = ...
while_start_42:
    loadw R8, 4008    # e
    mov R12, 0
    cmp R8, R12
    jg sk_44
    jmp while_end_43
sk_44:
    loadw R10, 4008    # e
    mov R0, R10    # arg1
    call is_odd
    mov R9, R0    # retorno de is_odd
    mov R13, 0
    cmp R9, R13
    jz if_next_46
    loadw R6, 3992    # result
    loadw R7, 4000    # b
    mul R6, R7
    storew R6, 3992    # result = ...
    jmp if_end_45
if_next_46:
if_end_45:
    loadw R11, 4000    # b
    loadw R8, 4000    # b
    mul R11, R8
    storew R11, 4000    # b = ...
    loadw R12, 4008    # e
    mov R10, 2
    div R12, R10
    storew R12, 4008    # e = ...
    jmp while_start_42
while_end_43:
    loadw R13, 3992    # result
    mov R0, R13    # valor de retorno
    ret
# 
# --- funcion isqrt(n) ---
isqrt:
    storew R0, 4016    # parametro n
    loadw R9, 4016    # n
    mov R7, 0
    cmp R9, R7
    jg if_next_48
    mov R6, 0
    mov R0, R6    # valor de retorno
    ret
    jmp if_end_47
if_next_48:
if_end_47:
    loadw R8, 4016    # n
    storew R8, 4024    # x = ...
    loadw R11, 4024    # x
    mov R10, 1
    add R11, R10
    mov R12, 2
    div R11, R12
    storew R11, 4032    # y = ...
while_start_49:
    loadw R13, 4032    # y
    loadw R9, 4024    # x
    cmp R13, R9
    jge while_end_50
    loadw R7, 4032    # y
    storew R7, 4024    # x = ...
    loadw R6, 4024    # x
    loadw R8, 4016    # n
    loadw R10, 4024    # x
    div R8, R10
    add R6, R8
    mov R12, 2
    div R6, R12
    storew R6, 4032    # y = ...
    jmp while_start_49
while_end_50:
    loadw R11, 4024    # x
    mov R0, R11    # valor de retorno
    ret
# 
# --- funcion factorial(n) ---
factorial:
    storew R0, 4040    # parametro n
    loadw R13, 4040    # n
    mov R9, 1
    cmp R13, R9
    jg if_next_52
    mov R7, 1
    mov R0, R7    # valor de retorno
    ret
    jmp if_end_51
if_next_52:
if_end_51:
    mov R10, 1
    storew R10, 4048    # result = ...
    mov R8, 2
    storew R8, 4056    # i = ...
while_start_53:
    loadw R12, 4056    # i
    loadw R6, 4040    # n
    cmp R12, R6
    jg while_end_54
    loadw R11, 4048    # result
    loadw R13, 4056    # i
    mul R11, R13
    storew R11, 4048    # result = ...
    loadw R9, 4056    # i
    mov R7, 1
    add R9, R7
    storew R9, 4056    # i = ...
    jmp while_start_53
while_end_54:
    loadw R10, 4048    # result
    mov R0, R10    # valor de retorno
    ret
# 
# --- funcion main() ---
main:
    mov R8, 7
    neg R8
    mov R0, R8    # arg1
    call abs
    mov R12, R0    # retorno de abs
    out R12    # print
    mov R6, 0
    mov R13, 3
    neg R13
    mov R0, R13    # arg1
    call sign
    mov R11, R0    # retorno de sign
    out R11    # print
    mov R7, 0
    mov R9, 0
    mov R0, R9    # arg1
    call sign
    mov R10, R0    # retorno de sign
    out R10    # print
    mov R8, 0
    mov R12, 5
    mov R0, R12    # arg1
    call sign
    mov R6, R0    # retorno de sign
    out R6    # print
    mov R13, 0
    mov R11, 3
    mov R7, 7
    mov R0, R11    # arg1
    mov R1, R7    # arg2
    call min
    mov R9, R0    # retorno de min
    out R9    # print
    mov R10, 0
    mov R8, 3
    mov R12, 7
    mov R0, R8    # arg1
    mov R1, R12    # arg2
    call max
    mov R6, R0    # retorno de max
    out R6    # print
    mov R13, 0
    mov R11, 15
    mov R7, 0
    mov R9, 10
    mov R0, R11    # arg1
    mov R1, R7    # arg2
    mov R2, R9    # arg3
    call clamp
    mov R10, R0    # retorno de clamp
    out R10    # print
    mov R8, 0
    mov R12, 2
    neg R12
    mov R6, 0
    mov R13, 10
    mov R0, R12    # arg1
    mov R1, R6    # arg2
    mov R2, R13    # arg3
    call clamp
    mov R11, R0    # retorno de clamp
    out R11    # print
    mov R7, 0
    mov R9, 17
    mov R10, 5
    mov R0, R9    # arg1
    mov R1, R10    # arg2
    call mod
    mov R8, R0    # retorno de mod
    out R8    # print
    mov R12, 0
    mov R6, 4
    mov R0, R6    # arg1
    call is_even
    mov R13, R0    # retorno de is_even
    out R13    # print
    mov R11, 0
    mov R7, 7
    mov R0, R7    # arg1
    call is_odd
    mov R9, R0    # retorno de is_odd
    out R9    # print
    mov R10, 0
    mov R8, 48
    mov R12, 18
    mov R0, R8    # arg1
    mov R1, R12    # arg2
    call gcd
    mov R6, R0    # retorno de gcd
    out R6    # print
    mov R13, 0
    mov R11, 4
    mov R7, 6
    mov R0, R11    # arg1
    mov R1, R7    # arg2
    call lcm
    mov R9, R0    # retorno de lcm
    out R9    # print
    mov R10, 0
    mov R8, 2
    mov R12, 10
    mov R0, R8    # arg1
    mov R1, R12    # arg2
    call power
    mov R6, R0    # retorno de power
    out R6    # print
    mov R13, 0
    mov R11, 3
    mov R7, 7
    mov R0, R11    # arg1
    mov R1, R7    # arg2
    call power
    mov R9, R0    # retorno de power
    out R9    # print
    mov R10, 0
    mov R8, 50
    mov R0, R8    # arg1
    call isqrt
    mov R12, R0    # retorno de isqrt
    out R12    # print
    mov R6, 0
    mov R13, 100
    mov R0, R13    # arg1
    call isqrt
    mov R11, R0    # retorno de isqrt
    out R11    # print
    mov R7, 0
    mov R9, 5
    mov R0, R9    # arg1
    call factorial
    mov R10, R0    # retorno de factorial
    out R10    # print
    mov R8, 0
    mov R12, 0
    mov R0, R12    # valor de retorno
    ret

# ------------------------------------------------------------------------
#  Sección de datos (variables)  [3800..4064)
# ------------------------------------------------------------------------
    .fill 264
