#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Practice 板块总览 index.md 自动生成脚本
优化版：使用 common.py 公共模块
"""

import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, load_config, read_metadata, get_current_time,
    safe_write, progress_bar, format_completion, get_annual_goal
)

# ==================== 配置 ====================
PROJECT_ROOT = r"E:\youth-sandbox\docs"
PRACTICE_PATH = os.path.join(PROJECT_ROOT, "tech-study", "practice")

CHAPTERS = ['ctf', 'cve', 'lab', 'src']
CHAPTER_ICONS = {'ctf': '🏆', 'cve': '🛡️', 'lab': '🧪', 'src': '🎯'}
CHAPTER_NAMES = {'ctf': 'CTF', 'cve': 'CVE', 'lab': 'Lab', 'src': 'SRC'}

def read_chapter_metadata(chapter_path: str) -> dict:
    """读取章节的 index.md 的 Front Matter"""
    index_path = os.path.join(chapter_path, 'index.md')
    return read_metadata(index_path)

def get_status_icon(rate: int) -> str:
    """根据完成率返回状态图标"""
    if rate == 100:
        return "✅"
    elif rate > 0:
        return "🔄"
    else:
        return "⬜"

def get_motivation(rate: int) -> str:
    """根据完成率返回激励语"""
    if rate >= 80:
        return "🎉 太棒了！接近完成！"
    elif rate >= 50:
        return "💪 完成过半，继续加油！"
    elif rate >= 20:
        return "📈 有进展，保持节奏！"
    elif rate > 0:
        return "🚀 好的开始是成功的一半！"
    else:
        return "🌟 从第一题开始吧！"

def get_bounty_motivation(bounty: int, target: int) -> str:
    """根据奖金返回激励语"""
    if bounty >= target:
        return "🎉 恭喜达成目标！"
    elif bounty >= target * 0.5:
        return "💪 已经过半，距离目标不远了！"
    elif bounty >= target * 0.2:
        return "📈 进展不错，继续挖洞！"
    elif bounty >= target * 0.05:
        return "🚀 小有成就，保持热情！"
    elif bounty > 0:
        return "💰 第一笔奖金到手，继续加油！"
    else:
        return "🌟 提交第一个漏洞，开启奖金之路！"

def get_bounty_message() -> str:
    """随机返回奖金相关的名言"""
    import random
    messages = [
        "每一份漏洞报告都是价值的体现",
        "漏洞挖掘，贵在坚持",
        "技术创造价值，漏洞变奖金",
        "挖洞如挖宝，耐心是关键",
        "每一个提交都离目标更近一步"
    ]
    return random.choice(messages)

def get_recent_activities(chapter_data: dict) -> list:
    """生成近期动态列表"""
    activities = []
    for chapter in CHAPTERS:
        last_updated = chapter_data[chapter].get('last_updated', '')
        if last_updated:
            if isinstance(last_updated, datetime):
                last_updated_str = last_updated.strftime("%Y-%m-%d")
            else:
                last_updated_str = str(last_updated)[:10]
            
            icon = CHAPTER_ICONS[chapter]
            name = CHAPTER_NAMES[chapter]
            total = chapter_data[chapter]['total']
            completed = chapter_data[chapter]['completed']
            
            activities.append(f"- {icon} **{name}** 最后更新：{last_updated_str} ({completed}/{total})")
    
    activities.sort(reverse=True)
    return activities[:5]

def generate_practice_index(dry_run: bool = False) -> None:
    """生成 Practice 板块总览 index.md"""
    logger.info("=" * 60)
    logger.info("Practice 板块总览 index.md 生成")
    logger.info("=" * 60)
    logger.info(f"路径: {PRACTICE_PATH}")
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")
    
    if not os.path.exists(PRACTICE_PATH):
        logger.error(f"路径不存在: {PRACTICE_PATH}")
        return
    
    config = load_config()
    annual_goal = get_annual_goal()
    target_bounty = annual_goal.get('target_bounty', 100000)
    
    chapter_data = {}
    total_all = 0
    completed_all = 0
    in_progress_all = 0
    not_started_all = 0
    total_bounty = 0
    
    for chapter in CHAPTERS:
        chapter_path = os.path.join(PRACTICE_PATH, chapter)
        metadata = read_chapter_metadata(chapter_path)
        
        if chapter == 'src':
            total = metadata.get('total_targets', 0)
            completed = metadata.get('completed_targets', 0)
            in_progress = metadata.get('in_progress_targets', 0)
            not_started = metadata.get('not_started_targets', 0)
            bounty = metadata.get('total_bounty', 0)
            total_bounty += bounty
        else:
            total = metadata.get('total', 0)
            completed = metadata.get('completed', 0)
            in_progress = metadata.get('in_progress', 0)
            not_started = metadata.get('not_started', 0)
            bounty = 0
        
        completion_rate = int(completed / total * 100) if total > 0 else 0
        last_updated = metadata.get('last_updated', '')
        
        chapter_data[chapter] = {
            'total': total,
            'completed': completed,
            'in_progress': in_progress,
            'not_started': not_started,
            'completion_rate': completion_rate,
            'bounty': bounty,
            'last_updated': last_updated
        }
        
        total_all += total
        completed_all += completed
        in_progress_all += in_progress
        not_started_all += not_started
    
    completion_rate = int(completed_all / total_all * 100) if total_all > 0 else 0
    progress = progress_bar(completion_rate)
    bounty_progress = progress_bar(int(total_bounty / target_bounty * 100)) if target_bounty > 0 else "░░░░░░░░░░ 0%"
    
    # 生成板块表格
    rows = []
    for chapter in CHAPTERS:
        data = chapter_data[chapter]
        rate = data['completion_rate']
        status_icon = get_status_icon(rate)
        icon = CHAPTER_ICONS[chapter]
        name = CHAPTER_NAMES[chapter]
        rows.append(f"| {icon} {name} | {data['total']} | {data['completed']} | {rate}% | {status_icon} |")
    
    # 生成近期动态
    recent_activities = get_recent_activities(chapter_data)
    recent_activities_str = "\n".join(recent_activities) if recent_activities else "- 暂无更新记录"
    
    # 计算连胜天数（简单逻辑）
    def get_streak(last_updated):
        if not last_updated:
            return 0
        try:
            if isinstance(last_updated, datetime):
                last_date = last_updated.date()
            else:
                last_date = datetime.strptime(str(last_updated)[:10], "%Y-%m-%d").date()
            days = (datetime.now().date() - last_date).days
            return max(0, 7 - days) if days < 7 else 0
        except:
            return 0
    
    ctf_streak = get_streak(chapter_data['ctf'].get('last_updated', ''))
    src_streak = get_streak(chapter_data['src'].get('last_updated', ''))
    
    last_updated = get_current_time()
    
    # 构建内容
    content = f"""---
