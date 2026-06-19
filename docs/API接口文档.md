# 调货助手 API 接口文档

> **版本**: v1.06
> **最后更新**: 2026-06-15
> **技术栈**: Python 3.x + PyQt6 + SQLite

---

## 目录

1. [数据库模块 (database.py)](#1-数据库模块)
2. [JSON 导入导出 (json_export.py)](#2-json-导入导出)
3. [Excel 导出 (excel_export.py)](#3-excel-导出)
4. [Word 解析 (word_parser.py)](#4-word-解析)
5. [图片生成 (image_gen.py)](#5-图片生成)
6. [智能跟单 (follow_up.py)](#6-智能跟单)
7. [月度报告 (monthly_report.py)](#7-月度报告)
8. [价格异动 (price_diff.py)](#8-价格异动)
9. [报价助手 (quote_assist.py)](#9-报价助手)
10. [远程诊断 (remote_diagnose.py)](#10-远程诊断)
11. [出库流程 (shipment_flow.py)](#11-出库流程)

---

## 1. 数据库模块

**文件**: `src/models/database.py`

### 初始化

#### `init_db()`
初始化数据库，创建所有表结构。

```python
from src.models.database import init_db
init_db()
```

#### `get_connection()`
获取数据库连接（启用 WAL 模式和外键约束）。

```python
from src.models.database import get_connection
conn = get_connection()
```

#### `backup_database()`
自动备份数据库，保留最近 7 个备份。

```python
from src.models.database import backup_database
success, message = backup_database()
```

---

### 机型管理

#### `add_product(series, cpu, ram, storage, gpu, screen, note)`
添加新机型。

```python
pid = add_product(
    series="小新Pro16",
    cpu="Ultra5-225",
    ram="32G",
    storage="1T",
    gpu="集成",
    screen="16英寸",
    note="新品"
)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| series | str | 系列名称 |
| cpu | str | CPU 型号 |
| ram | str | 内存规格 |
| storage | str | 硬盘规格 |
| gpu | str | 显卡型号 |
| screen | str | 屏幕尺寸 |
| note | str | 备注信息 |

**返回**: `int` - 新机型 ID

---

#### `update_product(pid, series, cpu, ram, storage, gpu, screen, note)`
更新机型信息。

```python
update_product(1, "小新Pro16", "Ultra7-255", "32G", "1T", "集成", "16英寸", "更新")
```

---

#### `delete_product(pid)`
删除机型（级联删除关联批次和报价）。

```python
delete_product(1)
```

---

#### `search_products(keyword)`
搜索机型（支持系列、CPU、备注关键词）。

```python
products = search_products("小新")
```

**返回**: `list[dict]` - 匹配的机型列表

---

#### `get_all_products()`
获取所有机型列表。

```python
products = get_all_products()
```

---

### 批次管理

#### `add_batch(product_id, purchase_price, quantity, remaining, date_str, remark, supplier_id, sn_list)`
添加批次库存。

```python
bid = add_batch(
    product_id=1,
    purchase_price=4500,
    quantity=10,
    remaining=10,
    date_str="2024-01-15",
    remark="含税",
    supplier_id=1,
    sn_list="PF123456,PF789012"
)
```

**返回**: `int` - 新批次 ID

---

#### `get_batches(product_id)`
获取指定机型的所有批次。

```python
batches = get_batches(1)
```

**返回**: `list[dict]` - 批次列表

---

#### `update_batch_remaining(batch_id, new_remaining)`
更新批次剩余数量。

```python
update_batch_remaining(1, 5)
```

---

#### `deduct_batch_remaining(batch_id, quantity)`
扣减批次库存。

```python
success, message = deduct_batch_remaining(1, 2)
```

**返回**: `tuple(bool, str)` - (是否成功, 消息)

---

#### `get_total_remaining(product_id)`
获取机型总库存。

```python
total = get_total_remaining(1)
```

---

#### `delete_batch(batch_id)`
删除批次（级联删除关联报价和付款）。

```python
delete_batch(1)
```

---

### 客户管理

#### `add_customer(name, wechat, qq, phone, note)`
添加客户。

```python
cid = add_customer(
    name="张三",
    wechat="zhangsan",
    phone="13800138000"
)
```

**返回**: `int` - 新客户 ID

---

#### `search_customers(keyword)`
搜索客户。

```python
customers = search_customers("张")
```

---

#### `get_all_customers()`
获取所有客户。

```python
customers = get_all_customers()
```

---

#### `delete_customer_cascade(customer_id)`
级联删除客户及其关联数据。

```python
result = delete_customer_cascade(1)
# {"quotes": 5, "payments": 3}
```

---

### 上游管理

#### `add_supplier(name, wechat, qq, phone, note)`
添加上游供应商。

```python
sid = add_supplier(name="李四", phone="13900139000")
```

**返回**: `int` - 新上游 ID

---

#### `search_suppliers(keyword)`
搜索上游。

---

#### `get_all_suppliers()`
获取所有上游。

---

#### `delete_supplier_cascade(supplier_id)`
级联删除上游（批次的上游字段设为 NULL）。

```python
result = delete_supplier_cascade(1)
# {"batches": 3, "payments": 2}
```

---

### 报价记录

#### `add_quote(batch_id, customer_id, quote_price, quote_quantity, quote_date, remark, paid, status, received_amount, sn_list)`
添加报价记录。

```python
add_quote(
    batch_id=1,
    customer_id=1,
    quote_price=5000,
    quote_quantity=2,
    quote_date="2024-01-20",
    status="待确认",
    sn_list="SN001,SN002"
)
```

---

#### `update_quote(quote_id, batch_id, customer_id, quote_price, quote_quantity, quote_date, remark, paid, sn_list)`
更新报价记录。

---

#### `delete_quote(quote_id)`
删除报价（级联删除付款记录）。

---

#### `get_quote_by_id(quote_id)`
获取报价详情（含机型、客户、批次信息）。

```python
quote = get_quote_by_id(1)
# {"id": 1, "series": "小新Pro16", "customer_name": "张三", ...}
```

---

#### `search_quotes(keyword, date_from, date_to, customer_id)`
高级搜索报价记录。

```python
quotes = search_quotes(
    keyword="小新",
    date_from="2024-01-01",
    date_to="2024-12-31",
    customer_id=1
)
```

**返回**: `list[dict]` - 匹配的报价列表（含完整关联信息）

---

#### `update_quote_status(quote_id, new_status)`
更新报价状态。

```python
update_quote_status(1, "已报价")
update_quote_status(1, "已出库")
update_quote_status(1, "已收款")
update_quote_status(1, "已取消")
```

**状态流转**: `待确认` → `已报价` → `已出库` → `已收款` / `已取消`

---

### 收付款管理

#### `add_payment(quote_id, customer_id, supplier_id, pay_type, amount, pay_date, method, remark)`
添加收款/付款记录。

```python
# 收款
add_payment(
    quote_id=1,
    customer_id=1,
    pay_type="receivable",
    amount=5000,
    pay_date="2024-01-25",
    method="微信"
)

# 付款
add_payment(
    supplier_id=1,
    pay_type="payable",
    amount=4500,
    pay_date="2024-01-15",
    method="转账"
)
```

---

#### `get_payments(quote_id, customer_id, supplier_id)`
查询付款记录。

```python
payments = get_payments(customer_id=1)
```

---

#### `get_customer_balance(customer_id)`
获取客户应收余额。

```python
balance = get_customer_balance(1)  # 单个客户
total = get_customer_balance()     # 所有客户总计
```

---

#### `get_supplier_payable(supplier_id)`
获取上游应付余额。

```python
payable = get_supplier_payable(1)  # 单个上游
total = get_supplier_payable()     # 所有上游总计
```

---

#### `get_customer_statement(customer_id, date_from, date_to)`
获取客户对账单。

```python
statements = get_customer_statement(1, "2024-01-01", "2024-12-31")
```

---

### 统计查询

#### `get_customer_stats(customer_id)`
获取客户统计信息。

```python
stats = get_customer_stats(1)
# {"total_quotes": 10, "total_amount": 50000, "total_profit": 5000}
```

---

#### `get_customer_quotes(customer_id)`
获取客户购买历史。

```python
history = get_customer_quotes(1)
```

---

## 2. JSON 导入导出

**文件**: `src/utils/json_export.py`

### `export_all_to_json(db_module, output_path)`
导出所有数据为 JSON 格式。

```python
from src.utils.json_export import export_all_to_json
from src.models import database

path = export_all_to_json(database)
# 导出到桌面: 调货助手备份_20240115_120000.json
```

**参数**:
- `db_module`: 数据库模块
- `output_path`: 输出路径（可选，默认桌面）

**返回**: `str` - 输出文件路径

---

### `import_from_json(json_path, db_module)`
从 JSON 文件导入数据。

```python
from src.utils.json_export import import_from_json
from src.models import database

success, message, stats = import_from_json("备份文件.json", database)
if success:
    print(f"导入成功: {stats}")
    # {"products": 100, "batches": 50, "quotes": 200, ...}
```

**返回**: `tuple(bool, str, dict)` - (是否成功, 消息, 统计信息)

---

### `validate_json_file(json_path)`
验证 JSON 备份文件格式。

```python
from src.utils.json_export import validate_json_file

valid, message, stats = validate_json_file("备份文件.json")
```

---

## 3. Excel 导出

**文件**: `src/utils/excel_export.py`

### `export_quotes_to_excel(quotes, output_path)`
将报价记录导出为 Excel 文件。

```python
from src.utils.excel_export import export_quotes_to_excel
from src.models.database import search_quotes

quotes = search_quotes()
path = export_quotes_to_excel(quotes)
```

**功能特点**:
- 自动添加表头样式
- 毛利列着色（正数绿色、负数红色）
- 状态列着色标识
- 奇偶行交替背景色
- 底部汇总行

---

## 4. Word 解析

**文件**: `src/utils/word_parser.py`

### `parse_word_pricelist(filepath)`
解析上游价格 Word 文档。

```python
from src.utils.word_parser import parse_word_pricelist

products = parse_word_pricelist("上游价格表.docx")
# [{'series': '小新Pro16', 'cpu': 'Ultra5-225', 'ram': '32G', 'storage': '1T', ...}, ...]
```

**支持格式**:
- 微软 Office Word (.docx)
- WPS Office 格式
- 多种机型前缀自动识别
- CPU、内存、硬盘、显卡自动提取

---

### `preview_parse(filepath)`
预览解析结果。

```python
from src.utils.word_parser import preview_parse

rows, products = preview_parse("上游价格表.docx")
# rows: 用于表格展示的二维数组
# products: 完整的机型字典列表
```

**返回**: `tuple(list, list)` - (表格数据, 完整产品列表)

---

## 5. 图片生成

**文件**: `src/utils/image_gen.py`

### `generate_quote_image(products, output_path, rows_per_page)`
生成报价单图片。

```python
from src.utils.image_gen import generate_quote_image
from src.utils.word_parser import parse_word_pricelist

products = parse_word_pricelist("上游价格表.docx")
paths = generate_quote_image(products)
# 返回生成的图片路径列表
```

---

### `generate_single_quote_card(series, cpu, ram, storage, gpu, screen, note, customer_name, quote_price, output_path, quote_quantity, total_price)`
生成单机报价卡片（用于私聊发图）。

```python
from src.utils.image_gen import generate_single_quote_card

path = generate_single_quote_card(
    series="小新Pro16",
    cpu="Ultra5-225",
    ram="32G",
    storage="1T",
    customer_name="张三",
    quote_price=5500,
    quote_quantity=2,
    total_price=11000
)
```

---

## 6. 智能跟单

**文件**: `src/utils/follow_up.py`

### `get_stale_quotes(stale_days=3)`
获取需要跟进的报价记录。

```python
from src.utils.follow_up import get_stale_quotes

result = get_stale_quotes(3)
# {
#   "pending_confirm": [...],  # 待确认超过3天
#   "quoted_no_ship": [...],   # 已报价超过3天未出库
#   "shipped_no_pay": [...],   # 已出库超过3天未收款
#   "total": 5
# }
```

---

### `format_reminder_text(stale_quotes)`
格式化提醒文本。

```python
from src.utils.follow_up import format_reminder_text

text = format_reminder_text(result)
# "共有 5 条订单需要跟进：\n📋 待确认（超过 3 天）：2 条\n..."
```

---

## 7. 月度报告

**文件**: `src/utils/monthly_report.py`

### `get_monthly_report(year, month)`
生成月度经营报告。

```python
from src.utils.monthly_report import get_monthly_report

report = get_monthly_report(2024, 1)
# {
#   "year": 2024, "month": 1, "period": "2024年1月",
#   "order_count": 50, "total_revenue": 250000,
#   "total_profit": 25000, "collection_rate": 85.5,
#   "profit_margin": 10.0, "revenue_change": 15.2,
#   "top_products": [...], "slow_movers": [...]
# }
```

---

### `format_report_text(report)`
格式化报告文本。

```python
from src.utils.monthly_report import format_report_text

text = format_report_text(report)
```

---

## 8. 价格异动

**文件**: `src/utils/price_diff.py`

### `save_snapshot(products, import_date)`
保存价格表快照。

```python
from src.utils.price_diff import save_snapshot
from src.utils.word_parser import parse_word_pricelist

products = parse_word_pricelist("新价格表.docx")
snapshot_id, count = save_snapshot(products)
```

---

### `get_latest_snapshot(before_date)`
获取最近一次快照。

```python
from src.utils.price_diff import get_latest_snapshot

snapshot = get_latest_snapshot()
# {"snapshot_id": 1, "import_date": "2024-01-15", "items": [...], ...}
```

---

### `diff_snapshots(old_snapshot, new_items)`
对比两次快照，生成异动报告。

```python
from src.utils.price_diff import diff_snapshots, get_latest_snapshot

old = get_latest_snapshot()
new = parse_word_pricelist("最新价格表.docx")
diff = diff_snapshots(old, new)
# {"added": [...], "removed": [...], "summary": "新增 5 项、下架 2 项"}
```

---

### `get_all_snapshots()`
获取所有快照列表。

```python
from src.utils.price_diff import get_all_snapshots

snapshots = get_all_snapshots()
```

---

## 9. 报价助手

**文件**: `src/utils/quote_assist.py`

### `get_quote_history(series, cpu, ram, storage, gpu)`
查询机型历史报价。

```python
from src.utils.quote_assist import get_quote_history

history = get_quote_history(series="小新Pro16", cpu="Ultra5")
# {
#   "total_quotes": 10, "min_price": 4800, "max_price": 5500,
#   "avg_price": 5100, "recent_quotes": [...]
# }
```

---

### `get_customer_price_history(customer_name, series)`
查询客户历史成交价。

```python
from src.utils.quote_assist import get_customer_price_history

history = get_customer_price_history("张三", "小新Pro16")
```

---

### `suggest_price(series, cpu, ram, storage, gpu, purchase_price, customer_name)`
获取建议报价。

```python
from src.utils.quote_assist import suggest_price

suggestion = suggest_price(
    series="小新Pro16",
    cpu="Ultra5-225",
    purchase_price=4500,
    customer_name="张三"
)
# {
#   "suggested_min": 4800, "suggested_max": 5200, "suggested_mid": 5000,
#   "margin_at_mid": 11.1, "confidence": "high", "basis": "基于 10 条历史报价..."
# }
```

---

## 10. 远程诊断

**文件**: `src/utils/remote_diagnose.py`

### `DIAGNOSE_TREE`
内置诊断决策树。

```python
from src.utils.remote_diagnose import DIAGNOSE_TREE

# 支持的诊断类型:
# - "蓝屏": 蓝屏故障排查
# - "开不了机": 开机问题排查
# - "WiFi断连": WiFi 连接问题
# - "风扇噪音大": 风扇噪音问题
```

---

### `search_diagnose(keyword)`
搜索匹配的诊断流程。

```python
from src.utils.remote_diagnose import search_diagnose

results = search_diagnose("蓝屏")
# [{"key": "蓝屏", "title": "蓝屏（Blue Screen）排查", "match_type": "标题匹配"}]
```

---

### `get_all_diagnose_keys()`
获取所有可用的诊断项。

```python
from src.utils.remote_diagnose import get_all_diagnose_keys

keys = get_all_diagnose_keys()
# [{"key": "蓝屏", "title": "..."}, ...]
```

---

### `generate_diagnose_report(key, selected_options, custom_notes)`
生成诊断报告。

```python
from src.utils.remote_diagnose import generate_diagnose_report

report = generate_diagnose_report(
    key="蓝屏",
    selected_options=["有错误代码", "开机就蓝屏"],
    custom_notes="客户反映是更新驱动后出现"
)
```

---

## 11. 出库流程

**文件**: `src/utils/shipment_flow.py`

### `parse_sn_input(raw_text)`
解析 SN 输入文本（支持条码枪连续扫描）。

```python
from src.utils.shipment_flow import parse_sn_input

sns = parse_sn_input("SN001\nSN002\nSN003")
# ["SN001", "SN002", "SN003"]
```

---

### `validate_sn(sn)`
校验单个 SN 格式。

```python
from src.utils.shipment_flow import validate_sn

ok, msg = validate_sn("PF123456789")
# (True, "OK")
ok, msg = validate_sn("AB")
# (False, "SN 过短（2 位），至少需要 6 位")
```

---

### `validate_sn_list(sn_list, expected_count)`
批量校验 SN 列表。

```python
from src.utils.shipment_flow import validate_sn_list

result = validate_sn_list(["SN001", "SN002"], expected_count=2)
# {"valid": [...], "invalid": [], "count_ok": True, "message": "有效 SN: 2 条 | 数量匹配"}
```

---

### `check_sn_duplicates(sn_list, existing_sn_text)`
检查 SN 是否重复。

```python
from src.utils.shipment_flow import check_sn_duplicates

result = check_sn_duplicates(["SN001", "SN003"], existing_sn_text="SN001,SN002")
# {"duplicates": ["SN001"], "new_unique": ["SN003"], "message": "⚠️ 1 条 SN 已存在: SN001"}
```

---

### `generate_shipment_receipt(quote, sn_list, batch_info)`
生成出库确认单文本。

```python
from src.utils.shipment_flow import generate_shipment_receipt

receipt = generate_shipment_receipt(
    quote={
        "series": "小新Pro16", "cpu": "Ultra5",
        "customer_name": "张三", "quote_price": 5000, "quote_quantity": 2
    },
    sn_list=["SN001", "SN002"]
)
```

---

## 数据库表结构

### products (机型表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| series | TEXT | 系列 |
| cpu | TEXT | CPU |
| ram | TEXT | 内存 |
| storage | TEXT | 硬盘 |
| gpu | TEXT | 显卡 |
| screen | TEXT | 屏幕 |
| note | TEXT | 备注 |
| created_at | TIMESTAMP | 创建时间 |

### batches (批次表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| product_id | INTEGER | 机型 ID |
| purchase_price | REAL | 购入价 |
| quantity | INTEGER | 进货数量 |
| remaining | INTEGER | 剩余数量 |
| date | TEXT | 入库日期 |
| remark | TEXT | 备注 |
| supplier_id | INTEGER | 上游 ID |
| sn_list | TEXT | SN 列表 |
| created_at | TIMESTAMP | 创建时间 |

### customers (客户表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 名称 |
| wechat | TEXT | 微信 |
| qq | TEXT | QQ |
| phone | TEXT | 电话 |
| note | TEXT | 备注 |
| balance | REAL | 应收余额 |
| created_at | TIMESTAMP | 创建时间 |

### suppliers (上游表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 名称 |
| wechat | TEXT | 微信 |
| qq | TEXT | QQ |
| phone | TEXT | 电话 |
| note | TEXT | 备注 |
| balance | REAL | 应付余额 |
| created_at | TIMESTAMP | 创建时间 |

### quotes (报价表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| batch_id | INTEGER | 批次 ID |
| customer_id | INTEGER | 客户 ID |
| quote_price | REAL | 对外报价 |
| quote_quantity | INTEGER | 报价数量 |
| quote_date | TEXT | 报价日期 |
| remark | TEXT | 备注 |
| paid | TEXT | 是否打款 |
| status | TEXT | 状态 |
| received_amount | REAL | 已收金额 |
| sn_list | TEXT | SN 列表 |
| created_at | TIMESTAMP | 创建时间 |

### payments (收付款表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| quote_id | INTEGER | 报价 ID |
| customer_id | INTEGER | 客户 ID |
| supplier_id | INTEGER | 上游 ID |
| type | TEXT | 类型 |
| amount | REAL | 金额 |
| pay_date | TEXT | 日期 |
| method | TEXT | 方式 |
| remark | TEXT | 备注 |
| created_at | TIMESTAMP | 创建时间 |

### price_snapshots (价格快照表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| import_date | TEXT | 导入日期 |
| item_count | INTEGER | 条目数量 |
| created_at | TIMESTAMP | 创建时间 |

### price_snapshot_items (快照明细表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| snapshot_id | INTEGER | 快照 ID |
| series | TEXT | 系列 |
| cpu | TEXT | CPU |
| ram | TEXT | 内存 |
| storage | TEXT | 硬盘 |
| gpu | TEXT | 显卡 |
| note | TEXT | 备注 |
| norm_key | TEXT | 规范化匹配 key |

---

## 错误码

| 错误类型 | 说明 |
|----------|------|
| `sqlite3.IntegrityError` | 外键约束违反 |
| `FileNotFoundError` | 文件不存在 |
| `json.JSONDecodeError` | JSON 格式错误 |
| `docx.opc.exceptions.PackageNotFoundError` | Word 文件损坏 |

---

## 使用示例

### 完整报价流程

```python
from src.models.database import (
    init_db, add_product, add_batch, add_customer,
    add_quote, update_quote_status, add_payment
)
from src.utils.excel_export import export_quotes_to_excel
from src.utils.word_parser import parse_word_pricelist

# 1. 初始化
init_db()

# 2. 导入机型
products = parse_word_pricelist("上游价格表.docx")
for p in products:
    add_product(p["series"], p["cpu"], p["ram"], p["storage"], p["gpu"])

# 3. 添加批次
add_batch(product_id=1, purchase_price=4500, quantity=10, remaining=10, date_str="2024-01-15")

# 4. 添加客户
cid = add_customer(name="张三", phone="13800138000")

# 5. 报价
add_quote(batch_id=1, customer_id=cid, quote_price=5000, quote_quantity=1, quote_date="2024-01-20")

# 6. 更新状态
update_quote_status(1, "已报价")
update_quote_status(1, "已出库")

# 7. 收款
add_payment(quote_id=1, customer_id=cid, pay_type="receivable", amount=5000, pay_date="2024-01-25")

# 8. 导出 Excel
from src.models.database import search_quotes
quotes = search_quotes()
export_quotes_to_excel(quotes)
```
