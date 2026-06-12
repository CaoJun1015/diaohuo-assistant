"""
测试导入问题 - 非GUI版本
"""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("开始测试导入...")

print("\n1. 测试基本导入")
try:
    import os
    print("OK os")
except Exception as e:
    print(f"FAIL os: {e}")

try:
    import re
    print("OK re")
except Exception as e:
    print(f"FAIL re: {e}")

try:
    import zipfile
    print("OK zipfile")
except Exception as e:
    print(f"FAIL zipfile: {e}")

try:
    import xml.etree.ElementTree
    print("OK xml.etree.ElementTree")
except Exception as e:
    print(f"FAIL xml.etree.ElementTree: {e}")

try:
    from docx import Document
    print("OK docx.Document")
except Exception as e:
    print(f"FAIL docx.Document: {e}")

try:
    import docx
    print("OK docx")
except Exception as e:
    print(f"FAIL docx: {e}")

print("\n2. 测试PyQt6导入")
try:
    from PyQt6.QtCore import QThread, pyqtSignal
    print("OK PyQt6.QtCore")
except Exception as e:
    print(f"FAIL PyQt6.QtCore: {e}")
    import traceback
    traceback.print_exc()

try:
    from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent
    print("OK PyQt6.QtGui")
except Exception as e:
    print(f"FAIL PyQt6.QtGui: {e}")
    import traceback
    traceback.print_exc()

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout
    print("OK PyQt6.QtWidgets")
except Exception as e:
    print(f"FAIL PyQt6.QtWidgets: {e}")
    import traceback
    traceback.print_exc()

print("\n3. 测试datetime")
try:
    from datetime import datetime
    print("OK datetime")
except Exception as e:
    print(f"FAIL datetime: {e}")

print("\n测试完成")
input("\n按Enter键退出...")
