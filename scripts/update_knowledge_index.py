#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_knowledge_index.py - 更新 knowledge/index.md
生成知识笔记总览页面
"""

import os
import sys
import io
import logging

# 修复 Windows 控制台编码，支持 emoji
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# 尝试导入公共模块
try:
    from common import (
        logger, get_current_time, safe_write, get_knowledge_path,
        read_index_metadata
    )
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
if HAS_COMMON:
    KNOWLEDGE_PATH = get_knowledge_path()
else:
    PROJECT_ROOT = r"E:\youth-sandbox\docs"
    KNOWLEDGE_PATH = os.path.join(PROJECT_ROOT, "tech-study", "knowledge")

# 已知章节的展示信息；未登记的 NN-* 目录会自动发现并使用默认展示
CHAPTER_META = {
    '01-foundation': ('🔰', '基础知识', '编程语言、操作系统基础、WAF绕过'),
    '02-network-protocol-security': ('🌐', '网络协议安全', 'ARP欺骗、ICMP攻击、TCP攻击、防火墙、VPN隧道'),
    '03-web-basics': ('🎯', 'Web基础漏洞', 'XSS、CSRF、SQL注入、SSRF、XXE、命令注入、文件上传、越权、信息泄露'),
    '04-web-advanced': ('⚡', 'Web高级漏洞', 'SSTI、原型链污染、API安全'),
    '05-java-security': ('☕', 'Java安全', 'Java反序列化、JNDI注入、内存马、框架漏洞'),
    '06-red-blue-confrontation': ('🔴🟦', '红蓝对抗', '权限提升、C2框架、免杀绕过、HVV、内网渗透、权限维持'),
    '07-server-side-component-security': ('🧩', '服务端组件安全', 'Apache、Nginx、Tomcat、PHP、Node.js、Java Web 等组件安全'),
    '08-software-system-security': ('💥', '软件系统安全', '缓冲区溢出、栈/堆利用、防御机制、Fuzzing'),
}

def count_markdown_notes(dir_path: str) -> int:
    """统计目录下实际笔记数（排除任意层级的 index.md）"""
    count = 0
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if f.endswith('.md') and f != 'index.md':
                count += 1
    return count

def scan_knowledge_notes_count() -> int:
    """
    扫描 knowledge 目录下的实际笔记数量（排除 index.md）
    这个数字是纯粹的知识笔记数
    """
    return count_markdown_notes(KNOWLEDGE_PATH)

def discover_chapters() -> list:
    """发现 knowledge 下所有 NN-* 章节目录，返回展示信息列表"""
    chapters = []
    if not os.path.isdir(KNOWLEDGE_PATH):
        return chapters

    for name in sorted(os.listdir(KNOWLEDGE_PATH)):
        path = os.path.join(KNOWLEDGE_PATH, name)
        if not os.path.isdir(path) or name.startswith('.'):
            continue
        if not (len(name) >= 2 and name[:2].isdigit()):
            continue

        note_count = count_markdown_notes(path)
        icon, title, description = CHAPTER_META.get(
            name,
            ('📁', name, f'{name} 学习笔记')
        )

        # 06 章节的 description 由 update_redblue_chapter.py 按实际模块生成
        if HAS_COMMON and name == '06-red-blue-confrontation':
            chapter_meta = read_index_metadata(path)
            description = chapter_meta.get('description', description) or description

        chapters.append({
            'dir': name,
            'icon': icon,
            'title': title,
            'description': description,
            'note_count': note_count,
        })
    return chapters

def build_chapter_list(chapters: list) -> str:
    """生成章节列表 Markdown"""
    lines = []
    for ch in chapters:
        lines.append(f"### [{ch['icon']} {ch['title']}]({ch['dir']}/)")
        lines.append(f"{ch['description']}（{ch['note_count']} 篇笔记）")
        lines.append("")
    return "\n".join(lines).rstrip()

# 模板内容
# 注意：knowledge_notes 字段存储的是知识笔记数（仅 knowledge 目录）
DEFAULT_CONTENT = '''---
knowledge_notes: {knowledge_notes}
last_updated: {update_time}
---

# 📖 知识笔记

> 网络安全知识体系，从基础到进阶。

## 📚 章节列表

{chapter_list}

---

## 📊 统计

- **章节数**：{chapter_count}
- **知识笔记数**：{knowledge_notes}
- **最后更新**：{update_time}

---

## 💬 安全语录

> "安全不是产品，而是一个过程。" —— Bruce Schneier

> "世界上只有两种公司：被黑过的，和被黑过但还不知道的。" —— 佚名

> "知道如何攻击，才知道如何防御。" —— 红队格言

---

*保持热爱，持续学习 🚀*
'''

def generate_knowledge_index(dry_run: bool = False) -> None:
    """生成 knowledge 板块总览 index.md"""
    print("=" * 60)
    print("Knowledge 板块总览 index.md 生成")
    print("=" * 60)
    print(f"路径: {KNOWLEDGE_PATH}")
    print(f"模式: {'DRY RUN' if dry_run else '实际运行'}")
    
    if not os.path.exists(KNOWLEDGE_PATH):
        print(f"错误：路径不存在 {KNOWLEDGE_PATH}")
        return
    
    # 实际扫描知识笔记数（仅 knowledge 目录）
    chapters = discover_chapters()
    knowledge_notes = scan_knowledge_notes_count()
    update_time = get_current_time()

    print(f"\n📊 扫描结果:")
    print(f"   章节数: {len(chapters)}")
    for ch in chapters:
        print(f"     {ch['dir']}: {ch['note_count']} 篇")
    print(f"   知识笔记数: {knowledge_notes}")
    print(f"   更新时间: {update_time}")

    content = DEFAULT_CONTENT.format(
        knowledge_notes=knowledge_notes,
        chapter_list=build_chapter_list(chapters),
        chapter_count=len(chapters),
        update_time=update_time
    )
    
    output_path = os.path.join(KNOWLEDGE_PATH, 'index.md')
    
    if safe_write(output_path, content, dry_run):
        print(f"\n✅ 已生成: {output_path}")
    
    print("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="更新 knowledge/index.md")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不实际写入")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    generate_knowledge_index(dry_run)