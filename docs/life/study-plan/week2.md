---
week: 2
start_date: "2026-05-16"
end_date: "2026-05-22"
status: "已完成"
theme: "掌握反序列化核心利用链，补齐Web关键漏洞原理，完成ISCC初赛复盘并开始实战挖洞"
keywords:
  - Gadget库对比
  - CC6链
  - CC5链
  - CC7链
  - 文件上传
  - 命令注入
  - ISCC复盘
  - WebGoat反序列化
  - EDUSRC
---

# 🌟 Week 2 学习计划

> **时间**：2026年5月16日 - 5月22日  
> **阶段目标**：掌握反序列化核心利用链，补齐Web关键漏洞原理，完成ISCC初赛复盘并开始实战挖洞

<link rel="stylesheet" href="../../asserts/css/weekly.css">
<script src="../../asserts/js/weekly.js" defer></script>

---

## 📊 本周打卡表

<div class="weekly-card">
  <div class="weekly-header">
    <span>📅 Week 2 进度</span>
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
| **周六 5/16** | Gadget库对比笔记 | <input type="checkbox" class="task-check" data-task="gadget-compare"> |
| | CC6链调用链路图 | <input type="checkbox" class="task-check" data-task="cc6-chain"> |
| | ISCC第一道题解题记录 | <input type="checkbox" class="task-check" data-task="iscc-1"> |
| **周日 5/17** | CC6链手工POC + ysoserial验证 | <input type="checkbox" class="task-check" data-task="cc6-poc"> |
| | 数据链路层实验 | <input type="checkbox" class="task-check" data-task="cmd-inject"> |
| | ISCC第一道题Writeup | <input type="checkbox" class="task-check" data-task="iscc-writeup-1"> |
| **周一 5/18** | CC5链分析 | <input type="checkbox" class="task-check" data-task="cc5-chain"> |
| | 文件上传原理 + Upload-Labs前5关 | <input type="checkbox" class="task-check" data-task="upload-1"> |
| | ISCC第二道题解题记录 | <input type="checkbox" class="task-check" data-task="iscc-2"> |
| | CC1 vs CC6对比表（草稿） | <input type="checkbox" class="task-check" data-task="compare-draft"> |
| **周二 5/19** | CC7链分析 | <input type="checkbox" class="task-check" data-task="cc7-chain"> |
| | 文件上传进阶（Upload-Labs 6-10关） | <input type="checkbox" class="task-check" data-task="upload-2"> |
| | ISCC第二道题Writeup | <input type="checkbox" class="task-check" data-task="iscc-writeup-2"> |
| | CC1 vs CC6对比表（完成） | <input type="checkbox" class="task-check" data-task="compare-final"> |
| **周三 5/20** | CC5/6/7三条链总结对比表 | <input type="checkbox" class="task-check" data-task="chains-summary"> |
| | ISCC剩余Web题复盘 + Writeup | <input type="checkbox" class="task-check" data-task="iscc-remaining"> |
| | WebGoat反序列化模块通关 | <input type="checkbox" class="task-check" data-task="webgoat"> |
| **周四 5/21** | CC链手写POC + 调用链默写 | <input type="checkbox" class="task-check" data-task="review-poc"> |
| | 命令注入 + 文件上传混合作战 | <input type="checkbox" class="task-check" data-task="web-mix"> |
| | EDUSRC挖洞测试 | <input type="checkbox" class="task-check" data-task="src-edu"> |
| **周五 5/22** | 查漏补缺 | <input type="checkbox" class="task-check" data-task="fill-gaps"> |
| | 本周复盘 + 整理仓库 | <input type="checkbox" class="task-check" data-task="weekly-review"> |
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
| Java反序列化 | Gadget库对比、CC6/CC5/CC7链、CC1 vs CC6对比、WebGoat反序列化模块 | 🔴 高 |
| ISCC复盘 | 3-4道Web题目复现 + Writeup撰写 | 🔴 高 |
| Web漏洞 | 命令注入 + 文件上传（原理 + 靶场） | 🟡 中 |
| 实战尝试 | EDUSRC挖洞练手（Web方向） | 🟢 低 |

---

## 🗓️ 每日安排

### 第1天（周六 / 5.16）

| 时间段 | 任务 |
|:------:|------|
| 上午 | Gadget库对比：整理CC链 vs Spring链 vs Jackson链的差异 |
| 下午 | CC6链入门：理解 HashMap + TiedMapEntry + LazyMap 调用链 |
| 晚上 | ISCC复盘：挑选第一道Web题，记录解题过程 |

**产出：**
- [ ] Gadget库对比笔记（表格形式）
- [ ] CC6链调用链路图

---

### 第2天（周日 / 5.17）

| 时间段 | 任务 |
|:------:|------|
| 上午 | CC6链调试：手工POC + ysoserial 验证 |
| 下午 | 数据链路层实验 |
| 晚上 | ISCC复盘：完成第一道题的Writeup |

