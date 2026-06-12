"""
Bug fix verification tests
"""
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

results = []
test_count = 0
pass_count = 0
fail_count = 0

def run_test(name, fn):
    global test_count, pass_count, fail_count
    test_count += 1
    print(f"\n  [{test_count}] {name}...")
    try:
        fn()
        pass_count += 1
        print("    PASS")
        results.append((name, True, None))
    except AssertionError as e:
        fail_count += 1
        print(f"    FAIL: {e}")
        results.append((name, False, str(e)))
    except Exception as e:
        fail_count += 1
        print(f"    FAIL: {type(e).__name__}: {e}")
        traceback.print_exc()
        results.append((name, False, str(e)))

def main():
    from src.models.database import (
        init_db, get_connection,
        add_product, get_all_products, search_products,
        add_batch, get_batches, delete_batch, delete_product,
        add_customer, get_all_customers,
        add_supplier, get_all_suppliers,
        add_quote, search_quotes, get_quote_by_id,
        update_quote_status, add_payment, get_payments,
        get_customer_balance, get_supplier_payable, get_customer_statement,
    )
    init_db()

    # Cleanup old test data
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("DELETE FROM payments WHERE customer_id IN (SELECT id FROM customers WHERE name LIKE 'BUGFIX_%')")
    conn.execute("DELETE FROM payments WHERE supplier_id IN (SELECT id FROM suppliers WHERE name LIKE 'BUGFIX_%')")
    conn.execute("DELETE FROM quotes WHERE customer_id IN (SELECT id FROM customers WHERE name LIKE 'BUGFIX_%')")
    conn.execute("DELETE FROM quotes WHERE batch_id IN (SELECT id FROM batches WHERE product_id IN (SELECT id FROM products WHERE series LIKE 'BUGFIX_%'))")
    conn.execute("DELETE FROM batches WHERE product_id IN (SELECT id FROM products WHERE series LIKE 'BUGFIX_%')")
    conn.execute("DELETE FROM products WHERE series LIKE 'BUGFIX_%'")
    conn.execute("DELETE FROM customers WHERE name LIKE 'BUGFIX_%'")
    conn.execute("DELETE FROM suppliers WHERE name LIKE 'BUGFIX_%'")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit(); conn.close()

    pid = add_product("BUGFIX_Model", "i9", "16G", "512G", "RTX4060", '15"', "test")
    cid = add_customer("BUGFIX_Cust", "wx", "qq", "138", "test")
    sid = add_supplier("BUGFIX_Supp", "wx", "qq", "139", "test")
    print(f"Setup: pid={pid}, cid={cid}, sid={sid}")

    # ============================================================
    # Bug 1: delete_product cascade test
    # ============================================================
    def t1():
        bid = add_batch(pid, 5000, 2, 2, "2026-05-25", "test", sid, "SN-01")
        add_quote(bid, cid, 6000, 1, "2026-05-25", "test", "")
        quotes_before = search_quotes("BUGFIX", "", "")
        assert len(quotes_before) >= 1, f"quotes before: {len(quotes_before)}"

        delete_product(pid)
        quotes_after = search_quotes("BUGFIX", "", "")
        assert len(quotes_after) == 0, f"quotes after delete: {len(quotes_after)}"
        batches = get_batches(pid)
        assert len(batches) == 0, f"batches after: {len(batches)}"
        print("    cascade delete OK: quotes and batches cleaned up")
    run_test("Bug1: delete_product cascade deletes batches+quotes", t1)

    # ============================================================
    # Bug 2a: finance receive now links to quote
    # ============================================================
    def t2():
        pid2 = add_product("BUGFIX_Model2", "i7", "8G", "256G", "GTX1650", '14"', "test")
        bid2 = add_batch(pid2, 4000, 3, 3, "2026-05-25", "test", sid, "")
        add_quote(bid2, cid, 5000, 2, "2026-05-25", "test", "")
        qs = search_quotes("BUGFIX_Model2", "", "")
        assert len(qs) == 1
        qid = qs[0]["id"]
        assert qs[0]["status"] == "待确认"

        # Collect partial payment via finance-style receive (with quote_id)
        add_payment(quote_id=qid, customer_id=cid, pay_type="receivable",
                    amount=3000, pay_date="2026-05-25", method="微信", remark="test")
        q = get_quote_by_id(qid)
        assert q["received_amount"] == 3000, f"received: {q['received_amount']}"
        assert q["status"] != "已收款"

        # Collect remaining
        add_payment(quote_id=qid, customer_id=cid, pay_type="receivable",
                    amount=7000, pay_date="2026-05-25", method="转账", remark="test")
        q2 = get_quote_by_id(qid)
        assert q2["received_amount"] == 10000, f"received: {q2['received_amount']}"
        assert q2["status"] == "已收款", f"status: {q2['status']}"
        print("    payment linked to quote: received_amount updated correctly, auto status change")

        # Cleanup
        conn = get_connection()
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("DELETE FROM payments WHERE quote_id=?", (qid,))
        conn.execute("DELETE FROM quotes WHERE id=?", (qid,))
        conn.execute("DELETE FROM batches WHERE id=?", (bid2,))
        conn.execute("DELETE FROM products WHERE id=?", (pid2,))
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit(); conn.close()
    run_test("Bug2a: payment with quote_id updates received_amount+status", t2)

    # ============================================================
    # Bug 2b: supplier payable now shows data
    # ============================================================
    def t3():
        # Reset supplier balance for clean test
        conn = get_connection()
        conn.execute("UPDATE suppliers SET balance=0 WHERE id=?", (sid,))
        conn.commit()
        conn.execute("DELETE FROM payments WHERE supplier_id=?", (sid,))
        conn.commit(); conn.close()

        # Add batch with supplier - should increase balance
        pid3 = add_product("BUGFIX_Model3", "i5", "8G", "256G", "集成", '14"', "test")
        add_batch(pid3, 3000, 5, 5, "2026-05-25", "test", sid, "")

        # Check supplier balance was updated
        conn = get_connection()
        balance = conn.execute("SELECT COALESCE(balance,0) FROM suppliers WHERE id=?", (sid,)).fetchone()[0]
        print(f"    supplier balance after purchase: {balance}")
        assert balance == 3000 * 5, f"balance should be 15000, got {balance}"

        # Now simulate paying
        add_payment(supplier_id=sid, pay_type="payable", amount=5000,
                    pay_date="2026-05-25", method="银行", remark="test")
        balance2 = conn.execute("SELECT COALESCE(balance,0) FROM suppliers WHERE id=?", (sid,)).fetchone()[0]
        print(f"    supplier balance after payment: {balance2}")
        assert balance2 == 10000, f"balance should be 10000, got {balance2}"
        conn.close()

        # Test dynamic payable query returns data
        conn = get_connection()
        debt = conn.execute("""
            SELECT COALESCE(SUM(b.purchase_price * b.quantity), 0) -
                   COALESCE((SELECT SUM(py.amount) FROM payments py WHERE py.supplier_id=s.id AND py.type='payable'), 0)
            FROM suppliers s
            LEFT JOIN batches b ON b.supplier_id = s.id
            WHERE s.id = ?
            GROUP BY s.id
        """, (sid,)).fetchone()
        print(f"    dynamic debt calculation: {debt[0] if debt else 0}")
        assert debt and debt[0] > 0, f"dynamic debt should be > 0"
        conn.close()

        # Cleanup supplier balance
        conn = get_connection()
        conn.execute("UPDATE suppliers SET balance=0 WHERE id=?", (sid,))
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("DELETE FROM payments WHERE supplier_id=?", (sid,))
        conn.execute("DELETE FROM quotes WHERE batch_id IN (SELECT id FROM batches WHERE product_id=?)", (pid3,))
        conn.execute("DELETE FROM batches WHERE product_id=?", (pid3,))
        conn.execute("DELETE FROM products WHERE id=?", (pid3,))
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit(); conn.close()
    run_test("Bug2b: supplier balance updates on purchase+payment, payable shows", t3)

    # ============================================================
    # Cleanup
    # ============================================================
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("DELETE FROM payments WHERE customer_id IN (SELECT id FROM customers WHERE name LIKE 'BUGFIX_%')")
    conn.execute("DELETE FROM payments WHERE supplier_id IN (SELECT id FROM suppliers WHERE name LIKE 'BUGFIX_%')")
    conn.execute("DELETE FROM quotes WHERE customer_id IN (SELECT id FROM customers WHERE name LIKE 'BUGFIX_%')")
    conn.execute("DELETE FROM quotes WHERE batch_id IN (SELECT id FROM batches WHERE product_id IN (SELECT id FROM products WHERE series LIKE 'BUGFIX_%'))")
    conn.execute("DELETE FROM batches WHERE product_id IN (SELECT id FROM products WHERE series LIKE 'BUGFIX_%')")
    conn.execute("DELETE FROM products WHERE series LIKE 'BUGFIX_%'")
    conn.execute("DELETE FROM customers WHERE name LIKE 'BUGFIX_%'")
    conn.execute("DELETE FROM suppliers WHERE name LIKE 'BUGFIX_%'")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit(); conn.close()
    print("\nCleanup done.")

    # Summary
    total = pass_count + fail_count
    print(f"\n{'='*50}\n  Total: {total}  Pass: {pass_count}  Fail: {fail_count}")
    if fail_count:
        print("  FAILED:")
        for n, ok, err in results:
            if not ok:
                print(f"    - {n}: {err}")
    else:
        print("  ALL TESTS PASSED!")
    print("="*50)
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())