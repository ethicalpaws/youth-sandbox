#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01-foundation 章节完整更新脚本
优化版：使用 common.py 公共模块
支持：
  1. bypass-waf：多笔记 + 关联 practice
  2. cryptography：多笔记（无关联）
  3. os：递归扫描所有子目录笔记
  4. programming：递归扫描所有子目录笔记
"""

import os
import sys
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
CHAPTER_PATH = os.path.join(KNOWLEDGE_PATH, "01-foundation")
PRACTICE_PATH = get_practice_path()

# 模块显示名称映射
MODULE_DISPLAY_NAMES = {
    'bypass-waf': 'WAF绕过',
    'cryptography': '密码学',
    'os': '操作系统',
    'programming': '编程基础'
}

def get_display_name(module_name: str) -> str:
    """获取模块的显示名称"""
    return MODULE_DISPLAY_NAMES.get(module_name, module_name.replace('-', ' ').title())

# bypass-waf 模板（关联 practice）
BYPASS_TEMPLATE = '''---
module_name: {module_name}
description: WAF绕过原理、技巧与实践
status: {module_status}
total_notes: {total_notes}
completed: {completed}
in_progress: {in_progress}
not_started: {not_started}
completion_rate: {completion_rate}
last_updated: {last_updated}
---

# 🛡️ 绕WAF技巧

> WAF绕过原理、技巧与实践

## 📝 技巧列表

| 技巧 | 说明 | 相关CTF |
|------|------|---------|
{notes_table}

## 📊 统计

| 指标 | 数值 |
|------|:----:|
| 技巧数 | {total_notes} |
| ✅ 已掌握 | {completed} |
| 🔄 学习中 | {in_progress} |
| ⬜ 未开始 | {not_started} |
| 完成率 | {progress_bar} |
| CTF关联 | {ctf_count} 道 |
| CVE关联 | {cve_count} 个 |
| Lab关联 | {lab_count} 个 |

## 🔗 关联实战

### CTF题目

{ctf_table}

### Lab靶场

{lab_table}

### CVE漏洞

{cve_table}

## 💡 常用绕过手法

- 🔄 **编码绕过**：URL编码、Unicode编码、HTML实体编码
- 📦 **协议绕过**：HTTP方法覆盖、分块传输、协议降级
- 🎯 **注入点绕过**：注释符、引号闭合、函数替换
- 🔧 **边界绕过**：换行绕过、注释嵌套、特殊字符

> 🎯 每一种WAF都有弱点，关键在于找到它的解析盲区

---
*自动更新：{update_time}
'''

# 通用模板（无关联）
GENERAL_TEMPLATE = '''---
module_name: {module_name}
description: {description}
status: {module_status}
total_notes: {total_notes}
completed: {completed}
in_progress: {in_progress}
not_started: {not_started}
completion_rate: {completion_rate}
last_updated: {last_updated}
---

# {module_name}

> {description}

## 📊 学习统计

| 指标 | 数值 |
|------|:----:|
| 总笔记数 | {total_notes} |
| ✅ 已完成 | {completed} |
| 🔄 进行中 | {in_progress} |
| ⬜ 未开始 | {not_started} |
| 完成率 | {progress_bar} |

## 📖 笔记列表

| 笔记 | 描述 | 状态 |
|------|------|:----:|
{notes_table}

---
*自动更新：{update_time}
'''

def collect_notes_recursive(module_dir: str) -> list:
    """递归收集模块目录下所有笔记的元数据"""
    notes_data = []
    
    for root, dirs, files in os.walk(module_dir):
        if root == module_dir:
            md_files = [f for f in files if f.endswith('.md') and f != 'index.md']
        else:
            md_files = [f for f in files if f.endswith('.md')]
        
        for note_file in md_files:
            note_path = os.path.join(root, note_file)
            metadata = read_metadata(note_path)
            
            title = metadata.get('title', note_file.replace('.md', ''))
            description = metadata.get('description', '')
            status_cn = metadata.get('status', '未开始')
            
            rel_path = os.path.relpath(note_path, module_dir)
            
            notes_data.append({
                'file': rel_path,
                'title': title,
                'description': description,
                'status_cn': status_cn
            })
    
    return notes_data

def update_bypass_module(module_dir: str, module_name: str, config: dict, dry_run: bool = False) -> dict:
    """更新 bypass-waf 模块"""
    logger.info(f"  处理模块: {module_name}")
    
    notes_data = collect_notes_recursive(module_dir)
    
    if not notes_data:
        logger.warning(f"    跳过：未找到笔记文件")
        return None
    
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
    
    # 生成笔记表格
    notes_table_lines = []
    for n in notes_data:
        status_emoji = get_status_emoji(n['status_cn'])
        desc_short = n['description'][:40] + "..." if len(n['description']) > 40 else n['description']
        notes_table_lines.append(f"| [{n['title']}]({n['file']}) | {desc_short} | {status_emoji} |")
    notes_table = "\n".join(notes_table_lines)
    
    # 关联 practice
    foundation_config = config.get('foundation_chapter', {})
    tag_mapping = foundation_config.get('module_tag_mapping', {})
    practice_items = scan_practice_related(PRACTICE_PATH, tag_mapping.get(module_name, []))
    
    ctf_table, ctf_count = generate_practice_table(practice_items['ctf'], 'ctf')
    lab_table, lab_count = generate_practice_table(practice_items['lab'], 'lab')
    cve_table, cve_count = generate_practice_table(practice_items['cve'], 'cve')
    
    logger.info(f"      关联 CTF: {ctf_count}, Lab: {lab_count}, CVE: {cve_count}")
    
    update_time = get_current_time()
    
    content = BYPASS_TEMPLATE.format(
        module_name=get_display_name(module_name),
        module_status=module_status,
        total_notes=total,
        completed=completed,
        in_progress=in_progress,
        not_started=not_started,
        completion_rate=completion_rate,
        progress_bar=progress,
        notes_table=notes_table,
        ctf_count=ctf_count,
        cve_count=cve_count,
        lab_count=lab_count,
        ctf_table=ctf_table,
        lab_table=lab_table,
        cve_table=cve_table,
        update_time=update_time,
        last_updated=update_time
    )
    
    index_path = os.path.join(module_dir, 'index.md')
    
    if safe_write(index_path, content, dry_run):
        logger.info(f"    ✅ 已生成模块 index.md (总笔记: {total}, 完成: {completed}, 完成率: {completion_rate}%)")
    
    return {
        'name': module_name,
        'display_name': get_display_name(module_name),
        'title': module_name,
        'status': module_status,
        'total_notes': total,
        'completed': completed,
        'in_progress': in_progress,
        'not_started': not_started,
        'completion_rate': completion_rate
    }

def update_general_module(module_dir: str, module_name: str, config: dict, dry_run: bool = False) -> dict:
    """更新通用模块"""
    logger.info(f"  处理模块: {module_name}")
    
    notes_data = collect_notes_recursive(module_dir)
    
    if not notes_data:
        logger.warning(f"    跳过：未找到笔记文件")
        return None
    
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
    
    # 生成笔记表格
    notes_table_lines = []
    for n in notes_data:
        status_emoji = get_status_emoji(n['status_cn'])
        desc_short = n['description'][:40] + "..." if len(n['description']) > 40 else n['description']
        notes_table_lines.append(f"| [{n['title']}]({n['file']}) | {desc_short} | {status_emoji} |")
    notes_table = "\n".join(notes_table_lines)
    
    update_time = get_current_time()
    
    content = GENERAL_TEMPLATE.format(
        module_name=get_display_name(module_name),
        description=f"{get_display_name(module_name)} 学习笔记",
        module_status=module_status,
        total_notes=total,
        completed=completed,
        in_progress=in_progress,
        not_started=not_started,
        completion_rate=completion_rate,
        progress_bar=progress,
        notes_table=notes_table,
        update_time=update_time,
        last_updated=update_time
    )
    
    index_path = os.path.join(module_dir, 'index.md')
    
    if safe_write(index_path, content, dry_run):
        logger.info(f"    ✅ 已生成模块 index.md (总笔记: {total}, 完成: {completed}, 完成率: {completion_rate}%)")
    
    return {
        'name': module_name,
        'display_name': get_display_name(module_name),
        'title': module_name,
        'status': module_status,
        'total_notes': total,
        'completed': completed,
        'in_progress': in_progress,
        'not_started': not_started,
        'completion_rate': completion_rate
    }

def update_chapter_index(modules_data: list, config: dict, dry_run: bool = False) -> None:
    """更新章节级 index.md"""
    total_modules = len(modules_data)
    total_notes = sum(m['total_notes'] for m in modules_data)
    completed_notes = sum(m['completed'] for m in modules_data)
    
    if all(m['status'] == '♻️' for m in modules_data):
        chapter_status = "♻️ 持续更新中"
    elif any(m['status'] == '🔄' for m in modules_data) or any(m['completed'] > 0 for m in modules_data):
        chapter_status = "🔄 进行中"
    else:
        chapter_status = "⬜ 未开始"
    
    completion_rate = int(completed_notes / total_notes * 100) if total_notes > 0 else 0
    progress = progress_bar(completion_rate)
    
    # 生成模块表格行（模块名称添加链接）
    module_rows = []
    for m in modules_data:
        module_link = f"[{m['display_name']}]({m['name']}/)"
        module_rows.append(f"| {module_link} | {m['total_notes']} | {m['completed']} | {m['completion_rate']}% | {m['status']} |")
    
    foundation_config = config.get('foundation_chapter', {})
    learning_route = foundation_config.get('learning_route', [
        "**编程基础**：Python、JavaScript、Java",
        "**操作系统**：Linux、Windows基础",
        "**WAF绕过**：基础绕过技巧"
    ])
    
    route_lines = "\n".join([f"{i+1}. {route}" for i, route in enumerate(learning_route)])
    
    update_time = get_current_time()
    
    # 构建内容（不使用三引号嵌套，改用字符串拼接）
    front_matter_lines = [
        "---",
        f"total_modules: {total_modules}",
        f"total_notes: {total_notes}",
        f"completed: {completed_notes}",
        f"in_progress: {sum(m['in_progress'] for m in modules_data)}",
        f"not_started: {sum(m['not_started'] for m in modules_data)}",
        f"completion_rate: {completion_rate}",
        f"last_updated: {update_time}",
        "---",
        ""
    ]
    front_matter = "\n".join(front_matter_lines)
    
    content_body_lines = [
        "# 🔰 基础知识",
        "",
        "> 编程语言、操作系统、密码学、WAF绕过等基础",
        "",
        f"## 章节状态：{chapter_status}",
        "",
        "## 📚 模块列表",
        "",
        "| 模块 | 笔记数 | 已完成 | 完成率 | 状态 |",
        "|------|:------:|:------:|:------:|:----:|",
    ]
    content_body_lines.extend(module_rows)
    content_body_lines.extend([
        "",
        "## 📊 学习进度",
        "",
        "| 指标 | 数值 |",
        "|------|:----:|",
        f"| 总模块数 | {total_modules} |",
        f"| 总笔记数 | {total_notes} |",
        f"| ✅ 已完成笔记 | {completed_notes} |",
        f"| 整体完成率 | {progress} |",
        "",
        "## 🎯 学习路线（建议顺序）",
        "",
        route_lines,
        "",
        "## 💡 学习建议",
        "",
        "📖 打好基础，循序渐进",
        "💻 多写代码，动手实践",
        "🔍 理解原理，举一反三",
        "",
        "---",
        f"*最后更新：{update_time} | 状态自动同步*",
        ""
    ])
    
    content = front_matter + "\n".join(content_body_lines)
    
    chapter_index_path = os.path.join(CHAPTER_PATH, 'index.md')
    
    if safe_write(chapter_index_path, content, dry_run):
        logger.info(f"\n✅ 已生成章节 index.md")
        logger.info(f"   章节状态: {chapter_status}")
        logger.info(f"   总模块: {total_modules}, 总笔记: {total_notes}, 已完成: {completed_notes}")
        logger.info(f"   完成率: {completion_rate}%")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    
    logger.info("=" * 60)
    logger.info("01-foundation 章节完整更新脚本")
    logger.info("=" * 60)
    logger.info(f"目标章节: {CHAPTER_PATH}")
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")
    
    if not os.path.exists(CHAPTER_PATH):
        logger.error(f"路径不存在: {CHAPTER_PATH}")
        return
    
    config = load_config()
    
    # 定义模块及其处理类型
    modules = {
        'bypass-waf': 'bypass',
        'cryptography': 'general',
        'os': 'general',
        'programming': 'general'
    }
    
    logger.info(f"\n发现模块: {list(modules.keys())}")
    logger.info("\n开始更新模块...")
    
    modules_data = []
    for module_name, module_type in modules.items():
        module_dir = os.path.join(CHAPTER_PATH, module_name)
        if not os.path.exists(module_dir):
            logger.warning(f"  ⚠️ 模块不存在: {module_name}")
            continue
        
        if module_type == 'bypass':
            data = update_bypass_module(module_dir, module_name, config, dry_run)
        else:
            data = update_general_module(module_dir, module_name, config, dry_run)
        
        if data:
            modules_data.append(data)
    
    logger.info("\n开始更新章节...")
    update_chapter_index(modules_data, config, dry_run)
    
    logger.info("\n" + "=" * 60)
    logger.info("完成！")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()