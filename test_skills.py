"""测试6个skill模块"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.database import init_db, add_product, add_customer, add_supplier, add_batch, add_quote, get_connection
import src.models.database as db

# Use temp DB
test_db = 'data/test_skills.db'
os.makedirs('data', exist_ok=True)
db.DB_PATH = test_db
if os.path.exists(test_db):
    os.remove(test_db)
init_db()

# Setup test data
pid = add_product('Y7000P', 'i7-13700H', '16G', '512G', 'RTX4060', '16', '')
pid2 = add_product('小新Pro16', 'i5-13500H', '16G', '1T', 'RTX3050', '16', '')
sid = add_supplier('联想总代')
bid = add_batch(pid, 6500, 10, 8, '2026-05-20', '含税', sid, 'SN001,SN002')
bid2 = add_batch(pid2, 4500, 5, 3, '2026-05-22', '', sid, '')
cid = add_customer('张三')
cid2 = add_customer('李四')
add_quote(bid, cid, 7200, 2, '2026-05-22', '', '否', '已报价', 0, 'SN010,SN011')
add_quote(bid, cid2, 7300, 1, '2026-05-23', '', '否', '已出库', 0, 'SN012')
add_quote(bid2, cid, 5000, 1, '2026-05-25', '', '否', '待确认', 0, '')

print('=== Test data setup OK ===')

# ========== Test 1: follow_up ==========
print('\n=== Test 1: follow_up ===')
from src.utils.follow_up import get_stale_quotes, format_reminder_text
result = get_stale_quotes(stale_days=1)
print(f'  pending_confirm: {len(result["pending_confirm"])}')
print(f'  quoted_no_ship: {len(result["quoted_no_ship"])}')
print(f'  shipped_no_pay: {len(result["shipped_no_pay"])}')
print(f'  total: {result["total"]}')
text = format_reminder_text(result)
assert len(text) > 0
print('  PASS')

# ========== Test 2: monthly_report ==========
print('\n=== Test 2: monthly_report ===')
from src.utils.monthly_report import get_monthly_report, format_report_text
report = get_monthly_report(2026, 5)
print(f'  period: {report["period"]}')
print(f'  order_count: {report["order_count"]}')
print(f'  total_revenue: {report["total_revenue"]}')
print(f'  total_profit: {report["total_profit"]}')
print(f'  top_products: {len(report["top_products"])}')
print(f'  slow_movers: {len(report["slow_movers"])}')
text = format_report_text(report)
assert len(text) > 0
print('  PASS')

# ========== Test 3: quote_assist ==========
print('\n=== Test 3: quote_assist ===')
from src.utils.quote_assist import get_quote_history, suggest_price, get_customer_price_history
hist = get_quote_history(series='Y7000P')
print(f'  total_quotes: {hist["total_quotes"]}')
print(f'  min_price: {hist["min_price"]}')
print(f'  max_price: {hist["max_price"]}')
print(f'  avg_price: {hist["avg_price"]:.0f}')
suggestion = suggest_price('Y7000P', purchase_price=6500, customer_name='张三')
print(f'  suggested_mid: {suggestion["suggested_mid"]}')
print(f'  confidence: {suggestion["confidence"]}')
print(f'  basis: {suggestion["basis"]}'.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))
cust_hist = get_customer_price_history('张三')
print(f'  customer_history: {len(cust_hist)} records')
print('  PASS')

# ========== Test 4: shipment_flow ==========
print('\n=== Test 4: shipment_flow ===')
from src.utils.shipment_flow import parse_sn_input, validate_sn, validate_sn_list, check_sn_duplicates, generate_shipment_receipt
sn_list = parse_sn_input('SN001,SN002\nSN003 SN004,SN001')
print(f'  parse_sn_input: {sn_list}')
assert sn_list == ['SN001', 'SN002', 'SN003', 'SN004']
ok, msg = validate_sn('ABC123')
assert ok
print(f'  validate_sn OK: {ok}')
ok2, msg2 = validate_sn('AB')
assert not ok2
print(f'  validate_sn short: {ok2}, {msg2}')
result = validate_sn_list(['SN001', 'AB', 'SN002'], expected_count=2)
print(f'  valid={len(result["valid"])}, invalid={len(result["invalid"])}, count_ok={result["count_ok"]}')
dup_result = check_sn_duplicates(['SN001', 'SN005'], 'SN001,SN002,SN003')
print(f'  dup={dup_result["duplicates"]}, new={dup_result["new_unique"]}')
receipt = generate_shipment_receipt({'series': 'Y7000P', 'cpu': 'i7', 'customer_name': '张三', 'quote_price': 7200, 'quote_quantity': 2}, ['SN010', 'SN011'])
assert len(receipt) > 0
print('  PASS')

# ========== Test 5: remote_diagnose ==========
print('\n=== Test 5: remote_diagnose ===')
from src.utils.remote_diagnose import search_diagnose, get_diagnose_tree, get_all_diagnose_keys, generate_diagnose_report
keys = get_all_diagnose_keys()
print(f'  keys: {[k["key"] for k in keys]}')
result = search_diagnose('蓝屏')
assert len(result) > 0
print(f'  search results: {len(result)}')
tree = get_diagnose_tree('蓝屏')
assert tree is not None
report = generate_diagnose_report('蓝屏', ['有错误代码'], '客户说是IRQL错误')
assert len(report) > 0
print('  PASS')

# ========== Test 6: price_diff ==========
print('\n=== Test 6: price_diff ===')
from src.utils.price_diff import save_snapshot, get_latest_snapshot, diff_snapshots, get_all_snapshots
# Need to create price_snapshots table
conn = get_connection()
conn.execute("""CREATE TABLE IF NOT EXISTS price_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_date TEXT NOT NULL,
    item_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
conn.execute("""CREATE TABLE IF NOT EXISTS price_snapshot_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    series TEXT, cpu TEXT, ram TEXT, storage TEXT, gpu TEXT, note TEXT,
    norm_key TEXT,
    FOREIGN KEY (snapshot_id) REFERENCES price_snapshots(id)
)""")
conn.commit()
conn.close()

products = [
    {'series': 'Y7000P', 'cpu': 'i7-13700H', 'ram': '16G', 'storage': '512G', 'gpu': 'RTX4060', 'note': ''},
    {'series': '小新Pro16', 'cpu': 'i5-13500H', 'ram': '16G', 'storage': '1T', 'gpu': 'RTX3050', 'note': ''},
]
sid, count = save_snapshot(products, '2026-05-20')
print(f'  save_snapshot: id={sid}, count={count}')
snapshot = get_latest_snapshot()
assert snapshot is not None
print(f'  get_latest: id={snapshot["snapshot_id"]}, date={snapshot["import_date"]}, items={len(snapshot["items"])}')

new_products = [
    {'series': 'Y7000P', 'cpu': 'i7-13700H', 'ram': '16G', 'storage': '512G', 'gpu': 'RTX4060', 'note': ''},
    {'series': 'ThinkPad X1', 'cpu': 'i7-1365U', 'ram': '16G', 'storage': '512G', 'gpu': '', 'note': '新增'},
]
diff = diff_snapshots(snapshot, new_products)
print(f'  diff: added={len(diff["added"])}, removed={len(diff["removed"])}, unchanged={diff["unchanged"]}')
print(f'  summary: {diff["summary"]}')
all_snaps = get_all_snapshots()
print(f'  all_snapshots: {len(all_snaps)}')
print('  PASS')

# Cleanup
if os.path.exists(test_db):
    os.remove(test_db)

print('\n' + '=' * 40)
print('  ALL 6 SKILL TESTS PASSED!')
print('=' * 40)
