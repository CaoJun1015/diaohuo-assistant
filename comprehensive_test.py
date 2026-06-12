"""
全面测试脚本 - 验证机型管理UI交互不会崩溃
结果写入 test_result.txt
"""

import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RESULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output_log.txt")


def log(msg):
    with open(RESULT_FILE, "a", encoding="utf-8") as f:
        f.write(f"  {msg}\n")


def write(msg):
    with open(RESULT_FILE, "a", encoding="utf-8") as f:
        f.write(f"{msg}\n")


def main():
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        f.write("=" * 50 + "\n")
        f.write("  调货助手 v1.04 - 机型管理交互全面测试\n")
        f.write("=" * 50 + "\n")

    test_count = 0
    pass_count = 0
    fail_count = 0
    results = []

    def run_test(name, fn):
        nonlocal test_count, pass_count, fail_count
        test_count += 1
        write(f"\n{'='*50}")
        write(f"  TEST {test_count}: {name}")
        write(f"{'='*50}")
        try:
            fn()
            pass_count += 1
            log("PASS")
            results.append((name, True, None))
        except Exception as e:
            fail_count += 1
            log(f"FAIL - {e}")
            trace = traceback.format_exc()
            write(trace)
            results.append((name, False, str(e)))

    # ---- DB init ----
    log("初始化数据库...")
    from src.models.database import init_db, add_product, get_all_products
    from src.models.database import add_batch, get_batches, get_total_remaining, delete_batch
    init_db()
    log("OK")

    log("检查测试数据...")
    existing = get_all_products()
    if not existing:
        add_product(series="拯救者Y9000P", cpu="i9-13900HX", ram="16GB",
                    storage="1TB", gpu="RTX4060", screen='16"')
        add_product(series="ThinkPad X1", cpu="i7-1360P", ram="32GB",
                    storage="512GB", gpu="集成", screen='14"')
        add_product(series="小新Pro16", cpu="R7-7840HS", ram="32GB",
                    storage="1TB", gpu="RTX4050", screen='16"')
        log("已添加 3 条测试机型")
    products = get_all_products()
    log(f"数据库中共有 {len(products)} 条机型")

    for p in products:
        batches = get_batches(p["id"])
        if not batches:
            add_batch(p["id"], 8000, 10, 10, "2026-01-01")
            add_batch(p["id"], 8200, 5, 5, "2026-02-01")
    log("批次数据就绪")

    # ---- Create app ----
    log("创建 QApplication...")
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    log("QApplication OK")

    log("创建 MainWindow...")
    from src.main import MainWindow, QuotePanel
    window = MainWindow()
    log(f"MainWindow OK, 标题={window.windowTitle()}, 产品行数={window.product_table.rowCount()}")

    # ---- TEST 1 ----
    def t1():
        assert window.windowTitle() == "调货助手 v1.04"
        assert window.product_table.rowCount() > 0
    run_test("主窗口初始化", t1)

    # ---- TEST 2 ----
    def t2():
        window.product_table.selectRow(0)
        assert window.product_table.currentRow() == 0
        pid = int(window.product_table.item(0, 0).text())
        assert window.quote_panel.current_product_id == pid
        assert window.quote_panel.batch_table.rowCount() > 0
        log(f"选中 ID={pid}, 批次={window.quote_panel.batch_table.rowCount()}")
    run_test("选择第一个机型", t2)

    # ---- TEST 3 ----
    def t3():
        assert window.product_table.rowCount() >= 2
        first = window.quote_panel.current_product_id
        window.product_table.selectRow(1)
        second = int(window.product_table.item(1, 0).text())
        assert window.quote_panel.current_product_id == second
        assert second != first
        log(f"切换 {first} -> {second}")
    run_test("切换机型", t3)

    # ---- TEST 4 ----
    def t4():
        total = window.product_table.rowCount()
        for _ in range(10):
            for idx in range(min(total, 3)):
                window.product_table.selectRow(idx)
        assert window.quote_panel.batch_table.rowCount() > 0
        log("30 次切换无崩溃")
    run_test("快速连续切换 - 30次", t4)

    # ---- TEST 5 ----
    def t5():
        total = window.product_table.rowCount()
        window.product_table.selectRow(total - 1)
        assert window.quote_panel.current_product_id is not None
    run_test("选择最后机型", t5)

    # ---- TEST 6 ----
    def t6():
        window.refresh_product_list()
        assert window.product_table.rowCount() > 0
        window.product_table.selectRow(0)
        assert window.quote_panel.current_product_id is not None
    run_test("刷新后重选", t6)

    # ---- TEST 7 ----
    def t7():
        window.search_edit.setText("拯救者")
        n = window.product_table.rowCount()
        log(f"搜索'拯救者'={n}条")
        if n > 0:
            window.product_table.selectRow(0)
            assert window.quote_panel.current_product_id is not None
        window.search_edit.clear()
        window.refresh_product_list()
    run_test("搜索后选择", t7)

    # ---- TEST 8 ----
    def t8():
        window.product_table.selectRow(0)
        pid = window.quote_panel.current_product_id
        before = len(get_batches(pid))
        add_batch(pid, 7500, 3, 3, "2026-05-25")
        window.quote_panel.refresh()
        after = window.quote_panel.batch_table.rowCount()
        assert after == before + 1
        batches = get_batches(pid)
        delete_batch(batches[-1]["id"])
    run_test("新增批次刷新", t8)

    # ---- TEST 9 ----
    def t9():
        window.product_table.selectRow(0)
        r = get_total_remaining(window.quote_panel.current_product_id)
        assert r >= 0
        log(f"库存={r}")
    run_test("库存计算", t9)

    # ---- TEST 10 ----
    def t10():
        panel = QuotePanel()
        p = products[0]
        panel.load_product(p["id"], p.get("series",""), p.get("cpu",""),
                          p.get("ram",""), p.get("storage",""), p.get("gpu",""),
                          p.get("screen",""), p.get("note",""))
        assert panel.current_product_id == p["id"]
        assert panel.batch_table.rowCount() > 0
    run_test("QuotePanel独立实例化", t10)

    # ---- TEST 11: KEY TEST ----
    def t11():
        call_count = [0]
        orig = window.on_product_selected
        def counting():
            call_count[0] += 1
            if call_count[0] > 100:
                raise RecursionError("递归!")
            orig()
        window.on_product_selected = counting
        try:
            window.refresh_product_list()
            log(f"on_product_selected 调用 {call_count[0]} 次")
            assert call_count[0] <= 5, f"过多调用: {call_count[0]}"
        finally:
            window.on_product_selected = orig
    run_test("【关键】无递归调用", t11)

    # ---- TEST 12 ----
    def t12():
        from src.models.database import delete_product as dp
        pid = add_product(series="DEL_TEST", cpu="x", ram="8GB",
                         storage="256GB", gpu="", screen='13"')
        window.refresh_product_list()
        before = window.product_table.rowCount()
        dp(pid)
        window.refresh_product_list()
        after = window.product_table.rowCount()
        assert after == before - 1
        if after > 0:
            window.product_table.selectRow(0)
            assert window.quote_panel.current_product_id is not None
    run_test("删除后界面稳定", t12)

    # ---- TEST 13: 新功能 - 状态变更 ----
    def t13():
        from src.models.database import update_quote_status, search_quotes
        quotes = search_quotes("", "", "")
        if quotes:
            qid = quotes[0]["id"]
            orig_status = quotes[0].get("status", "待确认")
            update_quote_status(qid, "已报价")
            q2 = search_quotes("", "", "")
            found = [q for q in q2 if q["id"] == qid]
            if found:
                assert found[0].get("status") == "已报价"
                update_quote_status(qid, orig_status)
            log(f"状态变更: {orig_status} -> 已报价 -> {orig_status}")
    run_test("状态变更", t13)

    # ---- TEST 14: 新功能 - 收款记录 ----
    def t14():
        from src.models.database import add_payment, get_payments, get_customer_balance
        quotes = search_quotes("", "", "")
        if quotes:
            q = quotes[0]
            if q.get("customer_id"):
                add_payment(quote_id=q["id"], customer_id=q["customer_id"],
                           pay_type="receivable", amount=100,
                           pay_date="2026-05-25", method="微信", remark="测试收款")
                payments = get_payments(quote_id=q["id"])
                assert len(payments) > 0
                log(f"收款记录: {len(payments)}条")
    run_test("收款记录", t14)

    # ---- TEST 15: 新功能 - 对账单查询 ----
    def t15():
        from src.models.database import get_customer_statement
        stmt = get_customer_statement(1, "", "")
        log(f"对账单查询: {len(stmt)}条记录")
    run_test("对账单查询", t15)

    # ---- TEST 16: 新功能 - SN序列号 ----
    def t16():
        from src.models.database import add_batch, get_batches, delete_batch
        products = get_all_products()
        if products:
            pid = products[0]["id"]
            add_batch(pid, 5000, 2, 2, "2026-05-25", "测试SN批次", None, "SN001,SN002")
            batches = get_batches(pid)
            last_batch = batches[-1]
            sn = last_batch.get("sn_list", "")
            log(f"SN存储: {sn}")
            delete_batch(last_batch["id"])
    run_test("SN序列号", t16)

    # ---- TEST 17: 新功能 - Tab验证 ----
    def t17():
        assert window.tabs.count() >= 5
        tab_texts = [window.tabs.tabText(i) for i in range(window.tabs.count())]
        log(f"Tab数量: {window.tabs.count()}, Tabs: {tab_texts}")
    run_test("Tab验证", t17)

    # ---- SUMMARY ----
    write(f"\n{'='*50}")
    write(f"  测试汇总")
    write(f"{'='*50}")
    write(f"  总数: {test_count}  通过: {pass_count}  失败: {fail_count}")
    if fail_count > 0:
        for name, ok, err in results:
            if not ok:
                write(f"    FAIL: {name} -> {err}")
    else:
        write(f"  全部 {pass_count}/{test_count} 测试通过!")
    write(f"{'='*50}")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())