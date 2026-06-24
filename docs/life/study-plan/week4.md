---
week: 4
start_date: "2026-05-30"
end_date: "2026-06-05"
status: "已完成"
theme: "从零掌握JNDI + Log4Shell完整复现 + 域渗透入门（环境+黄金票据）+ SSH隧道体验"
keywords:
  - JNDI
  - Log4Shell
  - 域渗透
  - Kerberos
  - 黄金票据
  - SSH隧道
  - BloodHound
---

# 🌟 Week 4 学习计划

> **时间**：2026年5月30日 - 6月5日  
> **阶段目标**：从零掌握JNDI + Log4Shell完整复现 + 域渗透入门（环境+黄金票据）+ SSH隧道体验  
> **核心调整**：JNDI从零开始学，域渗透放慢节奏（2天）

<link rel="stylesheet" href="/asserts/css/weekly.css">
<script src="/asserts/js/weekly.js" defer></script>

---

## 📊 本周打卡表

<div class="weekly-card">
  <div class="weekly-header">
    <span>📅 Week 4 进度</span>
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
| **周六 5.30** | JNDI概念学习（Context/InitialContext/lookup） | <input type="checkbox" class="task-check" data-task="jndi-concept"> |
| | JNDI架构（RMI/LDAP/DNS/SPI） | <input type="checkbox" class="task-check" data-task="jndi-arch"> |
| | 手写第一个JNDI程序 + CTF复盘WP框架 | <input type="checkbox" class="task-check" data-task="first-jndi"> |
| **周日 5.31** | JNDI注入原理（lookup参数可控的危害） | <input type="checkbox" class="task-check" data-task="jndi-inject"> |
| | Reference + trustURLCodebase | <input type="checkbox" class="task-check" data-task="jndi-reference"> |
| | JNDI注入流程图 + CTF复盘WP完稿 | <input type="checkbox" class="task-check" data-task="jndi-flow"> |
| **周一 6.1** | Log4j2 Lookup机制（${}/JndiLookup/Interpolator） | <input type="checkbox" class="task-check" data-task="log4j-lookup"> |
| | Log4Shell攻击链串联 + 恶意JNDI服务搭建 | <input type="checkbox" class="task-check" data-task="log4shell-chain"> |
| | Log4j攻击链总图（初稿） | <input type="checkbox" class="task-check" data-task="log4j-chain"> |
| **周二 6.2** | Log4Shell完整复现（反弹Shell） | <input type="checkbox" class="task-check" data-task="log4shell-exp"> |
| | SSH隧道体验（ssh -D + tcpdump） | <input type="checkbox" class="task-check" data-task="ssh-tunnel"> |
| | 整理Log4j + JNDI笔记 | <input type="checkbox" class="task-check" data-task="log4j-summary"> |
| **周三 6.3** | 域环境搭建（DC + Win10） | <input type="checkbox" class="task-check" data-task="domain-env"> |
| | Kerberos基础（AS/TGS/PAC/黄金票据原理） | <input type="checkbox" class="task-check" data-task="kerberos"> |
| | 域内基础信息收集（net user /domain） | <input type="checkbox" class="task-check" data-task="domain-info"> |
| **周四 6.4** | 获取krbtgt哈希 + 黄金票据制作 | <input type="checkbox" class="task-check" data-task="golden-ticket"> |
| | 黄金票据访问域控 + BloodHound入门 | <input type="checkbox" class="task-check" data-task="golden-ptt"> |
| | 整理域渗透笔记 | <input type="checkbox" class="task-check" data-task="domain-summary"> |
| **周五 6.5** | 总图定稿（Log4j/JNDI/Kerberos） | <input type="checkbox" class="task-check" data-task="final-charts"> |
| | 整理笔记 + 备份虚拟机快照 | <input type="checkbox" class="task-check" data-task="backup"> |
| | 撰写周报 + 考试期间保温备忘 | <input type="checkbox" class="task-check" data-task="weekly-report"> |

<div class="weekly-summary">
  <h4>📝 周记</h4>
  <textarea id="weeklyNotes" rows="3" placeholder="记录本周的收获、卡点、碎碎念..."></textarea>
  <button id="saveWeeklyBtn" class="weekly-save">💾 保存周记</button>
</div>

