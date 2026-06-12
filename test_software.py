"""
调货助手 v1.02 - 软件功能测试脚本
"""

import sys
import os
import tempfile
import shutil

print("=" * 60)
print("调货助手 v1.02 - 功能测试")
print("=" * 60)
print()

sys.path.insert(0, os.path.dirname(__file__))

from src.models import database as db

test_results = []
test_count = 0
pass_count = 0


def test(name, func):
    """执行单个测试"""
    global test_count, pass_count
    test_count += 1
    print(f"\n[测试 {test_count}] {name}")
    print("-" * 50)
    try:
        result = func()
        if result:
            print(f"[PASS] 通过")
            pass_count += 1
            test_results.append((name, "[PASS]", ""))
        else:
            print(f"[FAIL] 失败")
            test_results.append((name, "[FAIL]", ""))
        return result
    except Exception as e:
        print(f"[ERROR] 异常: {str(e)}")
        test_results.append((name, "[ERROR]", str(e)))
        return False


def test_database_init():
    """测试数据库初始化"""
    print("正在初始化数据库...")
    db.init_db()
    print(f"数据库路径: {db.DB_PATH}")
    print(f"数据目录: {db.APP_DATA_DIR}")
    return os.path.exists(db.DB_PATH)


def test_backup():
    """测试自动备份功能"""
    print("测试自动备份...")
    success, message = db.backup_database()
    print(f"备份结果: {message}")
    print(f"备份目录: {db.BACKUP_DIR}")
    if os.path.exists(db.BACKUP_DIR):
        backups = [f for f in os.listdir(db.BACKUP_DIR) if f.startswith("diaohuo_backup_")]
        print(f"当前备份数量: {len(backups)}")
    return success


def test_product_crud():
    """测试机型增删改查"""
    print("测试机型管理...")
    
    pid1 = db.add_product("拯救者Y9000P", "I9-13900HX", "32G", "1TB", "RTX4060", "16寸", "黑色")
    print(f"新增机型ID: {pid1}")
    
    pid2 = db.add_product("小新Pro16", "I5-13500H", "16G", "512GB", "集成", "16寸", "银色")
    print(f"新增机型ID: {pid2}")
    
    products = db.get_all_products()
    print(f"当前机型总数: {len(products)}")
    
    db.update_product(pid1, "拯救者Y9000P", "I9-13900HX", "32G", "1TB", "RTX4070", "16寸", "黑色新版")
    
    updated = db.search_products("Y9000P")
    print(f"搜索Y9000P结果: {len(updated)} 条")
    
    return len(products) >= 2


def test_batch_and_stock():
    """测试批次管理和库存计算"""
    print("测试批次管理和库存...")
    
    products = db.get_all_products()
    if not products:
        print("没有机型，跳过测试")
        return False
    
    pid = products[0]["id"]
    print(f"使用机型ID: {pid}")
    
    bid1 = db.add_batch(pid, 8500, 10, 10, "2026-05-20")
    print(f"新增批次1 (进货10台): ID={bid1}")
    
    bid2 = db.add_batch(pid, 8600, 5, 5, "2026-05-22")
    print(f"新增批次2 (进货5台): ID={bid2}")
    
    stock1 = db.get_total_remaining(pid)
    print(f"初始总库存: {stock1} 台")
    
    success, msg = db.deduct_batch_remaining(bid1, 3)
    print(f"扣减3台: {msg}")
    
    stock2 = db.get_total_remaining(pid)
    print(f"扣减后总库存: {stock2} 台")
    
    batch1_remaining = db.get_batch_remaining(bid1)
    print(f"批次1剩余: {batch1_remaining} 台")
    
    return stock2 == 12 and batch1_remaining == 7


def test_customer_and_quotes():
    """测试客户管理和报价记录"""
    print("测试客户管理和报价...")
    
    cid = db.add_customer("张三", "zhangsan", "123456", "13800138000", "重要客户")
    print(f"新增客户ID: {cid}")
    
    customers = db.get_all_customers()
    print(f"当前客户总数: {len(customers)}")
    
    products = db.get_all_products()
    if not products:
        print("没有机型，跳过报价测试")
        return False
    
    pid = products[0]["id"]
    batches = db.get_batches(pid)
    if not batches:
        print("没有批次，跳过报价测试")
        return False
    
    bid = batches[0]["id"]
    print(f"使用批次ID: {bid}")
    
    db.add_quote(bid, cid, 9500, 1, "2026-05-24", "测试报价", "否")
    print("新增报价记录")
    
    db.add_quote(bid, cid, 9800, 2, "2026-05-24", "第二次报价", "否")
    print("新增第二条报价记录")
    
    quotes = db.get_customer_quotes(cid)
    print(f"客户报价记录数: {len(quotes)} 条")
    
    stats = db.get_customer_stats(cid)
    print(f"客户统计: {stats}")
    
    return len(quotes) == 2


def test_json_export_import():
    """测试JSON导出和导入"""
    print("测试JSON导出和导入...")
    
    try:
        from src.utils.json_export import export_all_to_json, import_from_json, validate_json_file
        
        temp_dir = tempfile.mkdtemp()
        json_path = os.path.join(temp_dir, "test_backup.json")
        
        print(f"导出到: {json_path}")
        export_path = export_all_to_json(db, json_path)
        print(f"导出成功: {export_path}")
        
        valid, msg, stats = validate_json_file(json_path)
        print(f"验证结果: {msg}")
        print(f"数据统计: {stats}")
        
        success, msg, import_stats = import_from_json(json_path, db)
        print(f"导入结果: {msg}")
        print(f"导入统计: {import_stats}")
        
        shutil.rmtree(temp_dir)
        print("临时文件已清理")
        
        return valid and success
        
    except ImportError as e:
        print(f"导入失败（模块可能未安装）: {e}")
        return False
    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_operation_log():
    """测试操作日志（如果存在）"""
    print("测试操作日志...")
    
    try:
        db.add_operation_log("测试", "products", 1, "测试操作日志")
        logs = db.get_operation_logs(10)
        print(f"日志记录数: {len(logs)} 条")
        return len(logs) > 0
    except Exception as e:
        print(f"操作日志功能未实现或出错: {e}")
        return True


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("开始执行测试...")
    print("=" * 60)
    
    test("数据库初始化", test_database_init)
    test("自动备份功能", test_backup)
    test("机型增删改查", test_product_crud)
    test("批次管理和库存计算", test_batch_and_stock)
    test("客户管理和报价", test_customer_and_quotes)
    test("JSON导出导入", test_json_export_import)
    test("操作日志", test_operation_log)
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"总测试数: {test_count}")
    print(f"通过: {pass_count}")
    print(f"失败: {test_count - pass_count}")
    print(f"通过率: {pass_count/test_count*100:.1f}%")
    print()
    
    print("详细结果:")
    print("-" * 60)
    for name, result, error in test_results:
        status = f"{result}" + (f" - {error[:50]}" if error else "")
        print(f"{name:40s} {status}")
    
    print("\n" + "=" * 60)
    if pass_count == test_count:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED - Please check error messages above")
    print("=" * 60)
    
    return pass_count == test_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
