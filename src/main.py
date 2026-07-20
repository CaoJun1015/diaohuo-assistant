"""
主窗口及各个 UI 面板
"""

import sys
import os
import re
import traceback
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QComboBox, QTextEdit,
    QMessageBox, QFileDialog, QDialog, QFormLayout,
    QSpinBox, QDateEdit, QDialogButtonBox,
    QFrame, QHeaderView, QAbstractItemView, QCheckBox, QGroupBox,
    QGridLayout, QMenu, QMenuBar, QStatusBar,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QAction, QClipboard, QColor

# 确保能找到 src 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.database import (
    init_db, add_product, update_product, delete_product,
    search_products, get_all_products,
    add_batch, get_batches, update_batch_remaining, delete_batch, get_total_remaining,
    get_all_customers,
    add_supplier, search_suppliers, get_all_suppliers,
    add_quote, update_quote, delete_quote, search_quotes, export_quotes, get_quote_by_id,
    update_quote_status, add_payment, _add_payment_raw, get_payments, get_customer_balance,
    get_supplier_payable, get_customer_statement, deduct_batch_remaining,
    delete_supplier_cascade,
    get_payment_by_id, get_all_payments_with_details, update_payment, delete_payment,
    get_connection, ship_quote, add_operation_log,
)
from src.ui.style import APP_STYLE
from src.ui.dialogs import (
    ShipmentDialog, PaymentDialog, PaymentEditDialog, StatementDialog,
    ProductEditDialog, BatchDialog, CustomerDialog, QuoteEditDialog,
    OperationLogDialog,
)
from src.ui.quote_panel import QuotePanel
from src.ui.product_tab import ProductTab
from src.ui.record_tab import RecordTab
from src.ui.customer_tab import CustomerTab
from src.ui.supplier_tab import SupplierTab
from src.ui.utils import _validate_date, _global_excepthook
from src.utils.word_parser import parse_word_pricelist, preview_parse
from src.utils.image_gen import generate_quote_image, generate_single_quote_card, WATERMARK_TEXT
from src.utils.excel_export import export_quotes_to_excel
from src.utils.price_diff import save_snapshot, get_latest_snapshot, diff_snapshots, get_all_snapshots
from src.utils.follow_up import get_stale_quotes, format_reminder_text
from src.utils.monthly_report import get_monthly_report, format_report_text
from src.utils.shipment_flow import parse_sn_input, validate_sn, validate_sn_list, check_sn_duplicates, generate_shipment_receipt
from src.utils.quote_assist import get_quote_history, suggest_price, get_customer_price_history
from src.utils.remote_diagnose import search_diagnose, get_diagnose_tree, get_all_diagnose_keys, generate_diagnose_report


