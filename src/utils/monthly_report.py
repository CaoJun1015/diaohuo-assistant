"""
月度经营报告 (Monthly Business Report)

自动生成经营分析摘要：
- 销售额、毛利、毛利率
- 最赚钱机型 TOP5
- 滞销库存预警
- 回款率分析
- 环比变化
"""

from datetime import datetime, timedelta
from src.models.database import get_connection, calc_tax_adjusted_profit


def _calc_sales_profit(rows):
    """从查询结果集计算税后总销售额和总毛利"""
    total_revenue = 0
    total_profit = 0
    for r in rows:
        quote_price = r["quote_price"] or 0
        quote_quantity = r["quote_quantity"] or 1
        purchase_price = r["purchase_price"] or 0
        tax_rate = r["tax_rate"]
        purchase_tax_inclusive = r["purchase_tax_inclusive"] or 0
        quote_tax_inclusive = r["quote_tax_inclusive"] or 0
        total_revenue += quote_price * quote_quantity
        total_profit += calc_tax_adjusted_profit(
            purchase_price, quote_price, quote_quantity, tax_rate,
            purchase_tax_inclusive, quote_tax_inclusive,
        )
    return total_revenue, total_profit


def get_monthly_report(year=None, month=None):
    """
    生成指定月份的经营报告。

    参数:
        year: int — 年份，默认今年
        month: int — 月份，默认本月

    返回:
        dict — 包含所有经营指标
    """
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    date_from = f"{year:04d}-{month:02d}-01"
    if month == 12:
        date_to = f"{year + 1:04d}-01-01"
    else:
        date_to = f"{year:04d}-{month + 1:02d}-01"

    # 上月
    if month == 1:
        prev_from = f"{year - 1:04d}-12-01"
        prev_to = date_from
    else:
        prev_from = f"{year:04d}-{month - 1:02d}-01"
        prev_to = date_from

    conn = get_connection()

    # === 本月销售数据 ===
    sales_rows = conn.execute("""
        SELECT 
            q.quote_price, q.quote_quantity, b.purchase_price,
            q.tax_rate, q.purchase_tax_inclusive, q.quote_tax_inclusive,
            q.received_amount
        FROM quotes q
        JOIN batches b ON q.batch_id = b.id
        WHERE q.quote_date >= ? AND q.quote_date < ?
        AND q.status IN ('已报价', '已出库', '已收款')
    """, (date_from, date_to)).fetchall()
    total_revenue, total_profit = _calc_sales_profit(sales_rows)
    total_received = sum(r["received_amount"] or 0 for r in sales_rows)
    order_count = len(sales_rows)

    # === 上月销售数据（环比） ===
    prev_rows = conn.execute("""
        SELECT 
            q.quote_price, q.quote_quantity, b.purchase_price,
            q.tax_rate, q.purchase_tax_inclusive, q.quote_tax_inclusive
        FROM quotes q
        JOIN batches b ON q.batch_id = b.id
        WHERE q.quote_date >= ? AND q.quote_date < ?
        AND q.status IN ('已报价', '已出库', '已收款')
    """, (prev_from, prev_to)).fetchall()
    prev_revenue, prev_profit = _calc_sales_profit(prev_rows)

    # === 最赚钱机型 TOP5 ===
    top_products = conn.execute("""
        SELECT 
            p.series, p.cpu, p.ram, p.storage,
            COUNT(*) as sale_count,
            SUM(q.quote_price * q.quote_quantity) as revenue,
            q.quote_price, q.quote_quantity, b.purchase_price,
            q.tax_rate, q.purchase_tax_inclusive, q.quote_tax_inclusive
        FROM quotes q
        JOIN batches b ON q.batch_id = b.id
        JOIN products p ON b.product_id = p.id
        WHERE q.quote_date >= ? AND q.quote_date < ?
        AND q.status IN ('已报价', '已出库', '已收款')
        GROUP BY p.series, p.cpu, p.ram, p.storage,
                 q.quote_price, q.quote_quantity, b.purchase_price,
                 q.tax_rate, q.purchase_tax_inclusive, q.quote_tax_inclusive
        ORDER BY revenue DESC
        LIMIT 5
    """, (date_from, date_to)).fetchall()

    # === 滞销库存预警（有库存但本月无销售） ===
    slow_movers = conn.execute("""
        SELECT 
            p.series, p.cpu, p.ram, p.storage,
            SUM(b.remaining) as stock,
            MIN(b.date) as oldest_batch_date,
            COALESCE(SUM(b.remaining * b.purchase_price), 0) as tied_capital
        FROM batches b
        JOIN products p ON b.product_id = p.id
        WHERE b.remaining > 0
        AND p.id NOT IN (
            SELECT DISTINCT b2.product_id 
            FROM quotes q2 
            JOIN batches b2 ON q2.batch_id = b2.id 
            WHERE q2.quote_date >= ? AND q2.quote_date < ?
        )
        GROUP BY p.series, p.cpu, p.ram, p.storage
        HAVING stock > 0
        ORDER BY tied_capital DESC
        LIMIT 5
    """, (date_from, date_to)).fetchall()

    # === 回款率 ===
    total_revenue = total_revenue or 0
    total_received = total_received or 0
    collection_rate = (total_received / total_revenue * 100) if total_revenue > 0 else 0

    # === 环比计算 ===
    prev_revenue = prev_revenue or 0
    prev_profit = prev_profit or 0
    revenue_change = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
    profit_change = ((total_profit - prev_profit) / prev_profit * 100) if prev_profit > 0 else 0

    # 合并 TOP5 同类机型（按 series+cpu 聚合）
    from collections import defaultdict
    top_agg = defaultdict(lambda: {"sale_count": 0, "revenue": 0, "profit": 0})
    for r in top_products:
        key = (r["series"], r["cpu"] or "")
        top_agg[key]["series"] = r["series"]
        top_agg[key]["cpu"] = r["cpu"]
        top_agg[key]["sale_count"] += r["sale_count"]
        top_agg[key]["revenue"] += r["revenue"] or 0
        qp = r["quote_price"] or 0
        qq = r["quote_quantity"] or 1
        pp = r["purchase_price"] or 0
        tr = r["tax_rate"]
        pi = r["purchase_tax_inclusive"] or 0
        qi = r["quote_tax_inclusive"] or 0
        top_agg[key]["profit"] += calc_tax_adjusted_profit(pp, qp, qq, tr, pi, qi)
    sorted_top = sorted(top_agg.values(), key=lambda x: x["profit"], reverse=True)[:5]

    conn.close()

    return {
        "year": year,
        "month": month,
        "period": f"{year}年{month}月",
        "order_count": order_count,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_received": total_received,
        "collection_rate": collection_rate,
        "profit_margin": (total_profit / total_revenue * 100) if total_revenue > 0 else 0,
        "revenue_change": revenue_change,
        "profit_change": profit_change,
        "top_products": sorted_top,
        "slow_movers": [dict(r) for r in slow_movers],
    }


