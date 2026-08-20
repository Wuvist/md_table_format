"""
Table Formatter Engine for Sublime Text
Supports East Asian Monospace Width (Chinese/Japanese/Korean = 2, ASCII = 1),
Box-drawing tables (single, double, rounded, ascii), and Markdown pipe tables.
"""

import re
import unicodedata

# Box character styles
BOX_STYLES = {
    'single': {
        'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
        'h': '─', 'v': '│',
        'tm': '┬', 'bm': '┴', 'lm': '├', 'rm': '┤',
        'c': '┼'
    },
    'double': {
        'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝',
        'h': '═', 'v': '║',
        'tm': '╦', 'bm': '╩', 'lm': '╠', 'rm': '╣',
        'c': '╬'
    },
    'rounded': {
        'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯',
        'h': '─', 'v': '│',
        'tm': '┬', 'bm': '┴', 'lm': '├', 'rm': '┤',
        'c': '┼'
    },
    'heavy': {
        'tl': '┏', 'tr': '┓', 'bl': '┗', 'br': '┛',
        'h': '━', 'v': '┃',
        'tm': '┳', 'bm': '┻', 'lm': '┣', 'rm': '┫',
        'c': '╋'
    },
    'ascii': {
        'tl': '+', 'tr': '+', 'bl': '+', 'br': '+',
        'h': '-', 'v': '|',
        'tm': '+', 'bm': '+', 'lm': '+', 'rm': '+',
        'c': '+'
    }
}

BOX_CHARS_SET = set(
    '┌┐└┘─┬┴├┤┼'
    '╔╗╚╝═╦╩╠╣╬'
    '╭╮╰╯'
    '┏┓┗┛━┳┻┣┫╋'
    '╒╕╘╛╞╡╤╧╪'
    '╓╖╙╜╟╢╥╨╫'
    '+-|│║┃'
)

BOX_VERTICALS = set('│║┃|')
BOX_HORIZONTALS = set('─═━-')
BOX_LEFT_STARTS = set('┌╔╭┏├╠┣└╚╰┗+│║┃|')
BOX_RIGHT_ENDS = set('┐╗╮┓┤╣┫┘╝╯┛+│║┃|')


def char_width(ch, ambiguous_width=1):
    """
    Calculate visual display column width of a single character in monospace fonts.
    Chinese / Fullwidth / Ideographs / Emojis = 2
    ASCII / Halfwidth = 1
    Control / Non-spacing marks / Zero-width = 0
    Ambiguous = ambiguous_width (default 1)
    """
    code = ord(ch)

    # Zero width chars: format, control, variation selectors, zero-width joiner/space
    if code in (0x200B, 0x200C, 0x200D, 0xFEFF) or (0xFE00 <= code <= 0xFE0F):
        return 0
    if ch in ('\r', '\n', '\t'):
        return 1

    cat = unicodedata.category(ch)
    if cat.startswith('M') or cat in ('Cc', 'Cf'):
        return 0

    eaw = unicodedata.east_asian_width(ch)
    if eaw in ('W', 'F'):
        return 2
    if eaw == 'A':
        return ambiguous_width

    # Emoji & symbol range check for symbols not marked as W
    if (0x1F300 <= code <= 0x1FAFF) or (0x2600 <= code <= 0x27BF):
        return 2

    return 1


def str_width(s, ambiguous_width=1):
    """Calculate display width of a string in monospace font."""
    return sum(char_width(c, ambiguous_width) for c in s)


def detect_box_style(lines):
    """Detect box drawing style from lines."""
    text = '\n'.join(lines)
    if '╔' in text or '═' in text or '║' in text:
        return 'double'
    if '╭' in text or '╰' in text:
        return 'rounded'
    if '┏' in text or '━' in text or '┃' in text:
        return 'heavy'
    if '┌' in text or '─' in text or '│' in text:
        return 'single'
    return 'ascii'


def is_box_table_border(line):
    """Check if a stripped line is a horizontal border line of a box table."""
    s = line.strip()
    if not s or len(s) < 2:
        return False
    if not (s[0] in BOX_LEFT_STARTS and s[-1] in BOX_RIGHT_ENDS):
        return False
    # Must contain horizontal line characters
    if not any(c in BOX_HORIZONTALS for c in s):
        return False
    # All non-space characters must be valid box characters
    for c in s:
        if not c.isspace() and c not in BOX_CHARS_SET:
            return False
    return True


