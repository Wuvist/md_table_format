# MD Table Format (Sublime Text Plugin)

专为 **Sublime Text 3 / 4** 打造的 Markdown 表格自动对齐插件。支持在编辑 Markdown 文件（特别是代码块中的 Unicode Box-drawing 表格及标准 Markdown 管道表格）时，按照**严格的等宽字体规则（1 个中文字符/全角字符/Emoji = 2 个英文字宽）**进行像素级精准对齐与重构。

---

## ✨ 核心特性

- 📏 **严格等宽字符宽度计算**：基于 Unicode East Asian Width 标准及 Emoji 范围精确度量，中文字符、全角标点、Emoji 均按 2 列宽计算，ASCII 字符按 1 列宽计算。
- 📦 **完美支持各种边框样式**：
  - 单线边框（Single Box）：`┌─┬─┐`、`│ │ │`、`├─┼─┤`、`└─┴─┘`
  - 双线边框（Double Box）：`╔═╦═╗`、`║ ║ ║`、`╠═╬═╣`、`╚═╩═╝`
  - 圆角边框（Rounded Box）：`╭─┬─╮`、`│ │ │`、`├─┼─┤`、`╰─┴─╯`
  - 粗线边框（Heavy Box）：`┏━┳━┓`、`┃ ┃ ┃`、`┣━╋━┫`、`┗━┻━┛`
  - ASCII 网格（ASCII Box）：`+---+`、`|   |`、`+===+`
- 🏷️ **支持复杂跨列标题 / 多列单元格（Colspan / Spanning Headers）**：能自动识别顶部/段落居中大标题行并自动计算总列宽、智能选择连接符（如 `┬`、`┴`、`┼`、`─`）。
- 📝 **支持 Markdown Pipe 管道表格**：`| 列1 | 列2 |` 以及对齐标识 `:---` (左)、`:---:` (中)、`---:` (右)。
- 💾 **保存时自动对齐（Auto Format on Save）**：编辑保存 `.md` 文件时自动扫描代码块/全文表格并格式化对齐。
- ⚡ **智能上下文处理**：
  - 光标在表格内：仅格式化当前光标所在的表格。
  - 有选区：格式化选区覆盖的所有表格。
  - 无选区且光标在空白处：格式化全文所有表格。

---

## 📸 效果展示

