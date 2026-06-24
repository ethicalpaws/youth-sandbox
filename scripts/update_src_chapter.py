#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRC 章节级 index.md 自动生成脚本
优化版：使用 common.py 公共模块
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, load_config, read_index_metadata, get_current_time,
    safe_write, progress_bar, to_str, get_annual_goal, get_src_achievements
)

# ==================== 配置 ====================
PROJECT_ROOT = r"E:\youth-sandbox\docs"
SRC_PATH = os.path.join(PROJECT_ROOT, "tech-study", "practice", "src")

# 章节级模板（完全保持原样）
CHAPTER_TEMPLATE = '''---
total_modules: {total_modules}
total_targets: {total_targets}
completed_targets: {completed_targets}
in_progress_targets: {in_progress_targets}
not_started_targets: {not_started_targets}
completion_rate: {completion_rate}
total_bounty: {total_bounty}
critical_count: {critical_count}
high_count: {high_count}
medium_count: {medium_count}
low_count: {low_count}
last_updated: {last_updated}
---

# 🎯 SRC 漏洞挖掘

> 各大 SRC 平台真实漏洞挖掘记录 | 目标：年入 10w 💰

## 📊 整体战果

| 指标 | 数值 | 目标 |
|------|:----:|:----:|
| 覆盖平台 | {total_modules} | - |
| 总目标数 | {total_targets} | 🎯 {target_targets} |
| ✅ 已提交 | {completed_targets} | - |
| 🔄 挖掘中 | {in_progress_targets} | - |
| 累计奖金 | 💰 {total_bounty} 元 | 🏆 {target_bounty} 元 |
| 完成度 | {progress_bar} | - |

## 🏆 漏洞等级分布

| 等级 | 数量 | 奖金参考 |
|------|:----:|:--------:|
| 🔴 严重 | {critical_count} | {critical_ref} |
| 🟠 高危 | {high_count} | {high_ref} |
| 🟡 中危 | {medium_count} | {medium_ref} |
| 🔵 低危 | {low_count} | {low_ref} |

## 📚 平台详情

| 平台 | 目标数 | 已提交 | 奖金 | 进度 |
|------|:------:|:------:|:----:|:----:|
{module_rows}

## 💰 年度目标追踪

- 当前累计：💰 {total_bounty} 元
- 距 {target_bounty} 目标还差：💰 {remaining_bounty} 元
- 预计还需挖 {estimated_vulns} 个高危漏洞

## 🎖️ 成就系统

{achievements}

## 💡 挖掘心得

> 漏洞挖掘不仅是技术，更是耐心和细心的考验。

- 🎯 **目标选择**：优先选择资产丰富、更新频繁的站点
- 🔍 **信息收集**：子域名、端口、目录、JS 泄露
- ⚡ **快速验证**：先跑工具，再手动深入
- 📝 **报告质量**：清晰描述、完整复现步骤、合理定级

## 📌 快速导航

| 平台 | 链接 |
|------|------|
{nav_rows}

## 📝 近期战报

{recent_updates}

---
*最后更新：{last_updated} | 保持热爱，挖洞不止 💰*
'''

def get_achievements(total_bounty: int) -> str:
    """根据累计奖金生成成就"""
    achievements = []
    src_achievements = get_src_achievements()
    
    # 复制并移除 default
    achievements_dict = src_achievements.copy()
    default = achievements_dict.pop('default', '🔰 新手入门')
    
    for threshold_str, achievement in sorted(achievements_dict.items()):
        try:
            threshold = int(threshold_str)
            if total_bounty >= threshold:
                achievements.append(achievement)
        except ValueError:
            continue
    
    if not achievements:
        achievements.append(default)
    
    return " ".join(achievements)

