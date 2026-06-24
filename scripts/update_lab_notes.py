#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 板块题目级 index.md 自动生成脚本
优化版：使用 common.py 公共模块，功能与原脚本完全一致
"""

import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, load_config, parse_front_matter, read_metadata,
    get_status_emoji, get_difficulty_config, get_current_date,
    safe_write, need_update
)

# ==================== 配置 ====================
PROJECT_ROOT = r"E:\youth-sandbox\docs"
LAB_PATH = os.path.join(PROJECT_ROOT, "tech-study", "practice", "lab")

# Lab 模板（完全保持原样）
LAB_TEMPLATE = '''---
title: {title}
description: {description}
tags: {tags}
status: {status_emoji}
difficulty: {difficulty}
platform: {platform}
key_points: {key_points}
highlights: {highlights}
---

# 🎯 靶场记录 · {title}

---

### 📋 靶场档案

| 属性 | 数值 |
|------|------|
| `靶场名称` | **{title}** |
| `平台` | {platform} |
| `难度` | {level} |
| `状态` | {status_display} |

### 🏆 战利品

| 奖励 | 数量 |
|------|------|
| `经验值` | **+{exp} XP** ✨ |
| `成就` | {achievement} 🏅 |

---

### 📜 靶场描述

{description}

### ⚡ 渗透步骤

{key_points}

### 💡 关键点

{highlights}

---

### 🔗 关联档案

[📖 详细报告 →]({note_file})

---

<span style="animation: blink 1s step-end infinite; text-shadow: 0 0 5px #00cc66, 0 0 10px #009955;">🏴‍☠️</span> **TARGET COMPROMISED** · {finish_date}

<style>
@keyframes blink {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.6; }}
}}
</style>
'''

def get_difficulty_conf(difficulty: str) -> dict:
    """获取难度配置"""
    diff_config = get_difficulty_config()
    return diff_config.get(difficulty, {'exp': 20, 'level': '⭐⭐', 'achievement': '中等猎手'})

def generate_index_for_note(note_dir: str, note_file: str, dry_run: bool = False) -> bool:
    """生成单个 Lab 笔记的 index.md"""
    note_path = os.path.join(note_dir, note_file)
    index_path = os.path.join(note_dir, 'index.md')
    
    logger.info(f"处理: {note_path}")
    
    try:
        with open(note_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.warning(f"  读取失败: {e}")
        return False
    
    metadata, _ = parse_front_matter(content)
    
    if not metadata:
        logger.warning(f"  跳过：无 Front Matter")
        return False
    
    title = metadata.get('title')
    if not title:
        title = os.path.basename(note_dir)
    
    description = metadata.get('description', '')
    tags = metadata.get('tags', [])
    status_cn = metadata.get('status', '未开始')
    finish_date = metadata.get('finish-date', datetime.now().strftime("%Y-%m-%d"))
    difficulty = metadata.get('difficulty', '中等')
    platform = metadata.get('platform', '未知')
    key_points = metadata.get('key_points', '待补充')
    highlights = metadata.get('highlights', '待补充')
    
    # 获取配置
    diff_conf = get_difficulty_conf(difficulty)
    exp = metadata.get('exp', diff_conf.get('exp', 20))
    level = metadata.get('level', diff_conf.get('level', '⭐⭐'))
    achievement = metadata.get('achievement', diff_conf.get('achievement', '中等猎手'))
    
    status_emoji = get_status_emoji(status_cn)
    status_display = f"{status_emoji} **已攻略**" if status_cn == '已完成' else f"{status_emoji} **攻略中**"
    
    index_content = LAB_TEMPLATE.format(
        title=title,
        description=description,
        tags=tags,
        status_emoji=status_emoji,
        difficulty=difficulty,
        platform=platform,
        key_points=key_points,
        highlights=highlights,
        level=level,
        exp=exp,
        achievement=achievement,
        status_display=status_display,
        note_file=note_file,
        finish_date=finish_date
    )
    
    return safe_write(index_path, index_content, dry_run)

def scan_and_update(dry_run: bool = False) -> None:
    """扫描并更新所有 Lab 笔记"""
    logger.info("=" * 60)
    logger.info("Lab 板块题目级 index.md 自动生成脚本")
    logger.info("=" * 60)
    logger.info(f"扫描路径: {LAB_PATH}")
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")
    
    if not os.path.exists(LAB_PATH):
        logger.error(f"路径不存在: {LAB_PATH}")
        return
    
    success_count = 0
    skip_count = 0
    
    for root, dirs, files in os.walk(LAB_PATH):
        if root == LAB_PATH:
            continue
        
        note_files = [f for f in files if f.endswith('_wp.md')]
        if not note_files:
            note_files = [f for f in files if f.endswith('.md') and f != 'index.md']
        
        if not note_files:
            continue
        
        note_file = note_files[0]
        
        if generate_index_for_note(root, note_file, dry_run):
            success_count += 1
        else:
            skip_count += 1
    
    logger.info("=" * 60)
    logger.info(f"完成！成功生成 {success_count} 个，跳过 {skip_count} 个")
    logger.info("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    scan_and_update(dry_run)