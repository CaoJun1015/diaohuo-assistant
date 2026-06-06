# 调货助手 v1.04 — `main.py` 技术文档

## 总览

本文档为 `src/main.py` 的 API 级技术参考。该模块是调货助手桌面应用的 UI 层，基于 PyQt6 实现，负责机型管理、库存批次、报价操作、出库确认、收款/付款、客户对账、上游管理及数据导入导出的全部界面交互逻辑。

---

## 1. 模块概览

| 类名 | 类型 | 核心职责 |
|------|------|---------|
| `ShipmentDialog` | QDialog | 出库确认：选择批次、录入 SN、校验库存 |
| `PaymentDialog` | QDialog | 收款/付款：金额、方式、日期录入 |
| `StatementDialog` | QDialog | 客户对账单：按日期范围查询并导出 Excel |
| `export_statement_to_excel()` | 独立函数 | 将对账记录写入格式化 Excel 文件 |
| `ProductEditDialog` | QDialog | 机型 CRUD：新增/编辑机型七字段 |
| `BatchDialog` | QDialog | 批次入库：价格、数量、上游、SN |
| `CustomerDialog` | QDialog | 客户 CRUD：名称、微信、QQ、电话、备注 |
| `QuoteEditDialog` | QDialog | 报价记录编辑：报价、数量、客户、打款状态 |
| `QuotePanel` | QWidget | 报价操作面板：批次展示 + 报价 + 生成图片/文本 |
| `MainWindow` | QMainWindow | 主窗口：五 Tab 布局 + 全局工具栏 + 状态栏 |
| `APP_STYLE` | 常量 | 全局 QSS 样式表 |

---

## 2. 独立函数

### 2.1 `export_statement_to_excel`

**核心功能：** 将客户对账记录导出为带格式的 Excel 文件。

**输入参数：**

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `records` | `list[dict]` | 是 | 对账记录列表，每条需含 `purchase_price`、`quote_price`、`quote_quantity`、`received_amount`、`quote_date`、`series`、`cpu`、`status`、`batch_remark`、`remark` 等字段 |
| `customer_name` | `str` | 是 | 客户名称，用于文件命名 |

**返回值：** `str` — 生成的 Excel 文件绝对路径。

**输出路径：** `~/Desktop/对账单_{客户名}_{时间戳}.xlsx`

**异常处理：**

| 异常 | 触发条件 |
|------|---------|
| `OSError` | 桌面目录不可写、磁盘满 |
| `KeyError` | `records` 中缺少必需字段 |

**注意事项：**
- 文件路径硬编码为用户桌面，不支持自定义输出目录。
- `records` 中金额字段若为 `None`，会按 `0` 处理（`or 0` 兜底）。
- Excel 列宽硬编码为字母索引，仅支持到 Z 列（26 列以内）。

**使用示例：**
```python
records = get_customer_statement(customer_id, "2026-01-01", "2026-05-21")
path = export_statement_to_excel(records, "张三")
# => "C:/Users/xxx/Desktop/对账单_张三_20260521_104300.xlsx"
```

---

## 3. 对话框类

### 3.1 `ShipmentDialog`

**核心功能：** 出库确认对话框，选择扣减批次、录入 SN、校验库存充足性。

**构造函数：**

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `parent` | `QWidget` | 否 | 父窗口，默认 `None` |
| `quote` | `dict` | 是 | 报价记录，需含 `series`、`cpu`、`customer_name`、`quote_quantity` |
| `batches` | `list[dict]` | 否 | 可选批次列表，每项需含 `id`、`purchase_price`、`remaining`、`date` |

**关键方法：**

#### `get_data() -> dict`

返回用户选择的出库数据。

| 返回字段 | 类型 | 说明 |
|----------|------|------|
| `batch_id` | `int \| None` | 选中批次 ID |
| `sn_list` | `str` | 逗号分隔的 SN 序列号 |
| `remark` | `str` | 出库备注 |

**异常处理：**

| 异常 | 触发条件 |
|------|---------|
| 无异常抛出 | 内部通过 `QMessageBox.warning` 提示，不抛异常 |

**注意事项：**
- 库存不足时仅弹窗警告，不阻止对话框打开。
- SN 字段为选填，不校验格式。
- 批次列表通过 `QComboBox.currentData()` 存储 `batch_id`，若批次数据结构变更需同步更新 `addItem` 的 `userData`。

