"""
数据库模型定义：机型、批次库存、客户、报价记录
"""

import sqlite3
import os
import sys
import shutil
from datetime import datetime

BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "backup")
MAX_BACKUPS = 7

def get_app_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

APP_DATA_DIR = os.path.join(get_app_path(), "data")
DB_PATH = os.path.join(APP_DATA_DIR, "diaohuo.db")


def get_connection():
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def backup_database():
    """自动备份数据库，保留最近MAX_BACKUPS个备份"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        if not os.path.exists(DB_PATH):
            return True, "数据库文件不存在，跳过备份"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"diaohuo_backup_{timestamp}.db")
        
        shutil.copy2(DB_PATH, backup_path)
        
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("diaohuo_backup_")], reverse=True)
        if len(backups) > MAX_BACKUPS:
            for old_backup in backups[MAX_BACKUPS:]:
                os.remove(os.path.join(BACKUP_DIR, old_backup))
        
        return True, f"备份成功: {os.path.basename(backup_path)}"
    except Exception as e:
        return False, f"备份失败: {str(e)}"


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series TEXT NOT NULL,          -- 系列，如 Y7000P、小新Pro16
            cpu TEXT,                      -- CPU 型号
            ram TEXT,                      -- 内存
            storage TEXT,                  -- 硬盘
            gpu TEXT,                      -- 显卡
            screen TEXT,                   -- 屏幕尺寸
            note TEXT,                     -- 备注（颜色、新品等）
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            purchase_price REAL NOT NULL,  -- 购入价
            quantity INTEGER NOT NULL,     -- 进货数量
            remaining INTEGER NOT NULL,    -- 剩余数量
            date TEXT NOT NULL,            -- 入库日期 YYYY-MM-DD
            remark TEXT,                   -- 备注（含税/未税等）
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            wechat TEXT,
            qq TEXT,
            phone TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            wechat TEXT,
            qq TEXT,
            phone TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            customer_id INTEGER,
            quote_price REAL NOT NULL,      -- 对外报价
            quote_quantity INTEGER NOT NULL DEFAULT 1,  -- 报价数量
            quote_date TEXT NOT NULL,       -- 报价日期 YYYY-MM-DD
            remark TEXT,                    -- 备注
            paid TEXT,                      -- 是否打款（是/否）
            status TEXT DEFAULT '待确认',   -- 状态：待确认/已报价/已出库/已收款/已取消
            received_amount REAL DEFAULT 0, -- 已收金额
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (batch_id) REFERENCES batches(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_id INTEGER,
            customer_id INTEGER,
            supplier_id INTEGER,
            type TEXT NOT NULL,             -- 'receivable' 收款 / 'payable' 付款
            amount REAL NOT NULL,
            pay_date TEXT,
            method TEXT,                    -- 现金/转账/微信/支付宝
            remark TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quote_id) REFERENCES quotes(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        );
    """)
    
    cursor.execute("PRAGMA table_info(quotes)")
    columns = [col[1] for col in cursor.fetchall()]
    if "paid" not in columns:
        try:
            cursor.execute("ALTER TABLE quotes ADD COLUMN paid TEXT")
            cursor.execute("UPDATE quotes SET paid='否' WHERE paid IS NULL")
        except:
            pass
    
    if "quote_quantity" not in columns:
        try:
            cursor.execute("ALTER TABLE quotes ADD COLUMN quote_quantity INTEGER DEFAULT 1")
            cursor.execute("UPDATE quotes SET quote_quantity=1 WHERE quote_quantity IS NULL")
        except:
            pass
    
    cursor.execute("PRAGMA table_info(batches)")
    batch_columns = [col[1] for col in cursor.fetchall()]
    if "remark" not in batch_columns:
        try:
            cursor.execute("ALTER TABLE batches ADD COLUMN remark TEXT")
        except:
            pass

    if "supplier_id" not in batch_columns:
        try:
            cursor.execute("ALTER TABLE batches ADD COLUMN supplier_id INTEGER REFERENCES suppliers(id)")
        except:
            pass

    if "sn_list" not in batch_columns:
        try:
            cursor.execute("ALTER TABLE batches ADD COLUMN sn_list TEXT")
        except:
            pass

    if "status" not in columns:
        try:
            cursor.execute("ALTER TABLE quotes ADD COLUMN status TEXT DEFAULT '待确认'")
            cursor.execute("UPDATE quotes SET status='待确认' WHERE status IS NULL")
        except:
            pass

    if "received_amount" not in columns:
        try:
            cursor.execute("ALTER TABLE quotes ADD COLUMN received_amount REAL DEFAULT 0")
        except:
            pass

    if "sn_list" not in columns:
        try:
            cursor.execute("ALTER TABLE quotes ADD COLUMN sn_list TEXT")
        except:
            pass

    cursor.execute("PRAGMA table_info(customers)")
    customer_cols = [col[1] for col in cursor.fetchall()]
    if "balance" not in customer_cols:
        try:
            cursor.execute("ALTER TABLE customers ADD COLUMN balance REAL DEFAULT 0")
        except:
            pass

    cursor.execute("PRAGMA table_info(suppliers)")
    supplier_cols = [col[1] for col in cursor.fetchall()]
    if "balance" not in supplier_cols:
        try:
            cursor.execute("ALTER TABLE suppliers ADD COLUMN balance REAL DEFAULT 0")
        except:
            pass
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except:
        pass

    # 价格快照表（Skill 2: 价格异动哨兵）
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                import_date TEXT NOT NULL,
                item_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_snapshot_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER NOT NULL,
                series TEXT,
                cpu TEXT,
                ram TEXT,
                storage TEXT,
                gpu TEXT,
                note TEXT,
                norm_key TEXT,
                FOREIGN KEY (snapshot_id) REFERENCES price_snapshots(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshot_date ON price_snapshots(import_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshot_items ON price_snapshot_items(snapshot_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshot_normkey ON price_snapshot_items(norm_key)")
    except:
        pass
    
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_series ON products(series)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quotes_date ON quotes(quote_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quotes_customer ON quotes(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_time ON operation_logs(created_at)")
    except:
        pass
    
    conn.commit()
    conn.close()

    # 启动时自动备份
    backup_database()

    return True, "数据库初始化成功"


# ---------- 机型管理 ----------

def add_product(series, cpu="", ram="", storage="", gpu="", screen="", note=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO products (series, cpu, ram, storage, gpu, screen, note) VALUES (?,?,?,?,?,?,?)",
        (series, cpu, ram, storage, gpu, screen, note),
    )
    conn.commit()
    pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return pid


def update_product(pid, series, cpu, ram, storage, gpu, screen, note):
    conn = get_connection()
    conn.execute(
        "UPDATE products SET series=?, cpu=?, ram=?, storage=?, gpu=?, screen=?, note=? WHERE id=?",
        (series, cpu, ram, storage, gpu, screen, note, pid),
    )
    conn.commit()
    conn.close()


def delete_product(pid):
    """
    删除机型，级联删除关联数据

    特殊处理：
    - 回滚各关联批次的供应商欠款
    - 级联删除报价和付款记录
    """
    conn = get_connection()
    try:
        conn.execute("PRAGMA foreign_keys = OFF")

        # 先回滚各批次的供应商欠款
        batch_rows = conn.execute(
            "SELECT supplier_id, purchase_price, quantity FROM batches WHERE product_id=? AND supplier_id IS NOT NULL",
            (pid,)
        ).fetchall()
        for row in batch_rows:
            total = row["purchase_price"] * row["quantity"]
            conn.execute(
                "UPDATE suppliers SET balance = balance - ? WHERE id=?",
                (total, row["supplier_id"])
            )

        conn.execute("DELETE FROM payments WHERE quote_id IN (SELECT id FROM quotes WHERE batch_id IN (SELECT id FROM batches WHERE product_id=?))", (pid,))
        conn.execute("DELETE FROM quotes WHERE batch_id IN (SELECT id FROM batches WHERE product_id=?)", (pid,))
        conn.execute("DELETE FROM batches WHERE product_id=?", (pid,))
        conn.execute("DELETE FROM products WHERE id=?", (pid,))
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def search_products(keyword):
    conn = get_connection()
    like = f"%{keyword}%"
    rows = conn.execute(
        """
        SELECT id, series, cpu, ram, storage, gpu, screen, note
        FROM products
        WHERE series LIKE ? OR cpu LIKE ? OR ram LIKE ? OR storage LIKE ? OR gpu LIKE ? OR screen LIKE ? OR note LIKE ?
        ORDER BY series, cpu
        """,
        (like, like, like, like, like, like, like),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_products():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, series, cpu, ram, storage, gpu, screen, note FROM products ORDER BY series, cpu"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- 批次库存管理 ----------

def add_batch(product_id, purchase_price, quantity, remaining, date_str, remark="", supplier_id=None, sn_list=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO batches (product_id, purchase_price, quantity, remaining, date, remark, supplier_id, sn_list) VALUES (?,?,?,?,?,?,?,?)",
        (product_id, purchase_price, quantity, remaining, date_str, remark, supplier_id, sn_list),
    )
    if supplier_id:
        conn.execute(
            "UPDATE suppliers SET balance = COALESCE(balance, 0) + ? WHERE id=?",
            (purchase_price * quantity, supplier_id),
        )
    conn.commit()
    bid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return bid


def get_batches(product_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, product_id, purchase_price, quantity, remaining, date, remark, supplier_id, sn_list FROM batches WHERE product_id=? ORDER BY date DESC, id DESC",
        (product_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_batch_remaining(batch_id, new_remaining):
    conn = get_connection()
    conn.execute("UPDATE batches SET remaining=? WHERE id=?", (new_remaining, batch_id))
    conn.commit()
    conn.close()


def deduct_batch_remaining(batch_id, quantity):
    """扣减批次库存，返回是否成功"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT remaining FROM batches WHERE id=?", (batch_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "批次不存在"
    
    current_remaining = row[0]
    if current_remaining < quantity:
        conn.close()
        return False, f"库存不足！当前剩余 {current_remaining} 台，报价 {quantity} 台"
    
    new_remaining = current_remaining - quantity
    conn.execute("UPDATE batches SET remaining=? WHERE id=?", (new_remaining, batch_id))
    conn.commit()
    conn.close()
    return True, f"扣减成功，剩余 {new_remaining} 台"


def get_batch_remaining(batch_id):
    """获取指定批次的剩余库存"""
    conn = get_connection()
    cursor = conn.execute("SELECT remaining FROM batches WHERE id=?", (batch_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0


def delete_batch(batch_id):
    """
    删除批次

    特殊处理：
    - 回滚供应商欠款（如果批次有关联供应商）
    - 级联删除关联的报价和付款记录
    """
    conn = get_connection()
    try:
        # 先查询批次信息，用于回滚供应商欠款
        row = conn.execute(
            "SELECT supplier_id, purchase_price, quantity FROM batches WHERE id=?", (batch_id,)
        ).fetchone()

        conn.execute("PRAGMA foreign_keys = OFF")

        # 回滚供应商欠款
        if row and row[0]:
            total = row[1] * row[2]
            conn.execute(
                "UPDATE suppliers SET balance = balance - ? WHERE id=?",
                (total, row[0])
            )

        conn.execute("DELETE FROM payments WHERE quote_id IN (SELECT id FROM quotes WHERE batch_id=?)", (batch_id,))
        conn.execute("DELETE FROM quotes WHERE batch_id=?", (batch_id,))
        conn.execute("DELETE FROM batches WHERE id=?", (batch_id,))
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_total_remaining(product_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(remaining),0) FROM batches WHERE product_id=?", (product_id,)
    ).fetchone()[0]
    conn.close()
    return row


# ---------- 客户管理 ----------

def add_customer(name, wechat="", qq="", phone="", note=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO customers (name, wechat, qq, phone, note) VALUES (?,?,?,?,?)",
        (name, wechat, qq, phone, note),
    )
    conn.commit()
    cid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return cid


def search_customers(keyword):
    conn = get_connection()
    kw = f"%{keyword}%"
    rows = conn.execute(
        "SELECT id, name, wechat, qq, phone, note FROM customers WHERE name LIKE ? OR wechat LIKE ? OR qq LIKE ? OR phone LIKE ? OR note LIKE ? ORDER BY name",
        (kw, kw, kw, kw, kw),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_customers():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, wechat, qq, phone, note FROM customers ORDER BY name"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- 上游管理 ----------

def add_supplier(name, wechat="", qq="", phone="", note=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO suppliers (name, wechat, qq, phone, note) VALUES (?,?,?,?,?)",
        (name, wechat, qq, phone, note),
    )
    conn.commit()
    sid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return sid


def search_suppliers(keyword):
    conn = get_connection()
    kw = f"%{keyword}%"
    rows = conn.execute(
        "SELECT id, name, wechat, qq, phone, note FROM suppliers WHERE name LIKE ? OR wechat LIKE ? OR qq LIKE ? OR phone LIKE ? OR note LIKE ? ORDER BY name",
        (kw, kw, kw, kw, kw),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_suppliers():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, wechat, qq, phone, note FROM suppliers ORDER BY name"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_customer_cascade(customer_id):
    """级联删除客户及其关联的付款记录、报价记录。返回受影响记录数。"""
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = OFF")
    quote_count = conn.execute("SELECT COUNT(*) FROM quotes WHERE customer_id=?", (customer_id,)).fetchone()[0]
    payment_count = conn.execute("SELECT COUNT(*) FROM payments WHERE customer_id=?", (customer_id,)).fetchone()[0]
    conn.execute("DELETE FROM payments WHERE customer_id=?", (customer_id,))
    conn.execute("DELETE FROM payments WHERE quote_id IN (SELECT id FROM quotes WHERE customer_id=?)", (customer_id,))
    conn.execute("DELETE FROM quotes WHERE customer_id=?", (customer_id,))
    conn.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    conn.close()
    return {"quotes": quote_count, "payments": payment_count}


def delete_supplier_cascade(supplier_id):
    """级联删除上游及其关联的付款记录。批次的上游字段设为NULL。返回受影响记录数。"""
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = OFF")
    batch_count = conn.execute("SELECT COUNT(*) FROM batches WHERE supplier_id=?", (supplier_id,)).fetchone()[0]
    payment_count = conn.execute("SELECT COUNT(*) FROM payments WHERE supplier_id=?", (supplier_id,)).fetchone()[0]
    conn.execute("DELETE FROM payments WHERE supplier_id=?", (supplier_id,))
    conn.execute("UPDATE batches SET supplier_id=NULL WHERE supplier_id=?", (supplier_id,))
    conn.execute("DELETE FROM suppliers WHERE id=?", (supplier_id,))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    conn.close()
    return {"batches": batch_count, "payments": payment_count}


# ---------- 报价记录 ----------

def add_quote(batch_id, customer_id, quote_price, quote_quantity, quote_date, remark="", paid="", status="待确认", received_amount=0, sn_list=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO quotes (batch_id, customer_id, quote_price, quote_quantity, quote_date, remark, paid, status, received_amount, sn_list) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (batch_id, customer_id, quote_price, quote_quantity, quote_date, remark, paid, status, received_amount, sn_list),
    )
    conn.commit()
    qid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return qid


def update_quote(quote_id, batch_id, customer_id, quote_price, quote_quantity, quote_date, remark, paid, sn_list=""):
    conn = get_connection()
    conn.execute(
        "UPDATE quotes SET batch_id=?, customer_id=?, quote_price=?, quote_quantity=?, quote_date=?, remark=?, paid=?, sn_list=? WHERE id=?",
        (batch_id, customer_id, quote_price, quote_quantity, quote_date, remark, paid, sn_list, quote_id),
    )
    conn.commit()
    conn.close()


def delete_quote(quote_id):
    """
    删除报价记录

    特殊处理：
    - 如果报价状态为"已出库"，先回补库存再删除
    - 级联删除关联的收付款记录
    - 注意：出库时 SN 保存到 quotes.sn_list，batches.sn_list 不被修改，删除时无需处理 SN
    """
    conn = get_connection()
    try:
        # 获取报价信息，判断是否需要回补库存
        row = conn.execute(
            "SELECT status, batch_id, quote_quantity FROM quotes WHERE id=?",
            (quote_id,)
        ).fetchone()

        if row and row[0] == "已出库":
            batch_id = row[1]
            quote_quantity = row[2] or 0

            # 回补库存
            conn.execute(
                "UPDATE batches SET remaining = remaining + ? WHERE id = ?",
                (quote_quantity, batch_id)
            )

        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("DELETE FROM payments WHERE quote_id=?", (quote_id,))
        conn.execute("DELETE FROM quotes WHERE id=?", (quote_id,))
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_quote_by_id(quote_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT q.id, q.batch_id, q.customer_id, q.quote_price, q.quote_quantity, q.quote_date, q.remark, q.paid, q.status, q.received_amount, q.sn_list, "
        "p.series, p.cpu, p.ram, p.storage, p.gpu, "
        "b.purchase_price, b.sn_list as batch_sn_list, "
        "c.name as customer_name "
        "FROM quotes q "
        "JOIN batches b ON q.batch_id = b.id "
        "JOIN products p ON b.product_id = p.id "
        "LEFT JOIN customers c ON q.customer_id = c.id "
        "WHERE q.id=?",
        (quote_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def search_quotes(keyword="", date_from="", date_to="", customer_id=None):
    conn = get_connection()
    conditions = []
    params = []

    if keyword:
        kw = f"%{keyword}%"
        conditions.append("(p.series LIKE ? OR p.cpu LIKE ? OR p.ram LIKE ? OR p.storage LIKE ? OR p.gpu LIKE ? OR c.name LIKE ? OR b.remark LIKE ? OR q.remark LIKE ? OR b.sn_list LIKE ? OR s.name LIKE ?)")
        params.extend([kw] * 10)
    if date_from:
        conditions.append("q.quote_date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("q.quote_date <= ?")
        params.append(date_to)
    if customer_id:
        conditions.append("q.customer_id = ?")
        params.append(customer_id)

    where = " AND ".join(conditions) if conditions else "1=1"
    sql = f"""
        SELECT q.id, q.quote_price, q.quote_quantity, q.quote_date, q.remark, q.paid, q.status, q.received_amount, q.sn_list,
               p.series, p.cpu, p.ram, p.storage, p.gpu, p.screen, p.note,
               b.purchase_price, b.remark as batch_remark, b.id as batch_id, b.sn_list as batch_sn_list,
               c.name as customer_name, c.id as customer_id,
               s.name as supplier_name
        FROM quotes q
        JOIN batches b ON q.batch_id = b.id
        JOIN products p ON b.product_id = p.id
        LEFT JOIN customers c ON q.customer_id = c.id
        LEFT JOIN suppliers s ON b.supplier_id = s.id
        WHERE {where}
        ORDER BY q.quote_date DESC, q.id DESC
    """
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def export_quotes(date_from="", date_to="", customer_id=None):
    """导出的数据包含完整财务信息"""
    return search_quotes("", date_from, date_to, customer_id)


# 合法状态流转表
VALID_TRANSITIONS = {
    "待确认": ["已报价", "已取消"],
    "已报价": ["已出库", "已取消"],
    "已出库": ["已收款", "已取消"],
    "已收款": [],
    "已取消": [],
}


def ship_quote(quote_id, sn_list=""):
    """
    出库操作（封装校验+扣减+保存SN+状态更新）

    步骤：
    1. 校验报价是否存在
    2. 校验状态是否允许出库（待确认/已报价）
    3. 校验库存是否充足
    4. 扣减 batches.remaining
    5. 保存 SN 到 quotes.sn_list
    6. 更新状态为"已出库"

    返回 (True, "出库成功") 或 (False, 错误信息)
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT status, batch_id, quote_quantity FROM quotes WHERE id=?",
            (quote_id,)
        ).fetchone()
        if not row:
            return False, "报价记录不存在"

        old_status = row[0]
        batch_id = row[1]
        quote_quantity = row[2] or 0

        # 校验状态
        if old_status not in ("待确认", "已报价"):
            return False, f"当前状态「{old_status}」不允许出库"

        # 校验库存
        batch_row = conn.execute(
            "SELECT remaining FROM batches WHERE id=?", (batch_id,)
        ).fetchone()
        if not batch_row or batch_row[0] < quote_quantity:
            return False, "库存不足，无法出库"

        # 执行出库
        conn.execute(
            "UPDATE batches SET remaining = remaining - ? WHERE id = ?",
            (quote_quantity, batch_id)
        )
        conn.execute(
            "UPDATE quotes SET status='已出库', sn_list=? WHERE id=?",
            (sn_list, quote_id)
        )
        conn.commit()
        return True, "出库成功"
    except Exception as e:
        conn.rollback()
        return False, f"出库失败: {str(e)}"
    finally:
        conn.close()


def update_quote_status(quote_id, new_status):
    """
    更新报价状态（带状态机守卫）

    特殊处理：
    - 校验状态流转合法性，非法跳转返回 (False, 错误信息)
    - 从"已出库"变为"已取消"时，回补库存 + 清空报价SN
    - 返回 (True, "状态更新成功") 或 (False, 错误信息)
    """
    conn = get_connection()
    try:
        # 获取当前报价信息
        row = conn.execute(
            "SELECT status, batch_id, quote_quantity FROM quotes WHERE id=?",
            (quote_id,)
        ).fetchone()
        if not row:
            return False, "报价记录不存在"

        old_status = row[0]
        batch_id = row[1]
        quote_quantity = row[2] or 0

        # 校验状态流转合法性
        if new_status not in VALID_TRANSITIONS.get(old_status, []):
            return False, f"不允许从「{old_status}」变更为「{new_status}」"

        # 从"已出库"变为"已取消"：回补库存 + 清空报价SN
        if old_status == "已出库" and new_status == "已取消":
            conn.execute(
                "UPDATE batches SET remaining = remaining + ? WHERE id = ?",
                (quote_quantity, batch_id)
            )
            conn.execute(
                "UPDATE quotes SET sn_list = '' WHERE id = ?",
                (quote_id,)
            )

        conn.execute("UPDATE quotes SET status=? WHERE id=?", (new_status, quote_id))
        conn.commit()
        return True, "状态更新成功"
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def _add_payment_raw(conn, quote_id=None, customer_id=None, supplier_id=None,
                      pay_type="receivable", amount=0, pay_date="", method="", remark=""):
    """
    添加收付款记录的原始操作（不管理连接和事务）

    供批量收款/付款时在同一个事务中调用。
    外部调用方需自行管理 conn.commit() / conn.rollback() / conn.close()
    """
    conn.execute(
        "INSERT INTO payments (quote_id, customer_id, supplier_id, type, amount, pay_date, method, remark) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (quote_id, customer_id, supplier_id, pay_type, amount, pay_date, method, remark),
    )
    if quote_id and pay_type == "receivable":
        # 第一步：更新 received_amount
        conn.execute(
            "UPDATE quotes SET received_amount = received_amount + ? WHERE id=?",
            (amount, quote_id),
        )
        # 第二步：查询新值，基于新值更新 paid 和 status
        row = conn.execute(
            "SELECT received_amount, quote_price, quote_quantity, status FROM quotes WHERE id=?", (quote_id,)
        ).fetchone()
        if row:
            new_received = row[0]
            total = row[1] * row[2]
            paid = "是" if new_received >= total else "否"
            # 状态：收满则变为"已收款"，否则保持原状态（不自动回退）
            status = row[3]
            if new_received >= total:
                status = "已收款"
            conn.execute(
                "UPDATE quotes SET paid=?, status=? WHERE id=?",
                (paid, status, quote_id)
            )
    if pay_type == "payable" and supplier_id:
        conn.execute(
            "UPDATE suppliers SET balance = balance - ? WHERE id=?", (amount, supplier_id)
        )


def add_payment(quote_id=None, customer_id=None, supplier_id=None, pay_type="receivable",
                amount=0, pay_date="", method="", remark=""):
    """
    添加收付款记录（对外接口，自动管理连接和事务）
    """
    conn = get_connection()
    try:
        _add_payment_raw(conn, quote_id, customer_id, supplier_id, pay_type, amount, pay_date, method, remark)
        conn.commit()
        pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return pid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_payments(quote_id=None, customer_id=None, supplier_id=None):
    conn = get_connection()
    conditions = []
    params = []
    if quote_id:
        conditions.append("p.quote_id = ?")
        params.append(quote_id)
    if customer_id:
        conditions.append("p.customer_id = ?")
        params.append(customer_id)
    if supplier_id:
        conditions.append("p.supplier_id = ?")
        params.append(supplier_id)
    where = " AND ".join(conditions) if conditions else "1=1"
    sql = f"SELECT * FROM payments p WHERE {where} ORDER BY p.pay_date DESC, p.id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_customer_balance(customer_id=None):
    conn = get_connection()
    if customer_id:
        row = conn.execute(
            "SELECT COALESCE(SUM(q.quote_price * q.quote_quantity - q.received_amount), 0) "
            "FROM quotes q WHERE q.customer_id = ? AND q.status IN ('已报价','已出库')",
            (customer_id,),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT COALESCE(SUM(q.quote_price * q.quote_quantity - q.received_amount), 0) "
            "FROM quotes q WHERE q.status IN ('已报价','已出库')",
        ).fetchone()
    conn.close()
    return row[0] if row else 0


def get_supplier_payable(supplier_id=None):
    conn = get_connection()
    if supplier_id:
        row = conn.execute("SELECT COALESCE(balance, 0) FROM suppliers WHERE id=?", (supplier_id,)).fetchone()
    else:
        row = conn.execute("SELECT COALESCE(SUM(balance), 0) FROM suppliers").fetchone()
    conn.close()
    return row[0] if row else 0


def get_customer_statement(customer_id, date_from="", date_to=""):
    conn = get_connection()
    conditions = ["q.customer_id = ?"]
    params = [customer_id]
    if date_from:
        conditions.append("q.quote_date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("q.quote_date <= ?")
        params.append(date_to)
    where = " AND ".join(conditions)
    sql = f"""
        SELECT q.id, q.quote_date, q.quote_price, q.quote_quantity, q.status, q.paid, q.received_amount,
               p.series, p.cpu, p.ram, p.storage, p.gpu,
               b.purchase_price, b.remark as batch_remark, q.remark,
               s.name as supplier_name
        FROM quotes q
        JOIN batches b ON q.batch_id = b.id
        JOIN products p ON b.product_id = p.id
        LEFT JOIN suppliers s ON b.supplier_id = s.id
        WHERE {where}
        ORDER BY q.quote_date, q.id
    """
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_operation_log(operation, table_name, record_id, description=""):
    """记录操作日志"""
    conn = get_connection()
    conn.execute(
        "INSERT INTO operation_logs (operation, table_name, record_id, description) VALUES (?,?,?,?)",
        (operation, table_name, record_id, description),
    )
    conn.commit()
    conn.close()


def get_operation_logs(limit=100):
    """获取最近的操作日志"""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM operation_logs ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_customer_quotes(customer_id):
    """获取客户的所有报价记录（购买历史）"""
    conn = get_connection()
    sql = """
        SELECT q.id, q.quote_price, q.quote_quantity, q.quote_date, q.remark, q.paid,
               p.series, p.cpu, p.ram, p.storage, p.gpu, p.screen, p.note,
               b.purchase_price
        FROM quotes q
        JOIN batches b ON q.batch_id = b.id
        JOIN products p ON b.product_id = p.id
        WHERE q.customer_id = ?
        ORDER BY q.quote_date DESC, q.id DESC
    """
    rows = conn.execute(sql, (customer_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_customer_stats(customer_id):
    """获取客户统计信息"""
    conn = get_connection()
    row = conn.execute(
        """
        SELECT COUNT(*) as total_quotes, 
               COALESCE(SUM(q.quote_price * q.quote_quantity), 0) as total_amount,
               COALESCE(SUM((q.quote_price - b.purchase_price) * q.quote_quantity), 0) as total_profit
        FROM quotes q
        JOIN batches b ON q.batch_id = b.id
        WHERE q.customer_id = ? AND q.status != '已取消'
        """,
        (customer_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else {"total_quotes": 0, "total_amount": 0, "total_profit": 0}


# ---------- 收付款记录管理（修改/删除） ----------

def get_payment_by_id(payment_id):
    """获取单条收付款记录详情"""
    conn = get_connection()
    row = conn.execute(
        """
        SELECT p.id, p.quote_id, p.customer_id, p.supplier_id, p.type, p.amount,
               p.pay_date, p.method, p.remark, p.created_at,
               c.name as customer_name, s.name as supplier_name,
               q.quote_price, q.quote_quantity, q.received_amount
        FROM payments p
        LEFT JOIN customers c ON p.customer_id = c.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        LEFT JOIN quotes q ON p.quote_id = q.id
        WHERE p.id = ?
        """,
        (payment_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_payments_with_details(pay_type=None, customer_id=None, supplier_id=None, date_from=None, date_to=None):
    """获取所有收付款记录（带关联对象名称），支持筛选"""
    conn = get_connection()
    conditions = []
    params = []
    
    if pay_type and pay_type != "全部":
        conditions.append("p.type = ?")
        params.append(pay_type)
    if customer_id:
        conditions.append("p.customer_id = ?")
        params.append(customer_id)
    if supplier_id:
        conditions.append("p.supplier_id = ?")
        params.append(supplier_id)
    if date_from:
        conditions.append("p.pay_date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("p.pay_date <= ?")
        params.append(date_to)
    
    where = " AND ".join(conditions) if conditions else "1=1"
    sql = f"""
        SELECT p.id, p.quote_id, p.customer_id, p.supplier_id, p.type, p.amount,
               p.pay_date, p.method, p.remark, p.created_at,
               COALESCE(c.name, '') as customer_name,
               COALESCE(s.name, '') as supplier_name
        FROM payments p
        LEFT JOIN customers c ON p.customer_id = c.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE {where}
        ORDER BY p.pay_date DESC, p.id DESC
    """
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _update_quote_payment_status(conn, quote_id):
    """
    根据 quote 的 received_amount 重新计算 paid 和 status
    内部辅助函数，不管理连接和事务
    """
    row = conn.execute(
        "SELECT received_amount, quote_price, quote_quantity, status, sn_list FROM quotes WHERE id=?",
        (quote_id,),
    ).fetchone()
    if not row:
        return
    total_amount = row["quote_price"] * row["quote_quantity"]
    new_received = row["received_amount"]
    current_status = row["status"]
    sn_list = row["sn_list"] or ""

    # 计算 paid
    paid = "是" if new_received >= total_amount else "否"

    # 计算 status
    if new_received >= total_amount:
        new_status = "已收款"
    elif current_status == "已收款":
        # 从已收款回退，根据 sn_list 判断
        new_status = "已出库" if sn_list else "待确认"
    else:
        # 未收满且不是从已收款回退，保持当前状态不变
        new_status = current_status

    # paid 总是需要更新，status 只在变化时更新
    conn.execute(
        "UPDATE quotes SET paid=? WHERE id=?",
        (paid, quote_id),
    )
    if current_status != new_status:
        conn.execute(
            "UPDATE quotes SET status=? WHERE id=?",
            (new_status, quote_id),
        )


def update_payment(payment_id, new_amount, new_pay_date, new_method, new_remark):
    """修改收付款记录，同步更新关联数据"""
    conn = get_connection()
    try:
        # 获取原记录
        old_payment = conn.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()
        if not old_payment:
            conn.close()
            return False, "记录不存在"

        old_amount = old_payment["amount"]
        old_type = old_payment["type"]
        quote_id = old_payment["quote_id"]
        supplier_id = old_payment["supplier_id"]

        # 更新 payments 记录
        conn.execute(
            "UPDATE payments SET amount=?, pay_date=?, method=?, remark=? WHERE id=?",
            (new_amount, new_pay_date, new_method, new_remark, payment_id),
        )

        # 同步更新关联数据
        amount_diff = new_amount - old_amount

        if old_type == "receivable" and quote_id:
            # 更新 quotes 的 received_amount
            conn.execute(
                "UPDATE quotes SET received_amount = received_amount + ? WHERE id=?",
                (amount_diff, quote_id),
            )
            # 同步更新 paid 和 status
            _update_quote_payment_status(conn, quote_id)

        elif old_type == "payable" and supplier_id:
            # 更新 suppliers 的 balance
            conn.execute(
                "UPDATE suppliers SET balance = balance - ? WHERE id=?",
                (amount_diff, supplier_id),
            )

        conn.commit()
        return True, "修改成功"
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_payment(payment_id):
    """删除收付款记录，回滚关联数据"""
    conn = get_connection()
    try:
        # 获取原记录
        old_payment = conn.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()
        if not old_payment:
            conn.close()
            return False, "记录不存在", {}

        old_amount = old_payment["amount"]
        old_type = old_payment["type"]
        quote_id = old_payment["quote_id"]
        supplier_id = old_payment["supplier_id"]
        customer_id = old_payment["customer_id"]
        pay_date = old_payment["pay_date"]

        # 删除 payments 记录
        conn.execute("DELETE FROM payments WHERE id=?", (payment_id,))

        # 回滚关联数据
        affected = {"quote_id": quote_id, "supplier_id": supplier_id, "customer_id": customer_id}

        if old_type == "receivable" and quote_id:
            # 回滚 quotes 的 received_amount
            conn.execute(
                "UPDATE quotes SET received_amount = received_amount - ? WHERE id=?",
                (old_amount, quote_id),
            )
            # 同步更新 paid 和 status
            _update_quote_payment_status(conn, quote_id)

        elif old_type == "payable" and supplier_id:
            # 回滚 suppliers 的 balance（删除付款记录意味着欠款增加）
            conn.execute(
                "UPDATE suppliers SET balance = balance + ? WHERE id=?",
                (old_amount, supplier_id),
            )

        conn.commit()
        return True, "删除成功", affected
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()