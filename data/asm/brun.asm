mov  R1, 3          # número a verificar
    mov  R2, 1000         # límite superior
    fmov R14, 0.0       # acumulador B2

WHILE:
    cmp  R2, R1         # R2 - R1: si R1 > R2 → flag_N=1
    jn   END            # R1 > R2 → terminar

    # --- test primo para R1 ---
    mov  R4, 2
DIV_LOOP:
    cmp  R4, R1
    jz   IS_PRIME       # R4 == R1 → primo
    cmp  R1, R4
    jn   IS_PRIME       # R4 > R1  → primo
    mov  R5, R1
    mod  R5, R4
    cmp  R5, R3         # R3 = 0 siempre (lo inicializamos abajo)
    jz   NOT_PRIME
    inc  R4
    jmp  DIV_LOOP

NOT_PRIME:
    inc  R1
    jmp  WHILE

IS_PRIME:
    # --- guardar p en R9, calcular p+2 en R10 ---
    mov  R9, R1         # R9 = p
    mov  R10, R1
    addi R10, 2         # R10 = p+2

    # --- test primo para p+2 ---
    mov  R4, 2
DIV_LOOP2:
    cmp  R4, R10
    jz   TWIN_PRIME
    cmp  R10, R4
    jn   TWIN_PRIME
    mov  R5, R10
    mod  R5, R4
    cmp  R5, R3
    jz   NO_TWIN
    inc  R4
    jmp  DIV_LOOP2

NO_TWIN:
    inc  R1
    jmp  WHILE

TWIN_PRIME:
    # --- acumular 1/p + 1/(p+2) ---
    # convertir p a float y calcular 1/p
    mov  R11, R9        # R11 = p (entero)
    fi2f R11            # R11 = float(p)
    fmov R5, 1.0        # R5 = 1.0
    fdiv R5, R11        # R5 = 1/p

    # convertir p+2 a float y calcular 1/(p+2)
    mov  R11, R10       # R11 = p+2 (entero)
    fi2f R11            # R11 = float(p+2)
    fmov R6, 1.0        # R6 = 1.0
    fdiv R6, R11        # R6 = 1/(p+2)

    fadd R14, R5        # B2 += 1/p
    fadd R14, R6        # B2 += 1/(p+2)

    inc  R1
    jmp  WHILE

END:
    halt                # R14 = estimación de B2
