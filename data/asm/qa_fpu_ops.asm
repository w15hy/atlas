# qa_fpu_ops.asm - fi2f, fsqrt, fadd, fmul, fsub, and ff2i

    mov R0, 9
    fi2f R0
    fsqrt R0             # 3.0

    fmov R1, 1.5
    fadd R0, R1          # 4.5
    fmov R2, 2.0
    fmul R0, R2          # 9.0
    fmov R3, 1.0
    fsub R0, R3          # 8.0

    ff2i R0
    out R0               # expected: 8
    halt