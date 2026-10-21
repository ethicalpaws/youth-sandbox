#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 模块级 index.md 自动生成脚本
优化版：使用 common.py 公共模块

支持两种目录层级：
1. lab/<平台>/<靶场>/<笔记>.md
2. lab/<平台>/<分类>/<靶场>/<笔记>.md
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, load_config, read_index_metadata, get_current_time,
    safe_write, progress_bar, to_str,
    get_meta, normalize_status, get_status_emoji, is_real_dir,
    has_markdown, list_note_files
)

# ==================== 配置 ====================
PROJECT_ROOT = r"E:\youth-sandbox\docs"
LAB_PATH = os.path.join(PROJECT_ROOT, "tech-study", "practice", "lab")

# 平台/分类目录的展示名称；未登记时回退到目录名
MODULE_DISPLAY_NAMES = {
    'selfsetup': '自建环境',
    'ulab': 'ULab',
    'vulnstack': 'VulnStack',
}
CATEGORY_DISPLAY_NAMES = {
    'internal-network': '内网渗透',
    'IR': '应急响应',
}

# 模块级模板
MODULE_TEMPLATE = '''---
title: {module_title}
description: {module_description}
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

| 靶场 | 分类 | 难度 | 状态 |
|------|:----:|:----:|:----:|
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

# 分类目录（如 ulab/internal-network）的模板
COLLECTION_TEMPLATE = '''---
title: {title}
description: {description}
total: {total}
completed: {completed}
in_progress: {in_progress}
not_started: {not_started}
completion_rate: {completion_rate}
last_updated: {last_updated}
---

# 🎯 {title}

> {description}

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

## 📌 快速导航

| 靶场 | 链接 |
|------|------|
{nav_rows}