def is_box_table_data(line):
    """Check if a stripped line is a data row of a box table."""
    s = line.strip()
    if not s or len(s) < 2:
        return False
    # Must start and end with vertical characters
    if s[0] in BOX_VERTICALS and s[-1] in BOX_VERTICALS:
        return True
    return False


def is_box_table_line(line):
    """Check if a line looks like part of a box table."""
    return is_box_table_border(line) or is_box_table_data(line)


def is_pipe_table_delimiter(line):
    """Check if line is a markdown pipe table delimiter (|:---|:---:|---:|)."""
    s = line.strip()
    if not s:
        return False
    if s.startswith('|') and s.endswith('|'):
        inner = s[1:-1].strip()
    else:
        inner = s
    parts = inner.split('|')
    if not parts:
        return False
    for p in parts:
        seg = p.strip()
        if not seg:
            return False
        # Must only contain dashes, colons, spaces
        if not re.match(r'^:?-+:?$', seg):
            return False
    return True


def is_pipe_table_line(line):
    """Check if line is a markdown pipe table line."""
    s = line.strip()
    if not s or '|' not in s:
        return False
    if is_pipe_table_delimiter(line):
        return True
    # At least two pipes or pipe-enclosed
    if s.startswith('|') and s.endswith('|'):
        return True
    return False


class Cell:
    def __init__(self, raw_text, start_col, end_col, ambiguous_width=1):
        self.raw_text = raw_text
        self.content = raw_text.strip()
        self.start_col = start_col
        self.end_col = end_col
        self.ambiguous_width = ambiguous_width

        # Detect alignment from leading/trailing whitespace
        left_spaces = len(raw_text) - len(raw_text.lstrip(' '))
        right_spaces = len(raw_text) - len(raw_text.rstrip(' '))
        if not self.content:
            self.align = 'left'
        elif left_spaces >= 2 and right_spaces >= 2 and abs(left_spaces - right_spaces) <= 4:
            self.align = 'center'
        elif left_spaces >= 2 and right_spaces <= 1:
            self.align = 'right'
        else:
            self.align = 'left'

    @property
    def width(self):
        return str_width(self.content, self.ambiguous_width)


class BoxRow:
    def __init__(self, is_border=False, indent=''):
        self.is_border = is_border
        self.indent = indent
        self.cells = []
        self.raw_cells = []
        self.has_boundaries = set()


