"""
检查孤立批次数据 - 可能导致程序崩溃
"""
import sqlite3

def check_orphan_batches(db_path):
    """检查孤立的批次数据"""
    print(f"检查数据库: {db_path}")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查孤立的批次（batches.product_id 不存在）
    cursor.execute("""
        SELECT b.id, b.product_id, p.id 
        FROM batches b
        LEFT JOIN products p ON b.product_id = p.id
        WHERE p.id IS NULL
    """)
    orphan_batches = cursor.fetchall()
    
    if orphan_batches:
        print(f"\n[WARNING] 发现 {len(orphan_batches)} 条孤立批次!")
        for batch in orphan_batches[:10]:
            print(f"   批次ID: {batch[0]}, product_id: {batch[1]}")
    else:
        print("\n[OK] 没有孤立批次")
    
    # 检查孤立的报价（quotes.batch_id 不存在）
    cursor.execute("""
        SELECT q.id, q.batch_id, b.id
        FROM quotes q
        LEFT JOIN batches b ON q.batch_id = b.id
        WHERE b.id IS NULL
    """)
    orphan_quotes = cursor.fetchall()
    
    if orphan_quotes:
        print(f"\n[WARNING] 发现 {len(orphan_quotes)} 条孤立报价!")
        for quote in orphan_quotes[:10]:
            print(f"   报价ID: {quote[0]}, batch_id: {quote[1]}")
    else:
        print("\n[OK] 没有孤立报价")
    
    # 检查孤立的客户（quotes.customer_id 不存在）
    cursor.execute("""
        SELECT q.id, q.customer_id, c.id
        FROM quotes q
        LEFT JOIN customers c ON q.customer_id = c.id
        WHERE q.customer_id IS NOT NULL AND c.id IS NULL
    """)
    orphan_customers = cursor.fetchall()
    
    if orphan_customers:
        print(f"\n[WARNING] 发现 {len(orphan_customers)} 条孤立客户引用!")
    else:
        print("\n[OK] 没有孤立客户引用")
    
    # 检查报价记录中的 quote_quantity 是否为 NULL
    cursor.execute("SELECT COUNT(*) FROM quotes WHERE quote_quantity IS NULL")
    null_quantity = cursor.fetchone()[0]
    if null_quantity > 0:
        print(f"\n[WARNING] 发现 {null_quantity} 条报价记录的 quote_quantity 为 NULL!")
        print("   这可能导致统计计算错误")
    else:
        print("\n[OK] 所有报价记录的 quote_quantity 都有值")
    
    conn.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    import os
    db_path = r"D:\OH-workspace\diaohuo-assistant\data\diaohuo.db"
    if os.path.exists(db_path):
        check_orphan_batches(db_path)
    else:
        print(f"数据库文件不存在: {db_path}")
