#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
06-red-blue-confrontation 章节级 index.md 自动生成脚本
优化版：使用 common.py 公共模块
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, load_config, read_index_metadata, get_current_time,
    safe_write, progress_bar, get_knowledge_path,
    get_meta, normalize_status, collect_notes_recursive,
    calculate_module_stats, is_real_dir
)

# ==================== 配置 ====================
KNOWLEDGE_PATH = get_knowledge_path()
CHAPTER_PATH = os.path.join(KNOWLEDGE_PATH, "06-red-blue-confrontation")

# 模块分类（红队/蓝队）
RED_TEAM_MODULES = [
    'c2-framework',
    'evasion',
    'hvv',
    'internal-network',
    'persistence',
    'pivoting',
    'privesc',
    'pwn',
    'tools'
]

BLUE_TEAM_MODULES = [
    'blue-team'
]

# 模块显示名称
MODULE_NAMES = {
    'blue-team': '蓝队防御',
    'c2-framework': 'C2框架',
    'evasion': '免杀与绕过',
    'hvv': 'HVV 攻防演练',
    'internal-network': '内网渗透',
    'lateral-movement': '横向移动',
    'penetration-test': '渗透测试',
    'persistence': '权限维持',
    'pivoting': '隧道与代理',
    'privesc': '权限提升',
    'pwn': '二进制安全',
    'tools': '渗透工具'
}

def get_display_name(module_name: str) -> str:
    return MODULE_NAMES.get(module_name.lower(), MODULE_NAMES.get(module_name, module_name))

# 模板
CHAPTER_TEMPLATE = '''---
total_modules: {total_modules}
total_notes: {total_notes}
completed: {completed}
in_progress: {in_progress}
not_started: {not_started}
completion_rate: {completion_rate}
description: {description}
last_updated: {last_updated}
---

# 🔴🟦 红蓝对抗

> {description}

## ⚔️ 攻防态势

| 阵营 | 模块 | 笔记数 | 状态 |
|:---:|------|:------:|:----:|
{module_rows}

## 📊 战况统计

| 指标 | 数值 |
|------|:----:|
| 总模块数 | {total_modules} |
| 总笔记数 | {total_notes} |
| ✅ 已完成 | {completed} |
| 🔄 进行中 | {in_progress} |
| ⬜ 未开始 | {not_started} |
| 整体完成率 | {progress_bar} |

## 🔗 常用武器库

| 类别 | 工具 | 用途 |
|:---|:---|:---|
| 信息收集 | Nmap, BloodHound, ADExplorer | 资产发现、域信息收集 |
| 漏洞利用 | MSF, Cobalt Strike | 渗透框架 |
| 横向移动 | PsExec, WMI, Impacket | 内网扩散 |
| 权限维持 | Mimikatz, Rubeus | 凭证窃取、票据攻击 |
| 免杀 | ShellcodeLoader, Donut | AV/EDR绕过 |

## 💡 红蓝寄语

> 🔴 红队：知道如何攻击，才知道如何防御
> 🟦 蓝队：知道如何防御，才知道攻击的弱点
> ⚔️ 知己知彼，百战不殆

## 🏆 战绩里程碑

- [ ] 完成 3 个模块 → 🎖️ 红蓝新手
- [ ] 完成 6 个模块 → 🏅 红蓝战士
- [ ] 完成 9 个模块 → 🏆 红蓝精英
- [ ] 完成全部模块 → 👑 红蓝大师

---
*最后更新：{update_time} | 保持攻防思维，持续进化 💪*
'''

def generate_redblue_chapter(dry_run: bool = False) -> None:
    """生成红蓝对抗章节 index.md"""
    logger.info("=" * 60)
    logger.info("06-red-blue-confrontation 章节级 index.md 生成")
    logger.info("=" * 60)
    logger.info(f"路径: {CHAPTER_PATH}")
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")
    
    if not os.path.exists(CHAPTER_PATH):
        logger.error(f"路径不存在: {CHAPTER_PATH}")
        return
    
    modules = [d for d in sorted(os.listdir(CHAPTER_PATH))
               if is_real_dir(os.path.join(CHAPTER_PATH, d))]

    if not modules:
        logger.warning("未找到任何模块")
        return

    modules_data = []
    total_notes = 0
    completed = 0
    in_progress = 0
    not_started = 0

    for module_name in modules:
        module_path = os.path.join(CHAPTER_PATH, module_name)
        metadata = read_index_metadata(module_path)

        module_total = get_meta(metadata, 'total_notes', 0)
        module_completed = get_meta(metadata, 'completed', 0)
        module_in_progress = get_meta(metadata, 'in_progress', 0)
        module_not_started = get_meta(metadata, 'not_started', 0)
        module_status = get_meta(metadata, 'status', '')

        # 模块索引缺失或统计为空时，直接从笔记重新汇总
        if not module_total:
            notes_data = collect_notes_recursive(module_path)
            if notes_data:
                stats = calculate_module_stats(notes_data)
                module_total = stats['total_notes']
                module_completed = stats['completed']
                module_in_progress = stats['in_progress']
                module_not_started = stats['not_started']
                module_status = stats['module_status']

        modules_data.append({
            'name': module_name,
            'display_name': get_display_name(module_name),
            'total_notes': module_total,
            'completed': module_completed,
            'in_progress': module_in_progress,
            'not_started': module_not_started,
            'status': module_status or '⬜',
            'camp': '🔴' if module_name.lower() in RED_TEAM_MODULES else '🟦' if module_name.lower() in BLUE_TEAM_MODULES else '⚪'
        })
        
        total_notes += module_total
        completed += module_completed
        in_progress += module_in_progress
        not_started += module_not_started
    
    # 章节副标题跟随实际模块，避免目录调整后描述与内容不一致
    description = " · ".join(m['display_name'] for m in modules_data)

    completion_rate = int(completed / total_notes * 100) if total_notes > 0 else 0
    progress = progress_bar(completion_rate)
    
    module_rows = []
    for m in modules_data:
        module_rows.append(f"| {m['camp']} | [{m['display_name']}]({m['name']}/) | {m['total_notes']} | {m['status']} |")
    
    update_time = get_current_time()
    
    content = CHAPTER_TEMPLATE.format(
        total_modules=len(modules),
        total_notes=total_notes,
        completed=completed,
        in_progress=in_progress,
        not_started=not_started,
        completion_rate=completion_rate,
        progress_bar=progress,
        description=description,
        module_rows="\n".join(module_rows),
        update_time=update_time,
        last_updated=update_time
    )
    
    output_path = os.path.join(CHAPTER_PATH, 'index.md')
    
    if safe_write(output_path, content, dry_run):
        logger.info(f"✅ 已生成: {output_path}")
        logger.info(f"   模块数: {len(modules)}")
        logger.info(f"   总笔记: {total_notes}, 已完成: {completed}, 完成率: {completion_rate}%")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    generate_redblue_chapter(dry_run)