---
*最后更新：{last_updated} | 保持练习，持续进步 💪*
'''


def get_display_name(name: str, mapping: dict) -> str:
    """优先使用中文展示名，未登记时回退到目录名"""
    return mapping.get(name, name)


def cn_join(prefix: str, suffix: str) -> str:
    """中文展示名直接拼接，英文/数字展示名之间保留空格"""
    sep = ' ' if prefix and prefix[-1].isascii() else ''
    return f"{prefix}{sep}{suffix}"


def find_target_dirs(module_path: str) -> list:
    """
    递归查找真正包含笔记的靶场目录。

    返回 [(target_dir, rel_parts), ...]；例如：
    - lab/ulab/internal-network/zerologon -> (..., ['internal-network', 'zerologon'])
    - lab/ulab/IR/IR1.md                 -> (..., ['IR', 'IR1.md'])
    - lab/selfsetup/deployment           -> (..., ['deployment'])
    """
    targets = []

    def walk(current_path: str, rel_parts: list) -> None:
        # 目录本身直接有笔记：视为靶场，不再向下递归
        if list_note_files(current_path):
            targets.append((current_path, rel_parts))
            return

        for name in sorted(os.listdir(current_path)):
            if name.startswith('.'):
                continue
            child = os.path.join(current_path, name)
            if not os.path.isdir(child):
                continue
            # 跳过纯图片目录和空占位目录
            if not has_markdown(child):
                continue
            walk(child, rel_parts + [name])

    walk(module_path, [])
    return targets


def collect_targets(module_path: str, difficulty_config: dict) -> list:
    """读取所有靶场的 index.md 元数据"""
    targets_data = []
    for target_dir, rel_parts in find_target_dirs(module_path):
        metadata = read_index_metadata(target_dir)
        name = rel_parts[-1] if rel_parts else os.path.basename(module_path)
        title = get_meta(metadata, 'title', name)
        status_cn = normalize_status(get_meta(metadata, 'status', '未开始'))
        difficulty = get_meta(metadata, 'difficulty', '中等')
        last_updated = to_str(get_meta(metadata, 'last_updated', ''))

        targets_data.append({
            'name': name,
            'title': title,
            'rel_path': '/'.join(rel_parts) if rel_parts else '.',
            'category': rel_parts[0] if len(rel_parts) > 1 else '',
            'path': target_dir,
            'status_cn': status_cn,
            'status_emoji': get_status_emoji(status_cn),
            'difficulty': difficulty,
            'level': difficulty_config.get(difficulty, {}).get('level', '⭐⭐'),
            'last_updated': last_updated,
        })
    return targets_data


def summarize(targets_data: list) -> dict:
    """汇总靶场状态"""
    total = len(targets_data)
    completed = sum(1 for m in targets_data if m['status_cn'] == '已完成')
    in_progress = sum(1 for m in targets_data if m['status_cn'] == '进行中')
    not_started = sum(1 for m in targets_data if m['status_cn'] == '未开始')
    completion_rate = int(completed / total * 100) if total > 0 else 0
    return {
        'total': total,
        'completed': completed,
        'in_progress': in_progress,
        'not_started': not_started,
        'completion_rate': completion_rate,
        'progress_bar': progress_bar(completion_rate),
    }


def generate_collection_indexes(module_path: str, targets_data: list,
                                dry_run: bool = False) -> int:
    """为 ulab/internal-network、ulab/IR 等分类目录生成汇总 index.md"""
    groups = {}
    for target in targets_data:
        if target['category']:
            groups.setdefault(target['category'], []).append(target)

    generated = 0
    for category, items in sorted(groups.items()):
        category_dir = os.path.join(module_path, category)
        if not os.path.isdir(category_dir):
            continue

        stats = summarize(items)
        display = get_display_name(category, CATEGORY_DISPLAY_NAMES)
        title = cn_join(display, "靶场集")
        description = cn_join(display, "分类下的靶场渗透记录")

        sorted_items = sorted(
            items,
            key=lambda x: (x['status_cn'] != '已完成', x['name'])
        )
        rows = []
        nav_rows = []
        for item in sorted_items:
            rel_path = os.path.relpath(item['path'], category_dir).replace(os.sep, '/')
            rows.append(f"| {item['title']} | {item['level']} | {item['status_emoji']} |")
            nav_rows.append(f"| {item['title']} | [{rel_path}/]({rel_path}/) |")

        last_updated = get_current_time()
        content = COLLECTION_TEMPLATE.format(
            title=title,
            description=description,
            total=stats['total'],
            completed=stats['completed'],
            in_progress=stats['in_progress'],
            not_started=stats['not_started'],
            completion_rate=stats['completion_rate'],
            progress_bar=stats['progress_bar'],
            rows="\n".join(rows),
            nav_rows="\n".join(nav_rows),
            last_updated=last_updated,
        )
        output_path = os.path.join(category_dir, 'index.md')
        if safe_write(output_path, content, dry_run):
            logger.info(f"    ✅ 分类索引: {category}/index.md")
            generated += 1

    return generated


def generate_module_index(module_path: str, module_name: str,
                          dry_run: bool = False) -> bool:
    """生成单个模块的 index.md"""
    logger.info(f"\n处理模块: {module_name}")

    difficulty_config = load_config().get('difficulty_config', {})
    targets_data = collect_targets(module_path, difficulty_config)

    if not targets_data:
        logger.warning("  跳过：无靶场目录")
        return False

    generate_collection_indexes(module_path, targets_data, dry_run)

    stats = summarize(targets_data)
    display_name = get_display_name(module_name, MODULE_DISPLAY_NAMES)

    rows = []
    nav_rows = []
    for m in sorted(targets_data, key=lambda x: (x['status_cn'] != '已完成', x['name'])):
        if m['category']:
            category_display = get_display_name(m['category'], CATEGORY_DISPLAY_NAMES)
            category_label = f"[{category_display}]({m['category']}/)"
        else:
            category_label = "—"
        rows.append(
            f"| {m['title']} | {category_label} | {m['level']} | {m['status_emoji']} |"
        )
        nav_rows.append(f"| {m['title']} | [{m['rel_path']}/]({m['rel_path']}/) |")

    recent = [m for m in targets_data if m.get('last_updated')]
    recent.sort(key=lambda x: x['last_updated'], reverse=True)
    recent_lines = [f"- **{r['title']}** ({r['last_updated'][:10]}) : {r['status_emoji']}"
                    for r in recent[:5]] or ["- 暂无更新记录"]

    last_updated = get_current_time()
    module_title = cn_join(display_name, "靶场集")
    module_description = cn_join(display_name, "靶场渗透记录")

    content = MODULE_TEMPLATE.format(
        module_title=module_title,
        module_description=module_description,
        total=stats['total'],
        completed=stats['completed'],
        in_progress=stats['in_progress'],
        not_started=stats['not_started'],
        completion_rate=stats['completion_rate'],
        progress_bar=stats['progress_bar'],
        rows="\n".join(rows),
        nav_rows="\n".join(nav_rows),
        recent_updates="\n".join(recent_lines),
        last_updated=last_updated,
    )

    output_path = os.path.join(module_path, 'index.md')

    if safe_write(output_path, content, dry_run):
        logger.info(f"  ✅ 已生成: {output_path}")
        logger.info(
            f"     总靶场: {stats['total']}, 已攻略: {stats['completed']}, "
            f"完成率: {stats['completion_rate']}%"
        )
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

    modules = [d for d in sorted(os.listdir(LAB_PATH))
               if is_real_dir(os.path.join(LAB_PATH, d))]

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
