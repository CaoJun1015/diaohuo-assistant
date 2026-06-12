"""
测试完整窗口创建
"""
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("1. 导入所有模块...")
try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                                   QWidget, QMessageBox, QProgressBar, QFrame)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent
    print("OK 所有导入成功")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    input("\n按Enter键退出...")
    sys.exit(1)

print("\n2. 创建QApplication...")
try:
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))
    print("OK QApplication创建成功")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    input("\n按Enter键退出...")
    sys.exit(1)

print("\n3. 创建DropArea...")
try:
    class DropArea(QFrame):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setAcceptDrops(True)
            print("OK DropArea初始化成功")
            
            layout = QVBoxLayout(self)
            self.icon_label = QLabel("📄")
            self.icon_label.setFont(QFont("Arial", 60))
            self.text_label = QLabel("拖拽Word文档到此处")
            self.text_label.setFont(QFont("Microsoft YaHei", 14))
            layout.addWidget(self.icon_label)
            layout.addWidget(self.text_label)
            print("OK DropArea布局设置成功")
    
    drop_area = DropArea()
    print("OK DropArea创建成功")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    input("\n按Enter键退出...")
    sys.exit(1)

print("\n4. 创建MainWindow...")
try:
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("联想配置提取工具")
            self.setMinimumSize(500, 400)
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(20, 20, 20, 20)
            
            title_label = QLabel("联想配置提取工具")
            title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(title_label)
            
            main_layout.addSpacing(20)
            
            self.drop_area = DropArea(self)
            main_layout.addWidget(self.drop_area, 1)
            
            print("OK MainWindow创建成功")
    
    window = MainWindow()
    print("OK MainWindow实例化成功")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    input("\n按Enter键退出...")
    sys.exit(1)

print("\n5. 显示窗口...")
try:
    window.show()
    print("OK 窗口显示成功")
    print("\n3秒后自动退出...")
    import time
    time.sleep(3)
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    input("\n按Enter键退出...")
    sys.exit(1)

print("\n所有测试通过！")
input("\n按Enter键退出...")
