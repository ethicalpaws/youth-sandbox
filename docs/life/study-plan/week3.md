---
week: 3
start_date: "2026-05-23"
end_date: "2026-05-29"
status: "已完成"
theme: "完成CC2/3/4链学习，初步了解SSTI和信息泄露，落地Shiro550/WebLogic，完成SeedLab防火墙实验"
keywords:
  - CC2链
  - CC3链
  - CC4链
  - Shiro550
  - WebLogic
  - SSTI
  - 信息泄露
  - SeedLab防火墙
---

# 🌟 Week 3 学习计划

> **时间**：2026年5月23日 - 5月29日  
> **阶段目标**：完成CC2/3/4链学习，初步了解SSTI原理和信息泄露类型，落地Shiro550/WebLogic，完成SeedLab防火墙实验，输出CC1-7完整知识体系

<link rel="stylesheet" href="/asserts/css/weekly.css">
<script src="/asserts/js/weekly.js" defer></script>

---

## 📊 本周打卡表

<div class="weekly-card">
  <div class="weekly-header">
    <span>📅 Week 3 进度</span>
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
| **周六 5.23** | CC2链学习 + PriorityQueue入口分析 | <input type="checkbox" class="task-check" data-task="cc2"> |
| | CC3链复习（TemplatesImpl字节码加载） | <input type="checkbox" class="task-check" data-task="cc3-review"> |
| | 手写CC2 POC | <input type="checkbox" class="task-check" data-task="cc2-poc"> |
| | ISCC复盘WP（第一篇）| <input type="checkbox" class="task-check" data-task="iscc-wp1"> |
| **周日 5.24** | CC4链学习 + InstantiateTransformer | <input type="checkbox" class="task-check" data-task="cc4"> |
| | CC2/3/4对比总结 | <input type="checkbox" class="task-check" data-task="cc-compare"> |
| | CC1-7调用链图初稿 | <input type="checkbox" class="task-check" data-task="chain-draft"> |
| | ISCC复盘WP（第二篇） | <input type="checkbox" class="task-check" data-task="iscc-wp2"> |
| **周一 5.25** | Shiro550 环境搭建 | <input type="checkbox" class="task-check" data-task="shiro-env"> |
| | Shiro550 漏洞原理分析 | <input type="checkbox" class="task-check" data-task="shiro-principle"> |
| | 手工验证（ysoserial + 默认密钥） | <input type="checkbox" class="task-check" data-task="shiro-test"> |
| **周二 5.26** | Shiro550 密钥获取 | <input type="checkbox" class="task-check" data-task="shiro-key"> |
| | Shiro550 完整利用（反弹Shell） | <input type="checkbox" class="task-check" data-task="shiro-exp"> |
| | SSTI原理初步了解 | <input type="checkbox" class="task-check" data-task="ssti-basic"> |
| **周三 5.27** | WebLogic 环境搭建 | <input type="checkbox" class="task-check" data-task="weblogic-env"> |
| | WebLogic 漏洞利用（XML Payload） | <input type="checkbox" class="task-check" data-task="weblogic-exp"> |
| | 信息泄露类型初步了解 | <input type="checkbox" class="task-check" data-task="info-leak-basic"> |
| **周四 5.28** | CC1-7完整对比图 | <input type="checkbox" class="task-check" data-task="final-compare"> |
| | ISCC复盘WP（第三篇） | <input type="checkbox" class="task-check" data-task="iscc-wp3"> |
| | SeedLab防火墙实验 | <input type="checkbox" class="task-check" data-task="firewall-lab"> |
| **周五 5.29** | CC1-7总览图定稿 | <input type="checkbox" class="task-check" data-task="final-chain"> |
| | 本周漏洞复现总结 | <input type="checkbox" class="task-check" data-task="summary"> |
| | 周报撰写 + 下周计划 | <input type="checkbox" class="task-check" data-task="weekly-report"> |

<div class="weekly-summary">
  <h4>📝 周记</h4>
  <textarea id="weeklyNotes" rows="3" placeholder="记录本周的收获、卡点、碎碎念..."></textarea>
  <button id="saveWeeklyBtn" class="weekly-save">💾 保存周记</button>
</div>

---

## 📋 本周概览

| 维度 | 内容 | 优先级 |
|------|------|:------:|
| Java反序列化 | CC2/3/4链、CC1-7总览图、对比表 | 🔴 高 |
| 漏洞复现 | Shiro550、WebLogic（CVE-2017-10271） | 🔴 高 |
| Web漏洞 | SSTI原理初步了解、信息泄露类型初步了解 | 🟡 中 |
| CTF复盘 | ISCC初赛复盘WP三篇 | 🟡 中 |
| 网络安全 | SeedLab防火墙实验 | 🟡 中 |

---

## 🗓️ 每日安排

### 第1天（周六 / 5.23）

| 时间段 | 任务 |
|:------:|------|
| 上午 | CC2链学习：PriorityQueue + TransformingComparator 入口，与CC1/5/6/7入口对比 |
| 下午 | CC3链复习：TemplatesImpl 字节码加载、InstantiateTransformer、TrAXFilter |
| 晚上 | 手写CC2 POC + ISCC复盘WP（第一篇）：写解题思路和flag |

**产出：**
- [ ] CC2链POC + 调用链路图
- [ ] CC3链POC（复习完善）
- [ ] ISCC复盘WP第一篇

---

### 第2天（周日 / 5.24）

| 时间段 | 任务 |
|:------:|------|
| 上午 | CC4链学习：理解 InstantiateTransformer，CC2入口 + CC3尾部组合 |
| 下午 | CC2/3/4对比总结：入口、触发方式、适用场景、JDK限制、依赖版本 |
| 晚上 | CC1-7调用链图初稿 + ISCC复盘WP（第二篇） |

