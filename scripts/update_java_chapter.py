#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
05-java-security 章节级 index.md 自动生成脚本
优化版：使用 common.py 公共模块，模块名称添加链接
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import (
    logger, load_config, read_index_metadata, get_current_time,
    safe_write, progress_bar, get_knowledge_path
)

# ==================== 配置 ====================
KNOWLEDGE_PATH = get_knowledge_path()
CHAPTER_PATH = os.path.join(KNOWLEDGE_PATH, "05-java-security")

# 模块显示名称映射（将目录名转为友好显示名）
MODULE_DISPLAY_NAMES = {
    'framework-vulns': 'Framework Vulns',
    'java-deserialization': 'Java Deserialization',
    'jndi-injection': 'Jndi Injection',
    'memory-shell': 'Memory Shell'
}

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

def get_display_name(module_name: str) -> str:
    """获取模块的显示名称"""
    return MODULE_DISPLAY_NAMES.get(module_name, module_name.replace('-', ' ').title())

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
    
    modules = [d for d in os.listdir(CHAPTER_PATH)
               if os.path.isdir(os.path.join(CHAPTER_PATH, d))
               and not d.startswith('.')]
    
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
        metadata = read_index_metadata(module_path)
        
        module_total = metadata.get('total_notes', 0)
        module_completed = metadata.get('completed', 0)
        module_in_progress = metadata.get('in_progress', 0)
        module_not_started = metadata.get('not_started', 0)
        module_rate = metadata.get('completion_rate', 0)
        module_status = metadata.get('status', '⬜')
        
        modules_data.append({
            'name': module_name,
            'display_name': get_display_name(module_name),
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