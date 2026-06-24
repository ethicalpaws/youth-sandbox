---
week: 1
start_date: "2026-05-09"
end_date: "2026-05-15"
status: "已完成"
theme: "掌握核心Web漏洞原理，入门Java反序列化，完成CC1链与URLDNS链分析"
keywords:
  - URLDNS链
  - CC1链
  - 越权
  - SSRF
  - XXE
  - 反序列化基础
  - Gadget链
---
# 🌟 Week 1 学习计划

> **时间**：2026年5月9日 - 5月15日  
> **阶段目标**：掌握核心Web漏洞原理，入门Java反序列化，完成CC1链与URLDNS链分析

<link rel="stylesheet" href="../../asserts/css/weekly.css">
<script src="../../asserts/js/weekly.js" defer></script>

---

## 📊 本周打卡表

<div class="weekly-card">
  <div class="weekly-header">
    <span>📅 Week 1 进度</span>
    <span id="progressPercent">0</span><span>%</span>
  </div>
  <div class="progress-bar">
    <div class="progress-fill" id="progressFill" style="width: 0%"></div>
  </div>
  <div class="weekly-stats">
    <div>✅ 已完成: <span id="completedCount">0</span></div>
    <div>📋 总任务: <span id="totalCount">0</span></div>
  </div>
</div>

| 日期 | 任务 | 完成 |
|:----:|------|:----:|
| **周六 5/9** | 搭建Java反序列化调试环境 | <input type="checkbox" class="task-check" data-task="env-setup"> |
| | URLDNS链分析 + 调用链绘制 | <input type="checkbox" class="task-check" data-task="urldns"> |
| | 越权漏洞原理 + 靶场练习 | <input type="checkbox" class="task-check" data-task="idor"> |
| **周日 5/10** | CC1链分析（LazyMap版） | <input type="checkbox" class="task-check" data-task="cc1-lazy"> |
| | CC1链调试 + POC验证 | <input type="checkbox" class="task-check" data-task="cc1-poc"> |
| | SSRF原理 + 绕过技巧学习 | <input type="checkbox" class="task-check" data-task="ssrf"> |
| **周一 5/11** | CC1链TransformedMap版对比 | <input type="checkbox" class="task-check" data-task="cc1-transformed"> |
| | XXE原理 + 有回显/无回显利用 | <input type="checkbox" class="task-check" data-task="xxe"> |
| | ISCC热身赛题目浏览 | <input type="checkbox" class="task-check" data-task="iscc-warmup"> |
| **周二 5/12** | 反序列化基础理论复习 | <input type="checkbox" class="task-check" data-task="serialize-basic"> |
| | CC1链与URLDNS链对比 | <input type="checkbox" class="task-check" data-task="chains-compare"> |
| | ISCC Web题第一道解题 | <input type="checkbox" class="task-check" data-task="iscc-1"> |
| **周三 5/13** | 各漏洞防御方案整理 | <input type="checkbox" class="task-check" data-task="defenses"> |
| | 反序列化Gadget链概念梳理 | <input type="checkbox" class="task-check" data-task="gadget-concept"> |
| | ISCC Web题第二道解题 | <input type="checkbox" class="task-check" data-task="iscc-2"> |
| **周四 5/14** | 第一周综合复习 | <input type="checkbox" class="task-check" data-task="review"> |
| | 完成第一周检测题 | <input type="checkbox" class="task-check" data-task="detection"> |
| | ISCC Web题第三道解题 | <input type="checkbox" class="task-check" data-task="iscc-3"> |
| **周五 5/15** | 查漏补缺 | <input type="checkbox" class="task-check" data-task="fill-gaps"> |
| | 本周复盘 + 整理笔记到仓库 | <input type="checkbox" class="task-check" data-task="weekly-review"> |
| | 下周计划草稿 | <input type="checkbox" class="task-check" data-task="next-plan"> |

<div class="weekly-summary">
  <h4>📝 周记</h4>
  <textarea id="weeklyNotes" rows="3" placeholder="记录本周的收获、卡点、碎碎念..."></textarea>
  <button id="saveWeeklyBtn" class="weekly-save">💾 保存周记</button>
</div>

---

## 📋 本周概览

| 维度 | 内容 | 优先级 |
|------|------|:------:|
| Java反序列化 | URLDNS链、CC1链（LazyMap + TransformedMap）、调试环境搭建 | 🔴 高 |
| Web漏洞 | SSRF、XXE、越权（IDOR） | 🔴 高 |
| 工具与实战 | Burp Suite使用、ISCC热身赛/初赛 | 🟡 中 |
| 基础知识 | 反序列化原理、Gadget链概念 | 🔴 高 |

---

## 🗓️ 每日安排

### 第1天（周六 / 5.9）

| 时间段 | 任务 |
|:------:|------|
| 上午 | 搭建Java反序列化调试环境（JDK + IDEA + ysoserial） |
| 下午 | URLDNS链分析：理解 HashMap + URL 调用链 |
| 晚上 | 越权漏洞原理学习 + Pikachu靶场练习 |

