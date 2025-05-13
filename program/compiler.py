import re
import os # 导入os模块用于文件系统操作

# --- 配置 (Configuration) ---
# 定义指令助记符到其4位二进制操作码的映射
OPCODES = {
    "LDI":   "0000",  # LDI Rd, imm8  (将8位立即数加载到目标寄存器Rd)
    "ADD":   "0001",  # ADD Rd, Rs1, Rs2 (寄存器Rs1和Rs2相加，结果存入Rd)
    "SUB":   "0010",  # SUB Rd, Rs1, Rs2 (寄存器Rs1减去Rs2，结果存入Rd)
    "LOAD":  "0011",  # LOAD Rd, [A] (将数据存储器地址A的内容加载到Rd)
    "STORE": "0100",  # STORE Rs, [A] (将寄存器Rs的内容存储到数据存储器地址A)
    "JRZ":   "0101"   # JRZ Rd, offset (若寄存器Rd为0, 则相对跳转)
}

# --- 辅助函数 (Helper Functions) ---

def parse_register(reg_str):
    """
    将寄存器字符串（如 "R5"）转换为4位二进制字符串（如 "0101"）。
    Converts register string like "R5" to 4-bit binary "0101".
    """
    # 使用正则表达式验证寄存器格式是否为 R0-R15
    if not re.match(r"^[Rr]([0-9]|1[0-5])$", reg_str):
        raise ValueError(f"无效的寄存器格式: {reg_str}。应为 R0-R15。")
    reg_num = int(reg_str[1:]) # 提取寄存器编号
    if not (0 <= reg_num <= 15): # 检查编号是否在0-15范围内
        raise ValueError(f"寄存器编号超出范围: {reg_num}。应为 0-15。")
    return format(reg_num, '04b') # 将编号格式化为4位二进制字符串

def parse_value(val_str, bits, is_signed=False):
    """
    将数值字符串（十进制或十六进制）转换为指定位数的二进制字符串。
    对于8位偏移量，会处理有符号转换。
    Converts a numeric string (decimal or hex) to a n-bit binary string.
    Handles signed conversion for 8-bit offsets.
    """
    val_str = val_str.strip() # 去除首尾空格
    value = 0
    # 判断是十六进制还是十进制
    if val_str.startswith('0x') or val_str.startswith('0X'):
        value = int(val_str, 16)
    elif val_str.startswith('+'): # 处理像 JRZ R0, +2 这样的正号有符号偏移量
        value = int(val_str[1:])
    else:
        try:
            value = int(val_str) # 默认为十进制
        except ValueError:
            raise ValueError(f"无效的数值: {val_str}")

    if is_signed: # 如果是需要处理的有符号数
        # 检查有符号数是否在指定位数可表示的范围内
        if not (-(2**(bits-1)) <= value < (2**(bits-1))):
            raise ValueError(f"{bits}位有符号数 {value} 超出范围。")
        # 如果是负数，转换为补码表示
        if value < 0:
            value = (1 << bits) + value # (2**bits) + negative_value
        return format(value, f'0{bits}b') # 格式化为指定位数的二进制 (包含符号位)
    else: # 如果是无符号数
        # 检查无符号数是否在指定位数可表示的范围内
        if not (0 <= value < (2**bits)):
            raise ValueError(f"{bits}位无符号数 {value} 超出范围。")
        return format(value, f'0{bits}b') # 格式化为指定位数的二进制

