// ========== 通用的每周彩蛋系统 ==========
// 支持：单密码、多密码、图片/HTML内容

// 主要入口函数（自动判断使用哪种模式）
function checkWeeklyPassword(triggerElement) {
    // 检查是多密码模式还是单密码模式
    var passwordsStr = triggerElement.getAttribute('data-week-passwords');
    
    if (passwordsStr) {
        // 多密码模式：data-week-passwords 和 data-week-contents
        var contentsStr = triggerElement.getAttribute('data-week-contents');
        if (!contentsStr) {
            alert("⚠️ 多密码模式需要同时设置 data-week-passwords 和 data-week-contents");
            return;
        }
        handleMultiPassword(triggerElement, passwordsStr, contentsStr);
    } else {
        // 单密码模式：data-week-password 和 data-week-content
        var password = triggerElement.getAttribute('data-week-password');
        var content = triggerElement.getAttribute('data-week-content');
        var title = triggerElement.getAttribute('data-week-title') || "📖 本周彩蛋";
        
        if (!password) {
            alert("⚠️ 请设置 data-week-password 属性");
            return;
        }
        
        var userPassword = prompt("🔐 输入密码，才能看到隐藏内容：");
        if (userPassword === null) return;
        
        if (userPassword === password) {
            showEggModal(title, content || "✨ 恭喜你找到了隐藏内容！");
        } else {
            alert("❌ 密码错误，再试试？");
        }
    }
}

// 多密码模式处理
function handleMultiPassword(triggerElement, passwordsStr, contentsStr) {
    var passwords = passwordsStr.split(',');
    var contents = contentsStr.split('|');
    
    if (passwords.length !== contents.length) {
        alert("⚠️ 密码数量和内容数量不匹配");
        return;
    }
    
    var userPassword = prompt("🔐 输入密码：");
    if (userPassword === null) return;
    
    for (var i = 0; i < passwords.length; i++) {
        if (userPassword === passwords[i].trim()) {
            var title = triggerElement.getAttribute('data-week-title') || "彩蛋等级 " + (i + 1);
            showEggModal(title, contents[i]);
            return;
        }
    }
    alert("❌ 密码错误，再试试？");
}

// 显示弹窗（支持图片、HTML富文本）
function showEggModal(title, contentHtml) {
    // 移除已有的弹窗（防止重复）
    var existingOverlay = document.querySelector('.egg-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }
    var existingModal = document.querySelector('.egg-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    var overlay = document.createElement('div');
    overlay.className = 'egg-overlay';
    document.body.appendChild(overlay);
    
    var modal = document.createElement('div');
    modal.className = 'egg-modal';
    modal.innerHTML = `
        <div class="egg-close">✖</div>
        <div style="text-align: left; max-height: 70vh; overflow-y: auto;">
            <h3 style="color: #ffd700; margin-top: 0; margin-bottom: 10px;">${escapeHtml(title)}</h3>
            <hr style="margin: 10px 0; border-color: #444;">
            <div style="line-height: 1.6;">${contentHtml || '<p>✨ 暂无内容</p>'}</div>
            <hr style="margin: 10px 0; border-color: #444;">
            <p style="font-size: 10px; color: #666; margin-top: 15px; margin-bottom: 0;">🔒 下周密码会更新，记得再来~</p>
        </div>
    `;
    document.body.appendChild(modal);
    
    overlay.style.display = 'block';
    modal.style.display = 'block';
    
    var closeBtn = modal.querySelector('.egg-close');
    closeBtn.onclick = function() {
        modal.remove();
        overlay.remove();
    };
    overlay.onclick = function() {
        modal.remove();
        overlay.remove();
    };
}

// HTML转义（只转义敏感字符，保留HTML标签用于富文本）
function escapeHtml(text) {
    if (!text) return "";
    // 只转义标题中的特殊字符，防止XSS
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}
// 通过ID获取内容的多密码模式
function checkWeeklyPasswordById(triggerElement) {
    var passwordsStr = triggerElement.getAttribute('data-week-passwords');
    var contentIdsStr = triggerElement.getAttribute('data-week-content-ids');
    
    if (!passwordsStr || !contentIdsStr) {
        alert("⚠️ 请设置 data-week-passwords 和 data-week-content-ids");
        return;
    }
    
    var passwords = passwordsStr.split(',');
    var contentIds = contentIdsStr.split(',');
    
    if (passwords.length !== contentIds.length) {
        alert("⚠️ 密码数量和内容ID数量不匹配");
        return;
    }
    
    var userPassword = prompt("🔐 输入密码：");
    if (userPassword === null) return;
    
    for (var i = 0; i < passwords.length; i++) {
        if (userPassword === passwords[i].trim()) {
            var contentElement = document.getElementById(contentIds[i].trim());
            var title = triggerElement.getAttribute('data-week-title') || "彩蛋等级 " + (i + 1);
            var contentHtml = contentElement ? contentElement.innerHTML : "<p>内容加载失败</p>";
            showEggModal(title, contentHtml);
            return;
        }
    }
    alert("❌ 密码错误，再试试？");
}