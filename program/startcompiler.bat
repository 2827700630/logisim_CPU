@echo off
chcp 65001 > nul
title Python 汇编器启动器
color 0B

echo [信息] 正在准备Python汇编器...

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo 检测到已安装的Python环境，开始执行汇编器脚本...
    python compiler.py
) else (
    :: 如果没有安装Python,使用内置的便携版Python
    echo 未检测到系统Python环境，开始准备便携版Python...
    if not exist "python_portable" (
        echo 第一次运行或便携版Python不存在，将下载并解压，请稍候...
        powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.9.7/python-3.9.7-embed-amd64.zip' -OutFile 'python.zip'}"
        md python_portable
        powershell -Command "& {Expand-Archive -Path 'python.zip' -DestinationPath 'python_portable' -Force}"
        del python.zip
    )
    echo 便携版Python环境准备完毕!
    echo 正在执行汇编器脚本...
    .\python_portable\python.exe compiler.py
)

:: 如果发生错误则暂停
if errorlevel 1 (
    echo 汇编过程失败!
    echo 请检查脚本输出或联系技术支持。
    pause
    exit /b 1)

:: 正常退出
echo 汇编过程完毕，按任意键退出...
pause
exit /b 0