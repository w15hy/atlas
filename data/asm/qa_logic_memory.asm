# qa_logic_memory.asm - byte and word memory, LEA, and bitwise ops

    mov R0, 320          # base address
    mov R1, 5            # index
    mov R3, 170          # 0b10101010

    # R4 = 320 + 5*1 + 2 = 327
    lea R4, R0, R1, 1, 2
    store R3, R4, 0
    load R5, R4, 0

    mov R6, 240          # 0b11110000
    and R5, R6           # 160
    mov R7, 15           # 0b00001111
    or  R5, R7           # 175
    xor R5, R7           # 160
    not R5
    not R5
    rol R5
    ror R5
    shr R5               # 80
    shl R5               # 160

    storew R5, 500
    loadw R8, 500
    out R8               # expected: 160
    halt