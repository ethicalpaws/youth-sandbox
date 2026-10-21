---
title: pfSense 防火墙部署
description: 在红日靶场环境中配置 pfSense WAN 接口规则，打通 DMZ 与外网访问
tags: ['Lab', 'pfSense', '环境搭建', '防火墙']
status: ✅
difficulty: 中等
platform: 自建靶场
key_points: |
  1. 登录 pfSense Web 界面并配置 WAN 规则
  2. 放行 ICMP 与必要业务端口
  3. 验证各网段之间的连通性
highlights: |
  - 明确 WAN/LAN/DMZ 的边界与访问控制
  - 规则按最小放行原则配置
last_updated: 2026-10-07 21:14:51
---

# 🎯 靶场记录 · pfSense 防火墙部署

---

### 📋 靶场档案

| 属性 | 数值 |
|------|------|
| `靶场名称` | **pfSense 防火墙部署** |
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

在红日靶场环境中配置 pfSense WAN 接口规则，打通 DMZ 与外网访问

### ⚡ 渗透步骤

  1. 登录 pfSense Web 界面并配置 WAN 规则
  2. 放行 ICMP 与必要业务端口
  3. 验证各网段之间的连通性

### 💡 关键点

  - 明确 WAN/LAN/DMZ 的边界与访问控制
  - 规则按最小放行原则配置

---

### 🔗 关联档案

[📖 详细报告 →](deployment.md)



---

<span style="animation: blink 1s step-end infinite; text-shadow: 0 0 5px #00cc66, 0 0 10px #009955;">🏴‍☠️</span> **TARGET COMPROMISED** · 2026-10-07

<style>
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
