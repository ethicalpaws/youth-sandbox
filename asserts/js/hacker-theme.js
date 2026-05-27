// ============================================
// 黑客帝国风格 - 技术学习页面专用 JS
// 通过 URL 路径检测当前页面
// ============================================

(function() {
    // 检查当前是否在 tech-study 页面
    function isTechStudyPage() {
        const url = window.location.pathname;
        return url.includes('/tech-study/');
    }
    
    // 如果是技术学习页面，添加类名并执行特效
    if (isTechStudyPage()) {
        // 给 body 添加黑客主题类名
        document.body.classList.add('hacker-theme');
        console.log('🎮 黑客帝国模式已启动');
        
        // 1. 添加光标闪烁效果到所有 h1
        const h1Elements = document.querySelectorAll('.md-typeset h1');
        h1Elements.forEach(h1 => {
            if (!h1.querySelector('.cursor-blink')) {
                const cursor = document.createElement('span');
                cursor.className = 'cursor-blink';
                cursor.textContent = '_';
                cursor.style.cssText = `
                    display: inline-block;
                    animation: blink 1s step-end infinite;
                    margin-left: 2px;
                `;
                h1.appendChild(cursor);
            }
        });
        
        // 2. 添加终端提示符到代码块
        const codeBlocks = document.querySelectorAll('.md-typeset pre code');
        codeBlocks.forEach(code => {
            if (!code.hasAttribute('data-terminal')) {
                code.setAttribute('data-terminal', 'true');
                const lines = code.innerHTML.split('\n');
                const terminalLines = lines.map(line => {
                    if (line.trim()) {
                        return `<span style="color: #00ff41;">$></span> ${line}`;
                    }
                    return line;
                });
                code.innerHTML = terminalLines.join('\n');
            }
        });
    }
})();

// 添加 blink 动画样式到 head
const style = document.createElement('style');
style.textContent = `
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }
    
    .cursor-blink {
        display: inline-block;
        animation: blink 1s step-end infinite;
    }
    
    /* 终端代码块样式 */
    [data-terminal="true"] span {
        display: block;
    }
`;
document.head.appendChild(style);