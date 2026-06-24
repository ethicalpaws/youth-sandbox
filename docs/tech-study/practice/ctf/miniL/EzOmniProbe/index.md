---
title: EzOmniProbe
description: 竞态条件提权 + vm沙箱逃逸 + setuid/gconv提权
tags: ['race-condition', 'vm', 'sandbox-escape', 'setuid', 'gconv', 'privilege-escalation']
status: ✅
difficulty: 困难
exp: 50
level: ⭐⭐⭐
achievement: 困难猎手
weakness: 竞态条件 + 沙箱逃逸
finish-date: 2026-05-27
---

# 🗡️ 狩猎记录 · EzOmniProbe

---

### ⚔️ 目标档案

| 属性 | 数值 |
|------|------|
| `名称` | **EzOmniProbe** |
| `弱点` | 竞态条件 + 沙箱逃逸 |
| `威胁等级` | ⭐⭐⭐ |
| `状态` | ✅ **已讨伐** |

### 🏆 战利品

| 奖励 | 数量 |
|------|------|
| `经验值` | **+50 XP** ✨ |
| `成就` | 困难猎手 🏅 |

---

### 📜 任务简报

竞态条件提权 + vm沙箱逃逸 + setuid/gconv提权

### ⚡ 攻略要点

1. 竞态条件提权到admin
2. vm沙箱逃逸执行命令
3. setuid + gconv提权读取flag


---

### 🔗 关联档案

[📖 详细战报 →](EzOmniProbe_wp.md)

---

<span style="animation: blink 1s step-end infinite; text-shadow: 0 0 5px #ff4500, 0 0 10px #ff0000;">🏴‍☠️</span> **QUEST COMPLETE** · 2026-05-27

<style>
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