---

## 📋 本周概览

| 维度 | 内容 | 优先级 |
|------|------|:------:|
| Java安全 | JNDI从零开始、JNDI注入原理、Log4j2 Lookup机制、Log4Shell完整复现 | 🔴 高 |
| 域渗透 | 域环境搭建、Kerberos基础、黄金票据、域内信息收集 | 🔴 高 |
| 网络隧道 | SSH隧道快速体验（降级版） | 🟡 中 |
| CTF复盘 | Log4j相关CTF题目WP一篇 | 🟡 中 |
| 体系总结 | Log4j攻击链总图、JNDI注入流程图、Kerberos流程图 | 🟡 中 |

---

## 🗓️ 每日安排

### 第1天（周六 / 5.30）：JNDI从零开始

| 时间段 | 任务 |
|:------:|------|
| 上午 | JNDI概念：什么是JNDI？Context、InitialContext、lookup() |
| 下午 | JNDI架构：命名服务、目录服务、SPI、支持的协议（RMI/LDAP/DNS） |
| 晚上 | 手写第一个JNDI程序 + CTF复盘WP（Log4j题目）开始写 |

**产出：**
- [ ] JNDI概念笔记（用自己的话解释）
- [ ] 第一个JNDI程序代码
- [ ] CTF复盘WP（框架）

---

### 第2天（周日 / 5.31）：JNDI注入原理

| 时间段 | 任务 |
|:------:|------|
| 上午 | JNDI注入是什么：lookup()参数可控的危害 |
| 下午 | Reference和远程类加载：Reference类、trustURLCodebase |
| 晚上 | 画JNDI注入攻击流程图 + 完成CTF复盘WP |

**产出：**
- [ ] JNDI注入原理笔记
- [ ] JNDI注入攻击流程图
- [ ] CTF复盘WP完稿

---

### 第3天（周一 / 6.1）：Log4j2 + JNDI联动

| 时间段 | 任务 |
|:------:|------|
| 上午 | Log4j2 Lookup机制：`${}`解析、JndiLookup、Interpolator |
| 下午 | Log4Shell攻击链串联 + 搭建恶意JNDI服务（DNSLog验证） |
| 晚上 | 画Log4j攻击链总图（初稿） |

**产出：**
- [ ] Log4j2 Lookup原理笔记
- [ ] Log4Shell攻击链总图（初稿）

---

### 第4天（周二 / 6.2）：Log4Shell完整复现 + SSH隧道

| 时间段 | 任务 |
|:------:|------|
| 上午 | Log4Shell完整复现（反弹Shell） |
| 下午 | SSH隧道快速体验：`ssh -D` + tcpdump抓包 |
| 晚上 | 整理Log4j + JNDI笔记 |

**产出：**
- [ ] Log4Shell完整复现报告（含Payload构造、服务搭建、利用截图）
- [ ] SSH隧道原理笔记 + tcpdump抓包截图

---

### 第5天（周三 / 6.3）：域环境搭建 + Kerberos基础

| 时间段 | 任务 |
|:------:|------|
| 上午 | 域环境搭建：Windows Server 2019（域控）+ Windows 10（域成员） |
| 下午 | Kerberos基础：AS_REQ/AS_REP、TGS_REQ/TGS_REP、PAC、黄金票据原理 |
| 晚上 | 域内基础信息收集命令（`net user /domain`等） |

**产出：**
- [ ] 域环境搭建图文记录（含快照）
- [ ] Kerberos认证流程图 + 黄金票据原理笔记

---

### 第6天（周四 / 6.4）：黄金票据 + 域内信息收集

| 时间段 | 任务 |
|:------:|------|
| 上午 | 获取krbtgt哈希（mimikatz） + 黄金票据制作 |
| 下午 | 利用黄金票据访问域控 + BloodHound信息收集入门 |
| 晚上 | 整理域渗透笔记 |

**产出：**
- [ ] 黄金票据制作与利用完整记录（含命令和截图）
- [ ] BloodHound分析截图

---

### 第7天（周五 / 6.5）：复习收尾 + 周报 + 备份