def assemble_instruction(line_num, instruction_parts):
    """
    将单条指令的各个部分组装成16位的二进制字符串。
    Assembles a single instruction into a 16-bit binary string.
    """
    mnemonic = instruction_parts[0].upper() # 获取指令助记符并转为大写
    operands = [op.strip() for op in instruction_parts[1:]] # 获取操作数列表

    if mnemonic not in OPCODES: # 检查助记符是否已知
        raise ValueError(f"L{line_num}: 未知指令助记符: {mnemonic}")

    op_bin = OPCODES[mnemonic] # 获取操作码的二进制表示
    # 初始化各字段的二进制字符串
    rd_bin = ""
    rs1_bin = ""
    rs2_bin = ""
    imm8_bin = ""
    addr8_bin = ""
    offset8_bin = ""

    # 根据不同的指令类型处理操作数
    if mnemonic == "LDI": # LDI Rd, imm8
        if len(operands) != 2:
            raise ValueError(f"L{line_num} ({mnemonic}): 需要 2 个操作数 (Rd, imm8)，实际得到 {len(operands)}")
        rd_bin = parse_register(operands[0])    # 解析目标寄存器 Rd
        imm8_bin = parse_value(operands[1], 8) # 解析8位立即数 imm8
        return op_bin + rd_bin + imm8_bin      # 拼接形成16位指令

    elif mnemonic in ["ADD", "SUB"]: # ADD/SUB Rd, Rs1, Rs2
        if len(operands) != 3:
            raise ValueError(f"L{line_num} ({mnemonic}): 需要 3 个操作数 (Rd, Rs1, Rs2)，实际得到 {len(operands)}")
        rd_bin = parse_register(operands[0])    # 解析目标寄存器 Rd
        rs1_bin = parse_register(operands[1])   # 解析源寄存器 Rs1
        rs2_bin = parse_register(operands[2])   # 解析源寄存器 Rs2
        return op_bin + rd_bin + rs1_bin + rs2_bin # 拼接

    elif mnemonic == "LOAD": # LOAD Rd, [A]
        if len(operands) != 2:
            raise ValueError(f"L{line_num} ({mnemonic}): 需要 2 个操作数 (Rd, [A])，实际得到 {len(operands)}")
        rd_bin = parse_register(operands[0])    # 解析目标寄存器 Rd
        addr_op = operands[1]                   # 获取地址操作数，如 "[0x10]"
        # 检查地址是否用方括号括起来
        if not (addr_op.startswith('[') and addr_op.endswith(']')):
            raise ValueError(f"L{line_num} ({mnemonic}): 内存地址必须用方括号括起来, 例如 [0x10]。得到: {addr_op}")
        addr8_bin = parse_value(addr_op[1:-1], 8) # 去除方括号并解析8位地址 A
        return op_bin + rd_bin + addr8_bin        # 拼接

    elif mnemonic == "STORE": # STORE Rs, [A]
        if len(operands) != 2:
            raise ValueError(f"L{line_num} ({mnemonic}): 需要 2 个操作数 (Rs, [A])，实际得到 {len(operands)}")
        # 对于STORE指令, 源寄存器Rs使用指令格式中的Rd字段位
        rs_bin_for_rd_field = parse_register(operands[0]) # 解析源寄存器 Rs
        addr_op = operands[1]
        if not (addr_op.startswith('[') and addr_op.endswith(']')):
            raise ValueError(f"L{line_num} ({mnemonic}): 内存地址必须用方括号括起来, 例如 [0x10]。得到: {addr_op}")
        addr8_bin = parse_value(addr_op[1:-1], 8) # 去除方括号并解析8位地址 A
        return op_bin + rs_bin_for_rd_field + addr8_bin # 拼接

    elif mnemonic == "JRZ": # JRZ Rd, offset
        if len(operands) != 2:
            raise ValueError(f"L{line_num} ({mnemonic}): 需要 2 个操作数 (Rd, offset)，实际得到 {len(operands)}")
        rd_bin = parse_register(operands[0])            # 解析目标寄存器 Rd
        offset8_bin = parse_value(operands[1], 8, is_signed=True) # 解析8位有符号偏移量 offset
        return op_bin + rd_bin + offset8_bin            # 拼接

    else: # 理论上不应执行到这里，因为前面已经检查过mnemonic是否在OPCODES中
        raise ValueError(f"L{line_num}: 指令 {mnemonic} 已识别但未被汇编逻辑处理。")


