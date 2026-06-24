#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
02-network-protocol-security 章节完整更新脚本
优化版：使用 common.py 公共模块
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, load_config, parse_front_matter, read_metadata,
    get_status_emoji, get_current_time, safe_write, need_update,
    get_knowledge_path, progress_bar
)

# ==================== 配置 ====================
KNOWLEDGE_PATH = get_knowledge_path()
CHAPTER_PATH = os.path.join(KNOWLEDGE_PATH, "02-network-protocol-security")

# 模块显示名称映射
MODULE_DISPLAY_NAMES = {
    'network-basics': '网络基础',
    'network-attack': '网络攻击',
    'defense-tech': '防御技术',
    'firewall': '防火墙',
    'vpn': 'VPN隧道'
}

def get_display_name(module_name: str) -> str:
    """获取模块的显示名称"""
    return MODULE_DISPLAY_NAMES.get(module_name, module_name.replace('-', ' ').title())

# 模块级模板
MODULE_TEMPLATE = '''---
module_name: {module_name}
description: {description}
status: {module_status}
total_notes: {total_notes}
completed: {completed}
in_progress: {in_progress}
not_started: {not_started}
completion_rate: {completion_rate}
last_updated: {update_time}
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

def collect_notes_in_module(module_dir: str) -> list:
    """收集模块目录下所有笔记的元数据（非递归，只收集本级）"""
    notes_data = []
    
    md_files = [f for f in os.listdir(module_dir) 
                if f.endswith('.md') and f != 'index.md']
    
    for note_file in md_files:
        note_path = os.path.join(module_dir, note_file)
        metadata = read_metadata(note_path)
        
        title = metadata.get('title', note_file.replace('.md', ''))
        description = metadata.get('description', '')
        status_cn = metadata.get('status', '未开始')
        
        notes_data.append({
            'file': note_file,
            'title': title,
            'description': description,
            'status_cn': status_cn
        })
    
    return notes_data

def update_module_index(module_dir: str, module_name: str, config: dict, dry_run: bool = False) -> dict:
    """更新模块级 index.md"""
    logger.info(f"  处理模块: {module_name}")
    
    notes_data = collect_notes_in_module(module_dir)
    
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
        desc_short = n['description'][:50] + "..." if len(n['description']) > 50 else n['description']
        notes_table_lines.append(f"| [{n['title']}]({n['file']}) | {desc_short} | {status_emoji} |")
    
    notes_table = "\n".join(notes_table_lines)
    module_description = f"{get_display_name(module_name)} 学习笔记"
    update_time = get_current_time()
    
    content = MODULE_TEMPLATE.format(
        module_name=get_display_name(module_name),
        description=module_description,
        module_status=module_status,
        total_notes=total,
        completed=completed,
        in_progress=in_progress,
        not_started=not_started,
        completion_rate=completion_rate,
        progress_bar=progress,
        notes_table=notes_table,
        update_time=update_time
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
    total = len(modules_data)
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
    
    chapter_config = config.get('network_chapter', {})
    title = chapter_config.get('title', '🌐 网络协议安全')
    description = chapter_config.get('description', '网络基础、攻击技术与防御措施')
    learning_route = chapter_config.get('learning_route', [
        "**网络基础**：OSI模型、TCP/IP协议族",
        "**网络攻击**：ARP欺骗、ICMP攻击、TCP攻击",
        "**防御技术**：防火墙、VPN隧道"
    ])
    resources = chapter_config.get('resources', [
        {"name": "TCP/IP详解", "url": "https://book.douban.com/subject/1088054/", "purpose": "经典书籍"},
        {"name": "Wireshark", "url": "https://www.wireshark.org/", "purpose": "抓包分析工具"}
    ])
    milestones = chapter_config.get('milestones', [
        {"count": 2, "icon": "🎖️", "title": "网络基础入门"},
        {"count": 4, "icon": "🏅", "title": "网络基础进阶"},
        {"count": 6, "icon": "🏆", "title": "网络基础精通"}
    ])
    
    route_lines = "\n".join([f"{i+1}. {route}" for i, route in enumerate(learning_route)])
    
    resource_lines = ["| 资源 | 链接 | 用途 |", "|------|------|------|"]
    for r in resources:
        resource_lines.append(f"| {r['name']} | [链接]({r['url']}) | {r['purpose']} |")
    
    milestone_lines = [f"- [ ] 完成 {m['count']} 个模块 → {m['icon']} {m['title']}" for m in milestones]
    
    update_time = get_current_time()
    
    # 构建 Front Matter（不使用三引号嵌套）
    front_matter_lines = [
        "---",
        f"total_modules: {total}",
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
    
    # 构建正文
    content_body_lines = [
        f"# {title}",
        "",
        f"> {description}",
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
        f"| 总模块数 | {total} |",
        f"| 总笔记数 | {total_notes} |",
        f"| ✅ 已完成笔记 | {completed_notes} |",
        f"| 整体完成率 | {progress} |",
        "",
        "## 🎯 学习路线（建议顺序）",
        "",
        route_lines,
        "",
        "## 🔗 常用资源",
        "",
    ])
    content_body_lines.extend(resource_lines)
    content_body_lines.extend([
        "",
        "## 💡 学习建议",
        "",
        "🔍 理解协议原理，配合抓包分析",
        "📝 动手实践网络攻击实验",
        "🔄 定期复盘，总结攻击手法",
        "",
        "## 🚀 进度里程碑",
        "",
    ])
    content_body_lines.extend(milestone_lines)
    content_body_lines.extend([
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
        logger.info(f"   总模块: {total}, 总笔记: {total_notes}, 已完成: {completed_notes}")
        logger.info(f"   完成率: {completion_rate}%")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    
    logger.info("=" * 60)
    logger.info("02-network-protocol-security 章节完整更新脚本")
    logger.info("=" * 60)
    logger.info(f"目标章节: {CHAPTER_PATH}")
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")
    
    if not os.path.exists(CHAPTER_PATH):
        logger.error(f"路径不存在: {CHAPTER_PATH}")
        return
    
    config = load_config()
    
    modules = [d for d in os.listdir(CHAPTER_PATH)
               if os.path.isdir(os.path.join(CHAPTER_PATH, d))
               and not d.startswith('.')]
    
    logger.info(f"\n发现 {len(modules)} 个模块: {modules}")
    logger.info("\n开始更新模块...")
    
    modules_data = []
    for module in modules:
        module_dir = os.path.join(CHAPTER_PATH, module)
        data = update_module_index(module_dir, module, config, dry_run)
        if data:
            modules_data.append(data)
    
    logger.info("\n开始更新章节...")
    update_chapter_index(modules_data, config, dry_run)
    
    logger.info("\n" + "=" * 60)
    logger.info("完成！")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()