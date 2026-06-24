#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 章节级 index.md 自动生成脚本
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

# 章节级模板（完全保持原样）
CHAPTER_TEMPLATE = '''---
total_modules: {total_modules}
total_machines: {total_machines}
completed_machines: {completed_machines}
in_progress_machines: {in_progress_machines}
not_started_machines: {not_started_machines}
completion_rate: {completion_rate}
last_updated: {last_updated}
---

# 🎯 靶场训练场

> 各大平台靶场渗透记录

## 📊 整体进度

| 指标 | 数值 |
|------|:----:|
| 模块总数 | {total_modules} |
| 总靶场数 | {total_machines} |
| ✅ 已攻略 | {completed_machines} |
| 🔄 攻略中 | {in_progress_machines} |
| ⬜ 未开始 | {not_started_machines} |
| 整体完成率 | {progress_bar} |

## 📚 模块列表

| 模块 | 靶场数 | 已攻略 | 完成率 | 状态 |
|------|:------:|:------:|:------:|:----:|
{module_rows}

## 💡 渗透建议

1. **信息收集**：端口扫描、目录扫描、指纹识别
2. **漏洞利用**：寻找入口点，获取初始 shell
3. **提权**：SUID、内核漏洞、sudo 提权
4. **总结复盘**：记录关键步骤和技巧

## 🏆 里程碑

- [ ] 完成 5 个靶场 → 🎖️ 渗透新手
- [ ] 完成 10 个靶场 → 🏅 渗透进阶
- [ ] 完成 20 个靶场 → 🏆 渗透

## 📌 快速导航

| 模块 | 链接 |
|------|------|
{nav_rows}

## 📝 近期更新

{recent_updates}

---
*最后更新：{last_updated} | 保持练习，持续进步 💪*
'''

def generate_lab_chapter(dry_run: bool = False) -> None:
    """生成 Lab 章节 index.md"""
    logger.info("=" * 60)
    logger.info("Lab 章节级 index.md 生成")
    logger.info("=" * 60)
    logger.info(f"路径: {LAB_PATH}")
    
    if not os.path.exists(LAB_PATH):
        logger.error(f"路径不存在: {LAB_PATH}")
        return
    
    modules = [d for d in os.listdir(LAB_PATH)
               if os.path.isdir(os.path.join(LAB_PATH, d))
               and not d.startswith('.')]
    
    if not modules:
        logger.warning("未找到任何模块")
        return
    
    modules_data = []
    total_machines = 0
    completed_machines = 0
    in_progress_machines = 0
    not_started_machines = 0
    
    for name in modules:
        module_path = os.path.join(LAB_PATH, name)
        metadata = read_index_metadata(module_path)
        
        total = metadata.get('total', 0)
        completed = metadata.get('completed', 0)
        in_progress = metadata.get('in_progress', 0)
        not_started = metadata.get('not_started', 0)
        completion_rate = metadata.get('completion_rate', 0)
        last_updated = to_str(metadata.get('last_updated', ''))
        
        modules_data.append({
            'name': name,
            'title': name.upper(),
            'total': total,
            'completed': completed,
            'completion_rate': completion_rate,
            'last_updated': last_updated
        })
        
        total_machines += total
        completed_machines += completed
        in_progress_machines += in_progress
        not_started_machines += not_started
    
    completion_rate = int(completed_machines / total_machines * 100) if total_machines > 0 else 0
    progress = progress_bar(completion_rate)
    
    module_rows = []
    nav_rows = []
    for m in modules_data:
        if m['completion_rate'] == 100:
            status_icon = "✅"
        elif m['completion_rate'] > 0:
            status_icon = "🔄"
        else:
            status_icon = "⬜"
        
        module_rows.append(f"| {m['title']} | {m['total']} | {m['completed']} | {m['completion_rate']}% | {status_icon} |")
        nav_rows.append(f"| {m['title']} | [{m['name']}/]({m['name']}/) |")
    
    recent = [m for m in modules_data if m.get('last_updated')]
    recent.sort(key=lambda x: x['last_updated'], reverse=True)
    recent_lines = [f"- **{r['title']}** ({r['last_updated'][:10]}) : {r['completed']}/{r['total']} 靶场已完成"
                    for r in recent[:5]] or ["- 暂无更新记录"]
    
    last_updated = get_current_time()
    
    content = CHAPTER_TEMPLATE.format(
        total_modules=len(modules),
        total_machines=total_machines,
        completed_machines=completed_machines,
        in_progress_machines=in_progress_machines,
        not_started_machines=not_started_machines,
        completion_rate=completion_rate,
        progress_bar=progress,
        module_rows="\n".join(module_rows),
        nav_rows="\n".join(nav_rows),
        recent_updates="\n".join(recent_lines),
        last_updated=last_updated
    )
    
    output_path = os.path.join(LAB_PATH, 'index.md')
    
    if safe_write(output_path, content, dry_run):
        logger.info(f"✅ 已生成: {output_path}")
        logger.info(f"   模块数: {len(modules)}")
        logger.info(f"   总靶场: {total_machines}, 已攻略: {completed_machines}, 完成率: {completion_rate}%")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    generate_lab_chapter(dry_run)