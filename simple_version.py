"""
最简单的版本 - 只包含核心功能
"""
import sys
import os
import io
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

LOG_FILE = "simple_log.txt"

def log(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{msg}\n")

def main():
    log("程序开始")
    
    try:
        log("创建QApplication...")
        app = QApplication(sys.argv)
        app.setFont(QFont("Microsoft YaHei", 10))
        
        log("创建MainWindow...")
        window = QMainWindow()
        window.setWindowTitle("联想配置提取工具")
        window.setMinimumSize(500, 400)
        
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("联想配置提取工具 - 简化版")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        log("显示窗口...")
        window.show()
        
        log("进入事件循环...")
        sys.exit(app.exec())
        
    except Exception as e:
        log(f"错误: {type(e).__name__}: {e}")
        import traceback
        log(traceback.format_exc())
        raise

if __name__ == "__main__":
    main()
