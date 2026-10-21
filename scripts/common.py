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

def get_meta(metadata: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    读取元数据字段，并把 None / 空白字符串视为缺失。
    解决 YAML 中 `status:`、`title:` 这类“键存在但值为空”导致默认值失效的问题。
    """
    if not isinstance(metadata, dict):
        return default
    value = metadata.get(key, default)
    if value is None:
        return default
    if isinstance(value, str) and not value.strip():
        return default
    return value

def safe_int(value: Any, default: int = 0) -> int:
    """将值安全转换为 int（兼容 None、空字符串、浮点数）"""
    if value is None or value == '':
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default

def extract_heading(content: str, max_level: int = 2) -> str:
    """提取 Markdown 中第一/二级标题，作为无 Front Matter 笔记的标题"""
    match = re.search(r'^#{1,%d}\s+(.+?)\s*$' % max_level, content, re.MULTILINE)
    return match.group(1).strip() if match else ''

def get_note_title(metadata: Dict[str, Any], content: str, fallback: str) -> str:
    """获取笔记标题：Front Matter -> 一级/二级标题 -> 文件名"""
    title = get_meta(metadata, 'title', '')
    if title:
        return str(title).strip()
    heading = extract_heading(content)
    return heading or fallback

def list_note_files(dir_path: str) -> List[str]:
    """列出目录下直接包含的笔记文件（排除 index.md），按文件名排序"""
    if not os.path.isdir(dir_path):
        return []
    return sorted(
        f for f in os.listdir(dir_path)
        if f.endswith('.md') and f != 'index.md'
        and os.path.isfile(os.path.join(dir_path, f))
    )

def choose_primary_note(dir_path: str, note_files: List[str]) -> Optional[str]:
    """
    从同一目录的多篇笔记中确定主笔记。
    优先：有 title > 有明确状态 > *_wp.md > 文件名排序。
    保证结果不依赖文件系统遍历顺序。
    """
    if not note_files:
        return None

    def score(name: str):
        metadata = read_metadata(os.path.join(dir_path, name))
        has_title = 1 if get_meta(metadata, 'title') else 0
        has_status = 1 if normalize_status(get_meta(metadata, 'status', '')) != '未开始' else 0
        is_wp = 1 if name.endswith('_wp.md') else 0
        return (has_title, has_status, is_wp, name)

    return sorted(note_files, key=score, reverse=True)[0]

def build_other_notes_table(dir_path: str, note_files: List[str], primary: str) -> str:
    """为多笔记目录生成“同目录其他笔记”表格（无其他笔记时返回空字符串）"""
    others = [f for f in note_files if f != primary]
    if not others:
        return ''

    lines = [
        "### 📚 同目录其他笔记",
        "",
        "| 笔记 | 状态 |",
        "|------|:----:|",
    ]
    for name in others:
        metadata = read_metadata(os.path.join(dir_path, name))
        content = ''
        try:
            with open(os.path.join(dir_path, name), 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            pass
        title = get_note_title(metadata, content, name[:-3])
        status = normalize_status(get_meta(metadata, 'status', '未开始'))
        lines.append(f"| [{title}]({name}) | {get_status_emoji(status)} |")

    return "\n".join(lines)

def has_markdown(dir_path: str) -> bool:
    """判断目录（含子目录）中是否存在 Markdown 笔记"""
    if not os.path.isdir(dir_path):
        return False
    for root, dirs, files in os.walk(dir_path):
        if any(f.endswith('.md') for f in files):
            return True
    return False

def is_real_dir(dir_path: str) -> bool:
    """
    判断是否为可参与统计的目录：
    - 排除隐藏目录
    - 排除以 .md 结尾的异常目录（如 `xss&csrf-defense.md/`）
    - 排除“新建文件夹”占位目录
    - 目录内必须至少有一篇 Markdown
    """
    if not os.path.isdir(dir_path):
        return False
    name = os.path.basename(dir_path)
    if name.startswith('.') or name.lower().endswith('.md') or name.startswith('新建'):
        return False
    return has_markdown(dir_path)

# ==================== 状态工具 ====================

def get_status_map() -> Dict[str, str]:
    """获取状态映射（与 config.yaml 保持一致）"""
    config = load_config()
    return config.get('status_map', {
        '已完成': '✅',
        '进行中': '🔄',
        '未开始': '⬜'
    })

def normalize_status(value: Any) -> str:
    """将中文状态、emoji 或空值统一为三种标准中文状态"""
    if value in ('已完成', '完成', '✅'):
        return '已完成'
    if value in ('进行中', '分析中', '攻略中', '🔄'):
        return '进行中'
    return '未开始'

def get_status_emoji(status_cn: str) -> str:
    """根据中文状态或 emoji 获取表情符号"""
    if status_cn in ('✅', '🔄', '⬜', '♻️'):
        return status_cn
    status_map = get_status_map()
    return status_map.get(normalize_status(status_cn), '⬜')

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

def get_file_mtime(file_path: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """获取文件最后修改时间（用于笔记的 last_updated 字段）"""
    try:
        return datetime.fromtimestamp(os.path.getmtime(file_path)).strftime(format_str)
    except OSError:
        return ''

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
    递归收集模块目录下所有笔记的元数据（排除所有 index.md）。
    对缺失/为空的 title、description、status 做统一兜底。
    """
    notes_data = []
    if not os.path.isdir(module_dir):
        return notes_data

    for root, dirs, files in os.walk(module_dir):
        dirs.sort()
        md_files = sorted(f for f in files if f.endswith('.md') and f != 'index.md')

        for note_file in md_files:
            note_path = os.path.join(root, note_file)
            metadata = read_metadata(note_path)

            content = ''
            try:
                with open(note_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                pass

            title = get_note_title(metadata, content, note_file[:-3])
            description = get_meta(metadata, 'description', '')
            status_cn = normalize_status(get_meta(metadata, 'status', '未开始'))
            finish_date = get_meta(metadata, 'finish-date', '')

            rel_path = os.path.relpath(note_path, module_dir).replace('\\', '/')

            notes_data.append({
                'file': rel_path,
                'title': str(title),
                'description': str(description) if description is not None else '',
                'status_cn': status_cn,
                'finish_date': to_str(finish_date)
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
    'get_meta', 'safe_int', 'extract_heading', 'get_note_title',
    # 状态
    'normalize_status',
    # 进度
    'progress_bar', 'format_completion',
    # 时间
    'to_str', 'get_current_time', 'get_current_date', 'get_file_mtime',
    # 文件
    'need_update', 'safe_write', 'collect_md_files', 'get_subdirectories',
    'list_note_files', 'choose_primary_note', 'build_other_notes_table',
    'has_markdown', 'is_real_dir',
    # Practice
    'scan_practice_related', 'generate_practice_table',
    # 笔记
    'collect_notes_recursive', 'calculate_module_stats',
    # 命令行
    'add_common_arguments', 'setup_from_args',
]