---

### 3.2 `PaymentDialog`

**核心功能：** 通用收款/付款录入对话框。

**构造函数：**

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `parent` | `QWidget` | 否 | 父窗口 |
| `title` | `str` | 否 | 对话框标题，默认 `"收款"` |
| `pay_type` | `str` | 否 | 类型标识：`"receivable"` 或 `"payable"`，当前版本仅影响显示 |
| `quote` | `dict` | 否 | 关联报价记录，传入时显示客户/金额概览 |

**关键方法：**

#### `get_data() -> dict`

| 返回字段 | 类型 | 说明 |
|----------|------|------|
| `amount` | `int` | 金额（单位：元），范围 1–999999 |
| `method` | `str` | 支付方式：微信/支付宝/转账/现金 |
| `pay_date` | `str` | 日期，格式 `yyyy-MM-dd` |
| `remark` | `str` | 备注 |

**注意事项：**
- `amount` 使用 `QSpinBox`，精度为整数，不支持小数金额。
- 当传入 `quote` 时，显示的是**该订单维度**的待收金额，不考虑已分配的跨订单收款。

---

### 3.3 `StatementDialog`

**核心功能：** 按客户 + 日期范围生成对账单，支持表格展示和 Excel 导出。

**构造函数：**

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `parent` | `QWidget` | 否 | 父窗口 |

**内部依赖：**
- `get_all_customers()` — 加载客户下拉列表
- `get_customer_statement()` — 查询对账数据
- `export_statement_to_excel()` — 导出 Excel

**关键方法：**

#### `_query()`

根据选定客户和日期范围查询对账记录，填充表格并计算汇总（总购入、总金额、已收款、待收款、总毛利）。

#### `_export_excel()`

将当前查询结果导出 Excel。未先查询时弹窗提示。

**注意事项：**
- 客户选择支持下拉选择和手动输入，手动输入时会尝试模糊匹配。
- 查询结果缓存在 `self._records` 实例属性中，导出时直接读取。

---

### 3.4 `ProductEditDialog`

**核心功能：** 机型新增/编辑对话框。

**构造函数：**

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `parent` | `QWidget` | 否 | 父窗口 |
| `product` | `dict` | 否 | 传入时为编辑模式，字段为 `series`、`cpu`、`ram`、`storage`、`gpu`、`screen`、`note` |

**关键方法：**

#### `get_data() -> dict`

| 返回字段 | 类型 | 说明 |
|----------|------|------|
| `series` | `str` | 系列名称 |
| `cpu` | `str` | CPU 型号 |
| `ram` | `str` | 内存容量 |
| `storage` | `str` | 硬盘容量 |
| `gpu` | `str` | 显卡型号 |
| `screen` | `str` | 屏幕尺寸 |
| `note` | `str` | 备注 |

**注意事项：**
- 不在对话框内做 `series` 非空校验，由调用方（`MainWindow.on_add_product`）负责。

---

### 3.5 `BatchDialog`

**核心功能：** 库存批次入库对话框，支持选择/新建上游。

**构造函数：**

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `parent` | `QWidget` | 否 | 父窗口 |

**关键方法：**

#### `get_data() -> dict`

| 返回字段 | 类型 | 说明 |
|----------|------|------|
| `price` | `int` | 购入单价（元） |
| `quantity` | `int` | 入库数量 |
| `date` | `str` | 入库日期，格式 `yyyy-MM-dd` |
| `remark` | `str` | 备注 |
| `supplier_id` | `int` | 上游 ID，若手动输入新名称则自动创建 |
| `sn_list` | `str` | 逗号分隔的 SN 序列号 |

**注意事项：**
- 上游选择框可编辑，用户输入新名称时自动调用 `add_supplier()` 创建并返回 ID。
- SN 字段为选填，不校验格式或数量是否与 `quantity` 一致。

---

### 3.6 `CustomerDialog`

**核心功能：** 客户新增/编辑对话框（复用于上游编辑）。

**构造函数：**

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `parent` | `QWidget` | 否 | 父窗口 |
| `customer` | `dict` | 否 | 传入时为编辑模式 |

**关键方法：**

