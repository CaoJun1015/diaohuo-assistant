# 调货助手

面向 IT 硬件经销商的桌面管理工具。从上游价格表解析、报价、出库、收款到对账，一站式管理你的调货生意。

## 功能

- **机型管理** — 从上游 Word 价格表自动导入机型配置，支持联想、拯救者、小新、ThinkPad 等系列
- **库存批次** — 按批次管理进货，记录购入价、数量、上游供应商、SN 序列号
- **报价操作** — 选机型 → 选批次 → 输入报价 → 一键复制文本或生成报价图片
- **出库管理** — 选择批次扣减库存，录入 SN，支持条码枪扫描输入
- **客户管理** — 客户联系方式 + 购买历史 + 欠款跟踪
- **上游管理** — 供应商联系方式 + 采购历史
- **账款管理** — 应收/应付一目了然，支持 FIFO 自动分配收款
- **客户对账单** — 按客户 + 日期范围生成对账单，导出 Excel
- **报价记录** — 全流程状态追踪：待确认 → 已报价 → 已出库 → 已收款
- **数据备份** — 自动备份数据库，支持 JSON 格式全量导入导出

## 快速开始

### 环境要求

- Python 3.10+
- Windows 10/11

### 安装

```bash
git clone https://github.com/你的用户名/diaohuo-assistant.git
cd diaohuo-assistant
pip install -r requirements.txt
```

### 运行

```bash
python run.py
```

### 打包为 exe

```bash
python build_exe.py
```

打包后的 exe 文件在 `dist/` 目录下。

## 项目结构

```
diaohuo-assistant/
├── run.py                  # 启动入口
├── build_exe.py            # 打包脚本
├── build.spec              # PyInstaller 配置
├── requirements.txt        # 依赖清单
│
├── src/
│   ├── main.py             # UI 层（PyQt6 主窗口 + 对话框）
│   ├── models/
│   │   └── database.py     # 数据库模型和 CRUD
│   └── utils/
│       ├── word_parser.py  # Word 价格表解析
│       ├── image_gen.py    # 报价图片生成
│       ├── excel_export.py # Excel 导出
│       └── json_export.py  # JSON 导入导出
│
├── data/                   # 数据目录（数据库不提交到 git）
└── docs/                   # 文档
```

## 依赖

| 包 | 用途 |
|----|------|
| PyQt6 | 桌面 GUI 框架 |
| python-docx | 读取 Word 价格表 |
| Pillow | 生成报价图片 |
| openpyxl | 导出 Excel 报表 |

## 版本历史

- **v1.05** — 当前版本，详见 [CHANGELOG.md](CHANGELOG.md)
- **v1.04** — 批量报价图片、群发功能
- **v1.03** — 自动备份、操作日志、客户购买历史、JSON 备份
- **v1.02** — 报价数量支持、实时库存管理
- **v1.01** — 备注列显示、Word 解析修复
- **v1.0** — 初始版本

## 许可证

[MIT License](LICENSE)
