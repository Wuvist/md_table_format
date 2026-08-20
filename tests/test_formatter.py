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
        self.assertEqual(str_width("分布式系统架构演进路线图"), 24)
        self.assertEqual(str_width("Phase 0 (M0)"), 12)
        self.assertEqual(str_width("概念验证与基线评测"), 18)

    def test_spanning_title_box_table(self):
        before = """┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               分布式系统架构演进路线图                                  │
├───────────────────┬───────────────────┬─────────────────────────┬───────────────────────┤
│ Phase 0 (M0)      │ Phase 1 (M1)      │ Phase 2 (M2)            │ Phase 3 (M3)          │
│ 原型验证与基线评估│ 单机系统与测试交付│ 企业级多租户集群体系    │ 生产级治理与全链路深化│
│ [第 1 ~ 4 周]     │ [第 5 ~ 10 周]    │ [第 11 ~ 16 周]         │ [第 17 周及以后]      │
├───────────────────┼───────────────────┼─────────────────────────┼───────────────────────┤
│ · 统一网关转发验证│ · 渠道连接池化管理│ · K8s + Ingress 网格    │ · 智能流量调度引擎    │
│ · 规则检测过滤引擎│ · 租户权限隔离体系│ · PG (RLS) + Redis 集群 │ · 多活数据同步控制机制│
│ · 性能基线压力测试│ · 基础模型推理集成│ · 账本核算与结算系统    │ · 统一权限 RBAC 治理  │
│ · 极简代理吞吐压测│ · 内存敏感数据脱敏│ · 自动化审批流服务      │ · 全链路熔断保护机制  │
│                   │ · 控制台管理仪表盘│ · 审计日志合规报表系统  │ · 国际化与企业 SSO 对接│
└───────────────────┴───────────────────┴─────────────────────────┴───────────────────────┘"""

        formatted = format_table_block(before)
        lines = formatted.splitlines()

        # Check every line has exactly the same display width
        widths = [str_width(l) for l in lines]
        self.assertTrue(len(set(widths)) == 1, "Lines have different display widths: {}".format(widths))

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

    def test_markdown_pipe_table(self):
        pipe_table = """| 阶段 | 状态 | 备注 |
| :--- | :---: | ---: |
| M0 概念验证 | 完成 | 一切正常 |
| M1 单机 MVP | 进行中 | 核心功能就绪 |"""
        formatted = format_table_block(pipe_table)
        lines = formatted.splitlines()
        # Delimiter row should preserve alignment markings (: for center and right)
        self.assertTrue(lines[1].startswith('|') and lines[1].endswith('|'))
        self.assertIn(':----:', lines[1])  # Center aligned column
        self.assertTrue(lines[1].rstrip(' |').endswith(':'))  # Right aligned column

    def test_generic_pipe_table(self):
        table = """| 模块名称 | 核心交付物 | 关键衡量指标 | 评审参与人 |
|---|---|---|---|
| **M0 (阶段一)** | 原型验证、网关代理、评测集报告 | P95 < 5ms，可用率 > 99.9% | 架构组、业务负责人 |
| **M1 (阶段二)** | 单机版核心系统、权限模块、Web 控制台 | 端到端功能闭环，压测达标 | 研发团队、产品经理、体验用户 |
| **M2 (阶段三)** | 多租户集群版、分布式存储、合规审计导出 | 高可用 99.99%，支持并发集群 | 运维/SRE、合规官、财务运营 |
| **M3 (阶段四)** | 智能动态路由、熔断自愈、生产正式发布 | 资源节省 30%+，故障自愈 < 3s | 决策层、各业务线主管 |"""

        formatted = format_table_block(table)
        lines = formatted.splitlines()

        # Check all lines have identical display width
        widths = [str_width(l) for l in lines]
        self.assertTrue(len(set(widths)) == 1, "Line widths differ: {}".format(widths))

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