| 时间段 | 任务 |
|:------:|------|
| 上午 | 总图定稿：Log4j攻击链总图、JNDI注入流程图、Kerberos流程图 |
| 下午 | 整理本周所有笔记 + 代码 + 截图 |
| 晚上 | 撰写第四周周报 + 备份虚拟机快照 + 整理考试期间保温备忘 |

**产出：**
- [ ] Log4j攻击链总图（最终版）
- [ ] JNDI注入流程图（最终版）
- [ ] Kerberos流程图（最终版）
- [ ] Week 4复盘周报
- [ ] 虚拟机快照备份完成
- [ ] 考试期间“保温”备忘

---

## 📊 本周产出清单

| 类别 | 产出 | 状态 |
|------|------|:----:|
| **JNDI** | JNDI概念笔记 | ⬜ |
| | JNDI注入原理笔记 | ⬜ |
| | JNDI注入攻击流程图 | ⬜ |
| **Log4j** | Log4j2 Lookup原理笔记 | ⬜ |
| | Log4Shell完整复现报告（含截图） | ⬜ |
| | Log4j攻击链总图 | ⬜ |
| **域渗透** | 域环境搭建图文记录 | ⬜ |
| | Kerberos认证流程图 | ⬜ |
| | 黄金票据原理笔记 | ⬜ |
| | 黄金票据制作与利用记录 | ⬜ |
| | BloodHound分析截图 | ⬜ |
| **网络隧道** | SSH隧道原理笔记 + 抓包截图 | ⬜ |
| **CTF复盘** | Log4j CTF题目WP一篇 | ⬜ |
| **周报** | Week 4复盘周报 | ⬜ |

---

## 🎯 里程碑检查点

| 时间 | 检查点 | 通过标准 |
|:----:|--------|----------|
| 周日 | JNDI理解 | 能说出“JNDI是Java查找资源的API” |
| 周二 | Log4Shell复现 | 能独立完成从JNDI服务搭建到反弹Shell的全流程 |
| 周四 | 黄金票据 | 能成功制作黄金票据并访问域控（`dir \\dc\c$`） |
| 周五 | 体系总览 | 能画出Log4j攻击链总图、JNDI注入流程图、Kerberos流程图 |

---

## ⚠️ 注意事项

### 资源准备

| 资源 | 说明 | 状态 |
|------|------|:----:|
| Windows Server 2019 镜像 | 域控 | ⬜ |
| Windows 10 镜像 | 域成员 | ⬜ |
| VMware/VirtualBox | 虚拟机软件 | ⬜ |
| JNDI-Injection-Exploit 或 marshalsec | JNDI服务工具 | ⬜ |

### 学习建议

- **JNDI从零开始**：第1-2天不着急，确保理解“JNDI是什么”再往下学
- **域环境资源**：需要Windows Server 2019和Windows 10镜像，提前下载
- **期末考试准备**：第7天（6月5日）之后，彻底切换复习模式

### 暑假补充内容

以下内容放到暑假继续深入：

| 内容 | 说明 |
|------|------|
| JNDI三种利用方式对比（RMI/LDAP/Serialized） | 暑假补充 |
| 高版本JDK绕过（trustURLCodebase限制） | 暑假补充 |
| FastJSON中的JNDI利用 | 暑假补充 |

---

## 📝 考试期间“保温”备忘（6月6日 - 6月26日）

每天或隔天任选1-2项（10-15分钟）：

| 序号 | 动作 | 状态 |
|:----:|------|:----:|
| 1 | 看一遍Log4j攻击链总图 | ⬜ |
| 2 | 看一遍JNDI注入流程图 | ⬜ |
| 3 | 看一遍Kerberos认证流程图 | ⬜ |
| 4 | 在脑子里过一遍黄金票据的制作命令 | ⬜ |
| 5 | 读一篇安全文章（存到稍后读） | ⬜ |
| 6 | 敲几个域渗透基础命令（`net user /domain`等） | ⬜ |

---

## 🚀 暑假衔接预告

**6月27日** 激活暑假10周计划

---

<div class="weekly-tips">
  <h4>💪 本周寄语</h4>
  <p>这是期末考试前的最后一周系统学习。核心目标只有一个：让Log4Shell和黄金票据在你手里“跑起来”。</p>
  <p>不求多，但求精。学透这两个，暑假就能起飞。</p>
  <p>—— 加油，⛽️ 青春沙盒主</p>
</div>