class BoxTable:
    """Formatter for Unicode / ASCII Box-drawing tables."""

    def __init__(self, lines, ambiguous_width=1):
        self.lines = lines
        self.ambiguous_width = ambiguous_width
        self.style = detect_box_style(lines)
        self.rows = []
        self.num_cols = 1
        self.parse()

    def parse(self):
        parsed_rows = []
        max_cols = 1

        for line in self.lines:
            s = line.strip()
            if not s:
                continue
            indent = line[:len(line) - len(line.lstrip(' '))]

            if is_box_table_border(line):
                row = BoxRow(is_border=True, indent=indent)
                # Count segments if any
                parts = [p for p in re.split(r'[┌╔╭┏├╠┣└╚╰┗┐╗╮┓┤╣┫┘╝╯┛┬╦┳┴╩┻┼╬╋+]', s) if p]
                if len(parts) > max_cols:
                    max_cols = len(parts)
                parsed_rows.append(row)
            elif is_box_table_data(line):
                row = BoxRow(is_border=False, indent=indent)
                v = s[0]
                # Strip leading and trailing vertical
                inner = s[1:-1]
                raw_cells = inner.split(v)
                row.raw_cells = raw_cells
                if len(raw_cells) > max_cols:
                    max_cols = len(raw_cells)
                parsed_rows.append(row)
            else:
                row = BoxRow(is_border=True, indent=indent)
                parsed_rows.append(row)

        self.num_cols = max(max_cols, 1)
        self.rows = parsed_rows

        # Assign column spans
        for row in self.rows:
            if not row.is_border and row.raw_cells:
                k = len(row.raw_cells)
                if k == self.num_cols:
                    for i, raw_c in enumerate(row.raw_cells):
                        row.cells.append(Cell(raw_c, i, i, self.ambiguous_width))
                        if i < self.num_cols - 1:
                            row.has_boundaries.add(i + 1)
                elif k == 1:
                    row.cells.append(Cell(row.raw_cells[0], 0, self.num_cols - 1, self.ambiguous_width))
                else:
                    span_size = self.num_cols // k
                    curr = 0
                    for idx, raw_c in enumerate(row.raw_cells):
                        end = curr + span_size - 1 if idx < k - 1 else self.num_cols - 1
                        row.cells.append(Cell(raw_c, curr, end, self.ambiguous_width))
                        if end < self.num_cols - 1:
                            row.has_boundaries.add(end + 1)
                        curr = end + 1

    def compute_col_widths(self):
        col_widths = [0] * self.num_cols

        # Pass 1: single column cells
        for row in self.rows:
            if not row.is_border:
                for cell in row.cells:
                    if cell.start_col == cell.end_col:
                        c = cell.start_col
                        # padding: at least 1 leading space + 1 trailing space if content exists
                        w = cell.width + 2
                        if w > col_widths[c]:
                            col_widths[c] = w

        for i in range(self.num_cols):
            if col_widths[i] < 3:
                col_widths[i] = 3

        # Pass 2: multi-column spanning cells
        for row in self.rows:
            if not row.is_border:
                for cell in row.cells:
                    if cell.start_col < cell.end_col:
                        a, b = cell.start_col, cell.end_col
                        curr_width = sum(col_widths[j] for j in range(a, b + 1)) + (b - a)
                        needed = cell.width + 2
                        if needed > curr_width:
                            diff = needed - curr_width
                            cols_count = b - a + 1
                            add_each = diff // cols_count
                            rem = diff % cols_count
                            for j in range(a, b + 1):
                                col_widths[j] += add_each + (1 if j - a < rem else 0)

        return col_widths

    def format(self):
        col_widths = self.compute_col_widths()
        bs = BOX_STYLES[self.style]
        v = bs['v']
        h = bs['h']

        out_lines = []
        for i, row in enumerate(self.rows):
            indent = row.indent
            if row.is_border:
                # Find previous data row and next data row
                prev_data = None
                for p in range(i - 1, -1, -1):
                    if not self.rows[p].is_border:
                        prev_data = self.rows[p]
                        break
                next_data = None
                for n in range(i + 1, len(self.rows)):
                    if not self.rows[n].is_border:
                        next_data = self.rows[n]
                        break

                if prev_data is None:
                    # Top border
                    left = bs['tl']
                    right = bs['tr']
                    parts = []
                    for c in range(self.num_cols):
                        parts.append(h * col_widths[c])
                        if c < self.num_cols - 1:
                            if next_data and (c + 1) in next_data.has_boundaries:
                                parts.append(bs['tm'])
                            else:
                                parts.append(h)
                    out_lines.append(indent + left + ''.join(parts) + right)
                elif next_data is None:
                    # Bottom border
                    left = bs['bl']
                    right = bs['br']
                    parts = []
                    for c in range(self.num_cols):
                        parts.append(h * col_widths[c])
                        if c < self.num_cols - 1:
                            if prev_data and (c + 1) in prev_data.has_boundaries:
                                parts.append(bs['bm'])
                            else:
                                parts.append(h)
                    out_lines.append(indent + left + ''.join(parts) + right)
                else:
                    # Middle border
                    left = bs['lm']
                    right = bs['rm']
                    parts = []
                    for c in range(self.num_cols):
                        parts.append(h * col_widths[c])
                        if c < self.num_cols - 1:
                            b_idx = c + 1
                            has_above = prev_data and b_idx in prev_data.has_boundaries
                            has_below = next_data and b_idx in next_data.has_boundaries
                            if has_above and has_below:
                                junc = bs['c']
                            elif not has_above and has_below:
                                junc = bs['tm']
                            elif has_above and not has_below:
                                junc = bs['bm']
                            else:
                                junc = h
                            parts.append(junc)
                    out_lines.append(indent + left + ''.join(parts) + right)
            else:
                # Data row
                cell_strs = []
                for cell in row.cells:
                    a, b = cell.start_col, cell.end_col
                    target_w = sum(col_widths[j] for j in range(a, b + 1)) + (b - a)
                    content = cell.content
                    w = str_width(content, self.ambiguous_width)
                    if not content:
                        formatted = ' ' * target_w
                    elif cell.align == 'center':
                        diff = target_w - w
                        left_pad = diff // 2
                        right_pad = diff - left_pad
                        formatted = ' ' * left_pad + content + ' ' * right_pad
                    elif cell.align == 'right':
                        diff = target_w - w
                        formatted = ' ' * (diff - 1) + content + ' ' if diff >= 1 else content
                    else:  # left
                        diff = target_w - w
                        formatted = ' ' + content + ' ' * (diff - 1) if diff >= 1 else content
                    cell_strs.append(formatted)
                out_lines.append(indent + v + v.join(cell_strs) + v)

        return '\n'.join(out_lines)


