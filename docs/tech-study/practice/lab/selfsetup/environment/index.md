---
title: 靶场环境部署
description: 基于 VMware 与 pfSense 搭建红日靶场网络环境，配置多网段、Windows/Linux 主机与域环境
tags: ['Lab', 'VMware', '环境搭建', '域环境', 'pfSense']
status: ✅
difficulty: 中等
platform: 自建靶场
key_points: |
  1. 创建 VMnet2/3/4 仅主机网络并关闭 DHCP
  2. 配置 pfSense 与各主机网卡
  3. 部署 DC01、FS01、WS01、MONITOR、WEB01
  4. 预埋 DCSync ACL 与 SQL Server 环境
highlights: |
  - 三个网段分别对应攻击网、DMZ 与内网
  - 手动指定 IP，避免地址漂移
last_updated: 2026-10-07 19:47:16
---

# 🎯 靶场记录 · 靶场环境部署

---

### 📋 靶场档案

| 属性 | 数值 |
|------|------|
| `靶场名称` | **靶场环境部署** |
| `平台` | 自建靶场 |
| `难度` | ⭐⭐ |
| `状态` | ✅ **已攻略** |

### 🏆 战利品

| 奖励 | 数量 |
|------|------|
| `经验值` | **+20 XP** ✨ |
| `成就` | 中等猎手 🏅 |

---

### 📜 靶场描述

基于 VMware 与 pfSense 搭建红日靶场网络环境，配置多网段、Windows/Linux 主机与域环境

### ⚡ 渗透步骤

  1. 创建 VMnet2/3/4 仅主机网络并关闭 DHCP
  2. 配置 pfSense 与各主机网卡
  3. 部署 DC01、FS01、WS01、MONITOR、WEB01
  4. 预埋 DCSync ACL 与 SQL Server 环境

### 💡 关键点

  - 三个网段分别对应攻击网、DMZ 与内网
  - 手动指定 IP，避免地址漂移

---

### 🔗 关联档案

[📖 详细报告 →](environment.md)



---

<span style="animation: blink 1s step-end infinite; text-shadow: 0 0 5px #00cc66, 0 0 10px #009955;">🏴‍☠️</span> **TARGET COMPROMISED** · 2026-10-07

<style>
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
