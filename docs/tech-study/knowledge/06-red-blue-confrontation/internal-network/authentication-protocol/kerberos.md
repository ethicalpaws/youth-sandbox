---
title: Kerberos 协议与认证流程
description: Kerberos 协议的核心概念与角色组成、三步认证流程（AS/TGS/AP 交换）详解与数据包分析、票据缓存管理、抓包实验踩坑记录，以及 Kerberos 协议安全问题（PTH、黄金/白银票据、AS-REP/Kerberoasting、委派攻击）
tags: [Kerberos, 域认证, TGT, ST, AS-REQ, 黄金票据, 白银票据, Kerberoasting, 内网渗透]
status: 已完成
finish-date: 2026-09-26
difficulty: 困难
---

# kerberos

## Kerberos协议简介
>Kerberos 是一种网络认证协议，其设计目标是通过密钥系统为客户机 / 服务器应用程序提供强大的认证服务。该认证过程的实现不依赖于主机操作系统的认证，无需基于主机地址的信任，不要求网络上所有主机的物理安全，并假定网络上传送的数据包可以被任意地读取、修改和插入数据。在以上情况下， Kerberos 作为一种可信任的第三方认证服务，是通过传统的密码技术（如：共享密钥）执行认证服务的

- 定位：一种网络认证协议，由 MIT 开发，Windows 2000 之后将其作为域环境的默认认证协议。

- 核心特点：双向认证（客户端和服务器互相验证身份）、无明文密码传输、依赖可信第三方（KDC）。

- 为什么用它：解决了 NTLM 无法进行双向认证、容易遭受中继攻击的缺点，并且支持跨域信任。

## Kerberos协议角色组成
Kerberos 认证涉及三个核心角色：

- Client（客户端）：申请访问服务的用户或机器。

- Service（服务端）：提供资源（如文件共享、数据库、Web 服务）的服务器。

- KDC（Key Distribution Center，密钥分发中心）：域控（DC）的核心组件。它包含两个子服务：
  - AS（Authentication Server）：认证服务器，负责验证用户身份，发放 TGT（票据授权票据）。
  - TGS（Ticket Granting Server）：票据授权服务器，负责根据 TGT 发放访问具体服务的 ST（服务票据）。

## Kerberos协议认证流程（宏观三步）

- AS 交换：客户端向 AS 请求 TGT。AS 验证身份后，发放一个用用户密钥加密的 TGT。
- TGS 交换：客户端拿着 TGT 去向 TGS 申请访问某个特定服务的 ST。TGS 验证 TGT 后，发放一个用服务密钥加密的 ST。
- AP 交换：客户端拿着 ST 去访问真正的服务。服务用自己的密钥解密 ST，验证通过后提供服务。
### 流程图
```
用户登录
    │
    ▼
[AS_REQ] ──────► KDC ──────► [AS_REP] (返回TGT，用krbtgt加密)
    │
    ▼
[TGS_REQ] ─────► KDC ──────► [TGS_REP] (返回ST，用目标服务密码加密)
    │
    ▼
[AP_REQ] ──────► 目标服务器 ──────► [AP_REP] (访问成功)
```
## Kerberos认证-客户端和AS通信原理（AS-REQ / AS-REP）
- 客户端 -> AS (AS-REQ)：客户端发送自己的用户名、域名，以及一个用用户密码 Hash 加密的时间戳（预认证）。

- AS -> 客户端 (AS-REP)：AS 验证预认证通过后，返回的TGT包含两部分数据：

   ![](kerberos/2026-09-26-08-47-53.png)

- 客户端用自己的账号密码Hash解密TGT中用用户的Hash加密的部分，获得CT_SK，然后对AS发送的TGT进行重新封装生成新的TGT
  
   ![](kerberos/2026-09-26-09-09-55.png)
    
**渗透点：** 如果用户未开启“预认证”，攻击者可以伪造 AS-REQ 直接获取 AS-REP，离线破解用户密码（AS-REP Roasting）。

