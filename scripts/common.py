#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
common.py - 公共函数模块
所有脚本共享的基础函数

特性：
- 无依赖业务逻辑，仅提供工具函数
- 缺失时自动降级，不影响原有功能
- 支持 dry-run 和日志记录
"""

import os
import re
import yaml
import glob
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union

# ==================== 路径配置 ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.yaml")

# 项目根目录（可通过环境变量覆盖）
PROJECT_ROOT = os.environ.get("PROJECT_ROOT", r"E:\youth-sandbox\docs")

# ==================== 日志配置 ====================

# 全局日志器（默认只输出到控制台）
_logger = None

def get_logger():
    """获取日志记录器（延迟初始化）"""
    global _logger
    if _logger is None:
        _logger = logging.getLogger("docs-updater")
        _logger.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        _logger.addHandler(console_handler)
        
        # 文件处理器（可选）
        try:
            log_path = os.path.join(SCRIPT_DIR, "update.log")
            file_handler = logging.FileHandler(log_path, encoding='utf-8', mode='a')
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            _logger.addHandler(file_handler)
        except Exception:
            pass
    
    return _logger

logger = get_logger()

def set_log_level(level: Union[str, int]) -> None:
    """设置日志级别"""
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    logger.setLevel(level)

# ==================== 配置加载 ====================

_config_cache = None
_config_mtime = 0

def load_config(force_reload: bool = False) -> Dict[str, Any]:
    """加载配置文件（带缓存）"""
    global _config_cache, _config_mtime
    
    if not os.path.exists(CONFIG_FILE):
        logger.warning(f"配置文件不存在: {CONFIG_FILE}")
        return {}
    
    current_mtime = os.path.getmtime(CONFIG_FILE)
    
    if force_reload or _config_cache is None or current_mtime > _config_mtime:
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                _config_cache = yaml.safe_load(f) or {}
            _config_mtime = current_mtime
        except yaml.YAMLError as e:
            logger.error(f"配置文件解析失败: {e}")
            _config_cache = {}
    
    return _config_cache

def get_config_section(section: str, default: dict = None) -> dict:
    """获取配置的某个章节"""
    config = load_config()
    return config.get(section, default or {})

# ==================== Front Matter 解析 ====================

def parse_front_matter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    解析 YAML Front Matter
    返回: (metadata, rest_content)
    
    与原脚本完全兼容
    """
    if not content.startswith('---'):
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    try:
        metadata = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        metadata = {}
    
    return metadata, parts[2]

def read_metadata(file_path: str) -> Dict[str, Any]:
    """读取文件的 Front Matter 元数据"""
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        metadata, _ = parse_front_matter(content)
        return metadata
    except Exception:
        return {}

def read_index_metadata(dir_path: str) -> Dict[str, Any]:
    """读取目录下 index.md 的 Front Matter"""
    index_path = os.path.join(dir_path, 'index.md')
    return read_metadata(index_path)

# ==================== 状态工具 ====================

def get_status_map() -> Dict[str, str]:
    """获取状态映射（与 config.yaml 保持一致）"""
    config = load_config()
    return config.get('status_map', {
        '已完成': '✅',
        '进行中': '🔄',
        '未开始': '⬜'
    })

def get_status_emoji(status_cn: str) -> str:
    """根据中文状态获取表情符号"""
    status_map = get_status_map()
    return status_map.get(status_cn, '⬜')

def get_difficulty_config() -> Dict[str, Dict]:
    """获取难度配置"""
    config = load_config()
    return config.get('difficulty_config', {})

def get_annual_goal() -> Dict:
    """获取年度目标配置"""
    config = load_config()
    return config.get('annual_goal', {})

def get_src_achievements() -> Dict:
    """获取 SRC 成就配置"""
    config = load_config()
    return config.get('src_achievements', {})

def get_chapter_config(chapter_key: str) -> Dict:
    """获取章节配置"""
    config = load_config()
    return config.get(chapter_key, {})

# ==================== 进度条工具 ====================

def progress_bar(percentage: int, width: int = 10) -> str:
    """
    生成进度条字符串
    与原脚本格式完全一致：'█' * filled + '░' * (10-filled) + f' {percentage}%'
    """
    filled = int(percentage / (100 / width))
    return f"{'█' * filled}{'░' * (width - filled)} {percentage}%"

def format_completion(completed: int, total: int, width: int = 10) -> str:
    """格式化完成率"""
    if total == 0:
        return f"{'░' * width} 0%"
    rate = int(completed / total * 100)
    return progress_bar(rate, width)

