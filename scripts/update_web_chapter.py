#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web 章节通用更新脚本
支持 03-web-basics 和 04-web-advanced
优化版：使用 common.py 公共模块
"""

import os
import sys
import re
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, load_config, parse_front_matter, read_metadata,
    get_status_emoji, get_current_time, safe_write, need_update,
    get_knowledge_path, get_practice_path, progress_bar,
    scan_practice_related, generate_practice_table
)

# ==================== 配置 ====================
KNOWLEDGE_PATH = get_knowledge_path()
PRACTICE_PATH = get_practice_path()

# 模块级模板
MODULE_TEMPLATE = '''---
module_name: {module_name}
description: {description}
status: {module_status}
finish_date: {finish_date}
note_path: {note_path}
tags: {tags}
last_updated: {last_updated}
---

# {module_name} - 笔记概述

> {description}

## 📊 统计

- **完成情况**：{module_status}
- **完成日期**：{finish_date}

## 📖 笔记目录

{toc}

## 🔗 关联实战

### CTF题目

{ctf_table}

### Lab靶场

{lab_table}

### CVE漏洞

{cve_table}

---
*自动更新：{update_time}
'''

def extract_headers(content: str) -> list:
    """提取 Markdown 中的二级标题"""
    pattern = r'^##\s+(.+)$'
    return re.findall(pattern, content, re.MULTILINE)

def generate_toc(headers: list, note_path: str) -> str:
    """生成目录"""
    if not headers:
        return "暂无目录"
    lines = []
    for i, header in enumerate(headers, 1):
        anchor = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', header)
        anchor = anchor.strip().replace(' ', '-').lower()
        lines.append(f"{i}. [{header}]({note_path}#{anchor})")
    return "\n".join(lines)

def update_module_index(module_dir: str, module_name: str, tag_mapping: dict, dry_run: bool = False) -> dict:
    """更新单个模块的 index.md"""
    logger.info(f"  处理模块: {module_name}")
    
    md_files = [f for f in os.listdir(module_dir) if f.endswith('.md') and f != 'index.md']
    if not md_files:
        logger.warning(f"    跳过：未找到笔记文件")
        return None
    
    note_file = md_files[0]
    note_path = os.path.join(module_dir, note_file)
    
    with open(note_path, 'r', encoding='utf-8') as f:
        note_content = f.read()
    
    metadata, rest_content = parse_front_matter(note_content)
    
    title = metadata.get('title', module_name)
    description = metadata.get('description', '')
    finish_date = metadata.get('finish-date', '')
    tags = metadata.get('tags', [])
    status_cn = metadata.get('status', '未开始')
    
    module_status = get_status_emoji(status_cn)
    
    headers = extract_headers(rest_content)
    toc = generate_toc(headers, note_file)
    
    practice_items = scan_practice_related(PRACTICE_PATH, tag_mapping.get(module_name, []))
    
    ctf_table, ctf_count = generate_practice_table(practice_items['ctf'], 'ctf')
    lab_table, lab_count = generate_practice_table(practice_items['lab'], 'lab')
    cve_table, cve_count = generate_practice_table(practice_items['cve'], 'cve')
    
    logger.info(f"      关联 CTF: {ctf_count}, Lab: {lab_count}, CVE: {cve_count}")
    
    update_time = get_current_time()
    
    content = MODULE_TEMPLATE.format(
        module_name=title,
        description=description,
        module_status=module_status,
        finish_date=finish_date,
        note_path=note_file,
        tags=str(tags),
        last_updated=update_time,
        toc=toc,
        ctf_table=ctf_table,
        lab_table=lab_table,
        cve_table=cve_table,
        update_time=update_time
    )
    
    index_path = os.path.join(module_dir, 'index.md')
    
    if safe_write(index_path, content, dry_run):
        logger.info(f"    ✅ 已生成模块 index.md (状态: {module_status})")
    
    return {
        'name': module_name,
        'title': title,
        'description': description,
        'status': module_status,
        'finish_date': finish_date
    }

def update_chapter_index(chapter_path: str, modules_data: list, chapter_config: dict, dry_run: bool = False) -> None:
    """更新章节级 index.md"""
    total = len(modules_data)
    total_notes = len(modules_data)
    
    title = chapter_config.get('title', 'Web漏洞')
    description = chapter_config.get('description', '')
    learning_route = chapter_config.get('learning_route', [])
    resources = chapter_config.get('resources', [])
    milestones = chapter_config.get('milestones', [])
    
    completed_count = 0
    in_progress_count = 0
    not_started_count = 0
    
    modules_table_lines = []
    for module in modules_data:
        raw_status = module['status']
        
        if raw_status == '✅':
            completed_count += 1
        elif raw_status == '🔄':
            in_progress_count += 1
        else:
            not_started_count += 1
        
        description_text = module['description'] if module['description'] else '待补充'
        modules_table_lines.append(f"| [{module['title']}]({module['name']}/) | {description_text} | {raw_status} |")
    
    modules_table = "\n".join(modules_table_lines)
    
    # 章节状态判断
    if completed_count == total:
        chapter_status_symbol = "♻️"
        chapter_status_text = "持续更新中"
    elif not_started_count == total:
        chapter_status_symbol = "⬜"
        chapter_status_text = "未开始"
    else:
        chapter_status_symbol = "🔄"
        chapter_status_text = "进行中"
    
    chapter_status = f"{chapter_status_symbol} {chapter_status_text}"
    
    completion_rate = int(completed_count / total * 100) if total > 0 else 0
    filled = int(completion_rate / 10)
    progress_bar_str = f"{'█' * filled}{'░' * (10 - filled)} {completion_rate}%"
    
    route_lines = "\n".join([f"{i+1}. {route}" for i, route in enumerate(learning_route)]) if learning_route else "待补充"
    
    resource_lines = ["| 资源 | 链接 | 用途 |", "|------|------|------|"]
    for r in resources:
        resource_lines.append(f"| {r.get('name', '')} | [官网]({r.get('url', '#')}) | {r.get('purpose', '')} |")
    resources_table = "\n".join(resource_lines) if len(resources) > 0 else "| - | - | - |"
    
    milestone_lines = []
    for m in milestones:
        milestone_lines.append(f"- [ ] 完成 {m.get('count', 0)} 个模块 → {m.get('icon', '')} {m.get('title', '')}")
    milestones_list = "\n".join(milestone_lines) if milestones else "待补充"
    
    update_time = get_current_time()
    
    front_matter = f'''---
total_modules: {total}
total_notes: {total_notes}
completed: {completed_count}
status: {chapter_status_symbol}
last_updated: {update_time}
---

'''
    
    content = front_matter + f"""# {title}

