#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
07-server-side-component-security 章节级 index.md 自动生成脚本

该章节的笔记直接放在章节目录下（没有子模块目录），
因此只需生成 07/index.md，并忽略仅存放图片的同名目录。
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
from chapter_utils import load_direct_notes, render_notes_table


CHAPTER_PATH = os.path.join(get_knowledge_path(), "07-server-side-component-security")

CHAPTER_TEMPLATE = '''---
total_modules: 0
total_notes: {total_notes}
completed: {completed}
in_progress: {in_progress}
not_started: {not_started}
completion_rate: {completion_rate}
last_updated: {last_updated}
---

# 🧩 服务端组件安全

> Apache · Nginx · Tomcat · PHP · Node.js · Java Web 等服务端组件安全

## 📊 学习进度

| 指标 | 数值 |
|------|:----:|
| 笔记总数 | {total_notes} |
| ✅ 已完成 | {completed} |
| 🔄 进行中 | {in_progress} |
| ⬜ 未开始 | {not_started} |
| 完成率 | {progress_bar} |

## 📖 学习内容

{notes_table}

## 🗺️ 学习建议

1. **先理解容器模型**：Web 服务器、中间件、Web 容器的边界
2. **对比解析差异**：不同组件对扩展名、路径、编码的处理差异
3. **关注配置面**：默认配置、危险指令、错误配置导致的解析绕过
4. **结合 CVE**：将组件版本与公开漏洞关联验证

---
*最后更新：{update_time} | 组件安全，重在配置与解析细节 🔍*
'''


def generate_server_side_chapter(dry_run=False):
    logger.info("=" * 60)
    logger.info("07-server-side-component-security 章节级 index.md 生成")
    logger.info("=" * 60)
    logger.info(f"路径: {CHAPTER_PATH}")
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")

    if not os.path.isdir(CHAPTER_PATH):
        logger.error(f"路径不存在: {CHAPTER_PATH}")
        return

    notes = load_direct_notes(CHAPTER_PATH, heading_level=1)

    # 统计以实际笔记为准，避免读取不存在的模块索引
    stats = calculate_module_stats(collect_notes_recursive(CHAPTER_PATH))

    # 提示目录中的纯图片目录（不参与统计）
    ignored = [
        name for name in sorted(os.listdir(CHAPTER_PATH))
        if os.path.isdir(os.path.join(CHAPTER_PATH, name))
        and not is_real_dir(os.path.join(CHAPTER_PATH, name))
    ]
    if ignored:
        logger.info(f"   忽略非笔记目录: {', '.join(ignored)}")

    update_time = get_current_time()
    content = CHAPTER_TEMPLATE.format(
        total_notes=stats['total_notes'],
        completed=stats['completed'],
        in_progress=stats['in_progress'],
        not_started=stats['not_started'],
        completion_rate=stats['completion_rate'],
        progress_bar=progress_bar(stats['completion_rate']),
        notes_table=render_notes_table(notes),
        update_time=update_time,
        last_updated=update_time,
    )

    output_path = os.path.join(CHAPTER_PATH, 'index.md')
    if safe_write(output_path, content, dry_run):
        logger.info(f"✅ 已生成: {output_path}")
        logger.info(
            f"   笔记数: {stats['total_notes']}, 已完成: {stats['completed']}, "
            f"完成率: {stats['completion_rate']}%"
        )
    logger.info("=" * 60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()

    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    generate_server_side_chapter(dry_run)
