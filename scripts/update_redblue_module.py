#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
06-red-blue-confrontation 模块级 / 子模块级 index.md 自动生成脚本
优化版：使用 common.py 公共模块

递归处理 06 章节下的任意层级目录，例如：
  internal-network/
    authentication-protocol/
    lateral-movement/
    tools/
      credential-attack/
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, get_status_emoji, get_current_time, safe_write,
    get_knowledge_path, progress_bar,
    collect_notes_recursive, calculate_module_stats, is_real_dir
)

# ==================== 配置 ====================
KNOWLEDGE_PATH = get_knowledge_path()
CHAPTER_PATH = os.path.join(KNOWLEDGE_PATH, "06-red-blue-confrontation")

# 顶层模块显示名称
MODULE_DISPLAY_NAMES = {
    'blue-team': '🛡️ 蓝队防守',
    'c2-framework': '🎯 C2框架',
    'evasion': '👻 免杀与绕过',
    'hvv': '🛡️ HVV 攻防演练',
    'internal-network': '🌐 内网渗透',
    'lateral-movement': '🔄 横向移动',
    'penetration-test': '🔍 渗透测试',
    'persistence': '🔒 权限维持',
    'pivoting': '🔀 隧道与代理',
    'privesc': '⬆️ 权限提升',
    'pwn': '💥 二进制漏洞',
    'tools': '🔧 工具使用'
}

# 子模块显示名称，键为相对 06 章节的路径（小写）
PATH_DISPLAY_NAMES = {
    'privesc/linux': '🐧 Linux 提权',
    'privesc/windows': '🪟 Windows 提权',
    'hvv/basic': '🛡️ 蓝队基础',
    'hvv/incident-response': '🚨 应急响应',
    'hvv/研判': '🔍 研判分析',
    'internal-network/ad-delegation': '🧬 AD 委派',
    'internal-network/ad-basics': '📘 AD 基础',
    'internal-network/authentication-protocol': '🔐 认证协议',
    'internal-network/environment': '🧪 环境搭建',
    'internal-network/information-collection': '🔎 信息收集',
    'internal-network/kerberos-attack': '🎫 Kerberos 攻击',
    'internal-network/lateral-movement': '🔄 横向移动',
    'internal-network/password-capture': '🗝️ 密码抓取',
    'internal-network/proxy-tunnel': '🔀 代理隧道',
    'internal-network/ticket-attack': '🎟️ 票据攻击',
    'internal-network/tools': '🔧 工具使用',
    'internal-network/tools/credential-attack': '🔑 凭据攻击',
    'internal-network/tools/information-collection': '🔎 信息收集',
    'internal-network/tools/lateral-movement': '🔄 横向移动',
    'internal-network/tools/persistence': '🔒 权限维持',
    'internal-network/user-permissions': '👤 用户权限',
}

MODULE_TEMPLATE = '''---
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

## 模块状态：{module_status}

## 📊 学习统计

| 指标 | 数值 |
|------|:----:|
| 总笔记数 | {total_notes} |
| ✅ 已完成 | {completed} |
| 🔄 进行中 | {in_progress} |
| ⬜ 未开始 | {not_started} |
| 完成率 | {progress_bar} |

{children_section}## 📖 学习内容

{notes_table}

---
*自动更新：{update_time}
'''


def get_display_name(rel_parts: list) -> str:
    """按相对路径获取模块展示名，未登记时回退到目录名"""
    key = '/'.join(rel_parts).lower()
    if key in PATH_DISPLAY_NAMES:
        return PATH_DISPLAY_NAMES[key]

    leaf = rel_parts[-1].lower()
    if leaf in MODULE_DISPLAY_NAMES:
        return MODULE_DISPLAY_NAMES[leaf]

    return rel_parts[-1].replace('-', ' ').replace('_', ' ').title()


def build_children_section(children: list) -> str:
    """生成子模块表格；没有子模块时返回空字符串"""
    if not children:
        return ""

    rows = []
    for child in children:
        rows.append(
            f"| [{child['display_name']}]({child['name']}/) | "
            f"{child['total_notes']} | {child['completed']} | "
            f"{child['completion_rate']}% | {child['module_status']} |"
        )

    return (
        "## 📦 子模块\n\n"
        "| 子模块 | 笔记数 | 已完成 | 完成率 | 状态 |\n"
        "|--------|:------:|:------:|:------:|:----:|\n"
        + "\n".join(rows)
        + "\n\n"
    )


