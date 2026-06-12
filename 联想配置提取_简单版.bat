@echo off
chcp 65001 >nul

echo ========================================
echo 联想配置提取工具
echo ========================================
echo.

:: 进入脚本所在目录
cd /d "%~dp0"

:: 检查Python
python --version
if errorlevel 1 (
    echo 错误：未找到Python
    pause
    exit
)

:: 检查脚本
if not exist extract_lenovo_config.py (
    echo 错误：未找到 extract_lenovo_config.py
    pause
    exit
)

:: 检查模块
python -c "import docx" 2>nul
if errorlevel 1 (
    echo 安装python-docx...
    pip install python-docx
)

echo.
echo 请输入要处理的Word文档路径：
echo 例如：D:\文档\价格表.docx
echo.
set /p INPUT="输入路径: "

if "%INPUT%"=="" (
    echo 错误：未输入路径
    pause
    exit
)

:: 生成输出文件名
for %%i in ("%INPUT%") do set "FILENAME=%%~ni"
set "OUTPUT=%~dp0%FILENAME%_联想配置.docx"

echo.
echo 处理中...
echo.

python extract_lenovo_config.py "%INPUT%" "%OUTPUT%"

if errorlevel 1 (
    echo.
    echo 处理失败！
) else (
    echo.
    echo 成功！输出文件：
    echo %OUTPUT%
)

echo.
pause