**产出：**
- [ ] CC6链POC代码
- [ ] 数据链路层实验报告

---

### 第3天（周一 / 5.18）

| 时间段 | 任务 |
|:------:|------|
| 上午 | CC5链分析：BadAttributeValueExpException 触发链 |
| 下午 | 文件上传原理学习：Upload-Labs 前5关 |
| 晚上 | ISCC复盘：挑选第二道Web题，记录解题过程 |
| 零散时间 | CC1 vs CC6对比：整理入口、依赖、JDK限制差异表 |

**产出：**
- [ ] CC5链笔记（与CC1/CC6的对比）
- [ ] 文件上传笔记 + 绕过技巧总结
- [ ] CC1 vs CC6对比表（草稿）

---

### 第4天（周二 / 5.19）

| 时间段 | 任务 |
|:------:|------|
| 上午 | CC7链分析：Hashtable 触发链 |
| 下午 | 文件上传进阶：Upload-Labs 第6-10关（图片马、竞争上传） |
| 晚上 | ISCC复盘：完成第二道题的Writeup |
| 零散时间 | CC1 vs CC6对比：完成对比表 + 调用链差异分析 |

**产出：**
- [ ] CC7链笔记 + 与CC5/CC6的对比表
- [ ] 文件上传通关记录
- [ ] CC1 vs CC6完整对比文档

---

### 第5天（周三 / 5.20）

| 时间段 | 任务 |
|:------:|------|
| 上午 | CC5/CC6/CC7总结：整理三条链的异同、适用版本、触发点 |
| 下午 | ISCC复盘：集中完成剩余Web题的复盘和Writeup |
| 晚上 | WebGoat反序列化模块：实战验证CC链知识 |

**产出：**
- [ ] CC5/6/7对比总结表
- [ ] ISCC Web题Writeup（3-4篇）
- [ ] WebGoat反序列化模块通关截图

---

### 第6天（周四 / 5.21）

| 时间段 | 任务 |
|:------:|------|
| 上午 | CC链综合复习：手写POC + 默写调用链 |
| 下午 | Web漏洞巩固：命令注入 + 文件上传混合作战 |
| 晚上 | EDUSRC挖洞：尝试测试1-2个目标 |

**产出：**
- [ ] 手写POC通过
- [ ] SRC漏洞记录（如有发现）

---

### 第7天（周五 / 5.22）

| 时间段 | 任务 |
|:------:|------|
| 上午 | 查漏补缺：补本周未完成的任务 |
| 下午 | 本周复盘：整理笔记、代码、Writeup到Git仓库 |
| 晚上 | 下周计划：根据本周完成情况微调 |

**产出：**
- [ ] 本周学习周报
- [ ] 下周计划草稿

---

## 📊 本周产出清单

| 类别 | 产出 | 状态 |
|------|------|:----:|
| Java反序列化 | Gadget库对比笔记 | ⬜ |
| | CC6链POC + 调用链图 | ⬜ |
| | CC5链笔记 | ⬜ |
| | CC7链笔记 | ⬜ |
| | CC1/5/6/7对比表 | ⬜ |
| | 数据链路层实验报告 | ⬜ |
| | WebGoat反序列化模块通关 | ⬜ |
| ISCC复盘 | 3-4篇Web题Writeup | ⬜ |
| Web漏洞 | 命令注入笔记 + 靶场截图 | ⬜ |
| | 文件上传笔记 + 靶场通关 | ⬜ |
| 实战尝试 | EDUSRC测试记录（可选） | ⬜ |
| 周报 | Week 2 复盘周报 | ⬜ |

---

## 🎯 里程碑检查点

| 时间 | 检查点 | 通过标准 |
|:----:|--------|----------|
| 周二 | 反序列化进度 | 能画出CC6调用链图 + CC1 vs CC6对比表 |
| 周三 | WebGoat验证 | WebGoat反序列化模块通关 |
| 周四 | Web漏洞进度 | 能手工绕过Upload-Labs前10关 |
| 周五 | ISCC复盘进度 | 至少3篇Writeup完成 |

---

## ⚠️ 注意事项

- **CC1 vs CC6对比**：本周重点，能帮你理清两条最核心链的差异
- **WebGoat反序列化模块**：做完CC链后立刻实战验证，效果更好
- **CC5/CC7链**：使用频率低于CC6，以理解为主，不需花太多时间调试
- **ISCC复盘**：Writeup要写得清晰（题目 → 思路 → 解题过程 → flag），方便以后复习

---

<div class="weekly-tips">
  <h4>💪 本周寄语</h4>
  <p>反序列化是Java安全的深水区，CC链是敲门砖。一周啃下三条链，你已经超越了大多数人。</p>
  <p>—— 加油，⛽️ 青春沙盒主</p>
</div>