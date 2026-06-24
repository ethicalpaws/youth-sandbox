#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_all.py - 一键运行所有更新脚本

用法:
    python run_all.py                    # 运行所有脚本
    python run_all.py --dry-run          # 模拟运行
    python run_all.py --category practice # 只运行 practice 板块
    python run_all.py --category knowledge # 只运行 knowledge 板块
    python run_all.py --script update_ctf_notes.py  # 只运行单个脚本
    python run_all.py --skip-errors      # 遇到错误继续执行
    python run_all.py --list             # 列出所有可用脚本
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# 导入公共模块
try:
    from common import logger, set_log_level, get_current_time
    HAS_COMMON = True
except ImportError:
    HAS_COMMON = False
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    def get_current_time():
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==================== 脚本分类 ====================

SCRIPT_CATEGORIES: Dict[str, List[str]] = {
    "practice": [
        # 题目级
        "update_ctf_notes.py",
        "update_cve_notes.py",
        "update_lab_notes.py",
        "update_src_notes.py",
        # 模块级
        "update_ctf_modules.py",
        "update_lab_modules.py",
        "update_src_modules.py",
        # 章节级
        "update_ctf_chapter.py",
        "update_cve_chapter.py",
        "update_lab_chapter.py",
        "update_src_chapter.py",
        # 总览
        "update_practice_index.py",
    ],
    "knowledge": [
        "update_foundation_chapter.py",
        "update_network_chapter.py",
        "update_web_chapter.py",
        "update_java_chapter.py",
        "update_java_deserialization.py",
        "update_jndi_injection.py",
        "update_memory_shell.py",
        "update_framework_vulns.py",
        "update_redblue_module.py",
        "update_redblue_chapter.py",
        "update_knowledge_index.py",
    ],
    "java": [
        "update_java_chapter.py",
        "update_java_deserialization.py",
        "update_jndi_injection.py",
        "update_memory_shell.py",
        "update_framework_vulns.py",
    ],
    "weekly": [
        "update_weekly_all.py",
    ],
    "study": [
        "update_study_plan_index.py",
    ],
    "character": [
        "update_character_data.py",
    ],
    "web": ["update_web_chapter.py"],
    "network": ["update_network_chapter.py"],
    "foundation": ["update_foundation_chapter.py"],
    "redblue": ["update_redblue_module.py", "update_redblue_chapter.py"],
    "cve": ["update_cve_notes.py", "update_cve_chapter.py"],
    "ctf": ["update_ctf_notes.py", "update_ctf_modules.py", "update_ctf_chapter.py"],
    "lab": ["update_lab_notes.py", "update_lab_modules.py", "update_lab_chapter.py"],
    "src": ["update_src_notes.py", "update_src_modules.py", "update_src_chapter.py"],
    "tech": [
        "update_tech_study_index.py",
    ],
}

# 执行顺序（依赖关系）
EXECUTION_ORDER: List[str] = [
    # 1. Practice 题目级（先生成各笔记的 index.md）
    "update_ctf_notes.py",
    "update_cve_notes.py",
    "update_lab_notes.py",
    "update_src_notes.py",
    
    # 2. Knowledge 模块级
    "update_foundation_chapter.py",
    "update_network_chapter.py",
    "update_web_chapter.py",
    "update_java_deserialization.py",
    "update_jndi_injection.py",
    "update_memory_shell.py",
    "update_framework_vulns.py",
    "update_redblue_module.py",
    "update_java_chapter.py",
    "update_redblue_chapter.py",
    
    # 3. Practice 模块级
    "update_ctf_modules.py",
    "update_lab_modules.py",
    "update_src_modules.py",
    
    # 4. Practice 章节级
    "update_ctf_chapter.py",
    "update_cve_chapter.py",
    "update_lab_chapter.py",
    "update_src_chapter.py",
    
    # 5. 总览和角色
    "update_practice_index.py",
    "update_knowledge_index.py",
    "update_tech_study_index.py",
    "update_character_data.py",
    
    # 6. 周报和学习计划
    "update_weekly_all.py",
    "update_study_plan_index.py",
]

def get_all_scripts() -> List[str]:
    """获取所有可用的脚本文件"""
    all_scripts = set()
    for scripts in SCRIPT_CATEGORIES.values():
        all_scripts.update(scripts)
    
    existing = []
    for script in sorted(all_scripts):
        if os.path.exists(os.path.join(SCRIPT_DIR, script)):
            existing.append(script)
    return existing