### 对齐前（jagged / 错位）:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               AI Relay 演进里程碑路线图                                  │
├───────────────────┬───────────────────┬─────────────────────────┬───────────────────────┤
│ Phase 0 (M0)      │ Phase 1 (M1)      │ Phase 2 (M2)            │ Phase 3 (M3)          │
│ 概念验证与基线评测│ 单机 MVP 与试点交付│ 企业级 SaaS 多租户集群   │ 生产级治理与生态深化  │
│ [第 1 ~ 4 周]     │ [第 5 ~ 10 周]    │ [第 11 ~ 16 周]         │ [第 17 周及以后]      │
├───────────────────┼───────────────────┼─────────────────────────┼───────────────────────┤
│ · 统一 API 转发验证│ · “API 铺”渠道池化│ · K8s + Envoy ExtProc   │ · 智能模型路由分类器  │
│ · L0 规则检测引擎 │ · N:N 租户权限体系│ · PG (RLS) + Redis 集群 │ · 跨境数据驻留严格控制│
│ · 基线模型横评集   │ · L1 ONNX 模型集成│ · 供应链/终端双边账本   │ · MCP 工具级 RBAC 治理│
│ · 极简代理吞吐测试│ · 双向脱敏与内存Vault│ · 用户申报工作流 (PICS) │ · Agent 死循环熔断器  │
│                   │ · SQLite-First 控制台│ · 零原文审计导出与合规报表│ · 国际化与 SSO 集成   │
└───────────────────┴───────────────────┴─────────────────────────┴───────────────────────┘
```

### 自动对齐后（perfect alignment）:

```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     AI Relay 演进里程碑路线图                                     │
├─────────────────────┬───────────────────────┬────────────────────────────┬────────────────────────┤
│ Phase 0 (M0)        │ Phase 1 (M1)          │ Phase 2 (M2)               │ Phase 3 (M3)           │
│ 概念验证与基线评测  │ 单机 MVP 与试点交付   │ 企业级 SaaS 多租户集群     │ 生产级治理与生态深化   │
│ [第 1 ~ 4 周]       │ [第 5 ~ 10 周]        │ [第 11 ~ 16 周]            │ [第 17 周及以后]       │
├─────────────────────┼───────────────────────┼────────────────────────────┼────────────────────────┤
│ · 统一 API 转发验证 │ · “API 铺”渠道池化    │ · K8s + Envoy ExtProc      │ · 智能模型路由分类器   │
│ · L0 规则检测引擎   │ · N:N 租户权限体系    │ · PG (RLS) + Redis 集群    │ · 跨境数据驻留严格控制 │
│ · 基线模型横评集    │ · L1 ONNX 模型集成    │ · 供应链/终端双边账本      │ · MCP 工具级 RBAC 治理 │
│ · 极简代理吞吐测试  │ · 双向脱敏与内存Vault │ · 用户申报工作流 (PICS)    │ · Agent 死循环熔断器   │
│                     │ · SQLite-First 控制台 │ · 零原文审计导出与合规报表 │ · 国际化与 SSO 集成    │
└─────────────────────┴───────────────────────┴────────────────────────────┴────────────────────────┘
```

---

## 🚀 安装方法

### 方式 1：手动安装（推荐）

1. 打开 Sublime Text，在菜单栏点击 `Preferences` -> `Browse Packages...` 打开 Packages 目录。
2. 将本项目克隆或复制到 Packages 目录下，目录名命名为 `md_table_format`：

**macOS**:
```bash
cd ~/Library/Application\ Support/Sublime\ Text/Packages/
# 或者 Sublime Text 3: cd ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/
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

| 操作 | macOS | Windows / Linux |
| :--- | :--- | :--- |
| **对齐当前表格 / 选区表格** | `Super + Alt + T` (`⌘ + ⌥ + T`) | `Ctrl + Alt + T` |
| **对齐当前文件所有表格** | `Super + Alt + Shift + T` | `Ctrl + Alt + Shift + T` |

### 命令面板 (Command Palette)

按 `Ctrl + Shift + P` (Win/Linux) 或 `Cmd + Shift + P` (Mac)，输入：
- `MD Table Format: Format Table (Under Cursor / Selection)`
- `MD Table Format: Format All Tables in Document`
- `MD Table Format: Toggle Auto Format on Save`

### 菜单栏与右键菜单

- **右键菜单**：在 Markdown 文件中右键，选择 `Format Markdown Table`。
- **主菜单**：`Edit` -> `MD Table Format`。

---

## ⚙️ 配置项 (`MDTableFormat.sublime-settings`)

在 Sublime Text 中打开 `Preferences` -> `Package Settings` -> `MD Table Format` -> `Settings` 进行配置：

```json
{
    // 是否在保存 Markdown 文件时自动对齐表格 (默认: true)
    "format_on_save": true,

    // 全文对齐或保存时：
    // true: 仅对齐代码块（``` ... ```）中的表格
    // false: 对齐整个 Markdown 文件中的所有表格（包括代码块内和代码块外）
    "format_in_code_blocks_only": false,

    // 是否对齐 Unicode / ASCII Box 表格
    "format_box_tables": true,

    // 是否对齐标准 Markdown 管道表格 (| a | b |)
    "format_pipe_tables": true,

    // 是否将 Unicode 'Ambiguous' 字符（如某些特殊标点符号）视为 2 个字符宽度 (默认 false: 视作 1 宽)
    "ambiguous_as_wide": false
}
```

---

## 🧪 运行单元测试

可在终端中运行内置单元测试验证功能完整性：

```bash
python3 -m unittest discover tests
```

---

## 📄 License

MIT License
