"""
简单测试：检查Python环境和必要模块
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Python版本:", sys.version)
print()

# 测试1: 检查PyQt6
print("[测试1] 检查PyQt6...")
try:
    from PyQt6.QtWidgets import QApplication
    print("OK PyQt6 正常")
except ImportError as e:
    print(f"FAIL PyQt6 导入失败: {e}")
    print("请运行: pip install PyQt6")

# 测试2: 检查docx
print("\n[测试2] 检查python-docx...")
try:
    from docx import Document
    print("OK python-docx 正常")
except ImportError as e:
    print(f"FAIL python-docx 导入失败: {e}")
    print("请运行: pip install python-docx")

# 测试3: 检查其他模块
print("\n[测试3] 检查其他模块...")
try:
    import re
    import zipfile
    import xml.etree.ElementTree as ET
    print("OK re, zipfile, xml 模块正常")
except ImportError as e:
    print(f"FAIL 模块导入失败: {e}")

# 测试4: 尝试导入主程序
print("\n[测试4] 导入主程序...")
try:
    import extract_tool_gui
    print("OK extract_tool_gui 模块导入成功")
except Exception as e:
    print(f"FAIL extract_tool_gui 模块导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

input("\n按Enter键退出...")
