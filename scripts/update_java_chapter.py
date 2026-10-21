#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
05-java-security 章节级 index.md 自动生成脚本
优化版：使用 common.py 公共模块，模块名称添加链接
"""

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, load_config, read_index_metadata, read_metadata,
    extract_heading, get_current_time, safe_write, progress_bar,
    get_knowledge_path, get_meta, get_status_emoji,
    collect_notes_recursive, calculate_module_stats, is_real_dir
)

# ==================== 配置 ====================
KNOWLEDGE_PATH = get_knowledge_path()
CHAPTER_PATH = os.path.join(KNOWLEDGE_PATH, "05-java-security")

# 模块显示名称兜底映射（当模块 index.md 缺失或标题仍是目录名时使用）
MODULE_DISPLAY_NAMES = {
    'EL-injection': 'EL 表达式注入',
    'Java-Web': 'Java Web',
    'framework-vulns': '框架漏洞',
    'java-deserialization': 'Java 反序列化',
    'jndi-injection': 'JNDI 注入',
    'memory-shell': '内存马'
}

# 缺少模块 index.md 时使用的兜底模板
MODULE_FALLBACK_TEMPLATE = '''---
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

# {display_name}

> {description}

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

---
*自动更新：{update_time}
'''

# 模板（模块名称添加链接）
CHAPTER_TEMPLATE = '''---
total_modules: {total_modules}
total_notes: {total_notes}
completed: {completed}
in_progress: {in_progress}
not_started: {not_started}
completion_rate: {completion_rate}
last_updated: {last_updated}
---

# ☕ Java安全

> Java反序列化、内存马、JNDI注入、框架漏洞等

## 章节状态：{chapter_status}

## 📚 模块列表

| 模块 | 笔记数 | 已完成 | 完成率 | 状态 |
|------|:------:|:------:|:------:|:----:|
{module_rows}

## 📊 学习进度

| 指标 | 数值 |
|------|:----:|
| 总模块数 | {total_modules} |
| 总笔记数 | {total_notes} |
| ✅ 已完成笔记 | {completed} |
| 🔄 进行中 | {in_progress} |
| ⬜ 未开始 | {not_started} |
| 整体完成率 | {progress_bar} |

## 🎯 学习路线（建议顺序）

1. **反序列化**：CC链 → CB链 → Fastjson
2. **JNDI注入**：Log4j → RMI → LDAP
3. **内存马**：Filter → Servlet → Agent
4. **框架漏洞**：Fastjson → Shiro → Spring → Tomcat

## 🔗 常用资源

| 资源 | 链接 | 用途 |
|------|------|------|
| ysoserial | [GitHub](https://github.com/frohoff/ysoserial) | 反序列化工具 |
| Java安全漫谈 | [Seebug](https://paper.seebug.org/category/java/) | 学习文章 |

## 💡 学习建议

🔍 理解原理，动手调试
📝 总结 Gadget 链，形成知识库
🔄 定期复盘，对比不同链的差异

## 🏆 进度里程碑

- [ ] 完成 3 个模块 → 🎖️ Java安全入门
- [ ] 完成 6 个模块 → 🏅 Java安全进阶
- [ ] 完成 10 个模块 → 🏆 Java安全精通

---
*最后更新：{update_time} | 状态自动同步*
'''

def get_display_name(module_path: str, module_name: str) -> str:
    """
    获取模块显示名称，优先使用模块 index.md 的标题。

    读取顺序：Front Matter title -> module_name -> 一级标题。
    若标题只是英文目录名（或包含目录名），说明尚未本地化，
    则回退到 MODULE_DISPLAY_NAMES 中的中文名称。
    """
    index_path = os.path.join(module_path, 'index.md')
    metadata = read_metadata(index_path)

    content = ''
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError:
        pass

    candidates = [
        get_meta(metadata, 'title', ''),
        get_meta(metadata, 'module_name', ''),
        extract_heading(content, 1),
    ]
    for candidate in candidates:
        title = str(candidate).strip() if candidate else ''
        # 去掉标题前的装饰性 emoji/符号，避免表格中名称风格不一致
        title = re.sub(r'^[^\w]+', '', title).strip()
        if not title:
            continue
        # 标题仍是目录名（或把目录名嵌在标题里）时，不算有效展示名
        if module_name.lower() in title.lower():
            continue
        return title

    return MODULE_DISPLAY_NAMES.get(
        module_name, module_name.replace('-', ' ').title()
    )

def ensure_module_index(module_path: str, module_name: str, notes_data: list,
                        stats: dict, dry_run: bool = False) -> None:
    """模块缺少 index.md 时生成兜底索引（不覆盖已有手工/专用索引）"""
    index_path = os.path.join(module_path, 'index.md')
    if os.path.exists(index_path) or not notes_data:
        return

    display_name = get_display_name(module_path, module_name)
    rows = []
    for note in notes_data:
        status_emoji = get_status_emoji(note['status_cn'])
        desc = note.get('description', '') or ''
        desc_short = desc[:50] + "..." if len(desc) > 50 else desc
        rows.append(f"| [{note['title']}]({note['file']}) | {desc_short} | {status_emoji} |")

    update_time = get_current_time()
    content = MODULE_FALLBACK_TEMPLATE.format(
        module_name=display_name,
        display_name=display_name,
        description=f"{display_name} 学习笔记",
        module_status=stats['module_status'],
        total_notes=stats['total_notes'],
        completed=stats['completed'],
        in_progress=stats['in_progress'],
        not_started=stats['not_started'],
        completion_rate=stats['completion_rate'],
        progress_bar=progress_bar(stats['completion_rate']),
        notes_table="\n".join(rows),
        last_updated=update_time,
        update_time=update_time
    )
    if safe_write(index_path, content, dry_run):
        logger.info(f"    ✅ 已补生成模块索引: {module_name}/index.md")

def get_chapter_status(modules_data: list) -> str:
    """根据模块状态判断章节整体状态"""
    if not modules_data:
        return "⬜ 未开始"
    
    completed_modules = sum(1 for m in modules_data if m.get('module_status') == '♻️')
    in_progress_modules = sum(1 for m in modules_data if m.get('module_status') == '🔄')
    
    if completed_modules == len(modules_data):
        return "♻️ 持续更新中"
    elif in_progress_modules > 0 or completed_modules > 0:
        return "🔄 进行中"
    else:
        return "⬜ 未开始"

def generate_java_chapter(dry_run: bool = False) -> None:
    """生成 Java 安全章节 index.md"""
    logger.info("=" * 60)
    logger.info("05-java-security 章节级 index.md 生成")
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

        # 以实际笔记为准统计，避免模块索引缺失或状态为 null 时少算
        notes_data = collect_notes_recursive(module_path)
        if notes_data:
            stats = calculate_module_stats(notes_data)
            module_total = stats['total_notes']
            module_completed = stats['completed']
            module_in_progress = stats['in_progress']
            module_not_started = stats['not_started']
            module_rate = stats['completion_rate']
            module_status = stats['module_status']
            ensure_module_index(module_path, module_name, notes_data, stats, dry_run)
        else:
            metadata = read_index_metadata(module_path)
            module_total = get_meta(metadata, 'total_notes', 0)
            module_completed = get_meta(metadata, 'completed', 0)
            module_in_progress = get_meta(metadata, 'in_progress', 0)
            module_not_started = get_meta(metadata, 'not_started', 0)
            module_rate = get_meta(metadata, 'completion_rate', 0)
            module_status = get_meta(metadata, 'status', '⬜')

        modules_data.append({
            'name': module_name,
            'display_name': get_display_name(module_path, module_name),
            'total_notes': module_total,
            'completed': module_completed,
            'in_progress': module_in_progress,
            'not_started': module_not_started,
            'completion_rate': module_rate,
            'module_status': module_status
        })
        
        total_notes += module_total
        completed += module_completed
        in_progress += module_in_progress
        not_started += module_not_started
    
    completion_rate = int(completed / total_notes * 100) if total_notes > 0 else 0
    progress = progress_bar(completion_rate)
    chapter_status = get_chapter_status(modules_data)
    
    # 生成模块表格行（模块名称添加链接）
    module_rows = []
    for m in modules_data:
        # 模块名称带链接
        module_link = f"[{m['display_name']}]({m['name']}/)"
        module_rows.append(
            f"| {module_link} | {m['total_notes']} | {m['completed']} | {m['completion_rate']}% | {m['module_status']} |"
        )
    
    update_time = get_current_time()
    
    content = CHAPTER_TEMPLATE.format(
        total_modules=len(modules),
        total_notes=total_notes,
        completed=completed,
        in_progress=in_progress,
        not_started=not_started,
        completion_rate=completion_rate,
        progress_bar=progress,
        chapter_status=chapter_status,
        module_rows="\n".join(module_rows),
        update_time=update_time,
        last_updated=update_time
    )
    
    output_path = os.path.join(CHAPTER_PATH, 'index.md')
    
    if safe_write(output_path, content, dry_run):
        logger.info(f"✅ 已生成: {output_path}")
        logger.info(f"   模块数: {len(modules)}")
        logger.info(f"   总笔记: {total_notes}, 已完成: {completed}, 完成率: {completion_rate}%")
        logger.info(f"   章节状态: {chapter_status}")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    generate_java_chapter(dry_run)