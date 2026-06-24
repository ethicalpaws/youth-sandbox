---
title: 某大学信息泄露漏洞
description: 通过目录扫描发现敏感配置文件泄露
tags: ['信息泄露', '目录扫描', '敏感文件']
status: 🔄
difficulty: 简单
platform: edusrc
weakness: 敏感信息泄露
bounty: 500
info_gathering: 1. 使用 dirsearch 扫描目录
2. 发现 /backup/config.bak 文件

discovery: 1. 访问该文件发现数据库配置信息
2. 包含数据库账号密码

exploit: 1. 尝试连接数据库
2. 获取敏感数据

---

# 🎯 漏洞挖掘 · 某大学信息泄露漏洞

---

### 📋 目标档案

| 属性 | 数值 |
|------|------|
| `目标名称` | **某大学信息泄露漏洞** |
| `所属平台` | edusrc |
| `漏洞类型` | 敏感信息泄露 |
| `危害等级` | ⭐ |
| `挖掘状态` | 🔄 **挖掘中** |

### 🏆 战果

| 奖励 | 数量 |
|------|------|
| `奖金` | 💰 500 元 |
| `经验值` | **+10 XP** ✨ |
| `成就` | 简单猎手 🏅 |

---

### 📜 目标描述

通过目录扫描发现敏感配置文件泄露

### 🔍 信息收集

1. 使用 dirsearch 扫描目录
2. 发现 /backup/config.bak 文件


### ⚡ 漏洞发现

1. 访问该文件发现数据库配置信息
2. 包含数据库账号密码


### 💡 利用手法

1. 尝试连接数据库
2. 获取敏感数据


---

### 🔗 关联档案

[📖 详细报告 →](exploit.md)

---

<span style="animation: blink 1s step-end infinite; text-shadow: 0 0 5px #ff6600, 0 0 10px #ff3300;">🎯</span> **VULN FOUND** · 2026-06-07

<style>
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
