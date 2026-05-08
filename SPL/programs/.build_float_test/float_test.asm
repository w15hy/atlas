# ========================================================================
#   Compilado por Atlas Compiler - codegen
#   code=[0..280)  data=[280..296)  strings=[296..60000)  SP=60000
# ========================================================================
.org 0

    call main
    halt

# 
# --- funcion main() ---
main:
    fmov R6, 3.14    # literal float
    storew R6, 280    # a = ...
    fmov R7, 2.5    # literal float
    storew R7, 288    # b = ...
    loadw R8, 280    # a
    fout R8    # print float
    mov R9, 0
    loadw R10, 288    # b
    fout R10    # print float
    mov R11, 0
    loadw R12, 280    # a
    loadw R13, 288    # b
    fadd R12, R13
    fout R12    # print float
    mov R6, 0
    loadw R7, 280    # a
    loadw R8, 288    # b
    fsub R7, R8
    fout R7    # print float
    mov R9, 0
    loadw R10, 280    # a
    loadw R11, 288    # b
    fmul R10, R11
    fout R10    # print float
    mov R13, 0
    loadw R12, 280    # a
    loadw R6, 288    # b
    fdiv R12, R6
    fout R12    # print float
    mov R8, 0
    mov R7, 0
    mov R0, R7    # valor de retorno
    ret

# ------------------------------------------------------------------------
#  Sección de datos (variables)  [280..296)
# ------------------------------------------------------------------------
    .fill 16
