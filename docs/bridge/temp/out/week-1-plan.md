---
week: 1
start_date: "2026-06-29"
end_date: "2026-07-05"
status: "进行中"
theme: "启航 · Java安全（FastJSON + 内存马入门）"
keywords:
  - FastJSON
  - 内存马
  - 望闻问切
  - JNDI
---

# 🌟 Week 1 学习计划

> **时间**：2026-06-29 - 2026-07-05  
> **阶段目标**：完成 FastJSON 漏洞复现与分析，入门内存马，理解"望闻问切"框架  
> **核心调整**：第1周启航，建立节奏感

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
    <div>📋 总任务: <span id="totalCount">7</span></div>
  </div>
</div>

| 日期 | 任务 | 完成 |
|:----:|------|:----:|
| **周一 6.29** | FastJSON 环境搭建，1.2.24 RCE 复现。建立"望闻问切"框架雏形，分析调用链 | <input type="checkbox" class="task-check" data-task="w1d1-1"> |
| | 完成 POC 代码编写与调试 | <input type="checkbox" class="task-check" data-task="w1d1-2"> |
| **周二 6.30** | 1.2.47 漏洞复现，TemplatesImpl 链分析 | <input type="checkbox" class="task-check" data-task="w1d2-1"> |
| | 整理漏洞利用链笔记 | <input type="checkbox" class="task-check" data-task="w1d2-2"> |
| **周三 7.1** | 1.2.68 绕过分析，三版本演化脉络图绘制 | <input type="checkbox" class="task-check" data-task="w1d3-1"> |
| | 版本对比笔记整理 | <input type="checkbox" class="task-check" data-task="w1d3-2"> |
| **周四 7.2** | 复盘日。知识库目录规范定稿 | <input type="checkbox" class="task-check" data-task="w1d4-1"> |
| | 封装"望闻问切"五步模板 | <input type="checkbox" class="task-check" data-task="w1d4-2"> |
| **周五 7.3** | Servlet 内存马入门 + 注入 Demo | <input type="checkbox" class="task-check" data-task="w1d5-1"> |
| | 理解内存马原理 | <input type="checkbox" class="task-check" data-task="w1d5-2"> |
| **周六 7.4** | Filter 型内存马 + 与 Servlet 型对比 | <input type="checkbox" class="task-check" data-task="w1d6-1"> |
| | 两种内存马对比笔记 | <input type="checkbox" class="task-check" data-task="w1d6-2"> |
| **周日 7.5** | 收尾。内存马检测、第一轮抽象文档撰写 | <input type="checkbox" class="task-check" data-task="w1d7-1"> |
| | 第1周简报撰写 | <input type="checkbox" class="task-check" data-task="w1d7-2"> |

<div class="weekly-summary">
  <h4>📝 周记</h4>
  <textarea id="weeklyNotes" rows="3" placeholder="记录本周的收获、卡点、碎碎念..."></textarea>
  <button id="saveWeeklyBtn" class="weekly-save">💾 保存周记</button>
</div>

---

## 📋 本周概览

| 维度 | 内容 | 优先级 |
|------|------|:------:|
| 技术 | FastJSON 1.2.24/47/68 漏洞复现与分析 | 🔴 高 |
| 技术 | 内存马（Servlet/Filter）入门 | 🔴 高 |
| 方法论 | "望闻问切"框架初建 | 🟡 中 |
| 工程 | 知识库目录规范定稿 | 🟡 中 |

---

## 🗓️ 每日安排

### 第1天（周一 / 6.29）：FastJSON 1.2.24 RCE 复现

| 时间段 | 任务 |
|:------:|------|
| 上午 | 搭建 FastJSON 1.2.24 测试环境，引入依赖 |
| 下午 | 分析漏洞原理，编写 POC，复现 RCE |
| 晚上 | 建立"望闻问切"框架雏形，记录调用链分析 |

**产出：**
- [ ] FastJSON 1.2.24 测试环境搭建完成
- [ ] POC 代码及复现结果
- [ ] "望闻问切"框架雏形文档

---