# ==================== 时间工具 ====================

def to_str(value: Any) -> str:
    """
    将各种类型转换为字符串
    与原脚本的 to_str 函数完全一致
    """
    if value is None:
        return ''
    if hasattr(value, 'strftime'):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)

def get_current_time(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """获取当前时间字符串"""
    return datetime.now().strftime(format_str)

def get_current_date() -> str:
    """获取当前日期字符串"""
    return datetime.now().strftime("%Y-%m-%d")

# ==================== 文件操作工具 ====================

def need_update(output_path: str, source_paths: List[str]) -> bool:
    """
    检查是否需要更新（增量判断）
    如果输出文件不存在，或任一源文件比输出文件新，返回 True
    """
    if not os.path.exists(output_path):
        return True
    
    output_mtime = os.path.getmtime(output_path)
    
    for source_path in source_paths:
        if not os.path.exists(source_path):
            continue
        
        if os.path.isfile(source_path):
            if os.path.getmtime(source_path) > output_mtime:
                return True
        elif os.path.isdir(source_path):
            for root, dirs, files in os.walk(source_path):
                for f in files:
                    if f.endswith('.md'):
                        file_path = os.path.join(root, f)
                        try:
                            if os.path.getmtime(file_path) > output_mtime:
                                return True
                        except OSError:
                            pass
    
    return False

def safe_write(file_path: str, content: str, dry_run: bool = False, encoding: str = 'utf-8') -> bool:
    """安全写入文件（支持 dry run）"""
    if dry_run:
        logger.info(f"[DRY RUN] 将写入: {file_path}")
        return True
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"写入失败 {file_path}: {e}")
        return False

def collect_md_files(dir_path: str, recursive: bool = True, exclude_index: bool = True) -> List[str]:
    """收集目录下的所有 Markdown 文件"""
    if not os.path.exists(dir_path):
        return []
    
    if recursive:
        files = glob.glob(os.path.join(dir_path, '**', '*.md'), recursive=True)
    else:
        files = glob.glob(os.path.join(dir_path, '*.md'))
    
    if exclude_index:
        files = [f for f in files if not f.endswith('index.md')]
    
    return files

def get_subdirectories(dir_path: str) -> List[str]:
    """获取目录下的所有子目录"""
    if not os.path.exists(dir_path):
        return []
    
    return [d for d in os.listdir(dir_path)
            if os.path.isdir(os.path.join(dir_path, d))
            and not d.startswith('.')]

# ==================== Practice 关联工具 ====================

def scan_practice_related(practice_root: str, keywords: List[str]) -> Dict[str, List[Dict]]:
    """
    扫描 practice 目录，匹配关键词的题目
    返回格式与原脚本兼容
    """
    result = {'ctf': [], 'lab': [], 'cve': []}
    
    type_paths = {
        'ctf': os.path.join(practice_root, 'ctf'),
        'lab': os.path.join(practice_root, 'lab'),
        'cve': os.path.join(practice_root, 'cve')
    }
    
    keywords_lower = [kw.lower() for kw in keywords]
    
    for item_type, base_path in type_paths.items():
        if not os.path.exists(base_path):
            continue
        
        for index_file in glob.glob(os.path.join(base_path, '**', 'index.md'), recursive=True):
            metadata = read_metadata(index_file)
            tags = metadata.get('tags', [])
            
            if any(tag.lower() in keywords_lower for tag in tags):
                title = metadata.get('title', os.path.basename(os.path.dirname(index_file)))
                description = metadata.get('description', '')
                rel_path = os.path.relpath(os.path.dirname(index_file), practice_root)
                
                result[item_type].append({
                    'title': title,
                    'description': description,
                    'path': rel_path
                })
    
    return result

def generate_practice_table(items: List[Dict], table_type: str) -> Tuple[str, int]:
    """
    生成 CTF/Lab/CVE 表格
    返回 (表格内容, 数量)
    格式与原脚本完全一致
    """
    count = len(items)
    if not items:
        return "暂无", 0
    
    if table_type == 'cve':
        lines = ["| CVE编号 | 描述 |", "|---------|------|"]
        for item in items:
            link = f"../../../practice/{item['path']}"
            title_link = f"[{item['title']}]({link})"
            lines.append(f"| {title_link} | {item['description']} |")
    else:
        lines = ["| 题目 | 来源 | 描述 |", "|------|------|------|"]
        for item in items:
            link = f"../../../practice/{item['path']}"
            title_link = f"[{item['title']}]({link})"
            path_parts = item['path'].split(os.sep)
            source = path_parts[0] if path_parts else "未知"
            lines.append(f"| {title_link} | {source} | {item['description']} |")
    
    return "\n".join(lines), count

