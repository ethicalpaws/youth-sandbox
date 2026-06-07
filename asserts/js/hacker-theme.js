// ============================================
// 黑客帝国数字雨 + 极客增强版（无弹窗/无负载面板）
// 包含：数字雨、鼠标光晕、按键音效、拖尾残影
// ============================================

(function() {
  // 检查是否为 role-panel 页面
  function isRolePanelPage() {
    if (document.body && document.body.classList.contains('role-panel-page')) {
      return true;
    }
    if (window.location.pathname.includes('role-panel')) {
      return true;
    }
    return false;
  }
  
  if (isRolePanelPage()) {
    console.log('[Matrix] Role-panel page detected, skipping effects');
    return;
  }
  
  // ============================================
  // 1. 黑客帝国数字雨（Canvas 实现）
  // ============================================
  function initMatrixRain() {
    if (document.querySelector('.matrix-rain-canvas')) return;
    
    const canvas = document.createElement('canvas');
    canvas.className = 'matrix-rain-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.zIndex = '-1';
    canvas.style.pointerEvents = 'none';
    document.body.insertBefore(canvas, document.body.firstChild);
    
    let ctx = canvas.getContext('2d');
    let width, height;
    let drops = [];
    
    // 字符集 + 彩色字符概率
    const chars = "01";
    const colors = ['#33ff33', '#66ff66', '#88ff88', '#44ff44'];
    const specialColors = ['#ff4444', '#33ccff', '#cc33ff']; // 红、蓝、紫
    
    const fontSize = 18;
    
    function getRandomChar() {
      return chars[Math.floor(Math.random() * chars.length)];
    }
    
    function getRandomColor() {
      // 10% 概率出现特殊颜色
      if (Math.random() < 0.1) {
        return specialColors[Math.floor(Math.random() * specialColors.length)];
      }
      return colors[Math.floor(Math.random() * colors.length)];
    }
    
    function init() {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
      
      ctx.font = `bold ${fontSize}px 'Courier New', monospace`;
      
      const columns = Math.ceil(width / fontSize);
      drops = [];
      for (let i = 0; i < columns; i++) {
        drops[i] = Math.random() * -height;
      }
    }
    
    function drawRain() {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, width, height);
      
      ctx.font = `bold ${fontSize}px 'Courier New', monospace`;
      
      const columns = drops.length;
      for (let i = 0; i < columns; i++) {
        const char = getRandomChar();
        ctx.fillStyle = getRandomColor();
        
        const x = i * fontSize;
        const y = drops[i] * fontSize;
        
        ctx.fillText(char, x, y);
        
        if (y > height && Math.random() > 0.975) {
          drops[i] = 0;
        }
        
        drops[i] += 0.5 + Math.random() * 0.7;
      }
      
      requestAnimationFrame(drawRain);
    }
    
    window.addEventListener('resize', () => { init(); });
    init();
    drawRain();
  }
  
  // ============================================
  // 2. 鼠标跟随光晕
  // ============================================
  function initMouseGlow() {
    if (document.querySelector('.mouse-glow')) return;
    
    const glow = document.createElement('div');
    glow.className = 'mouse-glow';
    glow.style.position = 'fixed';
    glow.style.width = '200px';
    glow.style.height = '200px';
    glow.style.background = 'radial-gradient(circle, rgba(0, 255, 65, 0.12) 0%, transparent 70%)';
    glow.style.borderRadius = '50%';
    glow.style.pointerEvents = 'none';
    glow.style.zIndex = '9997';
    glow.style.transform = 'translate(-50%, -50%)';
    glow.style.transition = 'all 0.05s ease';
    document.body.appendChild(glow);
    
    document.addEventListener('mousemove', (e) => {
      glow.style.left = e.clientX + 'px';
      glow.style.top = e.clientY + 'px';
    });
  }
  
  // ============================================
  // 3. 窗口拖尾残影效果
  // ============================================
  function initMouseTrail() {
    const trailCount = 8;
    let trails = [];
    
    for (let i = 0; i < trailCount; i++) {
      const trail = document.createElement('div');
      trail.style.position = 'fixed';
      trail.style.width = '4px';
      trail.style.height = '4px';
      trail.style.backgroundColor = '#33ff33';
      trail.style.borderRadius = '50%';
      trail.style.pointerEvents = 'none';
      trail.style.zIndex = '9996';
      trail.style.opacity = '0';
      trail.style.transition = 'opacity 0.2s ease';
      document.body.appendChild(trail);
      trails.push(trail);
    }
    
    let positions = [];
    
    document.addEventListener('mousemove', (e) => {
      positions.unshift({ x: e.clientX, y: e.clientY });
      if (positions.length > trailCount) positions.pop();
      
      for (let i = 0; i < trails.length; i++) {
        if (positions[i]) {
          const opacity = 0.3 - (i * 0.03);
          trails[i].style.left = positions[i].x - 2 + 'px';
          trails[i].style.top = positions[i].y - 2 + 'px';
          trails[i].style.opacity = Math.max(0, opacity);
          trails[i].style.backgroundColor = `rgba(51, 255, 51, ${opacity})`;
        }
      }
    });
  }
  
  // ============================================
  // 4. 按键音效（需要音频文件，静默失败）
  // ============================================
  function initClickSound() {
    let clickSound = null;
    try {
      clickSound = new Audio('/youth-sandbox/asserts/sounds/click.mp3');
      clickSound.volume = 0.15;
    } catch(e) { console.log('Audio not supported'); }
    
    document.addEventListener('click', () => {
      if (clickSound) {
        clickSound.currentTime = 0;
        clickSound.play().catch(e => console.log('autoplay blocked'));
      }
    });
  }
  
  // ============================================
  // 5. 控制台彩蛋
  // ============================================
  function printConsoleWelcome() {
    console.log("%c\n┌─────────────────────────────────────────┐\n│  ✨ SYSTEM ACCESS GRANTED ✨           │\n│  🧠 WELCOME TO ETHICALPAWS DIGITAL GARDEN │\n│  🔐 SECURITY LEVEL: MAXIMUM              │\n│  💀 HACK THE PLANET                       │\n└─────────────────────────────────────────┘\n", "color: #00ff41; font-family: monospace; font-size: 12px");
    console.log("%c💡 Tip: Try typing 'sudo make me a sandwich'", "color: #66ff66");
    
    setInterval(() => {
      const mem = performance.memory ? (performance.memory.usedJSHeapSize / 1048576).toFixed(1) : '?';
      console.log(`%c⏱️ ${new Date().toLocaleTimeString()} | MEM: ${mem}MB | STATUS: MONITORING`, "color: #33ff33; font-family: monospace");
    }, 30000);
  }
  
  // ============================================
  // 初始化所有效果
  // ============================================
  function init() {
    if (isRolePanelPage()) return;
    
    initMatrixRain();
    initMouseGlow();
    initMouseTrail();        // 拖尾残影
    initClickSound();        // 按键音效（可选，无音频文件时静默失败）
    printConsoleWelcome();
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();