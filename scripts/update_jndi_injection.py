#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jndi-injection 模块 index.md 自动生成脚本
优化版：使用 common.py 公共模块
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, load_config, read_metadata,
    get_status_emoji, get_current_time, safe_write,
    get_knowledge_path, get_practice_path, progress_bar,
    scan_practice_related, generate_practice_table
)

# ==================== 配置 ====================
KNOWLEDGE_PATH = get_knowledge_path()
MODULE_PATH = os.path.join(KNOWLEDGE_PATH, "05-java-security", "jndi-injection")
PRACTICE_PATH = get_practice_path()

# 模板
MODULE_TEMPLATE = '''---
module_name: jndi-injection
description: JNDI注入漏洞学习笔记
status: {module_status}
total_notes: {total_notes}
completed: {completed}
in_progress: {in_progress}
not_started: {not_started}
completion_rate: {completion_rate}
last_updated: {last_updated}
---

# 🌐 jndi-injection

> JNDI注入漏洞学习笔记

## 模块状态：{module_status}

## 📊 学习统计

| 指标 | 数值 |
|------|:----:|
| 总笔记数 | {total_notes} |
| ✅ 已完成 | {completed} |
| 🔄 进行中 | {in_progress} |
| ⬜ 未开始 | {not_started} |
| 完成率 | {progress_bar} |

## 📖 学习内容

| 笔记 | 描述 | 状态 |
|------|------|:----:|
{notes_table}

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

def collect_notes() -> list:
    """收集模块目录下所有笔记的元数据"""
    notes_data = []
    
    if not os.path.exists(MODULE_PATH):
        return notes_data
    
    for f in os.listdir(MODULE_PATH):
        if not f.endswith('.md') or f == 'index.md':
            continue
        
        file_path = os.path.join(MODULE_PATH, f)
        metadata = read_metadata(file_path)
        
        title = metadata.get('title', f.replace('.md', ''))
        description = metadata.get('description', '')
        status_cn = metadata.get('status', '未开始')
        finish_date = metadata.get('finish-date', '')
        
        notes_data.append({
            'file': f,
            'title': title,
            'description': description,
            'status_cn': status_cn,
            'finish_date': finish_date
        })
    
    return notes_data

def update_module_index(dry_run: bool = False) -> bool:
    """更新模块级 index.md"""
    logger.info(f"\n处理模块: jndi-injection")
    
    notes_data = collect_notes()
    
    if not notes_data:
        logger.warning(f"    跳过：未找到笔记文件")
        return False
    
    total = len(notes_data)
    completed = sum(1 for n in notes_data if n['status_cn'] == '已完成')
    in_progress = sum(1 for n in notes_data if n['status_cn'] == '进行中')
    not_started = sum(1 for n in notes_data if n['status_cn'] == '未开始')
    completion_rate = int(completed / total * 100) if total > 0 else 0
    progress = progress_bar(completion_rate)
    
    if completed == total:
        module_status = "♻️"
    elif completed > 0 or in_progress > 0:
        module_status = "🔄"
    else:
        module_status = "⬜"
    
    # 生成笔记表格（按完成日期倒序）
    notes_data.sort(key=lambda x: x.get('finish_date', ''), reverse=True)
    
    notes_table_lines = []
    for n in notes_data:
        status_emoji = get_status_emoji(n['status_cn'])
        desc_short = n['description'][:50] + "..." if len(n['description']) > 50 else n['description']
        notes_table_lines.append(f"| [{n['title']}]({n['file']}) | {desc_short} | {status_emoji} |")
    notes_table = "\n".join(notes_table_lines)
    
    # 关联 practice
    config = load_config()
    java_config = config.get('java_security', {})
    tag_mapping = java_config.get('module_tag_mapping', {})
    practice_items = scan_practice_related(PRACTICE_PATH, tag_mapping.get('jndi-injection', []))
    
    ctf_table, ctf_count = generate_practice_table(practice_items['ctf'], 'ctf')
    lab_table, lab_count = generate_practice_table(practice_items['lab'], 'lab')
    cve_table, cve_count = generate_practice_table(practice_items['cve'], 'cve')
    
    logger.info(f"      关联 CTF: {ctf_count}, Lab: {lab_count}, CVE: {cve_count}")
    
    update_time = get_current_time()
    
    content = MODULE_TEMPLATE.format(
        module_status=module_status,
        total_notes=total,
        completed=completed,
        in_progress=in_progress,
        not_started=not_started,
        completion_rate=completion_rate,
        progress_bar=progress,
        notes_table=notes_table,
        ctf_table=ctf_table,
        lab_table=lab_table,
        cve_table=cve_table,
        update_time=update_time,
        last_updated=update_time
    )
    
    index_path = os.path.join(MODULE_PATH, 'index.md')
    
    if safe_write(index_path, content, dry_run):
        logger.info(f"    ✅ 已生成模块 index.md (总笔记: {total}, 完成: {completed}, 完成率: {completion_rate}%)")
        return True
    
    return False

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    
    logger.info("=" * 60)
    logger.info("jndi-injection 模块 index.md 自动生成脚本")
    logger.info("=" * 60)
    logger.info(f"目标模块: {MODULE_PATH}")
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")
    
    if not os.path.exists(MODULE_PATH):
        logger.error(f"路径不存在: {MODULE_PATH}")
        return
    
    update_module_index(dry_run)
    
    logger.info("\n" + "=" * 60)
    logger.info("完成！")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()