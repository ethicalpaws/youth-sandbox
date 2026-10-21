---
title: PTK 密钥传递
description: Kerberos 环境下 PTK 密钥传递的原理与利用思路
tags: [横向移动, ptk, kerberos]
status: 进行中
finish-date: 2026-10-05
difficulty: 困难
---

# PTK密钥 传递
概述
PTK（Pass The Key），中文称之为密钥传递攻击。在PTH密钥传递攻击中，使用的是NTLM-HASH值。PTK密钥传递攻击中使用的是AES256或者AES128的方式，PTK攻击只能用于Kerberos协议认证。

原理
在kerberos协议中 PTK攻击原理

AS-REQ（AS-requests）主要包含用户的身份信息，由客户端发送给AS的数据包，其中有几个重要信息：

PA-DATA pA-ENC-TIMESTAMP：使用用户的hash值或者AES key加密时间戳生成的key

PA-DATA pA-PAC-REQUEST：是否包含有pac（PAC 包含用户的SID、用户所在组等信息）

kdc-options：协商字段

cname：请求的用户名

realm：域名

sname：请求的服务名


————————————————
版权声明：本文为CSDN博主「Paxt0n」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/weixin_42248871/article/details/136253198