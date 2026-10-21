---
title: Kerberos 与 NetNTLM 核心对比
description: Kerberos 与 NetNTLM 两种 Windows 认证协议在认证方式、密码传输、中间环节、主要漏洞、适用场景和安全性六个维度的核心对比
tags: [Kerberos, NetNTLM, 认证协议, 对比, 内网渗透, Windows安全]
status: 已完成
finish-date: 2026-09-26
difficulty: 简单
---

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

## 两种访问方式的差异

**场景 1：用 IP 访问（触发 NTLM）**

```cmd
net use \\192.168.162.20\C$ /user:LAB\Administrator Admin@123
```
- Windows 尝试解析 192.168.162.20。

- 无法生成 SPN（cifs/192.168.162.20 不是合法的 SPN）。

- 回退到 NTLM 认证。

- 在 Wireshark 里会看到 NTLMSSP 包。

**场景 2：用主机名访问（触发 Kerberos）**

```cmd
net use \\web01.lab.com\C$ /user:LAB\Administrator Admin@123
```
- Windows 通过 DNS 解析 web01.lab.com 得到 IP。

- 同时，它会构造 SPN：cifs/web01.lab.com。

- 向域控（KDC）请求该 SPN 的服务票据（ST）。

- 使用 Kerberos 认证。

- 在 Wireshark 里会看到 KRB5 包（TGS-REQ / TGS-REP）。
