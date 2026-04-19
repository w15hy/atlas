# Fibonacci(n) — resultado en r5, entrada r0
mov  r0, 7
mov  r1, 0          # F(0)
mov  r2, 1          # F(1)
mov  r4, 0          # constante 0 para cmp
cmp  r0, r4         # n == 0 ?
jz   END

LOOP:   
mov  r3, r2         # temp = F(i+1)
add  r2, r1         # r2 = r2 + r1  →  F(i+2)
mov  r1, r3         # r1 = viejo r2
dec  r0
cmp  r0, r4         # n == 0 ?
jnz  LOOP

END:    
mov  r5, r1
halt