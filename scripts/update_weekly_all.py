#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_weekly_all.py - 每周检测完整更新脚本

功能：
1. 从 life/study-plan/weekX.md 的 Front Matter 提取时间范围
2. 检测 detection.md 是否有得分
3. 生成/更新每周的 index.md (week*/index.md)
4. 自动添加上一周/下一周导航链接
5. 生成/更新章节级 index.md (weekly-check/index.md)
6. 支持增量更新和 dry-run 模式

用法：
    python update_weekly_all.py              # 完整更新
    python update_weekly_all.py --dry-run    # 模拟运行
    python update_weekly_all.py --week 5     # 只更新第5周 + 章节级
    python update_weekly_all.py --no-chapter # 只更新周目录，不更新章节级
"""

import re
import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# 导入公共模块
try:
    from common import (
        logger, load_config, read_metadata, get_current_time,
        safe_write, need_update
    )
    HAS_COMMON = True
except ImportError:
    HAS_COMMON = False
    import logging
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
    
    def need_update(output_path, source_paths):
        if not os.path.exists(output_path):
            return True
        output_mtime = os.path.getmtime(output_path)
        for src in source_paths:
            if os.path.exists(src) and os.path.getmtime(src) > output_mtime:
                return True
        return False

# ==================== 配置 ====================

def get_docs_root() -> Path:
    """获取文档根目录"""
    if HAS_COMMON:
        config = load_config()
        if 'paths' in config and 'project_root' in config['paths']:
            return Path(config['paths']['project_root'])
    return Path(r"E:\youth-sandbox\docs")

def get_weekly_check_dir() -> Path:
    """获取 weekly-check 目录"""
    return get_docs_root() / "tech-study" / "weekly-check"

def get_study_plan_dir() -> Path:
    """获取 study-plan 目录"""
    return get_docs_root() / "life" / "study-plan"

def extract_week_number(week_dir: Path) -> int:
    """从 weekX 目录名提取周数，支持 week1, week2, week10 等"""
    match = re.search(r'week(\d+)', week_dir.name)
    return int(match.group(1)) if match else 0

def check_week_exists(week_num: int) -> bool:
    """检查周目录是否存在"""
    week_dir = get_weekly_check_dir() / f"week{week_num}"
    return week_dir.exists() and week_dir.is_dir()

# ==================== 时间解析函数（从 Front Matter 提取） ====================

def parse_date_from_study_plan(week_num: int) -> Optional[str]:
    """从 life/study-plan/weekX.md 的 Front Matter 提取时间范围"""
    study_plan_path = get_study_plan_dir() / f"week{week_num}.md"
    
    if not study_plan_path.exists():
        logger.debug(f"文件不存在: {study_plan_path}")
        return None
    
    try:
        content = study_plan_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.warning(f"读取失败 {study_plan_path}: {e}")
        return None
    
    # 检查是否有 Front Matter
    if not content.startswith('---'):
        logger.warning(f"week{week_num}.md 缺少 Front Matter，请添加 --- 开头的元数据")
        return None
    
    # 解析 Front Matter
    parts = content.split('---', 2)
    if len(parts) < 3:
        logger.warning(f"week{week_num}.md Front Matter 格式错误")
        return None
    
    try:
        metadata = yaml.safe_load(parts[1])
    except Exception as e:
        logger.warning(f"week{week_num}.md YAML 解析失败: {e}")
        return None
    
    start_date = metadata.get('start_date')
    end_date = metadata.get('end_date')
    
    # 如果是整数（被 YAML 计算了），说明没加引号，从原文提取
    if isinstance(start_date, int):
        logger.warning(f"start_date 被解析为整数 {start_date}，请用引号包裹日期")
        match = re.search(r'start_date:\s*"?(\d{4}-\d{2}-\d{2})"?', parts[1])
        if match:
            start_date = match.group(1)
        match = re.search(r'end_date:\s*"?(\d{4}-\d{2}-\d{2})"?', parts[1])
        if match:
            end_date = match.group(1)
    
    if start_date and end_date:
        start_date = str(start_date)
        end_date = str(end_date)
        
        # 提取年月日
        start_parts = start_date.split('-')
        end_parts = end_date.split('-')
        
        # 格式：2026.05.09-05.15
        start_short = f"{start_parts[0]}.{start_parts[1]}.{start_parts[2]}"
        end_short = f"{end_parts[1]}.{end_parts[2]}"
        result = f"{start_short}-{end_short}"
        logger.debug(f"解析成功: week{week_num} -> {result}")
        return result
    
    logger.warning(f"week{week_num}.md 缺少 start_date 或 end_date 字段")
    return None

# ==================== 得分解析函数 ====================

def extract_score_from_detection(detection_path: Path) -> Tuple[int, bool]:
    """从 detection.md 提取得分，返回 (score, has_score)"""
    if not detection_path.exists():
        return 0, False
    
    try:
        content = detection_path.read_text(encoding='utf-8')
    except Exception:
        return 0, False
    
    # 匹配 <span id="totalScore">87</span>
    match = re.search(r'<span\s+id="totalScore">\s*(\d+)\s*</span>', content)
    if match:
        return int(match.group(1)), True
    
    # 匹配 得分：93 或 总分：85
    match = re.search(r'(?:得分|总分)[：:]\s*(\d+)(?:/100)?', content)
    if match:
        return int(match.group(1)), True
    
    return 0, False

def extract_core_and_practice(detection_path: Path) -> Tuple[str, str]:
    """从 detection.md 提取本周核心和本周实践"""
    if not detection_path.exists():
        return "", ""
    
    try:
        content = detection_path.read_text(encoding='utf-8')
    except Exception:
        return "", ""
    
    core = ""
    practice = ""
    
    match = re.search(r'>\s*\*\*本周核心\*\*[：:]\s*([^\n]+)', content)
    if match:
        core = match.group(1).strip()
    
    match = re.search(r'>\s*\*\*本周实践\*\*[：:]\s*([^\n]+)', content)
    if match:
        practice = match.group(1).strip()
    
    return core, practice

# ==================== 生成周目录 index.md ====================

def get_status_text(score: int) -> str:
    """根据得分返回状态文字"""
    if score >= 90:
        return "优秀"
    elif score >= 75:
        return "良好"
    elif score >= 60:
        return "及格"
    elif score > 0:
        return "待改进"
    else:
        return "进行中"

def generate_week_index(week_num: int, date_range: Optional[str], has_score: bool, score: int = 0) -> str:
    """生成单周 index.md 内容"""
    
    if has_score:
        study_status = "✅ 已完成"
        test_status = f"✅ 已完成 ({score}/100)"
    else:
        study_status = "🔄 进行中"
        test_status = "⬜ 未开始"
    
    # 导航链接
    prev_link = ""
    next_link = ""
    
    if week_num > 1 and check_week_exists(week_num - 1):
        prev_link = f"- **上一周** [第{week_num-1}周](../week{week_num-1}/)\n"
    
    if check_week_exists(week_num + 1):
        next_link = f"- **下一周** [第{week_num+1}周](../week{week_num+1}/)\n"
    
    date_line = f"> 时间：{date_range}\n" if date_range else ""
    exp = round(20 * score / 100) if has_score and score > 0 else 0
    status_text = get_status_text(score)
    
    # 状态表情
    if has_score:
        status_icon = "✅"
    else:
        status_icon = "🔄"
    
    front_matter = f"""---