def generate_src_chapter(dry_run: bool = False) -> None:
    """生成 SRC 章节 index.md"""
    logger.info("=" * 60)
    logger.info("SRC 章节级 index.md 生成")
    logger.info("=" * 60)
    logger.info(f"路径: {SRC_PATH}")
    
    if not os.path.exists(SRC_PATH):
        logger.error(f"路径不存在: {SRC_PATH}")
        return
    
    config = load_config()
    annual_goal = get_annual_goal()
    target_bounty = annual_goal.get('target_bounty', 100000)
    target_targets = annual_goal.get('target_targets', 50)
    bounty_ref = annual_goal.get('bounty_reference', {})
    
    modules = [d for d in os.listdir(SRC_PATH)
               if os.path.isdir(os.path.join(SRC_PATH, d))
               and not d.startswith('.')]
    
    if not modules:
        logger.warning("未找到任何模块")
        return
    
    modules_data = []
    total_targets = 0
    completed_targets = 0
    in_progress_targets = 0
    not_started_targets = 0
    total_bounty = 0
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    
    for name in modules:
        module_path = os.path.join(SRC_PATH, name)
        metadata = read_index_metadata(module_path)
        
        total = metadata.get('total', 0)
        completed = metadata.get('completed', 0)
        in_progress = metadata.get('in_progress', 0)
        not_started = metadata.get('not_started', 0)
        completion_rate = metadata.get('completion_rate', 0)
        bounty = metadata.get('bounty', 0)
        last_updated = to_str(metadata.get('last_updated', ''))
        
        critical_count += metadata.get('critical_count', 0)
        high_count += metadata.get('high_count', 0)
        medium_count += metadata.get('medium_count', 0)
        low_count += metadata.get('low_count', 0)
        
        modules_data.append({
            'name': name,
            'title': name.upper(),
            'total': total,
            'completed': completed,
            'completion_rate': completion_rate,
            'bounty': bounty,
            'last_updated': last_updated
        })
        
        total_targets += total
        completed_targets += completed
        in_progress_targets += in_progress
        not_started_targets += not_started
        total_bounty += bounty
    
    completion_rate = int(completed_targets / total_targets * 100) if total_targets > 0 else 0
    progress = progress_bar(completion_rate)
    
    remaining_bounty = max(0, target_bounty - total_bounty)
    estimated_vulns = int(remaining_bounty / 3000) if remaining_bounty > 0 else 0
    
    achievements = get_achievements(total_bounty)
    
    module_rows = []
    nav_rows = []
    for m in modules_data:
        if m['completion_rate'] == 100:
            status_icon = "✅"
        elif m['completion_rate'] > 0:
            status_icon = "🔄"
        else:
            status_icon = "⬜"
        
        bounty_str = f"💰 {m['bounty']}" if m['bounty'] > 0 else "-"
        module_rows.append(f"| {m['title']} | {m['total']} | {m['completed']} | {bounty_str} | {status_icon} |")
        nav_rows.append(f"| {m['title']} | [{m['name']}/]({m['name']}/) |")
    
    recent = [m for m in modules_data if m.get('last_updated')]
    recent.sort(key=lambda x: x['last_updated'], reverse=True)
    recent_lines = [f"- **{r['title']}** ({r['last_updated'][:10]}) : {r['completed']}/{r['total']} 目标已完成"
                    for r in recent[:5]] or ["- 暂无更新记录"]
    
    last_updated = get_current_time()
    
    content = CHAPTER_TEMPLATE.format(
        total_modules=len(modules),
        total_targets=total_targets,
        completed_targets=completed_targets,
        in_progress_targets=in_progress_targets,
        not_started_targets=not_started_targets,
        completion_rate=completion_rate,
        progress_bar=progress,
        total_bounty=total_bounty,
        target_bounty=target_bounty,
        target_targets=target_targets,
        remaining_bounty=remaining_bounty,
        estimated_vulns=estimated_vulns,
        achievements=achievements,
        critical_count=critical_count,
        critical_ref=bounty_ref.get('严重', '5000-10000元'),
        high_count=high_count,
        high_ref=bounty_ref.get('高危', '2000-5000元'),
        medium_count=medium_count,
        medium_ref=bounty_ref.get('中危', '500-2000元'),
        low_count=low_count,
        low_ref=bounty_ref.get('低危', '50-500元'),
        module_rows="\n".join(module_rows),
        nav_rows="\n".join(nav_rows),
        recent_updates="\n".join(recent_lines),
        last_updated=last_updated
    )
    
    output_path = os.path.join(SRC_PATH, 'index.md')
    
    if safe_write(output_path, content, dry_run):
        logger.info(f"✅ 已生成: {output_path}")
        logger.info(f"   平台数: {len(modules)}")
        logger.info(f"   总目标: {total_targets}, 已提交: {completed_targets}, 完成率: {completion_rate}%")
        logger.info(f"   累计奖金: {total_bounty} 元, 距目标还差: {remaining_bounty} 元")
        logger.info(f"   成就: {achievements}")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    generate_src_chapter(dry_run)