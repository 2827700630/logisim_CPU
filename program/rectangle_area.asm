; rectangle_area.asm
; 计算矩形面积: area = width * height
;
; 输入假定:
;   Mem[0x00]: 存储矩形的长 (width)
;   Mem[0x01]: 存储矩形的高 (height)
; 输出:
;   Mem[0x02]: 存储计算得到的面积 (area)
;
; 注意: 结果溢出未处理。长、高、面积均为8位无符号数。
;
; 寄存器使用:
;   R0: 用于JRZ无条件跳转的零值，以及程序结束时的无限循环
;   R1: 存储 width (长)
;   R2: 存储 height (高), 作为乘法循环的计数器
;   R3: 存储 area (面积的累加结果)
;   R4: 存储立即数 1, 用于 R2-- (高减1操作)

LDI R3, 0       ; R3 (area) = 0. 初始化面积为0
LDI R4, 1       ; R4 = 1. 常量1, 用于将高R2减1

LOAD R1, [0x00] ; R1 = Mem[0x00]. 加载长到R1
LOAD R2, [0x01] ; R2 = Mem[0x01]. 加载高到R2

; 检查长(R1)是否为0. 如果是, 面积为0, 直接跳转到存储结果步骤.
; 跳转目标是 STORE R3, [0x02] 指令 (地址为 0B, 从0开始计数的话).
; 当前指令在地址 04. PC将是04+1=05. 跳转偏移量 = 0B - 05 = +6.
JRZ R1, +6      ; 如果 R1 == 0, 跳转6条指令到 STORE_RESULT

; 检查高(R2)是否为0. 如果是, 面积为0, 直接跳转到存储结果步骤.
; 跳转目标是 STORE R3, [0x02] 指令 (地址为 0B).
; 当前指令在地址 05. PC将是05+1=06. 跳转偏移量 = 0B - 06 = +5.
JRZ R2, +5      ; 如果 R2 == 0, 跳转5条指令到 STORE_RESULT

; LOOP_START: (实际指令地址 06)
; 乘法循环: area = area + width; height = height - 1
ADD R3, R3, R1  ; R3 (area) = R3 + R1 (width). 累加长到面积
SUB R2, R2, R4  ; R2 (height) = R2 - R4 (1). 高减1
; 如果高(R2)为0, 乘法完成, 跳转到存储结果步骤 (地址 0B).
; 当前指令在地址 08. PC将是08+1=09. 跳转偏移量 = 0B - 09 = +2.
JRZ R2, +2      ; 如果 R2 == 0, 跳转2条指令到 STORE_RESULT

; 如果高(R2)不为0, 继续循环 (无条件跳转回 LOOP_START)
LDI R0, 0       ; R0 = 0. 用于 JRZ R0, offset 实现无条件跳转
; 无条件跳转回 LOOP_START (地址 06).
; 当前指令在地址 0A. PC将是0A+1=0B. 跳转偏移量 = 06 - 0B = -5.
JRZ R0, -5      ; 跳转到 LOOP_START (向前5条指令)

; STORE_RESULT: (实际指令地址 0B)
STORE R3, [0x02]; Mem[0x02] = R3 (area). 存储计算结果

; END_PROGRAM: (实际指令地址 0C)
; 程序结束 (通过无限循环暂停CPU)
LDI R0, 0       ; R0 = 0
; 无限循环. PC = (当前PC+1) + offset = (0D+1) - 1 = 0D.
JRZ R0, -1      ; 跳转到自身指令，实现无限循环
