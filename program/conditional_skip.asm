; conditional_skip.asm
; 演示 JRZ 条件跳转

LDI R1, 0x01    ; R1 = 1 (非零)
LDI R2, 0x00    ; R2 = 0 (零)
LDI R10, 0xFF   ; R10 = 0xFF (初始值)
LDI R11, 0xFF   ; R11 = 0xFF (初始值)

; 测试 R1 (非零)
; JRZ R1, +2  ; 如果 R1 == 0, 则跳转2条指令 (跳过 LDI R10, 0x11)
; 由于 R1 非零, 下一条指令会执行
JRZ R1, +2      ; PC = PC+1+2. 当前指令地址假设为X, PC+1为X+1, 跳转目标为X+1+2=X+3
LDI R10, 0x11   ; 此指令应被执行, R10 = 0x11
LDI R12, 0xCC   ; 此指令是JRZ R1的跳转目标之后的指令，也会被执行

; 测试 R2 (零)
; JRZ R2, +2  ; 如果 R2 == 0, 则跳转2条指令 (跳过 LDI R11, 0x22)
; 由于 R2 为零, 下一条指令会被跳过
JRZ R2, +2      ; PC = PC+1+2.
LDI R11, 0x22   ; 此指令应被跳过, R11 保持 0xFF
LDI R13, 0xDD   ; 此指令是JRZ R2的跳转目标之后的指令，会被执行

; 结束程序
LDI R0, 0
JRZ R0, -1      ; 无限循环
