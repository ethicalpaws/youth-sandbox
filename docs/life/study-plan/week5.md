---
week: 5
start_date: "2026-06-08"
end_date: "2026-06-14"
status: "进行中"
theme: "期末考试冲刺 + 操作系统/计算机网络/密码学复习 + 域渗透基础预热"
keywords:
  - 操作系统
  - 计网
  - 密码学
  - 域渗透
---

# 🌟 Week 5 学习计划

> **时间**：2026年6月8日 - 6月14日  
> **阶段目标**：期末考试冲刺 + 操作系统/计算机网络/密码学复习 + 域渗透基础预热  
> **核心调整**：三门考试科目为主（60%），域渗透基础为辅（40%），实现“一箭双雕”

<link rel="stylesheet" href="/asserts/css/weekly.css">
<script src="/asserts/js/weekly.js" defer></script>

---

## 📊 本周打卡表

<div class="weekly-card">
  <div class="weekly-header">
    <span>📅 Week 5 进度</span>
    <span id="progressPercent">0</span><span>%</span>
  </div>
  <div class="progress-bar">
    <div class="progress-fill" id="progressFill" style="width: 0%"></div>
  </div>
  <div class="weekly-stats">
    <div>✅ 已完成: <span id="completedCount">0</span></div>
    <div>📋 总任务: <span id="totalCount">0</span></div>
  </div>
</div>

| 日期 | 任务 | 完成 |
|:----:|------|:----:|
| **周一 6.8** | 操作系统：进程管理（PCB、调度算法、进程状态） | <input type="checkbox" class="task-check" data-task="os-process"> |
| | 域渗透关联：lsass.exe进程、SYSTEM账户、进程注入基础 | <input type="checkbox" class="task-check" data-task="ad-process"> |
| | 计算机网络：OSI模型、TCP/IP分层 | <input type="checkbox" class="task-check" data-task="net-osi"> |
| **周二 6.9** | 操作系统：内存管理（分区、分页、分段、虚拟内存） | <input type="checkbox" class="task-check" data-task="os-memory"> |
| | 域渗透关联：LSASS内存、mimikatz原理、Token窃取基础 | <input type="checkbox" class="task-check" data-task="ad-memory"> |
| | 计算机网络：IP协议（子网划分、CIDR、NAT） | <input type="checkbox" class="task-check" data-task="net-ip"> |
| **周三 6.10** | 操作系统：文件系统（文件结构、目录、磁盘调度） | <input type="checkbox" class="task-check" data-task="os-filesystem"> |
| | 域渗透关联：NTFS权限、AD数据库(NTDS.dit) | <input type="checkbox" class="task-check" data-task="ad-ntfs"> |
| | 计算机网络：DNS协议（解析流程、记录类型） | <input type="checkbox" class="task-check" data-task="net-dns"> |
| **周四 6.11** | 密码学：对称加密（DES、AES、ECB/CBC模式） | <input type="checkbox" class="task-check" data-task="crypto-symmetric"> |
| | 域渗透关联：Kerberos加密类型、AES vs RC4 | <input type="checkbox" class="task-check" data-task="ad-kerberos-crypto"> |
| | 计算机网络：TCP/UDP（三次握手、四次挥手、流量控制） | <input type="checkbox" class="task-check" data-task="net-tcp"> |
| **周五 6.12** | 密码学：哈希函数（MD5、SHA、碰撞、盐） | <input type="checkbox" class="task-check" data-task="crypto-hash"> |
| | 域渗透关联：NTLM哈希格式、Pass-the-Hash原理 | <input type="checkbox" class="task-check" data-task="ad-pth"> |
| | 操作系统：死锁（必要条件、银行家算法） | <input type="checkbox" class="task-check" data-task="os-deadlock"> |
| **周六 6.13** | 密码学：RSA + 数字签名 + HMAC | <input type="checkbox" class="task-check" data-task="crypto-rsa"> |
| | 域渗透关联：Kerberos认证中的签名、票据加密 | <input type="checkbox" class="task-check" data-task="ad-sign"> |
| | 计算机网络：HTTP/HTTPS（TLS握手、证书） | <input type="checkbox" class="task-check" data-task="net-http"> |
| **周日 6.14** | 综合刷题：操作系统/网络/密码学历年卷 | <input type="checkbox" class="task-check" data-task="exam-review"> |
| | 域渗透预热：Windows安全模型（SID、Token、UAC） | <input type="checkbox" class="task-check" data-task="ad-security-model"> |
| | 整理笔记 + 考试准备 | <input type="checkbox" class="task-check" data-task="exam-prep"> |