> {description}

## 章节状态：{chapter_status}

## 📖 漏洞模块

| 模块 | 说明 | 状态 |
|------|------|:----:|
{modules_table}

## 📊 学习进度

| 指标 | 数值 |
|------|:----:|
| 总模块数 | {total} |
| ✅ 已完成 | {completed_count} |
| 🔄 进行中 | {in_progress_count} |
| ⬜ 未开始 | {not_started_count} |
| 整体完成率 | {progress_bar_str} |

## 🎯 学习路线（建议顺序）

{route_lines}

## 🔗 常用资源

{resources_table}

## 💡 学习建议

🔍 每个漏洞先理解**原理**，再动手**实践**
📝 完成模块后，在 `practice/` 中记录**WriteUp**
🔄 定期**复盘**，总结绕过技巧和防御方案
🏆 目标：完成所有模块 + 关联CTF题目

## 🚀 进度里程碑

{milestones_list}

---
*最后更新：{update_time} | 状态自动同步*
"""
    
    chapter_index_path = os.path.join(chapter_path, 'index.md')
    
    if safe_write(chapter_index_path, content, dry_run):
        logger.info(f"\n✅ 已生成章节 index.md")
        logger.info(f"   章节状态: {chapter_status}")
        logger.info(f"   总模块: {total}, 已完成: {completed_count}, 进行中: {in_progress_count}, 未开始: {not_started_count}")
        logger.info(f"   完成率: {completion_rate}% {progress_bar_str}")

def process_chapter(chapter_path: str, chapter_key: str, dry_run: bool = False) -> None:
    """处理单个章节"""
    config = load_config()
    chapter_config = config.get(chapter_key, {})
    tag_mapping = chapter_config.get('module_tag_mapping', {})
    
    if not os.path.exists(chapter_path):
        logger.error(f"\n路径不存在: {chapter_path}")
        return
    
    modules = [d for d in os.listdir(chapter_path)
               if os.path.isdir(os.path.join(chapter_path, d))
               and not d.startswith('.')]
    
    logger.info(f"\n发现 {len(modules)} 个模块: {modules}")
    logger.info("\n开始更新模块...")
    
    modules_data = []
    for module in modules:
        module_dir = os.path.join(chapter_path, module)
        data = update_module_index(module_dir, module, tag_mapping, dry_run)
        if data:
            modules_data.append(data)
    
    logger.info("\n开始更新章节...")
    update_chapter_index(chapter_path, modules_data, chapter_config, dry_run)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    
    logger.info("=" * 60)
    logger.info("Web 章节通用更新脚本")
    logger.info("=" * 60)
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")
    
    # 处理 03-web-basics
    logger.info("\n" + "=" * 60)
    logger.info("处理 03-web-basics")
    logger.info("=" * 60)
    chapter_03_path = os.path.join(KNOWLEDGE_PATH, "03-web-basics")
    process_chapter(chapter_03_path, "web_basics", dry_run)
    
    # 处理 04-web-advanced
    logger.info("\n" + "=" * 60)
    logger.info("处理 04-web-advanced")
    logger.info("=" * 60)
    chapter_04_path = os.path.join(KNOWLEDGE_PATH, "04-web-advanced")
    process_chapter(chapter_04_path, "web_advanced", dry_run)
    
    logger.info("\n" + "=" * 60)
    logger.info("完成！")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()