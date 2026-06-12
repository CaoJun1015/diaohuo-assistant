
@echo off
chcp 65001 >nul
title 调货助手 - 一键打包工具

echo ========================================
echo      调货助手 一键打包 EXE
echo ========================================
echo.

echo [1/3] 正在升级 PyInstaller...
pip install --upgrade pyinstaller pyinstaller-hooks-contrib
if errorlevel 1 (
    echo 升级失败，请以管理员身份运行！
    pause
    exit /b 1
)

echo.
echo [2/3] 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [3/3] 开始打包 (这可能需要 2-5 分钟)...
pyinstaller --onefile --windowed --name "调货助手 v1.03" --hidden-import PyQt6 --hidden-import PyQt6.QtCore --hidden-import PyQt6.QtGui --hidden-import PyQt6.QtWidgets --hidden-import openpyxl --hidden-import docx --hidden-import PIL run.py

echo.
echo ========================================
if exist "dist\调货助手 v1.03.exe" (
    echo ✓ 打包成功！
    echo.
    echo EXE 文件位置: %cd%\dist\调货助手 v1.03.exe
    echo.
    for %%I in ("dist\调货助手 v1.03.exe") do echo 文件大小: %%~zI 字节 (~%%~zI/1048576 MB)
    echo.
    echo 你可以把 dist 文件夹里的调货助手 v1.03.exe 复制到任何电脑使用！
) else (
    echo ✗ 打包失败，请检查错误信息
)
echo ========================================
echo.
pause

