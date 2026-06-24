#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTF 板块所有模块的 index.md 自动生成脚本
优化版：使用 common.py 公共模块，功能与原脚本完全一致
"""

import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, load_config, read_metadata, get_current_time,
    safe_write, need_update, setup_from_args, progress_bar
)

# ==================== 配置 ====================
PROJECT_ROOT = r"E:\youth-sandbox\docs"
CTF_PATH = os.path.join(PROJECT_ROOT, "tech-study", "practice", "ctf")

# 模块级模板（与原脚本完全一致）
MODULE_TEMPLATE = '''---
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
| 总题目 | {total} |
| ✅ 已完成 | {completed} |
| 🔄 进行中 | {in_progress} |
| ⬜ 未开始 | {not_started} |
| 完成率 | {progress_bar} |

## 📝 题目列表

| 题目 | 难度 | 状态 | WriteUp |
|------|:----:|:----:|---------|
{rows}

## 💡 刷题建议

1. **由易到难**：先做 ⭐⭐ 题目，建立信心
2. **总结归纳**：每道题记录解题思路和踩坑点
3. **举一反三**：尝试多种解法，拓展思路
4. **定期复盘**：回顾旧题，加深理解

## 🏆 刷题目标

- [ ] 完成所有 ⭐⭐ 题目 → 基础达标
- [ ] 完成所有 ⭐⭐⭐ 题目 → 进阶突破
- [ ] 完成全部题目 → 🎉 通关成就

## 🔗 常用工具

| 工具 | 用途 |
|------|------|
| Burp Suite | 抓包改包 |
| Python | 脚本编写 |
| CyberChef | 编码解码 |
| Dirsearch | 目录扫描 |

## 📌 快速导航

- **返回** [CTF章节](../index.md)

---
*最后更新：{last_updated} | 保持练习，持续进步 💪*
'''

def read_submodule_metadata(submodule_path: str) -> dict:
    """读取子模块的 index.md 的 Front Matter"""
    index_path = os.path.join(submodule_path, 'index.md')
    return read_metadata(index_path)

def generate_module_index(module_path: str, module_name: str, dry_run: bool = False) -> bool:
    """生成单个模块的 index.md"""
    logger.info(f"\n处理模块: {module_name}")
    
    # 获取所有子目录（题目）
    submodules = [d for d in os.listdir(module_path)
                  if os.path.isdir(os.path.join(module_path, d))
                  and not d.startswith('.')]
    
    if not submodules:
        logger.warning(f"  跳过：无子目录")
        return False
    
    # 读取每个题目的元数据
    modules_data = []
    for name in submodules:
        sub_path = os.path.join(module_path, name)
        metadata = read_submodule_metadata(sub_path)
        
        title = metadata.get('title', name)
        level = metadata.get('level', '⭐⭐')
        status = metadata.get('status', '⬜')
        
        modules_data.append({
            'name': name,
            'title': title,
            'level': level,
            'status': status
        })
    
    # 统计
    total = len(modules_data)
    completed = sum(1 for m in modules_data if m['status'] == '✅')
    in_progress = sum(1 for m in modules_data if m['status'] == '🔄')
    not_started = sum(1 for m in modules_data if m['status'] == '⬜')
    completion_rate = int(completed / total * 100) if total > 0 else 0
    
    # 生成表格行
    rows = []
    for m in modules_data:
        writeup_link = f"[📖]({m['name']}/)" if m['status'] == '✅' else "-"
        rows.append(f"| {m['title']} | {m['level']} | {m['status']} | {writeup_link} |")
    
    rows_str = "\n".join(rows)
    progress = progress_bar(completion_rate)
    last_updated = get_current_time()
    
    module_title = f"{module_name.upper()} WriteUp"
    module_description = f"{module_name}靶场解题记录"
    
    content = MODULE_TEMPLATE.format(
        module_title=module_title,
        module_description=module_description,
        total=total,
        completed=completed,
        in_progress=in_progress,
        not_started=not_started,
        completion_rate=completion_rate,
        progress_bar=progress,
        rows=rows_str,
        last_updated=last_updated
    )
    
    output_path = os.path.join(module_path, 'index.md')
    
    if safe_write(output_path, content, dry_run):
        logger.info(f"  ✅ 已生成: {output_path}")
        logger.info(f"     总题目: {total}, 已完成: {completed}, 完成率: {completion_rate}%")
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
    logger.info("CTF 板块所有模块 index.md 生成")
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
    
    logger.info(f"发现模块: {modules}")
    
    success = 0
    for module_name in modules:
        module_path = os.path.join(CTF_PATH, module_name)
        if generate_module_index(module_path, module_name, dry_run):
            success += 1
    
    logger.info(f"\n完成: 成功 {success}/{len(modules)} 个模块")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()