## Kerberos认证-客户端和TGS通信原理（TGS-REQ / TGS-REP）

- 客户端 -> TGS (TGS-REQ)：客户端发送 重新封装的 TGT

- TGS -> 客户端 (TGS-REP)：
  - TGS 用自己的密钥（krbtgt Hash）解密 客户端返回的TGT，获得CT_SK，
  - 使用CT_SK解密获得Name，IP，time并对这些数据进行比对校验
  - 验证通过后，生成一个 ST（服务票据） 和新的 Session Key（CS_SK）。
  ![](kerberos/2026-09-26-09-19-58.png) 

- 客户端对ST进行解密并重新封装
  - 使用CT_SK解密获取CS_SK
  - 使用CS_SK加密并重新封装ST
   
    ![](kerberos/2026-09-26-09-34-09.png)

**渗透点：** 如果攻击者拥有任意服务账户的 Hash，可以伪造 ST（白银票据）；如果拥有 krbtgt 的 Hash，可以伪造 TGT（黄金票据）。

## Kerberos认证-客户端和服务端通信原理（AP-REQ / AP-REP）

- 客户端 -> 服务端 (AP-REQ)：客户端把重新封装的 ST 发送给服务端。

- 服务端：用自己的 Hash 解密 ST，提取 Session Key，验证客户端身份。

双向认证：服务端返回一个用 Session Key 加密的时间戳，客户端解密验证，确保服务端也是合法的。

## Kerberos认证中的数据包分析
### 前置知识
1. port88：Kerberos认证端口
   是Kerberos协议使用的默认端口，KDC在该端口上监听等待客户端的认证请求
   传输Kerberos认证过程中的6个核心数据包（AS-REQ,AS-REP,TGS-REQ,TGS-REP,AP-REQ,AP-REP） 
2. port464：kpasswd服务端口
   是Kerberos的密码修改服务端口，是Kerberos环境中的客户端在使用，当用户要修改域密码时会连接KDC的该端口  
   传输修改密码的请求和响应的
3. 清除本地票据缓存（klist purge）
   1. 什么是票据：Kerberos 认证成功后，KDC 会发给客户端一个 TGT（Ticket Granting Ticket，票据授权票据）。这个票据会被缓存在本地内存中，下次访问域内服务时直接用，不需要再输入密码。
   2. 票据存在哪
      当前登录用户的票据，存储在 lsass.exe 进程的内存中
      相关命令
      - 查看当前票据：klist 
      - 只看TGT票据：klist tgt
      - 清除当前用户票据缓存：klist purge
      - 清除系统账户票据缓存：klist purge -li 0x37（需要管理员权限，0x3e7 是 SYSTEM 的 LogonId）
   3. 为什么要清除缓存
        | 场景 | 原因 |
        |------|------|
        | 抓包实验 | 如果不清除，票据还在缓存里，访问共享时会直接用旧票据，不会重新发起 Kerberos 认证流程，你就抓不到 AS-REQ/AS-REP 等包了 |
        | 权限切换 | 你用一个用户登录，想测试另一个用户的 Kerberos 流程，需要先清除旧用户的票据 |
        | 渗透测试（票据清理） | 拿到一个用户的票据后用完要清理，避免留下痕迹 |    

        ---   
    

   4. 清除前 vs 清除后
        | 状态 | 访问 `dir \\DC01\c$` 时的行为 |
        |------|-------------------------------|
        | 清除前（有票据缓存） | 直接用缓存的 Service Ticket 访问服务 → 抓不到 AS/TGS 包 |
        | 清除后（无票据缓存） | 重新发起完整 Kerberos 流程：AS-REQ → AS-REP → TGS-REQ → TGS-REP → AP-REQ → 抓包成功 |

        ---

