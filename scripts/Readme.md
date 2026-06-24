# 📚 文档自动更新脚本集

> 自动化生成和维护技术文档索引的工具集

## 📖 简介

本脚本集用于自动更新 `youth-sandbox/docs` 项目中的各类索引文件，包括：

- **知识笔记索引** (`knowledge/`) - 各章节的模块级和章节级索引
- **实战练习索引** (`practice/`) - CTF、CVE、Lab、SRC 的索引
- **每周检测索引** (`weekly-check/`) - 周报和检测记录索引
- **角色数据** (`data/character.json`) - 自动统计经验和能力值
- **总览页面** (`tech-study/index.md`) - 技术学习总览

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 依赖库：`pyyaml`

### 安装依赖

```bash
pip install pyyaml
```
一键运行所有脚本
```bash
python run_all.py
```
## 📁 脚本列表
核心模块
- common.py	公共函数模块（配置、Front Matter 解析、进度条等）
- run_all.py	统一入口脚本，按依赖顺序运行所有脚本
- config.yaml	全局配置文件
- Practice 板块（实战练习）

| 脚本 | 层级 | 说明 |
|------|------|------|
| `update_ctf_notes.py` | 题目级 | 生成 CTF 每道题的 index.md |
| `update_ctf_modules.py` | 模块级 | 生成 CTF 模块的 index.md |
| `update_ctf_chapter.py` | 章节级 | 生成 CTF 总览 index.md |
| `update_cve_notes.py` | 题目级 | 生成 CVE 每个漏洞的 index.md |
| `update_cve_chapter.py` | 章节级 | 生成 CVE 总览 index.md |
| `update_lab_notes.py` | 题目级 | 生成 Lab 每个靶场的 index.md |
| `update_lab_modules.py` | 模块级 | 生成 Lab 模块的 index.md |
| `update_lab_chapter.py` | 章节级 | 生成 Lab 总览 index.md |
| `update_src_notes.py` | 题目级 | 生成 SRC 每个目标的 index.md |
| `update_src_modules.py` | 模块级 | 生成 SRC 模块的 index.md |
| `update_src_chapter.py` | 章节级 | 生成 SRC 总览 index.md |
| `update_practice_index.py` | 总览 | 生成 practice/index.md |

## Knowledge 板块（知识笔记）

| 脚本 | 说明 |
|------|------|
| `update_foundation_chapter.py` | 更新 01-foundation 章节 |
| `update_network_chapter.py` | 更新 02-network 章节 |
| `update_web_chapter.py` | 更新 03-web-basics + 04-web-advanced 章节 |
| `update_java_chapter.py` | 更新 05-java-security 章节 |
| `update_java_deserialization.py` | 更新 java-deserialization 模块 |
| `update_jndi_injection.py` | 更新 jndi-injection 模块 |
| `update_memory_shell.py` | 更新 memory-shell 模块 |
| `update_framework_vulns.py` | 更新 framework-vulns 模块 |
| `update_redblue_module.py` | 更新红蓝对抗模块级索引 |
| `update_redblue_chapter.py` | 更新红蓝对抗章节级索引 |
| `update_knowledge_index.py` | 更新 knowledge/index.md |

## 其他板块

| 脚本 | 说明 |
|------|------|
| `update_weekly_all.py` | 每周检测完整更新（周目录 + 章节级） |
| `update_character_data.py` | 更新角色数据 character.json |
| `update_tech_study_index.py` | 更新 tech-study/index.md |


## 📖 使用指南
运行所有脚本
```bash
python run_all.py
```
只运行指定板块
```bash
# 只运行 practice 板块
python run_all.py -c practice

# 只运行 knowledge 板块
python run_all.py -c knowledge

# 只运行 Java 安全相关
python run_all.py -c java

# 只运行每周检测
python run_all.py -c weekly
```
只运行单个脚本
```bash
python run_all.py -s update_ctf_notes.py
```
模拟运行（预览）
```bash
python run_all.py --dry-run
```
查看所有可用脚本
```bash
python run_all.py --list
```
遇错继续执行
```bash
python run_all.py --skip-errors
```
详细输出模式
```bash
python run_all.py --verbose
```
## 📄 笔记元数据规范
所有笔记文件需要包含 Front Matter，示例：

```yaml
---
title: SQL注入基础
description: SQL注入的原理、分类和防御措施
tags: [SQL注入, sqli, 注入]
status: 已完成
finish-date: 2026-06-07
difficulty: 中等
---
```
## 📊 数据提取来源说明
1. 笔记元数据（Front Matter）
所有 .md 笔记文件开头的 YAML 格式元数据，是脚本的主要数据来源：

```yaml
---
title: 笔记标题
description: 笔记描述
tags: [标签1, 标签2]
status: 已完成        # 状态：已完成/进行中/未开始
difficulty: 中等      # 难度：简单/中等/困难/专家
finish-date: 2026-06-07
exp: 20              # 经验值（可选，优先使用）
level: "⭐⭐"         # 星级（可选）
achievement: 中等猎手 # 成就（可选）
---
```
2. 各模块 index.md 的 Front Matter
    脚本会递归读取各模块的 index.md，从中提取统计数据：

    | 字段 | 来源文件 | 说明 |
    |------|----------|------|
    | `total` | `ctf/*/index.md` | 模块总题目数 |
    | `completed` | `ctf/*/index.md` | 已完成题目数 |
    | `completion_rate` | `ctf/*/index.md` | 完成率 |
    | `analyzed` | `cve/index.md` | 已分析 CVE 数量 |
    | `bounty` | `src/*/index.md` | SRC 累计奖金 |