def build_notes_table(direct_notes: list) -> str:
    """生成当前目录直接包含的笔记表格"""
    if not direct_notes:
        return "_当前目录暂无直接笔记，请查看上方子模块。_"

    direct_notes = sorted(
        direct_notes,
        key=lambda x: x.get('finish_date', ''),
        reverse=True
    )
    lines = [
        "| 笔记 | 描述 | 状态 |",
        "|------|------|:----:|",
    ]
    for note in direct_notes:
        desc = note.get('description', '') or ''
        desc_short = desc[:50] + "..." if len(desc) > 50 else desc
        lines.append(
            f"| [{note['title']}]({note['file']}) | {desc_short} | "
            f"{get_status_emoji(note['status_cn'])} |"
        )
    return "\n".join(lines)


def build_module_index(module_dir: str, rel_parts: list,
                       notes_data: list, dry_run: bool = False):
    """
    递归生成目录的 index.md。

    先处理子模块，再生成当前目录，确保父级能汇总到子级统计。
    """
    if not notes_data:
        return None

    stats = calculate_module_stats(notes_data)
    direct_notes = [n for n in notes_data if '/' not in n['file']]

    children = []
    for name in sorted(os.listdir(module_dir)):
        if name.startswith('.'):
            continue
        child_dir = os.path.join(module_dir, name)
        if not os.path.isdir(child_dir):
            continue

        child_notes = collect_notes_recursive(child_dir)
        if not child_notes:
            continue

        child_data = build_module_index(
            child_dir, rel_parts + [name], child_notes, dry_run
        )
        if child_data:
            children.append(child_data)

    display_name = get_display_name(rel_parts)
    description = f"{display_name} 学习笔记"
    update_time = get_current_time()

    content = MODULE_TEMPLATE.format(
        module_name=display_name,
        description=description,
        module_status=stats['module_status'],
        total_notes=stats['total_notes'],
        completed=stats['completed'],
        in_progress=stats['in_progress'],
        not_started=stats['not_started'],
        completion_rate=stats['completion_rate'],
        progress_bar=progress_bar(stats['completion_rate']),
        children_section=build_children_section(children),
        notes_table=build_notes_table(direct_notes),
        update_time=update_time,
        last_updated=update_time
    )

    index_path = os.path.join(module_dir, 'index.md')
    if safe_write(index_path, content, dry_run):
        logger.info(
            f"    ✅ {os.path.join(*rel_parts)}/index.md "
            f"(笔记: {stats['total_notes']}, 完成: {stats['completed']}, "
            f"子模块: {len(children)})"
        )

    return {
        'name': rel_parts[-1],
        'rel_path': '/'.join(rel_parts),
        'display_name': display_name,
        'total_notes': stats['total_notes'],
        'completed': stats['completed'],
        'in_progress': stats['in_progress'],
        'not_started': stats['not_started'],
        'completion_rate': stats['completion_rate'],
        'module_status': stats['module_status']
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()

    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"

    logger.info("=" * 60)
    logger.info("06-red-blue-confrontation 模块/子模块 index.md 自动生成脚本")
    logger.info("=" * 60)
    logger.info(f"目标章节: {CHAPTER_PATH}")
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")

    if not os.path.exists(CHAPTER_PATH):
        logger.error(f"路径不存在: {CHAPTER_PATH}")
        return

    modules = [
        d for d in sorted(os.listdir(CHAPTER_PATH))
        if is_real_dir(os.path.join(CHAPTER_PATH, d))
    ]

    logger.info(f"\n发现 {len(modules)} 个顶层模块: {modules}")
    logger.info("\n开始递归更新模块...")

    modules_data = []
    for module_name in modules:
        module_dir = os.path.join(CHAPTER_PATH, module_name)
        notes_data = collect_notes_recursive(module_dir)
        data = build_module_index(module_dir, [module_name], notes_data, dry_run)
        if data:
            modules_data.append(data)

    logger.info("\n模块级更新完成；章节汇总请运行 update_redblue_chapter.py")
    logger.info("\n" + "=" * 60)
    logger.info(f"完成！成功处理 {len(modules_data)}/{len(modules)} 个顶层模块")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
