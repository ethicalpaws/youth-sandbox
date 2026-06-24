#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRC 模块级 index.md 自动生成脚本
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
SRC_PATH = os.path.join(PROJECT_ROOT, "tech-study", "practice", "src")

# 模块级模板（完全保持原样）
MODULE_TEMPLATE = '''---
total: {total}
completed: {completed}
in_progress: {in_progress}
not_started: {not_started}
completion_rate: {completion_rate}
bounty: {bounty}
critical_count: {critical_count}
high_count: {high_count}
medium_count: {medium_count}
low_count: {low_count}
last_updated: {last_updated}
---

# 🎯 {module_title}

> {module_description}

## 📊 挖掘进度

| 指标 | 数值 |
|------|:----:|
| 总目标 | {total} |
| ✅ 已提交 | {completed} |
| 🔄 挖掘中 | {in_progress} |
| ⬜ 待开始 | {not_started} |
| 累计奖金 | 💰 {bounty} 元 |
| 完成率 | {progress_bar} |

## 🏆 漏洞等级分布

| 等级 | 数量 | 占比 |
|------|:----:|:----:|
| 严重 | {critical_count} | {critical_percent}% |
| 高危 | {high_count} | {high_percent}% |
| 中危 | {medium_count} | {medium_percent}% |
| 低危 | {low_count} | {low_percent}% |

## 📝 目标列表

| 目标 | 漏洞类型 | 危害等级 | 状态 |
|------|---------|:----:|:----:|
{rows}

## 💡 挖掘建议

1. **信息收集**：子域名枚举、目录扫描、指纹识别
2. **寻找切入点**：测试所有功能点、关注边缘业务
3. **漏洞验证**：确认漏洞存在性和危害
4. **报告编写**：清晰描述漏洞和修复方案

## 📌 快速导航

| 目标 | 链接 |
|------|------|
{nav_rows}

## 📝 近期更新

{recent_updates}

---
*最后更新：{last_updated} | 持续挖洞，积累经验 💪*
'''

def normalize_status(status_raw):
    """将各种格式的状态统一为标准中文"""
    if status_raw in ['✅', '已完成']:
        return '已完成'
    elif status_raw in ['🔄', '进行中']:
        return '进行中'
    else:
        return '未开始'

def get_level_from_difficulty(difficulty: str, level: str) -> str:
    """获取危害等级（星级）"""
    if level:
        return level
    level_map = {'简单': '⭐', '中等': '⭐⭐', '困难': '⭐⭐⭐', '专家': '⭐⭐⭐⭐'}
    return level_map.get(difficulty, '⭐⭐')

