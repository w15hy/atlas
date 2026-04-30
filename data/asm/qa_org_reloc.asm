# qa_org_reloc.asm - .org plus relocatable jmp/call resolution

.org 4096

    jmp MAIN

DOUBLE:
    add R0, R0
    ret

MAIN:
    mov R0, 21
    call DOUBLE
    out R0               # expected: 42
    halt