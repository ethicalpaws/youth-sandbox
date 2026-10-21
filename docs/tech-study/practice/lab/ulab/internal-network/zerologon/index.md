---
title: ZeroLogon 靶场
description: ULab 内网 ZeroLogon 靶场：外网探测、域控识别、CVE-2020-1472 利用与域内凭据导出
tags: ['Lab', 'ULab', 'ZeroLogon', '域渗透', '内网渗透']
status: ✅
difficulty: 困难
platform: ULab
key_points: |
  1. nmap 探测存活主机与域控端口
  2. enum4linux-ng 收集域信息
  3. 利用 ZeroLogon 清空域控机器账户密码
  4. secretsdump 导出域管哈希并制作黄金票据
highlights: |
  - WMI 远程执行中文乱码通过 -codec gbk 解决
  - 域控接管后可进一步利用永恒之蓝横向
last_updated: 2026-10-21 21:57:29
---

# 🎯 靶场记录 · ZeroLogon 靶场

---

### 📋 靶场档案

| 属性 | 数值 |
|------|------|
| `靶场名称` | **ZeroLogon 靶场** |
| `平台` | ULab |
| `难度` | ⭐⭐⭐ |
| `状态` | ✅ **已攻略** |

### 🏆 战利品

| 奖励 | 数量 |
|------|------|
| `经验值` | **+50 XP** ✨ |
| `成就` | 困难猎手 🏅 |

---

### 📜 靶场描述

ULab 内网 ZeroLogon 靶场：外网探测、域控识别、CVE-2020-1472 利用与域内凭据导出

### ⚡ 渗透步骤

  1. nmap 探测存活主机与域控端口
  2. enum4linux-ng 收集域信息
  3. 利用 ZeroLogon 清空域控机器账户密码
  4. secretsdump 导出域管哈希并制作黄金票据

### 💡 关键点

  - WMI 远程执行中文乱码通过 -codec gbk 解决
  - 域控接管后可进一步利用永恒之蓝横向

---

### 🔗 关联档案

[📖 详细报告 →](zerologon.md)



---

<span style="animation: blink 1s step-end infinite; text-shadow: 0 0 5px #00cc66, 0 0 10px #009955;">🏴‍☠️</span> **TARGET COMPROMISED** · 2026-10-21

<style>
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
