
"""
调货助手 Demo 测试脚本
测试各个核心模块的功能
"""
import sys
import os
from datetime import datetime

# 确保能找到 src 包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("调货助手 - 功能测试 Demo")
print("=" * 60)
print()

# ========== 1. 测试数据库模块 ==========
print("[1] 测试数据库模块 (database.py)")
print("-" * 60)

from src.models.database import (
    init_db,
    add_product, update_product, delete_product,
    search_products, get_all_products,
    add_batch, get_batches, get_total_remaining,
    add_customer, search_customers, get_all_customers,
    add_quote, search_quotes
)

# 初始化数据库
init_db()
print("✓ 数据库初始化成功")

# 添加测试机型
pid1 = add_product(
    series="拯救者Y9000P",
    cpu="I9-14900HX",
    ram="32G",
    storage="1T",
    gpu="4060",
    screen="16",
    note="新品"
)
print(f"✓ 添加机型成功，ID: {pid1}")

pid2 = add_product(
    series="小新Pro16",
    cpu="U7-155H",
    ram="16G",
    storage="512G",
    gpu="集成",
    screen="16",
    note="办公本"
)
print(f"✓ 添加机型成功，ID: {pid2}")

# 查询所有机型
products = get_all_products()
print(f"✓ 数据库中共有 {len(products)} 条机型")
for p in products:
    print(f"  - {p['series']} | {p['cpu']} | {p['ram']}/{p['storage']}")

# 添加库存批次
bid1 = add_batch(pid1, 8999, 5, 5, "2025-05-20")
print(f"✓ 添加库存批次成功，ID: {bid1}")
bid2 = add_batch(pid1, 8899, 3, 3, "2025-05-21")
print(f"✓ 添加库存批次成功，ID: {bid2}")

# 查看库存批次
batches = get_batches(pid1)
print(f"✓ 该机型共有 {len(batches)} 个批次，总库存 {get_total_remaining(pid1)} 台")

# 添加客户
cid1 = add_customer("张总", "13800138000", "", "", "老客户")
print(f"✓ 添加客户成功，ID: {cid1}")

# 添加报价记录
today = datetime.now().strftime("%Y-%m-%d")
add_quote(bid1, cid1, 9599, today, "特惠价")
print(f"✓ 添加报价记录成功")

# 查询报价记录
quotes = search_quotes()
print(f"✓ 共有 {len(quotes)} 条报价记录")
for q in quotes:
    print(f"  - {q['quote_date']} | {q['customer_name']} | {q['series']} | 报价: ¥{q['quote_price']}")

print()

# ========== 2. 测试图片生成模块 ==========
print("[2] 测试图片生成模块 (image_gen.py)")
print("-" * 60)

from src.utils.image_gen import generate_quote_image, generate_single_quote_card, WATERMARK_TEXT

test_products = [
    {"series": "拯救者Y9000P", "cpu": "I9-14900HX", "ram": "32G", "storage": "1T", "gpu": "4060", "screen": "16", "note": "新品"},
    {"series": "小新Pro16", "cpu": "U7-155H", "ram": "16G", "storage": "512G", "gpu": "集成", "screen": "16", "note": "办公本"}
]

# 测试生成报价卡片
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(output_dir, exist_ok=True)

card_path = os.path.join(output_dir, f"报价_拯救者Y9000P_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
card_path = generate_single_quote_card(
    series="拯救者Y9000P",
    cpu="I9-14900HX",
    ram="32G",
    storage="1T",
    gpu="4060",
    screen="16",
    note="新品",
    customer_name="张总",
    quote_price="¥9599",
    output_path=card_path
)
print(f"✓ 单机报价卡片已生成: {card_path}")

# 测试生成批量报价图片
batch_img_path = os.path.join(output_dir, f"报价批量_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
img_paths = generate_quote_image(test_products, output_path=batch_img_path, rows_per_page=10)
print(f"✓ 批量报价图片已生成: {len(img_paths)} 张")
for p in img_paths:
    print(f"  - {p}")

print()

# ========== 3. 测试 Excel 导出 ==========
print("[3] 测试 Excel 导出模块 (excel_export.py)")
print("-" * 60)

from src.utils.excel_export import export_quotes_to_excel

export_quotes = search_quotes()
if export_quotes:
    excel_path = os.path.join(output_dir, f"报价记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    excel_path = export_quotes_to_excel(export_quotes, output_path=excel_path)
    print(f"✓ 报价记录已导出到 Excel: {excel_path}")

print()
print("=" * 60)
print("✅ Demo 测试完成！所有核心功能正常！")
print("=" * 60)
print("\n总结:")
print("- 数据库操作正常")
print("- 图片生成正常")
print("- Excel 导出正常")
print(f"- 水印文字: {WATERMARK_TEXT}")

