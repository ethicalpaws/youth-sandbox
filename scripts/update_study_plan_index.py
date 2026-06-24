#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_study_plan_index.py - 更新 study-plan/index.md
汇总所有周计划文件，生成带 Front Matter 的索引页面
"""

import os
import sys
import re
import io

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# 导入公共模块
try:
    from common import logger, load_config, get_current_time, safe_write, read_metadata
    HAS_COMMON = True
except ImportError:
    HAS_COMMON = False
    import logging
    from datetime import datetime
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    def get_current_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def safe_write(path, content, dry_run=False):
        if dry_run:
            print(f"[DRY RUN] 将写入: {path}")
            return True
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

# ==================== 配置 ====================
PROJECT_ROOT = r"E:\youth-sandbox\docs"
STUDY_PLAN_DIR = os.path.join(PROJECT_ROOT, "life", "study-plan")
OUTPUT_FILE = os.path.join(STUDY_PLAN_DIR, "index.md")

def parse_front_matter(content):
    """解析 YAML Front Matter"""
    if not content.startswith('---'):
        return {}
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}
    try:
        import yaml
        return yaml.safe_load(parts[1]) or {}
    except:
        return {}

def extract_theme_from_content(content):
    """从正文中提取阶段目标/主题"""
    match = re.search(r'>\s*\*\*阶段目标\*\*[：:]\s*([^\n]+)', content)
    if match:
        return match.group(1).strip()
    return "待补充"

def get_week_summary(week_num, content):
    """获取周次摘要（用于列表显示）"""
    # 优先从 Front Matter 获取
    metadata = parse_front_matter(content)
    if metadata.get('theme'):
        theme = metadata['theme']
        if len(theme) > 30:
            theme = theme[:27] + "..."
        return theme
    
    # 从正文提取
    theme = extract_theme_from_content(content)
    if len(theme) > 30:
        theme = theme[:27] + "..."
    return theme

def scan_week_files():
    """扫描所有 weekX.md 文件"""
    week_files = []
    pattern = re.compile(r'week(\d+)\.md')
    
    if not os.path.exists(STUDY_PLAN_DIR):
        return week_files
    
    for f in os.listdir(STUDY_PLAN_DIR):
        match = pattern.match(f)
        if match:
            week_num = int(match.group(1))
            week_files.append((week_num, f))
    
    week_files.sort(key=lambda x: x[0])
    return week_files

def generate_study_plan_index(dry_run=False):
    """生成 study-plan/index.md"""
    print("=" * 60)
    print("study-plan 板块总览 index.md 生成")
    print("=" * 60)
    print(f"路径: {STUDY_PLAN_DIR}")
    print(f"模式: {'DRY RUN' if dry_run else '实际运行'}")
    
    if not os.path.exists(STUDY_PLAN_DIR):
        print(f"错误：路径不存在 {STUDY_PLAN_DIR}")
        return
    
    week_files = scan_week_files()
    
    if not week_files:
        print("未找到任何 weekX.md 文件")
        return
    
    print(f"\n发现 {len(week_files)} 个周计划文件")
    for week_num, filename in week_files:
        print(f"   - week{week_num}.md")
    
    # 生成计划列表
    plan_items = []
    for week_num, filename in week_files:
        filepath = os.path.join(STUDY_PLAN_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        summary = get_week_summary(week_num, content)
        plan_items.append(f"- [第{week_num}周]({filename}) - {summary}")
    
    plan_list = "\n".join(plan_items)
    update_time = get_current_time()
    
    # 生成 Front Matter
    front_matter = f'''---
total_weeks: {len(week_files)}
last_updated: {update_time}
---
'''
    
    # 生成正文
    content = f'''# 📖 每周计划

> 每周的学习目标与安排。

## 📅 计划列表

{plan_list}

---

*最后更新：{update_time}*
'''
    
    full_content = front_matter + content
    
    if safe_write(OUTPUT_FILE, full_content, dry_run):
        print(f"\n✅ 已生成: {OUTPUT_FILE}")
        print(f"   总周数: {len(week_files)}")
    
    print("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="更新 study-plan/index.md")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不实际写入")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    generate_study_plan_index(dry_run)