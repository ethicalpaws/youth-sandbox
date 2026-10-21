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
    logger, read_metadata, get_current_time,
    safe_write, progress_bar, format_completion, get_annual_goal,
    get_practice_path, get_meta, safe_int
)

# ==================== 配置 ====================
PRACTICE_PATH = get_practice_path()

# 章节展示顺序；实际运行时只处理目录存在的章节
CHAPTERS = ['ctf', 'cve', 'lab', 'src']
CHAPTER_ICONS = {'ctf': '🏆', 'cve': '🛡️', 'lab': '🧪', 'src': '🎯'}
CHAPTER_NAMES = {'ctf': 'CTF', 'cve': 'CVE', 'lab': 'Lab', 'src': 'SRC'}

# 各章节 index.md 实际使用的字段名
CHAPTER_FIELDS = {
    'ctf': ('total_questions', 'completed_questions',
            'in_progress_questions', 'not_started_questions'),
    'cve': ('total_cves', 'analyzed', 'in_progress', 'not_started'),
    'lab': ('total_machines', 'completed_machines',
            'in_progress_machines', 'not_started_machines'),
    'src': ('total_targets', 'completed_targets',
            'in_progress_targets', 'not_started_targets'),
}

def get_existing_chapters() -> list:
    """返回实际存在目录的章节，避免引用已删除章节（如 src）"""
    return [
        chapter for chapter in CHAPTERS
        if os.path.isdir(os.path.join(PRACTICE_PATH, chapter))
    ]

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

def get_recent_activities(chapter_data: dict, chapters: list) -> list:
    """生成近期动态列表"""
    activities = []
    for chapter in chapters:
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

    chapters = get_existing_chapters()
    if not chapters:
        logger.error("未找到任何实战章节目录")
        return

    logger.info(f"包含章节: {', '.join(chapters)}")

    annual_goal = get_annual_goal()
    target_bounty = annual_goal.get('target_bounty', 100000)

    chapter_data = {}
    total_all = 0
    completed_all = 0
    in_progress_all = 0
    not_started_all = 0
    total_bounty = 0

    for chapter in chapters:
        chapter_path = os.path.join(PRACTICE_PATH, chapter)
        metadata = read_chapter_metadata(chapter_path)

        total_key, completed_key, in_progress_key, not_started_key = CHAPTER_FIELDS[chapter]
        total = safe_int(get_meta(metadata, total_key, 0))
        completed = safe_int(get_meta(metadata, completed_key, 0))
        in_progress = safe_int(get_meta(metadata, in_progress_key, 0))
        not_started = safe_int(get_meta(metadata, not_started_key, 0))
        bounty = safe_int(get_meta(metadata, 'total_bounty', 0)) if chapter == 'src' else 0
        total_bounty += bounty

        completion_rate = int(completed / total * 100) if total > 0 else 0
        last_updated = get_meta(metadata, 'last_updated', '')

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
    has_src = 'src' in chapters
    bounty_progress = (
        progress_bar(int(total_bounty / target_bounty * 100))
        if has_src and target_bounty > 0 else "░░░░░░░░░░ 0%"
    )

    # 生成板块表格
    rows = []
    for chapter in chapters:
        data = chapter_data[chapter]
        rate = data['completion_rate']
        status_icon = get_status_icon(rate)
        icon = CHAPTER_ICONS[chapter]
        name = CHAPTER_NAMES[chapter]
        rows.append(f"| {icon} {name} | {data['total']} | {data['completed']} | {rate}% | {status_icon} |")

    # 生成快速入口
    quick_links = "\n".join(
        f"| {CHAPTER_ICONS[chapter]} {CHAPTER_NAMES[chapter]} | "
        f"[{chapter}/]({chapter}/) |"
        for chapter in chapters
    )

    # 生成近期动态
    recent_activities = get_recent_activities(chapter_data, chapters)
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

    ctf_streak = get_streak(chapter_data['ctf'].get('last_updated', '')) if 'ctf' in chapters else 0
    src_streak = get_streak(chapter_data['src'].get('last_updated', '')) if has_src else 0

    streak_lines = [f"- CTF 连续解题：{ctf_streak} 天"]
    if has_src:
        streak_lines.append(f"- SRC 连续提交：{src_streak} 天")

    # SRC 章节被删除时不再渲染相关区块
    src_section = ""
    if has_src:
        src_section = f"""## 💰 SRC 战果

| 指标 | 数值 | 目标 |
|------|:----:|:----:|
| 累计奖金 | 💰 {total_bounty} 元 | 🏆 {target_bounty} 元 |
| 完成度 | {bounty_progress} | {get_bounty_motivation(total_bounty, target_bounty)} |

> {get_bounty_message()}

"""

    last_updated = get_current_time()

    # 只输出实际存在章节的统计字段
    front_matter_lines = []
    for chapter in chapters:
        front_matter_lines.append(f"total_{chapter}: {chapter_data[chapter]['total']}")
    front_matter_lines.append(f"total_all: {total_all}")
    for chapter in chapters:
        front_matter_lines.append(f"completed_{chapter}: {chapter_data[chapter]['completed']}")
    front_matter_lines.append(f"completed_all: {completed_all}")
    if has_src:
        front_matter_lines.append(f"total_bounty: {total_bounty}")
    front_matter_lines.append(f"completion_rate: {completion_rate}")
    front_matter_lines.append(f"last_updated: {last_updated}")
    front_matter = "\n".join(front_matter_lines)

    summary_desc = " · ".join(CHAPTER_NAMES[chapter] for chapter in chapters)

    # 构建内容
    content = f"""---
{front_matter}
---

# 🎯 实战训练场

> {summary_desc} 实战记录汇总

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

{src_section}## 🔥 当前连胜

{chr(10).join(streak_lines)}

## 📈 近期动态

{recent_activities_str}

## 🚀 快速入口

| 板块 | 链接 |
|------|------|
{quick_links}

---
*最后更新：{last_updated} | 保持热爱，持续输出 🚀*
"""

    output_path = os.path.join(PRACTICE_PATH, 'index.md')

    if safe_write(output_path, content, dry_run):
        logger.info(f"✅ 已生成: {output_path}")
        logger.info(f"   总题目/目标: {total_all}")
        logger.info(f"   已完成: {completed_all}, 完成率: {completion_rate}%")
        if has_src:
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