def list_scripts() -> None:
    """列出所有可用脚本"""
    print("\n" + "=" * 60)
    print("可用脚本列表")
    print("=" * 60)
    
    for category, scripts in SCRIPT_CATEGORIES.items():
        print(f"\n[{category.upper()}]")
        for script in scripts:
            exists = "YES" if os.path.exists(os.path.join(SCRIPT_DIR, script)) else "NO"
            print(f"  [{exists}] {script}")
    
    print("\n" + "=" * 60)
    print(f"总计: {len(get_all_scripts())} 个脚本可用")
    print("=" * 60)

def run_script(script_name: str, dry_run: bool = False, skip_errors: bool = False) -> bool:
    """运行单个脚本"""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    
    if not os.path.exists(script_path):
        logger.error(f"脚本不存在: {script_path}")
        return False
    
    if dry_run:
        logger.info(f"[DRY RUN] 将运行: {script_name}")
        return True
    
    logger.info(f"开始运行: {script_name}")
    
    try:
        env = os.environ.copy()
        if dry_run:
            env["DRY_RUN"] = "1"
        
        # 修复 Windows 编码问题
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            env=env,
            cwd=SCRIPT_DIR,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            logger.error(f"脚本执行失败: {script_name} (退出码: {result.returncode})")
            if result.stderr:
                # 过滤掉常见的编码警告
                stderr_lines = result.stderr.split('\n')
                for line in stderr_lines:
                    if 'UnicodeDecodeError' in line or 'gbk' in line.lower():
                        continue
                    if line.strip():
                        logger.error(f"错误输出: {line[:500]}")
            return False
        else:
            logger.info(f"完成: {script_name}")
            return True
        
    except Exception as e:
        logger.error(f"运行 {script_name} 时发生异常: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="统一文档更新脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_all.py                    # 运行所有脚本
  python run_all.py --dry-run          # 模拟运行
  python run_all.py -c practice        # 只运行 practice 板块
  python run_all.py -c knowledge       # 只运行 knowledge 板块
  python run_all.py -s update_ctf_notes.py  # 运行单个脚本
  python run_all.py --list             # 列出所有脚本
  python run_all.py --skip-errors      # 遇到错误继续执行
        """
    )
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不实际写入文件")
    parser.add_argument("--skip-errors", action="store_true", help="遇到错误继续执行")
    parser.add_argument("--category", "-c", choices=list(SCRIPT_CATEGORIES.keys()),
                        help="只运行指定板块")
    parser.add_argument("--script", "-s", help="只运行单个脚本")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有可用脚本")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    if args.verbose and HAS_COMMON:
        set_log_level("DEBUG")
    
    if args.list:
        list_scripts()
        return
    
    logger.info("=" * 60)
    logger.info(f"文档更新脚本启动 - {get_current_time()}")
    logger.info(f"模式: {'DRY RUN' if args.dry_run else '实际运行'}")
    logger.info("=" * 60)
    
    # 确定要运行的脚本
    scripts_to_run: List[str] = []
    
    if args.script:
        if not args.script.endswith('.py'):
            args.script += '.py'
        if os.path.exists(os.path.join(SCRIPT_DIR, args.script)):
            scripts_to_run = [args.script]
        else:
            logger.error(f"脚本不存在: {args.script}")
            sys.exit(1)
            
    elif args.category:
        scripts_to_run = [s for s in SCRIPT_CATEGORIES.get(args.category, [])
                         if os.path.exists(os.path.join(SCRIPT_DIR, s))]
        if not scripts_to_run:
            logger.error(f"板块 '{args.category}' 中没有可用脚本")
            sys.exit(1)
    else:
        # 按依赖顺序运行所有脚本
        scripts_to_run = [s for s in EXECUTION_ORDER
                         if os.path.exists(os.path.join(SCRIPT_DIR, s))]
    
    if not scripts_to_run:
        logger.error("未找到要运行的脚本")
        sys.exit(1)
    
    logger.info(f"将运行 {len(scripts_to_run)} 个脚本")
    
    success_count = 0
    fail_count = 0
    
    for i, script in enumerate(scripts_to_run, 1):
        logger.info(f"\n[{i}/{len(scripts_to_run)}] 执行: {script}")
        
        if run_script(script, args.dry_run, args.skip_errors):
            success_count += 1
        else:
            fail_count += 1
            if not args.skip_errors:
                logger.error("因错误停止执行")
                break
    
    logger.info("=" * 60)
    logger.info(f"执行完成 - 成功: {success_count}, 失败: {fail_count}")
    
    if fail_count > 0:
        sys.exit(1)
    else:
        logger.info("所有脚本执行成功！")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()