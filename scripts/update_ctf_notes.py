#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTF 板块题目级 index.md 自动生成脚本
优化版：使用 common.py 公共模块，功能与原脚本完全一致
"""

import os
import sys
from datetime import datetime

# 添加当前目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# 导入公共模块
from common import (
    logger, load_config, parse_front_matter, read_metadata,
    get_status_emoji, get_difficulty_config, get_current_date, get_file_mtime,
    safe_write, need_update, setup_from_args,
    get_meta, normalize_status, get_note_title,
    list_note_files, choose_primary_note, build_other_notes_table
)

# ==================== 配置 ====================
PROJECT_ROOT = r"E:\youth-sandbox\docs"
CTF_PATH = os.path.join(PROJECT_ROOT, "tech-study", "practice", "ctf")

# 模板（完全保持原样）
INDEX_TEMPLATE = '''---
title: {title}
description: {description}
tags: {tags}
status: {status_emoji}
difficulty: {difficulty}
exp: {exp}
level: {level}
achievement: {achievement}
weakness: {weakness}
finish-date: {finish_date}
last_updated: {last_updated}
---

# 🗡️ 狩猎记录 · {title}

---

### ⚔️ 目标档案

| 属性 | 数值 |
|------|------|
| `名称` | **{title}** |
| `弱点` | {weakness} |
| `威胁等级` | {level} |
| `状态` | {status_display} |

### 🏆 战利品

| 奖励 | 数量 |
|------|------|
| `经验值` | **+{exp} XP** ✨ |
| `成就` | {achievement} 🏅 |

---

### 📜 任务简报

{description}

### ⚡ 攻略要点

{key_points}

---

### 🔗 关联档案

[📖 详细战报 →]({note_file})

{other_notes}

---

<span style="animation: blink 1s step-end infinite; text-shadow: 0 0 5px #ff4500, 0 0 10px #ff0000;">🏴‍☠️</span> **QUEST COMPLETE** · {finish_date}

<style>
@keyframes blink {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.6; }}
}}
</style>
'''

def get_difficulty_conf(difficulty: str) -> dict:
    """获取难度配置（与原脚本逻辑一致）"""
    diff_config = get_difficulty_config()
    return diff_config.get(difficulty, {'exp': 20, 'level': '⭐⭐', 'achievement': '中等猎手'})

def generate_index_for_note(note_dir: str, note_file: str, note_files: list,
                            dry_run: bool = False) -> bool:
    """生成单个题目目录的 index.md（支持同一目录多篇笔记）"""
    note_path = os.path.join(note_dir, note_file)
    index_path = os.path.join(note_dir, 'index.md')

    logger.info(f"处理: {note_path}")

    try:
        with open(note_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.warning(f"  读取失败: {e}")
        return False

    metadata, rest = parse_front_matter(content)

    # 无 Front Matter 时用标题/文件名兜底，不再直接跳过
    title = get_note_title(metadata, rest, os.path.splitext(note_file)[0])

    # 提取字段（null / 空字符串统一走默认值）
    description = get_meta(metadata, 'description', '待补充')
    tags = get_meta(metadata, 'tags', [])
    status_cn = normalize_status(get_meta(metadata, 'status', '未开始'))
    finish_date = get_meta(metadata, 'finish-date', '')
    difficulty = get_meta(metadata, 'difficulty', '中等')
    weakness = get_meta(metadata, 'weakness', tags[0] if tags else '待补充')
    key_points = get_meta(metadata, 'key_points', '待补充')

    diff_conf = get_difficulty_conf(difficulty)
    exp = get_meta(metadata, 'exp', diff_conf.get('exp', 20))
    level = get_meta(metadata, 'level', diff_conf.get('level', '⭐⭐'))
    achievement = get_meta(metadata, 'achievement', diff_conf.get('achievement', '中等猎手'))

    status_emoji = get_status_emoji(status_cn)
    status_label = {'已完成': '已讨伐', '进行中': '进行中', '未开始': '未开始'}[status_cn]
    status_display = f"{status_emoji} **{status_label}**"
    other_notes = build_other_notes_table(note_dir, note_files, note_file)

    index_content = INDEX_TEMPLATE.format(
        title=title,
        description=description,
        tags=tags,
        status_emoji=status_emoji,
        difficulty=difficulty,
        exp=exp,
        level=level,
        achievement=achievement,
        weakness=weakness,
        finish_date=finish_date,
        last_updated=get_file_mtime(note_path),
        status_display=status_display,
        key_points=key_points,
        note_file=note_file,
        other_notes=other_notes
    )

    return safe_write(index_path, index_content, dry_run)

def scan_and_update(dry_run: bool = False) -> None:
    """扫描并更新所有 CTF 题目"""
    logger.info("=" * 60)
    logger.info("CTF 板块题目级 index.md 自动生成脚本")
    logger.info("=" * 60)
    logger.info(f"扫描路径: {CTF_PATH}")
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")
    
    if not os.path.exists(CTF_PATH):
        logger.error(f"路径不存在: {CTF_PATH}")
        return
    
    success_count = 0
    skip_count = 0
    
    for root, dirs, files in os.walk(CTF_PATH):
        if root == CTF_PATH:
            continue
        
        note_files = list_note_files(root)
        if not note_files:
            continue

        # 多笔记目录：优先有 title/status 的笔记，其次 *_wp.md，最后按文件名
        note_file = choose_primary_note(root, note_files)

        if generate_index_for_note(root, note_file, note_files, dry_run):
            success_count += 1
        else:
            skip_count += 1
    
    logger.info("=" * 60)
    logger.info(f"完成！成功生成 {success_count} 个，跳过 {skip_count} 个")
    logger.info("=" * 60)

if __name__ == "__main__":
    # 支持命令行参数
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    scan_and_update(dry_run=dry_run)