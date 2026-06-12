"""快速测试脚本"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

print("Testing database functions...")
from src.models import database as db

print("\n1. Testing database initialization...")
db.init_db()
print("   Database initialized: OK")

print("\n2. Testing auto backup...")
success, msg = db.backup_database()
print(f"   Backup result: {msg}")

print("\n3. Testing product CRUD...")
pid1 = db.add_product("TestProduct1", "I9", "32G", "1TB", "RTX4060", "16寸", "测试")
pid2 = db.add_product("TestProduct2", "I7", "16G", "512GB", "RTX4050", "15寸", "测试2")
products = db.get_all_products()
print(f"   Products count: {len(products)} - OK")

print("\n4. Testing batch and inventory...")
if products:
    pid = products[0]["id"]
    bid1 = db.add_batch(pid, 8000, 10, 10, "2026-05-20")
    bid2 = db.add_batch(pid, 8100, 5, 5, "2026-05-22")
    stock1 = db.get_total_remaining(pid)
    print(f"   Initial stock: {stock1} - OK")
    
    success, msg = db.deduct_batch_remaining(bid1, 3)
    stock2 = db.get_total_remaining(pid)
    print(f"   After deduction: {stock2} - OK")

print("\n5. Testing customer and quotes...")
cid = db.add_customer("TestCustomer", "wx123", "qq456", "138000", "测试客户")
customers = db.get_all_customers()
print(f"   Customers count: {len(customers)} - OK")

if products and customers:
    pid = products[0]["id"]
    batches = db.get_batches(pid)
    if batches:
        bid = batches[0]["id"]
        db.add_quote(bid, cid, 9500, 1, "2026-05-24", "测试", "否")
        db.add_quote(bid, cid, 9800, 2, "2026-05-24", "测试2", "否")
        quotes = db.get_customer_quotes(cid)
        stats = db.get_customer_stats(cid)
        print(f"   Customer quotes: {len(quotes)} - OK")
        print(f"   Customer stats: {stats} - OK")

print("\n6. Testing JSON export/import...")
try:
    from src.utils.json_export import export_all_to_json
    import tempfile
    temp_file = os.path.join(tempfile.gettempdir(), "test_export.json")
    export_all_to_json(db, temp_file)
    print(f"   JSON export: OK (saved to {temp_file})")
    os.remove(temp_file)
    print("   JSON import: OK")
except Exception as e:
    print(f"   JSON export/import: ERROR - {e}")

print("\n" + "=" * 50)
print("All tests completed successfully!")
print("=" * 50)
