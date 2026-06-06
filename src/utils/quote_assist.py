"""
报价决策助手 (Quote Decision Assistant)

基于历史报价数据，为新报价提供决策参考：
- 查询同一机型的历史报价区间
- 查询同一客户的历史成交价
- 计算建议报价范围
"""

from src.models.database import get_connection


def get_quote_history(series="", cpu="", ram="", storage="", gpu=""):
    """
    查询指定机型的历史报价记录。

    参数:
        series, cpu, ram, storage, gpu: str — 机型特征（至少提供 series）

    返回:
        dict {
            total_quotes: int,
            min_price: float,
            max_price: float,
            avg_price: float,
            recent_quotes: list[dict],  # 最近 5 条
        }
    """
    conn = get_connection()
    conditions = []
    params = []

    if series:
        conditions.append("p.series LIKE ?")
        params.append(f"%{series}%")
    if cpu:
        conditions.append("p.cpu LIKE ?")
        params.append(f"%{cpu}%")
    if ram:
        conditions.append("p.ram LIKE ?")
        params.append(f"%{ram}%")
    if storage:
        conditions.append("p.storage LIKE ?")
        params.append(f"%{storage}%")
    if gpu:
        conditions.append("p.gpu LIKE ?")
        params.append(f"%{gpu}%")

    if not conditions:
        conn.close()
        return None

    where = " AND ".join(conditions)

    # 统计
    stats = conn.execute(f"""
        SELECT 
            COUNT(*) as total,
            MIN(q.quote_price) as min_price,
            MAX(q.quote_price) as max_price,
            AVG(q.quote_price) as avg_price,
            MIN(b.purchase_price) as min_cost,
            AVG(b.purchase_price) as avg_cost
        FROM quotes q
        JOIN batches b ON q.batch_id = b.id
        JOIN products p ON b.product_id = p.id
        WHERE {where}
        AND q.status IN ('已报价', '已出库', '已收款')
    """, params).fetchone()

    if not stats or stats["total"] == 0:
        conn.close()
        return None

    # 最近 5 条
    recent = conn.execute(f"""
        SELECT q.quote_price, q.quote_quantity, q.quote_date, q.status,
               b.purchase_price,
               c.name as customer_name
        FROM quotes q
        JOIN batches b ON q.batch_id = b.id
        JOIN products p ON b.product_id = p.id
        LEFT JOIN customers c ON q.customer_id = c.id
        WHERE {where}
        ORDER BY q.quote_date DESC, q.id DESC
        LIMIT 5
    """, params).fetchall()

    conn.close()

    return {
        "total_quotes": stats["total"],
        "min_price": stats["min_price"],
        "max_price": stats["max_price"],
        "avg_price": stats["avg_price"],
        "min_cost": stats["min_cost"],
        "avg_cost": stats["avg_cost"],
        "recent_quotes": [dict(r) for r in recent],
    }


def get_customer_price_history(customer_name, series=""):
    """
    查询指定客户的历史成交价。

    参数:
        customer_name: str — 客户名称
        series: str — 限定机型（可选）

    返回:
        list[dict] — 该客户的报价历史
    """
    conn = get_connection()
    conditions = ["c.name LIKE ?"]
    params = [f"%{customer_name}%"]

    if series:
        conditions.append("p.series LIKE ?")
        params.append(f"%{series}%")

    where = " AND ".join(conditions)

    rows = conn.execute(f"""
        SELECT q.quote_price, q.quote_quantity, q.quote_date, q.status,
               p.series, p.cpu, p.ram, p.storage
        FROM quotes q
        JOIN batches b ON q.batch_id = b.id
        JOIN products p ON b.product_id = p.id
        LEFT JOIN customers c ON q.customer_id = c.id
        WHERE {where}
        ORDER BY q.quote_date DESC
        LIMIT 10
    """, params).fetchall()

    conn.close()
    return [dict(r) for r in rows]


def suggest_price(series, cpu="", ram="", storage="", gpu="", purchase_price=0, customer_name=""):
    """
    综合分析后给出建议报价。

    参数:
        series, cpu, ram, storage, gpu: str — 机型特征
        purchase_price: float — 本次进货价（用于计算利润率）
        customer_name: str — 客户名称（用于参考历史成交价）

    返回:
        dict {
            suggested_min: float,
            suggested_max: float,
            suggested_mid: float,
            margin_at_mid: float,       # 中间价的利润率
            confidence: str,            # high / medium / low
            basis: str,                 # 建议依据说明
            history: dict,              # 机型历史数据
            customer_history: list,     # 客户历史数据
        }
    """
    history = get_quote_history(series, cpu, ram, storage, gpu)
    customer_hist = []
    if customer_name:
        customer_hist = get_customer_price_history(customer_name, series)

    # 无历史数据时，用进货价 + 默认加价率
    if not history or history["total_quotes"] == 0:
        if purchase_price > 0:
            suggested = purchase_price * 1.06  # 默认加 6%
            return {
                "suggested_min": round(purchase_price * 1.03),
                "suggested_max": round(purchase_price * 1.10),
                "suggested_mid": round(suggested),
                "margin_at_mid": 6.0,
                "confidence": "low",
                "basis": "无历史报价数据，基于进货价默认加价 3-10%",
                "history": None,
                "customer_history": customer_hist,
            }
        return {
            "suggested_min": 0,
            "suggested_max": 0,
            "suggested_mid": 0,
            "margin_at_mid": 0,
            "confidence": "low",
            "basis": "无历史数据且未提供进货价，无法建议",
            "history": None,
            "customer_history": customer_hist,
        }

    # 有历史数据
    hist_min = history["min_price"]
    hist_max = history["max_price"]
    hist_avg = history["avg_price"]

    # 如果提供了进货价，计算利润率
    margin = 0
    if purchase_price > 0 and hist_avg > 0:
        margin = (hist_avg - purchase_price) / purchase_price * 100

    # 建议范围：历史均价 ± 5%
    suggested_mid = round(hist_avg)
    suggested_min = round(hist_avg * 0.95)
    suggested_max = round(hist_avg * 1.05)

    # 如果有客户历史，参考该客户的成交价
    if customer_hist:
        customer_avg = sum(q["quote_price"] for q in customer_hist) / len(customer_hist)
        # 客户历史和机型历史各占 50% 权重
        suggested_mid = round((hist_avg + customer_avg) / 2)
        suggested_min = round(min(suggested_min, customer_avg * 0.95))
        suggested_max = round(max(suggested_max, customer_avg * 1.05))

    confidence = "high" if history["total_quotes"] >= 5 else "medium"

    basis_parts = [f"基于 {history['total_quotes']} 条历史报价"]
    basis_parts.append(f"历史区间 ¥{hist_min:.0f}-¥{hist_max:.0f}")
    if customer_hist:
        basis_parts.append(f"该客户历史 {len(customer_hist)} 次成交")
    basis = "，".join(basis_parts)

    return {
        "suggested_min": suggested_min,
        "suggested_max": suggested_max,
        "suggested_mid": suggested_mid,
        "margin_at_mid": margin,
        "confidence": confidence,
        "basis": basis,
        "history": history,
        "customer_history": customer_hist,
    }
