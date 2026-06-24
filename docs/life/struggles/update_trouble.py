#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_trouble.py - 从 source.md 直接生成烦恼记录 HTML
用法: python update_trouble.py
"""

import os
import re
import json
from datetime import datetime

# ==================== 配置 ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = os.path.join(SCRIPT_DIR, "source.md")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "index.md")

# ==================== 样式 ====================
STYLES = '''
<style>
.wr-container { max-width: 800px; margin: 0 auto; }
.wr-item { margin-bottom: 1.5rem; }
.wr-locked {
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255, 100, 100, 0.3);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
}
.wr-locked:hover {
    background: rgba(0, 0, 0, 0.5);
    border-color: rgba(255, 100, 100, 0.6);
    transform: scale(1.01);
}
.wr-locked-icon { font-size: 3rem; display: block; margin-bottom: 1rem; }
.wr-locked-title { font-size: 1.2rem; color: #ffaa88; margin-bottom: 0.5rem; }
.wr-locked-hint { font-size: 0.75rem; color: #886666; }
.wr-unlocked {
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 170, 0, 0.3);
    border-radius: 16px;
    padding: 1.5rem;
    animation: wr-fadeIn 0.5s ease;
}
.wr-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 170, 0, 0.3);
}
.wr-header-icon { font-size: 1.5rem; }
.wr-header-title { font-size: 1.1rem; color: #ffaa88; font-weight: bold; }
.wr-date { font-size: 0.7rem; color: #886666; margin-left: auto; }
.wr-content { color: #ddccaa; font-size: 0.9rem; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; }
.wr-content p { margin-bottom: 0.8rem; }
.wr-content ul, .wr-content ol { margin-left: 1.5rem; margin-bottom: 0.8rem; }
.wr-content li { margin-bottom: 0.3rem; }
.wr-error {
    background: rgba(255, 68, 68, 0.2);
    border: 1px solid #ff4444;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    color: #ff8888;
    font-size: 0.75rem;
    margin-top: 0.5rem;
    display: none;
}
.wr-error.show { display: block; animation: wr-shake 0.3s ease; }
@keyframes wr-fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes wr-shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}
</style>
'''

# ==================== 解析函数 ====================

def parse_source_md(content):
    """解析 source.md，提取每条记录"""
    records = []
    
    # 按 --- 分隔每条记录
    blocks = re.split(r'\n---\n', content)
    
    for block in blocks:
        if not block.strip():
            continue
        
        lines = block.strip().split('\n')
        
        # 解析 Front Matter
        metadata = {}
        content_lines = []
        in_front_matter = True
        
        for line in lines:
            if in_front_matter:
                if line.strip() == '':
                    in_front_matter = False
                    continue
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
            else:
                content_lines.append(line)
        
        if not metadata.get('id'):
            continue
        
        # 转换内容为 HTML
        content_text = '\n'.join(content_lines).strip()
        html_content = text_to_html(content_text)
        
        # 格式化日期显示
        try:
            date_obj = datetime.strptime(metadata.get('date', ''), "%Y-%m-%d")
            display_date = date_obj.strftime("%Y年%m月%d日")
        except:
            display_date = metadata.get('date', '')
        
        record = {
            "id": int(metadata.get('id', 0)),
            "date": metadata.get('date', ''),
            "display_date": display_date,
            "time": metadata.get('time', '00:00'),
            "title": metadata.get('title', '未命名'),
            "icon": metadata.get('icon', '📝'),
            "question": metadata.get('question', '请输入密码：'),
            "answer": metadata.get('answer', ''),
            "content": html_content
        }
        
        records.append(record)
    
    return records

def text_to_html(text):
    """将纯文本转换为 HTML"""
    # 处理代码块
    text = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', text, flags=re.DOTALL)
    
    lines = text.split('\n')
    html_lines = []
    in_list = False
    list_type = None
    
    for line in lines:
        original_line = line
        line = line.strip()
        if not line:
            if in_list:
                html_lines.append('</{}>'.format(list_type))
                in_list = False
                list_type = None
            continue
        
        # 标题
        if line.startswith('### '):
            if in_list:
                html_lines.append('</{}>'.format(list_type))
                in_list = False
            html_lines.append('<h3>{}</h3>'.format(line[4:]))
        elif line.startswith('#### '):
            if in_list:
                html_lines.append('</{}>'.format(list_type))
                in_list = False
            html_lines.append('<h4>{}</h4>'.format(line[5:]))
        # 加粗
        elif line.startswith('**') and line.endswith('**'):
            if in_list:
                html_lines.append('</{}>'.format(list_type))
                in_list = False
            html_lines.append('<strong>{}</strong>'.format(line[2:-2]))
        # 无序列表
        elif re.match(r'^[-*]\s+', line):
            if not in_list or list_type != 'ul':
                if in_list:
                    html_lines.append('</{}>'.format(list_type))
                html_lines.append('<ul>')
                in_list = True
                list_type = 'ul'
            item_content = re.sub(r'^[-*]\s+', '', line)
            html_lines.append('<li>{}</li>'.format(item_content))
        # 有序列表
        elif re.match(r'^\d+\.\s+', line):
            if not in_list or list_type != 'ol':
                if in_list:
                    html_lines.append('</{}>'.format(list_type))
                html_lines.append('<ol>')
                in_list = True
                list_type = 'ol'
            item_content = re.sub(r'^\d+\.\s+', '', line)
            html_lines.append('<li>{}</li>'.format(item_content))
        # 引用块
        elif line.startswith('>'):
            if in_list:
                html_lines.append('</{}>'.format(list_type))
                in_list = False
            html_lines.append('<blockquote>{}</blockquote>'.format(line[1:].strip()))
        # 普通段落
        else:
            if in_list:
                html_lines.append('</{}>'.format(list_type))
                in_list = False
                list_type = None
            html_lines.append('<p>{}</p>'.format(line))
    
    if in_list:
        html_lines.append('</{}>'.format(list_type))
    
    return '\n'.join(html_lines)

# ==================== 生成 HTML ====================

def generate_html(records):
    """生成完整 HTML"""
    records_html = []
    
    # 生成配置 JS
    config_js = {}
    for r in records:
        config_js[str(r['id'])] = {
            "question": r['question'],
            "answer": r['answer']
        }
    
    for r in records:
        record_html = '''
    <div class="wr-item" data-wr-id="{id}">
        <div class="wr-locked" onclick="wr_unlock({id})">
            <span class="wr-locked-icon">🔒</span>
            <div class="wr-locked-title">{display_date} · {title}</div>
            <div class="wr-locked-hint">点击解锁 · 回答正确即可查看</div>
        </div>
        <div class="wr-unlocked" style="display: none;">
            <div class="wr-header">
                <span class="wr-header-icon">{icon}</span>
                <span class="wr-header-title">{title}</span>
                <span class="wr-date">{date} {time}</span>
            </div>
            <div class="wr-content">
                {content}
            </div>
        </div>
    </div>'''.format(
            id=r['id'],
            display_date=r['display_date'],
            title=r['title'],
            icon=r['icon'],
            date=r['date'],
            time=r['time'],
            content=r['content']
        )
        records_html.append(record_html)
    
    html = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>烦恼记录</title>
{styles}
</head>
<body>
<div class="wr-container">
    <h1 style="text-align: center; color: #ffaa88; margin-bottom: 2rem;">📔 烦恼记录</h1>
    {records}
</div>

<script>
(function() {{
    const wr_config = {config};
    
    function wr_showError(element, message) {{
        let errorDiv = element.querySelector('.wr-error');
        if (!errorDiv) {{
            errorDiv = document.createElement('div');
            errorDiv.className = 'wr-error';
            element.appendChild(errorDiv);
        }}
        errorDiv.innerText = message;
        errorDiv.classList.add('show');
        setTimeout(() => {{
            errorDiv.classList.remove('show');
        }}, 2000);
    }}
    
    window.wr_unlock = function(id) {{
        const item = document.querySelector('.wr-item[data-wr-id="' + id + '"]');
        if (!item) return;
        
        const lockedDiv = item.querySelector('.wr-locked');
        const unlockedDiv = item.querySelector('.wr-unlocked');
        
        if (unlockedDiv.style.display === 'block') return;
        
        const config = wr_config[id];
        if (!config) return;
        
        const userAnswer = prompt(config.question);
        if (userAnswer === null) return;
        
        if (userAnswer.trim() === config.answer) {{
            lockedDiv.style.display = 'none';
            unlockedDiv.style.display = 'block';
        }} else {{
            wr_showError(lockedDiv, '❌ 答案错误，再试试看～');
        }}
    }};
}})();
</script>
</body>
</html>'''.format(
        styles=STYLES,
        records='\n'.join(records_html),
        config=json.dumps(config_js, ensure_ascii=False)
    )
    
    return html

# ==================== 主函数 ====================

def main():
    print("=" * 60)
    print("烦恼记录更新脚本")
    print("=" * 60)
    print(f"源文件: {SOURCE_FILE}")
    print(f"输出文件: {OUTPUT_FILE}")
    
    if not os.path.exists(SOURCE_FILE):
        print(f"\n❌ 源文件不存在")
        print(f"请先创建 {SOURCE_FILE}")
        return
    
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.strip():
        print("\n❌ 源文件为空")
        return
    
    records = parse_source_md(content)
    print(f"\n📊 找到 {len(records)} 条记录")
    
    for r in records:
        print(f"   - [{r['id']}] {r['date']} {r['title'][:30]}...")
    
    if not records:
        print("\n⚠️ 未找到有效记录")
        print("\n请确保 source.md 格式正确：")
        print("  - 每条记录以 id: 开头")
        print("  - 字段和正文之间有一个空行")
        print("  - 记录之间用 --- 分隔")
        return
    
    html_content = generate_html(records)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ 已生成: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()