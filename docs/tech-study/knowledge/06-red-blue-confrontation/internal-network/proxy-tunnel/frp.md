---
title: FRP 代理
description: FRP C/S 架构、配置与内网代理隧道搭建
tags: [隧道, 代理, frp, 内网]
status: 已完成
finish-date: 2026-10-20
difficulty: 中等
---

# frp代理
>frp 是一个专注于内网穿透的高性能反向代理应用，核心作用是将没有公网 IP 的内网服务，通过一台有公网 IP 的中转服务器安全地暴露到公网

- **核心架构：C/S 模式**

  - frp 采用客户端/服务端架构，由两个核心组件构成：

    - frps（服务端）：部署在具有公网 IP 的机器上（如云服务器、VPS）。它作为流量中转枢纽，监听来自客户端的连接，并将公网用户的请求转发给对应的内网服务。

    - frpc（客户端）：部署在需要被穿透的内网机器上（如公司电脑、家庭 NAS）。它主动向服务端发起长连接，将本地的服务端口注册到服务端。

  - 由于是内网客户端主动向外连接，因此无需在路由器上配置端口映射，能有效穿透 NAT 和防火墙。

- **配置与使用（以 TCP 穿透 SSH 为例）**

  - 虽然新版 frp 已转向 TOML 格式，但 ini 格式仍被广泛使用且易于理解。以下是最小化的配置示例。

    - 服务端配置（frps.ini）
      在公网服务器上编辑配置文件，核心是设置客户端连接端口和认证令牌：

      ```ini
      [common]
      bind_port = 7000          # frpc 连接 frps 的端口
      token = your_secure_token # 身份验证密钥，客户端需保持一致
      ```
    - 客户端配置（frpc.ini）
      在内网机器上配置，指定要穿透的本地服务：

      ```ini
      [common]
      server_addr = 1.2.3.4     # 公网 frps 的 IP 地址
      server_port = 7000        # 对应 frps 的 bind_port
      token = your_secure_token # 与服务端一致

      [ssh]                     # 自定义代理名称
      type = tcp                # 代理类型
      local_ip = 127.0.0.1      # 本地服务地址
      local_port = 22           # 本地 SSH 端口
      remote_port = 6000        # 在公网服务器上暴露的端口
      ```
    - 启动与访问

      - 启动：分别运行 ./frps -c frps.ini（服务端）和 ./frpc -c frpc.ini（客户端）。

      - 访问：此时，通过 ssh -p 6000 user@1.2.3.4 即可连接到内网的 SSH 服务。

- **关键代理类型与安全考量**
  frp 提供了多种代理类型以适应不同场景：

  - TCP/UDP：最基础的端口映射，适用于 SSH、远程桌面、游戏联机等。

  - HTTP/HTTPS：专为 Web 服务设计，支持基于域名（custom_domains）的虚拟主机路由，方便在同一个端口暴露多个网站。

  - STCP/XTCP：安全 P2P 模式。STCP 要求访问者也部署 frpc，不在服务端暴露端口；XTCP 则尝试点对点直连，流量不经过服务器中转，更私密且节省服务器带宽。

- **安全提醒**：将内网服务暴露到公网会显著增加风险。务必设置强壮的 token 并启用 TLS 加密（tls_enable = true）。对于敏感服务（如数据库），应通过防火墙或 frp 的 allow_ports 限制访问来源，避免直接暴露给全网。
