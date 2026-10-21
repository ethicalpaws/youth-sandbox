---
title: Metasploit Framework
description: Metasploit 的分层架构、Stager/Stage 载荷机制、Meterpreter 与 post 模块
tags: [c2, metasploit, meterpreter, 后渗透]
status: 已完成
finish-date: 2026-09-23
difficulty: 中等
---

# Metaspolit Framework
>渗透测试领域最经典、最全面的开源框架，由 H.D. Moore 于 2003 年创建，现由 Rapid7 维护

##  架构与核心组件
>MSF 采用模块化架构，所有功能以“模块”形式组织，通过 msfconsole 命令行界面统一调用

**基础库层是整个框架的底座** 
Rex 提供网络套接字、协议实现、编码转换等底层能力；framework-core 负责模块调度与插件交互；framework-base 则封装了更上层的功能调用接口。

**模块体系是 MSF 的灵魂，按功能分为几大类**

- **Exploit（漏洞利用）模块** 针对具体 CVE 编写，如 exploit/multi/samba/usermap_script 对应 Samba 的命令注入漏洞。
- **Auxiliary（辅助）模块** 执行扫描、爆破、指纹识别等信息收集任务，不返回 shell。
- **Payload（攻击载荷）** 是漏洞利用成功后植入目标执行的代码，决定了后续如何控制目标。
- **Post（后渗透）模块** 在获得会话后运行，用于提权、凭据窃取、横向移动等操作。此外还有 
- **Encoder（编码器）** 用于绕过杀软特征检测
- **Evasion（规避）模块** 则直接生成免杀载荷。

**功能程序方面**，msfvenom 是最常用的命令行工具，可将 payload 封装为 exe、apk、php 等多种格式，并支持编码混淆

## Payload 的工作机制：Stager 与 Stage
>MSF 的 payload 分为 Single（单体） 和 Staged（分阶段） 两类。

**Staged payload 采用“两段式”投递**

- 第一段是 Stager（传输器），它是一个极小的代码片段，唯一任务是**建立通信连接并分配内存**

- 第二段是 Stage（主体），通过 Stager 建立的连接下载到目标内存中执行。
  
**这种设计的好处是：** 初始投递的 Stager 体积很小，容易嵌入各种漏洞利用的约束条件中；同时，通信机制与最终 payload 解耦，同一个 Stage 可以配合不同的 Stager（TCP、HTTP、HTTPS）使用。

**命名规则也体现了这种结构** 

windows/x64/meterpreter/reverse_tcp 中
- windows/x64 是平台与架构
- meterpreter 是最终 Stage
- reverse_tcp 是 Stager 的通信方式。


而 windows/x64/meterpreter（没有后缀）则是一个 Single payload，所有功能打包在一起，适合目标无网络出站能力的场景。

## Meterpreter：MSF 的“后渗透核心”
>Meterpreter 是 MSF 最具标志性的高级 Payload，完全在内存中运行，不向磁盘写入主要组件

**技术核心是反射式 DLL 注入（RDI）** metsrv.dll 的头部被修改为可作为 shellcode 使用，通过漏洞投递后在目标进程内存中自行加载，不触发 Windows 标准加载器 API，从而规避基于文件扫描的传统杀软。

**功能扩展机制。** Meterpreter 本身只是一个“协议外壳”，核心能力由扩展提供。stdapi 扩展提供文件操作、进程管理、网络命令等基础功能，会在会话建立后自动加载。其他扩展按需加载，保持核心体积精简。

**通信与配置。** Meterpreter 支持多传输机制，其配置块中存储了会话过期时间、ExitFunc（退出方式）、以及每个传输通道的 URL、重试策略等参数。这使其能够适应复杂网络环境下的持久通信需求。

## post/ 模块：标准化的“后渗透工具箱”
>在机器被攻陷之后使用的模块，用于从已建立的会话中收集、搜集或枚举数据。

*模块的路径名本身就表达了分类逻辑*

- post/windows/gather/ 下的模块是在 Windows 平台上做数据搜集
- post/linux/manage/ 下的是在 Linux 平台上做系统管理类操作

