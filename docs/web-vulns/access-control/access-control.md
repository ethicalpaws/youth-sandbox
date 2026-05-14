### 什么是访问控制
1. 在web应用中，访问控制决定了谁可以对何种资源执行什么操作
2. 容易混淆的概念
   1. 身份认证：确认你是谁
   2. 会话管理：维持后续的请求状态
   3. 访问控制：决定有什么权限
3. 核心观点：认证通过不等于拥有权限。绝大多数漏洞发生在开发者完成了认证校验，却忘记了授权校验。
### 访问控制的类型
1. 垂直访问控制：不同角色之间的权限差异【管理员&普通用户】
2. 水平访问控制：相同角色不同用户之间的数据隔离【用户A的订单&用户B的订单】
3. 依赖上下文的访问控制：基于应用状态或操作顺序的限制【必须先提交订单才能结算，不能直接请求结算接口】 
### 越权访问示例
1. 垂直越权
   1. 无保护功能（隐藏URL）
      1. 漏洞原因：开发者认为“只要不在菜单里放链接，用户就找不到”
      2. 实战手法：
         1. 目录爆破：使用ffuf、dirsearch或Burp Intruder，字典包含/admin、/management、/console、/api/swagger
         
         2. 前端泄露：查看JS文件。搜索location.href、window.open或apiUrl，经常能发现未公开的管理接口或相关逻辑。
            1. 实战示例：![](访问控制+越权实验报告/2026-05-12-12-19-03.png)![](访问控制+越权实验报告/2026-05-12-12-18-28.png)通过script脚本泄露接口
         3. 信息泄露文件：
            1. 检查robots.txt、sitemap.xml、.git/HEAD。
            2. 实战示例：![](访问控制+越权实验报告/2026-05-12-11-12-18.png)通过robors.txt文件发现/administrator-panel接口
   2. 基于参数的访问控制
      1. 漏洞原因：服务端完全信任客户端传递的“权限标识”
      2. 实战手法
         1. 修改Cookie：抓包发现Cookie: role=user，改为role=admin或role=administrator
            
         2. 修改请求参数：URL中带有?isAdmin=false、?permission=view，直接改为true或edit
         3. 修改隐藏表单的值：HTML中`<input type="hidden" name="userType" value="normal">`，改为`value="admin"`。
      3. 实战演练：![](访问控制+越权实验报告/2026-05-12-12-24-59.png)![](访问控制+越权实验报告/2026-05-12-12-41-49.png)登录普通用户，发现服务端会返回一个维持会话的session，改包，将Admin的值改为true之后重新发送，服务端返回来一个admin用户的session值
         1. 将访问主页面的请求包的session修改为admin的值，将Admin改为true重新发送![](访问控制+越权实验报告/2026-05-12-12-45-20.png)发现返回页面多了一个Admin panel接口，跳转链接为/admin![](访问控制+越权实验报告/2026-05-12-12-47-03.png)
         2. 访问该链接，burp拦截修改session和Admin之后发送成功进入管理员后台![](访问控制+越权实验报告/2026-05-12-12-48-20.png)
   3. 平台配置错误（绕过WAF与网关）
      1. HTTP方法绕过：某些API限制POST /admin/delete。尝试发送GET /admin/delete或PUT /admin/delete。如果后端控制器没有区分Method，可能会执行删除操作
         1. 实战演练：![](访问控制+越权实验报告/2026-05-12-18-22-56.png)![](访问控制+越权实验报告/2026-05-12-18-34-47.png)
      2. Header覆盖：利用X-Forwarded-For、X-Original-URL、X-Rewrite-URL、X-HTTP-Method-Override。【经典Payload：请求GET / HTTP/1.1，添加Header`X-Original-URL: /admin/deleteUser`。网关可能只检查了原始路径/，而后端却执行了/admin/deleteUser】
         1. 实战演练：![](访问控制+越权实验报告/2026-05-12-18-14-33.png)![](访问控制+越权实验报告/2026-05-12-18-16-49.png)![](访问控制+越权实验报告/2026-05-12-18-21-19.png)
      3. URL匹配差异：
         1. 后缀绕过：Spring Boot若开启useSuffixPatternMatch，请求/admin/deleteUser.json可能匹配/admin/deleteUser，绕过路径权限规则。
         2. 大小写与编码：尝试/ADMIN或/%61dmin（URL编码）。
