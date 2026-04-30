# qa_stack_call.asm - push/pop, xchg, call, and ret

    mov R0, 7
    mov R1, 9
    call SUM_SWAP
    out R2               # expected: 16
    halt

SUM_SWAP:
    push R0
    push R1
    pop R3
    pop R4
    xchg R3, R4
    add R3, R4
    mov R2, R3
    ret