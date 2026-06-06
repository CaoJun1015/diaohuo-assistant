"""
价格异动哨兵 (Price Change Sentinel)

对比两次价格表快照，识别：
- 🔴 涨价：上游成本上升，需检查报价是否覆盖
- 🟢 降价：利润空间变化或需尽快出货
- 🔵 新增：上游新上架的机型
- ⚠️ 下架：上游不再供货，检查库存
"""

import sqlite3
from datetime import datetime
from src.models.database import get_connection


def _normalize_key(series, cpu, ram, storage, gpu):
    """
    生成机型的规范化匹配 key。
    不同批次的价格表描述可能略有差异，用这个 key 做模糊匹配。
    """
    parts = []
    for val in [series, cpu, ram, storage, gpu]:
        if val:
            # 统一大小写，去除空格和标点差异
            cleaned = val.strip().upper().replace(" ", "").replace("-", "").replace("_", "")
            parts.append(cleaned)
    return "|".join(parts)


def save_snapshot(products, import_date=None):
    """
    保存一次价格表快照。

    参数:
        products: list[dict] — parse_word_pricelist() 的返回结果
                  每项需含 series, cpu, ram, storage, gpu, note
        import_date: str — 快照日期，默认今天

    返回:
        (snapshot_id, item_count)
    """
    if import_date is None:
        import_date = datetime.now().strftime("%Y-%m-%d")

    conn = get_connection()
    cursor = conn.cursor()

    # 创建快照头
    cursor.execute(
        "INSERT INTO price_snapshots (import_date, item_count) VALUES (?, ?)",
        (import_date, len(products),
    ))
    snapshot_id = cursor.lastrowid

    # 保存每条记录
    for p in products:
        series = p.get("series", "")
        cpu = p.get("cpu", "")
        ram = p.get("ram", "")
        storage = p.get("storage", "")
        gpu = p.get("gpu", "")
        note = p.get("note", "")
        norm_key = _normalize_key(series, cpu, ram, storage, gpu)

        cursor.execute(
            """INSERT INTO price_snapshot_items
               (snapshot_id, series, cpu, ram, storage, gpu, note, norm_key)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (snapshot_id, series, cpu, ram, storage, gpu, note, norm_key),
        )

    conn.commit()
    conn.close()
    return snapshot_id, len(products)


def get_latest_snapshot(before_date=None):
    """
    获取最近一次快照（不含 before_date 当天，用于对比上一版本）。

    返回:
        dict {snapshot_id, import_date, item_count, items: list[dict]}
        或 None
    """
    conn = get_connection()
    if before_date:
        row = conn.execute(
            "SELECT id, import_date, item_count FROM price_snapshots WHERE import_date < ? ORDER BY import_date DESC, id DESC LIMIT 1",
            (before_date,),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id, import_date, item_count FROM price_snapshots ORDER BY import_date DESC, id DESC LIMIT 1"
        ).fetchone()

    if not row:
        conn.close()
        return None

    snapshot = {"snapshot_id": row[0], "import_date": row[1], "item_count": row[2]}

    items = conn.execute(
        "SELECT id, series, cpu, ram, storage, gpu, note, norm_key FROM price_snapshot_items WHERE snapshot_id=?",
        (snapshot["snapshot_id"],),
    ).fetchall()
    conn.close()

    snapshot["items"] = [dict(i) for i in items]
    return snapshot


def get_all_snapshots():
    """获取所有快照列表（不含明细）。"""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, import_date, item_count, created_at FROM price_snapshots ORDER BY import_date DESC, id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def diff_snapshots(old_snapshot, new_items):
    """
    对比两次快照，返回异动报告。

    参数:
        old_snapshot: dict — get_latest_snapshot() 的返回值
        new_items: list[dict] — 新一批 parse_word_pricelist() 的结果

    返回:
        dict {
            old_date: str,
            new_date: str,
            increased: list,   # 涨价项（当前版本仅记录存在性变动，价格字段来自后续批次）
            decreased: list,   # 降价项
            added: list,       # 新增项
            removed: list,     # 下架项
            unchanged: int,    # 未变动数量
            summary: str,      # 文字摘要
        }
    """
    old_items = old_snapshot.get("items", []) if old_snapshot else []
    old_date = old_snapshot.get("import_date", "未知") if old_snapshot else "无"

    # 构建旧快照的 norm_key → item 映射
    old_map = {}
    for item in old_items:
        key = item.get("norm_key", "")
        if key:
            old_map[key] = item

    # 构建新快照的 norm_key → item 映射
    new_map = {}
    for item in new_items:
        norm_key = _normalize_key(
            item.get("series", ""),
            item.get("cpu", ""),
            item.get("ram", ""),
            item.get("storage", ""),
            item.get("gpu", ""),
        )
        item["_norm_key"] = norm_key
        if norm_key:
            new_map[norm_key] = item

    added = []
    removed = []
    unchanged = 0

    # 找新增
    for key, item in new_map.items():
        if key not in old_map:
            added.append(item)
        else:
            unchanged += 1

    # 找下架
    for key, item in old_map.items():
        if key not in new_map:
            removed.append(item)

    new_date = datetime.now().strftime("%Y-%m-%d")

    # 构建摘要
    parts = []
    if added:
        parts.append(f"新增 {len(added)} 项")
    if removed:
        parts.append(f"下架 {len(removed)} 项")
    if unchanged > 0:
        parts.append(f"未变动 {unchanged} 项")
    summary = "、".join(parts) if parts else "无变化"

    return {
        "old_date": old_date,
        "new_date": new_date,
        "increased": [],  # 价格变动需要历史价格数据，当前版本先不做
        "decreased": [],
        "added": added,
        "removed": removed,
        "unchanged": unchanged,
        "summary": summary,
    }