# ============================================================
# 主窗口
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("调货助手 v1.10")
        self.setMinimumSize(1100, 700)

        # 初始化数据库（含自动备份 + 完整性检查）
        init_ok, init_msg = init_db()
        self.backup_status = init_msg

        # 中心控件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # 搜索 + 工具栏
        top_bar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("globalSearch")
        self.search_edit.setPlaceholderText("搜索机型（系列/CPU/关键字）...")
        self.search_edit.textChanged.connect(self.on_search)
        self.search_edit.setMinimumWidth(250)

        self.import_btn = QPushButton("导入 Word 价格表")
        self.import_btn.setObjectName("ghostBtn")
        self.import_btn.clicked.connect(self.on_import_word)
        self.broadcast_btn = QPushButton("群发图片")
        self.broadcast_btn.setObjectName("ghostBtn")
        self.broadcast_btn.clicked.connect(self.on_broadcast)
        self.export_btn = QPushButton("导出 Excel")
        self.export_btn.setObjectName("ghostBtn")
        self.export_btn.clicked.connect(self.on_export_excel)
        self.export_json_btn = QPushButton("JSON备份")
        self.export_json_btn.setObjectName("ghostBtn")
        self.export_json_btn.clicked.connect(self.on_export_json)
        self.import_json_btn = QPushButton("JSON导入")
        self.import_json_btn.setObjectName("ghostBtn")
        self.import_json_btn.clicked.connect(self.on_import_json)
        self.log_btn = QPushButton("操作日志")
        self.log_btn.setObjectName("ghostBtn")
        self.log_btn.clicked.connect(self.on_show_logs)
        self.statement_btn = QPushButton("对账单")
        self.statement_btn.setObjectName("ghostBtn")
        self.statement_btn.clicked.connect(self.on_statement)
        self.follow_up_btn = QPushButton("🔔 跟单提醒")
        self.follow_up_btn.setObjectName("ghostBtn")
        self.follow_up_btn.clicked.connect(self.on_follow_up)
        self.report_btn = QPushButton("📊 月度报告")
        self.report_btn.setObjectName("ghostBtn")
        self.report_btn.clicked.connect(self.on_monthly_report)
        self.diagnose_btn = QPushButton("🔧 远程诊断")
        self.diagnose_btn.setObjectName("ghostBtn")
        self.diagnose_btn.clicked.connect(self.on_remote_diagnose)
        self.price_diff_btn = QPushButton("价格异动")
        self.price_diff_btn.setObjectName("ghostBtn")
        self.price_diff_btn.clicked.connect(self.on_price_diff)
        self.quote_assist_btn = QPushButton("报价助手")
        self.quote_assist_btn.setObjectName("ghostBtn")
        self.quote_assist_btn.clicked.connect(self.on_quote_assist)
        self.shipment_flow_btn = QPushButton("出库一条龙")
        self.shipment_flow_btn.setObjectName("ghostBtn")
        self.shipment_flow_btn.clicked.connect(self.on_shipment_flow)

        top_bar.addWidget(QLabel("🔍"))
        top_bar.addWidget(self.search_edit)
        top_bar.addStretch()

        def _add_sep(layout):
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.VLine)
            sep.setObjectName("toolbarSeparator")
            layout.addWidget(sep)

        top_bar.addWidget(self.follow_up_btn)
        top_bar.addWidget(self.report_btn)
        top_bar.addWidget(self.diagnose_btn)
        top_bar.addWidget(self.price_diff_btn)
        top_bar.addWidget(self.quote_assist_btn)
        top_bar.addWidget(self.shipment_flow_btn)
        _add_sep(top_bar)
        top_bar.addWidget(self.import_btn)
        top_bar.addWidget(self.broadcast_btn)
        top_bar.addWidget(self.export_btn)
        top_bar.addWidget(self.statement_btn)
        top_bar.addWidget(self.export_json_btn)
        top_bar.addWidget(self.import_json_btn)
        _add_sep(top_bar)
        top_bar.addWidget(self.log_btn)
        main_layout.addLayout(top_bar)

        # Tab 页面
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # === Tab 1: 机型管理 ===
        tab_products = QWidget()
        tab_layout = QHBoxLayout(tab_products)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左：机型列表
        self.product_tab = ProductTab(self)
        splitter.addWidget(self.product_tab)

        # 右：报价面板
        self.quote_panel = QuotePanel()
        splitter.addWidget(self.quote_panel)
        splitter.setSizes([600, 450])

        tab_layout.addWidget(splitter)
        self.tabs.addTab(tab_products, "📋 机型管理")

        # === Tab 2: 客户管理 ===
        tab_customers = self._build_customer_tab()
        self.tabs.addTab(tab_customers, "👤 客户管理")

        # === Tab 3: 上游管理 ===
        tab_suppliers = self._build_supplier_tab()
        self.tabs.addTab(tab_suppliers, "🏭 上游管理")

        # === Tab 4: 报价记录 ===
        tab_records = self._build_records_tab()
        self.tabs.addTab(tab_records, "📊 报价记录")

        # === Tab 5: 账款管理 ===
        tab_finance = self._build_finance_tab()
        self.tabs.addTab(tab_finance, "💰 账款管理")

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel(f"就绪 | {self.backup_status}")
        self.status_bar.addWidget(self.status_label)

        # 加载数据
        self.product_tab.refresh_product_list()
        self.customer_tab.refresh_customer_list()
        self.supplier_tab.refresh_supplier_list()
        self.refresh_records()

        # 启用所有表格的列头排序
        for table in self.findChildren(QTableWidget):
            table.setSortingEnabled(True)

    def on_confirm_quote(self):
        self.record_tab.on_confirm_quote()

    def on_ship_quote(self):
        self.record_tab.on_ship_quote()

    def on_receive_payment(self):
        self.record_tab.on_receive_payment()

    def on_cancel_quote(self):
        self.record_tab.on_cancel_quote()

    def on_statement(self):
        dlg = StatementDialog(self)
        dlg.exec()

    # -------------------------------------------------------
    # 账款管理
    # -------------------------------------------------------
    def _build_finance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)

        # === 上部分：应收/应付（占比调大） ===
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_title = QLabel("应收款项（客户欠款）")
        left_title.setObjectName("sectionTitleRed")
        left_layout.addWidget(left_title)

        self.receivable_table = QTableWidget()
        self.receivable_table.setAlternatingRowColors(True)
        self.receivable_table.setColumnCount(5)
        self.receivable_table.setHorizontalHeaderLabels(["客户", "欠款金额", "订单数", "联系方式", "操作"])
        self.receivable_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.receivable_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.receivable_table.horizontalHeader().setStretchLastSection(True)
        self.receivable_table.setMinimumHeight(200)  # 设置最小高度
        left_layout.addWidget(self.receivable_table)

        self.refresh_receivable_btn = QPushButton("刷新")
        self.refresh_receivable_btn.setObjectName("ghostBtn")
        self.refresh_receivable_btn.clicked.connect(self.refresh_finance)
        left_btn_row = QHBoxLayout()
        left_btn_row.addStretch()
        left_btn_row.addWidget(self.refresh_receivable_btn)
        left_layout.addLayout(left_btn_row)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_title = QLabel("应付款项（欠上游款）")
        right_title.setObjectName("sectionTitleOrange")
        right_layout.addWidget(right_title)

        self.payable_table = QTableWidget()
        self.payable_table.setAlternatingRowColors(True)
        self.payable_table.setColumnCount(5)
        self.payable_table.setHorizontalHeaderLabels(["上游", "欠款金额", "批次", "联系方式", "操作"])
        self.payable_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.payable_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.payable_table.horizontalHeader().setStretchLastSection(True)
        self.payable_table.setMinimumHeight(200)  # 设置最小高度
        right_layout.addWidget(self.payable_table)

        self.refresh_payable_btn = QPushButton("刷新")
        self.refresh_payable_btn.setObjectName("ghostBtn")
        self.refresh_payable_btn.clicked.connect(self.refresh_finance)
        right_btn_row = QHBoxLayout()
        right_btn_row.addStretch()
        right_btn_row.addWidget(self.refresh_payable_btn)
        right_layout.addLayout(right_btn_row)

        top_splitter.addWidget(left_widget)
        top_splitter.addWidget(right_widget)
        top_splitter.setSizes([400, 400])
        # 上部分占比 3（75%）
        layout.addWidget(top_splitter, stretch=3)

        # === 下部分：收付款流水预览（占比调小） ===
        flow_group = QGroupBox("收付款流水记录")
        flow_group.setMaximumHeight(250)  # 设置最大高度，限制流水区域
        flow_layout = QVBoxLayout(flow_group)

        # 筛选行
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("类型:"))
        self.payment_type_filter = QComboBox()
        self.payment_type_filter.addItems(["全部", "收款", "付款"])
        self.payment_type_filter.currentTextChanged.connect(self.refresh_payment_flow)
        filter_row.addWidget(self.payment_type_filter)

        filter_row.addWidget(QLabel("对象:"))
        self.payment_object_filter = QComboBox()
        self.payment_object_filter.setEditable(True)
        self.payment_object_filter.setPlaceholderText("全部对象...")
        self.payment_object_filter.currentTextChanged.connect(self.refresh_payment_flow)
        filter_row.addWidget(self.payment_object_filter)

        filter_row.addWidget(QLabel("日期从:"))
        self.payment_date_from = QDateEdit()
        self.payment_date_from.setCalendarPopup(True)
        self.payment_date_from.setDate(QDate.currentDate().addMonths(-3))
        self.payment_date_from.dateChanged.connect(self.refresh_payment_flow)
        filter_row.addWidget(self.payment_date_from)

        filter_row.addWidget(QLabel("至:"))
        self.payment_date_to = QDateEdit()
        self.payment_date_to.setCalendarPopup(True)
        self.payment_date_to.setDate(QDate.currentDate())
        self.payment_date_to.dateChanged.connect(self.refresh_payment_flow)
        filter_row.addWidget(self.payment_date_to)

        self.refresh_flow_btn = QPushButton("刷新")
        self.refresh_flow_btn.setObjectName("ghostBtn")
        self.refresh_flow_btn.clicked.connect(self.refresh_payment_flow)
        filter_row.addWidget(self.refresh_flow_btn)

        filter_row.addStretch()
        flow_layout.addLayout(filter_row)

        # 流水表格
        self.payment_flow_table = QTableWidget()
        self.payment_flow_table.setAlternatingRowColors(True)
        self.payment_flow_table.setColumnCount(8)
        self.payment_flow_table.setHorizontalHeaderLabels(
            ["ID", "日期", "类型", "金额", "方式", "关联对象", "备注", "操作"]
        )
        self.payment_flow_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.payment_flow_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.payment_flow_table.horizontalHeader().setStretchLastSection(True)
        self.payment_flow_table.setColumnHidden(0, True)  # 隐藏 ID 列
        flow_layout.addWidget(self.payment_flow_table)

        # 统计标签
        self.payment_flow_stats = QLabel()
        self.payment_flow_stats.setObjectName("summaryLabel")
        flow_layout.addWidget(self.payment_flow_stats)

        # 下部分占比 1（25%）
        layout.addWidget(flow_group, stretch=1)
        return tab

    def refresh_finance(self):
        """刷新应收/应付表格"""
        from src.models.database import get_connection
        conn = get_connection()

        rows = conn.execute("""
            SELECT c.id, c.name, c.wechat, c.phone,
                   COALESCE(SUM(q.quote_price * q.quote_quantity - q.received_amount), 0) as debt,
                   COUNT(q.id) as order_count
            FROM customers c
            LEFT JOIN quotes q ON q.customer_id = c.id AND q.status IN ('已报价','已出库')
            GROUP BY c.id
            HAVING debt > 0
            ORDER BY debt DESC
        """).fetchall()

        self.receivable_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.receivable_table.setItem(i, 0, QTableWidgetItem(r[1]))
            debt_item = QTableWidgetItem(f"¥{r[4]:.0f}")
            debt_item.setForeground(QColor("#D32F2F"))
            self.receivable_table.setItem(i, 1, debt_item)
            self.receivable_table.setItem(i, 2, QTableWidgetItem(str(r[5])))
            contact = " | ".join(filter(None, [r[2] or "", r[3] or ""]))
            self.receivable_table.setItem(i, 3, QTableWidgetItem(contact))
            pay_btn = QPushButton("收款")
            pay_btn.setObjectName("tableActionPrimary")
            pay_btn.clicked.connect(lambda checked, cid=r[0]: self._on_finance_receive(cid))
            self.receivable_table.setCellWidget(i, 4, pay_btn)
        self.receivable_table.resizeColumnsToContents()

        s_rows = conn.execute("""
            SELECT s.id, s.name, s.wechat, s.phone,
                   COALESCE(SUM(b.purchase_price * b.quantity), 0) -
                   COALESCE((SELECT SUM(py.amount) FROM payments py WHERE py.supplier_id = s.id AND py.type = 'payable'), 0) as debt
            FROM suppliers s
            LEFT JOIN batches b ON b.supplier_id = s.id
            GROUP BY s.id
            HAVING debt > 0
            ORDER BY debt DESC
        """).fetchall()

        self.payable_table.setRowCount(len(s_rows))
        for i, r in enumerate(s_rows):
            self.payable_table.setItem(i, 0, QTableWidgetItem(r[1]))
            debt_item = QTableWidgetItem(f"¥{r[4]:.0f}")
            debt_item.setForeground(QColor("#F57C00"))
            self.payable_table.setItem(i, 1, debt_item)
            batch_count = conn.execute(
                "SELECT COUNT(*) FROM batches WHERE supplier_id=?", (r[0],)
            ).fetchone()[0]
            self.payable_table.setItem(i, 2, QTableWidgetItem(str(batch_count)))
            contact = " | ".join(filter(None, [r[2] or "", r[3] or ""]))
            self.payable_table.setItem(i, 3, QTableWidgetItem(contact))
            pay_btn = QPushButton("付款")
            pay_btn.setObjectName("tableActionOrange")
            pay_btn.clicked.connect(lambda checked, sid=r[0]: self._on_finance_pay(sid))
            self.payable_table.setCellWidget(i, 4, pay_btn)
        self.payable_table.resizeColumnsToContents()

        conn.close()

        # 同时刷新流水记录和筛选对象列表
        self._load_payment_object_filter()
        self.refresh_payment_flow()

    def _load_payment_object_filter(self):
        """加载筛选对象下拉框（客户+上游）"""
        self.payment_object_filter.clear()
        self.payment_object_filter.addItem("全部对象", None)
        customers = get_all_customers()
        for c in customers:
            self.payment_object_filter.addItem(f"客户: {c['name']}", ("customer", c["id"]))
        suppliers = get_all_suppliers()
        for s in suppliers:
            self.payment_object_filter.addItem(f"上游: {s['name']}", ("supplier", s["id"]))

    def refresh_payment_flow(self):
        """刷新收付款流水表格"""
        # 获取筛选条件
        pay_type = self.payment_type_filter.currentText()
        if pay_type == "收款":
            pay_type = "receivable"
        elif pay_type == "付款":
            pay_type = "payable"
        else:
            pay_type = None

        object_data = self.payment_object_filter.currentData()
        customer_id = None
        supplier_id = None
        if object_data:
            if object_data[0] == "customer":
                customer_id = object_data[1]
            elif object_data[0] == "supplier":
                supplier_id = object_data[1]

        date_from = self.payment_date_from.date().toString("yyyy-MM-dd")
        date_to = self.payment_date_to.date().toString("yyyy-MM-dd")

        # 获取数据
        payments = get_all_payments_with_details(pay_type, customer_id, supplier_id, date_from, date_to)

        self.payment_flow_table.setRowCount(len(payments))
        total_receive = 0
        total_pay = 0

        for i, p in enumerate(payments):
            self.payment_flow_table.setItem(i, 0, QTableWidgetItem(str(p["id"])))
            self.payment_flow_table.setItem(i, 1, QTableWidgetItem(p.get("pay_date", "")))

            type_text = "收款" if p.get("type") == "receivable" else "付款"
            type_item = QTableWidgetItem(type_text)
            type_item.setForeground(QColor("#388E3C") if p.get("type") == "receivable" else QColor("#F57C00"))
            self.payment_flow_table.setItem(i, 2, type_item)

            amount_item = QTableWidgetItem(f"¥{p.get('amount', 0):.0f}")
            amount_item.setForeground(QColor("#388E3C") if p.get("type") == "receivable" else QColor("#F57C00"))
            self.payment_flow_table.setItem(i, 3, amount_item)

            self.payment_flow_table.setItem(i, 4, QTableWidgetItem(p.get("method", "")))

            # 关联对象
            obj_name = p.get("customer_name", "") or p.get("supplier_name", "")
            if p.get("type") == "receivable" and obj_name:
                obj_name = f"客户: {obj_name}"
            elif p.get("type") == "payable" and obj_name:
                obj_name = f"上游: {obj_name}"
            self.payment_flow_table.setItem(i, 5, QTableWidgetItem(obj_name))

            self.payment_flow_table.setItem(i, 6, QTableWidgetItem(p.get("remark", "") or ""))

            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)

            edit_btn = QPushButton("修改")
            edit_btn.setObjectName("tableActionPrimary")
            edit_btn.clicked.connect(lambda checked, pid=p["id"]: self._on_edit_payment(pid))
            btn_layout.addWidget(edit_btn)

            del_btn = QPushButton("删除")
            del_btn.setObjectName("tableActionDanger")
            del_btn.clicked.connect(lambda checked, pid=p["id"]: self._on_delete_payment(pid))
            btn_layout.addWidget(del_btn)

            self.payment_flow_table.setCellWidget(i, 7, btn_widget)

            if p.get("type") == "receivable":
                total_receive += p.get("amount", 0)
            else:
                total_pay += p.get("amount", 0)

        self.payment_flow_table.resizeColumnsToContents()
        self.payment_flow_stats.setText(
            f"共 {len(payments)} 条记录 | 收款合计: ¥{total_receive:.0f} | 付款合计: ¥{total_pay:.0f}"
        )

    def _on_edit_payment(self, payment_id):
        """修改收付款记录（两次确认）"""
        payment = get_payment_by_id(payment_id)
        if not payment:
            QMessageBox.warning(self, "错误", "无法获取记录信息")
            return

        # 第一次确认：显示原记录信息
        type_text = "收款" if payment["type"] == "receivable" else "付款"
        obj_name = payment.get("customer_name", "") or payment.get("supplier_name", "")
        info = f"原记录信息:\n\n类型: {type_text}\n金额: ¥{payment['amount']:.0f}\n日期: {payment['pay_date']}\n方式: {payment['method']}\n关联对象: {obj_name}\n备注: {payment['remark'] or '无'}\n\n是否要修改此记录？"
        reply = QMessageBox.question(self, "确认修改 - 第一步", info, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        # 弹出编辑对话框
        dlg = PaymentEditDialog(self, payment)
        if dlg.exec():
            new_data = dlg.get_data()
            if new_data["amount"] <= 0:
                QMessageBox.warning(self, "提示", "金额必须大于 0")
                return

            # 第二次确认：显示修改内容对比
            changes = []
            if payment["amount"] != new_data["amount"]:
                changes.append(f"金额: ¥{payment['amount']:.0f} → ¥{new_data['amount']:.0f}")
            if payment["pay_date"] != new_data["pay_date"]:
                changes.append(f"日期: {payment['pay_date']} → {new_data['pay_date']}")
            if payment["method"] != new_data["method"]:
                changes.append(f"方式: {payment['method']} → {new_data['method']}")
            if (payment["remark"] or "") != new_data["remark"]:
                changes.append(f"备注: {payment['remark'] or '无'} → {new_data['remark'] or '无'}")

            if not changes:
                QMessageBox.information(self, "提示", "没有任何修改")
                return

            confirm_text = f"确认以下修改:\n\n" + "\n".join(changes) + "\n\n修改后将自动更新关联数据（报价已收金额/供应商欠款）。\n是否确认修改？"
            reply2 = QMessageBox.question(self, "确认修改 - 第二步", confirm_text, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply2 != QMessageBox.StandardButton.Yes:
                return

            # 执行修改
            success, msg = update_payment(payment_id, new_data["amount"], new_data["pay_date"], new_data["method"], new_data["remark"])
            if success:
                QMessageBox.information(self, "成功", "修改成功！关联数据已同步更新。")
                self.refresh_payment_flow()
                self.refresh_finance()
                self.refresh_records()
            else:
                QMessageBox.warning(self, "失败", msg)

    def _on_delete_payment(self, payment_id):
        """删除收付款记录（两次确认 + 回滚）"""
        payment = get_payment_by_id(payment_id)
        if not payment:
            QMessageBox.warning(self, "错误", "无法获取记录信息")
            return

        # 第一次确认：显示记录信息
        type_text = "收款" if payment["type"] == "receivable" else "付款"
        obj_name = payment.get("customer_name", "") or payment.get("supplier_name", "")
        info = f"即将删除的记录:\n\n类型: {type_text}\n金额: ¥{payment['amount']:.0f}\n日期: {payment['pay_date']}\n方式: {payment['method']}\n关联对象: {obj_name}\n备注: {payment['remark'] or '无'}\n\n删除后将自动回滚关联数据。\n是否继续？"
        reply = QMessageBox.question(self, "确认删除 - 第一步", info, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        # 第二次确认：显示影响范围
        if payment["type"] == "receivable" and payment.get("quote_id"):
            impact = f"影响范围:\n• 报价记录 #{payment['quote_id']} 的已收金额将减少 ¥{payment['amount']:.0f}\n• 若已收金额不足，订单状态可能从「已收款」回退为「已出库」"
        elif payment["type"] == "payable" and payment.get("supplier_id"):
            impact = f"影响范围:\n• 上游供应商「{obj_name}」的欠款将增加 ¥{payment['amount']:.0f}"
        else:
            impact = "此记录无直接关联数据，删除后仅影响流水统计。"

        confirm_text = f"⚠️ 最终确认\n\n{impact}\n\n此操作不可撤销！\n是否确认删除？"
        reply2 = QMessageBox.question(self, "确认删除 - 第二步", confirm_text, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply2 != QMessageBox.StandardButton.Yes:
            return

        # 执行删除
        success, msg, affected = delete_payment(payment_id)
        if success:
            QMessageBox.information(self, "成功", "删除成功！关联数据已回滚。")
            self.refresh_payment_flow()
            self.refresh_finance()
            self.refresh_records()
        else:
            QMessageBox.warning(self, "失败", msg)

    def _on_finance_receive(self, customer_id):
        """收款操作（带预览确认）"""
        from src.models.database import get_connection
        conn = get_connection()
        unpaid = conn.execute("""
            SELECT id, quote_price, quote_quantity, received_amount,
                   quote_price * quote_quantity - received_amount as remaining
            FROM quotes
            WHERE customer_id=? AND status IN ('已报价','已出库','待确认')
            AND quote_price * quote_quantity > received_amount
            ORDER BY quote_date ASC
        """, (customer_id,)).fetchall()
        total_pending = sum(r[4] for r in unpaid)
        conn.close()

        if not unpaid:
            QMessageBox.information(self, "提示", "该客户没有待收款项")
            return

        # 弹出收款对话框（带预览）
        dlg = PaymentDialog(self, title="收款", pay_type="receivable", preview_pending=total_pending)
        if dlg.exec():
            data = dlg.get_data()
            if data["amount"] <= 0:
                QMessageBox.warning(self, "提示", "请输入收款金额")
                return

            # 预览确认：显示收款后的剩余待收
            remaining_after = total_pending - data["amount"]
            preview_text = f"收款确认:\n\n本次收款: ¥{data['amount']:.0f}\n当前待收: ¥{total_pending:.0f}\n收款后剩余待收: ¥{remaining_after:.0f}\n\n收款方式: {data['method']}\n收款日期: {data['pay_date']}"
            if remaining_after < 0:
                preview_text += "\n\n⚠️ 注意: 收款金额超过待收金额，将自动结清所有欠款。"

            reply = QMessageBox.question(self, "确认收款", preview_text, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

            # 批量收款在同一个事务中执行，保证原子性
            conn = get_connection()
            try:
                remaining = data["amount"]
                for q in unpaid:
                    if remaining <= 0:
                        break
                    qid, _, _, _, pending = q
                    apply_amount = min(remaining, pending)
                    _add_payment_raw(
                        conn,
                        quote_id=qid,
                        customer_id=customer_id,
                        pay_type="receivable",
                        amount=apply_amount,
                        pay_date=data["pay_date"],
                        method=data["method"],
                        remark=data["remark"],
                    )
                    remaining -= apply_amount
                conn.commit()
                QMessageBox.information(self, "成功", f"收款 ¥{data['amount']:.2f} 已记录！")
            except Exception as e:
                conn.rollback()
                QMessageBox.critical(self, "收款失败", f"收款操作失败: {str(e)}")
                return
            finally:
                conn.close()
            self.refresh_finance()
            self.refresh_records()

    def _on_finance_pay(self, supplier_id):
        """付款操作"""
        dlg = PaymentDialog(self, title="付款", pay_type="payable")
        if dlg.exec():
            data = dlg.get_data()
            if data["amount"] <= 0:
                QMessageBox.warning(self, "提示", "请输入付款金额")
                return
            add_payment(
                supplier_id=supplier_id,
                pay_type="payable",
                amount=data["amount"],
                pay_date=data["pay_date"],
                method=data["method"],
                remark=data["remark"],
            )
            QMessageBox.information(self, "成功", f"付款 ¥{data['amount']:.2f} 已记录！")
            self.refresh_finance()

    # -------------------------------------------------------
    # Tab 构建
    # -------------------------------------------------------
    def _build_customer_tab(self):
        self.customer_tab = CustomerTab(self)
        return self.customer_tab

    def _build_records_tab(self):
        self.record_tab = RecordTab(self)
        return self.record_tab

    def on_search(self, text):
        self.product_tab.on_search(text)

    # -------------------------------------------------------
    # 上游管理
    # -------------------------------------------------------
    def _build_supplier_tab(self):
        self.supplier_tab = SupplierTab(self)
        return self.supplier_tab

    # -------------------------------------------------------
    # 报价记录（委托到 RecordTab）
    # -------------------------------------------------------
    def refresh_records(self):
        self.record_tab.refresh_records()

    def on_edit_quote(self):
        self.record_tab.on_edit_quote()

    def on_delete_quote(self):
        self.record_tab.on_delete_quote()

    # -------------------------------------------------------
    # 导入 Word（委托到 RecordTab）
    # -------------------------------------------------------
    def on_import_word(self):
        self.record_tab.on_import_word()

    # -------------------------------------------------------
    # Skill 3: 智能跟单提醒（委托到 RecordTab）
    # -------------------------------------------------------
    def on_follow_up(self):
        self.record_tab.on_follow_up()

    # -------------------------------------------------------
    # Skill 4: 月度经营报告（委托到 RecordTab）
    # -------------------------------------------------------
    def on_monthly_report(self):
        self.record_tab.on_monthly_report()

    # -------------------------------------------------------
    # Skill 6: 远程诊断助手
    # -------------------------------------------------------
    def on_remote_diagnose(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("🔧 远程诊断助手")
        dlg.setMinimumSize(650, 550)
        layout = QVBoxLayout(dlg)

        # 搜索栏
        search_row = QHBoxLayout()
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("输入症状关键词（如：蓝屏、开不了机、WiFi断连、风扇噪音大）")
        search_btn = QPushButton("搜索")
        search_row.addWidget(search_edit)
        search_row.addWidget(search_btn)
        layout.addLayout(search_row)

        # 快捷按钮
        quick_row = QHBoxLayout()
        for key_info in get_all_diagnose_keys():
            btn = QPushButton(key_info["title"])
            btn.setObjectName("diagnoseOptionBtn")
            btn.clicked.connect(lambda checked, k=key_info["key"]: self._show_diagnose_steps(dlg, k))
            quick_row.addWidget(btn)
        quick_row.addStretch()
        layout.addLayout(quick_row)

        # 结果区域
        result_text = QTextEdit()
        result_text.setReadOnly(True)
        result_text.setPlaceholderText("选择一个故障类型开始排查...")
        result_text.setObjectName("reportText")
        layout.addWidget(result_text)

        def do_search():
            kw = search_edit.text().strip()
            if not kw:
                return
            results = search_diagnose(kw)
            if results:
                lines = [f"找到 {len(results)} 个匹配项：\n"]
                for r in results:
                    lines.append(f"• {r['title']}（{r['match_type']}）")
                lines.append("\n点击上方快捷按钮开始排查")
                result_text.setPlainText("\n".join(lines))
            else:
                result_text.setPlainText(f"未找到与「{kw}」相关的诊断流程。\n\n当前支持的故障类型：\n" +
                                         "\n".join(f"• {k['title']}" for k in get_all_diagnose_keys()))

        search_btn.clicked.connect(do_search)
        search_edit.returnPressed.connect(do_search)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)
        dlg.exec()

    def _show_diagnose_steps(self, parent_dlg, key):
        tree = get_diagnose_tree(key)
        if not tree:
            return

        dlg = QDialog(parent_dlg)
        dlg.setWindowTitle(f"🔧 {tree['title']}")
        dlg.setMinimumSize(600, 450)
        layout = QVBoxLayout(dlg)

        title = QLabel(tree["title"])
        title.setObjectName("sectionTitleBlue")
        layout.addWidget(title)

        result_text = QTextEdit()
        result_text.setReadOnly(True)
        result_text.setObjectName("reportText")
        layout.addWidget(result_text)

        selected_path = []

        def show_step(step_idx):
            if step_idx >= len(tree["steps"]):
                return
            step = tree["steps"][step_idx]
            result_text.append(f"\n❓ {step['q']}\n")

            # 清除旧按钮
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                if item.widget() and isinstance(item.widget(), QPushButton) and item.widget().text() not in ("关闭",):
                    item.widget().deleteLater()

            for opt_name, opt_data in step["options"].items():
                btn = QPushButton(f"→ {opt_name}")
                btn.setObjectName("diagnoseOptionBtn")
                btn.clicked.connect(lambda checked, on=opt_name, od=opt_data, si=step_idx: handle_option(on, od, si))
                layout.insertWidget(layout.count() - 1, btn)

        def handle_option(opt_name, opt_data, step_idx):
            selected_path.append(opt_name)
            result_text.append(f"  ✅ {opt_name}")

            if "action" in opt_data:
                result_text.append(f"\n📋 处理方案:\n{opt_data['action']}\n")

                # 生成报告按钮
                report_btn = QPushButton("📄 生成诊断报告")
                report_btn.setObjectName("successBtn")
                report_btn.clicked.connect(lambda: self._save_diagnose_report(key, selected_path))
                layout.insertWidget(layout.count() - 1, report_btn)

            elif "next" in opt_data:
                show_step(opt_data["next"])

        show_step(0)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        dlg.exec()

    def _save_diagnose_report(self, key, selected_path):
        report = generate_diagnose_report(key, selected_path)
        # 复制到剪贴板
        clipboard = QApplication.clipboard()
        clipboard.setText(report)
        QMessageBox.information(self, "诊断报告", f"报告已复制到剪贴板！\n\n{report}")

    # -------------------------------------------------------
    # Skill: 价格异动哨兵
    # -------------------------------------------------------
    def on_price_diff(self):
        """价格异动哨兵 - 在导入Word时自动对比"""
        snapshots = get_all_snapshots()
        if not snapshots:
            QMessageBox.information(self, "价格异动", "暂无历史价格快照。\n导入 Word 价格表时会自动保存快照。")
            return

        latest = get_latest_snapshot()
        if not latest:
            QMessageBox.information(self, "价格异动", "无法获取最新快照")
            return

        # 显示快照列表
        items_text = "\n".join([f"  {s['import_date']} | {s['item_count']} 条机型" for s in snapshots[:10]])
        QMessageBox.information(self, "价格快照历史", f"已有 {len(snapshots)} 个快照：\n\n{items_text}\n\n下次导入 Word 价格表时将自动对比异动。")

    # -------------------------------------------------------
    # Skill: 报价决策助手
    # -------------------------------------------------------
    def on_quote_assist(self):
        """报价决策助手"""
        dlg = QDialog(self)
        dlg.setWindowTitle("报价决策助手")
        dlg.setMinimumWidth(450)
        layout = QFormLayout(dlg)

        series_edit = QLineEdit()
        series_edit.setPlaceholderText("输入系列名称（如 Y7000P）")
        cpu_edit = QLineEdit()
        cpu_edit.setPlaceholderText("CPU（选填）")
        price_spin = QSpinBox()
        price_spin.setRange(0, 999999)
        price_spin.setPrefix("¥ ")
        customer_edit = QLineEdit()
        customer_edit.setPlaceholderText("客户名称（选填）")

        layout.addRow("系列:", series_edit)
        layout.addRow("CPU:", cpu_edit)
        layout.addRow("进货价:", price_spin)
        layout.addRow("客户:", customer_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addRow(buttons)

        if dlg.exec():
            series = series_edit.text().strip()
            if not series:
                QMessageBox.warning(self, "提示", "请输入系列名称")
                return
            suggestion = suggest_price(
                series=series,
                cpu=cpu_edit.text().strip(),
                purchase_price=price_spin.value(),
                customer_name=customer_edit.text().strip(),
            )

            conf_text = {"high": "高", "medium": "中", "low": "低"}[suggestion["confidence"]]
            text = (
                f"建议报价范围: ¥{suggestion['suggested_min']:,.0f} ~ ¥{suggestion['suggested_max']:,.0f}\n"
                f"建议中间价: ¥{suggestion['suggested_mid']:,.0f}\n"
                f"利润率: {suggestion['margin_at_mid']:.1f}%\n"
                f"置信度: {conf_text}\n\n"
                f"依据: {suggestion['basis']}"
            )
            if suggestion.get("history"):
                h = suggestion["history"]
                text += f"\n\n历史报价: {h['total_quotes']} 条\n区间: ¥{h['min_price']:,.0f} ~ ¥{h['max_price']:,.0f}\n均价: ¥{h['avg_price']:,.0f}"

            QMessageBox.information(self, "报价建议", text)

    # -------------------------------------------------------
    # Skill: 出库一条龙
    # -------------------------------------------------------
    def on_shipment_flow(self):
        self.record_tab.on_shipment_flow()

    # -------------------------------------------------------
    # 价格异动报告（Skill 2）
    # -------------------------------------------------------
    def _show_diff_report(self, diff):
        """弹出价格异动报告对话框"""
        dlg = QDialog(self)
        dlg.setWindowTitle("📊 价格异动报告")
        dlg.setMinimumSize(700, 500)
        layout = QVBoxLayout(dlg)

        # 标题
        title = QLabel(f"📊 价格异动报告（{diff['old_date']} → {diff['new_date']}）")
        title.setObjectName("sectionTitleBlue")
        layout.addWidget(title)

        # 摘要
        summary = QLabel(diff["summary"])
        summary.setObjectName("summaryLabel")
        layout.addWidget(summary)

        # Tab 切换
        tabs = QTabWidget()

        # === 新增 ===
        if diff["added"]:
            add_tab = QWidget()
            add_layout = QVBoxLayout(add_tab)
            add_table = QTableWidget()
            add_table.setAlternatingRowColors(True)
            add_table.setColumnCount(6)
            add_table.setHorizontalHeaderLabels(["系列", "CPU", "内存", "硬盘", "显卡", "备注"])
            add_table.setRowCount(len(diff["added"]))
            for i, item in enumerate(diff["added"]):
                add_table.setItem(i, 0, QTableWidgetItem(item.get("series", "")))
                add_table.setItem(i, 1, QTableWidgetItem(item.get("cpu", "")))
                add_table.setItem(i, 2, QTableWidgetItem(item.get("ram", "")))
                add_table.setItem(i, 3, QTableWidgetItem(item.get("storage", "")))
                add_table.setItem(i, 4, QTableWidgetItem(item.get("gpu", "")))
                add_table.setItem(i, 5, QTableWidgetItem(item.get("note", "")))
            add_table.horizontalHeader().setStretchLastSection(True)
            add_table.resizeColumnsToContents()
            add_layout.addWidget(add_table)
            tabs.addTab(add_tab, f"🔵 新增 ({len(diff['added'])})")

        # === 下架 ===
        if diff["removed"]:
            rm_tab = QWidget()
            rm_layout = QVBoxLayout(rm_tab)
            rm_label = QLabel("⚠️ 以下机型在新价格表中已下架，请检查是否有库存需要尽快出货：")
            rm_label.setObjectName("dangerSummaryLabel")
            rm_layout.addWidget(rm_label)
            rm_table = QTableWidget()
            rm_table.setAlternatingRowColors(True)
            rm_table.setColumnCount(6)
            rm_table.setHorizontalHeaderLabels(["系列", "CPU", "内存", "硬盘", "显卡", "备注"])
            rm_table.setRowCount(len(diff["removed"]))
            for i, item in enumerate(diff["removed"]):
                rm_table.setItem(i, 0, QTableWidgetItem(item.get("series", "")))
                rm_table.setItem(i, 1, QTableWidgetItem(item.get("cpu", "")))
                rm_table.setItem(i, 2, QTableWidgetItem(item.get("ram", "")))
                rm_table.setItem(i, 3, QTableWidgetItem(item.get("storage", "")))
                rm_table.setItem(i, 4, QTableWidgetItem(item.get("gpu", "")))
                rm_table.setItem(i, 5, QTableWidgetItem(item.get("note", "")))
            rm_table.horizontalHeader().setStretchLastSection(True)
            rm_table.resizeColumnsToContents()
            rm_layout.addWidget(rm_table)
            tabs.addTab(rm_tab, f"⚠️ 下架 ({len(diff['removed'])})")

        layout.addWidget(tabs)

        # 底部按钮
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dlg.accept)
        layout.addWidget(buttons)

        dlg.exec()

    # -------------------------------------------------------
    # 群发图片
    # -------------------------------------------------------
    def on_broadcast(self):
        self.record_tab.on_broadcast()

    # -------------------------------------------------------
    # 群发图片（委托到 RecordTab）
    # -------------------------------------------------------
    def on_export_records_excel(self):
        self.record_tab.on_export_records_excel()

    def on_export_excel(self):
        self.record_tab.on_export_excel()

    def on_export_json(self):
        """导出全量数据为 JSON 格式"""
        try:
            from src.utils.json_export import export_all_to_json
            from src.models import database as db
            
            output_path = export_all_to_json(db)
            QMessageBox.information(
                self, "导出成功",
                f"数据已成功导出为 JSON 格式！\n\n文件位置: {output_path}\n\n可用于数据备份或迁移到其他电脑。"
            )
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出时发生错误:\n{str(e)}")

    def on_import_json(self):
        """从 JSON 文件导入数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 JSON 备份文件", "",
            "JSON 文件 (*.json);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        # 文件大小校验（最大 50 MB）
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024:
            QMessageBox.warning(self, "文件过大",
                f"文件大小 {file_size / (1024*1024):.1f} MB 超过限制（最大 50 MB）")
            return
        
        from src.utils.json_export import validate_json_file, import_from_json
        from src.models import database as db
        
        valid, message, stats = validate_json_file(file_path)
        if not valid:
            QMessageBox.warning(self, "文件无效", message)
            return
        
        reply = QMessageBox.question(
            self, "确认导入",
            f"即将导入以下数据:\n\n"
            f"• 机型: {stats.get('products', 0)} 条\n"
            f"• 批次: {stats.get('batches', 0)} 条\n"
            f"• 客户: {stats.get('customers', 0)} 条\n"
            f"• 报价: {stats.get('quotes', 0)} 条\n\n"
            f"是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message, import_stats = import_from_json(file_path, db)
            
            if success:
                self.product_tab.refresh_product_list()
                self.customer_tab.refresh_customer_list()
                self.supplier_tab.refresh_supplier_list()
                self.refresh_records()
                
                QMessageBox.information(
                    self, "导入成功",
                    f"数据导入完成！\n\n"
                    f"• 机型: {import_stats.get('products', 0)} 条\n"
                    f"• 批次: {import_stats.get('batches', 0)} 条\n"
                    f"• 客户: {import_stats.get('customers', 0)} 条\n"
                    f"• 报价: {import_stats.get('quotes', 0)} 条\n\n"
                    f"注意: 如果导入的数据与现有数据重复，可能会产生重复记录。"
                )
            else:
                QMessageBox.critical(self, "导入失败", message)

    def on_show_logs(self):
        """显示操作日志"""
        dlg = OperationLogDialog(self)
        dlg.exec()


def main():
    app = QApplication(sys.argv)
    sys.excepthook = _global_excepthook
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()