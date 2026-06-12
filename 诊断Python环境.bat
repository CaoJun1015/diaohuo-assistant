@echo off
chcp 65001 >nul 2>&1
title Python环境诊断工具

echo ================================================================
echo.
echo            Python环境诊断工具
echo.
echo ================================================================
echo.

echo [检查1] Python是否安装...
python --version >nul 2>&1
if errorlevel 1 (
    echo [失败] Python未安装或未添加到PATH
    echo.
    echo 解决方案：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载Python 3.8或更高版本
    echo 3. 运行安装程序
    echo 4. 重要：勾选 "Add Python to PATH"
    echo.
) else (
    for /f "delims=" %%v in ('python --version 2^>^&1') do echo [成功] Python版本: %%v
)

echo.
echo [检查2] pip是否可用...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [失败] pip未安装或未添加到PATH
) else (
    for /f "delims=" %%v in ('pip --version 2^>^&1') do echo [成功] pip版本: %%v
)

echo.
echo [检查3] python-docx模块是否安装...
python -c "import docx; print('[成功] python-docx已安装')" 2>nul
if errorlevel 1 (
    echo [失败] python-docx未安装
    echo.
    echo 正在安装...
    pip install python-docx
    if errorlevel 1 (
        echo [失败] 安装失败！
        echo.
        echo 请手动运行以下命令：
        echo pip install python-docx
    ) else (
        echo [成功] python-docx安装完成
    )
)

echo.
echo [检查4] 当前工作目录...
cd
echo.

echo [检查5] extract_lenovo_config.py是否存在...
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"
echo 当前目录: %CURRENT_DIR%
echo.
if exist "%CURRENT_DIR%\extract_lenovo_config.py" (
    echo [成功] extract_lenovo_config.py存在
) else (
    echo [失败] extract_lenovo_config.py不存在
    echo.
    echo 请将以下文件放在同一目录：
    echo 1. 联想配置提取工具.bat
    echo 2. extract_lenovo_config.py
)

echo.
echo ================================================================
echo.
echo            诊断完成
echo.
echo ================================================================
echo.
echo 如果有问题，请将上面的输出截图发给我
echo.

pause