**产出：**
- [ ] 调试环境截图
- [ ] URLDNS调用链路图
- [ ] 越权漏洞笔记

---

### 第2天（周日 / 5.10）

| 时间段 | 任务 |
|:------:|------|
| 上午 | CC1链分析（LazyMap版）：理解 AnnotationInvocationHandler |
| 下午 | CC1链调试 + 手工POC验证 |
| 晚上 | SSRF原理学习 + 绕过技巧 + 靶场练习 |

**产出：**
- [ ] CC1链调用链路图
- [ ] CC1链POC代码
- [ ] SSRF笔记 + 绕过方法总结

---

### 第3天（周一 / 5.11）

| 时间段 | 任务 |
|:------:|------|
| 上午 | CC1链TransformedMap版分析（与LazyMap版对比） |
| 下午 | XXE原理学习 + 有回显/无回显（Blind XXE）利用 |
| 晚上 | ISCC热身赛题目浏览，熟悉比赛平台 |

**产出：**
- [ ] CC1两版对比笔记
- [ ] XXE笔记 + OAST平台使用记录

---

### 第4天（周二 / 5.12）

| 时间段 | 任务 |
|:------:|------|
| 上午 | 反序列化基础理论复习（readObject、serialVersionUID、transient） |
| 下午 | CC1链 vs URLDNS链对比（入口、触发条件、JDK限制） |
| 晚上 | ISCC初赛Web题第一道解题 |

**产出：**
- [ ] 反序列化基础笔记
- [ ] 两条链对比表
- [ ] ISCC第一道题解题记录

---

### 第5天（周三 / 5.13）

| 时间段 | 任务 |
|:------:|------|
| 上午 | 各漏洞防御方案整理（SSRF、XXE、越权、反序列化） |
| 下午 | 反序列化Gadget链概念梳理（Transformer、ChainedTransformer等） |
| 晚上 | ISCC初赛Web题第二道解题 |

**产出：**
- [ ] 防御方案速查表
- [ ] Gadget链概念笔记
- [ ] ISCC第二道题解题记录

---

### 第6天（周四 / 5.14）

| 时间段 | 任务 |
|:------:|------|
| 上午 | 第一周综合复习：默写调用链、手写POC |
| 下午 | 完成第一周检测题（自测打分） |
| 晚上 | ISCC初赛Web题第三道解题 |

**产出：**
- [ ] 检测题完成截图
- [ ] ISCC第三道题解题记录

---

### 第7天（周五 / 5.15）

| 时间段 | 任务 |
|:------:|------|
| 上午 | 查漏补缺：补本周未完成的任务 |
| 下午 | 本周复盘：整理笔记、代码到Git仓库 |
| 晚上 | 下周计划草稿（Week 2） |

**产出：**
- [ ] 本周学习周报
- [ ] 下周计划草稿

---

## 📊 本周产出清单

| 类别 | 产出 | 状态 |
|------|------|:----:|
| Java反序列化 | URLDNS调用链路图 | ⬜ |
| | CC1链调用链路图 + POC | ⬜ |
| | CC1两版对比笔记 | ⬜ |
| | 反序列化基础笔记 | ⬜ |
| | Gadget链概念笔记 | ⬜ |
| Web漏洞 | 越权漏洞笔记 | ⬜ |
| | SSRF笔记 + 绕过方法 | ⬜ |
| | XXE笔记（含Blind XXE） | ⬜ |
| | 防御方案速查表 | ⬜ |
| ISCC | 3道Web题解题记录 | ⬜ |
| 检测 | 第一周检测题完成 | ⬜ |
| 周报 | Week 1 复盘周报 | ⬜ |

---

## 🎯 里程碑检查点

| 时间 | 检查点 | 通过标准 |
|:----:|--------|----------|
| 周日 | CC1链进度 | 能画出CC1调用链图 + 手工POC验证通过 |
| 周二 | Web漏洞进度 | 能说出SSRF/XXE/越权的核心原理和绕过方法 |
| 周四 | ISCC进度 | 至少3道Web题有解题记录 |
| 周五 | 检测题 | 检测题得分 ≥ 70分 |

---

## ⚠️ 注意事项

- **调试环境**：JDK版本建议8u20以下（CC1链在高版本JDK下无法触发）
- **CC1链**：LazyMap版和TransformedMap版都要理解，面试常考
- **Blind XXE**：结合外部VPS或OAST平台（如Burp Collaborator）理解数据外带
- **ISCC**：重在参与，每道题都要写Writeup，方便复盘

---

<div class="weekly-tips">
  <h4>💪 本周寄语</h4>
  <p>反序列化是Java安全的深水区，CC1链是敲门砖。第一周啃下CC1，第二周才能冲刺CC5/6/7。</p>
  <p>—— 加油，⛽️ 青春沙盒主</p>
</div>