<div class="weekly-summary">
  <h4>📝 周记</h4>
  <textarea id="weeklyNotes" rows="3" placeholder="记录本周的收获、卡点、碎碎念..."></textarea>
  <button id="saveWeeklyBtn" class="weekly-save">💾 保存周记</button>
</div>

---

## 📋 本周概览

| 维度 | 内容 | 优先级 |
|------|------|:------:|
| **期末考试冲刺** | 操作系统、计算机网络、现代密码学 | 🔴 高 |
| **域渗透预热** | Windows安全模型、LSASS、NTDS.dit、NTLM哈希、Kerberos加密 | 🟡 中 |
| **安全关联** | 将考试知识点与渗透场景关联（一箭双雕） | 🟢 低 |

---

## 🔗 考试知识点 ↔ 域渗透关联表（核心亮点）

| 考试科目 | 考试知识点 | 域渗透关联 | 渗透工具/场景 |
|----------|-----------|-----------|---------------|
| **操作系统** | 进程管理（PCB、进程状态） | lsass.exe是域认证核心进程，SYSTEM账户权限最高 | mimikatz、PsExec |
| | 内存管理（虚拟内存、内存布局） | LSASS内存中存放明文密码和哈希 | sekurlsa::logonpasswords |
| | 文件系统（NTFS权限） | AD数据库NTDS.dit存放所有域用户哈希 | secretsdump.py、ntdsutil |
| | 用户/组管理 | Domain Admins组、SID、Token | whoami /groups、mimikatz |
| **计算机网络** | DNS协议（解析流程） | 域控发现、SPN、DNS隧道 | nslookup、dnscat2 |
| | TCP/IP（端口、协议） | Kerberos(88)、LDAP(389)、SMB(445) | nmap、端口扫描 |
| | HTTP/HTTPS（TLS） | HTTPS流量解密、中间人攻击 | Burp Suite、mitmproxy |
| **现代密码学** | 对称加密（AES-CBC、IV） | Kerberos加密票据、Shiro550 | kerberos::golden |
| | 哈希函数（MD5、SHA） | NTLM哈希格式、LM/NTLMv1/v2 | hashcat、john |
| | RSA/数字签名/HMAC | Kerberos签名、JWT伪造、黄金票据 | ticketer.py、JWT_tool |

---

## 🗓️ 每日安排

### 第1天（周一 / 6.8）：进程管理 + OSI模型

| 时间段 | 任务 |
|:------:|------|
| 上午 | **操作系统**：进程管理（PCB、进程状态转换、调度算法） |
| 中午 | **域渗透关联**：lsass.exe进程、SYSTEM账户、进程注入基础 |
| 下午 | **计算机网络**：OSI七层模型、TCP/IP四层、网络设备 |
| 晚上 | 整理笔记 + 做课后习题 |

**产出：**
- [ ] 进程状态转换图
- [ ] lsass.exe进程笔记（关联mimikatz）
- [ ] OSI vs TCP/IP对比表

**域渗透要点：**
> `lsass.exe` 是Local Security Authority Subsystem Service，负责本地安全认证和域认证。mimikatz的`sekurlsa::logonpasswords`就是从LSASS进程中提取凭证。SYSTEM账户是Windows最高权限账户，`psexec -s`可以获取。

---

### 第2天（周二 / 6.9）：内存管理 + IP协议

| 时间段 | 任务 |
|:------:|------|
| 上午 | **操作系统**：内存管理（分区、分页、分段、虚拟内存、页面置换） |
| 中午 | **域渗透关联**：LSASS内存保护、mimikatz原理、Token窃取 |
| 下午 | **计算机网络**：IP协议（分类、子网划分、CIDR、NAT、IPv6） |
| 晚上 | 整理笔记 + 子网划分计算练习 |

