# ============================================================
# vecmat.asm  —  Biblioteca estándar: Vectores y Matrices
# Máquina Von Neumann sy_00
# ============================================================
#
# CÓMO INCLUIR:
#   Al inicio de tu programa .asm escribe:
#       jmp MAIN
#       #include <stdlib/vecmat.asm>
#   MAIN:
#       ...
#
# CONVENCIÓN DE LLAMADA:
#   Argumentos   : R0, R1, R2, R3  (en orden)
#   Valor retorno: R0
#   Scratch      : R4, R5, R6, R7  (pueden ser modificados)
#   Llamada      : call NOMBRE_FUNCION   →   ret  (dentro)
#
# ============================================================
# LAYOUT EN MEMORIA — VECTOR
#   mem[base + 0]         = N  (longitud)
#   mem[base + 1]         = elem[0]
#   mem[base + 2]         = elem[1]
#   ...
#   mem[base + N]         = elem[N-1]
#
# LAYOUT EN MEMORIA — MATRIZ  (row-major)
#   mem[base + 0]         = filas
#   mem[base + 1]         = cols
#   mem[base + 2]         = mat[0][0]
#   mem[base + 3]         = mat[0][1]
#   ...
#   mem[base + 2 + i*C+j] = mat[i][j]
# ============================================================

# ============================================================
#  ██╗   ██╗███████╗ ██████╗████████╗ ██████╗ ██████╗ ███████╗
#  ██║   ██║██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝
#  ██║   ██║█████╗  ██║        ██║   ██║   ██║██████╔╝█████╗
#  ╚██╗ ██╔╝██╔══╝  ██║        ██║   ██║   ██║██╔══██╗██╔══╝
#   ╚████╔╝ ███████╗╚██████╗   ██║   ╚██████╔╝██║  ██║███████╗
#    ╚═══╝  ╚══════╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝
# ============================================================

# ------------------------------------------------------------
# VEC_INIT — Inicializa un vector (escribe la longitud N)
# Entrada : R0 = dirección base en RAM
#           R1 = longitud N
# Salida  : ninguna
# ------------------------------------------------------------
VEC_INIT:
    store R1, R0, 0, 0          # mem[base] = N
    ret

# ------------------------------------------------------------
# VEC_LEN — Retorna la longitud del vector
# Entrada : R0 = base
# Salida  : R0 = longitud N
# ------------------------------------------------------------
VEC_LEN:
    load  R0, R0, 0, 0          # R0 = mem[base]
    ret

# ------------------------------------------------------------
# VEC_SET — Escribe el elemento en la posición dada
# Entrada : R0 = base, R1 = índice (0-based), R2 = valor
# Salida  : ninguna
# ------------------------------------------------------------
VEC_SET:
    addi  R1, 1                 # R1 = índice + 1  (saltar cabecera)
    lea   R3, R0, R1, 1, 0      # R3 = base + (índice+1)
    store R2, R3, 0, 0          # mem[R3] = valor
    ret

# ------------------------------------------------------------
# VEC_GET — Lee el elemento en la posición dada
# Entrada : R0 = base, R1 = índice (0-based)
# Salida  : R0 = valor del elemento
# ------------------------------------------------------------
VEC_GET:
    addi  R1, 1                 # R1 = índice + 1
    lea   R3, R0, R1, 1, 0      # R3 = dirección del elemento
    load  R0, R3, 0, 0          # R0 = mem[R3]
    ret

# ------------------------------------------------------------
# VEC_FILL — Rellena todos los elementos con un valor fijo
# Entrada : R0 = base, R1 = valor
# Salida  : ninguna
# Clobbers: R4, R5
# ------------------------------------------------------------
VEC_FILL:
    load  R4, R0, 0, 0          # R4 = longitud
    addi  R0, 1                 # R0 = primer elemento
    mov   R5, R0                # R5 = cursor
_VF_LOOP:
    store R1, R5, 0, 0          # mem[cursor] = valor
    addi  R5, 1                 # cursor++
    dec   R4                    # contador--
    jnz   _VF_LOOP
    ret

# ------------------------------------------------------------
# VEC_SUM — Suma todos los elementos del vector
# Entrada : R0 = base
# Salida  : R0 = suma de todos los elementos
# Clobbers: R4, R5, R6, R7
# ------------------------------------------------------------
VEC_SUM:
    load  R4, R0, 0, 0          # R4 = longitud
    addi  R0, 1                 # R0 = dirección primer elemento
    mov   R5, R0                # R5 = cursor
    mov   R6, 0                 # R6 = acumulador = 0
_VS_LOOP:
    load  R7, R5, 0, 0          # R7 = mem[cursor]
    add   R6, R7                # acumulador += R7
    addi  R5, 1                 # cursor++
    dec   R4                    # contador--
    jnz   _VS_LOOP
    mov   R0, R6                # R0 = resultado
    ret

