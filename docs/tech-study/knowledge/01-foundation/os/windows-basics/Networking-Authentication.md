---
title: Windows网络与认证
description: NTLM认证流程、Kerberos认证流程、凭据存储位置
tags: [windows, ntlm, kerberos, 认证, 域安全]
status: 已完成
finish-date: 2026-06-01
difficulty: 中等
---

# 网络与认证
## 网络相关组件
**核心协议栈**：TCP/IP、UDP、NetBIOS、SMB（445端口）
**名字解析方式**：
- DNS（Domain Name System）：域名→IP
- NetBIOS（137/138/139端口）：计算机名→IP（旧）
- LLMNR（链路本地多播名称解析）：局域网内名字解析
- NBNS（NetBIOS名称服务）：同上

## 本地认证（NTLM）
**NTLM认证流程（简化）**：
```
用户输入用户名+密码
|
系统将密码转换成NTLM哈希
|
客户端向服务器发送用户名
|
服务器回复一个8字节随机数（Challenge）
|
客户端用NTLM哈希加密Challenge，返回Response
|
服务器验证Response是否正确
```
**核心**：服务器验证时，需要该用户的NTLM哈希。所以拿到哈希就能冒充用户，不需要知道明文密码
## 域认证（Kerberos）
**Kerberos核心组件**

| 组件 | 作用 |
|------|------|
| AS（Authentication Service） | 认证用户，颁发 TGT |
| KDC（Key Distribution Center） | AS + TGS 合称 |
| TGS（Ticket Granting Service） | 发放服务票据 |
| TGT（Ticket Granting Ticket） | 证明用户已认证 |
| 服务票据 | 用来访问具体服务（如文件服务器） |

---

**Kerberos流程（简化）**
```
1. 用户 → AS：发送用户名，请求TGT
2. AS → 用户：返回TGT（用krbtgt哈希加密）
3. 用户 → TGS：发送TGT + 想访问的服务名
4. TGS → 用户：返回服务票据（用目标服务的哈希加密）
5. 用户 → 目标服务器：发送服务票据
6. 目标服务器验证票据，允许/拒绝访问
```
**关键**：krbtgt是KDC自己的账号，用来加密所有TGT。如果拿到krbtgt哈希，可以伪造任何用户的TGT（黄金票据）
## 凭据存储位置

| 类型 | 存储位置 | 是否加密 |
|------|----------|----------|
| 本地用户哈希 | SAM 文件（`C:\Windows\System32\config\SAM`） | 是（但可破解） |
| 缓存域登录 | `C:\Windows\System32\config\SECURITY` | 是 |
| LSASS 内存中的明文字段 | 内存中 | 否（运行时明文） |
| DPAPI 保护的凭据 | `AppData\Roaming\Microsoft\Credentials` | 是（但可用用户密码解密） |
| 域内所有用户 | NTDS.dit（域控上） | 是 |

---
