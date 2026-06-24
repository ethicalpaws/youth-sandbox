---
title: Kerberos认证协议详解
description: Kerberos认证流程、TGT/ST/PAC、黄金票据/白银票据、Kerberoasting、AS-REP Roasting、NetNTLM对比
tags: [kerberos, authentication,黄金票据,白银票据,kerberoasting,域安全]
status: 已完成
finish-date: 2026-06-04
difficulty: 中等
---

# 身份验证方法
Windows 域环境中两大核心认证协议：Kerberos（当前默认主流）和 NetNTLM（旧版兼容）
##  Kerberos 认证协议详解
Kerberos 是一种票据 (Ticket) 认证协议，核心思想是：用户只要证明一次身份，获取一张“通行证”，后续就用这张通行证去兑换访问特定服务的“门票”，无需反复输密码
### 关键组件
- KDC：域控制器上的密钥分发中心
- krbtgt：KDC 账户，其哈希是域的最高机密
- TGT：登录时获得的身份票据
- ST：访问特定服务时获得的服务票据
- PAC：包含用户 SID 和组信息的权限数据
- Client：请求服务的用户。
- SPN：服务与主机名的绑定标识（例如 HTTP/webserver）。
### 认证三步骤
1. 第一步：获取 TGT (黄金票据)
   - 请求：用户发送加密的用户名 + 时间戳给 KDC，加密密钥由用户密码的 Hash 派生。
   - 验证：KDC 验证用户身份，如果正确：
     - 生成一个 TGT (Ticket Granting Ticket)，内容包含 Session Key 的副本。
     - TGT 加密：使用 KRBTGT 账户的密码 Hash 加密 TGT（用户无法查看或伪造）。
     - 下发：KDC 将 TGT 和一个 Session Key 发给用户。
   - 结果：用户内存中缓存了 TGT 和 Session Key。
2. 第二步：获取 TGS (服务票据)
   - 请求：用户要访问服务时，向 KDC 发送
     - 之前的 TGT。
     - 本次请求访问的 SPN。
     - 用 Session Key 加密的时间戳。
   - 验证：KDC 用 KRBTGT Hash 解密 TGT，从中取出 Session Key，再用它验证时间戳。
     - 生成 TGS，包含一个新的 Service Session Key。
     - TGS 加密：使用目标服务所有者账户的 Hash (例如 MSSQL_SVC 用户的密码 Hash) 加密 TGS。
     - 下发：KDC 将 TGS 和 Service Session Key 发给用户。
3. 第三步：访问服务
   - 请求：用户向目标服务器发送 TGS 和 Service Session Key 加密的验证信息。
   - 验证：服务使用自己账户的密码 Hash 解密 TGS，取出 Service Session Key，验证用户身份。
   - 结果：验证通过，建立连接。
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
### 攻击者视角的 Kerberos
#### 黄金票据
如果攻击者拿到 KRBTGT 账户的 Hash，就可以离线伪造任意用户（包括域管）的 TGT，进而访问任何服务。只要不改 KRBTGT 密码，后门永久有效。
**原理**
1. 获取 krbtgt 账户的哈希
2. 伪造任意用户的 TGT
3. 用伪造的 TGT 请求服务票据
4. 获得目标服务的访问权限
## 白银票据
如果攻击者拿到特定服务账户的 Hash（例如 MSSQL_SVC），可以伪造直接访问该服务的 TGS。比黄金票据更隐蔽，但权限仅限于该服务。
**原理**
1. 获取目标服务账户的哈希
2. 直接伪造访问该服务的 ST
3. 不需要与 KDC 通信
#### Kerberoasting：
任何域用户都可以向 KDC 请求指定 SPN 的 TGS。KDC 返回的 TGS 是用服务账户的密码 Hash 加密的。攻击者拿到 TGS 后可离线暴力破解，得出服务账户的明文密码。这是最常用的横向移动手段之一。
#### AS-REP Roasting：
如果用户账户设置了“不需要 Kerberos 预身份验证”，攻击者可以直接向 KDC 请求该用户的 TGT，KDC 会返回用该用户密码 Hash 加密的 TGT 部分内容，可离线破解。常用于无口令登录的账户。
## NetNTLM 认证协议详解
NetNTLM 是一种挑战-响应 (Challenge-Response) 协议，更古老，主要用于兼容旧系统或非域环境。
### 认证流程 (四步)
- 请求：客户端向服务器请求认证。
- 挑战：服务器生成一个随机数，作为“挑战”发给客户端。
- 响应：客户端用 NTLM Hash + 挑战进行运算，生成“响应”，发回给服务器。**注意**：NTLM Hash 和密码都不在网络中传输。
- 验证：服务器将 挑战 + 响应 转发给域控。域控用存储的用户 NTLM Hash 重新计算响应，进行比对。结果返回给服务器，再由服务器告知客户端。
### 攻击者视角的 NetNTLM
- 哈希传递攻击 (Pass-the-Hash, PtH)：因为认证只需要 NTLM Hash，不需要明文密码，攻击者拿到 Hash 后，可以直接用它模拟用户登录其他机器，无需破解。
- NTLM 中继攻击 (NTLM Relay)：攻击者作为“中间人”，截获客户端的 NetNTLM 认证信息（挑战+响应），然后将其中继到另一台服务器（如域控），从而实现横向移动或提权。使用 SMB 签名等机制可防御。
- NetNTLMv1/v2 破解：捕获到的 NetNTLMv1 或 v2 响应可离线暴力破解，得到明文密码。v1 弱很多，v2 依赖密码强度。
##  Kerberos vs. NetNTLM 核心对比
| 特性 | Kerberos（现代默认） | NetNTLM（遗留兼容） |
|------|----------------------|---------------------|
| 认证方式 | 票据（Ticket） | 挑战-响应（Challenge-Response） |
| 密码传输 | 不直接传输，使用派生密钥 | 不直接传输，使用 Hash + 挑战运算 |
| 中间环节 | 依赖 KDC 这个可信第三方 | 依赖域控做最终验证 |
| 主要漏洞 | 黄金票据、白银票据、Kerberoasting | 哈希传递、NTLM 中继、离线破解 |
| 适用场景 | 域内现代服务（SMB、HTTP 等） | 兼容旧系统、非域环境、部分特定服务 |
| 安全性 | 较高（但依赖 KRBTGT 安全） | 较低，易受中继和传递攻击 |

---


