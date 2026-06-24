---
title: Windows进程与线程
description: 进程概念、线程概念、进程内部结构、关键系统进程
tags: [windows, process, thread, 进程, 线程]
status: 已完成
finish-date: 2026-06-01
difficulty: 简单
---

## 进程的概念
1. 定义：进程是一个正在运行的程序实例，是资源分配的基本单位。
2. 进程包含的内容：
   - 可执行代码（.exe/.dll中的代码段）
   - 数据（全局变量、静态变量）
   - 堆（动态分配的内存）
   - 栈（函数调用、局部变量）
   - 打开的文件句柄、注册表键
   - 环境变量
   - 安全令牌（Token）
   - 一个或多个线程
3. 进程的标识
   - PID（Process ID）：数字标识，系统唯一
   - 进程名：如notepad.exe
   - 进程句柄：内核给调用者返回的引用  
## 进程的内部结构
Windows内核为每个进程维护一个结构体叫EPROCESS，位于内核内存中，普通程序无法直接访问
| 字段 | 说明 |
|------|------|
| PID | 进程ID |
| 进程名 | 如 "notepad.exe" |
| 父进程PID | 谁创建了它 |
| Token | 安全令牌指针 |
| 线程列表 | 该进程拥有的所有线程 |
| 虚拟地址空间描述符 | 内存布局信息 |
| 打开句柄表 | 文件、注册表等资源 |
| 进程状态 | 运行/就绪/等待/终止 |

**关键点**：每个进程有独立的虚拟地址空间，一个进程崩溃不会影响其他进程。

---

## 线程的概念 
1. 线程是CPU调度的基本单位，一个进程至少有一个线程。
2. 线程包含的内容：
   - 线程ID（TID）
   - 程序计数器（下一条指令在哪）
   - 寄存器上下文（当前计算到哪了）
   - 栈（局部变量、函数调用链）
   - Thread Local Storage（线程私有数据） 
3. 线程的特点：
   - 同一进程内的线程共享进程的资源（内存、句柄等）
   - 线程切换比进程切换代价小得多 
## 进程的生命周期
```
创建 → 就绪 → 运行 → 等待（可选） → 终止
```
**创建方式**：
- CreateProcess（Windows API）
- 双击图标（explorer.exe调用CreateProcess）
- 命令行启动
**终止方式**：
- 正常退出（调用ExitProcess）
- 被任务管理器结束（TerminateProcess）
- 崩溃
## 关键系统进程
| 进程名 | 文件路径 | 作用 |
|--------|----------|------|
| System（PID=4） | 内核 | 内核态进程，管理驱动、虚拟内存 |
| System Idle Process（PID=0） | 内核 | 空闲时占用 CPU |
| smss.exe | `\Windows\System32\` | Session Manager，第一个用户态进程 |
| csrss.exe | `\Windows\System32\` | 控制台管理、Win32 子系统 |
| wininit.exe | `\Windows\System32\` | 启动 services.exe、lsass.exe |
| services.exe | `\Windows\System32\` | 服务控制管理器，管理所有系统服务 |
| lsass.exe | `\Windows\System32\` | 本地安全认证，处理登录、密码 |
| svchost.exe | `\Windows\System32\` | 服务宿主，多个服务共享一个进程 |
| winlogon.exe | `\Windows\System32\` | 处理登录/注销、锁定屏幕 |
| explorer.exe | `\Windows\` | 桌面外壳、任务栏、文件管理器 |

---
