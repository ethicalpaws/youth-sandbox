#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_character_data.py - 自动更新角色数据 character.json
从各模块的 index.md 读取统计数据，根据 config.yaml 配置计算能力值
"""

import os
import sys
import re
import json
import glob
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ==================== 配置 ====================
PROJECT_ROOT = r"E:\youth-sandbox\docs"
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CHARACTER_FILE = os.path.join(DATA_DIR, "character.json")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.yaml")

TECH_STUDY_PATH = os.path.join(PROJECT_ROOT, "tech-study")
KNOWLEDGE_PATH = os.path.join(TECH_STUDY_PATH, "knowledge")
PRACTICE_PATH = os.path.join(TECH_STUDY_PATH, "practice")
WEEKLY_PATH = os.path.join(TECH_STUDY_PATH, "weekly-check")
CODE_ATTACHMENT = os.path.join(TECH_STUDY_PATH, "code-attachment")

# ==================== 辅助函数 ====================

def load_config() -> Dict:
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}

def parse_front_matter(content: str) -> Dict:
    """解析 Front Matter，返回元数据字典"""
    if not content.startswith('---'):
        return {}
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}
    try:
        metadata = yaml.safe_load(parts[1])
        return metadata if isinstance(metadata, dict) else {}
    except:
        return {}

def read_index_metadata(index_path: str) -> Dict:
    """读取目录下的 index.md 的 Front Matter"""
    if not os.path.exists(index_path):
        return {}
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return parse_front_matter(content)

def scan_code_attachments() -> int:
    """扫描代码附件目录下的 .java, .js, .py 文件数量"""
    if not os.path.exists(CODE_ATTACHMENT):
        return 0
    count = 0
    for ext in ['*.java', '*.js', '*.py']:
        count += len(glob.glob(os.path.join(CODE_ATTACHMENT, '**', ext), recursive=True))
    return count

def scan_sources_folders() -> int:
    """扫描 code-attachment/sources 下的文件夹数量"""
    sources_path = os.path.join(CODE_ATTACHMENT, "sources")
    if not os.path.exists(sources_path):
        return 0
    return len([d for d in os.listdir(sources_path) 
                if os.path.isdir(os.path.join(sources_path, d)) 
                and not d.startswith('.')])

def scan_practice_related(keywords: List[str]) -> int:
    """扫描 practice 目录，统计匹配关键词的题目数量"""
    count = 0
    type_paths = {
        'ctf': os.path.join(PRACTICE_PATH, 'ctf'),
        'cve': os.path.join(PRACTICE_PATH, 'cve'),
        'lab': os.path.join(PRACTICE_PATH, 'lab')
    }
    
    keywords_lower = [kw.lower() for kw in keywords]
    
    for item_type, base_path in type_paths.items():
        if not os.path.exists(base_path):
            continue
        for index_file in glob.glob(os.path.join(base_path, '**', 'index.md'), recursive=True):
            metadata = read_index_metadata(index_file)
            tags = metadata.get('tags', [])
            if any(tag.lower() in keywords_lower for tag in tags):
                count += 1
    
    return count

def calculate_skill_value(base_value: float) -> float:
    """能力值衰减计算：超过 50 分后按阶梯比例衰减"""
    if base_value <= 50:
        return round(base_value, 1)
    
    result = 50.0
    remaining = base_value - 50
    
    tiers = [
        (10, 0.9),   # 51-60: 90%
        (10, 0.7),   # 61-70: 70%
        (10, 0.5),   # 71-80: 50%
        (10, 0.3),   # 81-90: 30%
        (float('inf'), 0.1)  # 91+: 10%
    ]
    
    for tier_limit, ratio in tiers:
        if remaining <= 0:
            break
        take = min(remaining, tier_limit)
        result += take * ratio
        remaining -= take
    
    return round(result, 1)

def calculate_level(total_exp: int) -> Tuple[int, int, int]:
    """计算等级、当前经验、下一级所需经验"""
    remaining = total_exp
    level = 1
    required = 200
    while remaining >= required:
        remaining -= required
        level += 1
        required = int(required * 1.2)
    return level, remaining, required

def get_skill_value(skill_config: Dict) -> float:
    """根据配置计算单个能力值"""
    try:
        source_type = skill_config.get('source_type', 'index')
        result = 0.0
        
        if source_type == 'code_attachments':
            if 'sources' in skill_config.get('source', ''):
                result = scan_sources_folders()
            else:
                result = scan_code_attachments()
            multiplier = skill_config.get('multiplier', 1)
            if multiplier != 1:
                result = result * multiplier
        
        elif source_type == 'practice_related':
            keywords = skill_config.get('keywords', [])
            result = scan_practice_related(keywords)
            multiplier = skill_config.get('multiplier', 1)
            if multiplier != 1:
                result = result * multiplier
        
        else:
            source_path = skill_config.get('source', '')
            full_path = os.path.join(PROJECT_ROOT, "tech-study", source_path)
            metadata = read_index_metadata(full_path)
            
            field = skill_config.get('field', 'completed')
            base_value = metadata.get(field, 0)
            if not isinstance(base_value, (int, float)):
                base_value = 0
            
            extra_field = skill_config.get('extra_field', '')
            extra_value = 0
            if extra_field:
                extra_value = metadata.get(extra_field, 0)
                if not isinstance(extra_value, (int, float)):
                    extra_value = 0
            
            extra_source = skill_config.get('extra_source', '')
            extra_source_value = 0
            if extra_source:
                extra_full_path = os.path.join(PROJECT_ROOT, "tech-study", extra_source)
                extra_metadata = read_index_metadata(extra_full_path)
                extra_source_field = skill_config.get('extra_field', 'completed')
                extra_source_value = extra_metadata.get(extra_source_field, 0)
                if not isinstance(extra_source_value, (int, float)):
                    extra_source_value = 0
            
            code_attachments = scan_code_attachments()
            practice_keywords = skill_config.get('practice_keywords', [])
            practice_related = scan_practice_related(practice_keywords) if practice_keywords else 0
            
            formula = skill_config.get('formula', '')
            
            if formula == 'value':
                result = base_value
            elif formula == 'value + code_attachments/30':
                result = base_value + code_attachments / 30
            elif formula == '(value + practice_related) * 3':
                result = (base_value + practice_related) * 3
            elif formula == 'completed*5 + in_progress*3':
                result = base_value * 5 + extra_value * 3
            elif formula == 'value*5 + extra*10':
                result = base_value * 5 + extra_source_value * 10
            else:
                result = base_value
            
            multiplier = skill_config.get('multiplier', 1)
            if multiplier != 1:
                result = result * multiplier
        
        max_value = skill_config.get('max', 100)
        if result > max_value:
            result = max_value
        
        return float(result)
    
    except Exception as e:
        print(f"  警告: 计算 {skill_config.get('source', 'unknown')} 失败 - {e}")
        return 0.0

def scan_skills_from_config(skills_config: Dict) -> Dict[str, float]:
    """根据配置文件扫描所有能力值"""
    skills = {}
    for skill_name, skill_config in skills_config.items():
        try:
            value = get_skill_value(skill_config)
            skills[skill_name] = value
        except Exception as e:
            print(f"  警告: 计算 {skill_name} 失败 - {e}")
            skills[skill_name] = 0
    return skills

# ==================== 经验值统计 ====================

def scan_notes_count() -> int:
    """
    统计所有笔记数量（knowledge + practice + weekly-check）
    排除各目录下的 index.md
    """
    count = 0
    
    # 1. 扫描 knowledge 目录
    if os.path.exists(KNOWLEDGE_PATH):
        for md_file in glob.glob(os.path.join(KNOWLEDGE_PATH, "**", "*.md"), recursive=True):
            if os.path.basename(md_file) != "index.md":
                count += 1
        print(f"   knowledge 笔记: {count}")
    
    # 2. 扫描 practice 目录（CTF、CVE、Lab、SRC 的 WriteUp）
    practice_start = count
    if os.path.exists(PRACTICE_PATH):
        for md_file in glob.glob(os.path.join(PRACTICE_PATH, "**", "*.md"), recursive=True):
            if os.path.basename(md_file) != "index.md":
                count += 1
        print(f"   practice 笔记: {count - practice_start}")
    
    # 3. 扫描 weekly-check 目录（周报）
    weekly_start = count
    if os.path.exists(WEEKLY_PATH):
        for md_file in glob.glob(os.path.join(WEEKLY_PATH, "**", "*.md"), recursive=True):
            if os.path.basename(md_file) != "index.md":
                count += 1
        print(f"   weekly 笔记: {count - weekly_start}")
    
    return count

def scan_ctf_xp() -> Tuple[int, int]:
    """统计 CTF 题目数量和经验值"""
    index_path = os.path.join(PRACTICE_PATH, "ctf", "index.md")
    metadata = read_index_metadata(index_path)
    total = metadata.get('total', 0)
    return total, total * 20

def scan_cve_xp() -> Tuple[int, int]:
    """统计 CVE 数量和经验值"""
    index_path = os.path.join(PRACTICE_PATH, "cve", "index.md")
    metadata = read_index_metadata(index_path)
    analyzed = metadata.get('analyzed', 0)
    return analyzed, analyzed * 40

def scan_src_xp(first_bug_awarded: bool) -> Tuple[int, int, bool, bool]:
    """统计 SRC 数量和经验值"""
    index_path = os.path.join(PRACTICE_PATH, "src", "index.md")
    metadata = read_index_metadata(index_path)
    count = metadata.get('completed_targets', 0)
    total_xp = count * 50
    trigger_first = False
    if count > 0 and not first_bug_awarded:
        total_xp += 100
        trigger_first = True
        first_bug_awarded = True
    return count, total_xp, first_bug_awarded, trigger_first

def scan_weekly_xp() -> Tuple[int, List[int]]:
    """统计周测经验值和得分列表"""
    if not os.path.exists(WEEKLY_PATH):
        return 0, []
    total_xp = 0
    scores = []
    for week_dir in sorted(glob.glob(os.path.join(WEEKLY_PATH, "week*"))):
        detection_path = os.path.join(week_dir, "detection.md")
        if not os.path.exists(detection_path):
            continue
        with open(detection_path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'id="totalScore">(\d+)</span>', content)
        if not match:
            match = re.search(r'得分[：:]\s*(\d+)(?:/100)?', content)
        if match:
            score = int(match.group(1))
            xp = round(20 * score / 100)
            total_xp += xp
            scores.append(score)
    return total_xp, scores

# ==================== 热力图数据 ====================

def scan_heatmap_data() -> Dict:
    """扫描所有笔记文件的修改时间，生成52周热力图数据"""
    heatmap = {}
    
    # 扫描所有目录的笔记文件
    all_paths = [KNOWLEDGE_PATH, PRACTICE_PATH, WEEKLY_PATH]
    for base_path in all_paths:
        if not os.path.exists(base_path):
            continue
        for md_file in glob.glob(os.path.join(base_path, "**", "*.md"), recursive=True):
            if os.path.basename(md_file) == "index.md":
                continue
            mtime = os.path.getmtime(md_file)
            date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
            heatmap[date] = heatmap.get(date, 0) + 1
    
    start_date = datetime(2026, 5, 9)
    weeks = []
    
    for week_offset in range(52):
        week_start = start_date + timedelta(days=week_offset * 7)
        week_total = 0
        daily_data = []
        for d in range(7):
            date = (week_start + timedelta(days=d)).strftime("%Y-%m-%d")
            count = heatmap.get(date, 0)
            week_total += count
            daily_data.append(count)
        
        weeks.append({
            "total": week_total,
            "max_daily": max(daily_data) if daily_data else 0,
            "days": daily_data
        })
    
    return {
        "weeks": weeks,
        "total_notes": sum(heatmap.values()),
        "active_days": len(heatmap),
        "max_contrib": max(heatmap.values()) if heatmap else 0
    }

# ==================== 主函数 ====================

def load_manual_data() -> Dict:
    """加载手动配置的角色数据"""
    default = {
        "name": "ethicalpaws",
        "avatar": "/youth-sandbox/asserts/images/avatar/avatar.png",
        "title": "安全学徒",
        "motto": "路漫漫其修远兮",
        "join_date": datetime.now().strftime("%Y-%m-%d"),
        "special_achievements": []
    }
    if os.path.exists(CHARACTER_FILE):
        try:
            with open(CHARACTER_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "manual" in data:
                    result = default.copy()
                    result.update(data["manual"])
                    return result
        except:
            pass
    return default

def main():
    print("=" * 60)
    print("[角色数据] 更新脚本")
    print("=" * 60)
    
    config = load_config()
    char_config = config.get('character', {})
    skills_config = char_config.get('skills', {})
    
    if not skills_config:
        print("错误：config.yaml 中缺少 character.skills 配置")
        return
    
    manual = load_manual_data()
    
    # 读取首洞奖励状态
    first_bug = False
    if os.path.exists(CHARACTER_FILE):
        try:
            with open(CHARACTER_FILE, 'r', encoding='utf-8') as f:
                old = json.load(f)
                first_bug = old.get("auto", {}).get("first_bug_awarded", False)
        except:
            pass
    
    print("\n[统计] 能力值...")
    
    # 从配置计算能力值
    raw_skills = scan_skills_from_config(skills_config)
    
    # 应用衰减计算最终能力值
    skills = {}
    for k, v in raw_skills.items():
        skills[k] = calculate_skill_value(v)
    
    print("\n[结果] 最终能力值:")
    for k, v in skills.items():
        print(f"   {k}: {v}")
    
    print("\n[统计] 经验值...")
    note_cnt = scan_notes_count()
    ctf_cnt, ctf_xp = scan_ctf_xp()
    cve_cnt, cve_xp = scan_cve_xp()
    src_cnt, src_xp, first_bug, trigger = scan_src_xp(first_bug)
    week_xp, week_scores = scan_weekly_xp()
    
    total_exp = note_cnt * 10 + ctf_xp + cve_xp + src_xp + week_xp
    level, cur_exp, next_exp = calculate_level(total_exp)
    
    print(f"   笔记: {note_cnt} (+{note_cnt*10})")
    print(f"   CTF: {ctf_cnt} (+{ctf_xp})")
    print(f"   CVE: {cve_cnt} (+{cve_xp})")
    print(f"   SRC: {src_cnt} (+{src_xp})")
    if trigger:
        print("   [首洞奖励] +100 XP")
    print(f"   周测: +{week_xp}")
    print(f"   总经验: {total_exp}")
    print(f"   等级: Lv.{level} ({cur_exp}/{next_exp})")
    
    print("\n[统计] 热力图数据...")
    heatmap = scan_heatmap_data()
    print(f"   总笔记数: {heatmap['total_notes']}")
    print(f"   活跃天数: {heatmap['active_days']}")
    
    auto = {
        "level": level,
        "current_exp": cur_exp,
        "next_exp": next_exp,
        "total_exp": total_exp,
        "stats": {
            "notes_count": note_cnt,
            "ctf_count": ctf_cnt,
            "cve_count": cve_cnt,
            "src_count": src_cnt,
            "weekly_scores": week_scores
        },
        "skills": skills,
        "heatmap": heatmap,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "first_bug_awarded": first_bug,
        "start_date": manual.get("join_date", "2026-05-09"),
    }
    
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CHARACTER_FILE, 'w', encoding='utf-8') as f:
        json.dump({"manual": manual, "auto": auto}, f, ensure_ascii=False, indent=2)
    
    print(f"\n[完成] 已保存: {CHARACTER_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()