#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CVE 章节级 index.md 自动生成脚本
优化版：使用 common.py 公共模块，功能与原脚本完全一致
"""

import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, load_config, read_index_metadata, get_current_time,
    safe_write, progress_bar, to_str
)

# ==================== 配置 ====================
PROJECT_ROOT = r"E:\youth-sandbox\docs"
CVE_PATH = os.path.join(PROJECT_ROOT, "tech-study", "practice", "cve")

# 章节级模板（完全保持原样）
CHAPTER_TEMPLATE = '''---
total_cves: {total_cves}
analyzed: {analyzed}
in_progress: {in_progress}
not_started: {not_started}
completion_rate: {completion_rate}
last_updated: {last_updated}
---

# 🐞 CVE 漏洞分析

> 真实CVE漏洞复现与分析记录

## 📊 学习进度

| 指标 | 数值 |
|------|:----:|
| CVE总数 | {total_cves} |
| ✅ 已分析 | {analyzed} |
| 🔄 分析中 | {in_progress} |
| ⬜ 未开始 | {not_started} |
| 完成率 | {progress_bar} |

## 📋 漏洞列表

| CVE编号 | 漏洞描述 | 危害等级 | 难度 | 状态 |
|---------|---------|:----:|:----:|:----:|
{rows}

## 🔥 漏洞类型分布

| 漏洞类型 | 数量 | 占比 |
|---------|:----:|:----:|
{type_rows}

## 💡 学习建议

1. **理解原理**：不要只复现，要理解漏洞根因
2. **动手实践**：搭建环境亲自复现
3. **代码审计**：阅读源码，理解触发点
4. **关联拓展**：学习相似漏洞

## 🏆 里程碑

- [ ] 分析 5 个 CVE → 🎖️ 漏洞初学者
- [ ] 分析 10 个 CVE → 🏅 漏洞研究员
- [ ] 分析 20 个 CVE → 🏆 漏洞专家

## 📌 快速导航

| CVE | 链接 |
|------|------|
{nav_rows}

## 📝 近期更新

{recent_updates}

---
*最后更新：{last_updated} | 持续学习，深度思考 💪*
'''

def normalize_status(status_raw):
    """将各种格式的状态统一为标准中文"""
    if status_raw in ['✅', '已完成', '完成']:
        return '已完成'
    elif status_raw in ['🔄', '进行中', '分析中']:
        return '进行中'
    else:
        return '未开始'

def get_risk_level(difficulty: str, cvss: str) -> str:
    """根据难度和CVSS评分获取危害等级"""
    risk_map = {'简单': '低危', '中等': '中危', '困难': '高危', '专家': '严重'}
    
    if cvss and cvss != '待补充':
        try:
            score = float(cvss)
            if score >= 9.0:
                return "严重"
            elif score >= 7.0:
                return "高危"
            elif score >= 4.0:
                return "中危"
            else:
                return "低危"
        except:
            pass
    
    return risk_map.get(difficulty, '中危')

def generate_cve_chapter(dry_run: bool = False) -> None:
    """生成 CVE 章节 index.md"""
    logger.info("=" * 60)
    logger.info("CVE 章节级 index.md 生成")
    logger.info("=" * 60)
    logger.info(f"路径: {CVE_PATH}")
    
    if not os.path.exists(CVE_PATH):
        logger.error(f"路径不存在: {CVE_PATH}")
        return
    
    cve_dirs = [d for d in os.listdir(CVE_PATH)
                if os.path.isdir(os.path.join(CVE_PATH, d))
                and not d.startswith('.')]
    
    if not cve_dirs:
        logger.warning("未找到任何 CVE 目录")
        return
    
    cves_data = []
    type_count = {}
    
    for name in cve_dirs:
        cve_dir = os.path.join(CVE_PATH, name)
        metadata = read_index_metadata(cve_dir)
        
        title = metadata.get('title', name)
        description = metadata.get('description', '')
        status_raw = metadata.get('status', '未开始')
        status_cn = normalize_status(status_raw)
        difficulty = metadata.get('difficulty', '中等')
        cvss = metadata.get('cvss', '')
        cve_id = metadata.get('cve_id', name)
        weakness = metadata.get('weakness', '')
        last_updated = to_str(metadata.get('last_updated', ''))
        
        if weakness:
            type_count[weakness] = type_count.get(weakness, 0) + 1
        else:
            type_count['其他'] = type_count.get('其他', 0) + 1
        
        risk_level = get_risk_level(difficulty, cvss)
        
        status_map = {'已完成': '✅', '进行中': '🔄', '未开始': '⬜'}
        status_icon = status_map.get(status_cn, '⬜')
        
        cves_data.append({
            'name': name,
            'title': title,
            'description': description,
            'status_cn': status_cn,
            'status_icon': status_icon,
            'difficulty': difficulty,
            'risk': risk_level,
            'cve_id': cve_id,
            'weakness': weakness,
            'last_updated': last_updated
        })
    
    total = len(cves_data)
    analyzed = sum(1 for c in cves_data if c['status_cn'] == '已完成')
    in_progress = sum(1 for c in cves_data if c['status_cn'] == '进行中')
    not_started = sum(1 for c in cves_data if c['status_cn'] == '未开始')
    completion_rate = int(analyzed / total * 100) if total > 0 else 0
    progress = progress_bar(completion_rate)
    
    rows = []
    nav_rows = []
    
    for c in sorted(cves_data, key=lambda x: (x['status_cn'] != '已完成', x['name'])):
        desc_short = c['description'][:50] + "..." if len(c['description']) > 50 else c['description']
        rows.append(f"| {c['cve_id']} | {desc_short} | {c['risk']} | {c['difficulty']} | {c['status_icon']} |")
        nav_rows.append(f"| {c['cve_id']} | [{c['name']}/]({c['name']}/) |")
    
    rows_str = "\n".join(rows)
    nav_rows_str = "\n".join(nav_rows)
    
    type_rows = []
    for t, count in sorted(type_count.items(), key=lambda x: x[1], reverse=True):
        percent = int(count / total * 100) if total > 0 else 0
        type_rows.append(f"| {t} | {count} | {percent}% |")
    type_rows_str = "\n".join(type_rows) if type_rows else "| 暂无 | 0 | 0% |"
    
    recent = [c for c in cves_data if c.get('last_updated')]
    recent.sort(key=lambda x: x['last_updated'], reverse=True)
    
    recent_lines = []
    for r in recent[:5]:
        date_str = r['last_updated'][:10] if len(r['last_updated']) >= 10 else r['last_updated']
        recent_lines.append(f"- **{r['cve_id']}** ({date_str}) : {r['status_icon']}")
    
    if not recent_lines:
        recent_lines = ["- 暂无更新记录"]
    recent_updates = "\n".join(recent_lines)
    
    last_updated = get_current_time()
    
    content = CHAPTER_TEMPLATE.format(
        total_cves=total,
        analyzed=analyzed,
        in_progress=in_progress,
        not_started=not_started,
        completion_rate=completion_rate,
        progress_bar=progress,
        rows=rows_str,
        type_rows=type_rows_str,
        nav_rows=nav_rows_str,
        recent_updates=recent_updates,
        last_updated=last_updated
    )
    
    output_path = os.path.join(CVE_PATH, 'index.md')
    
    if safe_write(output_path, content, dry_run):
        logger.info(f"✅ 已生成: {output_path}")
        logger.info(f"   CVE总数: {total}, 已分析: {analyzed}, 完成率: {completion_rate}%")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    generate_cve_chapter(dry_run)