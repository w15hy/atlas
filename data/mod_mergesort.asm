# =============================================================================
# mod_mergesort.asm — Módulo: MergeSort bottom-up como función
# =============================================================================
# Exporta MERGESORT(R0=ARR_BASE, R1=N, R2=TMP_BASE)
# Necesita la stdlib vecmat para LEA/LOAD/STORE con arreglos
# =============================================================================

.global MERGESORT

# ============================================================
# MERGE — combina arr[lo..mid-1] y arr[mid..hi-1]
# Pre: R0=ARR_BASE, R2=TMP_BASE, R4=lo, R5=mid, R6=hi
# ============================================================
MERGE:
    # left_len = mid - lo
    mov   R10, R5
    sub   R10, R4           # R10 = mid - lo

    # Paso 1: copiar arr[lo..mid-1] a tmp[0..left_len-1]
    mov   R7, 0             # i = 0
    mov   R9, R4            # k = lo (cursor sobre arr)

COPY_LEFT:
    lea   R11, R0, R9, 1, 0
    load  R12, R11, 0, 0
    lea   R11, R2, R7, 1, 0
    store R12, R11, 0, 0
    inc   R7
    inc   R9
    cmp   R7, R10
    jc    COPY_LEFT

    # Paso 2: mezcla
    mov   R7, 0             # i = 0
    mov   R8, R5            # j = mid
    mov   R9, R4            # k = lo

MLOOP:
    cmp   R7, R10
    jc    MLOOP_CHK_J
    jmp   ML_DONE

MLOOP_CHK_J:
    cmp   R8, R6
    jc    MLOOP_CMP
    jmp   COPY_REST_L

MLOOP_CMP:
    lea   R11, R2, R7, 1, 0
    load  R11, R11, 0, 0
    lea   R12, R0, R8, 1, 0
    load  R12, R12, 0, 0
    cmp   R11, R12
    jc    TAKE_L
    jz    TAKE_L

TAKE_R:
    lea   R12, R0, R8, 1, 0
    load  R13, R12, 0, 0
    lea   R12, R0, R9, 1, 0
    store R13, R12, 0, 0
    inc   R8
    inc   R9
    jmp   MLOOP

TAKE_L:
    lea   R11, R2, R7, 1, 0
    load  R13, R11, 0, 0
    lea   R11, R0, R9, 1, 0
    store R13, R11, 0, 0
    inc   R7
    inc   R9
    jmp   MLOOP

COPY_REST_L:
    lea   R11, R2, R7, 1, 0
    load  R13, R11, 0, 0
    lea   R11, R0, R9, 1, 0
    store R13, R11, 0, 0
    inc   R7
    inc   R9
    cmp   R7, R10
    jc    COPY_REST_L

ML_DONE:
    ret

# ============================================================
# MERGESORT — ordena arr[R0..R0+R1-1] (bottom-up)
# Pre: R0=ARR_BASE, R1=N, R2=TMP_BASE
# ============================================================
MERGESORT:
    mov   R3, 1             # width = 1

MS_OUTER:
    mov   R4, 0             # lo = 0

MS_INNER:
    cmp   R4, R1
    jc    MS_BLOCK
    jmp   MS_NEXT_W

MS_BLOCK:
    mov   R5, R4
    add   R5, R3
    cmp   R5, R1
    jc    MS_MID_OK
    mov   R5, R1
MS_MID_OK:

    mov   R6, R4
    add   R6, R3
    add   R6, R3
    cmp   R6, R1
    jc    MS_HI_OK
    mov   R6, R1
MS_HI_OK:

    cmp   R5, R6
    jz    MS_SKIP

    push  R1
    push  R3
    push  R4
    call  MERGE
    pop   R4
    pop   R3
    pop   R1

MS_SKIP:
    add   R4, R3
    add   R4, R3
    jmp   MS_INNER

MS_NEXT_W:
    add   R3, R3
    cmp   R3, R1
    jc    MS_OUTER

MS_DONE:
    ret
