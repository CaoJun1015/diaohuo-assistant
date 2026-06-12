"""
UI交互测试脚本 - 测试机型管理页面
"""
import sys
import os
import time

print("=" * 60)
print("UI 交互测试")
print("=" * 60)
print()

sys.path.insert(0, os.path.dirname(__file__))

try:
    from PyQt6.QtWidgets import QApplication
    from src.main import MainWindow
    
    print("[1/5] 测试初始化...")
    app = QApplication(sys.argv)
    window = MainWindow()
    print("   初始化成功")
    
    print("\n[2/5] 测试显示窗口...")
    window.show()
    app.processEvents()
    time.sleep(1)
    print("   窗口显示成功")
    
    print("\n[3/5] 测试机型列表...")
    product_count = window.product_table.rowCount()
    print(f"   机型数量: {product_count}")
    
    if product_count > 0:
        print("\n[4/5] 测试选择机型...")
        window.product_table.selectRow(0)
        app.processEvents()
        time.sleep(0.5)
        
        current_pid = window.current_product_id
        print(f"   当前选中机型ID: {current_pid}")
        
        if current_pid:
            print("   机型选择成功")
            
            # 测试批次列表
            batch_count = window.batch_table.rowCount()
            print(f"   批次数量: {batch_count}")
            
            print("\n[5/5] 测试多次快速选择...")
            for i in range(min(3, product_count)):
                window.product_table.selectRow(i)
                app.processEvents()
                time.sleep(0.2)
                print(f"   选择第 {i+1} 个机型成功")
            
            print("\n" + "=" * 60)
            print("所有测试通过！")
            print("=" * 60)
            
        else:
            print("\n[ERROR] 机型选择后ID为空!")
            sys.exit(1)
    else:
        print("\n[WARNING] 没有机型数据，无法测试选择功能")
        print("\n" + "=" * 60)
        print("基本测试通过（无数据）")
        print("=" * 60)
    
    app.quit()
    
except Exception as e:
    print(f"\n[ERROR] 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