2. 水平越权【原理：未验证当前用户是否拥有所请求资源的所属权。】
   1. 不安全的直接对象引用 (IDOR)【开发者在SQL查询中直接使用where id = $_GET['id']，忘记了加上and user_id = session_id】
      1. 数字ID遍历
         1. 实战演练：![](访问控制+越权实验报告/2026-05-12-19-40-31.png)修改id即可![](访问控制+越权实验报告/2026-05-12-19-39-48.png)
      2. 文件名/路径遍历
         1. 实战演练：![](访问控制+越权实验报告/2026-05-13-01-45-39.png)![](访问控制+越权实验报告/2026-05-13-02-05-02.png)
      3. GUID/UUID预测：虽然难以枚举，但GUID可能在其他地方泄露（如评论区的头像URL：/images/avatar/a1b2c3d4.png），或基于时间戳生成（弱随机）。
         1. 实战演练：![](访问控制+越权实验报告/2026-05-12-19-29-11.png)找到用户的uid![](访问控制+越权实验报告/2026-05-12-19-29-37.png)替换即可越权
    2. 重定向中的数据泄露
       1. 现象：当你水平越权访问他人数据时，服务器返回302跳转到/login。
       2. 漏洞：在浏览器跳转前，Burp Suite捕获的响应体（Response Body）中，可能已经包含了完整的敏感JSON数据（如用户手机号、地址）。开发者仅做了重定向，未清空响应缓冲区。
       3. 实战演练：![](访问控制+越权实验报告/2026-05-12-19-43-23.png)修改id并查看原始响应中![](访问控制+越权实验报告/2026-05-12-19-42-03.png)
    3. 从横向到纵向的升级：
       1. 原理：先通过IDOR获取了管理员用户的api_token或password reset hash，然后用这个令牌去执行垂直越权操作
       2. 实战演练：![](访问控制+越权实验报告/2026-05-12-23-21-13.png)![](访问控制+越权实验报告/2026-05-12-23-47-55.png)查看源码获得密码![](访问控制+越权实验报告/2026-05-13-00-10-21.png)![](访问控制+越权实验报告/2026-05-13-00-10-31.png)成功登录
3. 其他场景
   1. 多步骤流程中的访问控制漏洞
      1. 场景：修改密码流程 -> 步骤1：验证旧密码；步骤2：输入新密码；步骤3：提交更新。
      2. 漏洞：步骤3的接口没有校验“是否完成了步骤1和2”。
      3. 利用：直接使用Burp Repeater重放步骤3的请求包（仅包含新密码），即可绕过旧密码验证，重置任意用户密码。
   2. 基于 Referer 的访问控制
      1. 原理：API检查请求头中的Referer: https://trusted-site.com/admin来放行。
      2. 缺陷：HTTP头完全可控。
      3. 绕过：伪造Referer: https://target.com/admin，或者如果校验不严格，使用Referer: https://target.com/evil?admin
      4. 实战演练：
   3. 基于位置的访问控制
      1. 原理：仅允许特定IP段（如内网/公司VPN）访问后台。
      2. 绕过：
         1. 添加Header：X-Forwarded-For: 127.0.0.1、X-Real-IP: 192.168.1.1。
         2. 寻找CloudFlare或其他CDN的真实IP泄露。
         3. 如果目标限制不严，使用代理/VPN进入白名单IP范围。
### 如何防御
1. 默认拒绝原则 (Deny by Default)：
   1. 所有接口、方法、目录，除非明确声明为PUBLIC，否则一律视为PRIVATE。反例：先写允许逻辑，最后加拒绝逻辑。
2. 单一的全局鉴权机制：
   1. 不要在每个Controller方法里写if(role==admin)。使用框架统一的拦截器（Interceptor）、中间件（Middleware）或过滤器（Filter）。
   2. 推荐：Spring Security @PreAuthorize、ASP.NET [Authorize] 属性、Express.js passport + 自定义中间件。
   3. 代码级声明：
      1. 权限必须与业务代码绑定，而不是写在配置文件中（配置文件容易遗忘）。使用注解是较好的实践：
       java
         @PreAuthorize("hasPermission(#userId, 'User', 'read')")
         public User getUser(String userId) { ... }
3. 服务端强制校验 (永不信任前端)：
   1. 禁止依赖隐藏输入框、前端JS变量、不可见的菜单。
   2. 禁止依赖客户端传来的role、isAdmin参数。
   3. 必须从服务端的Session或JWT解析出当前用户ID，与请求的目标资源Owner ID进行比对。

