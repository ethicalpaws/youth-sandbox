---
title: 横向移动
description: 横向移动的常见入口分类：Web 漏洞、RDP、远控、凭据与错误配置
tags: [横向移动, 攻击面]
status: 已完成
finish-date: 2026-09-29
difficulty: 中等
---

# 横向移动
## 通过WEB漏洞（Web Exploitation）
**原理**：利用目标内网中其他Web服务器上存在的漏洞（如SQL注入、文件上传、反序列化、Struts2、Log4j等），直接获取该Web服务器的权限（通常是Webshell）。

**适用场景**：内网中有大量对外提供服务的Web应用，或者内网办公系统（OA、CMS）。

**实战工具**：Burp Suite、sqlmap、蚁剑/冰蝎（连接Webshell）、各类漏洞利用脚本（EXP）。

**渗透路径**：
```
从机器A（已攻陷的边界Web服务器）发现机器E（内网另一台Web服务器）存在漏洞 -> 利用漏洞拿下机器E的权限。
```

**优势**：往往能直接获得一个稳定的Shell，且不容易触发内网流量监控。

## 利用远程桌面（RDP）
>远程桌面协议(RDP)是一个多通道(multi-channel)的协议，让使用者(所在计算机称为用户端或'本地计算机')连上提供微软终端机服务的计算机(称为服务端或'远程计算机')


**原理**：利用 Windows 的远程桌面协议（RDP，默认端口3389）或其他远控软件，使用合法或窃取到的账号密码，直接图形化登录目标机器。

**远程桌面的利用条件**：

1. 开启了3389端口
2. 防火墙等安全设备没有禁止
3. 网络必须相通
4. 拥有账号和密码（或者Hash）（可以是本身的账号也可以是自己添加的）

**适用场景**：运维人员经常使用RDP管理内网服务器。

**渗透路径**

```
你拿下了机器B，在内存中抓到了管理员登录B时留下的凭据（Hash或明文） -> 用这个凭据去RDP连接机器E。
```

**示例**
    -  

**进阶技巧**
    
- **RDP会话劫持**：如果你有机器B的SYSTEM权限，且机器B上有管理员正通过RDP登录，你可以用 tscon 命令直接接管他的桌面，无需密码。

PtH to RDP：使用 Mimikatz 的 sekurlsa::pth 配合 mstsc，用Hash直接登录（需要目标开启Restricted Admin模式）。

## 利用远控工具
**todesk远控横向**

**gotohttp远控横向**

**rustdesk远控横向**

## 通过账号密码（Credential-Based）
原理：这是最常见、最基础的方式。当你通过抓取内存（Mimikatz）、导出SAM/NTDS、键盘记录、密码喷洒等方式获取了某个高权限账户的明文密码或NTLM Hash后，直接用这个凭据去登录内网的其他机器。

适用场景：内网存在密码复用（同一密码登录多台机器）或高权限账户在低安全机器上登录的情况。

实战工具：

SMB：psexec.py、crackmapexec（支持PtH）。

WMI：wmiexec.py、wmicexec。

WinRM：evil-winrm。

RDP：mstsc / xfreerdp。

渗透路径：你拿到了 LAB\Administrator 的 Hash -> 用 crackmapexec 扫描内网所有机器 -> 发现B、D、E、F都接受这个Hash -> 批量横向移动。

## 通过不安全的配置（Misconfiguration）
原理：利用内网中配置错误的服务或权限，绕过正常的认证机制。

常见场景：

SMB共享权限过松：任何人都能读写共享目录，甚至上传恶意文件（如 .lnk 文件、.scf 文件）诱导管理员点击。

SMB签名未开启：导致 NTLM 中继攻击（Relay） 成功。攻击者可以伪装成一台机器，把从A机器抓到的认证请求，直接中继给B机器，实现“借刀杀人”。

委派配置错误：Kerberos 委派（非约束性、约束性、基于资源的约束性）配置不当，允许普通用户冒充管理员访问其他服务。

ACL（访问控制列表）配置错误：普通用户对域管拥有 GenericAll 权限，可以直接修改域管密码。

实战工具：Responder + ntlmrelayx.py（中继）、BloodHound（分析ACL）、PowerView。

## 通过系统漏洞（System Exploitation）
原理：利用目标机器操作系统本身存在的远程代码执行漏洞（RCE），直接获取系统权限。

经典漏洞：

MS17-010（永恒之蓝）：利用 SMB 协议漏洞，直接拿下 Windows 机器（无需账号密码）。

CVE-2019-0708（BlueKeep）：RDP 远程代码执行漏洞。

CVE-2020-1472（ZeroLogon）：直接攻击域控，瞬间获取域管权限。

实战工具：Metasploit、POC 脚本。

渗透路径：你拿下机器A，扫描内网发现机器H是未打补丁的 Windows 2008 -> 使用 MS17-010 漏洞直接拿下机器H。