3. 配置文件 config.yaml
    | 配置项 | 用途 |
    |--------|------|
    | `status_map` | 状态中文到表情符号的映射 |
    | `difficulty_config` | 难度对应的经验值、星级、成就 |
    | `annual_goal` | 年度目标（奖金、目标数） |
    | `src_achievements` | SRC 成就阈值 |
    | `module_tag_mapping` | 模块与 practice 题目的关联关键词 |

4. 角色数据 character.json
    由 update_character_data.py 生成和维护，包含：
    | 字段 | 来源 |
    |------|------|
    | `level` | 根据总经验值计算 |
    | `total_exp` | 笔记数×10 + CTF×20 + CVE×40 + SRC×50 + 周测经验 |
    | `notes_count` | 扫描 knowledge/ + practice/ + weekly-check/ 所有笔记 |
    | `skills` | 从各模块 index.md 的统计字段计算 |
    | `heatmap` | 扫描所有笔记文件的修改时间 |

5. 学习计划文件 life/study-plan/weekX.md
用于周报的时间范围提取：

```yaml
---
week: 1
start_date: "2026-05-09"
end_date: "2026-05-15"
---
```
6. 检测文件 weekly-check/weekX/detection.md
用于提取每周检测得分：
```
从 <span id="totalScore">87</span> 或 得分：87 格式提取分数
```
## 📊 数据流向图
```text
┌─────────────────────────────────────────────────────────────┐
│                      原始数据源                              │
├─────────────────────────────────────────────────────────────┤
│  .md 笔记文件          config.yaml          study-plan/     │
│  (Front Matter)        (全局配置)            (周次时间)      │
└───────────┬─────────────────┬───────────────────┬───────────┘
            │                 │                   │
            ▼                 ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      脚本处理层                              │
├─────────────────────────────────────────────────────────────┤
│  update_*_notes.py    → 生成题目级 index.md                  │
│  update_*_modules.py  → 生成模块级 index.md                  │
│  update_*_chapter.py  → 生成章节级 index.md                  │
│  update_character_data.py → 生成 character.json             │
└───────────┬─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                      输出产物                                │
├─────────────────────────────────────────────────────────────┤
│  knowledge/*/index.md   知识索引                            │
│  practice/*/index.md    实战索引                            │
│  weekly-check/index.md  周报索引                            │
│  tech-study/index.md    技术学习总览                        │
│  data/character.json    角色数据                            │
└─────────────────────────────────────────────────────────────┘
```
📄 笔记元数据规范
状态说明
状态	图标	说明
已完成	✅	内容已完成
进行中	🔄	 正在学习中
未开始	⬜	尚未开始
难度说明
难度	经验值	星级	成就
简单	10	⭐	      简单猎手
中等	20	⭐⭐	     中等猎手
困难	50	⭐⭐⭐	   困难猎手
专家	100	⭐⭐⭐⭐  专家猎手

## 🔧 配置文件说明
config.yaml 包含以下配置项：

```yaml
# 状态映射
status_map:
  已完成: "✅"
  进行中: "🔄"
  未开始: "⬜"

# 难度配置
difficulty_config:
  简单:
    exp: 10
    level: "⭐"
    achievement: "简单猎手"
  # ...

# 年度目标
annual_goal:
  target_bounty: 100000
  target_targets: 50

# 各章节的标签映射
web_basics:
  module_tag_mapping:
    xss:
      - xss
      - XSS
    # ...
```
## 📁 目录结构
```text
docs/
├── tech-study/
│   ├── index.md              # 技术学习总览
│   ├── knowledge/            # 知识笔记
│   │   ├── index.md          # 知识笔记总览
│   │   ├── 01-foundation/
│   │   ├── 02-network/
│   │   └── ...
│   ├── practice/             # 实战练习
│   │   ├── index.md          # 实战总览
│   │   ├── ctf/
│   │   ├── cve/
│   │   ├── lab/
│   │   └── src/
│   └── weekly-check/         # 每周检测
│       ├── index.md          # 周报总览
│       ├── week1/
│       └── week2/
├── data/
│   └── character.json        # 角色数据
└── life/
    └── study-plan/           # 学习计划
        ├── week1.md
        └── week2.md
```
⚠️ 注意事项
运行顺序：建议使用 run_all.py 自动按依赖顺序执行

编码问题：Windows 用户请确保控制台支持 UTF-8

首次运行：需要先安装依赖 pip install pyyaml

🐛 常见问题
Q: 提示 No module named 'yaml'
bash
pip install pyyaml
Q: Windows 控制台显示乱码或报错
脚本已内置编码修复，如仍有问题，请确保：

使用 PowerShell 或 Windows Terminal

或运行 chcp 65001 切换编码

Q: 知识笔记数和总笔记数不一致
这是正常的：

知识笔记数：仅 knowledge/ 目录下的笔记

总笔记数：包含 knowledge/ + practice/ + weekly-check/ 的所有笔记

## 📝 更新日志
2026-06-07
完成所有脚本的优化重构

新增 common.py 公共模块

新增 run_all.py 统一入口

修复 Windows 控制台编码问题

优化增量更新逻辑

## 📄 许可证
内部使用，请勿外传。

保持热爱，持续学习 🚀

```text

这份 README 包含了：
- 项目简介
- 快速开始指南
- 完整的脚本列表和说明
- 使用命令示例
- 笔记元数据规范
- 配置文件说明
- 目录结构
- 数据来源
- 常见问题解答
```