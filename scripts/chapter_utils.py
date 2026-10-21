#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chapter_utils.py - 章节/模块索引生成的共享工具

供 07、08 等“目录层级与旧章节不同”的章节脚本复用：
- 读取目录下的直接笔记（排除 index.md）
- 读取直接子模块（排除纯图片目录）
- 生成笔记表格 / 子模块表格
- 写入模块级、章节级 index.md
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, read_metadata, get_meta, get_note_title, extract_heading,
    normalize_status, get_status_emoji, list_note_files, is_real_dir,
    collect_notes_recursive, calculate_module_stats,
    progress_bar, get_current_time, safe_write
)


def load_direct_notes(dir_path, title_map=None, heading_level=2):
    """读取目录下直接包含的笔记，返回统一结构"""
    title_map = title_map or {}
    notes = []

    for name in list_note_files(dir_path):
        path = os.path.join(dir_path, name)
        metadata = read_metadata(path)

        content = ''
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            pass

        fallback = name[:-3]
        title = title_map.get(name)
        if not title:
            if heading_level == 1:
                title = get_meta(metadata, 'title', '') or extract_heading(content, 1) or fallback
            else:
                title = get_note_title(metadata, content, fallback)

        description = get_meta(metadata, 'description', '') or ''
        status_cn = normalize_status(get_meta(metadata, 'status', '未开始'))
        finish_date = get_meta(metadata, 'finish-date', '') or ''

        notes.append({
            'file': name,
            'title': str(title).strip(),
            'description': str(description),
            'status_cn': status_cn,
            'finish_date': str(finish_date),
        })

    return notes


def render_notes_table(notes):
    """生成笔记表格（链接相对于当前 index.md）"""
    if not notes:
        return '| 笔记 | 描述 | 状态 |\n|------|------|:----:|\n| 暂无笔记 | - | - |'

    lines = [
        '| 笔记 | 描述 | 状态 |',
        '|------|------|:----:|',
    ]
    for note in notes:
        desc = note.get('description', '') or ''
        desc_short = desc[:60] + '...' if len(desc) > 60 else desc
        lines.append(
            f"| [{note['title']}]({note['file']}) | {desc_short} | "
            f"{get_status_emoji(note['status_cn'])} |"
        )
    return '\n'.join(lines)


def discover_child_modules(dir_path, display_name=None):
    """发现包含 Markdown 的直接子目录（忽略图片目录、空目录）"""
    if not os.path.isdir(dir_path):
        return []

    children = []
    for name in sorted(os.listdir(dir_path)):
        child_path = os.path.join(dir_path, name)
        if is_real_dir(child_path):
            notes = collect_notes_recursive(child_path)
            stats = calculate_module_stats(notes)
            children.append({
                'name': name,
                'display_name': display_name(name) if display_name else name,
                'path': child_path,
                'stats': stats,
            })
    return children


def render_modules_table(children):
    """生成子模块表格"""
    if not children:
        return '| 暂无模块 | - | - | - | - |\n|---|---|---|---|---|'

    lines = [
        '| 模块 | 笔记数 | 已完成 | 完成率 | 状态 |',
        '|------|:------:|:------:|:------:|:----:|',
    ]
    for child in children:
        stats = child['stats']
        lines.append(
            f"| [{child['display_name']}]({child['name']}/) | "
            f"{stats['total_notes']} | {stats['completed']} | "
            f"{stats['completion_rate']}% | {stats['module_status']} |"
        )
    return '\n'.join(lines)


MODULE_TEMPLATE = '''---
module_name: {module_name}
description: {description}
status: {module_status}
total_notes: {total_notes}
completed: {completed}
in_progress: {in_progress}
not_started: {not_started}
completion_rate: {completion_rate}
last_updated: {last_updated}
---

# {display_name}

> {description}

## 📊 学习统计

| 指标 | 数值 |
|------|:----:|
| 总笔记数 | {total_notes} |
| ✅ 已完成 | {completed} |
| 🔄 进行中 | {in_progress} |
| ⬜ 未开始 | {not_started} |
| 完成率 | {progress_bar} |

{body}

---
*自动更新：{update_time}
'''


def write_module_index(dir_path, display_name, description, title_map=None,
                       heading_level=2, child_display_name=None, dry_run=False):
    """生成单个目录的模块索引（笔记表 + 子模块表）"""
    notes = load_direct_notes(dir_path, title_map=title_map, heading_level=heading_level)
    children = discover_child_modules(dir_path, display_name=child_display_name)

    if not notes and not children:
        logger.warning(f"  跳过（无笔记/子模块）: {dir_path}")
        return None

    all_notes = collect_notes_recursive(dir_path)
    stats = calculate_module_stats(all_notes)

    sections = []
    if notes:
        sections.append('## 📖 学习内容\n\n' + render_notes_table(notes))
    if children:
        sections.append('## 📚 子模块\n\n' + render_modules_table(children))
    body = '\n\n'.join(sections)

    update_time = get_current_time()
    content = MODULE_TEMPLATE.format(
        module_name=display_name,
        display_name=display_name,
        description=description,
        module_status=stats['module_status'],
        total_notes=stats['total_notes'],
        completed=stats['completed'],
        in_progress=stats['in_progress'],
        not_started=stats['not_started'],
        completion_rate=stats['completion_rate'],
        progress_bar=progress_bar(stats['completion_rate']),
        body=body,
        update_time=update_time,
        last_updated=update_time,
    )

    index_path = os.path.join(dir_path, 'index.md')
    if safe_write(index_path, content, dry_run):
        logger.info(
            f"    ✅ {os.path.relpath(index_path, SCRIPT_DIR)} "
            f"(笔记 {stats['total_notes']}, 完成 {stats['completed']})"
        )
    return stats
