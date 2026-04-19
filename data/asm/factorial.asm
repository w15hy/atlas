# Factorial de n
# Entrada : r0 = n  (ej: 5)
# Resultado: r5
# Registros : r0 = contador, r5 = acumulador

mov  r0, 5          # n = 5  → calcula 5!
mov  r5, 1          # acumulador = 1
mov  r2, 1
LOOP:   
cmp  r0, r2          # compara contador con 1
jz   END            # si r0 == 1  →  terminamos (r5 ya tiene el resultado)
mul  r5, r0     # r5 = r5 * r0
dec  r0             # r0--
jmp  LOOP
END:    
halt