class PipeTable:
    """Formatter for Markdown Pipe tables."""

    def __init__(self, lines, ambiguous_width=1):
        self.lines = lines
        self.ambiguous_width = ambiguous_width
        self.indent = ''
        self.alignments = []  # 'left', 'center', 'right'
        self.rows = []  # list of list of strings
        self.delim_index = -1
        self.parse()

    def parse(self):
        raw_rows = []
        for idx, line in enumerate(self.lines):
            s = line.strip()
            if not s:
                continue
            if not self.indent:
                self.indent = line[:len(line) - len(line.lstrip(' '))]

            if s.startswith('|') and s.endswith('|'):
                inner = s[1:-1]
            elif s.startswith('|'):
                inner = s[1:]
            elif s.endswith('|'):
                inner = s[:-1]
            else:
                inner = s

            parts = [p.strip() for p in inner.split('|')]

            if is_pipe_table_delimiter(line) and self.delim_index == -1:
                self.delim_index = len(raw_rows)
                aligns = []
                for p in parts:
                    clean_p = p.strip()
                    if clean_p.startswith(':') and clean_p.endswith(':'):
                        aligns.append('center')
                    elif clean_p.endswith(':'):
                        aligns.append('right')
                    else:
                        aligns.append('left')
                self.alignments = aligns
                raw_rows.append(None)  # Placeholder for delimiter
            else:
                raw_rows.append(parts)

        # Determine number of columns
        max_cols = 1
        if self.alignments:
            max_cols = max(max_cols, len(self.alignments))
        for r in raw_rows:
            if r is not None:
                max_cols = max(max_cols, len(r))

        # Fill alignments if missing
        while len(self.alignments) < max_cols:
            self.alignments.append('left')

        # Normalize rows to have max_cols
        normalized = []
        for r in raw_rows:
            if r is None:
                normalized.append(None)
            else:
                while len(r) < max_cols:
                    r.append('')
                normalized.append(r)

        self.rows = normalized
        self.num_cols = max_cols

    def format(self):
        col_widths = [0] * self.num_cols

        for r in self.rows:
            if r is not None:
                for c, cell_text in enumerate(r):
                    w = str_width(cell_text, self.ambiguous_width)
                    if w > col_widths[c]:
                        col_widths[c] = w

        for c in range(self.num_cols):
            # minimum 3 for delimiter '---'
            if col_widths[c] < 3:
                col_widths[c] = 3

        out_lines = []
        for r in self.rows:
            if r is None:
                # Delimiter row
                delims = []
                for c in range(self.num_cols):
                    align = self.alignments[c]
                    w = col_widths[c]
                    if align == 'center':
                        d = ':' + '-' * max(1, w - 2) + ':' if w >= 2 else ':-:'
                    elif align == 'right':
                        d = '-' * max(1, w - 1) + ':'
                    else:
                        d = '-' * w
                    delims.append(d)
                out_lines.append(f"{self.indent}| {' | '.join(delims)} |")
            else:
                cells = []
                for c, cell_text in enumerate(r):
                    align = self.alignments[c]
                    w = col_widths[c]
                    tw = str_width(cell_text, self.ambiguous_width)
                    diff = max(0, w - tw)
                    if align == 'center':
                        left = diff // 2
                        right = diff - left
                        padded = ' ' * left + cell_text + ' ' * right
                    elif align == 'right':
                        padded = ' ' * diff + cell_text
                    else:
                        padded = cell_text + ' ' * diff
                    cells.append(padded)
                out_lines.append(f"{self.indent}| {' | '.join(cells)} |")

        return '\n'.join(out_lines)