total_ctf: {chapter_data['ctf']['total']}
total_cve: {chapter_data['cve']['total']}
total_lab: {chapter_data['lab']['total']}
total_src: {chapter_data['src']['total']}
total_all: {total_all}
completed_ctf: {chapter_data['ctf']['completed']}
completed_cve: {chapter_data['cve']['completed']}
completed_lab: {chapter_data['lab']['completed']}
completed_src: {chapter_data['src']['completed']}
completed_all: {completed_all}
total_bounty: {total_bounty}
completion_rate: {completion_rate}
last_updated: {last_updated}
---

# 🎯 实战训练场

> CTF · CVE · Lab · SRC 实战记录汇总

## 📊 总览

| 指标 | 数值 | 进度 |
|------|:----:|:----:|
| 总题目/目标数 | {total_all} | 🎯 |
| ✅ 已完成 | {completed_all} | {format_completion(completed_all, total_all)} |
| 🔄 进行中 | {in_progress_all} | ⏳ |
| ⬜ 未开始 | {not_started_all} | 📋 |
| 整体完成率 | {progress} | {get_motivation(completion_rate)} |

## 📚 板块详情

| 板块 | 总数 | 已完成 | 完成率 | 状态 |
|------|:----:|:------:|:------:|:----:|
{chr(10).join(rows)}

## 💰 SRC 战果

| 指标 | 数值 | 目标 |
|------|:----:|:----:|
| 累计奖金 | 💰 {total_bounty} 元 | 🏆 {target_bounty} 元 |
| 完成度 | {bounty_progress} | {get_bounty_motivation(total_bounty, target_bounty)} |

> {get_bounty_message()}

## 🔥 当前连胜

- CTF 连续解题：{ctf_streak} 天
- SRC 连续提交：{src_streak} 天

## 📈 近期动态

{recent_activities_str}

## 🚀 快速入口

| 板块 | 链接 |
|------|------|
| 🏆 CTF | [ctf/](ctf/) |
| 🛡️ CVE | [cve/](cve/) |
| 🧪 Lab | [lab/](lab/) |
| 🎯 SRC | [src/](src/) |

---
*最后更新：{last_updated} | 保持热爱，持续输出 🚀*
"""
    
    output_path = os.path.join(PRACTICE_PATH, 'index.md')
    
    if safe_write(output_path, content, dry_run):
        logger.info(f"✅ 已生成: {output_path}")
        logger.info(f"   总题目/目标: {total_all}")
        logger.info(f"   已完成: {completed_all}, 完成率: {completion_rate}%")
        logger.info(f"   SRC累计奖金: {total_bounty} 元")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    generate_practice_index(dry_run)