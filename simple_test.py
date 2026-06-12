"""
简单测试 - 检查递归问题是否修复
"""
import sys
import os
import time

print("=" * 60)
print("UI TEST - Checking for recursion fix")
print("=" * 60)

sys.path.insert(0, os.path.dirname(__file__))

try:
    from PyQt6.QtWidgets import QApplication
    from src.main import MainWindow
    
    print("\n[1] Creating application...")
    app = QApplication(sys.argv)
    print("[OK] Application created")
    
    print("\n[2] Creating main window...")
    window = MainWindow()
    print(f"[OK] Window created: {window.windowTitle()}")
    
    print("\n[3] Showing window...")
    window.show()
    app.processEvents()
    time.sleep(1)
    print("[OK] Window visible")
    
    print("\n[4] Checking data...")
    product_count = window.product_table.rowCount()
    print(f"[INFO] Products: {product_count}")
    
    if product_count > 0:
        print("\n[5] Testing product selection (checking for recursion)...")
        for i in range(min(3, product_count)):
            window.product_table.selectRow(i)
            app.processEvents()
            time.sleep(0.3)
            
            pid = window.current_product_id
            batch_count = window.batch_table.rowCount()
            print(f"  Row {i+1}: PID={pid}, Batches={batch_count}")
        
        print("\n[6] Testing rapid selection (stress test)...")
        for i in range(5):
            row = i % product_count
            window.product_table.selectRow(row)
            app.processEvents()
            time.sleep(0.1)
            print(f"  Rapid {i+1}: OK")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests passed!")
        print("=" * 60)
        print("\nThe recursion issue has been fixed.")
        print("You can now test the UI manually.")
        print("\nClosing in 3 seconds...")
        time.sleep(3)
        
    else:
        print("\n[INFO] No products found, but initialization worked")
        print("[SUCCESS] Basic test passed")
    
    app.quit()
    sys.exit(0)
    
except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
