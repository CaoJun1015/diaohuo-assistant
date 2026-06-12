
@echo off
chcp 65001 >nul
title 调货助手 v1.0
echo ========================================
echo           调货助手 正在启动...
echo ========================================
python run.py
if errorlevel 1 (
    echo.
    echo 启动出错！请检查是否安装了 Python 和依赖库
    echo.
    pause
)

