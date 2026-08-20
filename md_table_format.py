"""
Sublime Text Plugin: MD Table Format
Auto-formats and aligns Markdown Box-drawing and Pipe tables with strict East Asian monospace width calculation.
"""

import sys

try:
    import sublime
    import sublime_plugin
except ImportError:
    # Running outside Sublime Text (e.g. CLI/tests)
    sublime = None
    sublime_plugin = object

try:
    from .table_formatter import (
        format_table_block,
        format_markdown_document,
        is_box_table_line,
        is_pipe_table_line,
        find_table_ranges_in_text,
    )
except ImportError:
    from table_formatter import (
        format_table_block,
        format_markdown_document,
        is_box_table_line,
        is_pipe_table_line,
        find_table_ranges_in_text,
    )


SETTINGS_FILE = "MDTableFormat.sublime-settings"


def get_settings():
    if sublime is None:
        return {}
    return sublime.load_settings(SETTINGS_FILE)


def is_markdown_view(view):
    """Check if the given Sublime view is a Markdown file."""
    if view is None:
        return False
    # Check syntax scope
    syntax = view.scope_name(0)
    if "text.html.markdown" in syntax or "source.gfm" in syntax or "text.markdown" in syntax:
        return True
    # Check file name extension
    file_name = view.file_name()
    if file_name:
        fn_lower = file_name.lower()
        if fn_lower.endswith((".md", ".markdown", ".mdown", ".mkd", ".mdwn", ".mdtxt")):
            return True
    return False


def get_ambiguous_width(settings):
    ambiguous_as_wide = settings.get("ambiguous_as_wide", False)
    return 2 if ambiguous_as_wide else 1


if sublime is not None:

    class MdTableFormatCommand(sublime_plugin.TextCommand):
        """
        Format table under cursor, tables in selected regions, or all tables in the file.
        """

        def run(self, edit, silent=False):
            view = self.view
            settings = get_settings()
            ambiguous_w = get_ambiguous_width(settings)
            format_box = settings.get("format_box_tables", True)
            format_pipe = settings.get("format_pipe_tables", True)
            code_blocks_only = settings.get("format_in_code_blocks_only", False)

            full_text = view.substr(sublime.Region(0, view.size()))
            selections = list(view.sel())

            # Check if any selection is non-empty
            has_selection = any(not sel.empty() for sel in selections)

            if has_selection:
                # Format tables intersecting the selected regions
                table_ranges = find_table_ranges_in_text(
                    full_text,
                    in_code_blocks_only=False,
                    format_box_tables=format_box,
                    format_pipe_tables=format_pipe,
                )
                formatted_count = 0
                for start_off, end_off, t_type, original_text in reversed(table_ranges):
                    tbl_region = sublime.Region(start_off, end_off)
                    if any(sel.intersects(tbl_region) for sel in selections):
                        formatted = format_table_block(original_text, ambiguous_width=ambiguous_w)
                        has_trailing_nl = original_text.endswith("\n") or original_text.endswith("\r\n")
                        if has_trailing_nl and not formatted.endswith("\n"):
                            formatted += "\n"
                        view.replace(edit, tbl_region, formatted)
                        formatted_count += 1

                if not silent:
                    view.window().status_message(f"MD Table Format: Formatted {formatted_count} selected table(s)")
                return

            # If no selection, check if cursor is currently inside a table
            cursor_pt = selections[0].begin() if selections else 0
            cur_line_region = view.line(cursor_pt)
            cur_line_text = view.substr(cur_line_region)

            is_cur_box = is_box_table_line(cur_line_text)
            is_cur_pipe = is_pipe_table_line(cur_line_text)

            if is_cur_box or is_cur_pipe:
                # Expand upwards and downwards to find table boundaries
                start_line_reg = cur_line_region
                end_line_reg = cur_line_region

                # Scan up
                while start_line_reg.begin() > 0:
                    prev_line_reg = view.line(start_line_reg.begin() - 1)
                    prev_text = view.substr(prev_line_reg)
                    if is_cur_box and is_box_table_line(prev_text):
                        start_line_reg = prev_line_reg
                    elif is_cur_pipe and is_pipe_table_line(prev_text):
                        start_line_reg = prev_line_reg
                    else:
                        break

                # Scan down
                while end_line_reg.end() < view.size():
                    next_line_reg = view.line(end_line_reg.end() + 1)
                    next_text = view.substr(next_line_reg)
                    if is_cur_box and is_box_table_line(next_text):
                        end_line_reg = next_line_reg
                    elif is_cur_pipe and is_pipe_table_line(next_text):
                        end_line_reg = next_line_reg
                    else:
                        break

                table_region = sublime.Region(start_line_reg.begin(), end_line_reg.end())
                table_text = view.substr(table_region)
                formatted = format_table_block(table_text, ambiguous_width=ambiguous_w)
                view.replace(edit, table_region, formatted)
                if not silent:
                    view.window().status_message("MD Table Format: Table aligned")
                return

            # Otherwise, format all tables in the file
            formatted_doc = format_markdown_document(
                full_text,
                in_code_blocks_only=code_blocks_only,
                ambiguous_width=ambiguous_w,
                format_box_tables=format_box,
                format_pipe_tables=format_pipe,
            )
            if formatted_doc != full_text:
                view.replace(edit, sublime.Region(0, view.size()), formatted_doc)
                if not silent:
                    view.window().status_message("MD Table Format: All tables aligned")
            else:
                if not silent:
                    view.window().status_message("MD Table Format: No unaligned tables found")


    class MdTableFormatAllCommand(sublime_plugin.TextCommand):
        """
        Format all tables in the current document.
        """

        def run(self, edit, silent=False):
            view = self.view
            settings = get_settings()
            ambiguous_w = get_ambiguous_width(settings)
            format_box = settings.get("format_box_tables", True)
            format_pipe = settings.get("format_pipe_tables", True)
            code_blocks_only = settings.get("format_in_code_blocks_only", False)

            full_text = view.substr(sublime.Region(0, view.size()))
            formatted_doc = format_markdown_document(
                full_text,
                in_code_blocks_only=code_blocks_only,
                ambiguous_width=ambiguous_w,
                format_box_tables=format_box,
                format_pipe_tables=format_pipe,
            )
            if formatted_doc != full_text:
                view.replace(edit, sublime.Region(0, view.size()), formatted_doc)
                if not silent:
                    view.window().status_message("MD Table Format: All tables formatted")
            else:
                if not silent:
                    view.window().status_message("MD Table Format: No unaligned tables found")


    class MdTableFormatEventListener(sublime_plugin.EventListener):
        """
        Event listener to auto-format tables on save if enabled.
        """

        def on_pre_save(self, view):
            if not is_markdown_view(view):
                return
            settings = get_settings()
            if not settings.get("format_on_save", False):
                return

            view.run_command("md_table_format_all", {"silent": True})


    class MdTableFormatToggleSaveCommand(sublime_plugin.ApplicationCommand):
        """
        Toggle the format_on_save setting on or off.
        """

        def run(self):
            settings = get_settings()
            current = settings.get("format_on_save", False)
            new_val = not current
            settings.set("format_on_save", new_val)
            sublime.save_settings(SETTINGS_FILE)
            status = "enabled" if new_val else "disabled"
            sublime.status_message(f"MD Table Format: Format on save is now {status}")
