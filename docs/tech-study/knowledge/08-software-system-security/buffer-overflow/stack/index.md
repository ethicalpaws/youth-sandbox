---
module_name: 栈溢出
description: 栈溢出入门、ret2text、ret2shellcode、ret2libc、ROP
status: ♻️
total_notes: 7
completed: 7
in_progress: 0
not_started: 0
completion_rate: 100
last_updated: 2026-10-22 01:04:37
---

# 栈溢出

> 栈溢出入门、ret2text、ret2shellcode、ret2libc、ROP

## 📊 学习统计

| 指标 | 数值 |
|------|:----:|
| 总笔记数 | 7 |
| ✅ 已完成 | 7 |
| 🔄 进行中 | 0 |
| ⬜ 未开始 | 0 |
| 完成率 | ██████████ 100% |

## 📖 学习内容

| 笔记 | 描述 | 状态 |
|------|------|:----:|
| [栈溢出基础](basic.md) | 栈的构造、栈帧建立/销毁与栈溢出基础 | ✅ |
| [pwn 基础练习——缓冲区溢出入门](pwn-basic.md) | 缓冲区溢出基础原理与 ret2text 实战，涵盖编译选项、汇编分析、偏移量计算（cyclic 工具）、gdb 调试脚本... | ✅ |
| [ret2libc 基础练习](ret2libc.md) | ret2libc 系列攻击详解，涵盖 ret2libc1（直接调用 system）、ret2libc2（写入 /bin/... | ✅ |
| [Ret2Shellcode](ret2shellcode.md) | ret2shellcode 的核心思想、DEP 限制与绕过思路 | ✅ |
| [ret2libc 二次溢出与地址泄露](retl2ibctwo.md) | ret2libc 二次溢出攻击详解，涵盖 PLT/GOT 动态链接机制、ASLR 绕过原理、通过 puts 泄露 lib... | ✅ |
| [ROP 基础练习](rop.md) | ROP（面向返回编程）基础练习，涵盖 ret2shellcode（shellcode 写入可执行段）、rop（通过 ga... | ✅ |
| [栈溢出利用思路总结](stack-overflow-summary.md) | 栈溢出利用思路总结，按 NX/Canary/PIE 与 system 入口等条件分类 | ✅ |

---
*自动更新：2026-10-22 01:04:37
