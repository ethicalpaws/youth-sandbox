---
total_modules: 2
total_notes: 21
completed: 20
in_progress: 0
not_started: 1
completion_rate: 95
last_updated: 2026-10-22 01:04:38
---

# 💥 软件系统安全

> 缓冲区溢出 · 栈/堆利用 · 格式化字符串 · 整数溢出 · 防御机制

## 📊 学习进度

| 指标 | 数值 |
|------|:----:|
| 模块数 | 2 |
| 笔记总数 | 21 |
| ✅ 已完成 | 20 |
| 🔄 进行中 | 0 |
| ⬜ 未开始 | 1 |
| 完成率 | █████████░ 95% |

## 📚 模块列表

| 模块 | 笔记数 | 已完成 | 完成率 | 状态 |
|------|:------:|:------:|:------:|:----:|
| 📘 [基础](basic/) | 3 | 2 | 66% | 🔄 |
| 💥 [缓冲区溢出](buffer-overflow/) | 18 | 18 | 100% | ♻️ |

## 🗺️ 学习路线

1. **基础**：计算机存储空间 → 汇编/寄存器 → 栈帧结构
2. **栈溢出**：ret2text → ret2shellcode → ret2libc → ROP
3. **堆利用**：堆基础 → UAF → double-free → fastbin → unlink
4. **其他溢出**：格式化字符串 → 整数溢出
5. **防御机制**：ASLR、CFI、Canary、NX/PIE 及绕过思路

## 🛠️ 常用工具

| 工具 | 用途 |
|------|------|
| pwntools | exploit 编写 |
| pwndbg / GEF | GDB 调试增强 |
| checksec | 二进制保护检查 |
| cyclic | 偏移量计算 |
| one_gadget | libc 利用 |

---
*最后更新：2026-10-22 01:04:38 | 从内存布局到控制流劫持，循序渐进 🧠*
