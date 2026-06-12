@echo off
chcp 65001 >nul
title 联想电脑配置提取 - 拖拽版

:: 获取拖拽的文件
set "INPUT_FILE=%~1"

if "%INPUT_FILE%"=="" (
    echo ================================================================
    echo.
    echo               联想电脑配置提取工具
    echo.
    echo ================================================================
    echo.
    echo 使用方法:
    echo   方法1: 直接将Word文档拖拽到此文件上
    echo   方法2: 双击运行，然后选择文件
    echo.
    echo 支持格式: .docx (WPS和微软Office)
    echo.
    echo ================================================================
    echo.
    
    :: 打开文件选择对话框
    powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; $file = New-Object System.Windows.Forms.OpenFileDialog; $file.Filter = 'Word文档 (*.docx)|*.docx'; $file.Title = '选择Word文档'; $file.ShowDialog() | Out-Null; $file.FileName" > temp_input.txt
    set /p INPUT_FILE=<temp_input.txt
    del temp_input.txt >nul 2>&1
    
    if "%INPUT_FILE%"=="" (
        echo [取消] 未选择文件，程序退出
        pause
        exit /b 0
    )
)

:: 检查文件是否存在
if not exist "%INPUT_FILE%" (
    echo [错误] 文件不存在: %INPUT_FILE%
    pause
    exit /b 1
)

:: 获取文件扩展名
for %%i in ("%INPUT_FILE%") do set "EXT=%%~xi"
if /i "%EXT%" neq ".docx" (
    echo [警告] 文件格式不是.docx，可能是: %EXT%
    echo 继续处理...
)

:: 获取文件名和路径
for %%i in ("%INPUT_FILE%") do (
    set "FILENAME=%%~ni"
    set "FILEPATH=%%~dpi"
)

set "OUTPUT_FILE=%FILEPATH%%FILENAME%_联想配置.docx"

echo ================================================================
echo.
echo               联想电脑配置提取工具
echo.
echo ================================================================
echo.
echo [输入] %INPUT_FILE%
echo [输出] %OUTPUT_FILE%
echo.
echo ================================================================
echo.

:: 获取当前目录
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: 执行Python脚本
cd /d "%SCRIPT_DIR%"
python extract_lenovo_config.py "%INPUT_FILE%" "%OUTPUT_FILE%"

if errorlevel 1 (
    echo.
    echo ================================================================
    echo [错误] 提取失败
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

:: 打开输出文件
if exist "%OUTPUT_FILE%" (
    start "" "%OUTPUT_FILE%"
)

pause