#### `get_data() -> dict`

| 返回字段 | 类型 | 说明 |
|----------|------|------|
| `name` | `str` | 客户名称 |
| `wechat` | `str` | 微信号 |
| `qq` | `str` | QQ 号 |
| `phone` | `str` | 电话号码 |
| `note` | `str` | 备注 |

**注意事项：**
- 该对话框被上游编辑功能复用（`MainWindow.on_add_supplier` 中 `dlg.setWindowTitle("新增上游")`），但类本身不含"上游"语义，属于设计层面的妥协。

---

### 3.7 `QuoteEditDialog`

**核心功能：** 报价记录编辑对话框，支持修改报价、数量、客户、打款状态。

**构造函数：**

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `parent` | `QWidget` | 否 | 父窗口 |
| `quote` | `dict` | 否 | 传入时为编辑模式，需含 `quote_price`、`quote_quantity`、`quote_date`、`remark`、`sn_list`、`paid`、`batch_id` |
| `batch_id` | `int` | 否 | 预设批次 ID（当前版本未使用） |
| `customer_id` | `int` | 否 | 预选客户 ID |

**关键方法：**

#### `get_data() -> dict`

| 返回字段 | 类型 | 说明 |
|----------|------|------|
| `quote_price` | `int` | 对外报价（元） |
| `quote_quantity` | `int` | 数量 |
| `quote_date` | `str` | 报价日期 |
| `customer_id` | `int` | 客户 ID，新客户自动创建 |
| `remark` | `str` | 备注 |
| `sn_list` | `str` | SN 序列号 |
| `paid` | `str` | 打款状态：`"是"` 或 `"否"` |
| `batch_id` | `int \| None` | 批次 ID，从原 `quote` 对象继承 |

**注意事项：**
- `batch_id` 从原 `self.quote` 中取而非用户选择，编辑报价时不允许变更批次。
- 客户选择框可编辑，新客户自动调用 `add_customer()` 创建。

---

## 4. 组件类

### 4.1 `QuotePanel`

**核心功能：** 报价操作面板，右侧展示选中机型的批次库存并执行报价/生成图片。

**构造函数：**

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `parent` | `QWidget` | 否 | 父窗口 |

**关键方法：**

#### `load_product(product_id, series, cpu, ram, storage, gpu, screen, note)`

加载指定机型的详情并刷新批次表格。

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `product_id` | `int` | 是 | 机型 ID |
| `series` | `str` | 是 | 系列名称 |
| `cpu` | `str` | 是 | CPU |
| `ram` | `str` | 是 | 内存 |
| `storage` | `str` | 是 | 硬盘 |
| `gpu` | `str` | 是 | 显卡 |
| `screen` | `str` | 是 | 屏幕 |
| `note` | `str` | 是 | 备注 |

**返回值：** 无

#### `refresh()`

重新加载当前机型的批次列表和客户下拉列表。无参数，无返回值。

#### `on_quote_and_copy()`

报价并复制文本到剪贴板。执行流程：校验 → 准备数据 → 记录报价 → 格式化文本 → 复制到剪贴板。

#### `on_quote_image()`

报价并生成单条报价图片。执行流程：校验 → 准备数据 → 记录报价 → 调用 `generate_single_quote_card()`。

#### `_validate_quote() -> bool`

校验报价前置条件：机型已选、报价金额 > 0、已选批次、库存充足。

#### `_prepare_quote_data() -> tuple`

返回 `(product, batch, quote_price, quote_quantity, customer_name, remark)` 六元组。

#### `_record_quote(batch_id, quote_price, quote_quantity, remark) -> tuple[bool, str]`

将报价写入数据库。自动处理客户查找/创建。返回 `(success, message)`。

#### `_format_quote_text(product, quote_price, customer_name, quote_quantity) -> str`

格式化报价文本，包含机型规格、价格、客户名和水印。

**注意事项：**
- `_record_quote` 中客户匹配逻辑为**精确匹配**：先 `search_customers` 模糊搜索，再从结果中精确过滤 `name == customer_name`，匹配不到则新建。
- 报价写入数据库后**不立即扣减库存**，库存扣减在出库流程中完成。
- `_prepare_quote_data` 中 `batches` 重新从数据库查询，若表格行数与查询结果不一致（并发修改场景），`row` 索引可能越界。