def generate_module_index(module_path: str, module_name: str, dry_run: bool = False) -> bool:
    """生成单个模块的 index.md"""
    logger.info(f"\n处理模块: {module_name}")
    
    status_map = load_config().get('status_map', {})
    
    targets = [d for d in os.listdir(module_path)
               if os.path.isdir(os.path.join(module_path, d))
               and not d.startswith('.')]
    
    if not targets:
        logger.warning(f"  跳过：无目标目录")
        return False
    
    targets_data = []
    total_bounty = 0
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    
    for name in targets:
        target_dir = os.path.join(module_path, name)
        metadata = read_index_metadata(target_dir)
        
        title = metadata.get('title', name)
        status_raw = metadata.get('status', '未开始')
        status_cn = normalize_status(status_raw)
        difficulty = metadata.get('difficulty', '中等')
        weakness = metadata.get('weakness', '待补充')
        level = metadata.get('level', '')
        bounty = metadata.get('bounty', 0)
        last_updated = to_str(metadata.get('last_updated', ''))
        
        status_icon = status_map.get(status_raw, '⬜')
        
        # 统计等级分布
        level_star = get_level_from_difficulty(difficulty, level)
        if level_star == '⭐⭐⭐⭐':
            critical_count += 1
        elif level_star == '⭐⭐⭐':
            high_count += 1
        elif level_star == '⭐⭐':
            medium_count += 1
        elif level_star == '⭐':
            low_count += 1
        
        total_bounty += bounty
        
        targets_data.append({
            'name': name,
            'title': title,
            'status_cn': status_cn,
            'status_icon': status_icon,
            'weakness': weakness,
            'level': level_star,
            'last_updated': last_updated
        })
    
    total = len(targets_data)
    completed = sum(1 for t in targets_data if t['status_cn'] == '已完成')
    in_progress = sum(1 for t in targets_data if t['status_cn'] == '进行中')
    not_started = sum(1 for t in targets_data if t['status_cn'] == '未开始')
    completion_rate = int(completed / total * 100) if total > 0 else 0
    progress = progress_bar(completion_rate)
    
    total_vulns = critical_count + high_count + medium_count + low_count
    critical_percent = int(critical_count / total_vulns * 100) if total_vulns > 0 else 0
    high_percent = int(high_count / total_vulns * 100) if total_vulns > 0 else 0
    medium_percent = int(medium_count / total_vulns * 100) if total_vulns > 0 else 0
    low_percent = int(low_count / total_vulns * 100) if total_vulns > 0 else 0
    
    rows = []
    nav_rows = []
    for t in sorted(targets_data, key=lambda x: (x['status_cn'] != '已完成', x['name'])):
        rows.append(f"| {t['title']} | {t['weakness']} | {t['level']} | {t['status_icon']} |")
        nav_rows.append(f"| {t['title']} | [{t['name']}/]({t['name']}/) |")
    
    recent = [t for t in targets_data if t.get('last_updated')]
    recent.sort(key=lambda x: x['last_updated'], reverse=True)
    recent_lines = [f"- **{r['title']}** ({r['last_updated'][:10]}) : {r['status_icon']}"
                    for r in recent[:5]] or ["- 暂无更新记录"]
    
    last_updated = get_current_time()
    
    content = MODULE_TEMPLATE.format(
        module_title=f"{module_name} 目标集",
        module_description=f"{module_name} 平台漏洞挖掘记录",
        total=total,
        completed=completed,
        in_progress=in_progress,
        not_started=not_started,
        completion_rate=completion_rate,
        progress_bar=progress,
        bounty=total_bounty,
        critical_count=critical_count,
        critical_percent=critical_percent,
        high_count=high_count,
        high_percent=high_percent,
        medium_count=medium_count,
        medium_percent=medium_percent,
        low_count=low_count,
        low_percent=low_percent,
        rows="\n".join(rows),
        nav_rows="\n".join(nav_rows),
        recent_updates="\n".join(recent_lines),
        last_updated=last_updated
    )
    
    output_path = os.path.join(module_path, 'index.md')
    
    if safe_write(output_path, content, dry_run):
        logger.info(f"  ✅ 已生成: {output_path}")
        logger.info(f"     总目标: {total}, 已提交: {completed}, 奖金: {total_bounty}元")
        logger.info(f"     等级分布: 严重:{critical_count}, 高危:{high_count}, 中危:{medium_count}, 低危:{low_count}")
        return True
    
    return False

def scan_and_update(dry_run: bool = False) -> None:
    """扫描并更新所有 SRC 模块"""
    logger.info("=" * 60)
    logger.info("SRC 模块级 index.md 自动生成脚本")
    logger.info("=" * 60)
    logger.info(f"扫描路径: {SRC_PATH}")
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")
    
    if not os.path.exists(SRC_PATH):
        logger.error(f"路径不存在: {SRC_PATH}")
        return
    
    modules = [d for d in os.listdir(SRC_PATH)
               if os.path.isdir(os.path.join(SRC_PATH, d))
               and not d.startswith('.')]
    
    if not modules:
        logger.warning("未找到任何模块")
        return
    
    logger.info(f"发现模块: {modules}")
    
    success = 0
    for module_name in modules:
        module_path = os.path.join(SRC_PATH, module_name)
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