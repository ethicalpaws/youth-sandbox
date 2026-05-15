// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 给外部链接添加 target="_blank"
    document.querySelectorAll('.md-typeset a[href^="http"]').forEach(link => {
        if (!link.href.includes(location.hostname)) {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        }
    });
    
    // 控制台输出欢迎语
    console.log('%c🌱 欢迎来到青春沙盒', 'color: #7c3aed; font-size: 16px;');
    console.log('%c记录技术，也记录青春', 'color: #666; font-size: 12px;');
});

// 可选：添加回到顶部按钮的动画
window.addEventListener('scroll', function() {
    const backToTop = document.querySelector('.md-top');
    if (backToTop) {
        if (window.scrollY > 300) {
            backToTop.style.opacity = '1';
        } else {
            backToTop.style.opacity = '0';
        }
    }
});