def main_assembler(input_asm_file_path, output_hex_file_path):
    """
    主汇编函数。读取指定的汇编文件，逐行解析和转换，最后输出到指定的Logisim ROM格式的十六进制文件。
    Main assembler function.
    """
    assembled_instructions_hex = [] # 存储转换后的十六进制指令
    print(f"开始汇编文件: {input_asm_file_path}...")

    try:
        with open(input_asm_file_path, 'r', encoding='utf-8') as f_asm: # 以UTF-8编码读取
            for line_num, line in enumerate(f_asm, 1): # 逐行读取，行号从1开始
                line = line.strip() # 去除行首尾的空白字符

                # 去除注释 (分号 ';' 之后的所有内容)
                comment_start = line.find(';')
                if comment_start != -1:
                    line = line[:comment_start].strip()

                if not line: # 如果是空行，则跳过
                    continue

                # 分割助记符和操作数
                parts = re.split(r'[,\s]+', line, maxsplit=1)
                mnemonic_part = parts[0]
                
                if len(parts) > 1 and parts[1]:
                    operands_part_str = parts[1]
                    raw_operands = []
                    current_op = ""
                    in_bracket = False
                    for char in operands_part_str: # 修正: 遍历字符而不是索引
                        if char == '[':
                            in_bracket = True
                        elif char == ']':
                            in_bracket = False
                        
                        if char == ',' and not in_bracket:
                            raw_operands.append(current_op.strip())
                            current_op = ""
                        else:
                            current_op += char
                    raw_operands.append(current_op.strip())
                    instruction_parts = [mnemonic_part] + [op for op in raw_operands if op]
                else:
                    instruction_parts = [mnemonic_part]

                try:
                    binary_instruction = assemble_instruction(line_num, instruction_parts)
                    if len(binary_instruction) != 16:
                        raise ValueError(f"L{line_num}: 汇编后的指令不是16位: {binary_instruction}")
                    
                    hex_instruction = format(int(binary_instruction, 2), '04x')
                    assembled_instructions_hex.append(hex_instruction)
                    # print(f"L{line_num:02d}: {line:<30} -> {binary_instruction} ({hex_instruction})") # 详细输出可以取消注释

                except ValueError as e:
                    print(f"汇编错误，文件 '{input_asm_file_path}' 行 {line_num}: {line}\n  >>> {e}")
                    return False
    except FileNotFoundError:
        print(f"错误: 输入文件 '{input_asm_file_path}' 未找到。")
        return False
    except Exception as e:
        print(f"读取文件 '{input_asm_file_path}' 时发生错误: {e}")
        return False
    
    # 将汇编结果写入Logisim ROM文件
    try:
        with open(output_hex_file_path, 'w') as f_hex:
            f_hex.write("v2.0 raw\n")
            f_hex.write("0000\n") # <--- 新增：在0x00地址固定放入0000
            for hex_instr in assembled_instructions_hex:
                f_hex.write(hex_instr + "\n")
        print(f"汇编成功。输出文件: {output_hex_file_path}")
        # 调整指令计数，因为我们添加了一个额外的0000指令
        print(f"文件 '{input_asm_file_path}' 共汇编用户指令数: {len(assembled_instructions_hex)}")
        print(f"ROM文件总指令数 (包含0x00处的0000): {len(assembled_instructions_hex) + 1}")
        return True
    except IOError as e:
        print(f"写入输出文件 {output_hex_file_path} 失败: {e}")
        return False

# --- 脚本执行入口 (Script Execution) ---
if __name__ == "__main__":
    # 获取脚本文件所在的真实目录
    script_directory = os.path.dirname(os.path.abspath(__file__))
    print(f"编译器脚本所在目录: {script_directory}")
    print(f"将在该目录下查找 .asm 文件并输出 .hex 文件。")
    
    asm_files_found = 0
    for filename in os.listdir(script_directory): # 在脚本目录中查找文件
        if filename.lower().endswith(".asm"): # 检查文件是否以 .asm 结尾 (不区分大小写)
            asm_files_found += 1
            # 构建输入文件的完整路径 (基于脚本目录)
            input_asm_file_path = os.path.join(script_directory, filename)
            
            # 构建输出文件名，例如 "myprogram.asm" -> "myprogram_rom.hex"
            base_name = filename[:-4] # 去掉 ".asm" 后缀
            output_hex_filename = base_name + "_rom.hex"
            # 构建输出文件的完整路径 (基于脚本目录)
            output_hex_file_path = os.path.join(script_directory, output_hex_filename)
            
            print("-" * 40) # 分隔符
            if main_assembler(input_asm_file_path, output_hex_file_path):
                print(f"成功处理文件: {filename}")
            else:
                print(f"处理文件失败: {filename}")
            print("-" * 40) # 分隔符

    if asm_files_found == 0:
        print(f"在目录 '{script_directory}' 中未找到任何 .asm 文件。")
        print("请将您的汇编文件 (.asm) 放置在本脚本所在的目录中，然后重新运行。")
        # 以下是之前用于生成示例文件的代码，您可以取消注释以生成一个测试文件
        # print("\n正在生成一个示例 .asm 文件 'example.asm' 供测试...")
        # example_asm_content = """
        # ; 示例汇编程序
        # LDI R1, 0x0A  ; R1 = 10
        # LDI R2, 0x03  ; R2 = 3
        # ADD R3, R1, R2 ; R3 = R1 + R2 = 13 (0x0D)
        # STORE R3, [0x20] ; 内存地址0x20的值设为R3
        # LDI R0, 0
        # JRZ R0, -1 ; 无限循环
        # """
        # example_input_filename = "example.asm"
        # with open(os.path.join(script_directory, example_input_filename), "w", encoding='utf-8') as f: # 注意这里也用 script_directory
        #     f.write(example_asm_content)
        # print(f"已创建 '{example_input_filename}'。请重新运行脚本来汇编它。")

    print("\n所有操作完成。")