---
week: {week}
start_date: "{start_date}"
end_date: "{end_date}"
status: "进行中"
theme: "{本周主题}"
keywords:
  - {关键词1}
  - {关键词2}
  - {关键词3}
---

# 🌟 Week {week} 学习计划

> **时间**：{start_date} - {end_date}  
> **阶段目标**：{阶段目标描述}  
> **核心调整**：{核心调整说明}

<link rel="stylesheet" href="/asserts/css/weekly.css">
<script src="/asserts/js/weekly.js" defer></script>

---

## 📊 本周打卡表

<div class="weekly-card">
  <div class="weekly-header">
    <span>📅 Week {week} 进度</span>
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
| **{周几} {月}.{日}** | {任务描述1} | <input type="checkbox" class="task-check" data-task="{task-id-1}"> |
| | {任务描述2} | <input type="checkbox" class="task-check" data-task="{task-id-2}"> |
| | {任务描述3} | <input type="checkbox" class="task-check" data-task="{task-id-3}"> |
| **{周几} {月}.{日}** | {任务描述1} | <input type="checkbox" class="task-check" data-task="{task-id-4}"> |
| | {任务描述2} | <input type="checkbox" class="task-check" data-task="{task-id-5}"> |
| | {任务描述3} | <input type="checkbox" class="task-check" data-task="{task-id-6}"> |
| **{周几} {月}.{日}** | {任务描述1} | <input type="checkbox" class="task-check" data-task="{task-id-7}"> |
| | {任务描述2} | <input type="checkbox" class="task-check" data-task="{task-id-8}"> |
| | {任务描述3} | <input type="checkbox" class="task-check" data-task="{task-id-9}"> |
| **{周几} {月}.{日}** | {任务描述1} | <input type="checkbox" class="task-check" data-task="{task-id-10}"> |
| | {任务描述2} | <input type="checkbox" class="task-check" data-task="{task-id-11}"> |
| | {任务描述3} | <input type="checkbox" class="task-check" data-task="{task-id-12}"> |
| **{周几} {月}.{日}** | {任务描述1} | <input type="checkbox" class="task-check" data-task="{task-id-13}"> |
| | {任务描述2} | <input type="checkbox" class="task-check" data-task="{task-id-14}"> |
| | {任务描述3} | <input type="checkbox" class="task-check" data-task="{task-id-15}"> |
| **{周几} {月}.{日}** | {任务描述1} | <input type="checkbox" class="task-check" data-task="{task-id-16}"> |
| | {任务描述2} | <input type="checkbox" class="task-check" data-task="{task-id-17}"> |
| | {任务描述3} | <input type="checkbox" class="task-check" data-task="{task-id-18}"> |
| **{周几} {月}.{日}** | {任务描述1} | <input type="checkbox" class="task-check" data-task="{task-id-19}"> |
| | {任务描述2} | <input type="checkbox" class="task-check" data-task="{task-id-20}"> |
| | {任务描述3} | <input type="checkbox" class="task-check" data-task="{task-id-21}"> |

<div class="weekly-summary">
  <h4>📝 周记</h4>
  <textarea id="weeklyNotes" rows="3" placeholder="记录本周的收获、卡点、碎碎念..."></textarea>
  <button id="saveWeeklyBtn" class="weekly-save">💾 保存周记</button>
</div>

---

## 📋 本周概览

| 维度 | 内容 | 优先级 |
|------|------|:------:|
| {维度1} | {内容描述} | {🔴 高 / 🟡 中 / 🟢 低} |
| {维度2} | {内容描述} | {🔴 高 / 🟡 中 / 🟢 低} |
| {维度3} | {内容描述} | {🔴 高 / 🟡 中 / 🟢 低} |

---

## 🗓️ 每日安排

### 第1天（{周几} / {月}.{日}）：{主题}

| 时间段 | 任务 |
|:------:|------|
| 上午 | {任务描述} |
| 下午 | {任务描述} |
| 晚上 | {任务描述} |

**产出：**
- [ ] {产出1}
- [ ] {产出2}
- [ ] {产出3}

---

### 第2天（{周几} / {月}.{日}）：{主题}

| 时间段 | 任务 |
|:------:|------|
| 上午 | {任务描述} |
| 下午 | {任务描述} |
| 晚上 | {任务描述} |

**产出：**
- [ ] {产出1}
- [ ] {产出2}
- [ ] {产出3}

---

### 第3天（{周几} / {月}.{日}）：{主题}

| 时间段 | 任务 |
|:------:|------|
| 上午 | {任务描述} |
| 下午 | {任务描述} |
| 晚上 | {任务描述} |

**产出：**
- [ ] {产出1}
- [ ] {产出2}
- [ ] {产出3}

---

### 第4天（{周几} / {月}.{日}）：{主题}

| 时间段 | 任务 |
|:------:|------|
| 上午 | {任务描述} |
| 下午 | {任务描述} |
| 晚上 | {任务描述} |

**产出：**
- [ ] {产出1}
- [ ] {产出2}
- [ ] {产出3}

---

### 第5天（{周几} / {月}.{日}）：{主题}

| 时间段 | 任务 |
|:------:|------|
| 上午 | {任务描述} |
| 下午 | {任务描述} |
| 晚上 | {任务描述} |

**产出：**
- [ ] {产出1}
- [ ] {产出2}
- [ ] {产出3}

---

### 第6天（{周几} / {月}.{日}）：{主题}

| 时间段 | 任务 |
|:------:|------|
| 上午 | {任务描述} |
| 下午 | {任务描述} |
| 晚上 | {任务描述} |

**产出：**
- [ ] {产出1}
- [ ] {产出2}
- [ ] {产出3}

---

### 第7天（{周几} / {月}.{日}）：{主题}

| 时间段 | 任务 |
|:------:|------|
| 上午 | {任务描述} |
| 下午 | {任务描述} |
| 晚上 | {任务描述} |

**产出：**
- [ ] {产出1}
- [ ] {产出2}
- [ ] {产出3}

---

## 📊 本周产出清单

| 类别 | 产出 | 状态 |
|------|------|:----:|
| **{类别1}** | {产出描述} | ⬜ |
| | {产出描述} | ⬜ |
| **{类别2}** | {产出描述} | ⬜ |
| | {产出描述} | ⬜ |
| **{类别3}** | {产出描述} | ⬜ |
| | {产出描述} | ⬜ |

---

## 🎯 里程碑检查点

| 时间 | 检查点 | 通过标准 |
|:----:|--------|----------|
| {第N天} | {检查点描述} | {通过标准} |
| {第N天} | {检查点描述} | {通过标准} |
| {第N天} | {检查点描述} | {通过标准} |

---

## ⚠️ 注意事项

### 资源准备

| 资源 | 说明 | 状态 |
|------|------|:----:|
| {资源1} | {说明} | ⬜ |
| {资源2} | {说明} | ⬜ |
| {资源3} | {说明} | ⬜ |

### 学习建议

- {建议1}
- {建议2}
- {建议3}

---

<div class="weekly-tips">
  <h4>💪 本周寄语</h4>
  <p>{寄语内容}</p>
</div>