4. 理解 C$ 是什么
   C是Windows自动创建的隐藏管理共享，末尾的$使其在常规网络浏览中不可见 
    | 共享 | 指向路径 | 用途 |
    |------|----------|------|
    | C$ | C:\ 根目录 | 远程管理系统盘 |
    | ADMIN$ | C:\Windows | 远程管理系统目录 |
    | IPC$ | 命名管道 | 进程间通信，不指向具体文件 |   

    >这些共享默认只有 Administrators 组成员能访问

    ---

5. Windows 为了性能和体验，会复用已有的连接。
   如果之前通过 `dir \\DC01.lab.com\c$ `已经成功访问过共享，系统会：
   - 记住这个连接
   - 哪怕你行 klist purge 清除了票据，连接仍然可以被复用
   - 下次访问时，不会重新发起完整的 Kerberos 认证
6. Kerberos vs NTLM
    | 场景 | 使用的认证协议 | 说明 |
    |------|----------------|------|
    | 用 IP 访问（`\\192.168.1.10\c$`） | NTLM | Kerberos 要求用域名，所以这不会触发 Kerberos 流程 |
    | 用域名访问（`\\DC01.corp.lab\c$`） | Kerberos | 这才是我们抓包想要的！ |

    > Kerberos 依赖域名。只有用 DNS 名称（如 主机名.域名）访问时，客户端才会向 KDC 请求票据，触发 AS-REQ/AS-REP/TGS-REQ/TGS-REP 流程

    ---

7. 当访问一个服务时，AP-REQ（服务请求）不是独立发送的，而是被封装在应用层协议内部
    | 访问的服务 | 使用的协议 | AP-REQ 藏在哪？ |
    |--------------|------------|-----------------|
    | 文件共享（`\\DC01\c$`） | SMB | SMB 协议的 Session Setup 请求内部 |
    | LDAP 查询 | LDAP | LDAP 的 Bind Request 内部 |
    | HTTP（IIS） | HTTP | HTTP 的 `Authorization: Negotiate` 头部 |
    | RDP（远程桌面） | RDP | RDP 的认证阶段 |

    ---

### 实验环境搭建
1. 环境拓扑
    | 角色 | 主机名 | IP地址 | 说明 |
    |------|--------|--------|------|
    | 域控/KDC | DC01.lab.com | 192.168.162.10 | 同时扮演 AS 和 TGS |
    | 客户端 | WIN10.lab.com | 192.168.162.20 | 域成员，进行认证测试 |
    | 目标服务 | DC01.lab.com | 192.168.162.10 | 提供共享服务（可选） |   

    ---


2. 抓包前准备
   1. 在DC01上执行命令`net share`,检查DC01是否开启C$共享服务
      ![](wireshark-analysiss/2026-06-04-05-07-31.png)
   2. 在web01上执行命令`klist purge`,清除票据缓存 
      ![](wireshark-analysiss/2026-06-04-05-35-40.png)
   3. 在web01上执行命令`net use * /delete`删除所有已建立的网络连接
      ![](wireshark-analysiss/2026-06-04-07-42-18.png) 
   4. 确保时间同步（Kerberos对时间敏感，默认允许偏差5分钟）
      在域控上执行命令`w32tm /query /status`检查时间服务状态
      ![](wireshark-analysiss/2026-06-04-05-20-13.png)
      在客户端执行命令`w32tm /resync /force`强制同步时间【注意要以管理员身份，普通用户没有权限强制同步系统时间】
      ![](wireshark-analysiss/2026-06-04-05-25-28.png) 

### 进行抓包
1. 设置wireshark捕获过滤器`(`并开始抓包
2. 以管理员身份运行【不然会拒绝访问】cmd然后执行命令`dir \\DC01.lab.com\c$`访问c$
3. 检查wireshark中的抓包记录，成功抓到域认证的数据包
   ![](wireshark-analysiss/2026-06-04-08-20-59.png)
4. 将过滤条件改为smb2就可以查找到AP-REQ和AP-REP
   ![](kerberos/2026-09-26-12-29-02.png)
5. 验证本地票据klist
   ![](wireshark-analysiss/2026-06-04-08-48-17.png) 

