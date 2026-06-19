# 调货助手项目迁移指南 - Trae Solo

> **版本**: v1.0
> **最后更新**: 2026-06-18
> **适用场景**: 新项目窗口/新对话初始化

---

## 目录

1. [项目概述](#1-项目概述)
2. [命令行为逻辑](#2-命令行为逻辑)
3. [GitHub 工作流程](#3-github-工作流程)
4. [文件操作规范](#4-文件操作规范)
5. [Trae Solo 迁移指南](#5-trae-solo-迁移指南)
6. [常见问题](#6-常见问题)

---

## 1. 项目概述

### 1.1 项目基础信息

| 项目属性 | 说明 |
|----------|------|
| **项目名称** | 调货助手 (diaohuo-assistant) |
| **技术栈** | Python 3.x + PyQt6 + SQLite |
| **项目路径** | `d:\OH-workspace\diaohuo-assistant\` |
| **远程仓库** | `git@github.com:CaoJun1015/diaohuo-assistant.git` |

### 1.2 核心功能模块

| 模块 | 文件位置 | 说明 |
|------|----------|------|
| **机型管理** | `src/models/database.py` | 机型 CRUD、搜索 |
| **库存批次** | `src/models/database.py` | 批次管理、库存扣减 |
| **客户管理** | `src/models/database.py` | 客户信息、购买历史 |
| **上游管理** | `src/models/database.py` | 供应商管理 |
| **报价记录** | `src/models/database.py` | 报价流程、状态流转 |
| **收付款** | `src/models/database.py` | 应收应付管理 |
| **智能跟单** | `src/utils/follow_up.py` | 跟进提醒 |
| **月度报告** | `src/utils/monthly_report.py` | 经营分析 |

### 1.3 目录结构

```
diaohuo-assistant/
├── src/
│   ├── main.py              # 主窗口及 UI 面板
│   ├── models/
│   │   └── database.py      # 数据库操作模块
│   ├── ui/
│   │   └── __init__.py
│   └── utils/
│       ├── excel_export.py  # Excel 导出
│       ├── follow_up.py     # 智能跟单
│       ├── image_gen.py     # 图片生成
│       ├── json_export.py   # JSON 导入导出
│       ├── monthly_report.py # 月度报告
│       ├── price_diff.py    # 价格异动哨兵
│       ├── quote_assist.py  # 报价决策助手
│       ├── remote_diagnose.py # 远程诊断
│       ├── shipment_flow.py # 出库一条龙
│       └── word_parser.py   # Word 解析
├── data/
│   └── diaohuo.db           # SQLite 数据库
├── docs/
│   └── API接口文档.md        # API 接口文档
├── .gitignore               # Git 忽略规则
├── 调货助手 v1.06.spec      # PyInstaller 打包配置
└── README.md                # 项目说明
```

---

## 2. 命令行为逻辑

### 2.1 核心命令分类

#### 2.1.1 代码读取命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `Read` | 读取文件内容 | `Read(file_path="d:/OH-workspace/diaohuo-assistant/src/main.py")` |
| `LS` | 列出目录内容 | `LS(path="d:/OH-workspace/diaohuo-assistant/src")` |
| `Glob` | 文件模式匹配 | `Glob(pattern="**/*.py", path="d:/OH-workspace/diaohuo-assistant")` |

#### 2.1.2 代码修改命令

| 命令 | 用途 | 注意事项 |
|------|------|----------|
| `Edit` | 精确字符串替换 | 必须先 Read 获取最新内容 |
| `Write` | 覆盖写入文件 | 覆盖前必须先 Read |
| `DeleteFile` | 删除文件 | 谨慎使用，确认文件路径正确 |

#### 2.1.3 Git 命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `git init` | 初始化仓库 | 首次设置时使用 |
| `git checkout -b dev` | 创建开发分支 | 从 main 分支创建 |
| `git add .` | 暂存变更 | 提交前执行 |
| `git commit -m "feat: xxx"` | 提交变更 | 遵循语义化规范 |
| `git push origin <branch>` | 推送分支 | 推送到远程 |
| `git merge <branch>` | 合并分支 | 将 dev 合并到 main |

#### 2.1.4 测试与构建命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `python src/main.py` | 运行开发版本 | 直接启动应用 |
| `pyinstaller "调货助手 v1.06.spec"` | 打包构建 | 生成可执行文件 |

### 2.2 命令执行注意事项

**PowerShell 环境约束**:
- 不支持 bash heredoc (`cat <<EOF`)
- 不支持 `&&` 连接符，使用分号 `;` 替代
- 路径中含空格时需要用引号包裹

**示例**:
```powershell
# 正确：使用分号分隔命令
git status; git branch

# 正确：路径加引号
python "d:\OH-workspace\diaohuo-assistant\src\main.py"

# 正确：多行提交信息
git commit -m "feat(quote): 新增报价功能" -m "添加了报价记录的增删改查"

# 错误：PowerShell 不支持 &&
git status && git branch  # ❌ 会报错
```

---

## 3. GitHub 工作流程

### 3.1 初始化流程

```
1. git init                                # 在项目目录初始化
2. 生成 .gitignore                          # 屏蔽不需要的文件
3. git add .                               # 暂存所有文件
4. git commit -m "chore: 初始化项目"         # 初始提交
5. git branch -M main                      # 重命名主分支
6. git remote add origin <URL>              # 关联远程仓库
7. git push -u origin main                 # 推送主分支
8. git checkout -b dev                      # 创建开发分支
9. git push -u origin dev                   # 推送开发分支
```

### 3.2 分支管理策略

| 分支 | 用途 | 保护策略 |
|------|------|----------|
| `main` | 生产版本 | 禁止直接推送，需通过 PR |
| `dev` | 开发分支 | 日常开发，可直接推送 |
| `feature/*` | 功能分支 | 可选，用于大型功能开发 |

### 3.3 开发工作流

```
┌─────────────────────────────────────────────────────────────┐
│                    开发流程                                 │
├─────────────────────────────────────────────────────────────┤
│  1. git checkout dev        # 切换到开发分支              │
│  2. git pull origin dev     # 拉取最新代码               │
│  3. 编写代码               # 实现功能/修复bug            │
│  4. git add .              # 暂存变更                   │
│  5. git commit -m "xxx"    # 提交（语义化）             │
│  6. git push origin dev     # 推送到远程                 │
│  7. 创建 PR                # 合并到 main                │
└─────────────────────────────────────────────────────────────┘
```

### 3.4 语义化 Commit 规范

**Commit 类型**:

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(quote): 添加报价复制功能` |
| `fix` | 修复 bug | `fix(supplier): 修复上游管理UI卡死问题` |
| `refactor` | 重构 | `refactor(db): 优化数据库查询` |
| `style` | 代码风格 | `style(main): 格式化代码` |
| `docs` | 文档更新 | `docs(api): 更新接口文档` |
| `test` | 测试相关 | `test: 添加单元测试` |
| `chore` | 杂务 | `chore: 删除测试文件` |

**格式**:
```
<类型>(<模块>): <描述>

<详细说明（可选）>
```

**示例**:
```
fix(supplier): 修复上游管理UI点击卡死问题

- 替换 clicked 信号为 cellClicked 信号
- 修复 QModelIndex 不稳定导致的崩溃
```

---

## 4. 文件操作规范

### 4.1 文件增删改查规则

#### 4.1.1 创建文件

```python
# 场景：新增工具模块
Write(file_path="d:/OH-workspace/diaohuo-assistant/src/utils/new_module.py", content="...")

# 场景：创建配置文件
Write(file_path="d:/OH-workspace/diaohuo-assistant/config.yaml", content="...")
```

#### 4.1.2 修改文件

```python
# 必须先读取最新内容
content = Read(file_path="d:/OH-workspace/diaohuo-assistant/src/main.py")

# 然后进行修改
Edit(
    file_path="d:/OH-workspace/diaohuo-assistant/src/main.py",
    old_string="old_code",
    new_string="new_code"
)
```

#### 4.1.3 删除文件

```python
# 删除单个文件
DeleteFile(file_paths=["d:/OH-workspace/diaohuo-assistant/test.py"])

# 删除多个文件
DeleteFile(file_paths=[
    "d:/OH-workspace/diaohuo-assistant/test.py",
    "d:/OH-workspace/diaohuo-assistant/test.bat"
])
```

#### 4.1.4 查询文件

```python
# 列出目录
LS(path="d:/OH-workspace/diaohuo-assistant/src")

# 模式匹配
Glob(pattern="**/*.py", path="d:/OH-workspace/diaohuo-assistant")

# 内容搜索
Grep(pattern="def add_quote", path="d:/OH-workspace/diaohuo-assistant/src")
```

### 4.2 命名规范

| 文件类型 | 命名规则 | 示例 |
|----------|----------|------|
| Python 模块 | 小写蛇形 | `database.py`, `excel_export.py` |
| 配置文件 | 小写蛇形 | `config.yaml`, `.gitignore` |
| 文档文件 | 中文/英文 | `API接口文档.md`, `README.md` |
| 测试文件 | test_ 前缀 | `test_database.py` |

### 4.3 代码风格要求

1. **缩进**: 4 空格
2. **行宽**: 120 字符
3. **命名**:
   - 函数/变量：小写蛇形 `get_user_info()`
   - 类：大驼峰 `class QuoteDialog`
   - 常量：全大写加下划线 `MAX_BACKUPS = 7`
4. **注释**: 中文注释，清晰说明业务逻辑

### 4.4 文档管理

| 文档类型 | 位置 | 说明 |
|----------|------|------|
| API 文档 | `docs/API接口文档.md` | 所有接口说明 |
| 更新手册 | `docs/v1.04_to_v1.06_更新手册.md` | 版本变更记录 |
| 技术文档 | `docs/` | 架构设计、技术说明 |

---

## 5. Trae Solo 迁移指南

### 5.1 新窗口初始化清单

**必做步骤**:

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 检查工作目录 | `LS(path="d:/OH-workspace/diaohuo-assistant")` |
| 2 | 检查 Git 状态 | `RunCommand(command="git status", cwd="d:/OH-workspace/diaohuo-assistant", blocking=True, requires_approval=False)` |
| 3 | 检查分支 | `RunCommand(command="git branch -a", cwd="d:/OH-workspace/diaohuo-assistant", blocking=True, requires_approval=False)` |
| 4 | 读取关键文件 | `Read(file_path="d:/OH-workspace/diaohuo-assistant/src/main.py")` |
| 5 | 读取数据库模块 | `Read(file_path="d:/OH-workspace/diaohuo-assistant/src/models/database.py")` |

**可选步骤**:

| 步骤 | 操作 | 说明 |
|------|------|------|
| 6 | 检查数据库 | `RunCommand(command="dir data", cwd="d:/OH-workspace/diaohuo-assistant", blocking=True, requires_approval=False)` |
| 7 | 运行测试 | `RunCommand(command="python src/main.py", cwd="d:/OH-workspace/diaohuo-assistant", blocking=False, requires_approval=False, wait_ms_before_async=3000)` |

### 5.2 环境配置检查

```python
# 1. 检查 Python 版本
RunCommand(command="python --version", cwd="d:/OH-workspace/diaohuo-assistant", blocking=True, requires_approval=False)

# 2. 检查依赖安装
RunCommand(command="pip list | findstr PyQt", cwd="d:/OH-workspace/diaohuo-assistant", blocking=True, requires_approval=False)

# 3. 检查 Git 配置
RunCommand(command="git config --list", cwd="d:/OH-workspace/diaohuo-assistant", blocking=True, requires_approval=False)
```

### 5.3 状态恢复流程

当新对话开始时，需要恢复的关键状态：

1. **当前分支**: 确认在 `dev` 分支进行开发
2. **工作目录**: 确认在项目根目录
3. **未提交变更**: 检查是否有未提交的文件
4. **数据库连接**: 确认 `data/diaohuo.db` 存在

**恢复脚本**:
```powershell
# 切换到开发分支
git checkout dev

# 拉取最新代码
git pull origin dev

# 检查状态
git status

# 确认数据库存在
dir data\diaohuo.db
```

### 5.4 迁移注意事项

1. **不要直接修改 main 分支**: 所有开发在 `dev` 分支进行
2. **每次修改前拉取**: `git pull origin dev`
3. **小步提交**: 避免单次提交大量变更
4. **提交前验证**: 运行应用确认功能正常
5. **保持 .gitignore 同步**: 添加新文件类型时更新忽略规则

---

## 6. 常见问题

### 6.1 Git 操作问题

**Q: 推送失败，提示权限不足**

**A**: 检查 SSH 密钥配置，确保本地密钥已添加到 GitHub 账户。

```powershell
# 检查 SSH 连接
ssh -T git@github.com
```

**Q: 合并冲突**

**A**: 手动解决冲突后重新提交：

```powershell
# 查看冲突文件
git status

# 编辑冲突文件，删除冲突标记
# 然后
git add .
git commit -m "fix: 解决合并冲突"
git push
```

### 6.2 代码修改问题

**Q: Edit 命令失败，提示字符串不唯一**

**A**: 增加匹配上下文，确保 `old_string` 在文件中唯一：

```python
# 错误：匹配字符串太短
Edit(file_path="...", old_string="def func():", new_string="...")

# 正确：增加上下文
Edit(file_path="...", old_string="    def func(self):\n        '''函数说明'''\n        pass", new_string="...")
```

**Q: Read 命令提示文件不存在**

**A**: 确认文件路径正确，使用绝对路径：

```python
Read(file_path="d:/OH-workspace/diaohuo-assistant/src/main.py")
```

### 6.3 运行问题

**Q: 运行应用时提示模块找不到**

**A**: 检查 Python 路径配置，确保 `src` 目录在路径中：

```python
import sys
sys.path.insert(0, "d:/OH-workspace/diaohuo-assistant")
```

**Q: 数据库文件找不到**

**A**: 确认 `data` 目录存在且有写入权限：

```powershell
mkdir data -Force  # PowerShell 创建目录
```

---

## 附录：常用命令速查

### Git 常用命令

| 命令 | 用途 |
|------|------|
| `git status` | 查看工作区状态 |
| `git branch` | 查看本地分支 |
| `git branch -a` | 查看所有分支 |
| `git checkout <branch>` | 切换分支 |
| `git pull origin <branch>` | 拉取远程分支 |
| `git push origin <branch>` | 推送到远程分支 |
| `git log --oneline -10` | 查看最近 10 条提交 |
| `git diff` | 查看未暂存的变更 |

### 项目操作命令

| 命令 | 用途 |
|------|------|
| `python src/main.py` | 启动应用 |
| `pyinstaller "调货助手 v1.06.spec"` | 打包构建 |
| `dir data` | 查看数据库目录 |
| `del data\*.db` | 删除数据库（谨慎） |

---

**文档版本**: v1.0  
**作者**: Trae Solo  
**日期**: 2026-06-18