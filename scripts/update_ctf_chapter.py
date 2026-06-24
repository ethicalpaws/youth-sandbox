#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTF 章节级 index.md 自动生成脚本
优化版：使用 common.py 公共模块，功能与原脚本完全一致
"""

import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, load_config, read_index_metadata, get_current_time,
    safe_write, need_update, progress_bar, to_str
)

# ==================== 配置 ====================
PROJECT_ROOT = r"E:\youth-sandbox\docs"
CTF_PATH = os.path.join(PROJECT_ROOT, "tech-study", "practice", "ctf")

# 章节级模板（与原脚本完全一致）
CHAPTER_TEMPLATE = '''---
total_modules: {total_modules}
total_questions: {total_questions}
completed_questions: {completed_questions}
in_progress_questions: {in_progress_questions}
not_started_questions: {not_started_questions}
completion_rate: {completion_rate}
last_updated: {last_updated}
---

# 🎯 CTF 训练场

> 各大CTF比赛WriteUp汇总

## 📊 整体进度

| 指标 | 数值 |
|------|:----:|
| 模块总数 | {total_modules} |
| 总题目数 | {total_questions} |
| ✅ 已解决 | {completed_questions} |
| 🔄 进行中 | {in_progress_questions} |
| ⬜ 未开始 | {not_started_questions} |
| 整体完成率 | {progress_bar} |

## 📚 模块列表

| 模块 | 题目数 | 已完成 | 完成率 | 状态 |
|------|:------:|:------:|:------:|:----:|
{module_rows}

## 🔥 热门漏洞类型

| 漏洞类型 | 题目数 | 掌握程度 |
|---------|:------:|:--------:|
| SQL注入 | 3 | 🟢 熟练 |
| XSS跨站脚本 | 2 | 🟡 学习中 |
| 反序列化 | 4 | 🟡 学习中 |
| 命令注入 | 2 | 🟢 熟练 |
| 文件上传 | 1 | 🔴 待加强 |
| SSRF | 1 | 🔴 待加强 |

## 💡 刷题建议

1. **按模块刷题**：先完成一个模块的所有题目
2. **难度递进**：从 ⭐⭐ 到 ⭐⭐⭐
3. **总结归纳**：每道题写WriteUp，形成知识库
4. **定期复习**：回顾旧题，巩固知识点

## 🏆 通关里程碑

- [ ] 完成 10 道题 → 🎖️ CTF新手
- [ ] 完成 30 道题 → 🏅 CTF进阶
- [ ] 完成 50 道题 → 🏆 CTF高手
- [ ] 完成所有题目 → 👑 CTF大师

## 🛠️ 常用工具链

| 工具 | 用途 | 熟练度 |
|------|------|:------:|
| Burp Suite | 抓包改包/重放攻击 | ⭐⭐⭐ |
| Python | POC编写/自动化 | ⭐⭐⭐ |
| CyberChef | 编码/解码/加解密 | ⭐⭐ |
| Dirsearch | 目录扫描 | ⭐⭐ |
| Nmap | 端口扫描/服务探测 | ⭐⭐ |
| JADX | APK反编译 | ⭐ |

## 📖 学习资源

| 资源 | 链接 | 说明 |
|------|------|------|
| CTF Wiki | [https://ctf-wiki.org/](https://ctf-wiki.org/) | CTF知识库 |
| BugKu | [https://ctf.bugku.com/](https://ctf.bugku.com/) | CTF练习平台 |
| Buuoj | [https://buuoj.cn/](https://buuoj.cn/) | CTF题目合集 |
| PicoCTF | [https://picoctf.org/](https://picoctf.org/) | 入门级CTF |

## 📌 快速导航

| 模块 | 链接 |
|------|------|
{nav_rows}

## 📝 近期更新

{recent_updates}

---
*最后更新：{last_updated} | 保持练习，持续进步 💪*
'''

def generate_ctf_index(dry_run: bool = False) -> None:
    """生成 CTF 章节 index.md"""
    logger.info("=" * 60)
    logger.info("CTF 章节级 index.md 生成")
    logger.info("=" * 60)
    logger.info(f"路径: {CTF_PATH}")
    
    if not os.path.exists(CTF_PATH):
        logger.error(f"路径不存在: {CTF_PATH}")
        return
    
    modules = [d for d in os.listdir(CTF_PATH)
               if os.path.isdir(os.path.join(CTF_PATH, d))
               and not d.startswith('.')]
    
    if not modules:
        logger.warning("未找到任何模块")
        return
    
    modules_data = []
    total_questions = 0
    completed_questions = 0
    in_progress_questions = 0
    not_started_questions = 0
    
    for name in modules:
        module_path = os.path.join(CTF_PATH, name)
        metadata = read_index_metadata(module_path)
        
        total = metadata.get('total', 0)
        completed = metadata.get('completed', 0)
        in_progress = metadata.get('in_progress', 0)
        not_started = metadata.get('not_started', 0)
        completion_rate = metadata.get('completion_rate', 0)
        last_updated = to_str(metadata.get('last_updated', ''))
        
        modules_data.append({
            'name': name,
            'title': name.upper(),
            'total': total,
            'completed': completed,
            'completion_rate': completion_rate,
            'last_updated': last_updated
        })
        
        total_questions += total
        completed_questions += completed
        in_progress_questions += in_progress
        not_started_questions += not_started
    
    completion_rate = int(completed_questions / total_questions * 100) if total_questions > 0 else 0
    progress = progress_bar(completion_rate)
    
    # 生成模块表格行
    module_rows = []
    nav_rows = []
    
    for m in sorted(modules_data, key=lambda x: x['completion_rate'], reverse=True):
        if m['completion_rate'] == 100:
            status_icon = "✅"
        elif m['completion_rate'] > 0:
            status_icon = "🔄"
        else:
            status_icon = "⬜"
        
        module_rows.append(f"| {m['title']} | {m['total']} | {m['completed']} | {m['completion_rate']}% | {status_icon} |")
        nav_rows.append(f"| {m['title']} | [{m['name']}/]({m['name']}/) |")
    
    module_rows_str = "\n".join(module_rows)
    nav_rows_str = "\n".join(nav_rows)
    
    # 生成近期更新
    recent = [m for m in modules_data if m.get('last_updated')]
    recent.sort(key=lambda x: x['last_updated'], reverse=True)
    
    recent_lines = []
    for r in recent[:5]:
        date_str = r['last_updated'][:10] if len(r['last_updated']) >= 10 else r['last_updated']
        recent_lines.append(f"- **{r['title']}** ({date_str}) : {r['completed']}/{r['total']} 题已完成")
    
    if not recent_lines:
        recent_lines = ["- 暂无更新记录"]
    recent_updates = "\n".join(recent_lines)
    
    last_updated = get_current_time()
    
    content = CHAPTER_TEMPLATE.format(
        total_modules=len(modules),
        total_questions=total_questions,
        completed_questions=completed_questions,
        in_progress_questions=in_progress_questions,
        not_started_questions=not_started_questions,
        completion_rate=completion_rate,
        progress_bar=progress,
        module_rows=module_rows_str,
        nav_rows=nav_rows_str,
        recent_updates=recent_updates,
        last_updated=last_updated
    )
    
    output_path = os.path.join(CTF_PATH, 'index.md')
    
    if safe_write(output_path, content, dry_run):
        logger.info(f"✅ 已生成: {output_path}")
        logger.info(f"   模块数: {len(modules)}")
        logger.info(f"   总题目: {total_questions}, 已完成: {completed_questions}, 完成率: {completion_rate}%")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    generate_ctf_index(dry_run)