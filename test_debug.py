"""
详细的UI交互测试 - 包含日志输出
"""
import sys
import os
import time

print("=" * 60)
print("调货助手 v1.03 - UI交互详细测试")
print("=" * 60)
print()

sys.path.insert(0, os.path.dirname(__file__))

try:
    print("[步骤1] 导入必要的模块...")
    from PyQt6.QtWidgets import QApplication
    from src.main import MainWindow
    print("✓ 模块导入成功")
    
    print("\n[步骤2] 创建应用和窗口...")
    app = QApplication(sys.argv)
    window = MainWindow()
    print(f"✓ 窗口创建成功，标题: {window.windowTitle()}")
    
    print("\n[步骤3] 显示窗口...")
    window.show()
    app.processEvents()
    print("✓ 窗口已显示")
    
    # 等待窗口稳定
    print("\n[步骤4] 等待窗口初始化...")
    time.sleep(1)
    app.processEvents()
    
    print("\n[步骤5] 检查数据...")
    product_count = window.product_table.rowCount()
    print(f"✓ 机型列表行数: {product_count}")
    
    customer_count = window.customer_table.rowCount()
    print(f"✓ 客户列表行数: {customer_count}")
    
    if product_count > 0:
        print("\n[步骤6] 测试选择第一个机型...")
        window.product_table.selectRow(0)
        app.processEvents()
        time.sleep(0.5)
        
        current_pid = window.current_product_id
        print(f"✓ 选中机型ID: {current_pid}")
        
        if current_pid:
            print("✓ 机型选择成功")
            
            # 检查批次
            batch_count = window.batch_table.rowCount()
            print(f"✓ 批次列表行数: {batch_count}")
            
            # 检查库存显示
            stock_item = window.product_table.item(0, 8)
            if stock_item:
                print(f"✓ 库存显示: {stock_item.text()}")
            
            print("\n[步骤7] 快速切换选择（测试递归）...")
            for i in range(min(5, product_count)):
                window.product_table.selectRow(i)
                app.processEvents()
                time.sleep(0.3)
                
                pid = window.current_product_id
                batch_count = window.batch_table.rowCount()
                print(f"  选择 {i+1}: PID={pid}, 批次={batch_count}")
            
            print("\n" + "=" * 60)
            print("✓ 所有测试通过！程序运行正常！")
            print("=" * 60)
            print("\n现在你可以手动测试：")
            print("1. 点击左侧机型列表")
            print("2. 切换不同机型")
            print("3. 新增批次")
            print("4. 报价测试")
            print("\n关闭程序后按回车键结束测试...")
            
            # 等待用户关闭
            app.exec()
            
        else:
            print("\n✗ 机型选择失败：current_product_id 为空")
            sys.exit(1)
    else:
        print("\n! 警告：没有机型数据")
        print("  这是正常现象，请先添加机型数据")
        
    print("\n测试结束")
    
except Exception as e:
    print(f"\n✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