def format_table_block(table_text, ambiguous_width=1):
    """Format a single table block (box table or pipe table)."""
    lines = table_text.strip('\r\n').splitlines()
    if not lines:
        return table_text

    # Priority 1: Check if markdown pipe table with delimiter
    if any(is_pipe_table_delimiter(l) for l in lines):
        table = PipeTable(lines, ambiguous_width=ambiguous_width)
        return table.format()

    # Priority 2: Check if unicode/ascii box table
    box_lines_count = sum(1 for line in lines if is_box_table_line(line))
    pipe_lines_count = sum(1 for line in lines if is_pipe_table_line(line))

    if box_lines_count >= len(lines) * 0.7:
        table = BoxTable(lines, ambiguous_width=ambiguous_width)
        return table.format()
    elif pipe_lines_count >= len(lines) * 0.7:
        table = PipeTable(lines, ambiguous_width=ambiguous_width)
        return table.format()

    return table_text


def find_table_ranges_in_text(text, in_code_blocks_only=False, format_box_tables=True, format_pipe_tables=True):
    """
    Find all table ranges (start_char, end_char, type, original_text) in a text.
    Respects in_code_blocks_only and table formats.
    """
    lines = text.splitlines(True)
    table_ranges = []

    # Map code blocks
    code_block_spans = []  # list of (start_line_idx, end_line_idx)
    in_code_block = False
    cb_fence = ''
    cb_fence_len = 0
    cb_start_idx = 0

    for idx, line in enumerate(lines):
        stripped = line.rstrip('\r\n')
        m = re.match(r'^[ \t]*(`{3,}|~{3,})', stripped)
        if m:
            curr_fence = m.group(1)
            if not in_code_block:
                in_code_block = True
                cb_fence = curr_fence[0]
                cb_fence_len = len(curr_fence)
                cb_start_idx = idx
            else:
                if stripped.strip().startswith(cb_fence * cb_fence_len):
                    in_code_block = False
                    code_block_spans.append((cb_start_idx + 1, idx - 1))

    # Determine eligible lines
    is_line_eligible = [True] * len(lines)
    if in_code_blocks_only:
        is_line_eligible = [False] * len(lines)
        for s_idx, e_idx in code_block_spans:
            for l in range(s_idx, min(e_idx + 1, len(lines))):
                is_line_eligible[l] = True

    def get_line_char_range(start_idx, count):
        s_offset = sum(len(lines[i]) for i in range(start_idx))
        e_offset = sum(len(lines[i]) for i in range(start_idx + count))
        return s_offset, e_offset

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        eligible = is_line_eligible[idx]

        is_box = format_box_tables and is_box_table_line(line) if eligible else False
        is_pipe = format_pipe_tables and is_pipe_table_line(line) if eligible else False

        if is_box:
            # Accumulate box table
            start_line = idx
            box_lines = []
            while idx < len(lines) and is_line_eligible[idx] and is_box_table_line(lines[idx]):
                box_lines.append(lines[idx])
                idx += 1
            if len(box_lines) >= 2:
                s_off, e_off = get_line_char_range(start_line, len(box_lines))
                table_ranges.append((s_off, e_off, 'box', ''.join(box_lines)))
            continue
        elif is_pipe:
            # Accumulate pipe table
            start_line = idx
            pipe_lines = []
            while idx < len(lines) and is_line_eligible[idx] and is_pipe_table_line(lines[idx]):
                pipe_lines.append(lines[idx])
                idx += 1
            if len(pipe_lines) >= 2 and any(is_pipe_table_delimiter(l) for l in pipe_lines):
                s_off, e_off = get_line_char_range(start_line, len(pipe_lines))
                table_ranges.append((s_off, e_off, 'pipe', ''.join(pipe_lines)))
            continue

        idx += 1

    return table_ranges


def format_markdown_document(text, in_code_blocks_only=False, ambiguous_width=1,
                             format_box_tables=True, format_pipe_tables=True):
    """
    Format all tables within a Markdown document.
    Preserves all surrounding text and code blocks.
    """
    ranges = find_table_ranges_in_text(
        text,
        in_code_blocks_only=in_code_blocks_only,
        format_box_tables=format_box_tables,
        format_pipe_tables=format_pipe_tables
    )

    if not ranges:
        return text

    # Replace from back to front to keep character offsets valid
    result = text
    for start_off, end_off, t_type, original_text in reversed(ranges):
        formatted = format_table_block(original_text, ambiguous_width=ambiguous_width)
        # Preserve original line ending style
        has_trailing_newline = original_text.endswith('\n') or original_text.endswith('\r\n')
        if has_trailing_newline and not formatted.endswith('\n'):
            formatted += '\n'
        result = result[:start_off] + formatted + result[end_off:]

    return result