---

## 5. 主窗口类

### 5.1 `MainWindow`

**核心功能：** 应用主窗口，五 Tab 布局（机型管理、客户管理、上游管理、报价记录、账款管理），承载全部业务操作入口。

**构造函数：**

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| 无 | — | — | — |

**初始化流程：**
1. 调用 `init_db()` 初始化数据库
2. 调用 `backup_database()` 自动备份
3. 构建 UI（五 Tab + 工具栏 + 状态栏）
4. 加载初始数据（机型、客户、上游、报价记录）

#### 5.1.1 Tab 1 — 机型管理

**布局：** 左右分栏（`QSplitter`），左侧机型列表 + 右侧 `QuotePanel`。

**关键方法：**

| 方法 | 功能 |
|------|------|
| `refresh_product_list(keyword=None)` | 刷新机型表格。`keyword` 为空时加载全部，否则按关键字搜索。 |
| `on_product_selected()` | 机型表格选中事件，将选中机型信息传递给 `QuotePanel.load_product()`。 |
| `on_add_product()` | 弹出 `ProductEditDialog` 新增机型。校验 `series` 非空后调用 `add_product()`。 |
| `on_edit_product()` | 弹出 `ProductEditDialog` 编辑当前选中机型。 |
| `on_delete_product()` | 确认后删除机型及关联数据。 |

#### 5.1.2 Tab 2 — 客户管理

**布局：** 上方客户表格 + 下方购买历史面板。

**关键方法：**

| 方法 | 功能 |
|------|------|
| `refresh_customer_list()` | 根据搜索框关键字刷新客户表格。 |
| `on_add_customer()` | 弹出 `CustomerDialog` 新增客户。 |
| `on_edit_customer_from_table()` | 双击客户行，弹出编辑对话框。**注意：** 编辑采用直接 SQL `UPDATE`，未走 `database.py` 的封装函数。 |
| `on_delete_customer()` | 确认后直接 SQL `DELETE`。无级联删除关联报价记录。 |
| `on_customer_cell_clicked(row, col)` | 单击客户行，加载该客户的购买历史和统计信息。 |

#### 5.1.3 Tab 3 — 上游管理

**布局与行为：** 结构与客户管理 Tab 对称。复用 `CustomerDialog` 作为编辑对话框。

**关键方法：**

| 方法 | 功能 |
|------|------|
| `refresh_supplier_list()` | 刷新上游表格。 |
| `on_add_supplier()` | 弹出 `CustomerDialog`（标题改为"新增上游"）。 |
| `on_edit_supplier_from_table()` | 双击编辑，直接 SQL `UPDATE`。 |
| `on_delete_supplier()` | 确认后直接 SQL `DELETE`。 |
| `on_supplier_cell_clicked(row, col)` | 单击上游行，加载采购历史和统计。 |

#### 5.1.4 Tab 4 — 报价记录

**布局：** 工具栏（确认报价/出库/收款/取消/编辑/删除/刷新）+ 筛选栏（日期范围 + 状态 + 搜索）+ 报价表格 + 统计标签。

**关键方法：**

| 方法 | 功能 |
|------|------|
| `refresh_records()` | 按日期范围、关键字、状态筛选刷新报价表格。计算并显示总购入、总报价、毛利。 |
| `on_confirm_quote()` | 将"待确认"状态的报价更新为"已报价"。 |
| `on_ship_quote()` | 出库操作：弹出 `ShipmentDialog` → 扣减批次库存 → 更新 SN → 更新状态为"已出库"。 |
| `on_receive_payment()` | 弹出 `PaymentDialog` 记录收款。 |
| `on_cancel_quote()` | 取消订单。"已收款"状态不可取消。 |
| `on_edit_quote()` | 弹出 `QuoteEditDialog` 编辑报价记录。 |
| `on_delete_quote()` | 确认后删除报价记录。 |

**`on_ship_quote()` 流程详解：**
1. 获取当前选中报价记录
2. 校验状态为"待确认"或"已报价"
3. 通过 `batch_row` 查询获取 `product_id`
4. 弹出 `ShipmentDialog` 让用户选择批次
5. 调用 `deduct_batch_remaining()` 扣减库存
6. 若有 SN，追加到批次的 `sn_list` 字段（**覆盖写入，非追加**）
7. 更新报价状态为"已出库"

