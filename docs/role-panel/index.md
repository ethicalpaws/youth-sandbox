---
title: 角色档案
hide:
  - navigation
  - toc
---

<script>
// 给 body 添加 role-panel 类名，排除全局样式
document.body.classList.add('role-panel-page');
</script>

<!-- Chart.js CDN -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background: linear-gradient(135deg, #0a0a0f 0%, #1a0a0a 100%);
    font-family: 'Segoe UI', system-ui, sans-serif;
}

/* ============================================
   Role Panel 页面 - 导航栏游戏化适配
   ============================================ */

/* 导航栏背景与游戏面板统一 */
body.role-panel-page .md-header {
  background: linear-gradient(135deg, #0a0a0f 0%, #1a0a0a 100%) !important;
  border-bottom: 2px solid #ffaa00 !important;
  box-shadow: none !important;
  height: 52px !important;
}

/* 隐藏默认的导航栏文字，用自定义内容替代 */
body.role-panel-page .md-header__topic {
  display: none !important;
}

/* 自定义导航栏内容 */
body.role-panel-page .md-header__inner {
  justify-content: space-between !important;
}

body.role-panel-page .md-header__inner::before {
  content: "🎮 角色档案系统" !important;
  color: #ffaa00 !important;
  font-family: 'Segoe UI', monospace !important;
  font-size: 0.9rem !important;
  font-weight: bold !important;
  letter-spacing: 2px !important;
  text-shadow: 0 0 10px rgba(255, 68, 68, 0.5) !important;
}

body.role-panel-page .md-header__inner::after {
  content: "⚔️ ETHICAL HACKER" !important;
  color: #ff6666 !important;
  font-family: monospace !important;
  font-size: 0.7rem !important;
  background: rgba(255, 68, 68, 0.15) !important;
  padding: 4px 12px !important;
  border-radius: 20px !important;
  border: 1px solid rgba(255, 170, 0, 0.3) !important;
}

/* 隐藏搜索框和 tabs */
body.role-panel-page .md-search,
body.role-panel-page .md-tabs,
body.role-panel-page .md-header__source {
  display: none !important;
}

/* 页面背景完全统一 */
body.role-panel-page {
  background: linear-gradient(135deg, #0a0a0f 0%, #1a0a0a 100%) !important;
}

body.role-panel-page .md-main {
  background: transparent !important;
  padding-top: 0.5rem !important;
}

/* 游戏面板与导航栏之间增加呼吸间距 */
body.role-panel-page .game-panel {
  margin-top: 1rem !important;
}

.loading {
    text-align: center;
    padding: 4rem;
    color: #886666;
}

.game-panel {
    max-width: 900px;
    width: 100%;
    margin: 2rem auto;
    background: linear-gradient(145deg, #0d0d12 0%, #15151a 100%);
    border-radius: 24px;
    border: 1px solid rgba(255, 170, 0, 0.3);
    box-shadow: 0 0 30px rgba(255, 68, 68, 0.15);
    overflow: hidden;
}

.game-header {
    background: linear-gradient(135deg, #1a0a0a 0%, #0d0d12 100%);
    padding: 1.5rem;
    border-bottom: 2px solid #ffaa00;
    position: relative;
}

.header-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.avatar {
    font-size: 3rem;
    background: linear-gradient(145deg, #2a1515, #1a0a0a);
    width: 70px;
    height: 70px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid #ffaa00;
    box-shadow: 0 0 15px rgba(255, 170, 0, 0.3);
}

.player-name {
    font-size: 1.3rem;
    font-weight: bold;
    color: #ffdd88;
}

.player-title {
    font-size: 0.75rem;
    color: #ff6666;
    margin-top: 0.25rem;
}

.header-right {
    text-align: right;
}

.level-badge {
    background: linear-gradient(135deg, #ff4444, #cc0000);
    color: #ffdd88;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
    border: 1px solid #ffaa00;
    display: inline-block;
}

.combat-power {
    font-size: 0.7rem;
    color: #ffaa88;
    margin-top: 0.25rem;
}

.motto {
    font-size: 0.7rem;
    color: #aa8866;
    margin-top: 0.75rem;
    font-style: italic;
    text-align: center;
}

.title-road {
    margin-top: 0.75rem;
    padding: 0.5rem;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 20px;
    text-align: center;
    font-size: 0.65rem;
    color: #ffaa88;
}

.game-content {
    padding: 1.5rem;
}

.card {
    background: rgba(0, 0, 0, 0.4);
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 1.25rem;
    border: 1px solid rgba(255, 68, 68, 0.3);
}

.card-title {
    color: #ffaa00;
    font-size: 0.85rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.exp-bar-container {
    background: #2a1515;
    border-radius: 20px;
    height: 28px;
    overflow: hidden;
    margin: 0.5rem 0;
}

.exp-bar-fill {
    background: linear-gradient(90deg, #ff4444, #ff8866);
    width: 0%;
    height: 100%;
    border-radius: 20px;
    transition: width 1s cubic-bezier(0.4, 1.2, 0.6, 1);
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 10px;
    color: #fff;
    font-size: 0.7rem;
    font-weight: bold;
}

.exp-stats {
    display: flex;
    justify-content: space-between;
    color: #ffaa88;
    font-size: 0.7rem;
    margin-top: 0.5rem;
}

.attrs-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.8rem;
}

.attr-item {
    margin-bottom: 0.5rem;
}

.attr-header {
    display: flex;
    justify-content: space-between;
    color: #ffddaa;
    font-size: 0.7rem;
    margin-bottom: 0.25rem;
}

.attr-bar {
    background: #1a0a0a;
    border-radius: 10px;
    height: 8px;
    overflow: hidden;
}

.attr-fill {
    background: linear-gradient(90deg, #ffaa00, #ffcc44);
    width: 0%;
    height: 100%;
    border-radius: 10px;
    transition: width 0.8s ease-out;
}

.radar-container {
    max-width: 280px;
    margin: 0 auto;
}

/* 技能树美化 */
.skills-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.8rem;
}

.skill-item {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 12px;
    padding: 0.6rem 0.8rem;
    transition: all 0.2s ease;
    border: 1px solid rgba(255, 170, 0, 0.2);
}

.skill-item:hover {
    border-color: rgba(255, 170, 0, 0.6);
    background: rgba(255, 170, 0, 0.05);
    transform: translateX(4px);
}

.skill-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #ffccaa;
    font-size: 0.7rem;
    margin-bottom: 0.35rem;
    font-weight: 500;
}

.skill-name {
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.skill-name::before {
    content: "▸";
    color: #ffaa00;
    font-size: 0.6rem;
}

.skill-bar {
    background: #1a0a0a;
    border-radius: 10px;
    height: 6px;
    overflow: hidden;
    box-shadow: inset 0 0 2px rgba(0,0,0,0.5);
}

.skill-fill {
    background: linear-gradient(90deg, #ffaa00, #ffcc44);
    width: 0%;
    height: 100%;
    border-radius: 10px;
    transition: width 0.6s cubic-bezier(0.4, 1.2, 0.6, 1);
    position: relative;
    overflow: hidden;
}

.skill-fill::after {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, rgba(255,255,255,0.2), transparent);
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.heatmap {
    display: flex;
    flex-wrap: wrap;
    gap: 3px;
    justify-content: center;
    max-height: 130px;
    overflow-y: auto;
    padding: 0.25rem;
}

.heatmap-day {
    width: 18px;
    height: 18px;
    border-radius: 3px;
}

.heatmap-day.level-0 { background: #c9c9c940; }
.heatmap-day.level-1 { background: #8B5A2B; }
.heatmap-day.level-2 { background: #DAA520; }
.heatmap-day.level-3 { background: #FF6347; }
.heatmap-day.level-4 { background: #FF0000; }

.achievement-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px solid rgba(255, 68, 68, 0.2);
}

.achievement-item:last-child {
    border-bottom: none;
}

.achievement-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.achievement-name {
    font-size: 0.75rem;
    color: #ffccaa;
}

.achievement-date {
    font-size: 0.65rem;
    color: #886666;
}

.achievement-xp {
    font-size: 0.7rem;
    color: #ffaa44;
}

.quote {
    background: linear-gradient(135deg, rgba(255, 68, 68, 0.1), rgba(255, 170, 0, 0.05));
    border-radius: 12px;
    padding: 0.75rem 1rem;
    text-align: center;
    color: #ffaa88;
    font-size: 0.75rem;
    font-style: italic;
}

.two-columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

@media (max-width: 700px) {
    .two-columns {
        grid-template-columns: 1fr;
    }
    .attrs-grid {
        grid-template-columns: 1fr;
    }
    .skills-grid {
        grid-template-columns: 1fr;
    }
}
</style>

<div id="role-panel-root">
  <div class="loading">🎮 加载角色数据中...</div>
</div>

<script>
async function loadRolePanel() {
    const container = document.getElementById('role-panel-root');
    
    try {
        const [charRes, quotesRes] = await Promise.all([
            fetch('/youth-sandbox/data/character.json'),
            fetch('/youth-sandbox/data/quotes.json')
        ]);
        
        if (!charRes.ok) throw new Error('角色数据加载失败: ' + charRes.status);
        if (!quotesRes.ok) throw new Error('语录数据加载失败: ' + quotesRes.status);
        
        const charData = await charRes.json();
        const quotesData = await quotesRes.json();
        
        const auto = charData.auto;
        const manual = charData.manual;
        const skills = auto.skills || {};
        
        // 头衔映射
        function getTitleByLevel(level) {
            if (level <= 10) return "安全萌新";
            if (level <= 15) return "脚本小子";
            if (level <= 20) return "漏洞猎人";
            if (level <= 25) return "安全专家";
            if (level <= 30) return "攻防大师";
            if (level <= 35) return "红队精英";
            if (level <= 40) return "安全研究员";
            if (level <= 45) return "守护者";
            return "传奇黑客";
        }
        
        // 头衔进阶路线
        const titleRoad = [
            { level: 10, name: "安全萌新" },
            { level: 15, name: "脚本小子" },
            { level: 20, name: "漏洞猎人" },
            { level: 25, name: "安全专家" },
            { level: 30, name: "攻防大师" },
            { level: 35, name: "红队精英" },
            { level: 40, name: "安全研究员" },
            { level: 45, name: "守护者" },
            { level: 50, name: "传奇黑客" }
        ];
        
        let currentIndex = 0;
        for (let i = 0; i < titleRoad.length; i++) {
            if (auto.level <= titleRoad[i].level) {
                currentIndex = i;
                break;
            }
        }
        
        let roadHtml = '';
        for (let i = 0; i < titleRoad.length; i++) {
            const isCurrent = i === currentIndex;
            const isPassed = i < currentIndex;
            roadHtml += `<span style="color: ${isPassed ? '#ffaa44' : (isCurrent ? '#ff4444' : '#886666')}">${titleRoad[i].name}</span>`;
            if (i < titleRoad.length - 1) roadHtml += ' → ';
        }
        
        // 战力计算 - 包含所有16项能力
        const combatPower = Math.floor(
            (skills.web_security || 0) * 80 +
            (skills.web_advanced || 0) * 80 +
            (skills.java_security || 0) * 150 +
            (skills.ctf_ability || 0) * 70 +
            (skills.cve_analysis || 0) * 80 +
            (skills.programming || 0) * 60 +
            (skills.bypass_waf || 0) * 100 +
            (skills.code_review || 0) * 90 +
            (skills.internal_network || 0) * 100 +
            (skills.pwn || 0) * 120 +
            (skills.evasion || 0) * 80 +
            (skills.lateral_movement || 0) * 90 +
            (skills.c2_framework || 0) * 90 +
            (skills.blue_team || 0) * 70 +
            (skills.network_traffic || 0) * 60 +
            (skills.cryptography || 0) * 50
        );
        
        const currentTitle = getTitleByLevel(auto.level);
        const expPercent = (auto.current_exp / auto.next_exp * 100).toFixed(1);
        
        // 属性面板
        const rpgAttrs = [
            { 
                name: "🎯 信息收集", 
                value: (skills.web_security || 0) * 0.7 + (skills.code_review || 0) * 0.3, 
                max: 100 
            },
            { 
                name: "🔓 漏洞挖掘", 
                value: (skills.web_advanced || 0) * 0.15 + (skills.src_dig || 0) * 0.4 + (skills.cve_analysis || 0) * 0.3 + (skills.cryptography || 0) * 0.15, 
                max: 100 
            },
            { 
                name: "💣 利用开发", 
                value: (skills.ctf_ability || 0) * 0.3 + (skills.java_security || 0) * 0.3 + (skills.programming || 0) * 0.3 + (skills.cryptography || 0) * 0.1, 
                max: 100 
            },
            { 
                name: "🛡️ 绕过技巧", 
                value: (skills.web_security || 0) * 0.3 + (skills.ctf_ability || 0) * 0.4 + (skills.bypass_waf || 0) * 0.3, 
                max: 100 
            },
            { 
                name: "⚔️ 攻防对抗", 
                value: (skills.network_traffic || 0) * 0.1 + (skills.c2_framework || 0) * 0.2 + (skills.lateral_movement || 0) * 0.3 + (skills.evasion || 0) * 0.1 + (skills.internal_network || 0) * 0.3, 
                max: 100 
            }
        ];
        
        // 雷达图数据
        const radarLabels = ['Web安全', 'Java安全', 'CTF能力', 'CVE分析', '编程能力', '绕WAF', '内网渗透', '二进制安全'];
        const radarValues = [
            (skills.web_security || 0) + (skills.web_advanced || 0),
            skills.java_security || 0,
            skills.ctf_ability || 0,
            skills.cve_analysis || 0,
            skills.programming || 0,
            skills.bypass_waf || 0,
            skills.internal_network || 0,
            skills.pwn || 0
        ];
        
        // 动态计算雷达图最大值
        let maxValue = Math.max(...radarValues);
        let radarMax = 20;
        if (maxValue > 90) radarMax = 100;
        else if (maxValue > 80) radarMax = 90;
        else if (maxValue > 70) radarMax = 80;
        else if (maxValue > 60) radarMax = 70;
        else if (maxValue > 50) radarMax = 60;
        else if (maxValue > 40) radarMax = 50;
        else if (maxValue > 30) radarMax = 40;
        else if (maxValue > 20) radarMax = 30;
        else radarMax = 20;
        
        // 技能树 - 16项能力
        const skillTree = [
            { name: "Web基础", value: skills.web_security || 0, icon: "🌐", max: 100 },
            { name: "Web高级", value: skills.web_advanced || 0, icon: "⚡", max: 100 },
            { name: "Java安全", value: skills.java_security || 0, icon: "☕", max: 100 },
            { name: "CTF能力", value: skills.ctf_ability || 0, icon: "🏆", max: 100 },
            { name: "CVE分析", value: skills.cve_analysis || 0, icon: "🐞", max: 100 },
            { name: "编程能力", value: skills.programming || 0, icon: "💻", max: 100 },
            { name: "绕WAF", value: skills.bypass_waf || 0, icon: "🛡️", max: 100 },
            { name: "代码审计", value: skills.code_review || 0, icon: "🔍", max: 100 },
            { name: "内网渗透", value: skills.internal_network || 0, icon: "🌐", max: 100 },
            { name: "二进制安全", value: skills.pwn || 0, icon: "⚙️", max: 100 },
            { name: "免杀能力", value: skills.evasion || 0, icon: "🎭", max: 100 },
            { name: "横向移动", value: skills.lateral_movement || 0, icon: "🔄", max: 100 },
            { name: "C2框架", value: skills.c2_framework || 0, icon: "📡", max: 100 },
            { name: "蓝队防御", value: skills.blue_team || 0, icon: "🛡️", max: 100 },
            { name: "网络流量", value: skills.network_traffic || 0, icon: "📊", max: 100 },
            { name: "密码学", value: skills.cryptography || 0, icon: "🔐", max: 100 }
        ];
        
        // 生成技能树 HTML
        const skillsHtml = skillTree.map(skill => {
            const percent = (skill.value / skill.max * 100).toFixed(1);
            return `
                <div class="skill-item">
                    <div class="skill-header">
                        <div class="skill-name">
                            <span>${skill.icon}</span>
                            <span>${skill.name}</span>
                        </div>
                        <span>${skill.value} / ${skill.max}</span>
                    </div>
                    <div class="skill-bar">
                        <div class="skill-fill" data-width="${percent}%"></div>
                    </div>
                </div>
            `;
        }).join('');
        
        // 热力图数据
        const heatmapData = auto.heatmap || { weeks: [] };
        const weeksData = heatmapData.weeks || [];
        const weeklyScores = auto.stats.weekly_scores || [];

        function getWeekActivityLevel(weekDays, weekIndex) {
            let totalNotes = 0;
            for (let d = 0; d < 7; d++) totalNotes += weekDays[d] || 0;
            const weeklyScore = weeklyScores[weekIndex] || 0;
            
            let noteScore = 0;
            if (totalNotes >= 10) noteScore = 2;
            else if (totalNotes >= 7) noteScore = 1.8;
            else if (totalNotes >= 5) noteScore = 1.5;
            else if (totalNotes >= 3) noteScore = 1.0;
            else if (totalNotes >= 1) noteScore = 0.5;
            
            let testScore = 0;
            if (weeklyScore >= 95) testScore = 2;
            else if (weeklyScore >= 90) testScore = 1.8;
            else if (weeklyScore >= 85) testScore = 1.5;
            else if (weeklyScore >= 80) testScore = 1.2;
            else if (weeklyScore >= 75) testScore = 1.0;
            else if (weeklyScore >= 70) testScore = 0.8;
            else if (weeklyScore >= 65) testScore = 0.5;
            else if (weeklyScore >= 60) testScore = 0.3;
            
            const totalScore = noteScore + testScore;
            if (totalScore >= 3.5) return 4;
            if (totalScore >= 2.5) return 3;
            if (totalScore >= 1.5) return 2;
            if (totalScore >= 0.5) return 1;
            return 0;
        }

        let heatmapHtml = '';
        for (let i = 0; i < weeksData.length; i++) {
            const week = weeksData[i];
            const level = getWeekActivityLevel(week.days, i);
            heatmapHtml += `<div class="heatmap-day level-${level}" title="第${i+1}周"></div>`;
        }
        
        // 成就
        const achievements = manual.special_achievements || [];
        
        // 随机语录
        const tips = quotesData.weekly_tips || ['Flag 出来的那一刻，值了'];
        const randomQuote = tips[Math.floor(Math.random() * tips.length)];
        
        // 生成属性面板 HTML
        const attrsHtml = rpgAttrs.map(attr => {
            const percent = (attr.value / attr.max * 100).toFixed(1);
            return `
                <div class="attr-item">
                    <div class="attr-header">
                        <span>${attr.name}</span>
                        <span>${attr.value.toFixed(1)}</span>
                    </div>
                    <div class="attr-bar">
                        <div class="attr-fill" data-width="${percent}%"></div>
                    </div>
                </div>
            `;
        }).join('');
        
        // 生成成就 HTML
        const achievementsHtml = achievements.length > 0 
            ? achievements.map(ach => {
                const parts = ach.split(' - ');
                return `
                    <div class="achievement-item">
                        <div class="achievement-info">
                            <span>🏆</span>
                            <div>
                                <div class="achievement-name">${parts[0]}</div>
                                <div class="achievement-date">${parts[1] || ''}</div>
                            </div>
                        </div>
                        <div class="achievement-xp">✨</div>
                    </div>
                `;
            }).join('')
            : '<div style="color:#886666; text-align:center; padding:0.5rem;">暂无成就，继续努力！</div>';
        
        // 头像处理
        const avatarHtml = manual.avatar && (manual.avatar.startsWith('/') || manual.avatar.startsWith('http'))
            ? `<img src="${manual.avatar}" alt="avatar" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">`
            : `<span style="font-size: 3rem;">${manual.avatar || '🐕'}</span>`;

        const panelHtml = `
            <div class="game-panel">
                <div class="game-header">
                    <div class="header-top">
                        <div class="header-left">
                            <div class="avatar">${avatarHtml}</div>
                            <div>
                                <div class="player-name">${manual.name || 'ethicalpaws'}</div>
                                <div class="player-title">🔰 ${currentTitle}</div>
                            </div>
                        </div>
                        <div class="header-right">
                            <div class="level-badge">⭐ Lv.${auto.level}</div>
                            <div class="combat-power">⚡ 战力 ${combatPower.toLocaleString()}</div>
                        </div>
                    </div>
                    <div class="motto">"${manual.motto || '路漫漫其修远兮'}"</div>
                    <div class="title-road">📈 进阶路线：${roadHtml}</div>
                </div>
                <div class="game-content">
                    <div class="card">
                        <div class="card-title">📊 经验值</div>
                        <div class="exp-bar-container">
                            <div class="exp-bar-fill" id="expFill" data-width="${expPercent}%">${expPercent}%</div>
                        </div>
                        <div class="exp-stats">
                            <span>${auto.current_exp} / ${auto.next_exp}</span>
                            <span>${expPercent}%</span>
                        </div>
                    </div>
                    
                    <div class="two-columns">
                        <div class="card">
                            <div class="card-title">⚔️ 属性面板</div>
                            <div class="attrs-grid">${attrsHtml}</div>
                        </div>
                        
                        <div class="card">
                            <div class="card-title">📡 能力雷达</div>
                            <div class="radar-container">
                                <canvas id="radarChart" width="250" height="250"></canvas>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-title">🔧 技能树</div>
                        <div class="skills-grid">${skillsHtml}</div>
                    </div>
                    
                    <div class="card">
                        <div class="card-title">🔥 学习热力图</div>
                        <div class="heatmap">${heatmapHtml}</div>
                        <div style="margin-top: 0.5rem; font-size: 0.6rem; color: #886666; text-align: center; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                            <span><span style="display: inline-block; width: 12px; height: 12px; background: #bdb5b5c6; border-radius: 2px;"></span> 无</span>
                            <span><span style="display: inline-block; width: 12px; height: 12px; background: #DAA520; border-radius: 2px;"></span> 中</span>
                            <span><span style="display: inline-block; width: 12px; height: 12px; background: #FF6347; border-radius: 2px;"></span> 高</span>
                            <span><span style="display: inline-block; width: 12px; height: 12px; background: #FF0000; border-radius: 2px;"></span> 极高</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-title">🏆 成就殿堂</div>
                        ${achievementsHtml}
                    </div>
                    
                    <div class="quote">💬 "${randomQuote}"</div>
                </div>
            </div>
        `;
        
        container.innerHTML = panelHtml;
        
        // 初始化雷达图
        const ctx = document.getElementById('radarChart').getContext('2d');
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: radarLabels,
                datasets: [{
                    label: '能力值',
                    data: radarValues,
                    backgroundColor: 'rgba(255, 170, 0, 0.2)',
                    borderColor: '#ffaa00',
                    borderWidth: 2,
                    pointBackgroundColor: '#ffaa00',
                    pointBorderColor: '#fff',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: radarMax,
                        ticks: {
                            stepSize: radarMax / 5,
                            color: '#ffaa88'
                        },
                        grid: {
                            color: 'rgba(255, 170, 0, 0.2)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffaa88'
                        }
                    }
                }
            }
        });
        
        // 执行进度条动画
        setTimeout(() => {
            const expFill = document.getElementById('expFill');
            if (expFill) expFill.style.width = expFill.getAttribute('data-width') + '%';
            document.querySelectorAll('.attr-fill, .skill-fill').forEach(fill => {
                const width = fill.getAttribute('data-width');
                if (width) fill.style.width = width + '%';
            });
        }, 100);
        
    } catch (error) {
        console.error('加载失败:', error);
        container.innerHTML = '<div class="loading">⚠️ 加载失败，请刷新重试<br><br>' + error.message + '</div>';
    }
}

loadRolePanel();
</script>