week: {week_num}
display_name: 第{week_num}周
time_range: {date_range or "待定"}
score: {score if has_score else 0}
exp: {exp}
status: {status_icon}
last_updated: {get_current_time()}
---
"""
    
    content = f"""# 第{week_num}周

{date_line}> 第{week_num}周学习内容与成果自测

## 📊 学习进度

| 项目 | 状态 |
|------|:----:|
| 学习内容 | {study_status} |
| 自测完成 | {test_status} |
| 获得经验 | +{exp} XP |

## 📂 导航

- [📝 自检测试](detection.md) - 本周知识点自测（含答案）

## 📌 快速导航

{prev_link}- **返回** [每周检测总览](../index.md)
{next_link}

---

*自动更新：{get_current_time()}*
"""
    
    return front_matter + content

def update_week_index(week_data: Dict, dry_run: bool = False) -> bool:
    """更新单个周的 index.md"""
    week_num = week_data["week_num"]
    week_dir = week_data["week_dir"]
    index_path = week_dir / "index.md"
    
    source_paths = [
        str(week_dir / "detection.md"),
        str(get_study_plan_dir() / f"week{week_num}.md"),
    ]
    
    if not need_update(str(index_path), source_paths):
        logger.debug(f"  跳过（未更新）: week{week_num}/index.md")
        return True
    
    logger.info(f"  更新: week{week_num}/index.md")
    if week_data.get("date_range"):
        logger.info(f"      时间范围: {week_data['date_range']}")
    
    content = generate_week_index(
        week_num=week_num,
        date_range=week_data.get("date_range"),
        has_score=week_data.get("has_score", False),
        score=week_data.get("score", 0)
    )
    
    return safe_write(str(index_path), content, dry_run)

# ==================== 生成章节级 index.md ====================

def get_chapter_status_icon(score: int) -> str:
    """根据得分返回章节级状态图标"""
    if score >= 90:
        return "✅"
    elif score >= 75:
        return "🔄"
    elif score >= 60:
        return "⚠️"
    elif score > 0:
        return "🔴"
    else:
        return "🔄"

def get_chapter_status_text(score: int) -> str:
    """根据得分返回章节级状态文字"""
    if score >= 90:
        return "优秀"
    elif score >= 75:
        return "良好"
    elif score >= 60:
        return "及格"
    elif score > 0:
        return "待改进"
    else:
        return "进行中"

def scan_weeks_for_chapter() -> List[Dict]:
    """扫描所有周目录，提取章节级需要的数据"""
    weekly_check_dir = get_weekly_check_dir()
    weeks_data = []
    
    if not weekly_check_dir.exists():
        return weeks_data
    
    for week_dir in sorted(weekly_check_dir.glob("week*")):
        if not week_dir.is_dir():
            continue
        
        week_num = extract_week_number(week_dir)
        if week_num == 0:
            continue
        
        detection_path = week_dir / "detection.md"
        score, has_score = extract_score_from_detection(detection_path)
        date_range = parse_date_from_study_plan(week_num)
        
        if not date_range:
            date_range = "日期待定"
        
        exp = round(20 * score / 100) if has_score else 0
        status_icon = get_chapter_status_icon(score)
        status_text = get_chapter_status_text(score)
        core, practice = extract_core_and_practice(detection_path)
        
        weeks_data.append({
            "num": week_num,
            "week_num": f"week{week_num}",
            "display_name": f"第{week_num}周",
            "time_range": date_range,
            "score": score,
            "exp": exp,
            "status_icon": status_icon,
            "status_text": status_text,
            "core": core,
            "practice": practice
        })
    
    weeks_data.sort(key=lambda x: x["num"])
    return weeks_data

def get_chapter_fixed_header() -> str:
    """章节级文件开头的固定内容"""
    return '''# 📋 每周检测

> 每周学习成果自测与复盘

这里记录我每周的学习检测和收获总结，用于：

- ✅ **自我检验**：通过检测题评估本周知识掌握程度
- 📝 **复盘总结**：记录本周的学习成果、卡点与突破
- 🔄 **持续改进**：根据检测结果调整下周学习计划

---

> 自动汇总各周学习成果与自测得分

## 📊 周次概览

| 周次 | 时间 | 得分 | 经验值 | 状态 | 详细 |
|:----:|------|:----:|:------:|:----:|:----:|'''

def get_chapter_fixed_footer() -> str:
    """章节级文件末尾的固定内容"""
    return '''


<div id="weekly-tip" style="background: #0f172a; padding: 1rem 1.25rem; border-radius: 8px; border-left: 5px solid #10b981; margin: 1rem 0; font-family: 'Courier New', monospace;">
<span style="color: #15cb04;">$></span>
<span id="tip-text" style="color: #15cb04; margin-left: 0.5rem;">加载中...</span>
<span style="color: #00ff41; animation: blink 1s infinite;">_</span>
</div>

<style>
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style>

<script>
const tips = [
  "每周一测，见证成长 📈",
  "得分越高，经验值越多 ⭐",
  "持续学习，持续进步 💪",
  "每一次检测都是自我突破 🎯",
  "知识复利，时间看得见 ⏰"
];

function getWeeklyTip() {
  const date = new Date();
  const weekNum = Math.ceil(date.getDate() / 7);
  const tipIndex = weekNum % tips.length;
  return tips[tipIndex];
}

document.addEventListener('DOMContentLoaded', function() {
  const tipElement = document.getElementById('tip-text');
  if (tipElement) {
    tipElement.textContent = getWeeklyTip();
  }
});
</script>'''

def update_chapter_index(dry_run: bool = False) -> bool:
    """更新章节级 index.md (weekly-check/index.md)"""
    logger.info("=" * 60)
    logger.info("更新章节级 index.md (weekly-check/index.md)")
    logger.info("=" * 60)
    
    weekly_check_dir = get_weekly_check_dir()
    
    if not weekly_check_dir.exists():
        logger.error(f"路径不存在: {weekly_check_dir}")
        return False
    
    weeks_data = scan_weeks_for_chapter()
    
    if not weeks_data:
        logger.warning("未找到任何周报目录")
        return False
    
    logger.info(f"发现 {len(weeks_data)} 个周报")
    
    # 生成表格行
    rows = []
    for w in weeks_data:
        rows.append(
            f"| {w['display_name']} | {w['time_range']} | {w['score']}/100 | {w['exp']} | {w['status_icon']} {w['status_text']} | [查看]({w['week_num']}/) |"
        )
    table_rows = "\n".join(rows)
    
    # 统计信息
    scores = [w["score"] for w in weeks_data if w["score"] > 0]
    if scores:
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        total_exp = sum(w["exp"] for w in weeks_data)
        completed = len(scores)
        
        max_week = ""
        for w in weeks_data:
            if w["score"] == max_score:
                max_week = w["display_name"]
                break
    else:
        avg_score = 0
        max_score = 0
        total_exp = 0
        completed = 0
        max_week = ""
    
    statistics_block = f"""