**产出：**
- [ ] CC4链POC
- [ ] CC2/3/4对比总结表
- [ ] CC1-7调用链图初稿（手绘或流程图工具）
- [ ] ISCC复盘WP第二篇

---

### 第3天（周一 / 5.25）

| 时间段 | 任务 |
|:------:|------|
| 上午 | Shiro550 环境搭建：Vulhub shiro/CVE-2016-4437 |
| 下午 | 漏洞原理分析：RememberMe AES加密流程、Cookie传递、反序列化触发点 |
| 晚上 | 手工验证：用 ysoserial 生成CC链Payload，结合默认密钥测试 |

**产出：**
- [ ] Shiro550 环境搭建记录
- [ ] 漏洞原理笔记（含流程图）
- [ ] 手工验证截图

---

### 第4天（周二 / 5.26）

| 时间段 | 任务 |
|:------:|------|
| 上午 | Shiro550 密钥获取：源码泄露、默认密钥字典、工具爆破 |
| 下午 | 完整利用：构造加密Payload，替换Cookie，执行命令 + 反弹Shell |
| 晚上 | SSTI原理初步了解：什么是模板注入、基本检测手法（无完整笔记） |

**产出：**
- [ ] Shiro550完整利用记录（含反弹Shell截图）
- [ ] SSTI原理了解（口头理解，未形成笔记）

> **说明**：SSTI只学习了基本原理，未产出完整笔记，暑假再深入。

---

### 第5天（周三 / 5.27）

| 时间段 | 任务 |
|:------:|------|
| 上午 | WebLogic 环境搭建：Vulhub weblogic/CVE-2017-10271 |
| 下午 | 漏洞原理 + 利用：XMLDecoder反序列化，发送恶意XML Payload |
| 晚上 | 信息泄露类型初步了解：.git、.env、Swagger、JS接口（无完整笔记） |

**产出：**
- [ ] WebLogic利用记录（执行 touch /tmp/success）
- [ ] 信息泄露类型了解（口头理解，未形成笔记）

> **说明**：信息泄露只了解了常见类型，未产出完整笔记，暑假再深入。

---

### 第6天（周四 / 5.28）

| 时间段 | 任务 |
|:------:|------|
| 上午 | CC1-7完整对比图：入口、触发方式、JDK限制、CC版本、命令执行方式 |
| 下午 | ISCC复盘WP（第三篇）：整理思路、完善解题过程 |
| 晚上 | SeedLab防火墙实验：学习防火墙规则配置，理解包过滤与策略设置 |

**产出：**
- [ ] CC1-7完整对比图（表格或思维导图）
- [ ] ISCC复盘WP第三篇
- [ ] SeedLab防火墙实验报告（含规则配置截图）

---

### 第7天（周五 / 5.29）

| 时间段 | 任务 |
|:------:|------|
| 上午 | CC1-7总览图定稿：合并调用链图和对比图，形成完整知识图谱 |
| 下午 | 本周漏洞复现总结：Shiro550、WebLogic |
| 晚上 | 周报撰写 + 下周计划 |

**产出：**
- [ ] CC1-7完整调用链图（最终版）
- [ ] CC1-7完整对比表（最终版）
- [ ] 本周学习周报
- [ ] 下周计划草稿

---

## 📊 本周产出清单

| 类别 | 产出 | 状态 |
|------|------|:----:|
| Java反序列化 | CC2/3/4链POC + 调用链路图 | ⬜ |
| | CC2/3/4对比总结表 | ⬜ |
| | CC1-7完整调用链图 | ⬜ |
| | CC1-7完整对比表 | ⬜ |
| 漏洞复现 | Shiro550完整利用记录 | ⬜ |
| | WebLogic CVE-2017-10271利用记录 | ⬜ |
| Web漏洞 | SSTI原理初步了解（无笔记） | ⚠️ 口头理解 |
| | 信息泄露类型初步了解（无笔记） | ⚠️ 口头理解 |
| CTF复盘 | ISCC复盘WP三篇 | ⬜ |
| 网络安全 | SeedLab防火墙实验报告 | ⬜ |
| 周报 | Week 3 复盘周报 | ⬜ |

---

## 🎯 里程碑检查点

| 时间 | 检查点 | 通过标准 |
|:----:|--------|----------|
| 周日 | CC2/3/4 | 能画出CC2/3/4调用链路图，说出CC2和CC4的区别 |
| 周二 | Shiro550 | 能独立完成从密钥获取到反弹Shell的全流程 |
| 周三 | WebLogic | 能发送恶意XML Payload并执行命令 |
| 周四 | 防火墙实验 | 完成SeedLab防火墙实验，理解包过滤规则 |
| 周五 | CC1-7总览 | 能画出完整的CC1-7调用链总览图（不看笔记） |

---

## 🔗 资源链接

| 资源 | 链接 | 用途 |
|------|------|------|
| Vulhub Shiro550 | vulhub/shiro/CVE-2016-4437 | Shiro漏洞环境 |
| Vulhub WebLogic | vulhub/weblogic/CVE-2017-10271 | WebLogic漏洞环境 |
| ysoserial | https://github.com/frohoff/ysoserial | Payload生成工具 |

---

<div class="weekly-tips">
  <h4>💪 本周寄语</h4>
  <p>本周的核心目标是：把前两周学的CC链知识，在Shiro550和WebLogic这两个真实漏洞里“落地”。</p>
  <p>当你能用手头的武器库打穿这两个环境时，你对Java反序列化的理解就真正形成了闭环。</p>
  <p>—— 加油，⛽️ 青春沙盒主</p>
</div>