*模块按行为划分*
- gather 是数据搜集与枚举
- gather/credentials 专门偷凭据
- manage 是修改或操作系统（包括会话迁移、进程注入）
- recon 是侦察但不等同于偷数据
- capture 是监控类如键盘记录
- 还有一个历史遗留的 escalate 分类，现在提权模块已经全部归到 exploit 类，但老的模块路径保留了下来。

**常用模块**

- **凭据收集**

  - post/windows/gather/credentials/credential_collector 从内存中收割哈希和令牌
  - post/windows/gather/lsa_secrets 提取 LSA 密钥
  - post/windows/gather/cachedump 读域缓存的凭据
  - post/multi/gather/ssh_creds 搜刮 SSH 私钥
  - Windows 平台下还有一个值得单独提的模块 post/windows/gather/credentials/gpp，它枚举域控并通过 SMB 连接，寻找组策略首选项（GPP）的 XML 文件，用微软公开的 AES 密钥解密其中的本地账户密码。这个模块利用的是管理员在 GPP 里硬编码密码的常见错误。

- **系统枚举**
  
  - post/windows/gather/enum_applications 列出安装的软件
  - post/windows/gather/enum_logged_on_users 看当前登录用户
  - post/windows/gather/enum_shares 枚举共享
  - post/linux/gather/enum_configs 收集 Linux 配置文件
  - Linux 平台还有一个 post/linux/gather/enum_protections，专门检测目标系统是否启用了 SMEP、SMAP、KPTI、SELinux、grsecurity 等内核加固机制，以及是否安装了 tripwire、snort、apparmor 等安全软件。

- **提权辅助**
  
  - post/windows/escalate/getsystem 是老的 getsystem 模块化版本
  - post/multi/recon/local_exploit_suggester 根据目标补丁情况自动推荐可用的本地提权漏洞利用。

- **持久化**
  
  - post/windows/manage/persistence_exe 在 Windows 上安装可执行文件后门
  - post/linux/manage/sshkey_persistence 通过写入 SSH 密钥维持访问
  - post/linux/manage/apache_htaccess_persistence，通过写入恶意 .htaccess 文件并利用 Apache 的 CGI 执行来维持访问，实测在 Metasploitable2 上可以自动建立 Meterpreter 会话。

- **跳板与路由**
  
  - post/multi/manage/autoroute 是最常用的内网路由添加模块
  - 配合 post/multi/manage/socks_proxy 可以实现全协议穿透。

## post模块的底层实现：Mixins
所有 post/ 模块都继承 Msf::Post，通过 include 一系列 Mixins 获得与目标系统交互的能力。
这套设计的关键在于：同一个模块代码可以在 Meterpreter、Shell、PowerShell 三种会话类型上运行，Mixins 帮模块屏蔽了底层的会话差异。

**Msf::Post::Common** 是每个后渗透模块几乎都会 include 的。它提供 cmd_exec 执行命令（旧 API），以及更现代的 create_process 支持带参数的命令执行。还有 get_envs 批量读取环境变量、command_exists? 检查命令是否存在。

**Msf::Post::File** 抽象了文件系统操作。read_file、write_file、directory?、readable? 这些方法在 Windows 和 Linux 上调用方式完全一致，模块开发者不需要为两个平台写两套文件操作代码。expand_path 能自动展开 $HOME 或 %APPDATA% 这类平台特定的路径变量。

**Msf::Post::Process** 处理进程枚举与操作。get_processes 返回进程列表，pidof('nginx') 查找特定进程的 PID，kill_process 终止进程，has_pid? 检查进程是否存在。

平台特定的 Mixin 提供该平台独有的能力。**Msf::Post::Windows** 包含注册表操作、服务管理和 Windows API 访问；**Msf::Post::Linux::System** 提供 is_root? 权限判断和 get_users 用户枚举；**Msf::Post::Unix** 下的 enum_user_directories 可以自动发现用户目录中的 SSH 密钥文件。

