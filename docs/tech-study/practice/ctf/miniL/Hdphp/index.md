---
title: Hdphp
description: Nginx临时文件 + /proc/self/fd/ + 路径规范化LFI
tags: ['lfi', 'nginx', 'proc', 'file-inclusion', 'path-normalization']
status: ✅
difficulty: 困难
exp: 50
level: ⭐⭐⭐
achievement: 困难猎手
weakness: 本地文件包含
finish-date: 2026-05-26
---

# 🗡️ 狩猎记录 · Hdphp

---

### ⚔️ 目标档案

| 属性 | 数值 |
|------|------|
| `名称` | **Hdphp** |
| `弱点` | 本地文件包含 |
| `威胁等级` | ⭐⭐⭐ |
| `状态` | ✅ **已讨伐** |

### 🏆 战利品

| 奖励 | 数量 |
|------|------|
| `经验值` | **+50 XP** ✨ |
| `成就` | 困难猎手 🏅 |

---

### 📜 任务简报

Nginx临时文件 + /proc/self/fd/ + 路径规范化LFI

### ⚡ 攻略要点

1. Nginx大请求体触发临时文件
2. /proc/self/fd/ 软连接指向临时文件
3. 路径规范化绕过realpath检查
4. LFI包含临时文件实现RCE


---

### 🔗 关联档案

[📖 详细战报 →](Hdphp_wp.md)

---

<span style="animation: blink 1s step-end infinite; text-shadow: 0 0 5px #ff4500, 0 0 10px #ff0000;">🏴‍☠️</span> **QUEST COMPLETE** · 2026-05-26

<style>
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
