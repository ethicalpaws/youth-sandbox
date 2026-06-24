#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 模块级 index.md 自动生成脚本
优化版：使用 common.py 公共模块
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, load_config, read_index_metadata, get_current_time,
    safe_write, progress_bar, to_str
)

# ==================== 配置 ====================
PROJECT_ROOT = r"E:\youth-sandbox\docs"
LAB_PATH = os.path.join(PROJECT_ROOT, "tech-study", "practice", "lab")

# 模块级模板（完全保持原样）
MODULE_TEMPLATE = '''---
total: {total}
completed: {completed}
in_progress: {in_progress}
not_started: {not_started}
completion_rate: {completion_rate}
last_updated: {last_updated}
---

# 🎯 {module_title}

> {module_description}

## 📊 学习进度

| 指标 | 数值 |
|------|:----:|
| 总靶场 | {total} |
| ✅ 已攻略 | {completed} |
| 🔄 攻略中 | {in_progress} |
| ⬜ 未开始 | {not_started} |
| 完成率 | {progress_bar} |

## 📝 靶场列表

| 靶场 | 难度 | 状态 |
|------|:----:|:----:|
{rows}

## 💡 刷题建议

1. **由易到难**：先从简单靶场入手
2. **独立渗透**：尽量不依赖 WriteUp
3. **总结归纳**：记录关键步骤和技巧
4. **举一反三**：尝试多种提权方式

## 📌 快速导航

| 靶场 | 链接 |
|------|------|
{nav_rows}

## 📝 近期更新

{recent_updates}

---
*最后更新：{last_updated} | 保持练习，持续进步 💪*
'''

def normalize_status(status_raw):
    """将各种格式的状态统一为标准中文"""
    if status_raw in ['✅', '已完成', '完成']:
        return '已完成'
    elif status_raw in ['🔄', '进行中']:
        return '进行中'
    else:
        return '未开始'

def generate_module_index(module_path: str, module_name: str, dry_run: bool = False) -> bool:
    """生成单个模块的 index.md"""
    logger.info(f"\n处理模块: {module_name}")
    
    status_map = load_config().get('status_map', {})
    difficulty_config = load_config().get('difficulty_config', {})
    
    machines = [d for d in os.listdir(module_path)
                if os.path.isdir(os.path.join(module_path, d))
                and not d.startswith('.')]
    
    if not machines:
        logger.warning(f"  跳过：无靶场目录")
        return False
    
    machines_data = []
    for name in machines:
        machine_dir = os.path.join(module_path, name)
        metadata = read_index_metadata(machine_dir)
        
        title = metadata.get('title', name)
        status_raw = metadata.get('status', '未开始')
        status_cn = normalize_status(status_raw)
        difficulty = metadata.get('difficulty', '中等')
        last_updated = to_str(metadata.get('last_updated', ''))
        
        status_emoji = status_map.get(status_raw, '⬜')
        
        level = difficulty_config.get(difficulty, {}).get('level', '⭐⭐')
        
        machines_data.append({
            'name': name,
            'title': title,
            'status_cn': status_cn,
            'status_emoji': status_emoji,
            'difficulty': difficulty,
            'level': level,
            'last_updated': last_updated
        })
    
    total = len(machines_data)
    completed = sum(1 for m in machines_data if m['status_cn'] == '已完成')
    in_progress = sum(1 for m in machines_data if m['status_cn'] == '进行中')
    not_started = sum(1 for m in machines_data if m['status_cn'] == '未开始')
    completion_rate = int(completed / total * 100) if total > 0 else 0
    progress = progress_bar(completion_rate)
    
    rows = []
    nav_rows = []
    for m in sorted(machines_data, key=lambda x: (x['status_cn'] != '已完成', x['name'])):
        rows.append(f"| {m['title']} | {m['level']} | {m['status_emoji']} |")
        nav_rows.append(f"| {m['title']} | [{m['name']}/]({m['name']}/) |")
    
    recent = [m for m in machines_data if m.get('last_updated')]
    recent.sort(key=lambda x: x['last_updated'], reverse=True)
    recent_lines = [f"- **{r['title']}** ({r['last_updated'][:10]}) : {r['status_emoji']}"
                    for r in recent[:5]] or ["- 暂无更新记录"]
    
    last_updated = get_current_time()
    
    content = MODULE_TEMPLATE.format(
        module_title=f"{module_name} 靶场集",
        module_description=f"{module_name} 平台靶场渗透记录",
        total=total,
        completed=completed,
        in_progress=in_progress,
        not_started=not_started,
        completion_rate=completion_rate,
        progress_bar=progress,
        rows="\n".join(rows),
        nav_rows="\n".join(nav_rows),
        recent_updates="\n".join(recent_lines),
        last_updated=last_updated
    )
    
    output_path = os.path.join(module_path, 'index.md')
    
    if safe_write(output_path, content, dry_run):
        logger.info(f"  ✅ 已生成: {output_path}")
        logger.info(f"     总靶场: {total}, 已攻略: {completed}, 完成率: {completion_rate}%")
        return True
    
    return False

def scan_and_update(dry_run: bool = False) -> None:
    """扫描并更新所有 Lab 模块"""
    logger.info("=" * 60)
    logger.info("Lab 模块级 index.md 自动生成脚本")
    logger.info("=" * 60)
    logger.info(f"扫描路径: {LAB_PATH}")
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")
    
    if not os.path.exists(LAB_PATH):
        logger.error(f"路径不存在: {LAB_PATH}")
        return
    
    modules = [d for d in os.listdir(LAB_PATH)
               if os.path.isdir(os.path.join(LAB_PATH, d))
               and not d.startswith('.')]
    
    if not modules:
        logger.warning("未找到任何模块")
        return
    
    logger.info(f"发现模块: {modules}")
    
    success = 0
    for module_name in modules:
        module_path = os.path.join(LAB_PATH, module_name)
        if generate_module_index(module_path, module_name, dry_run):
            success += 1
    
    logger.info(f"\n完成！成功生成 {success}/{len(modules)} 个模块")
    logger.info("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    scan_and_update(dry_run)