import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.database import init_db, add_product, get_all_products, add_batch
from src.main import MainWindow, QApplication

def test_ui_interaction():
    init_db()
    
    products = get_all_products()
    if not products:
        print("正在添加测试数据...")
        add_product(series="测试机型", cpu="i7", ram="16GB", storage="512GB", gpu="RTX4060", screen="15.6\"", note="测试用")
        products = get_all_products()
    
    print(f"当前有机型: {len(products)} 条")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    
    window.show()
    
    if products:
        window.product_table.selectRow(0)
        print("已选中第一行机型，触发 on_product_selected")
        
        selected_row = window.product_table.currentRow()
        if selected_row >= 0:
            pid = int(window.product_table.item(selected_row, 0).text())
            print(f"选中的机型ID: {pid}")
            print(f"报价面板当前产品ID: {window.quote_panel.current_product_id}")
            print("测试通过！机型选择没有崩溃")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_ui_interaction()