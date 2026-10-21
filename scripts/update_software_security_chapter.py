#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
08-software-system-security 章节级 index.md 自动生成脚本

汇总 basic、buffer-overflow 等模块的统计信息，生成 08/index.md。
模块页由 update_software_security_modules.py 先生成。
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, get_knowledge_path, collect_notes_recursive,
    calculate_module_stats, progress_bar, get_current_time,
    safe_write, is_real_dir
)
from chapter_utils import discover_child_modules


CHAPTER_PATH = os.path.join(get_knowledge_path(), "08-software-system-security")

MODULE_META = {
    'basic': ('📘', '基础', '计算机存储空间、汇编/栈/寄存器基础'),
    'buffer-overflow': ('💥', '缓冲区溢出', '栈溢出、堆利用、其他溢出与防御机制'),
    'fuzzing': ('🎲', '模糊测试', 'Fuzzing 相关笔记（待补充）'),
}

CHAPTER_TEMPLATE = '''---
total_modules: {total_modules}
total_notes: {total_notes}
completed: {completed}
in_progress: {in_progress}
not_started: {not_started}
completion_rate: {completion_rate}
last_updated: {last_updated}
---

# 💥 软件系统安全

> 缓冲区溢出 · 栈/堆利用 · 格式化字符串 · 整数溢出 · 防御机制

## 📊 学习进度

| 指标 | 数值 |
|------|:----:|
| 模块数 | {total_modules} |
| 笔记总数 | {total_notes} |
| ✅ 已完成 | {completed} |
| 🔄 进行中 | {in_progress} |
| ⬜ 未开始 | {not_started} |
| 完成率 | {progress_bar} |

## 📚 模块列表

| 模块 | 笔记数 | 已完成 | 完成率 | 状态 |
|------|:------:|:------:|:------:|:----:|
{module_rows}

## 🗺️ 学习路线

1. **基础**：计算机存储空间 → 汇编/寄存器 → 栈帧结构
2. **栈溢出**：ret2text → ret2shellcode → ret2libc → ROP
3. **堆利用**：堆基础 → UAF → double-free → fastbin → unlink
4. **其他溢出**：格式化字符串 → 整数溢出
5. **防御机制**：ASLR、CFI、Canary、NX/PIE 及绕过思路

## 🛠️ 常用工具

| 工具 | 用途 |
|------|------|
| pwntools | exploit 编写 |
| pwndbg / GEF | GDB 调试增强 |
| checksec | 二进制保护检查 |
| cyclic | 偏移量计算 |
| one_gadget | libc 利用 |

---
*最后更新：{update_time} | 从内存布局到控制流劫持，循序渐进 🧠*
'''


def get_module_display(name):
    return MODULE_META.get(name, ('📁', name, f'{name} 学习笔记'))


def generate_software_security_chapter(dry_run=False):
    logger.info("=" * 60)
    logger.info("08-software-system-security 章节级 index.md 生成")
    logger.info("=" * 60)
    logger.info(f"路径: {CHAPTER_PATH}")
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")

    if not os.path.isdir(CHAPTER_PATH):
        logger.error(f"路径不存在: {CHAPTER_PATH}")
        return

    modules = discover_child_modules(CHAPTER_PATH)
    if not modules:
        logger.warning("未找到任何包含笔记的模块目录")
        return

    # 汇总统计以实际笔记为准
    stats = calculate_module_stats(collect_notes_recursive(CHAPTER_PATH))

    rows = []
    for module in modules:
        icon, title, _ = get_module_display(module['name'])
        m = module['stats']
        rows.append(
            f"| {icon} [{title}]({module['name']}/) | {m['total_notes']} | "
            f"{m['completed']} | {m['completion_rate']}% | {m['module_status']} |"
        )

    ignored = [
        name for name in sorted(os.listdir(CHAPTER_PATH))
        if os.path.isdir(os.path.join(CHAPTER_PATH, name))
        and not is_real_dir(os.path.join(CHAPTER_PATH, name))
    ]
    if ignored:
        logger.info(f"   忽略非笔记目录: {', '.join(ignored)}")

    update_time = get_current_time()
    content = CHAPTER_TEMPLATE.format(
        total_modules=len(modules),
        total_notes=stats['total_notes'],
        completed=stats['completed'],
        in_progress=stats['in_progress'],
        not_started=stats['not_started'],
        completion_rate=stats['completion_rate'],
        progress_bar=progress_bar(stats['completion_rate']),
        module_rows='\n'.join(rows),
        update_time=update_time,
        last_updated=update_time,
    )

    output_path = os.path.join(CHAPTER_PATH, 'index.md')
    if safe_write(output_path, content, dry_run):
        logger.info(f"✅ 已生成: {output_path}")
        logger.info(
            f"   模块数: {len(modules)}, 笔记数: {stats['total_notes']}, "
            f"已完成: {stats['completed']}, 完成率: {stats['completion_rate']}%"
        )
    logger.info("=" * 60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()

    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    generate_software_security_chapter(dry_run)