### 第2天（周二 / 6.30）：1.2.47 漏洞复现 + TemplatesImpl 链

| 时间段 | 任务 |
|:------:|------|
| 上午 | FastJSON 1.2.47 环境搭建 |
| 下午 | TemplatesImpl 链深入分析 |
| 晚上 | 整理漏洞利用链笔记 |

**产出：**
- [ ] 1.2.47 POC 复现完成
- [ ] TemplatesImpl 调用链笔记

---

### 第3天（周三 / 7.1）：1.2.68 绕过 + 版本演化

| 时间段 | 任务 |
|:------:|------|
| 上午 | 1.2.68 绕过分析 |
| 下午 | 绘制三版本演化脉络图 |
| 晚上 | 版本对比笔记整理 |

**产出：**
- [ ] 1.2.68 绕过原理理解
- [ ] FastJSON 版本演化脉络图

---

### 第4天（周四 / 7.2）：复盘日 + 框架封装

| 时间段 | 任务 |
|:------:|------|
| 上午 | 知识库目录规范定稿 |
| 下午 | 封装"望闻问切"五步模板 |
| 晚上 | 本周技术复盘 |

**产出：**
- [ ] 知识库目录规范文档
- [ ] "望闻问切"五步模板

---

### 第5天（周五 / 7.3）：Servlet 内存马入门

| 时间段 | 任务 |
|:------:|------|
| 上午 | 内存马概念与原理学习 |
| 下午 | Servlet 内存马注入 Demo |
| 晚上 | 理解内存马优缺点 |

**产出：**
- [ ] Servlet 内存马 Demo
- [ ] 内存马原理笔记

---

### 第6天（周六 / 7.4）：Filter 型内存马

| 时间段 | 任务 |
|:------:|------|
| 上午 | Filter 型内存马原理 |
| 下午 | Filter 与 Servlet 型对比 |
| 晚上 | 两种内存马对比笔记 |

**产出：**
- [ ] Filter 内存马 Demo
- [ ] 对比分析笔记

---

### 第7天（周日 / 7.5）：收尾 + 第1周简报

| 时间段 | 任务 |
|:------:|------|
| 上午 | 内存马检测方法学习 |
| 下午 | 第一轮抽象文档撰写 |
| 晚上 | 第1周简报撰写 |

**产出：**
- [ ] 内存马检测笔记
- [ ] 第1周简报

---

## 📊 本周产出清单

| 类别 | 产出 | 状态 |
|------|------|:----:|
| **漏洞复现** | FastJSON 1.2.24 POC | ⬜ |
| | FastJSON 1.2.47 POC | ⬜ |
| | FastJSON 1.2.68 绕过分析 | ⬜ |
| **内存马** | Servlet 内存马 Demo | ⬜ |
| | Filter 内存马 Demo | ⬜ |
| **方法论** | "望闻问切"五步模板 | ⬜ |
| | 知识库目录规范 | ⬜ |
| **文档** | FastJSON 版本演化脉络图 | ⬜ |
| | 第1周简报 | ⬜ |

---

## 🎯 里程碑检查点

| 时间 | 检查点 | 通过标准 |
|:----:|--------|----------|
| 第1天 | FastJSON 环境 | 1.2.24 POC 成功反弹 shell |
| 第3天 | 版本演化理解 | 能画出三版本演化图 |
| 第4天 | 望闻问切 | 五步模板完成并理解 |
| 第7天 | 周简报 | 第1周简报完成 |

---

## ⚠️ 注意事项

### 资源准备

| 资源 | 说明 | 状态 |
|------|------|:----:|
| JDK 1.8+ | Java 编译环境 | ⬜ |
| Maven | 依赖管理 | ⬜ |
| Burp Suite | 抓包分析 | ⬜ |

### 学习建议

- 先理解原理再动手，避免盲目抄 POC
- 每晚复盘当天内容，形成笔记
- "望闻问切"框架在实战中迭代优化

---

<div class="weekly-tips">
  <h4>💪 本周寄语</h4>
  <p>第1周是起点。节奏比完美更重要。先跑通，再优化。</p>
</div>