## 📈 统计信息

- **平均得分**：{avg_score:.1f}
- **最高分**：{max_week}（{max_score}分）
- **总经验值**：{total_exp}
- **已完成周数**：{completed}
"""
    
    content = f"{get_chapter_fixed_header()}\n{table_rows}\n{statistics_block}\n{get_chapter_fixed_footer()}"
    
    output_path = weekly_check_dir / 'index.md'
    
    if safe_write(str(output_path), content, dry_run):
        logger.info(f"✅ 已生成章节级 index.md")
        logger.info(f"   总周数: {len(weeks_data)}, 已完成: {completed}, 总经验: {total_exp}")
        return True
    
    return False

# ==================== 主函数 ====================

def scan_all_weeks() -> List[Dict]:
    """扫描所有周目录，返回数据列表"""
    weekly_check_dir = get_weekly_check_dir()
    weeks_data = []
    
    if not weekly_check_dir.exists():
        logger.error(f"目录不存在: {weekly_check_dir}")
        return weeks_data
    
    for week_dir in sorted(weekly_check_dir.glob("week*")):
        if not week_dir.is_dir():
            continue
        
        week_num = extract_week_number(week_dir)
        if week_num == 0:
            logger.warning(f"无法解析周数: {week_dir.name}")
            continue
        
        detection_path = week_dir / "detection.md"
        score, has_score = extract_score_from_detection(detection_path)
        date_range = parse_date_from_study_plan(week_num)
        
        weeks_data.append({
            "week_num": week_num,
            "week_dir": week_dir,
            "date_range": date_range,
            "score": score,
            "has_score": has_score,
        })
    
    weeks_data.sort(key=lambda x: x["week_num"])
    return weeks_data

def update_all_weeks(dry_run: bool = False) -> int:
    """更新所有周目录的 index.md，返回成功数量"""
    weeks_data = scan_all_weeks()
    
    if not weeks_data:
        logger.warning("未找到任何 week 目录")
        return 0
    
    logger.info(f"发现 {len(weeks_data)} 个周目录")
    
    success_count = 0
    for week_data in weeks_data:
        if update_week_index(week_data, dry_run):
            success_count += 1
    
    return success_count

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="每周检测完整更新脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python update_weekly_all.py              # 完整更新（周目录 + 章节级）
  python update_weekly_all.py --dry-run    # 模拟运行
  python update_weekly_all.py --week 5     # 只更新第5周 + 章节级
  python update_weekly_all.py --no-chapter # 只更新周目录，不更新章节级
        """
    )
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不实际写入")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--week", "-w", type=int, help="只更新指定周")
    parser.add_argument("--no-chapter", action="store_true", help="不更新章节级 index.md")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    
    logger.info("=" * 60)
    logger.info("每周检测完整更新脚本（使用 Front Matter）")
    logger.info(f"模式: {'DRY RUN' if dry_run else '实际运行'}")
    logger.info("=" * 60)
    
    # 1. 更新周目录
    if args.week:
        weeks_data = scan_all_weeks()
        target_weeks = [w for w in weeks_data if w["week_num"] == args.week]
        if not target_weeks:
            logger.error(f"未找到第 {args.week} 周目录")
            return
        
        logger.info(f"只更新第 {args.week} 周")
        success_count = 0
        for week_data in target_weeks:
            if update_week_index(week_data, dry_run):
                success_count += 1
        logger.info(f"周目录更新完成: {success_count}/{len(target_weeks)}")
    else:
        success_count = update_all_weeks(dry_run)
        logger.info(f"周目录更新完成: {success_count} 个")
    
    # 2. 更新章节级 index.md
    if not args.no_chapter:
        logger.info("")
        update_chapter_index(dry_run)
    else:
        logger.info("跳过章节级 index.md 更新")
    
    logger.info("=" * 60)
    logger.info("全部完成！")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()