#### 5.1.5 Tab 5 — 账款管理

**布局：** 左右分栏，左侧应收（客户欠款）、右侧应付（欠上游款）。

**关键方法：**

| 方法 | 功能 |
|------|------|
| `refresh_finance()` | 刷新应收/应付表格。应收按客户汇总未结清报价，应付按上游汇总采购金额减已付款。 |
| `_on_finance_receive(customer_id)` | 对指定客户收款，采用**先进先出**（FIFO）策略自动分配到最早的未结清订单。 |
| `_on_finance_pay(supplier_id)` | 对指定上游付款，记录到 `payments` 表。 |

**注意事项：**
- `_on_finance_receive` 的 FIFO 分配逻辑直接操作数据库，跨订单分配金额，若中途异常可能导致部分订单已分配部分未分配。
- 应付计算使用子查询，数据量大时可能有性能问题。

#### 5.1.6 工具栏操作

| 方法 | 功能 |
|------|------|
| `on_import_word()` | 导入 Word 价格表：调用 `parse_word_pricelist()` 解析 → 预览 → 按系列+CPU 去重后批量插入。 |
| `on_broadcast()` | 群发图片：弹出选择对话框 → 勾选机型 → 调用 `generate_quote_image()` 批量生成。 |
| `on_export_records_excel()` | 导出当前筛选条件下的报价记录为 Excel。 |
| `on_export_json()` | 全量数据 JSON 导出。 |
| `on_import_json()` | 从 JSON 文件导入数据。含预览确认和导入统计。 |

---

## 6. 全局常量

### 6.1 `APP_STYLE`

**类型：** `str`

**说明：** 全局 QSS 样式表，定义了主窗口、表格、按钮、输入框、Tab 页、分组框、状态栏的统一视觉风格。支持 `.blue`、`.orange`、`.green`、`.red` 四种按钮颜色变体。

---

## 7. 数据流总览

```
Word 价格表
    │  parse_word_pricelist()
    ▼
机型表 (products)
    │  手动新增 / 导入
    ▼
批次表 (batches) ←── 上游表 (suppliers)
    │  入库
    ▼
报价记录 (quotes) ←── 客户表 (customers)
    │  报价 → 确认 → 出库 → 收款
    ▼
付款记录 (payments)
    │  收款/付款
    ▼
账款管理 (应收/应付)
```

---

## 8. 已知设计缺陷与注意事项

| 编号 | 类别 | 描述 |
|------|------|------|
| D-01 | **数据一致性** | `on_edit_quote` 中直接 SQL 更新 `batches.sn_list`，覆盖而非追加 SN，可能丢失原有 SN 记录。 |
| D-02 | **数据一致性** | `on_ship_quote` 中 SN 追加逻辑直接操作数据库，绕过 `database.py` 封装，且无事务保护。 |
| D-03 | **级联删除** | `on_delete_product` / `on_delete_customer` / `on_delete_supplier` 均无级联清理关联记录，可能导致孤儿数据。 |
| D-04 | **客户编辑** | `on_edit_customer_from_table` 和 `on_edit_supplier_from_table` 使用原始 SQL 而非 `database.py` 封装函数，违反数据访问层抽象。 |
| D-05 | **并发安全** | `QuotePanel._prepare_quote_data` 中重新查询批次列表，但表格行索引可能与查询结果不一致。 |
| D-06 | **SN 格式** | 全局 SN 输入均使用逗号分隔的纯文本，无格式校验、无去重、无数量一致性检查。 |
| D-07 | **金额精度** | `PaymentDialog.amount_spin` 为 `QSpinBox`（整数），不支持小数金额。 |
| D-08 | **导入去重** | `on_import_word` 去重仅按 `series + cpu`，同一机型不同内存/硬盘配置会被误判为重复跳过。 |
| D-09 | **代码复用** | `CustomerDialog` 被上游编辑复用，语义不清，且对话框标题在调用方修改而非类内部区分。 |
| D-10 | **资源管理** | `refresh_finance` 中 `get_connection()` 后手动 `close()`，若中间代码抛异常则连接泄漏。建议使用 `with` 上下文管理器。 |
