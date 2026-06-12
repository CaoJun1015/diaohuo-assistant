"""
数据库修复脚本 - 从 v1.02 升级到 v1.03
"""
import sqlite3
import os
import shutil
from datetime import datetime

def backup_old_db(db_path):
    """备份旧数据库"""
    if os.path.exists(db_path):
        backup_path = db_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(db_path, backup_path)
        print(f"已备份旧数据库: {backup_path}")
        return True
    return False

def fix_database(db_path):
    """修复数据库结构"""
    print(f"\n修复数据库: {db_path}")
    print("=" * 60)
    
    if not os.path.exists(db_path):
        print("错误: 数据库文件不存在!")
        return False
    
    backup_old_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    changes = []
    
    # 1. 添加 paid 字段
    cursor.execute("PRAGMA table_info(quotes)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "paid" not in columns:
        try:
            cursor.execute("ALTER TABLE quotes ADD COLUMN paid TEXT")
            cursor.execute("UPDATE quotes SET paid='否' WHERE paid IS NULL")
            changes.append("添加 paid 字段")
            print("[OK] 添加 paid 字段")
        except Exception as e:
            print(f"[ERROR] 添加 paid 字段失败: {e}")
    else:
        print("[OK] paid 字段已存在")
    
    # 2. 添加 quote_quantity 字段
    if "quote_quantity" not in columns:
        try:
            cursor.execute("ALTER TABLE quotes ADD COLUMN quote_quantity INTEGER DEFAULT 1")
            cursor.execute("UPDATE quotes SET quote_quantity=1 WHERE quote_quantity IS NULL")
            changes.append("添加 quote_quantity 字段")
            print("[OK] 添加 quote_quantity 字段")
        except Exception as e:
            print(f"[ERROR] 添加 quote_quantity 字段失败: {e}")
    else:
        print("[OK] quote_quantity 字段已存在")
    
    # 3. 创建 operation_logs 表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operation_logs'")
    if not cursor.fetchone():
        try:
            cursor.execute("""
                CREATE TABLE operation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id INTEGER,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            changes.append("创建 operation_logs 表")
            print("[OK] 创建 operation_logs 表")
        except Exception as e:
            print(f"[ERROR] 创建 operation_logs 表失败: {e}")
    else:
        print("[OK] operation_logs 表已存在")
    
    # 4. 创建索引
    indexes = [
        ("idx_products_series", "CREATE INDEX IF NOT EXISTS idx_products_series ON products(series)"),
        ("idx_quotes_date", "CREATE INDEX IF NOT EXISTS idx_quotes_date ON quotes(quote_date)"),
        ("idx_quotes_customer", "CREATE INDEX IF NOT EXISTS idx_quotes_customer ON quotes(customer_id)"),
        ("idx_logs_time", "CREATE INDEX IF NOT EXISTS idx_logs_time ON operation_logs(created_at)")
    ]
    
    for idx_name, idx_sql in indexes:
        try:
            cursor.execute(idx_sql)
            print(f"[OK] 索引 {idx_name} 已创建")
        except Exception as e:
            print(f"[WARNING] 索引 {idx_name} 创建失败: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    if changes:
        print("修复完成! 执行的变更:")
        for change in changes:
            print(f"  - {change}")
    else:
        print("数据库已经是最新版本，无需修复")
    
    return True

if __name__ == "__main__":
    print("调货助手数据库修复工具")
    print("用于从 v1.02 升级到 v1.03")
    print()
    
    # 查找数据库文件
    possible_paths = [
        r"D:\OH-workspace\diaohuo-assistant\data\diaohuo.db",
        r"data\diaohuo.db",
        r".\data\diaohuo.db",
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("未找到数据库文件!")
        print("请确保 diaohuo.db 文件位于 data/ 目录下")
        input("\n按回车键退出...")
        exit(1)
    
    print(f"找到数据库: {db_path}")
    
    fix_database(db_path)
    
    print("\n现在可以运行程序了!")
    input("\n按回车键退出...")
