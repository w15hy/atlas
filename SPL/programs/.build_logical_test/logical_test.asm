# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..1656)  data=[1656..1680)  strings=[1680..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion main() ---
main:
    mov R6, 5
    storew R6, 1656    # a = ...
    mov R7, 3
    storew R7, 1664    # b = ...
    mov R8, 0
    storew R8, 1672    # c = ...
    loadw R9, 1672    # c
    mov R10, 0
    cmp R9, R10
    jz not_z_3
    mov R9, 0
    jmp not_e_4
not_z_3:
    mov R9, 1
not_e_4:
    mov R11, 0
    cmp R9, R11
    jz if_next_2
    mov R12, 1
    out R12    # print
    mov R13, 0
    jmp if_end_1
if_next_2:
if_end_1:
    loadw R6, 1656    # a
    mov R7, 0
    cmp R6, R7
    jz not_z_7
    mov R6, 0
    jmp not_e_8
not_z_7:
    mov R6, 1
not_e_8:
    mov R8, 0
    cmp R6, R8
    jz if_next_6
    mov R10, 99
    out R10    # print
    mov R11, 0
    jmp if_end_5
if_next_6:
if_end_5:
    loadw R9, 1656    # a
    mov R12, 0
    cmp R9, R12
    jg cmp_t_11
    mov R9, 0
    jmp cmp_e_12
cmp_t_11:
    mov R9, 1
cmp_e_12:
    mov R13, 0
    cmp R9, R13
    jne sc_short_13
    loadw R7, 1664    # b
    mov R8, 10
    cmp R7, R8
    jg cmp_t_15
    mov R7, 0
    jmp cmp_e_16
cmp_t_15:
    mov R7, 1
cmp_e_16:
    mov R6, 0
    cmp R7, R6
    jz sc_short_17
    loadw R10, 1672    # c
    mov R11, 0
    cmp R10, R11
    jg cmp_t_19
    mov R10, 0
    jmp cmp_e_20
cmp_t_19:
    mov R10, 1
cmp_e_20:
    mov R7, R10
    jmp sc_end_18
sc_short_17:
    mov R7, 0
sc_end_18:
    mov R9, R7
    jmp sc_end_14
sc_short_13:
    mov R9, 1
sc_end_14:
    mov R12, 0
    cmp R9, R12
    jz if_next_10
    mov R13, 2
    out R13    # print
    mov R8, 0
    jmp if_end_9
if_next_10:
if_end_9:
    loadw R6, 1656    # a
    loadw R11, 1664    # b
    cmp R6, R11
    jg cmp_t_23
    mov R6, 0
    jmp cmp_e_24
cmp_t_23:
    mov R6, 1
cmp_e_24:
    mov R10, 0
    cmp R6, R10
    jz sc_short_25
    loadw R7, 1656    # a
    mov R12, 0
    cmp R7, R12
    jg cmp_t_27
    mov R7, 0
    jmp cmp_e_28
cmp_t_27:
    mov R7, 1
cmp_e_28:
    mov R6, R7
    jmp sc_end_26
sc_short_25:
    mov R6, 0
sc_end_26:
    mov R9, 0
    cmp R6, R9
    jz if_next_22
    mov R13, 3
    out R13    # print
    mov R8, 0
    jmp if_end_21
if_next_22:
if_end_21:
    loadw R11, 1656    # a
    loadw R10, 1664    # b
    cmp R11, R10
    jg cmp_t_31
    mov R11, 0
    jmp cmp_e_32
cmp_t_31:
    mov R11, 1
cmp_e_32:
    mov R12, 0
    cmp R11, R12
    jz sc_short_33
    loadw R7, 1656    # a
    mov R9, 0
    cmp R7, R9
    jg cmp_t_35
    mov R7, 0
    jmp cmp_e_36
cmp_t_35:
    mov R7, 1
cmp_e_36:
    mov R11, R7
    jmp sc_end_34
sc_short_33:
    mov R11, 0
sc_end_34:
    mov R6, 0
    cmp R11, R6
    jz if_next_30
    mov R13, 4
    out R13    # print
    mov R8, 0
    jmp if_end_29
if_next_30:
if_end_29:
    loadw R10, 1672    # c
    mov R12, 0
    cmp R10, R12
    jg cmp_t_39
    mov R10, 0
    jmp cmp_e_40
cmp_t_39:
    mov R10, 1
cmp_e_40:
    mov R9, 0
    cmp R10, R9
    jne sc_short_41
    loadw R7, 1656    # a
    mov R6, 0
    cmp R7, R6
    jg cmp_t_43
    mov R7, 0
    jmp cmp_e_44
cmp_t_43:
    mov R7, 1
cmp_e_44:
    mov R10, R7
    jmp sc_end_42
sc_short_41:
    mov R10, 1
sc_end_42:
    mov R11, 0
    cmp R10, R11
    jz if_next_38
    mov R13, 5
    out R13    # print
    mov R8, 0
    jmp if_end_37
if_next_38:
if_end_37:
    loadw R12, 1672    # c
    mov R9, 0
    cmp R12, R9
    jg cmp_t_47
    mov R12, 0
    jmp cmp_e_48
cmp_t_47:
    mov R12, 1
cmp_e_48:
    mov R6, 0
    cmp R12, R6
    jne sc_short_49
    loadw R7, 1656    # a
    mov R11, 0
    cmp R7, R11
    jg cmp_t_51
    mov R7, 0
    jmp cmp_e_52
cmp_t_51:
    mov R7, 1
cmp_e_52:
    mov R12, R7
    jmp sc_end_50
sc_short_49:
    mov R12, 1
sc_end_50:
    mov R10, 0
    cmp R12, R10
    jz if_next_46
    mov R13, 6
    out R13    # print
    mov R8, 0
    jmp if_end_45
if_next_46:
if_end_45:
    loadw R9, 1656    # a
    mov R6, 0
    cmp R9, R6
    jz not_z_55
    mov R9, 0
    jmp not_e_56
not_z_55:
    mov R9, 1
not_e_56:
    mov R11, 0
    cmp R9, R11
    jz not_z_57
    mov R9, 0
    jmp not_e_58
not_z_57:
    mov R9, 1
not_e_58:
    mov R7, 0
    cmp R9, R7
    jz if_next_54
    mov R10, 7
    out R10    # print
    mov R12, 0
    jmp if_end_53
if_next_54:
if_end_53:
    mov R13, 0
    mov R0, R13    # valor de retorno
    ret

# ------------------------------------------------------------------------
#  Sección de datos (variables)  [1656..1680)
# ------------------------------------------------------------------------
    .fill 24
