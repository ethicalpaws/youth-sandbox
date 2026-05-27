// A3 暗黑游戏风格 - 完整逻辑
async function loadRolePanel() {
    const container = document.getElementById('role-panel-root');
    
    try {
        // 使用相对路径：从 asserts/js/ 向上两级到 docs/，再进入 data/
        const charRes = await fetch('../../data/character.json');
        const quotesRes = await fetch('../../data/quotes.json');
        
        if (!charRes.ok) throw new Error('角色数据加载失败: ' + charRes.status);
        if (!quotesRes.ok) throw new Error('语录数据加载失败: ' + quotesRes.status);
        
        const charData = await charRes.json();
        const quotesData = await quotesRes.json();
        
        const auto = charData.auto;
        const manual = charData.manual;
        
        const expPercent = (auto.current_exp / auto.next_exp * 100).toFixed(1);
        const skills = auto.skills || {};
        
        const rpgAttrs = [
            { name: "⚔️ 攻击力", value: (skills.web_security || 0) * 8 + 20, max: 100 },
            { name: "🛡️ 防御力", value: (skills.java_security || 0) * 6 + 20, max: 100 },
            { name: "⚡ 敏捷度", value: (skills.ctf_ability || 0) * 7 + 20, max: 100 },
            { name: "🔮 智慧", value: (skills.cve_analysis || 0) * 9 + 20, max: 100 }
        ];
        
        const termSkills = [
            { name: "WEB_SECURITY", level: skills.web_security || 0, max: 20 },
            { name: "WEB_ADVANCED", level: skills.web_advanced || 0, max: 20 },
            { name: "JAVA_SECURITY", level: skills.java_security || 0, max: 20 },
            { name: "CTF_ABILITY", level: skills.ctf_ability || 0, max: 20 }
        ];
        
        const achievements = manual.special_achievements || [];
        const tips = quotesData.weekly_tips || ['Flag 出来的那一刻，值了'];
        const randomQuote = tips[Math.floor(Math.random() * tips.length)];
        
        const rpgHtml = rpgAttrs.map(attr => {
            const percent = (attr.value / attr.max * 100).toFixed(1);
            return `
                <div class="attr-item">
                    <div class="attr-header">
                        <span>${attr.name}</span>
                        <span>${attr.value}</span>
                    </div>
                    <div class="attr-bar">
                        <div class="attr-fill" data-width="${percent}%"></div>
                    </div>
                </div>
            `;
        }).join('');
        
        const skillsHtml = termSkills.map(skill => {
            const percent = (skill.level / skill.max * 100).toFixed(1);
            return `
                <div class="skill-item">
                    <div class="skill-header">
                        <span>├─ ${skill.name}</span>
                        <span>Lv.${skill.level}</span>
                    </div>
                    <div class="skill-bar">
                        <div class="skill-fill" data-width="${percent}%"></div>
                    </div>
                </div>
            `;
        }).join('');
        
        const achievementsHtml = achievements.length > 0 
            ? achievements.map(ach => `
                <div class="achievement-item">
                    <div class="achievement-info">
                        <span>🏆</span>
                        <div>
                            <div class="achievement-name">${ach}</div>
                        </div>
                    </div>
                    <div class="achievement-xp">✨</div>
                </div>
            `).join('')
            : '<div style="color:#886666; text-align:center; padding:0.5rem;">暂无成就，继续努力！</div>';
        
        const panelHtml = `
            <div class="game-panel">
                <div class="game-header">
                    <div class="level-badge">⭐ Lv.${auto.level}</div>
                    <div class="avatar">🐕</div>
                    <div class="player-name">${manual.name || 'ethicalpaws'}</div>
                    <div class="player-title">✨ ${manual.title || '漏洞猎人'} ✨</div>
                    <div class="motto">"${manual.motto || '路漫漫其修远兮'}"</div>
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
                    
                    <div class="card">
                        <div class="card-title">⚔️ 属性面板</div>
                        ${rpgHtml}
                    </div>
                    
                    <div class="card">
                        <div class="card-title">📚 技能树</div>
                        ${skillsHtml}
                    </div>
                    
                    <div class="card">
                        <div class="card-title">🏆 成就殿堂</div>
                        ${achievementsHtml}
                    </div>
                    
                    <div class="quote">
                        💬 "${randomQuote}"
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = panelHtml;
        
        setTimeout(() => {
            const expFill = document.getElementById('expFill');
            if (expFill) {
                expFill.style.width = expFill.getAttribute('data-width') + '%';
            }
            document.querySelectorAll('.attr-fill, .skill-fill').forEach(fill => {
                fill.style.width = fill.getAttribute('data-width') + '%';
            });
        }, 100);
        
    } catch (error) {
        console.error('加载失败:', error);
        container.innerHTML = '<div class="loading">⚠️ 加载失败<br><br>' + error.message + '</div>';
    }
}

if (document.getElementById('role-panel-root')) {
    loadRolePanel();
}