// 更完整的首页动态推送逻辑
(async function() {
    const container = document.getElementById('latest-posts');
    if (!container) return;
    
    container.innerHTML = '<div class="loading-spinner" style="margin: 0 auto;"></div>';
    
    try {
        const response = await fetch('/updates.json');
        const data = await response.json();
        const posts = data.posts.slice(0, 5);
        
        if (posts.length === 0) {
            container.innerHTML = '<div>✨ 暂无动态，快去写第一篇吧！</div>';
            return;
        }
        
        const html = posts.map(post => `
            <div class="post-card" style="background: var(--md-surface-2); border-radius: 12px; padding: 1rem; margin: 1rem 0; border-left: 4px solid #7c3aed;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem">
                    <span style="font-size: 0.8rem; color: #7c3aed">📅 ${post.date}</span>
                    ${post.categories ? `<span style="font-size: 0.7rem; background: #7c3aed20; padding: 0.2rem 0.6rem; border-radius: 20px">${post.categories[0]}</span>` : ''}
                </div>
                <h3 style="margin: 0"><a href="${post.url}" style="text-decoration: none; color: var(--md-typeset-color)">${post.title}</a></h3>
                <div style="font-size: 0.9rem; color: var(--md-default-fg-color--light); margin-top: 0.5rem">${post.excerpt || '点击查看详情 →'}</div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    } catch (err) {
        console.error('加载动态失败:', err);
        container.innerHTML = '<div>⚠️ 加载失败，请刷新重试</div>';
    }
})();