### AS-REQ和AS-REP数据包分析

![](wireshark-analysiss/2026-06-05-15-12-22.png)
**先看第61号包是KDC返回给客户端的KRB5KDCERR_PREAUTH_REQUIRED 错误包** 意思是需要预认证，如果没有这一步就说明该账户就是一个存在漏洞、可以进行 AS-REP Roasting 攻击的用户账户
1. AS-REQ
   ```
    Kerberos
    ├── as-req
        ├── pvno: 5
        ├── msg-type: AS-REQ (10)
        |—— padata
        |      |
        |      |—— PA-DATA pA-ENC-TIMESTAMP 使用用户的hash,或者AES key加密时间戳 生成value
        |      |__ PA-DATA pA-PAC-REQUEST，是否包含了PAC
        | 
        └── req-body
                ├── cname (客户端名称) ← 这里面是用户名
                │    └── realm: LAB.COM
                └── etype (加密类型列表) ← 客户端支持的加密算法
   ```
   ![](kerberos/2026-09-26-12-21-21.png)
2. AS-REP
   ```
    Kerberos
    ├── as-rep
        ├── pvno: 5
        ├── msg-type: AS-REP (11)
        ├── crealm: LAB.COM
        ├── cname ← 确认是你的用户名
        ├── ticket (这是最重要的！)
        │    ├── tkt-vno: 5
        │    ├── realm: LAB.COM
        │    ├── sname (服务名称)
        │    │    └── name-string: krbtgt ← 关键！这是 TGT 票据
        │    └── enc-part ← 加密的部分（用 krbtgt 的 Hash 加密的）
        └── enc-part ← 这个是用用户的密码 Hash 加密的，包含 Session Key
   ``` 

   ![](kerberos/2026-09-26-12-22-04.png)
   sname:krbtgt证明该包返回的是TGT票据

### TGS-REQ和TGS-REP数据包分析
1. TGS-REQ
   ```
    Kerberos
    ├── tgs-req
        ├── pvno: 5
        ├── msg-type: TGS-REQ (12)
        └── req-body
                ├── sname (你想要访问的服务)
                │    └── name-string: cifs ← 文件共享服务！
                │         └── DC01.lab.com ← 你要访问的目标
                └── etype
   ``` 

   ![](kerberos/2026-09-26-12-23-11.png)
   sname: cifs/DC01.lab.com 说明在请求访问域控的文件共享服务

2. TGS-REP
   ```
    Kerberos
    ├── tgs-rep
        ├── pvno: 5
        ├── msg-type: TGS-REP (13)
        ├── ticket
        │    ├── sname
        │    │    └── name-string: cifs ← 这是服务票据
        │    │         └── DC01.lab.com
        │    └── enc-part ← 用目标服务（DC01）的密码 Hash 加密
        └── enc-part ← 用 TGT 中的 Session Key（CT-SK） 加密
   ``` 

   ![](kerberos/2026-09-26-12-24-21.png)
   sname: cifs/DC01.lab.com 证明了这个包返回的就是 ST 服务票据，用来访问指定的目标服务

### AP-REQ和AP-REP数据包分析

1. AP-REQ
   ```
    SMB2 (Server Message Block Protocol Version 2)
    └── SMB2 Header
        └── Command: SMB2_COM_SESSION_SETUP (1)
                └── Session Setup Request
                    └── Security Buffer
                        └── GSS-API
                            └── OID: 1.2.840.113554.1.2.2 (Kerberos 5)
                                    └── Kerberos Ticket
                                        └── ap-req ← 这就是要找的
   ``` 

   ![](kerberos/2026-09-26-12-29-49.png)
2. AP-REP
   服务端发送给客户端的信息，包含了客户端验证服务端的信息 
   ![](wireshark-analysiss/2026-06-04-09-20-18.png) 
3. PAC藏在AP-REP和TGS-REP的ticket中的enc-part部分，由于wireshark无法解密所有只能看到占位符看不到具体内容
   ![](wireshark-analysiss/2026-06-04-09-31-30.png) 

