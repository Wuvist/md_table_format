# MD Table Format (Sublime Text Plugin)

专为 **Sublime Text 3 / 4** 设计的 Markdown 表格智能自动对齐插件。

在编辑 Markdown 文件时（无论是在代码块 ` ``` ` 中还是普通正文中），本插件能按照**严格的等宽字体规则（1 个中文字符 / 全角字符 / Emoji = 2 个英文字宽）**，对各类 **Unicode Box-drawing 表格**及 **Markdown 管道表格**进行像素级精准对齐与重构排版。

---

## 🌟 核心特性

- 📏 **严格等宽字符宽度度量（East Asian Monospace Width）**：
  - 中文字符（CJK 汉字）、全角符号（`（）`、`【】`、`，`、`。`）及标准 Emoji（`🚀`、`✅`、`⭐` 等）按 **2 列宽**计算。
  - ASCII 字母、数字、半角标点符号及空格按 **1 列宽**计算。
  - 零宽字符（Zero-width joiners、Variation Selectors 等）按 **0 列宽**计算。
- 📦 **全边框样式支持（Unicode & ASCII Box Tables）**：
  - 单线边框（Single Box）：`┌─┬─┐`、`│ │ │`、`├─┼─┤`、`└─┴─┘`
  - 双线边框（Double Box）：`╔═╦═╗`、`║ ║ ║`、`╠═╬═╣`、`╚═╩═╝`
  - 圆角边框（Rounded Box）：`╭─┬─╮`、`│ │ │`、`├─┼─┤`、`╰─┴─╯`
  - 粗线边框（Heavy Box）：`┏━┳━┓`、`┃ ┃ ┃`、`┣━╋━┫`、`┗━┻━┛`
  - ASCII 网格（ASCII Box）：`+---+`、`|   |`、`+===+`
- 🏷️ **跨列大标题与智能连接符（Spanning Headers）**：
  - 自动识别顶部或段落居中的通栏大标题行，自动计算合并列宽并精准居中。
  - 依据上下行的列分布，动态生成符合拓扑结构的边框连接字符（`┬`、`┴`、`┼`、`─`）。
- 📝 **标准 Markdown 管道表格（GFM Pipe Table）**：
  - 支持 `| 列1 | 列2 |` 管道表格排版。
  - 自动识别并保留列对齐修饰符：`:---`（左对齐）、`:---:`（居中对齐）、`---:`（右对齐）。
- 💾 **保存时自动对齐（Auto Format on Save）**：
  - 在保存 `.md` 文件时自动扫描并对齐表格（可配置仅对齐代码块中的表格或全文表格）。
- 🎯 **智能上下文感知**：
  - 光标在表格内：仅格式化当前光标所在表格。
  - 选中区域：仅格式化选区覆盖的表格。
  - 无选区且光标在空白处：格式化全文所有表格。
- 🔌 **极致兼容性**：
  - 纯 Python 原生实现，无外部第三方依赖。
  - 完美兼容 **Sublime Text 3（Python 3.3+）** 及 **Sublime Text 4（Python 3.8+）**。

---

## 📸 对齐效果演示

### 示例 1：Unicode Box-drawing 表格（含跨列标题与中英混排）

#### 格式化前（字符数量不等导致的错位与锯齿）：
```text
┌───────────────────────────────────────────────────────────┐
│                 分布式系统架构组件矩阵                     │
├──────────────┬──────────────┬──────────────┬──────────────┤
│ 接入层 (Gateway)│ 计算服务 (Core)│ 存储引擎 (Storage)│ 监控告警 (Ops)│
│ API 路由与鉴权│ 业务逻辑处理集群│ 分布式事务与持久化│ 链路追踪与指标度量│
├──────────────┼──────────────┼──────────────┼──────────────┤
│ · gRPC / HTTP │ · 状态机引擎 │ · RocksDB 存储│ · OpenTelemetry│
│ · OAuth2 / JWT│ · 异步事件总线│ · Raft 共识协议│ · Prometheus  │
│ · 限流熔断器 │ · 工作流引擎  │ · 多副本同步机制│ · Grafana 看板 │
│ · 负载均衡分发│ · 弹性扩缩容  │ · 实时增量备份 │ · 智能异常预警 │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

#### 格式化后（严格等宽、边框与分隔线完美垂直对齐）：
```text
┌───────────────────────────────────────────────────────────────────────────────┐
│                            分布式系统架构组件矩阵                             │
├──────────────────┬──────────────────┬────────────────────┬────────────────────┤
│ 接入层 (Gateway) │ 计算服务 (Core)  │ 存储引擎 (Storage) │ 监控告警 (Ops)     │
│ API 路由与鉴权   │ 业务逻辑处理集群 │ 分布式事务与持久化 │ 链路追踪与指标度量 │
├──────────────────┼──────────────────┼────────────────────┼────────────────────┤
│ · gRPC / HTTP    │ · 状态机引擎     │ · RocksDB 存储     │ · OpenTelemetry    │
│ · OAuth2 / JWT   │ · 异步事件总线   │ · Raft 共识协议    │ · Prometheus       │
│ · 限流熔断器     │ · 工作流引擎     │ · 多副本同步机制   │ · Grafana 看板     │
│ · 负载均衡分发   │ · 弹性扩缩容     │ · 实时增量备份     │ · 智能异常预警     │
└──────────────────┴──────────────────┴────────────────────┴────────────────────┘
```