**产出：**
- [ ] 虚拟内存地址转换图
- [ ] mimikatz原理笔记（Debug权限、内存读取）
- [ ] 子网划分练习

**域渗透要点：**
> mimikatz需要`SeDebugPrivilege`才能读取LSASS进程内存。Windows开启PPL（Protected Process Light）保护时会阻止mimikatz，需要特殊绕过。

---

### 第3天（周三 / 6.10）：文件系统 + DNS协议

| 时间段 | 任务 |
|:------:|------|
| 上午 | **操作系统**：文件系统（文件结构、目录、磁盘调度算法） |
| 中午 | **域渗透关联**：NTFS权限、AD数据库NTDS.dit、SYSVOL |
| 下午 | **计算机网络**：DNS协议（报文格式、解析流程、记录类型） |
| 晚上 | 整理笔记 + 磁盘调度算法对比 |

**产出：**
- [ ] 磁盘调度算法对比表
- [ ] NTDS.dit笔记（域哈希存储位置）
- [ ] DNS解析流程图

**域渗透要点：**
> `NTDS.dit`是Active Directory的数据库文件，存放所有域用户的NTLM哈希。攻击者获得域控权限后，可以用`ntdsutil`或`secretsdump.py`导出。`SYSVOL`共享存放域策略（GPO），可能泄露明文密码。

---

### 第4天（周四 / 6.11）：对称加密 + TCP协议

| 时间段 | 任务 |
|:------:|------|
| 上午 | **密码学**：对称加密（DES、AES结构、ECB/CBC模式、IV） |
| 中午 | **域渗透关联**：Kerberos加密类型（AES-256、RC4-HMAC） |
| 下午 | **计算机网络**：TCP/UDP（三次握手、四次挥手、流量控制、拥塞控制） |
| 晚上 | 整理笔记 + 画TCP状态图 |

**产出：**
- [ ] AES-CBC加解密流程图
- [ ] Kerberos加密类型对比表
- [ ] TCP三次握手/四次挥手状态图

**域渗透要点：**
> Kerberos协议支持多种加密类型：RC4-HMAC（可被破解）、AES-128-CTS-HMAC-SHA1-96、AES-256-CTS-HMAC-SHA1-96。高安全域环境禁用RC4，黄金票据需指定加密类型。

---

### 第5天（周五 / 6.12）：哈希函数 + 死锁

| 时间段 | 任务 |
|:------:|------|
| 上午 | **密码学**：哈希函数（MD5、SHA、碰撞、盐、彩虹表） |
| 中午 | **域渗透关联**：NTLM哈希格式、LM vs NTLM、Pass-the-Hash原理 |
| 下午 | **操作系统**：死锁（必要条件、银行家算法、死锁检测） |
| 晚上 | 整理笔记 + 银行家算法练习 |

**产出：**
- [ ] 哈希+盐存储笔记
- [ ] NTLM哈希格式说明
- [ ] Pass-the-Hash攻击流程图

**域渗透要点：**
> NTLM哈希格式：`用户名:RID:LM-Hash:NT-Hash:::`
> Pass-the-Hash攻击：攻击者不需要破解哈希，直接用NTLM哈希进行认证。mimikatz的`sekurlsa::pth`就是实现PtH。

---

### 第6天（周六 / 6.13）：RSA + HTTP/HTTPS

| 时间段 | 任务 |
|:------:|------|
| 上午 | **密码学**：RSA（公私钥生成、加解密、签名原理）+ HMAC + 数字证书 |
| 中午 | **域渗透关联**：Kerberos签名、PAC、黄金票据/白银票据原理 |
| 下午 | **计算机网络**：HTTP/HTTPS（请求响应结构、方法、状态码、TLS握手） |
| 晚上 | 整理笔记 + HTTP状态码记忆 |

**产出：**
- [ ] RSA加解密/签名流程图
- [ ] 黄金票据/白银票据原理笔记
- [ ] HTTP状态码分类表

