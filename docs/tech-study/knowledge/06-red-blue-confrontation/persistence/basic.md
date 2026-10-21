---
title: 持久化
description: 内网权限维持的常见手法分类：账号凭证、服务自启动、隧道、载荷与票据
tags: [持久化, 内网, 权限维持]
status: 已完成
finish-date: 2026-10-20
difficulty: 中等
---

# 持久化
## 账号与凭证类（最简单、最直接）

| 手法 | 说明 |
|------|------|
| SSH 公钥写入 | 把攻击机公钥写进 `authorized_keys`，免密登录 |
| 隐藏 root 用户 | `useradd -o -u 0` 创建 UID=0 的伪装用户，配密码 |
| 添加域管账户 | `net user xxx /add /domain` + 加入 Domain Admins |
| 明文密码留存 | 从配置/内存抓到密码后记录，作为备用登录 |

- 优点：简单、稳定、不依赖进程存活。
- 缺点：账号类容易被审计发现（尤其域管账户）；公钥被删即失效，需备用。

## 服务/自启动类（系统级常驻）
>核心是利用操作系统的服务管理机制，让木马或转发脚本开机自启、崩溃重启。

- **Linux（systemd）**
    
  | 手法 | 关键点 |
  |------|--------|
  | 自定义 .service 托管木马 | `Restart=always` + `RestartSec` + `enable` |
  | 自定义 .service 托管 socat 转发 | 通道持久化，`After=network.target` 保证网络就绪 |
  | 伪装命名 | `.sys-monitor`、`net-forward`、隐藏目录 + 点开头文件名 |


- **Windows**

  | 手法 | 关键点 |
  |------|--------|
  | 计划任务 | `schtasks /sc onstart`（开机）或 `onlogon`（登录），`/ru SYSTEM` 最高权限 |
  | 注册表 Run 键 | `HKLM\...\CurrentVersion\Run`，开机自启 |
  | 服务注册 | `sc create` 注册为 Windows 服务（需 System 权限） |
  | WMI 事件订阅 | 隐蔽性高，触发式执行 |

- 优点：重启自动恢复，是持久化的主力。
- 缺点：服务/任务名、路径易被查；需 Restart=always 抗查杀。

## 通道/隧道类（保证"路"一直在）
>持久化不只是"人在"，还要"路通"。攻击链大量依赖转发，所以通道也要持久化。

| 手法 | 说明 |
|------|------|
| socat + systemd | 端口转发常驻（Web1:22222→22、4444→Kali、2222→Web2:22） |
| frpc/frps + systemd | 反向代理隧道常驻，维持 socks5 |
| EW 级联 | 多级代理，但 EW 本身不持久，需配合服务托管 |
| SSH 动态代理 -D | 临时性强，重启即断，建议用 autossh 或 systemd 保活 |

- 关键设计：把转发命令写进脚本 → 脚本交给 systemd → enable 开机自启 + Restart=always 崩溃重启。

## 载荷/进程类

| 手法 | 说明 |
|------|------|
| MSF 木马 + 计划任务 | PC1/PC2 上传 exe，计划任务 `onstart`/`onlogon` 拉起 |
| 进程迁移 | `migrate -N explorer.exe`，注入常驻进程，抗进程查杀 |
| 反向木马替代 bind_tcp | `bind_tcp` 依赖攻击机主动连，跨多层代理不可靠；改反向回连跳板 |
| SUID shell | `cp /bin/bash; chmod u+s`，任何用户执行即 root |
| DLL 劫持 / 服务劫持 | 替换合法程序依赖的 DLL 或服务可执行文件 |

- 要点：载荷持久化要和"通道"配合——木马回连地址必须是跳板上已持久化的转发端口，否则通道断则载荷失联。

## 身份/票据类（域环境最高级）

| 手法 | 说明 |
|------|------|
| 黄金票据（Golden Ticket） | 用 krbtgt 哈希伪造任意 TGT，默认 10 年有效，不依赖进程存活 |
| 白银票据（Silver Ticket） | 用服务账户哈希伪造服务票据，范围小但更隐蔽 |
| DCSync 权限 | 给账户授 DCSync 权限，可反复导出哈希 |
| Skeleton Key | 给 DC 打万能密码补丁（内存级，重启失效） |

- 优点：不依赖进程/文件，靠密码学凭证长期有效，最难清除（黄金票据需重置 krbtgt 两次）。
- 缺点：域管审计、krbtgt 轮换会失效；Zerologon 后需注意恢复机器账户密码避免环境异常。