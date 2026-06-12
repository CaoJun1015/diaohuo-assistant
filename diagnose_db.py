"""
数据库诊断脚本 - 检查数据库结构和迁移问题
"""
import sqlite3
import os

def diagnose_database(db_path):
    """诊断数据库问题"""
    print(f"诊断数据库: {db_path}")
    print("=" * 60)
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查 quotes 表结构
    print("\n1. 检查 quotes 表结构:")
    cursor.execute("PRAGMA table_info(quotes)")
    columns = {row[1]: row for row in cursor.fetchall()}
    print(f"   字段数量: {len(columns)}")
    for name, col in columns.items():
        print(f"   - {name}: {col[2]} (NOT NULL: {col[3]}, DEFAULT: {col[4]})")
    
    # 检查是否有 quote_quantity 字段
    if 'quote_quantity' in columns:
        print("\n   [OK] quote_quantity 字段存在")
    else:
        print("\n   [ERROR] quote_quantity 字段不存在!")
        print("   解决方案: 执行 ALTER TABLE quotes ADD COLUMN quote_quantity INTEGER DEFAULT 1")
    
    # 检查是否有 paid 字段
    if 'paid' in columns:
        print("\n   [OK] paid 字段存在")
    else:
        print("\n   [WARNING] paid 字段不存在")
        print("   解决方案: 执行 ALTER TABLE quotes ADD COLUMN paid TEXT")
    
    # 检查 operation_logs 表
    print("\n2. 检查 operation_logs 表:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operation_logs'")
    if cursor.fetchone():
        print("   [OK] operation_logs 表存在")
    else:
        print("   [ERROR] operation_logs 表不存在!")
        print("   解决方案: 创建 operation_logs 表")
    
    # 检查 samples 表
    print("\n3. 检查 batches 表数据:")
    cursor.execute("SELECT COUNT(*) FROM batches")
    batch_count = cursor.fetchone()[0]
    print(f"   批次总数: {batch_count}")
    
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    print(f"   机型总数: {product_count}")
    
    cursor.execute("SELECT COUNT(*) FROM quotes")
    quote_count = cursor.fetchone()[0]
    print(f"   报价总数: {quote_count}")
    
    # 检查报价记录中的 quote_quantity
    if quote_count > 0 and 'quote_quantity' in columns:
        cursor.execute("SELECT quote_quantity FROM quotes LIMIT 5")
        samples = cursor.fetchall()
        print(f"   报价数量示例: {samples}")
    
    conn.close()
    print("\n" + "=" * 60)
    print("诊断完成")

if __name__ == "__main__":
    # 检查开发环境数据库
    db_path = r"D:\OH-workspace\diaohuo-assistant\data\diaohuo.db"
    diagnose_database(db_path)