**域渗透要点：**
> Kerberos票据中的PAC（Privilege Attribute Certificate）用域控的密钥签名。黄金票据就是伪造整个TGT（含PAC），白银票据伪造Service Ticket。

---

### 第7天（周日 / 6.14）：综合复习 + 域渗透预热

| 时间段 | 任务 |
|:------:|------|
| 上午 | 综合刷题：操作系统/计算机网络/密码学历年真题 |
| 下午 | **域渗透预热**：Windows安全模型（SID、Token、UAC、服务） |
| 晚上 | 整理错题本 + 考试准备 + 心态调整 |

**产出：**
- [ ] 三门课错题本
- [ ] Windows安全模型笔记（SID/Token/UAC）
- [ ] 高频考点总结

**域渗透要点：**
> SID（安全标识符）是用户/组的唯一标识，黄金票据需要域SID。Token（访问令牌）决定进程权限，Token窃取是提权常用手段。UAC（用户账户控制）需要绕过才能提权。

---

## 📊 本周产出清单

| 类别 | 产出 | 状态 |
|------|------|:----:|
| **操作系统** | 进程/内存/文件系统/死锁笔记 | ⬜ |
| | 进程状态转换图 | ⬜ |
| | 虚拟内存地址转换图 | ⬜ |
| **计算机网络** | OSI/TCP/IP对比表 | ⬜ |
| | DNS解析流程图 | ⬜ |
| | TCP三次握手/四次挥手状态图 | ⬜ |
| | HTTP状态码分类表 | ⬜ |
| **现代密码学** | 对称加密笔记（AES-CBC） | ⬜ |
| | 哈希+盐存储笔记 | ⬜ |
| | RSA加解密/签名流程图 | ⬜ |
| **域渗透预热** | lsass.exe与mimikatz原理 | ⬜ |
| | NTLM哈希格式与PtH | ⬜ |
| | NTDS.dit与AD数据库 | ⬜ |
| | Kerberos加密类型对比 | ⬜ |
| | 黄金票据/白银票据原理 | ⬜ |
| | Windows安全模型（SID/Token/UAC） | ⬜ |
| **考试准备** | 三门课错题本 | ⬜ |
| | 高频考点总结 | ⬜ |

---

## 🎯 里程碑检查点

| 时间 | 检查点 | 通过标准 |
|:----:|--------|----------|
| 周三 | 操作系统 | 能说出进程与线程的区别、分页与分段的区别 |
| 周五 | 计算机网络 | 能画出TCP三次握手图、DNS解析流程图 |
| 周六 | 现代密码学 | 能解释AES-CBC为什么需要IV、RSA签名流程 |
| 周日 | 域渗透预热 | 能说出lsass.exe的作用、NTLM哈希格式 |

---

## ⚠️ 注意事项

### 学习策略

- **二八原则**：60%时间复习考试高频考点，40%时间做域渗透关联
- **一箭双雕**：每学一个考试知识点，问自己“这个在域渗透哪里用到？”
- **两栏笔记法**：左边记考试重点，右边记渗透关联


> 请根据实际考试安排调整复习顺序

---


## 🚀 暑假衔接预告

**6月27日** 激活暑假10周计划

暑假将聚焦：

| 优先级 | 方向 | 说明 |
|:------:|------|------|
| P0 | 域渗透深化 | Kerberoasting、白银票据、ACL攻击、Impacket |
| P0 | Web进阶补齐 | SSTI、原型链污染完整学完 |
| P1 | Java安全延伸 | FastJSON复现、内存马原理 |
| P2 | 实战产出 | SRC挖第一个洞 |

---

<div class="weekly-tips">
  <h4>💪 本周寄语</h4>
  <p>你不是在“应付考试”，而是在“为暑假的域渗透深潜打基础”。</p>
  <p>每学一个知识点，多想一步：这个在渗透测试里怎么用？</p>
  <p>这门课考完，你的知识库第1层就完整了。</p>
  <p>冲刺两周，暑假起飞。期末加油！⛽️</p>
</div>