@echo off
chcp 65001 >nul
echo ================================================================
echo 测试Python环境
echo ================================================================
echo.

echo 1. 测试Python是否可用...
python -c "print('Python OK')"
if errorlevel 1 (
    echo [失败] Python不可用
    goto :end
)

echo.
echo 2. 测试python-docx模块...
python -c "import docx; print('python-docx OK')"
if errorlevel 1 (
    echo [失败] python-docx未安装
    echo 正在安装...
    pip install python-docx
    if errorlevel 1 (
        echo [失败] 安装失败
        goto :end
    )
    echo [成功] 安装完成
)

echo.
echo 3. 测试extract_lenovo_config.py...
python -c "import extract_lenovo_config; print('extract_lenovo_config OK')"
if errorlevel 1 (
    echo [失败] extract_lenovo_config导入失败
    goto :end
)

echo.
echo ================================================================
echo 所有测试通过！
echo ================================================================
echo.

:end
echo 按任意键退出...
pause >nul
