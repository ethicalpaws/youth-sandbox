<!-- 隐藏的内容模板 -->
<div style="display: none;">
    <div id="egg-content-1">
        <p>🔰 <strong>初级彩蛋</strong><br>URLDNS链的基础分析</p>
        <p>📌 调用链：</p>
        <pre style="background: #2a2a2a; padding: 10px; border-radius: 6px; overflow-x: auto;">
HashMap.readObject()
  → hash()
    → URL.hashCode()
      → URLStreamHandler.hashCode()
        → getHostAddress()
          → InetAddress.getByName() → DNS查询
        </pre>
        <p>⚠️ <strong>踩坑记录</strong>：JDK版本必须用 8u121 以下</p>
    </div>
    
    <div id="egg-content-2">
        <p>🔥 <strong>深度彩蛋</strong><br>CC1链的完整调试过程</p>
        <p>📌 Transformer 链调用顺序：</p>
        <pre style="background: #2a2a2a; padding: 10px; border-radius: 6px; overflow-x: auto;">
ConstantTransformer(Runtime.class)
  → InvokerTransformer("getMethod", ...)
    → InvokerTransformer("invoke", ...)
      → InvokerTransformer("exec", ...)
        </pre>
        <p>💡 关键点：LazyMap.get() 触发 transform 链</p>
    </div>
</div>


<div class="egg-trigger"
     data-week-passwords="urlnds2024,cc1chain"
     data-week-content-ids="egg-content-1,egg-content-2"
     data-week-title="🎁 本周学习彩蛋"
     onclick="checkWeeklyPasswordById(this)"
     style="cursor: pointer; display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 8px 20px; border-radius: 25px; margin: 10px 0;">
    🔐 多级彩蛋入口
</div>
<p style="font-size: 12px; color: #666; margin-top: 8px;">
</p>