# ------------------------------------------------------------
# VEC_COPY — Copia un vector completo a otra dirección
# Entrada : R0 = base_origen, R1 = base_destino
# Salida  : ninguna
# Nota    : destino debe tener espacio suficiente (N+1 bytes)
# Clobbers: R4, R5
# ------------------------------------------------------------
VEC_COPY:
    load  R4, R0, 0, 0          # R4 = longitud
    store R4, R1, 0, 0          # mem[dst+0] = longitud (cabecera)
    addi  R0, 1                 # R0 = primer elemento origen
    addi  R1, 1                 # R1 = primer elemento destino
_VC_LOOP:
    load  R5, R0, 0, 0          # R5 = elem origen
    store R5, R1, 0, 0          # mem[dst] = R5
    addi  R0, 1
    addi  R1, 1
    dec   R4
    jnz   _VC_LOOP
    ret

# ------------------------------------------------------------
# VEC_ADD — Suma vectorial elemento a elemento:  A[i] += B[i]
# Entrada : R0 = base_A, R1 = base_B  (misma longitud N)
# Salida  : resultado almacenado en el vector A
# Clobbers: R4, R5, R6
# ------------------------------------------------------------
VEC_ADD:
    load  R4, R0, 0, 0          # R4 = longitud
    addi  R0, 1                 # R0 = primer elemento de A
    addi  R1, 1                 # R1 = primer elemento de B
_VA_LOOP:
    load  R5, R0, 0, 0          # R5 = A[i]
    load  R6, R1, 0, 0          # R6 = B[i]
    add   R5, R6                # R5 = A[i] + B[i]
    store R5, R0, 0, 0          # A[i] = R5
    addi  R0, 1
    addi  R1, 1
    dec   R4
    jnz   _VA_LOOP
    ret


# ============================================================
#  ███╗   ███╗ █████╗ ████████╗██████╗ ██╗███████╗
#  ████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗██║╚══███╔╝
#  ██╔████╔██║███████║   ██║   ██████╔╝██║  ███╔╝
#  ██║╚██╔╝██║██╔══██║   ██║   ██╔══██╗██║ ███╔╝
#  ██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║██║███████╗
#  ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝
# ============================================================

# ------------------------------------------------------------
# MAT_INIT — Inicializa la cabecera de una matriz
# Entrada : R0 = base, R1 = filas, R2 = columnas
# Salida  : ninguna
# ------------------------------------------------------------
MAT_INIT:
    store R1, R0, 0, 0          # mem[base]   = filas
    store R2, R0, 0, 1          # mem[base+1] = cols
    ret

# ------------------------------------------------------------
# MAT_ROWS — Retorna el número de filas
# Entrada : R0 = base
# Salida  : R0 = filas
# ------------------------------------------------------------
MAT_ROWS:
    load  R0, R0, 0, 0          # R0 = mem[base]
    ret

# ------------------------------------------------------------
# MAT_COLS — Retorna el número de columnas
# Entrada : R0 = base
# Salida  : R0 = cols
# ------------------------------------------------------------
MAT_COLS:
    load  R0, R0, 0, 1          # R0 = mem[base+1]
    ret

# ------------------------------------------------------------
# MAT_GET — Lee mat[fila][col]
# Entrada : R0 = base, R1 = fila, R2 = col
# Salida  : R0 = valor
# Clobbers: R4, R5
# Fórmula : addr = base + 2 + fila*cols + col
# ------------------------------------------------------------
MAT_GET:
    load  R4, R0, 0, 1          # R4 = cols
    mul   R1, R4                # R1 = fila * cols
    add   R1, R2                # R1 = fila*cols + col
    addi  R1, 2                 # R1 += 2  (saltar cabecera)
    lea   R5, R0, R1, 1, 0      # R5 = base + offset
    load  R0, R5, 0, 0          # R0 = mem[R5]
    ret

# ------------------------------------------------------------
# MAT_SET — Escribe mat[fila][col] = val
# Entrada : R0 = base, R1 = fila, R2 = col, R3 = valor
# Salida  : ninguna
# Clobbers: R4, R5
# ------------------------------------------------------------
MAT_SET:
    load  R4, R0, 0, 1          # R4 = cols
    mul   R1, R4                # R1 = fila * cols
    add   R1, R2                # R1 = fila*cols + col
    addi  R1, 2                 # R1 += 2
    lea   R5, R0, R1, 1, 0      # R5 = dirección
    store R3, R5, 0, 0          # mem[R5] = valor
    ret

# ------------------------------------------------------------
# MAT_FILL — Rellena toda la matriz con un valor fijo
# Entrada : R0 = base, R1 = valor
# Salida  : ninguna
# Clobbers: R4, R5, R6
# ------------------------------------------------------------
MAT_FILL:
    load  R4, R0, 0, 0          # R4 = filas
    load  R5, R0, 0, 1          # R5 = cols
    mul   R4, R5                # R4 = filas * cols  (total elementos)
    addi  R0, 2                 # R0 = primer elemento (saltar cabecera)
    mov   R6, R0                # R6 = cursor
_MF_LOOP:
    store R1, R6, 0, 0          # mem[cursor] = valor
    addi  R6, 1
    dec   R4
    jnz   _MF_LOOP
    ret

# ============================================================
# fin de stdlib/vecmat.asm
# ============================================================
