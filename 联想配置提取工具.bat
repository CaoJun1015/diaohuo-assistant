@echo off
chcp 65001 >nul
title 联想电脑配置提取工具

echo ================================================================
echo.
echo               联想电脑配置提取工具
echo.
echo ================================================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python环境
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 获取当前目录
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: 检查extract_lenovo_config.py是否存在
if not exist "%SCRIPT_DIR%\extract_lenovo_config.py" (
    echo [错误] 未找到 extract_lenovo_config.py 文件
    echo 请确保此脚本与 extract_lenovo_config.py 在同一目录下
    pause
    exit /b 1
)

echo [信息] 准备开始提取...
echo.

:: 使用PowerShell打开文件选择对话框
echo 请在弹出的窗口中选择要处理的Word文档...
powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; $file = New-Object System.Windows.Forms.OpenFileDialog; $file.Filter = 'Word文档 (*.docx)|*.docx|所有文件 (*.*)|*.*'; $file.Title = '选择Word文档'; $file.ShowDialog() | Out-Null; $file.FileName" > temp_input.txt

set /p INPUT_FILE=<temp_input.txt
del temp_input.txt >nul 2>&1

if "%INPUT_FILE%"=="" (
    echo [取消] 未选择文件，程序退出
    pause
    exit /b 0
)

echo [选择] 输入文件: %INPUT_FILE%
echo.

:: 生成默认输出文件名
for %%i in ("%INPUT_FILE%") do set "FILENAME=%%~ni"
set "OUTPUT_FILE=%SCRIPT_DIR%\%FILENAME%_联想配置.docx"

:: 询问是否使用默认输出路径
echo [询问] 输出文件将保存为:
echo        %OUTPUT_FILE%
echo.
set /p CONFIRM="是否使用此路径? (Y/N): "
if /i "%CONFIRM%"=="Y" (
    set "OUTPUT_FILE=%SCRIPT_DIR%\%FILENAME%_联想配置.docx"
) else (
    echo 请在弹出的窗口中选择输出位置...
    powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; $file = New-Object System.Windows.Forms.SaveFileDialog; $file.Filter = 'Word文档 (*.docx)|*.docx'; $file.Title = '选择保存位置'; $file.FileName = '%FILENAME%_联想配置.docx'; $file.ShowDialog() | Out-Null; $file.FileName" > temp_output.txt
    set /p OUTPUT_FILE=<temp_output.txt
    del temp_output.txt >nul 2>&1
    
    if "%OUTPUT_FILE%"=="" (
        echo [取消] 未选择保存位置，程序退出
        pause
        exit /b 0
    )
)

echo.
echo ================================================================
echo.
echo               开始提取联想电脑配置...
echo.
echo ================================================================
echo.

:: 执行Python脚本
cd /d "%SCRIPT_DIR%"
python extract_lenovo_config.py "%INPUT_FILE%" "%OUTPUT_FILE%"

if errorlevel 1 (
    echo.
    echo ================================================================
    echo [错误] 提取失败，请检查输入文件格式
    echo ================================================================
    pause
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

:: 询问是否打开输出文件
set /p OPEN="是否打开生成的文档? (Y/N): "
if /i "%OPEN%"=="Y" (
    start "" "%OUTPUT_FILE%"
)

:: 询问是否打开输出目录
set /p EXPLORE="是否打开文件所在目录? (Y/N): "
if /i "%EXPLORE%"=="Y" (
    explorer /select,"%OUTPUT_FILE%"
)

pause
