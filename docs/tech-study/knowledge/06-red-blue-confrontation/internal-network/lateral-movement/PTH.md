---
title: PTH 哈希传递
description: PTH 哈希传递原理、利用条件、批量碰撞与远程桌面利用
tags: [横向移动, pth, ntlm, 哈希传递]
status: 已完成
finish-date: 2026-10-05
difficulty: 中等
---

# PTH哈希传递

>PTH（pass the hash），中文称之为哈希传递攻击，在NTLM和Kerberos认证中，都需要使用用户的NTLM-Hash值进行加密认证，所以知道了对方用户的NTLM-Hash值之后就可以使用PTH进行认证。

>在域环境中，用户登录计算机时一般使用的都是域账户，大量计算机在安装时会使用相同的本地管理员账户和密码。

>如果计算机的本地管理员账户和密码也是相同的，故攻击者就可以使用哈希传递攻击这种方法登录内网中其他计算机。


## PTH原理
**NTLM认证中**

- response = NTProofStr+blob两部分组成的

- NTProofStr：NTLM-v2-hash值和challenge+blob进行HMAC-MD5加密

- NTLM-v2-hash：大写的用户名+域名编码成Unicode格式，然后和密码的NTLM-HASH值进行HMAC-MD5加密

- blob是由时间、目标信息、随机填充字符等生成

**kerberos认证中**

- AS-REQ（AS-requests）主要包含用户的身份信息，由客户端发送给AS的数据包，其中有几个重要信息：

  - PA-DATA pA-ENC-TIMESTAMP：使用用户的hash值或者AES key加密时间戳生成的key

  - PA-DATA pA-PAC-REQUEST：是否包含有pac（PAC 包含用户的SID、用户所在组等信息）

  - kdc-options：协商字段

  - cname：请求的用户名

  - realm：域名

  - sname：请求的服务名

## PTH的利用条件
1、有管理员的NTLM Hash值

2、目标机器开放了445端口

**不同用户下的PTH区别**

*本地账户传递*

administrator账户可以进行PTH传递，本地普通管理员只可以在Windows server 2003 、XP中进行PTH传递，本地普通用户不可以进行PTH传递。

*域内账户测试环境*

域内administrator和普通管理员可以进行PTH传递，域内普通用户不可以进行PTH传递（默认）。

## Hash值批量碰撞
内网中，系统在安装的时候，一般会采用统一的账户和密码，当我们获取到一台电脑的hash值之后，可以使用hash碰撞的方式，找出拥有相同账户密码的计算机。



## PTH认证CS上线
## 利用PTH进行远程桌面

开启远程桌面的命令
```
REG ADD "HKLM\System\CurrentControlSet\Control\Lsa" /v DisableRestrictedAdmin /t REG_DWORD /d 00000000 /f
```

Mimikatz命令
```
privilege::debug
sekurlsa::pth /user:用户名 /domain:域名或IP地址 /ntlm:hash值  "/run:mstsc.exe /restrictedadmin"
```


例如：
```
sekurlsa::pth /user:administrator /domain:192.168.110.10 /ntlm:db40247dab331ac57
```