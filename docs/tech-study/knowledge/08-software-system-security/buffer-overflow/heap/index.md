---
module_name: 堆利用
description: 堆基础、UAF、double-free、fastbin 攻击、unlink 攻击
status: ♻️
total_notes: 6
completed: 6
in_progress: 0
not_started: 0
completion_rate: 100
last_updated: 2026-10-22 01:04:37
---

# 堆利用

> 堆基础、UAF、double-free、fastbin 攻击、unlink 攻击

## 📊 学习统计

| 指标 | 数值 |
|------|:----:|
| 总笔记数 | 6 |
| ✅ 已完成 | 6 |
| 🔄 进行中 | 0 |
| ⬜ 未开始 | 0 |
| 完成率 | ██████████ 100% |

## 📖 学习内容

| 笔记 | 描述 | 状态 |
|------|------|:----:|
| [UAF（use-after-free）](UAF.md) | UAF 的成因、释放后重引用流程、潜在后果与实例 | ✅ |
| [堆溢出基础](basic.md) | 堆的工作原理、chunk 结构、分配器与堆溢出基础 | ✅ |
| [双重释放（double-free）](double-free.md) | 双重释放的漏洞原理、堆块合并/unlink 与现代防御 | ✅ |
| [Fastbin 攻击](fastbin-attack.md) | Fastbin 的组织结构、尺寸限制、分配/释放流程与攻击面 | ✅ |
| [Fastbin Dup 攻击练习](fastbin_dup.md) | Fastbin Dup 题目分析：攻击原理、静态分析与逆向推理 | ✅ |
| [Unlink 攻击](unlink-attack.md) | Unlink 机制与攻击 unlink 的利用原理 | ✅ |

---
*自动更新：2026-10-22 01:04:37