# ==================== 笔记收集工具 ====================

def collect_notes_recursive(module_dir: str) -> List[Dict]:
    """
    递归收集模块目录下所有笔记的元数据
    返回格式与原脚本兼容
    """
    notes_data = []
    
    for root, dirs, files in os.walk(module_dir):
        if root == module_dir:
            md_files = [f for f in files if f.endswith('.md') and f != 'index.md']
        else:
            md_files = [f for f in files if f.endswith('.md')]
        
        for note_file in md_files:
            note_path = os.path.join(root, note_file)
            metadata = read_metadata(note_path)
            
            title = metadata.get('title', note_file.replace('.md', ''))
            description = metadata.get('description', '')
            status_cn = metadata.get('status', '未开始')
            finish_date = metadata.get('finish-date', '')
            
            rel_path = os.path.relpath(note_path, module_dir)
            
            notes_data.append({
                'file': rel_path,
                'title': title,
                'description': description,
                'status_cn': status_cn,
                'finish_date': finish_date
            })
    
    return notes_data

def calculate_module_stats(notes_data: List[Dict]) -> Dict:
    """
    计算模块统计数据
    返回与原脚本兼容的统计字典
    """
    total = len(notes_data)
    completed = sum(1 for n in notes_data if n['status_cn'] == '已完成')
    in_progress = sum(1 for n in notes_data if n['status_cn'] == '进行中')
    not_started = sum(1 for n in notes_data if n['status_cn'] == '未开始')
    completion_rate = int(completed / total * 100) if total > 0 else 0
    
    if completed == total:
        module_status = "♻️"
    elif completed > 0 or in_progress > 0:
        module_status = "🔄"
    else:
        module_status = "⬜"
    
    return {
        'total_notes': total,
        'completed': completed,
        'in_progress': in_progress,
        'not_started': not_started,
        'completion_rate': completion_rate,
        'module_status': module_status
    }

# ==================== 命令行参数 ====================

def add_common_arguments(parser):
    """添加公共命令行参数"""
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不实际写入文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--quiet", "-q", action="store_true", help="安静模式")
    return parser

def setup_from_args(args) -> bool:
    """根据命令行参数设置环境，返回 dry_run 值"""
    if hasattr(args, 'verbose') and args.verbose:
        set_log_level(logging.DEBUG)
    if hasattr(args, 'quiet') and args.quiet:
        set_log_level(logging.WARNING)
    
    dry_run = (hasattr(args, 'dry_run') and args.dry_run) or os.environ.get("DRY_RUN", "0") == "1"
    return dry_run

# ==================== 路径工具 ====================

def get_knowledge_path() -> str:
    """获取 knowledge 目录路径"""
    return os.path.join(PROJECT_ROOT, "tech-study", "knowledge")

def get_practice_path() -> str:
    """获取 practice 目录路径"""
    return os.path.join(PROJECT_ROOT, "tech-study", "practice")

def get_weekly_check_path() -> str:
    """获取 weekly-check 目录路径"""
    return os.path.join(PROJECT_ROOT, "tech-study", "weekly-check")

def get_data_path() -> str:
    """获取 data 目录路径"""
    return os.path.join(PROJECT_ROOT, "data")

# ==================== 导出列表 ====================

__all__ = [
    # 路径
    'PROJECT_ROOT', 'CONFIG_FILE',
    'get_knowledge_path', 'get_practice_path', 'get_weekly_check_path', 'get_data_path',
    # 日志
    'logger', 'set_log_level',
    # 配置
    'load_config', 'get_config_section',
    'get_status_map', 'get_status_emoji', 'get_difficulty_config',
    'get_annual_goal', 'get_src_achievements', 'get_chapter_config',
    # Front Matter
    'parse_front_matter', 'read_metadata', 'read_index_metadata',
    # 进度
    'progress_bar', 'format_completion',
    # 时间
    'to_str', 'get_current_time', 'get_current_date',
    # 文件
    'need_update', 'safe_write', 'collect_md_files', 'get_subdirectories',
    # Practice
    'scan_practice_related', 'generate_practice_table',
    # 笔记
    'collect_notes_recursive', 'calculate_module_stats',
    # 命令行
    'add_common_arguments', 'setup_from_args',
]