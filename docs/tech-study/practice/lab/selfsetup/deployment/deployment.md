---
title: pfSense 防火墙部署
description: 在红日靶场环境中配置 pfSense WAN 接口规则，打通 DMZ 与外网访问
tags: [Lab, pfSense, 环境搭建, 防火墙]
status: 已完成
finish-date: 2026-10-07
difficulty: 中等
platform: 自建靶场
key_points: |
  1. 登录 pfSense Web 界面并配置 WAN 规则
  2. 放行 ICMP 与必要业务端口
  3. 验证各网段之间的连通性
highlights: |
  - 明确 WAN/LAN/DMZ 的边界与访问控制
  - 规则按最小放行原则配置
---

# 部署

## pfSense
>从 MONITOR 或 DC01 访问 pfSense Web 界面

**第一步：登录 pfSense Web 界面**

在 MONITOR 上打开浏览器，访问：

```text
https://10.10.30.1
```
- 用户名：admin

- 密码：之前修改过的密码

浏览器提示证书不受信任时，点击“高级” → “继续访问”。


**第二步：配置 WAN 接口规则**

进入 Firewall → Rules → WAN 标签。

*规则1：允许 ICMP*

点击 Add（向上箭头图标）：

| 字段 | 值 |
|------|-----|
| Action | Pass |
| Interface | WAN |
| Address Family | IPv4 |
| Protocol | ICMP |
| ICMP type | Echo request |
| Source | any |
| Destination | WAN address |
| Description | Allow ICMP for lab |

![](deployment/2026-10-07-18-04-38.png)

点击 Save。

*规则2：允许访问 DMZ Web*

再次点击 Add：


| 字段 | 值 |
|------|-----|
| Action | Pass |
| Interface | WAN |
| Protocol | TCP |
| Source | any |
| Destination | OPT1 subnets |
| Destination Port Range | 80 |
| Description | Allow Web to DMZ |

![](deployment/2026-10-07-18-13-49.png)
点击 Save

再次点击 Add：


| 字段 | 值 |
|------|-----|
| Action | Pass |
| Interface | WAN |
| Protocol | TCP |
| Source | any |
| Destination | OPT1 subnets |
| Destination Port Range | 8080 |
| Description | Allow Web to DMZ |

![](deployment/2026-10-07-18-16-46.png)
点击 Save

再次点击 Add：


| 字段 | 值 |
|------|-----|
| Action | Pass |
| Interface | WAN |
| Protocol | TCP |
| Source | any |
| Destination | OPT1 subnets |
| Destination Port Range | 443 |
| Description | Allow Web to DMZ |

![](deployment/2026-10-07-18-17-49.png)
点击 Save

*规则3：阻止 WAN 访问 LAN*

再次点击 Add：

| 字段 | 值 |
|------|-----|
| Action | Block |
| Interface | WAN |
| Protocol | any |
| Source | any |
| Destination | LAN net |
| Description | Block WAN to LAN |

![](deployment/2026-10-07-18-20-08.png)
点击 Save。

点击右上角 “Apply Changes”
![](deployment/2026-10-07-20-39-40.png)

**第三步：配置 DMZ 接口规则**

进入 Firewall → Rules → OPT1 标签。

*规则1：允许 DMZ 访问 LAN 数据库端口*

点击 Add：

| 字段 | 值 |
|------|-----|
| Action | Pass |
| Interface | OPT1 |
| Protocol | TCP |
| Source | OPT1 subnets |
| Destination | LAN subnets |
| Destination Port Range | 3306 |
| Description | Allow DB from DMZ |

![](deployment/2026-10-07-19-28-35.png)
点击 Save。

点击 Add：

| 字段 | 值 |
|------|-----|
| Action | Pass |
| Interface | OPT1 |
| Protocol | TCP |
| Source | OPT1 subnets |
| Destination | LAN subnets |
| Destination Port Range | 1433 |
| Description | Allow DB from DMZ |

![](deployment/2026-10-07-19-29-24.png)
点击 Save。

*规则2：阻止 DMZ 访问 LAN 其他端口*

再次点击 Add：

| 字段 | 值 |
|------|-----|
| Action | Block |
| Interface | OPT1 |
| Protocol | any |
| Source | OPT1 subnets |
| Destination | LAN subnets |
| Description | Block DMZ to LAN |

![](deployment/2026-10-07-19-31-28.png)
点击 Save。

*在 Block 规则上面，添加一条允许 DMZ 出站的规则：*

点击 Add：

| 字段 | 值 |
|------|-----|
| Action | Pass |
| Interface | OPT1 |
| Protocol | any |
| Source | OPT1 subnets |
| Destination | any |
| Description | Allow DMZ outbound |

![](deployment/2026-10-07-20-36-31.png)
点击 Save。

在 OPT1 规则最上面，加一条允许 DMZ 访问 pfSense 自身的规则：

点击 Add：

| 字段 | 值 |
|------|-----|
| Action | Pass |
| Interface | OPT1 |
| Protocol | any |
| Source | OPT1 subnets |
| Destination | This Firewall (self) |
| Description | Allow DMZ to pfSense |

![](deployment/2026-10-07-21-09-25.png)

| 字段 | 值 |
|------|-----|
| Action | Pass |
| Interface | OPT1 |
| Protocol | ICMP |
| Source | OPT1 subnets |
| Destination | LAN subnets |
| Description | Allow ICMP reply to LAN |

![](deployment/2026-10-07-21-14-49.png)
点击 “Apply Changes”。
![](deployment/2026-10-07-21-14-24.png)

**第四步：确认 LAN 规则**

进入 Firewall → Rules → LAN 标签。

LAN 默认应该已有一条规则：允许 LAN net 访问 any。如果没有，点击 Add 添加：

| 字段 | 值 |
|------|-----|
| Action | Pass |
| Interface | LAN |
| Protocol | any |
| Source | LAN subnets |
| Destination | any |
| Description | Default LAN allow |

点击 Save → Apply Changes。
![](deployment/2026-10-07-19-35-13.png)

**第五步：恢复包过滤**

在 pfSense 控制台输入 8（Shell），执行：
```bash
pfctl -e
```
或者在 Web 界面 Diagnostics → Command Prompt 中执行。
![](deployment/2026-10-07-19-37-31.png)

**第六步：验证隔离效果**

从 Kali 测试
```bash
ping 10.10.10.1     # WAN，应该通
ping 10.10.20.10    # DMZ，应该通
ping 10.10.30.10    # LAN，应该不通（被拦截）
curl http://10.10.20.10:8080   # Struts2，应该通
```


从 WEB01 测试
```bash
ping 10.10.20.1     # DMZ网关，通
ping 10.10.30.20    # FS01，1433端口应该通
ping 10.10.30.10    # DC01，应该不通
```


从 MONITOR 测试
```bash
ping 10.10.30.10    # DC01，通
ping 10.10.20.10    # DMZ，通
```

![](deployment/2026-10-07-19-43-10.png)