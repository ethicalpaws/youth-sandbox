---
title: Windows安全模型
description: SID、访问令牌、安全描述符、DACL、ACE、权限与特权、UAC
tags: [windows, security, sid, token, uac, 权限]
status: 进行中
finish-date: 2026-06-01
difficulty: 中等
---

# Windows安全模型
## 安全标识符（SID）
1. 定义：SID是Windows中唯一标识安全主体（用户、组、计算机）的可变长度字符串
2. 格式：`S-1-5-21-3623811015-3361044348-30300820-1013`
    | 部分 | 含义 |
    |------|------|
    | S | 前缀，表示 SID |
    | 1 | 版本号 |
    | 5 | 颁发机构（NT Authority） |
    | 21 | 子机构（表示是域或本地计算机） |
    | 3623811015... | 计算机/域的唯一标识 |
    | 1013 | 相对 ID（RID），表示具体用户 |    

    ---

    常见SID
    | SID | 对应主体 |
    |------|----------|
    | S-1-0-0 | Nobody |
    | S-1-1-0 | Everyone（所有人） |
    | S-1-5-18 | LOCAL SYSTEM（最高权限） |
    | S-1-5-19 | LOCAL SERVICE |
    | S-1-5-20 | NETWORK SERVICE |
    | S-1-5-32-544 | Administrators 组 |
    | S-1-5-32-545 | Users 组 |
    | S-1-5-21-xxx-500 | 内置 Administrator 账号 |
    | S-1-5-21-xxx-502 | 内置 Guest 账号 |
    | S-1-5-21-xxx-512 | Domain Admins 组（域环境） |   

    ---

## 访问令牌（Token）
**定义**：每个进程/线程都有一个Token，描述其安全上下文
**Token包含的信息**：
```
Token {
    用户SID
    组SID列表（用户所属的所有组）
    特权列表（如SeShutdownPrivilege、SeDebugPrivilege）
    完整性级别（Low/Medium/High/System）
    默认所有者SID
    默认DACL
    会话ID（Session ID）
}
```
**两种Token**：
- 主令牌（Primary Token）：关联到进程，表示该进程的默认身份
- 模拟令牌（Impersonation Token）：线程临时借用其他身份
## 安全描述符（Security Descriptor）
**定义**：每个安全对象（文件、进程、注册表项等）都有一个安全描述符
**安全描述符包含**
```
Security Descriptor {
    所有者SID（Owner）
    主组SID（Primary Group）
    DACL（自由访问控制列表）
    SACL（系统访问控制列表，用于审计）
}
```
## DACL与ACE
**DACL**（Discretionary Access Control List）：决定谁可以怎样访问对象
**DACL的结构**
```
DACL {
    ACE1: 用户A, 允许, 读
    ACE2: 用户B, 拒绝, 写
    ACE3: 组C, 允许, 完全控制
}
```
**ACE**（Access Control Entry）：DACL中的单个条目。
**ACE的格式**：
- 主体SID（谁）
- 访问掩码（什么权限：读/写/执行/删除/改权限）
- 类型（允许/拒绝）
- 继承标志（是否传给子对象）
## 权限与特权
**权限**（Permission）：针对具体对象（如对C:\test.txt的读权限）
**特权**（Privilege）：系统级别的能力，独立于具体对象
**关键特权列表**:
| 特权 | 名称 | 作用 |
|------|------|------|
| SeDebugPrivilege | 调试特权 | 可以读写任何进程的内存 |
| SeImpersonatePrivilege | 模拟特权 | 可以冒充其他用户 |
| SeAssignPrimaryTokenPrivilege | 分配主令牌 | 可以在创建新进程时指定令牌 |
| SeShutdownPrivilege | 关机特权 | 可以关闭系统 |
| SeTakeOwnershipPrivilege | 取得所有权 | 可以获得任意对象的所有权 |
| SeBackupPrivilege | 备份特权 | 可以绕过 ACL 读取文件 |
| SeRestorePrivilege | 恢复特权 | 可以绕过 ACL 写入文件 |

---

**查看当前用户拥有的特权**:`whoami /priv`
## UAC（用户账户控制）
**UAC解决的问题**：即使你用的是管理员账户，默认Token是中完整性级别，防止恶意软件静默做坏事
**UAC的工作机制**
  1. 用户登录（管理员账户）→ 生成两个Token
     - 完整管理员Token（High完整性），存储起来但默认不用
     - 过滤后的管理员Token（Medium完整性），用于日常操作
  2. 普通程序用Medium Token运行
  3. 当程序需要管理员权限时：
     - 自动触发UAC弹窗（如果程序标记了requireAdministrator）
     - 或者用户右键“以管理员身份运行”
  4. 用户点击“是” → 进程获得完整管理员Token 

**UAC的四个等级**

| 等级 | 行为 |
|------|------|
| 始终通知 | 任何操作都弹窗 |
| 仅当程序尝试更改计算机时通知（默认） | 标准行为 |
| 仅当程序尝试更改计算机时通知（不降低桌面亮度） | 同上但不切桌面 |
| 从不通知 | UAC 关闭（不推荐） |

---
