---
title: Linux 提权概述
description: Linux 提权的基本分类与常见方法，包括系统配置、定时任务和 sudoers 等提权入口
tags: [linux, 提权, 权限提升]
status: 已完成
finish-date: 2026-10-16
difficulty: 简单
---

# Linux提权概述
## 概述
在渗透测试过程中，当我们拿一个webshell权限时，通常该webshell权限是一个普通用户权限，能做的事情相对较少。特别是Linux系统。所以我们需要使用普通帐户权限对目标主机进行提权，将普通用户权限提升为root权限，并将权限维持下来。

## 提权的方法
1、内核漏洞提权：内存溢出的方式。更多就是各种CVE漏洞。类似永恒之蓝/黑、各种土豆、脏牛漏洞（Linux）。

2、操作系统配置提权：注册表，Linux中定时任务，/etc/sudoer文件等。

3、第三方提权：Redis, MySQL, Docker等

## 