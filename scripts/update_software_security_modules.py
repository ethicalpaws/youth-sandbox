#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
08-software-system-security 模块级 index.md 自动生成脚本

该章节为多层目录结构：
    08/
      basic/
      buffer-overflow/
        basic/ defense/ else-overflow/ heap/ stack/
      fuzzing/（空目录，暂不生成）

脚本自底向上为所有“包含 Markdown 笔记的目录”生成 index.md，
自动忽略仅存放图片的目录（如 heap/basic/、stack/pwn/）。
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from common import logger, get_knowledge_path, is_real_dir
from chapter_utils import write_module_index


CHAPTER_PATH = os.path.join(get_knowledge_path(), "08-software-system-security")

# 模块显示名称与描述
MODULE_META = {
    'basic': ('基础', '计算机存储空间原理、汇编指令、栈与寄存器基础实验'),
    'buffer-overflow': ('缓冲区溢出', '栈溢出、堆利用、格式化字符串、整数溢出与防御机制'),
    'stack': ('栈溢出', '栈溢出入门、ret2text、ret2shellcode、ret2libc、ROP'),
    'heap': ('堆利用', '堆基础、UAF、double-free、fastbin 攻击、unlink 攻击'),
    'defense': ('防御机制', 'ASLR、CFI 等二进制缓解与绕过思路'),
    'else-overflow': ('其他溢出', '格式化字符串溢出、整数溢出'),
    'fuzzing': ('模糊测试', 'Fuzzing 相关笔记（待补充）'),
}


def get_meta(module_name):
    return MODULE_META.get(module_name, (module_name, f'{module_name} 学习笔记'))


def get_module_title(module_name):
    return get_meta(module_name)[0]


def process_module_dir(dir_path, dry_run=False):
    """递归处理模块目录：先子模块，后当前目录"""
    module_name = os.path.basename(dir_path)
    display_name, description = get_meta(module_name)

    children = [
        name for name in sorted(os.listdir(dir_path))
        if is_real_dir(os.path.join(dir_path, name))
    ]

    for child in children:
        process_module_dir(os.path.join(dir_path, child), dry_run)

    # 当前目录自身没有笔记时，仍会生成“子模块汇总”页
    return write_module_index(
        dir_path,
        display_name=display_name,
        description=description,
        heading_level=1,
        child_display_name=get_module_title,
        dry_run=dry_run,
    )


def generate_software_security_modules(dry_run=False):
    logger.info("=" * 60)
    logger.info("08-software-system-security 模块级 index.md 生成")
    logger.info("=" * 60)
    logger.info(f"路径: {CHAPTER_PATH}")
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")

    if not os.path.isdir(CHAPTER_PATH):
        logger.error(f"路径不存在: {CHAPTER_PATH}")
        return

    modules = [
        name for name in sorted(os.listdir(CHAPTER_PATH))
        if is_real_dir(os.path.join(CHAPTER_PATH, name))
    ]

    if not modules:
        logger.warning("未找到任何包含笔记的模块目录")
        return

    # 提示被忽略的空目录 / 纯图片目录
    ignored = [
        name for name in sorted(os.listdir(CHAPTER_PATH))
        if os.path.isdir(os.path.join(CHAPTER_PATH, name))
        and not is_real_dir(os.path.join(CHAPTER_PATH, name))
    ]
    if ignored:
        logger.info(f"   忽略非笔记目录: {', '.join(ignored)}")

    logger.info(f"发现 {len(modules)} 个模块: {modules}")

    for module_name in modules:
        logger.info(f"  处理模块: {module_name}")
        process_module_dir(os.path.join(CHAPTER_PATH, module_name), dry_run)

    logger.info("=" * 60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()

    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    generate_software_security_modules(dry_run)
