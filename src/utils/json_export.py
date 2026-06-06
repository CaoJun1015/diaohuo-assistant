"""
JSON 数据导入导出模块：用于全量数据备份和迁移
"""

import json
import os
from datetime import datetime


def export_all_to_json(db_module, output_path=None):
    """
    导出所有数据为 JSON 格式
    
    db_module: 数据库模块，包含各种获取数据的函数
    output_path: 输出路径，默认桌面
    """
    if not output_path:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(desktop, f"调货助手备份_{timestamp}.json")
    
    data = {
        "version": "v1.04",
        "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": {
            "products": db_module.get_all_products(),
            "suppliers": _get_all_suppliers(db_module),
            "batches": _get_all_batches(db_module),
            "customers": db_module.get_all_customers(),
            "quotes": _get_all_quotes(db_module),
            "payments": _get_all_payments(db_module),
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_path


def _get_all_suppliers(db_module):
    """获取所有上游数据"""
    from src.models.database import get_connection
    conn = get_connection()
    rows = conn.execute("SELECT * FROM suppliers ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _get_all_batches(db_module):
    """获取所有批次数据"""
    from src.models.database import get_connection
    conn = get_connection()
    rows = conn.execute(
        "SELECT b.*, p.series FROM batches b JOIN products p ON b.product_id = p.id ORDER BY b.id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _get_all_quotes(db_module):
    """获取所有报价记录"""
    from src.models.database import get_connection
    conn = get_connection()
    sql = """
        SELECT q.*, p.series, p.cpu, p.ram, p.storage, p.gpu, p.screen,
               b.purchase_price, c.name as customer_name
        FROM quotes q
        JOIN batches b ON q.batch_id = b.id
        JOIN products p ON b.product_id = p.id
        LEFT JOIN customers c ON q.customer_id = c.id
        ORDER BY q.id
    """
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _get_all_payments(db_module):
    """获取所有收付款记录"""
    from src.models.database import get_connection
    conn = get_connection()
    rows = conn.execute("SELECT * FROM payments ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def import_from_json(json_path, db_module):
    """
    从 JSON 文件导入数据
    
    返回: (success: bool, message: str, stats: dict)
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "version" not in data or "data" not in data:
            return False, "无效的备份文件格式", {}
        
        stats = {
            "products": 0,
            "suppliers": 0,
            "batches": 0,
            "customers": 0,
            "quotes": 0,
            "payments": 0,
        }
        
        imported_products = {}
        
        for product in data["data"].get("products", []):
            pid = _import_product(product, db_module)
            imported_products[product["id"]] = pid
            stats["products"] += 1
        
        imported_suppliers = {}
        for supplier in data["data"].get("suppliers", []):
            sid = _import_supplier(supplier, db_module)
            imported_suppliers[supplier["id"]] = sid
            stats["suppliers"] += 1
        
        imported_batches = {}
        for batch in data["data"].get("batches", []):
            old_product_id = batch.get("product_id") or batch.get("id")
            new_product_id = imported_products.get(old_product_id)
            if new_product_id:
                old_supplier_id = batch.get("supplier_id")
                new_supplier_id = imported_suppliers.get(old_supplier_id) if old_supplier_id else None
                bid = _import_batch(batch, new_product_id, new_supplier_id, db_module)
                imported_batches[batch["id"]] = bid
                stats["batches"] += 1
        
        imported_customers = {}
        for customer in data["data"].get("customers", []):
            cid = _import_customer(customer, db_module)
            imported_customers[customer["id"]] = cid
            stats["customers"] += 1
        
        imported_quotes = {}
        for quote in data["data"].get("quotes", []):
            old_batch_id = quote.get("batch_id")
            old_customer_id = quote.get("customer_id")
            new_batch_id = imported_batches.get(old_batch_id)
            new_customer_id = imported_customers.get(old_customer_id)
            if new_batch_id:
                qid = _import_quote(quote, new_batch_id, new_customer_id, db_module)
                if qid:
                    imported_quotes[quote["id"]] = qid
                    stats["quotes"] += 1
        
        for payment in data["data"].get("payments", []):
            old_quote_id = payment.get("quote_id")
            old_customer_id = payment.get("customer_id")
            old_supplier_id = payment.get("supplier_id")
            new_quote_id = imported_quotes.get(old_quote_id)
            new_customer_id = imported_customers.get(old_customer_id)
            new_supplier_id = imported_suppliers.get(old_supplier_id)
            _import_payment(payment, new_quote_id, new_customer_id, new_supplier_id, db_module)
            stats["payments"] += 1
        
        return True, "导入成功", stats
    
    except FileNotFoundError:
        return False, "文件不存在", {}
    except json.JSONDecodeError:
        return False, "文件格式错误，不是有效的JSON文件", {}
    except Exception as e:
        return False, f"导入失败: {str(e)}", {}


def _import_product(product, db_module):
    """导入机型"""
    try:
        pid = db_module.add_product(
            series=product.get("series", ""),
            cpu=product.get("cpu", ""),
            ram=product.get("ram", ""),
            storage=product.get("storage", ""),
            gpu=product.get("gpu", ""),
            screen=product.get("screen", ""),
            note=product.get("note", ""),
        )
        return pid
    except:
        return None


def _import_supplier(supplier, db_module):
    """导入上游"""
    try:
        sid = db_module.add_supplier(
            name=supplier.get("name", ""),
            wechat=supplier.get("wechat", ""),
            qq=supplier.get("qq", ""),
            phone=supplier.get("phone", ""),
            note=supplier.get("note", ""),
        )
        return sid
    except:
        return None


def _import_batch(batch, product_id, supplier_id, db_module):
    """导入批次"""
    try:
        bid = db_module.add_batch(
            product_id=product_id,
            purchase_price=batch.get("purchase_price", 0),
            quantity=batch.get("quantity", 0),
            remaining=batch.get("remaining", 0),
            date_str=batch.get("date", ""),
            remark=batch.get("remark", ""),
            supplier_id=supplier_id,
            sn_list=batch.get("sn_list", ""),
        )
        return bid
    except:
        return None


def _import_customer(customer, db_module):
    """导入客户"""
    try:
        cid = db_module.add_customer(
            name=customer.get("name", ""),
            wechat=customer.get("wechat", ""),
            qq=customer.get("qq", ""),
            phone=customer.get("phone", ""),
            note=customer.get("note", ""),
        )
        return cid
    except:
        return None


def _import_quote(quote, batch_id, customer_id, db_module):
    """导入报价"""
    try:
        qid = db_module.add_quote(
            batch_id=batch_id,
            customer_id=customer_id,
            quote_price=quote.get("quote_price", 0),
            quote_quantity=quote.get("quote_quantity", 1),
            quote_date=quote.get("quote_date", ""),
            remark=quote.get("remark", ""),
            paid=quote.get("paid", ""),
            status=quote.get("status", "待确认"),
            received_amount=quote.get("received_amount", 0),
        )
        return qid
    except:
        return None


def _import_payment(payment, quote_id, customer_id, supplier_id, db_module):
    """导入收付款记录"""
    try:
        db_module.add_payment(
            quote_id=quote_id,
            customer_id=customer_id,
            supplier_id=supplier_id,
            pay_type=payment.get("type", "receivable"),
            amount=payment.get("amount", 0),
            pay_date=payment.get("pay_date", ""),
            method=payment.get("method", ""),
            remark=payment.get("remark", ""),
        )
    except:
        pass


def validate_json_file(json_path):
    """验证 JSON 文件格式"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "version" not in data or "data" not in data:
            return False, "无效的备份文件格式"
        
        stats = {
            "products": len(data["data"].get("products", [])),
            "suppliers": len(data["data"].get("suppliers", [])),
            "batches": len(data["data"].get("batches", [])),
            "customers": len(data["data"].get("customers", [])),
            "quotes": len(data["data"].get("quotes", [])),
            "payments": len(data["data"].get("payments", [])),
        }
        
        return True, "有效的备份文件", stats
    
    except FileNotFoundError:
        return False, "文件不存在", {}
    except json.JSONDecodeError:
        return False, "文件格式错误", {}
    except Exception as e:
        return False, f"验证失败: {str(e)}", {}