"""
Unit tests for Table Formatter
"""

import unittest
from table_formatter import (
    char_width,
    str_width,
    BoxTable,
    PipeTable,
    format_table_block,
    format_markdown_document,
    find_table_ranges_in_text
)


class TestTableFormatter(unittest.TestCase):

    def test_east_asian_width(self):
        # ASCII
        self.assertEqual(char_width('a'), 1)
        self.assertEqual(char_width('1'), 1)
        self.assertEqual(char_width(' '), 1)
        # Chinese
        self.assertEqual(char_width('中'), 2)
        self.assertEqual(char_width('文'), 2)
        # Fullwidth
        self.assertEqual(char_width('（'), 2)
        self.assertEqual(char_width('【'), 2)
        # Emojis
        self.assertEqual(char_width('🚀'), 2)
        self.assertEqual(char_width('✅'), 2)

        # String width
        self.assertEqual(str_width("AI Relay 演进里程碑路线图"), 25)
        self.assertEqual(str_width("Phase 0 (M0)"), 12)
        self.assertEqual(str_width("概念验证与基线评测"), 18)

    def test_user_example_roadmap_table(self):
        before = """┌─────────────────────────────────────────────────────────────────────────────────────────┐
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
└───────────────────┴───────────────────┴─────────────────────────┴───────────────────────┘"""

        formatted = format_table_block(before)
        lines = formatted.splitlines()

        # Check every line has exactly the same display width
        widths = [str_width(l) for l in lines]
        self.assertTrue(len(set(widths)) == 1, f"Lines have different display widths: {widths}")

        # Check column dividers align vertically across all rows
        # Line 0 is top border, Line 2 is middle border
        # Check that '│' dividers are at the exact same column positions
        data_lines = [l for l in lines if l.startswith('│')]
        # Multi-column data lines should have same divider positions
        four_col_data_lines = [l for l in data_lines if l.count('│') == 5]
        self.assertTrue(len(four_col_data_lines) > 0)

        div_positions = []
        for l in four_col_data_lines:
            # calculate display position of each '│'
            pos = 0
            cur_positions = []
            for ch in l:
                if ch == '│':
                    cur_positions.append(pos)
                pos += char_width(ch)
            div_positions.append(cur_positions)

        for p in div_positions[1:]:
            self.assertEqual(div_positions[0], p, "Vertical dividers not aligned!")

    def test_double_box_table(self):
        before = """╔═════════════╦═════════════╗
║ 任务名称    ║ 进度        ║
╠═════════════╬═════════════╣
║ 架构设计    ║ 100% 完成   ║
║ 编码实现    ║ 80%         ║
╚═════════════╩═════════════╝"""
        formatted = format_table_block(before)
        lines = formatted.splitlines()
        widths = [str_width(l) for l in lines]
        self.assertTrue(len(set(widths)) == 1)
        self.assertTrue(lines[0].startswith('╔') and lines[0].endswith('╗'))
        self.assertTrue(lines[-1].startswith('╚') and lines[-1].endswith('╝'))

    def test_rounded_box_table(self):
        before = """╭──────┬──────╮
│ 项目 │ 负责人 │
├──────┼──────┤
│ 后端 │ 张三 │
│ 前端 │ 李四 │
╰──────┴──────╯"""
        formatted = format_table_block(before)
        lines = formatted.splitlines()
        widths = [str_width(l) for l in lines]
        self.assertTrue(len(set(widths)) == 1)
        self.assertTrue(lines[0].startswith('╭') and lines[0].endswith('╮'))
        self.assertTrue(lines[-1].startswith('╰') and lines[-1].endswith('╯'))

    def test_user_pipe_table(self):
        user_table = """| 里程碑 | 关键交付物 | 核心衡量指标 | 评审参与人 |
|---|---|---|---|
| **M0 (第4周末)** | POC 代理、L0 规则库、评测集报告 | L0 P95 < 2ms，召回率 > 99% | 架构师、合规顾问 |
| **M1 (第10周末)** | 单机版 MVP、级联护栏、API铺与基础计费、Web UI | 护栏 P95 < 120ms，端到端功能闭环 | 研发团队、产品经理、首批内测用户 |
| **M2 (第16周末)** | 多租户集群版、PG/Redis、FinOps 报表、PCPD 审计导出 | 可用性 99.95%，支持 50+ 企业租户并发 | 运维/SRE、合规官、财务运营 |
| **M3 (第20周末)** | 动态意图路由、Agent 熔断、Envoy ExtProc、商用上线 | 智能路由节省 30%+ 成本，故障自愈 < 3s | 决策层、业务线负责人 |"""

        formatted = format_table_block(user_table)
        lines = formatted.splitlines()

        # Check all lines have identical display width
        widths = [str_width(l) for l in lines]
        self.assertTrue(len(set(widths)) == 1, f"Line widths differ: {widths}")

        # Check delimiter line uses | and dashes
        self.assertTrue(lines[1].startswith('|') and lines[1].endswith('|'))
        self.assertNotIn('+', lines[1])

        # Check pipes | are at exact identical positions
        pipe_positions = []
        for l in lines:
            pos = 0
            cur = []
            for ch in l:
                if ch == '|':
                    cur.append(pos)
                pos += char_width(ch)
            pipe_positions.append(cur)

        for p in pipe_positions[1:]:
            self.assertEqual(pipe_positions[0], p, "Markdown pipe vertical lines not aligned!")


    def test_markdown_document_with_code_blocks(self):
        doc = """# Markdown Title

Here is some roadmap inside code block:

```
┌─────────────────┬─────────────────┐
│ 模块名称        │ 负责人          │
├─────────────────┼─────────────────┤
│ 数据引擎 (Go)   │ 张三            │
│ 界面设计        │ Alice           │
└─────────────────┴─────────────────┘
```

Some python code:

```python
def foo():
    return "bar"
```

End of document.
"""
        formatted = format_markdown_document(doc, in_code_blocks_only=True)
        self.assertIn('def foo():', formatted)
        self.assertIn('模块名称', formatted)

        # Check table inside is aligned
        ranges = find_table_ranges_in_text(formatted, in_code_blocks_only=True)
        self.assertEqual(len(ranges), 1)
        _, _, _, tbl_text = ranges[0]
        tbl_lines = tbl_text.splitlines()
        widths = [str_width(l) for l in tbl_lines]
    def test_ascii_table(self):
        before = """+------------+------------+
| Column A   | Column B   |
+============+============+
| 中文测试   | Value 1    |
| 12345      | 测试 2     |
+------------+------------+"""
        formatted = format_table_block(before)
        lines = formatted.splitlines()
        widths = [str_width(l) for l in lines]
        self.assertTrue(len(set(widths)) == 1)

    def test_empty_cells(self):
        before = """┌──────┬──────┐
│ A    │      │
├──────┼──────┤
│      │ B    │
└──────┴──────┘"""
        formatted = format_table_block(before)
        lines = formatted.splitlines()
        widths = [str_width(l) for l in lines]
        self.assertTrue(len(set(widths)) == 1)

    def test_multi_table_document(self):
        doc = """# Heading

```markdown
┌──────┬──────┐
│ 第一 │ 第二 │
├──────┼──────┤
│ 1    │ 2    │
└──────┴──────┘
```

Some text in between.

```
╔══════╦══════╗
║ 苹果 ║ 香蕉 ║
╠══════╬══════╣
║ $10  ║ $5   ║
╚══════╩══════╝
```
"""
        formatted = format_markdown_document(doc, in_code_blocks_only=True)
        ranges = find_table_ranges_in_text(formatted, in_code_blocks_only=True)
        self.assertEqual(len(ranges), 2)


if __name__ == '__main__':
    unittest.main()