---

### 示例 2：标准 Markdown 管道表格（带对齐控制）

#### 格式化前：
```markdown
| 模块名称 | 开发状态 | 优先级 | 负责人 | 预期完成时间 |
|---|:---:|:---:|---|---|
| 用户认证中心 (SSO) | 进行中 | P0 | 张三 | 2026-Q3 |
| 高性能数据流管道 | 已完成 | P0 | 李四 / Bob | 2026-Q2 |
| 实时指标看板展示 | 待排期 | P1 | 王五 | 2026-Q4 |
| 多语言国际化支持 | 规划中 | P2 | Alice | 2027-Q1 |
```

#### 格式化后：
```markdown
| 模块名称           | 开发状态 | 优先级 | 负责人     | 预期完成时间 |
| ------------------ | :------: | :----: | ---------- | ------------ |
| 用户认证中心 (SSO) |  进行中  |   P0   | 张三       | 2026-Q3      |
| 高性能数据流管道   |  已完成  |   P0   | 李四 / Bob | 2026-Q2      |
| 实时指标看板展示   |  待排期  |   P1   | 王五       | 2026-Q4      |
| 多语言国际化支持   |  规划中  |   P2   | Alice      | 2027-Q1      |
```

---

## 🚀 安装指南

### 方法 1：手动安装 / 软链接（推荐）

1. 在 Sublime Text 顶部菜单栏点击 **`Preferences` -> `Browse Packages...`** 打开 `Packages` 目录。
2. 将此插件仓库克隆或软链接至该目录下，命名为 `md_table_format`：

**macOS**:
```bash
# 软链接方式
ln -s /path/to/md_table_format ~/Library/Application\ Support/Sublime\ Text/Packages/md_table_format

# 或通过 git clone
cd ~/Library/Application\ Support/Sublime\ Text/Packages/
git clone https://github.com/your-username/md_table_format.git
```

**Windows**:
```powershell
cd "$env:APPDATA\Sublime Text\Packages"
git clone https://github.com/your-username/md_table_format.git
```

**Linux**:
```bash
cd ~/.config/sublime-text/Packages/
git clone https://github.com/your-username/md_table_format.git
```

---

## ⌨️ 快捷键与使用方法

| 操作功能 | macOS 快捷键 | Windows / Linux 快捷键 |
| :--- | :--- | :--- |
| **格式化当前光标所在表格 / 选区表格** | `Super + Alt + T` (`⌘ + ⌥ + T`) | `Ctrl + Alt + T` |
| **格式化当前文件中所有表格** | `Super + Alt + Shift + T` | `Ctrl + Alt + Shift + T` |

### 1. 命令面板 (Command Palette)
按 `Cmd + Shift + P` (Mac) 或 `Ctrl + Shift + P` (Win/Linux)，输入关键字 `MD Table`：
- `MD Table Format: Format Table (Under Cursor / Selection)` —— 格式化当前/选中表格
- `MD Table Format: Format All Tables in Document` —— 格式化全文所有表格
- `MD Table Format: Toggle Auto Format on Save` —— 快捷开启/关闭保存自动格式化

### 2. 菜单集成
- **右键上下文菜单**：在任何 Markdown 文件中右键点击 `Format Markdown Table`。
- **主菜单栏**：`Edit` -> `MD Table Format`。

---

## ⚙️ 配置说明 (`MDTableFormat.sublime-settings`)

在 Sublime Text 中打开 `Preferences` -> `Package Settings` -> `MD Table Format` -> `Settings` 进行个性化调整：

```json
{
    // 是否在保存 Markdown 文件时自动格式化表格 (默认: true)
    "format_on_save": true,

    // 全文对齐或保存时：
    // - true: 仅对齐代码块（``` ... ```）中的表格
    // - false: 对齐 Markdown 文档中的所有表格（包含代码块内与正文表格）
    "format_in_code_blocks_only": false,

    // 是否启用 Unicode / ASCII Box 表格对齐
    "format_box_tables": true,

    // 是否启用 Markdown 管道表格对齐
    "format_pipe_tables": true,

    // 是否将 Unicode 歧义宽度字符（Ambiguous，如特殊引号、标点等）视作 2 列宽 (默认 false: 视作 1 列宽)
    "ambiguous_as_wide": false
}
```

---

## 🧪 单元测试

项目包含完整的单元测试，覆盖东亚宽字符度量、跨列居中大标题、各种边框样式与管道表格对齐。在项目根目录下运行：

```bash
python3 -m unittest discover tests -v
```

---

## 📄 License

MIT License © 2026
