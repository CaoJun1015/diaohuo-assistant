"""
调试运行脚本 - 捕获并显示所有错误
"""
import sys
import os
import traceback

print("Starting debug run...")
print(f"Python: {sys.version}")
print(f"Working directory: {os.getcwd()}")

try:
    print("\nImporting modules...")
    from src.models.database import init_db
    print("Database module imported")
    
    print("\nInitializing database...")
    init_db()
    print("Database initialized")
    
    print("\nStarting application...")
    from PyQt6.QtWidgets import QApplication
    from src.main import MainWindow
    
    app = QApplication(sys.argv)
    print("QApplication created")
    
    window = MainWindow()
    print(f"MainWindow created: {window.windowTitle()}")
    
    print("\nShowing window...")
    window.show()
    print("Window shown")
    
    print("\n[SUCCESS] Application started successfully!")
    print("=" * 60)
    print("You can now interact with the application.")
    print("Close the window to exit.")
    print("=" * 60)
    
    sys.exit(app.exec())
    
except Exception as e:
    print(f"\n[ERROR] Failed to start: {e}")
    traceback.print_exc()
    input("\nPress Enter to exit...")
    sys.exit(1)
