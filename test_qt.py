"""
测试PyQt6是否正常工作
"""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("测试1: 导入PyQt6")
try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
    print("OK PyQt6导入成功")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n测试2: 创建QApplication")
try:
    app = QApplication(sys.argv)
    print("OK QApplication创建成功")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n测试3: 创建窗口")
try:
    window = QMainWindow()
    window.setWindowTitle("测试窗口")
    window.setMinimumSize(400, 300)
    print("OK 窗口创建成功")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n测试4: 显示窗口")
try:
    window.show()
    print("OK 窗口显示成功")
    print("\n3秒后自动关闭...")
    import time
    time.sleep(3)
    print("测试完成，程序正常退出")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

input("\n按Enter键退出...")
