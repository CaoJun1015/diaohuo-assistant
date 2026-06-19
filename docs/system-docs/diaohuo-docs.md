# 调货助手 — 系统说明文档

**版本**：v1.06  
**日期**：2026-06-18  
**技术栈**：Python + PyQt6 + SQLite3

---

## 目录

- [一、系统概述](#一系统概述)
- [二、安装与运行](#二安装与运行)
- [三、项目结构](#三项目结构)
- [四、核心模块说明](#四核心模块说明)
- [五、数据库设计](#五数据库设计)
- [六、业务流程](#六业务流程)
- [七、智能技能系统](#七智能技能系统)
- [八、数据备份与恢复](#八数据备份与恢复)
- [九、打包发布](#九打包发布)
- [十、常见问题](#十常见问题)

---

## 一、系统概述

调货助手是一款面向 IT 硬件经销商的本地化桌面管理工具，采用 **Python + PyQt6 + SQLite3** 技术栈，完全离线运行，无需服务器和联网。

系统覆盖从上游价格表导入、库存批次管理、客户报价、出库发货、收款对账的完整业务闭环，并通过 6 个内置智能技能模块提供数据驱动的经营辅助。

### 1.1 核心特性

- **完全本地化**：数据存储在本地 SQLite 数据库，不上传云端
- **Word 自动解析**：一键导入上游价格表，自动提取机型配置
- **实时库存管理**：报价自动扣减库存，防止超卖
- **智能报价建议**：基于历史数据自动推荐报价区间
- **条码枪支持**：出库时连续扫描 SN 码，自动校验去重
- **经营分析报告**：月度自动汇总销售额、毛利、回款率、滞销预警
- **自动备份**：启动时自动备份，保留最近 7 个版本

### 1.2 适用场景

- 笔记本/台式机调货商
- 小型电脑装机店
- IT 硬件区域代理

---

## 二、安装与运行

### 2.1 环境要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10/11 |
| Python | 3.10 或更高版本 |
| 内存 | 4GB 及以上 |
| 磁盘空间 | 100MB 及以上（含数据库和备份） |

### 2.2 源码运行

```bash
# 1. 克隆仓库
git clone https://github.com/CaoJun1015/diaohuo-assistant.git
cd diaohuo-assistant

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动程序
python run.py
```

### 2.3 打包为 exe

```bash
# 安装 PyInstaller（如未安装）
pip install pyinstaller

# 执行打包脚本
python build_exe.py

# 打包后的文件位于 dist/ 目录下
# diaohuo-assistant.exe 可直接在无 Python 环境的电脑上运行
```

> **注意**：打包后的 exe 首次运行时，Windows 可能会提示"未知发布者"，点击"更多信息" → "仍要运行"即可。这是自签名程序的正常提示。

---

## 三、项目结构

```
diaohuo-assistant/
├── run.py                      # 程序启动入口
├── build_exe.py                # PyInstaller 打包脚本
├── build.spec                  # PyInstaller 配置文件
├── requirements.txt            # Python 依赖清单
├── README.md                   # 项目说明
├── CHANGELOG.md                # 版本更新日志
├── LICENSE                     # MIT 许可证
│
├── src/                        # 核心源代码
│   ├── __init__.py
│   ├── main.py                 # UI 主窗口（PyQt6，约 2800 行）
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py         # 数据库模型与 CRUD（约 770 行）
│   └── utils/                  # 工具模块
│       ├── __init__.py
│       ├── word_parser.py      # Word 价格表解析（约 300 行）
│       ├── image_gen.py        # 报价图片生成（约 200 行）
│       ├── excel_export.py     # Excel 导出（约 136 行）
│       ├── json_export.py      # JSON 全量备份/导入（约 200 行）
│       ├── price_diff.py       # 价格异动哨兵
│       ├── follow_up.py        # 智能跟单提醒
│       ├── monthly_report.py   # 月度经营报告
│       ├── quote_assist.py     # 报价决策助手
│       ├── shipment_flow.py    # 出库一条龙（SN 校验）
│       └── remote_diagnose.py  # 远程诊断助手
│
├── data/                       # 数据目录
│   ├── diaohuo.db              # SQLite 主数据库
│   └── backup/                 # 自动备份文件
│
├── docs/                       # 文档目录
│   ├── API接口文档.md
│   ├── v1.04_to_v1.06_更新手册.md
│   ├── skills.md               # 技能模块说明
│   ├── prd/                    # PRD 文档
│   │   ├── diaohuo-prd.html
│   │   └── diaohuo-prd.md
│   └── system-docs/            # 系统说明文档
│       ├── diaohuo-docs.html
│       └── diaohuo-docs.md
│
├── skills/                     # TRAE SOLO Skill
│   └── it-remote-diagnose/
│       └── SKILL.md
│
├── dist/                       # 打包输出目录
├── build/                      # PyInstaller 构建产物
└── test_output/                # 测试输出文件
```

---

## 四、核心模块说明

### 4.1 main.py — UI 主窗口

系统的入口和界面层，基于 PyQt6 构建。主要包含：

- **5 个 Tab 页面**：机型管理、客户管理、上游管理、报价记录、账款管理
- **工具栏**：导入 Word、导出、对账、以及 6 个 Skill 按钮
- **对话框**：出库对话框（ShipmentDialog）、收款对话框（PaymentDialog）、对账单对话框（StatementDialog）
- **状态栏**：显示备份状态、操作提示

文件规模约 2800 行，同时承担 View 和 Controller 职责。

### 4.2 database.py — 数据访问层

系统的数据核心，负责 SQLite 数据库的连接、表结构初始化和所有 CRUD 操作。

关键设计：

- **WAL 模式**：`PRAGMA journal_mode=WAL`，提升并发性能
- **外键约束**：`PRAGMA foreign_keys=ON`，保证数据完整性
- **自动备份**：启动时自动复制数据库，保留最近 7 个版本
- **数据库迁移**：通过 `PRAGMA table_info` 检测字段缺失并自动 ALTER

### 4.3 word_parser.py — Word 解析器

解析上游发来的 Word 价格表，提取机型配置信息。

技术要点：

- 支持**标准 python-docx**和**WPS 兼容模式**（直接解析 XML）
- 按已知机型前缀分割文本（Y7000P、小新Pro16、拯救者等 20+ 个前缀）
- 正则提取 CPU、内存、硬盘、显卡、屏幕尺寸
- 处理斜杠分隔格式（如 `ultra5-225/32/1T`）
- 智能合并文本碎片，过滤显存干扰

### 4.4 image_gen.py — 图片生成

使用 Pillow 生成报价图片，包含：

- 批量报价单图片（多机型汇总）
- 单机报价卡片（单机型详情）
- 水印功能（防止报价图片被滥用）

### 4.5 excel_export.py — Excel 导出

使用 openpyxl 导出报价记录为 Excel 文件，包含：

- 状态颜色标记（不同状态用不同背景色）
- 完整财务信息（购入价、报价、数量、毛利）
- 自动调整列宽

### 4.6 json_export.py — JSON 备份

全量数据导出/导入模块：

- 导出：将所有表数据序列化为 JSON，保存到桌面
- 导入：从 JSON 恢复数据，自动处理外键关系映射
- 适用于数据迁移和灾难恢复

---

## 五、数据库设计

### 5.1 ER 关系图

```
products ||--o{ batches : "包含"
batches ||--o{ quotes : "被报价"
customers ||--o{ quotes : "下单"
suppliers ||--o{ batches : "供货"
quotes ||--o{ payments : "收付款"
customers ||--o{ payments : "付款"
suppliers ||--o{ payments : "收款"
```

### 5.2 表结构详情

| 表名 | 用途 | 核心字段 | 关联 |
|------|------|---------|------|
| products | 机型信息 | series, cpu, ram, storage, gpu, screen, note | 1:N → batches |
| batches | 库存批次 | product_id, purchase_price, quantity, remaining, supplier_id, sn_list | N:1 → products, N:1 → suppliers, 1:N → quotes |
| customers | 客户 | name, wechat, qq, phone, balance | 1:N → quotes, 1:N → payments |
| suppliers | 上游供应商 | name, wechat, qq, phone, balance | 1:N → batches, 1:N → payments |
| quotes | 报价记录 | batch_id, customer_id, quote_price, quote_quantity, status, received_amount | N:1 → batches, N:1 → customers, 1:N → payments |
| payments | 收付款记录 | quote_id, customer_id, supplier_id, type, amount, method | N:1 → quotes/customers/suppliers |
| operation_logs | 操作日志 | operation, table_name, record_id, description | 独立表 |
| price_snapshots | 价格快照 | import_date, item_count | 1:N → price_snapshot_items |
| price_snapshot_items | 快照明细 | snapshot_id, series, cpu, norm_key | N:1 → price_snapshots |

### 5.3 数据库特性

- **WAL 模式**：写前日志，提升读写并发性能
- **外键约束**：级联删除保护数据一致性
- **索引优化**：series、quote_date、customer_id、created_at 等字段建有索引
- **自动迁移**：启动时检测字段缺失并自动 ALTER TABLE

---

## 六、业务流程

### 6.1 核心业务流程：从进货到收款

**步骤 1：导入价格表**

上游发来 Word 价格表 → 点击"导入 Word" → 选择文件 → 预览解析结果 → 勾选确认 → 机型入库（products 表）。导入后自动触发**价格异动哨兵**，对比上一版本检测新增/下架。

**步骤 2：新增库存批次**

选择机型 → 录入购入价、数量、入库日期、上游供应商、SN 列表 → 保存到 batches 表。系统实时计算并显示该机型的总库存。

**步骤 3：创建报价**

选择机型 → 选择批次 → 输入报价金额和数量 → 选择客户 → 保存到 quotes 表（状态 = 待确认）。系统自动加载**报价决策助手**推荐价格。

**步骤 4：确认报价**

在报价记录列表中找到该记录 → 点击"确认报价" → 状态更新为"已报价"。此时可一键复制报价文本或生成报价图片发给客户。

**步骤 5：出库发货**

报价记录 → 点击"出库" → 弹出 ShipmentDialog → 选择扣减批次 → 条码枪扫描 SN（支持连续扫码）→ SN 格式校验 + 去重检查 → 确认出库 → 状态更新为"已出库"，批次 remaining 扣减。

**步骤 6：收款**

报价记录 → 点击"收款" → 弹出 PaymentDialog → 输入收款金额和方式 → 确认。支持部分收款，累计收款足额后状态自动更新为"已收款"。

**步骤 7：对账**

客户 + 日期范围 → 生成对账单 → 查看明细 → 导出 Excel。

### 6.2 报价状态流转

```
[创建报价] → 待确认 → [确认报价] → 已报价 → [出库操作] → 已出库 → [收款足额] → 已收款
                                          ↓
                                    [取消订单] → 已取消
```

### 6.3 数据流图

```
Word价格表 → word_parser → products表
                              ↓
                        选择机型 → 新增批次
                              ↓
                        batches表 → 库存管理
                              ↓
                        选择批次 → 创建报价
                              ↓
                        quotes表 → 报价记录
                              ↓
                    确认 → 已报价 → 出库 → shipment_flow
                                          ↓
                                    扣减库存 → 已出库 → 收款
                                                          ↓
                                                    payments表 → 账款管理
                                                          ↓
                                                    足额 → 已收款
```

---

## 七、智能技能系统

系统内置 6 个智能技能模块，均位于 `src/utils/` 目录下，彼此独立，可单独调用。

### 7.1 报价决策助手（quote_assist.py）

| 项目 | 说明 |
|------|------|
| 功能 | 基于历史报价数据推荐报价金额 |
| 输入 | 机型特征 + 进货价（可选）+ 客户名（可选） |
| 输出 | 建议报价区间、利润率、置信度、依据说明 |
| 算法 | 历史均价 ± 5%；客户历史与机型历史各占 50% 权重 |
| 触发 | 选择机型后自动加载 / 手动点击按钮 |

### 7.2 价格异动哨兵（price_diff.py）

| 项目 | 说明 |
|------|------|
| 功能 | 检测价格表的新增/下架机型 |
| 输入 | 当前导入的机型列表 |
| 输出 | 新增列表、下架列表 |
| 算法 | 系列+CPU+内存+硬盘+显卡+备注的规范化组合对比 |
| 触发 | 导入 Word 价格表后自动执行 |

### 7.3 智能跟单提醒（follow_up.py）

| 项目 | 说明 |
|------|------|
| 功能 | 扫描超期未成交订单 |
| 规则 | 待确认/已报价/已出库 超过 3 天未推进 |
| 输出 | 按状态分类的超期订单列表 |
| 触发 | 手动点击"跟单提醒"按钮 |

### 7.4 月度经营报告（monthly_report.py）

| 项目 | 说明 |
|------|------|
| 功能 | 自动生成月度经营分析 |
| 指标 | 销售额、毛利、毛利率、回款率、TOP5、滞销预警、环比 |
| 输出 | 格式化文本报告 |
| 触发 | 手动点击"月度报告"按钮 |

### 7.5 出库一条龙（shipment_flow.py）

| 项目 | 说明 |
|------|------|
| 功能 | SN 批量扫描/校验/去重/确认单 |
| 输入 | SN 文本（支持换行/逗号/空格分隔） |
| 校验 | 长度 6-30 位，仅字母/数字/短横线 |
| 输出 | 去重后的 SN 列表、出库确认单文本 |
| 触发 | 出库对话框中自动调用 |

### 7.6 远程诊断助手（remote_diagnose.py）

| 项目 | 说明 |
|------|------|
| 功能 | 结构化故障排查决策树 |
| 支持故障 | 蓝屏、开不了机、WiFi 问题、风扇噪音 |
| 数据结构 | DIAGNOSE_TREE 字典，支持多级分支 |
| 输出 | 排查步骤 + 处理方案 + 诊断报告 |
| 触发 | 手动点击"远程诊断"按钮 |

---

## 八、数据备份与恢复

### 8.1 自动备份

- **时机**：程序启动时自动执行
- **位置**：`data/backup/diaohuo_backup_YYYYMMDD_HHMMSS.db`
- **保留策略**：最近 7 个版本，超出自动删除最旧的
- **状态提示**：状态栏显示备份成功/失败信息

### 8.2 手动 JSON 导出

- **范围**：全量数据（所有表）
- **格式**：JSON，包含外键关系映射
- **位置**：桌面（`diaohuo_backup_YYYYMMDD_HHMMSS.json`）
- **用途**：跨设备迁移、长期归档

### 8.3 手动 JSON 导入

- **流程**：选择 JSON 文件 → 解析 → 清空现有表 → 重建数据
- **外键处理**：自动重新映射 ID 关系
- **注意**：导入会覆盖现有数据，建议先备份

### 8.4 Excel 导出

- **范围**：报价记录（支持按日期/客户筛选）
- **格式**：.xlsx，含状态颜色标记
- **位置**：桌面

---

## 九、打包发布

### 9.1 打包配置

使用 PyInstaller 打包为单文件 exe，配置位于 `build.spec`：

- 单文件模式（`--onefile`）
- 包含 data 目录作为资源
- 隐藏控制台窗口（`--noconsole`）
- 自定义图标

### 9.2 打包步骤

```bash
python build_exe.py
```

脚本会自动执行以下操作：

1. 清理旧的 build/ 和 dist/ 目录
2. 运行 PyInstaller 打包
3. 复制必要的资源文件到 dist/
4. 输出生成的 exe 路径

### 9.3 分发注意事项

- exe 文件需与 data/ 目录放在同一目录下运行
- 首次运行会自动创建 data/diaohuo.db
- Windows 可能会提示安全警告，需用户手动允许

---

## 十、常见问题

### Q1：Word 价格表导入失败或解析不全

**可能原因**：WPS 生成的 docx 格式与标准格式有差异。

**解决**：系统已内置 WPS 兼容模式，会自动尝试两种解析方式。如仍失败，建议用微软 Office 重新保存一次再导入。

### Q2：库存数量不对

**可能原因**：报价时扣减了库存但订单后来取消，目前取消订单不会自动回滚库存。

**解决**：手动在批次管理中调整 remaining 数量。后续版本会优化库存回滚逻辑。

### Q3：备份文件在哪里

**位置**：`data/backup/` 目录下，文件名格式为 `diaohuo_backup_YYYYMMDD_HHMMSS.db`。

### Q4：如何迁移数据到另一台电脑

**方法**：在原电脑上使用"JSON 导出"功能，将生成的 JSON 文件复制到新电脑，然后使用"JSON 导入"恢复。

### Q5：报价决策助手推荐的价格不合理

**原因**：历史报价数据不足或存在异常值。

**解决**：系统会标注置信度（high/medium/low）。low 置信度时建议以进货价 + 默认加价率（3-10%）为参考，结合市场行情手动调整。

### Q6：条码枪扫描 SN 时自动提交了对话框

**解决**：出库对话框已针对条码枪优化，拦截了回车键的默认提交行为，每扫一条自动换行。如仍有问题，请检查条码枪是否模拟了其他按键。
