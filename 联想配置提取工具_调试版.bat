@echo off
chcp 65001 >nul 2>&1
title 联想电脑配置提取工具 - 调试模式

echo ================================================================
echo.
echo               联想电脑配置提取工具
echo               (调试模式)
echo.
echo ================================================================
echo.

:: 等待按键，防止一闪而过
echo 按任意键开始...
pause >nul

:: 检查Python是否安装
echo [步骤1] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python！
    echo.
    echo 请先安装Python环境：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载并安装Python 3.x
    echo 3. 安装时勾选"Add Python to PATH"
    echo.
    echo 按任意键退出...
    pause >nul
    exit /b 1
)

for /f "delims=" %%v in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%v"
echo [成功] %PYTHON_VERSION%
echo.

:: 检查必要的文件
echo [步骤2] 检查必要文件...
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

echo [信息] 脚本目录: %SCRIPT_DIR%
echo.

if not exist "%SCRIPT_DIR%\extract_lenovo_config.py" (
    echo [错误] 未找到 extract_lenovo_config.py 文件！
    echo.
    echo 请确保以下文件在同一目录下：
    echo 1. 联想配置提取工具.bat
    echo 2. extract_lenovo_config.py
    echo.
    echo 按任意键退出...
    pause >nul
    exit /b 1
)

echo [成功] extract_lenovo_config.py 存在
echo.

:: 检查Python模块
echo [步骤3] 检查Python模块...
python -c "import docx" 2>nul
if errorlevel 1 (
    echo [警告] python-docx 模块未安装，正在安装...
    pip install python-docx
    if errorlevel 1 (
        echo [错误] 安装 python-docx 失败！
        echo.
        echo 请手动运行以下命令安装：
        echo pip install python-docx
        echo.
        echo 按任意键退出...
        pause >nul
        exit /b 1
    )
    echo [成功] python-docx 安装完成
)

echo [成功] Python模块检查通过
echo.

:: 获取输入文件
echo [步骤4] 选择输入文件...
echo.

if not "%~1"=="" (
    set "INPUT_FILE=%~1"
    echo [拖拽] 使用拖拽的文件: %INPUT_FILE%
) else (
    echo 请在弹出的窗口中选择Word文档...
    echo 如果没有弹出窗口，请检查杀毒软件设置...
    echo.
    
    :: 使用PowerShell打开文件对话框
    powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; $file = New-Object System.Windows.Forms.OpenFileDialog; $file.Filter = 'Word文档 (*.docx)|*.docx'; $file.Title = '选择Word文档'; $result = $file.ShowDialog(); if ($result -eq 'OK') { Write-Host $file.FileName } else { exit }" > temp_input.txt
    
    set /p INPUT_FILE=<temp_input.txt
    del temp_input.txt >nul 2>&1
    
    if "%INPUT_FILE%"=="" (
        echo [取消] 未选择文件
        echo.
        echo 按任意键退出...
        pause >nul
        exit /b 0
    )
)

echo [选择] 输入文件: %INPUT_FILE%
echo.

:: 检查文件是否存在
if not exist "%INPUT_FILE%" (
    echo [错误] 文件不存在: %INPUT_FILE%
    echo.
    echo 按任意键退出...
    pause >nul
    exit /b 1
)

:: 生成输出文件名
for %%i in ("%INPUT_FILE%") do (
    set "FILENAME=%%~ni"
    set "FILEPATH=%%~dpi"
)

set "OUTPUT_FILE=%FILEPATH%%FILENAME%_联想配置.docx"

echo [步骤5] 准备输出文件...
echo [输出] %OUTPUT_FILE%
echo.

:: 检查输出文件是否已存在
if exist "%OUTPUT_FILE%" (
    echo [警告] 输出文件已存在，将被覆盖
)

echo.
echo ================================================================
echo.
echo               开始提取联想电脑配置
echo.
echo ================================================================
echo.

:: 执行Python脚本
cd /d "%SCRIPT_DIR%"
echo [执行] 运行提取脚本...
echo.

python extract_lenovo_config.py "%INPUT_FILE%" "%OUTPUT_FILE%" 2>&1

if errorlevel 1 (
    echo.
    echo ================================================================
    echo [错误] 提取失败！
    echo.
    echo 常见问题：
    echo 1. Word文档格式不正确（非.docx）
    echo 2. Word文档为空或损坏
    echo 3. 文档中没有联想电脑信息
    echo.
    echo 解决方案：
    echo 1. 确认文件是.docx格式
    echo 2. 用Word或WPS打开检查内容
    echo 3. 确保文档包含联想电脑配置信息
    echo ================================================================
    echo.
    echo 按任意键退出...
    pause >nul
    exit /b 1
)

echo.
echo ================================================================
echo.
echo [成功] 配置提取完成！
echo.
echo [输出] %OUTPUT_FILE%
echo.
echo ================================================================
echo.

:: 检查输出文件是否生成
if exist "%OUTPUT_FILE%" (
    echo [检查] 输出文件已生成
    
    :: 打开输出文件
    echo [操作] 正在打开生成的文档...
    start "" "%OUTPUT_FILE%"
    
    echo.
    echo [完成] 处理完毕！
) else (
    echo [错误] 输出文件未生成
)

echo.
echo 按任意键退出...
pause >nul
