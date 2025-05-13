; loop_counter.asm
; 演示使用 JRZ 和 SUB 实现循环计数

LDI R1, 5       ; R1 作为计数器, 初始化为 5
LDI R2, 1       ; R2 存储常量 1, 用于 R1--
LDI R3, 0       ; R3 用于累加 (可选, 演示循环体内的操作)
LDI R4, 10      ; R4 存储常量 10, 用于累加

; LOOP_START:
ADD R3, R3, R4  ; 循环体操作: R3 = R3 + 10
SUB R1, R1, R2  ; 计数器 R1 减 1
JRZ R1, +2      ; 如果 R1 == 0, 则跳转2条指令 (跳出循环到 END_LOOP)
LDI R0, 0       ; 用于无条件跳转
JRZ R0, -4      ; 无条件跳转回 LOOP_START (向前4条指令: LDI R0, JRZ R0, ADD R3, SUB R1)

; END_LOOP:
STORE R3, [0x40]; 将 R3 的最终结果 (5 * 10 = 50 = 0x32) 存储到内存 0x40

; 结束程序
LDI R0, 0
JRZ R0, -1      ; 无限循环
