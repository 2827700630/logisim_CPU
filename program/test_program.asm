
; 测试程序 - 8位CPU
; 雪豹

LDI R1, 0x05    ; R1 <- 0x05 (将立即数5加载到寄存器R1)
LDI R2, 0x0A    ; R2 <- 0x0A (将立即数10加载到寄存器R2)
ADD R3, R1, R2  ; R3 <- R1 + R2 (0x0F)
STORE R3, [0x10]; Mem[0x10] <- R3 (0x0F) (将R3的内容存储到内存地址0x10)

LDI R4, 0       ; R4 <- 0x00 (清零R4)
LOAD R4, [0x10] ; R4 <- Mem[0x10] (R4应为0x0F) (从内存地址0x10加载到R4)
SUB R5, R4, R1  ; R5 <- R4 - R1 (0x0F - 0x05 = 0x0A)

LDI R6, 0       ; R6 <- 0x00 (用于JRZ测试)
JRZ R6, +2      ; 如果R6为0则跳转 (PC+1+2) (偏移量为+2)
LDI R7, 0x7F    ; 此指令应被跳过
LDI R8, 0x55    ; 此指令应被跳过
LDI R9, 0x3C    ; 跳转目标, R9 <- 0x3C

LDI R0, 0       ; R0 <- 0 (用于无限循环)
JRZ R0, -1      ; 无限循环 (PC+1-1) (偏移量-1, 8位补码为0xFF)
    