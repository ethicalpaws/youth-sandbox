<h1 class="terminal-text">青春沙盒</h1>

<p class="terminal-text">这里是 **ethicalpaws** 的数字花园，记录我的安全学习与青春轨迹。</p>

> **沙盒**：一个安全、隔离的运行环境，可以自由尝试，不怕犯错。  
> **青春**：一段同样可以大胆探索、试错成长的时光。



- 🔒 **技术笔记**：Web漏洞、Java安全、网络攻击、CTF等知识沉淀
- 🌱 **青春记录**：每周计划、随笔日记、成就时刻、复盘反思
- 🔔 **动态推送**：学习路上的高光与突破

---

## 🔔 最新动态

<div id="latest-posts" style="margin: 2rem 0">
  <div style="text-align: center; color: var(--md-default-fg-color--light)">
    ⏳ 加载中...
  </div>
</div>

<script>
fetch('/youth-sandbox/updates.json')
  .then(res => res.json())
  .then(data => {
    const posts = data.posts.slice(0, 5);
    const html = posts.map(post => `
      <div style="background: var(--md-surface-2); border-radius: 12px; padding: 1rem; margin: 1rem 0; border-left: 4px solid #7c3aed;">
        <div style="font-size: 0.8rem; color: #7c3aed; margin-bottom: 0.25rem">📅 ${post.date}</div>
        <h3 style="margin: 0"><a href="${post.url}" style="text-decoration: none">${post.title}</a></h3>
        <div style="font-size: 0.9rem; color: var(--md-default-fg-color--light); margin-top: 0.5rem">${post.excerpt || ''}</div>
      </div>
    `).join('');
    document.getElementById('latest-posts').innerHTML = html;
  })
  .catch(() => {
    document.getElementById('latest-posts').innerHTML = '<div>✨ 暂无动态，快去写第一篇吧！</div>';
  });
</script>

---

## 📂 快速入口

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0">
  <a href="tech-study/" style="text-align: center; padding: 1.5rem; background: var(--md-surface-2); border-radius: 12px; text-decoration: none">
    <div style="font-size: 2rem">📚</div>
    <div style="font-weight: bold">技术笔记</div>
    <div style="font-size: 0.8rem">安全知识沉淀</div>
  </a>
  <a href="life/" style="text-align: center; padding: 1.5rem; background: var(--md-surface-2); border-radius: 12px; text-decoration: none">
    <div style="font-size: 2rem">🌱</div>
    <div style="font-weight: bold">青春记录</div>
    <div style="font-size: 0.8rem">计划·日记·成就</div>
  </a>
  <a href="updates/" style="text-align: center; padding: 1.5rem; background: var(--md-surface-2); border-radius: 12px; text-decoration: none">
    <div style="font-size: 2rem">🔔</div>
    <div style="font-weight: bold">动态推送</div>
    <div style="font-size: 0.8rem">学习里程碑</div>
  </a>
  <a href="spiritual/" style="text-align: center; padding: 1.5rem; background: var(--md-surface-2); border-radius: 12px; text-decoration: none">
    <div style="font-size: 2rem">🔋</div>
    <div style="font-weight: bold">精神食粮</div>
    <div style="font-size: 0.8rem">音乐·照片·句子</div>
  </a>
  <a href="bridge/" style="text-align: center; padding: 1.5rem; background: var(--md-surface-2); border-radius: 12px; text-decoration: none">
    <div style="font-size: 2rem">🌉</div>
    <div style="font-weight: bold">修桥工程</div>
    <div style="font-size: 0.8rem">体系·锚点·光年</div>
  </a>
</div>


