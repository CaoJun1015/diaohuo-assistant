"""测试SN fallback逻辑"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.database import init_db, add_product, add_customer, add_supplier, add_batch, add_quote, search_quotes, get_quote_by_id, update_quote
import src.models.database as db

test_db = 'data/test_sn_fallback.db'
os.makedirs('data', exist_ok=True)
db.DB_PATH = test_db
if os.path.exists(test_db):
    os.remove(test_db)
init_db()

# 场景1: 新增批次时有SN，创建报价时不传SN
pid = add_product('Y7000P', 'i7', '16G', '512G', 'RTX4060', '16', '')
sid = add_supplier('Test')
bid = add_batch(pid, 6500, 10, 10, '2026-05-30', '', sid, 'SN001,SN002')
cid = add_customer('Test')
add_quote(bid, cid, 7200, 2, '2026-05-30', '', '否', '待确认', 0, '')

# search_quotes 应返回 batch_sn_list 作为 fallback
quotes = search_quotes()
q = quotes[0]
q_sn = q.get("sn_list", "")
q_bsn = q.get("batch_sn_list", "")
print(f"quotes.sn_list = '{q_sn}'")
print(f"batch_sn_list = '{q_bsn}'")
sn_display = q_sn or q_bsn or ""
print(f"sn_display (fallback) = '{sn_display}'")
assert sn_display == "SN001,SN002", f"Expected SN001,SN002, got {sn_display}"
print("Test 1 PASS: Fallback to batch_sn_list works in search_quotes")

# get_quote_by_id 也应返回 batch_sn_list
quote = get_quote_by_id(1)
sn_edit = quote.get("sn_list", "") or quote.get("batch_sn_list", "")
print(f"quote.sn_list = '{quote.get('sn_list', '')}'")
print(f"quote.batch_sn_list = '{quote.get('batch_sn_list', '')}'")
print(f"sn_edit (fallback) = '{sn_edit}'")
assert sn_edit == "SN001,SN002", f"Expected SN001,SN002, got {sn_edit}"
print("Test 2 PASS: Fallback to batch_sn_list works in get_quote_by_id")

# 场景2: 编辑报价时设置了 quotes.sn_list，应优先显示
update_quote(1, bid, cid, 7200, 2, '2026-05-30', '', '否', 'SN_EDIT')
quote2 = get_quote_by_id(1)
sn_edit2 = quote2.get("sn_list", "") or quote2.get("batch_sn_list", "")
print(f"After edit: sn_edit = '{sn_edit2}'")
assert sn_edit2 == "SN_EDIT", f"Expected SN_EDIT, got {sn_edit2}"
print("Test 3 PASS: quotes.sn_list takes priority over batch_sn_list")

if os.path.exists(test_db):
    os.remove(test_db)

print("\nALL SN FALLBACK TESTS PASSED!")