def format_report_text(report):
    """格式化报告文本。"""
    parts = []
    p = report

    parts.append(f"📊 {p['period']} 经营摘要")
    parts.append("=" * 30)
    parts.append("")

    # 核心指标
    parts.append(f"📦 成交订单: {p['order_count']} 单")
    parts.append(f"💰 总销售额: ¥{p['total_revenue']:,.0f}")
    parts.append(f"📈 总毛利: ¥{p['total_profit']:,.0f}")
    parts.append(f"📊 毛利率: {p['profit_margin']:.1f}%")
    parts.append(f"💵 已收款: ¥{p['total_received']:,.0f}")
    parts.append(f"📋 回款率: {p['collection_rate']:.1f}%")
    parts.append("")

    # 环比
    rev_arrow = "↑" if p["revenue_change"] >= 0 else "↓"
    prof_arrow = "↑" if p["profit_change"] >= 0 else "↓"
    parts.append(f"📉 环比: 销售额 {rev_arrow}{abs(p['revenue_change']):.1f}%  |  毛利 {prof_arrow}{abs(p['profit_change']):.1f}%")
    parts.append("")

    # TOP5 机型
    if p["top_products"]:
        parts.append("🏆 最赚钱机型 TOP5:")
        for i, item in enumerate(p["top_products"], 1):
            name = item["series"]
            if item.get("cpu"):
                name += f" {item['cpu']}"
            parts.append(f"  {i}. {name} | 卖{item['sale_count']}台 | 毛利 ¥{item['profit']:,.0f}")
        parts.append("")

    # 滞销预警
    if p["slow_movers"]:
        parts.append("⚠️ 滞销库存预警:")
        for item in p["slow_movers"]:
            name = item["series"]
            if item.get("cpu"):
                name += f" {item['cpu']}"
            parts.append(f"  • {name} | 库存{item['stock']}台 | 占资金 ¥{item['tied_capital']:,.0f} | 最早入库 {item['oldest_batch_date']}")
        parts.append("")
        parts.append("建议: 考虑降价促销或联系上游调货")

    return "\n".join(parts)
