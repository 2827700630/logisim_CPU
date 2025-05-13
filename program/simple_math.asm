; simple_math.asm
; 演示基本的算术运算

LDI R1, 0x10    ; R1 = 16
LDI R2, 0x05    ; R2 = 5
LDI R3, 0x02    ; R3 = 2

ADD R4, R1, R2  ; R4 = R1 + R2 (16 + 5 = 21 = 0x15)
SUB R5, R4, R3  ; R5 = R4 - R3 (21 - 2 = 19 = 0x13)

STORE R4, [0x20]; Mem[0x20] = R4 (0x15)
STORE R5, [0x21]; Mem[0x21] = R5 (0x13)

; 结束程序
LDI R0, 0
JRZ R0, -1      ; 无限循环