### 踩坑记录
1. 刚开始抓包一直抓不到域认证数据包
   1. 先查看自己是不是域成员
   2. 在检查DNS解析是否正确
      ![](wireshark-analysiss/2026-06-04-05-51-09.png)
      发现DNS 响应里出现了两条记录：
      - 192.168.162.10（IPv4）
      - fd15:4ba5:...（IPv6）
      在 Windows / Kerberos 的行为逻辑中，IPv6 优先级高于 IPv4
   3. 在web01中禁用ipv6【仅限于实验环境，生成环境不用这样做】
      ![](wireshark-analysiss/2026-06-04-05-53-55.png)
      然后重启web01

## Kerberos协议安全问题（内网渗透的核心战场）
>Kerberos 虽然比 NTLM 安全，但配置不当或设计缺陷会导致极其严重的攻击：

### AS-REQ（客户端向 AS 请求 TGT）
**攻击手法**：**PTH（Pass-the-Hash，哈希传递）、域内用户枚举、密码喷洒**

**原理解析**：

- **PTH**：因为 AS-REQ 中包含了用用户 Hash 加密的时间戳。如果你有用户的 NTLM Hash，就可以直接构造这个请求，无需明文密码。
- **用户枚举**：Kerberos 协议有一个特性，当请求的用户不存在时，AS 会返回一个错误码；而用户存在但密码错误时，返回的是另一个错误码。攻击者通过发送大量请求，可以精确枚举出域内所有存在的用户名。
- **密码喷洒**：利用枚举出的用户名，用同一个弱密码（如 `Password123`）去尝试登录所有用户。因为 Kerberos 预认证有次数限制，密码喷洒比暴力破解更隐蔽，不易触发账户锁定。

### AS-REP（AS 返回 TGT）
**攻击手法**：**Golden Ticket（黄金票据）、Roasting（烘焙攻击）**

**原理解析**：

- **Golden Ticket**：AS-REP 中的 TGT 是用 **krbtgt 账户的 Hash** 加密的。如果你拿到了 krbtgt 的 Hash，你就可以伪造任意用户的 TGT（黄金票据），获得域内最高权限。
- **Roasting**：这里特指 **AS-REP Roasting**。如果某个用户没有开启“预认证”，攻击者可以伪造 AS-REQ 直接请求 AS-REP。AS-REP 中有一部分数据是用**用户密码 Hash** 加密的，攻击者可以导出这部分数据离线破解用户密码。


### TGS-REP（TGS 返回 ST）
**攻击手法**：**SILVER TICKET（白银票据）、Kerberoasting（Kerberos 烘焙）**

**原理解析**：

- **Silver Ticket**：TGS-REP 中的 ST 是用**目标服务账户的 Hash** 加密的。如果你拿到了某个服务账户（比如 `MSSQLSvc` 或 `HTTP`）的 Hash，你就可以伪造 ST（白银票据），直接访问该服务，而无需与 KDC 通信。
- **Kerberoasting**：攻击者请求一个服务账户（通常是 SQL Server、IIS 等）的 ST。ST 是用服务账户的 Hash 加密的。攻击者拿到 ST 后，可以离线暴力破解服务账户的密码。因为服务账户的密码通常很少更换，且复杂度较低，这是内网渗透中最常用的提权手法之一。

### Kerberos扩展协议（PAC、S4U）
**攻击手法**：**委派攻击、Kerberos bronze bit**

**原理解析**：

- **委派攻击（Delegation）**：微软为了支持多层应用，扩展了 S4U 协议。如果配置不当（如非约束性委派、约束性委派、基于资源的约束性委派），攻击者可以冒充高权限用户（如域管）去访问其他服务。
- **Kerberos bronze bit**：这是一个具体的漏洞（CVE-2020-17049），利用了 Kerberos 委派中的缺陷，可以绕过某些限制，实现权限提升。







