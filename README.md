# 8位Logisim CPU仿真项目

## 项目简介

本项目是一个使用 [Logisim](http://www.cburch.com/logisim/) 设计和仿真的8位CPU。CPU拥有自定义的指令集，并配备了一个使用Python编写的汇编器 (`compiler.py`)，用于将汇编代码转换为CPU可执行的16位机器码。此外，项目还包含一个批处理脚本 (`run_compiler.bat`)，方便在Windows环境下运行汇编器，即使系统未全局配置Python。

仓库主要语言构成：Python (汇编器), Batchfile (启动器), Assembly (示例程序)。

## 特性

*   **8位CPU架构**：包含16个通用的8位寄存器 (R0-R15)。
*   **自定义指令集**：包含6条精心设计的16位定长指令。
*   **Logisim仿真**：CPU核心逻辑和数据通路在Logisim中实现，便于可视化和调试。
*   **Python汇编器**：将特定格式的汇编语言 (`.asm` 文件) 转换为Logisim ROM可以直接加载的十六进制机器码 (`_rom.hex` 文件)。
*   **Windows批处理启动器**：简化汇编器的运行，并能在未配置系统Python环境时自动下载和使用便携版Python。

## CPU架构简述

*   **数据位宽**：8位
*   **寄存器**：
    *   16个通用8位寄存器 (R0 至 R15)。
*   **指令位宽**：16位
*   **内存寻址**：数据内存地址为8位 (0x00 - 0xFF)。
*   **程序计数器 (PC)**：用于指向下一条待执行指令的地址。
*   **指令寄存器 (IR)**：用于存放当前正在执行的指令。

## 指令集 (Instruction Set Architecture - ISA)

CPU支持以下6条16位指令：

| 助记符         | 操作数            | 功能描述                                                                    | 16位二进制格式 (字段名[位宽])        | 主操作码 |
| -------------- | ----------------- | --------------------------------------------------------------------------- | --------------------------------------- | -------- |
| `LDI Rd, imm8`   | Rd, imm8         | `Rd ← imm8` (将8位立即数 `imm8` 加载到目标寄存器 `Rd`)                               | `Op[3:0] Rd[3:0] imm8[7:0]`             | `0000`   |
| `ADD Rd, Rs1, Rs2` | Rd, Rs1, Rs2    | `Rd ← Rs1 + Rs2` (寄存器 `Rs1` 和 `Rs2` 的内容相加，结果存入 `Rd`)                      | `Op[3:0] Rd[3:0] Rs1[3:0] Rs2[3:0]`    | `0001`   |
| `SUB Rd, Rs1, Rs2` | Rd, Rs1, Rs2    | `Rd ← Rs1 - Rs2` (寄存器 `Rs1` 的内容减去 `Rs2` 的内容，结果存入 `Rd`)                   | `Op[3:0] Rd[3:0] Rs1[3:0] Rs2[3:0]`    | `0010`   |
| `LOAD Rd, [A]`   | Rd, A            | `Rd ← MEM[A]` (将数据存储器中地址 `A` (8位) 的内容加载到寄存器 `Rd`)                  | `Op[3:0] Rd[3:0] A[7:0]`                | `0011`   |
| `STORE Rs, [A]`  | Rs, A            | `MEM[A] ← Rs` (将寄存器 `Rs` 的内容存储到数据存储器中地址 `A` (8位))                  | `Op[3:0] Rs[3:0] A[7:0]`                | `0100`   |
| `JRZ Rd, offset` | Rd, offset       | `IF Rd == 0 THEN PC ← PC + sign_extend(offset)` (若寄存器`Rd`为0, 则相对跳转。`offset`为8位有符号字偏移量，相对于PC+1) | `Op[3:0] Rd[3:0] offset[7:0]`           | `0101`   |

**字段说明:**
*   `Op[3:0]`: 4位操作码。
*   `Rd[3:0]`: 4位目标寄存器地址。
*   `Rs1[3:0]`: 4位第一个源寄存器地址。
*   `Rs2[3:0]`: 4位第二个源寄存器地址。
*   `imm8[7:0]`: 8位立即数。
*   `A[7:0]`: 8位内存地址。
*   `offset[7:0]`: 8位有符号偏移量 (用于JRZ指令，补码表示)。

## 文件结构 (主要文件)

*   `RISC.circ` : Logisim CPU设计文件。
*   `compiler.py`: Python汇编器脚本。
*   `run_compiler.bat`: Windows环境下运行汇编器的批处理脚本。
*   `*.asm`: 汇编语言源文件示例。
*   `*_rom.hex`: 由汇编器生成的、可加载到Logisim ROM的机器码文件。

## 汇编器 (`compiler.py`)

该Python脚本用于将为本CPU编写的汇编语言程序 (`.asm` 文件) 转换为16位的十六进制机器码 (`.hex` 文件)，格式符合Logisim ROM加载要求。

**使用方法：**

1.  确保您的计算机上安装了Python (建议版本3.6+)。
2.  将您的汇编代码保存为 `.asm` 文件，并与 `compiler.py` 放置在同一目录下。
3.  打开终端或命令提示符，导航到该目录。
4.  运行汇编器：
    ```bash
    python compiler.py
    ```
5.  脚本会自动查找当前目录下的所有 `.asm` 文件，并为每个文件生成一个对应的 `[文件名]_rom.hex` 文件。

**汇编语法要点：**
*   注释以分号 `;` 开始。
*   寄存器表示为 `R0` 到 `R15`。
*   立即数和地址可以是十进制 (如 `10`) 或十六进制 (如 `0x0A`)。
*   `LOAD` 和 `STORE` 指令的内存地址需用方括号括起来，如 `[0x10]`。
*   `JRZ` 指令的偏移量可以是正数 (如 `+2`) 或负数 (如 `-1`)。

## Windows批处理启动器 (`run_compiler.bat`)

此脚本为Windows用户提供了一个便捷的方式来运行汇编器，特别是当系统未正确配置Python环境变量或未安装Python时。

**使用方法：**

1.  将 `run_compiler.bat` 和 `compiler.py` 以及您的 `.asm` 文件放在同一目录下。
2.  双击运行 `run_compiler.bat`。
3.  脚本会自动检测Python环境。如果未检测到，它会尝试下载并使用便携版Python来执行 `compiler.py`。
4.  编译结果与直接运行 `compiler.py` 相同。

## Logisim仿真

1.  **打开CPU设计**: 使用Logisim打开项目中的 `.circ` 文件 ( `RISC.circ`)。
2.  **准备机器码**: 使用上述汇编器将您的 `.asm` 程序编译成 `_rom.hex` 文件。
3.  **加载到ROM**:
    *   在Logisim电路中找到程序存储器 (ROM) 元件。
    *   右键点击ROM元件。
    *   选择 "Load Image..."。
    *   浏览并选择您生成的 `_rom.hex` 文件。
4.  **运行仿真**:
    *   复位CPU (通常通过一个特定的输入引脚或Logisim的仿真控制)。
    *   通过Logisim的仿真菜单 (Simulate -> Ticks Enabled, หรือ Simulate -> Tick Frequency) 或快捷键 (Ctrl+K) 来驱动时钟信号，观察CPU的运行状态、寄存器内容和内存变化。

## 如何开始 / 使用步骤

1.  **克隆/下载仓库**：获取本项目所有文件。
2.  **编写汇编程序**：在您选择的文本编辑器中创建一个新的 `.asm` 文件，按照上述指令集编写您的程序。
3.  **汇编程序**：
    *   **选项A (推荐)**: 将 `.asm` 文件与 `compiler.py` 和 (可选的) `run_compiler.bat` 放在同一目录。
        *   Windows用户可以直接双击 `run_compiler.bat`。
        *   其他用户或希望直接使用Python的用户，在终端中运行 `python compiler.py`。
    *   **选项B**: 如果您已将 `compiler.py` 编译为 `.exe`，则将 `.exe` 文件与 `.asm` 文件放在同一目录，然后运行该 `.exe` 文件。
4.  **查看输出**：汇编器会在同目录下生成一个 `[您的程序名]_rom.hex` 文件。
5.  **加载并仿真**：按照 "Logisim仿真" 部分的说明，在Logisim中加载并运行您的程序。

## 示例程序

仓库中可能包含一些 `.asm` 示例程序，您可以参考它们来学习如何为该CPU编写代码，并测试汇编器和CPU的功能。

## 作者

*   [雪豹](https://github.com/2827700630)

---