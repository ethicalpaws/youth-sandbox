---
title: 不同Gadget库对比
description: Jackson反序列化漏洞原理与触发链、Spring框架自动反序列化机制、CC链核心原理、三大Gadget库对比分析
tags: [Jackson, Spring, CC链, 反序列化, Gadget, TemplatesImpl, readObject, RequestBody]
status: 已完成
finish-date: 2026-05-17
difficulty: 困难
---

# 不同Gadget库对比
## Jackson
1. Jackson是干什么的：JSON数据<-->Java对象的转换器
2. 核心能力：自动把JSON字符串转成Java对象，把Java对象转成JSON
   ```java
   // 没有Jackson时，你得手动解析JSON
   String json = "{\"name\":\"张三\",\"age\":18}";
   // 手动解析... 很麻烦

   // 有了Jackson，一行搞定
   ObjectMapper mapper = new ObjectMapper();
   User user = mapper.readValue(json, User.class);  // JSON → Java对象
   // user.name = "张三", user.age = 18

   String json2 = mapper.writeValueAsString(user);  // Java对象 → JSON
   ```
3. 反序列化漏洞为什么会出现在Jackson中
   1. 正常用法
      ```java
      // 明确告诉Jackson：转成User类
      User user = mapper.readValue(json, User.class);
      ```
      此时攻击者只能控制JSON中的字段值无法控制创建什么类 
   2. 危险用法（需要配置）
      ```java
      // 告诉Jackson：根据JSON里的@class字段，自己决定创建什么类
      mapper.enableDefaultTyping();  // 开启"多态类型绑定"
      Object obj = mapper.readValue(json, Object.class);  // 注意是Object.class
      ``` 
      攻击者可以通过@class字段指定要创建的类
4. 找到能执行命令的类TemplatesImpl，这个类（用于XSLT转换），它有一个方法：
      ```java
      public synchronized Properties getOutputProperties() {
         // 里面会调用 newTransformer()
         // newTransformer() 会加载 _bytecodes 里的字节码并执行
         return this.newTransformer().getOutputProperties();
      }
      ```
5. 构造恶意JSON数据
   ```json
   {
      "@class": "com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl",
      "_bytecodes": ["yv66vgAA..."],  // 恶意字节码Base64
      "_name": "test",
      "outputProperties": {}  // 触发getOutputProperties()
   }
   ```
6. 完整Jackson工作流程![](java-deserialization(ing)/2026-05-16-15-36-40.png)
   1. 实例化对象：调用无参构造器
      这是 Jackson 反序列化的标准流程。当解析到 JSON 中 `"@class": "com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl"` 时，Jackson 会：
      通过 Class.forName() 加载 TemplatesImpl 类
      调用其无参构造器创建一个空的实例
      ```java
      Class<?> targetClass = Class.forName("com.sun...TemplatesImpl");
      Object obj = targetClass.newInstance();
      ``` 
   2. 填充数据：
      1. 通过字段直接赋值
      创建出空对象后，Jackson 需要将 JSON 中的值填入对象。对于 TemplatesImpl 来说，它没有为关键私有字段（如 _bytecodes、_name）提供 public 的 setter 方法因此，Jackson 会直接使用反射来修改这些私有字段的值。它不关心字段是 private、protected 还是 public，只要能找到这个字段，就会强制将 JSON 中的值（如 Base64 编码的字节码）写入进去 
      2. 处理 "outputProperties": {}：
         1. Jackson解析到"outputProperties"字段
         2. 扫描TemplatesImpl类，发现有getOutputProperties()方法
         3. 推断存在"outputProperties"属性
         4. 没有setter，无法写入新Jackson决定：调用getter读取当前属性值
         5. 调用 getOutputProperties()
            ```
            getOutputProperties() → newTransformer() 
               ↓
            newTransformer() 检查 _name != null ✅
               ↓
            newTransformer() 读取 _bytecodes ✅
               ↓
            加载字节码并实例化
               ↓
            💥 RCE
            ``` 
7. Jackson链的漏洞入口：readValue()
   1. 用法1：指定具体类（安全）
      ```java
      User user = mapper.readValue(json, User.class);
      // 无论JSON里写什么，都只创建User对象
      // ✅ 安全，无法利用
      ``` 
   2. 用法2：指定为Object类（危险，需配合DefaultTyping）
      ```java
      mapper.enableDefaultTyping();  // 先开启多态
      Object obj = mapper.readValue(json, Object.class);
      // ⚠️ 如果JSON里有@class，Jackson会根据@class创建任意类
      // ❌ 有漏洞风险
      ``` 
   3. 用法3：指定为泛型/抽象类（危险，需配合DefaultTyping）
      【泛型让代码能处理"任意类型"，抽象类代表"不完整需要子类填充"。当Jackson遇到目标类型是 Object（最抽象的泛型参数）时，它需要JSON中的@class字段来明确具体类。攻击者利用这一点，让Jackson实例化了TemplatesImpl等危险类，从而触发反序列化漏洞】
      ```java
      mapper.enableDefaultTyping();
      Map<String, Object> map = mapper.readValue(json, new TypeReference<Map<String, Object>>(){});
      // 如果JSON里有@class，Jackson会对Map的value部分应用多态
      // ❌ 有漏洞风险
      ``` 
## Spring
1. Spring是什么：一个工具箱（包含web功能）
2. 作用：Spring Web让开发者写网站更简单
   ```java
   // 没有Spring时，你得写一大堆Servlet代码...
   // 有了Spring，一个注解搞定
   @RestController
   public class MyController {
      
      @PostMapping("/login")
      public String login(@RequestBody User user) {  // ← 重点看这里
         // Spring会自动把HTTP请求里的JSON转成User对象
         System.out.println(user.name + " 尝试登录");
         return "ok";
      }
   }
   ```
3. Spring 链的本质是：
   Spring MVC 的 @RequestBody 自动反序列化机制，调用了底层 Jackson 的 enableDefaultTyping() 多态功能，结合 TemplatesImpl 的 getOutputProperties() 触发链，最终实现远程代码执行。
4. 之所以叫"Spring 链"而非"Jackson 链"，是因为：
   1. 入口是 Spring：@RequestBody 注解驱动
   2. 环境是 Spring：利用 Spring Boot 的自动配置
   3. 传播是 Spring：整个请求处理链在 Spring 框架内完成
   4. 底层的"炸药"依然是 Jackson + TemplatesImpl 的组合。
5. Spring链完整原理
   1. 核心架构：Spring 如何集成 Jackson
      ```java
      @RestController
      public class VulController {
         
         @PostMapping("/data")
         public void process(@RequestBody MyWrapper wrapper) {
            // Spring 自动将 HTTP Body 绑定到 wrapper 对象
            System.out.println(wrapper.getData());
         }
      }

      class MyWrapper {
         private Object data;  // ← 多态的关键点
         
         public Object getData() { return data; }
         public void setData(Object data) { this.data = data; }
      }      
      ```
   2. 为什么叫Spring链
      1. 入口是 Spring 的机制：Spring Web应用中，使用 @RequestBody 注解让Spring自动把HTTP请求体（JSON）转成Java对象。
         ```java
         // Spring 的 RequestResponseBodyMethodProcessor 核心逻辑（简化）
         public class RequestResponseBodyMethodProcessor {
            
            @Override
            public Object resolveArgument(MethodParameter parameter) {
               // 1. 从 HTTP 请求中读取 Body
               HttpInputMessage msg = new ServletServerHttpRequest(request);
               
               // 2. 找到合适的 HttpMessageConverter
               HttpMessageConverter<?> converter = findConverter(parameter);
               
               // 3. 调用 Jackson 转换器
               return converter.read(parameter.getParameterType(), msg);
            }
         }         
         ```
         触发入口：Spring自动处理 @RequestBody这意味着：
         1. 开发者不需要手动调用 mapper.readValue()
         2. Spring在框架内部悄悄调用了Jackson（或其它HttpMessageConverter）
         3. 攻击者只需要发送一个HTTP请求到有这个注解的接口
      2. Spring 自动配置了 Jackson
         ```java
         // Spring Boot 自动配置
         @Configuration
         public class JacksonAutoConfiguration {
            
            @Bean
            public ObjectMapper jacksonObjectMapper() {
               ObjectMapper mapper = new ObjectMapper();
               
               // ⚠️ 关键：Spring Boot 1.x 默认开启 DefaultTyping
               // 这会导致多态反序列化漏洞
               mapper.enableDefaultTyping();
               
               return mapper;
            }
         }
         ```
         Spring Boot 1.x 的情况：Spring Boot 1.x 为了"开箱即用"，默认配置了Jackson的某些多态特性结果，开发者什么都没做，Spring已经帮他们开启了危险配置！
         Spring Boot 2.x 及以后：修复了这个"默认不安全"的问题，默认不再开启多态类型绑定。但仍然可能存在其他漏洞或配置。
   3. 攻击流程详解
      1. 客户端构造恶意 JSON
         ```json
         POST /data HTTP/1.1
         Content-Type: application/json

         {
            "data": {
               "@class": "com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl",
               "_bytecodes": ["yv66vgAAADQ...（Base64 恶意类）"],
               "_name": "pwned",
               "_tfactory": {},
               "outputProperties": {}
            }
         }
         ```
      2. Spring 解析参数
         ```java
         // Spring 看到 @RequestBody MyWrapper
         // 知道需要将 JSON 绑定到 MyWrapper 对象

         MyWrapper wrapper = new MyWrapper();  // 创建目标对象
         // 开始填充 data 字段...         
         ```  
      3. Jackson 处理多态
         ```java
         // Jackson 看到 MyWrapper.data 是 Object 类型
         // 需要根据 @class 决定实例化哪个具体类

         JavaType targetType = mapper.constructType(MyWrapper.class);
         // 解析 JSON 中的 @class: TemplatesImpl
         // 调用 TemplatesImpl 无参构造器创建实例         
         ``` 
      4. 触发漏洞
         ```java
         // Jackson 填充 outputProperties 字段时
         // 找不到 setter，调用 getOutputProperties()
         // → newTransformer() → 加载字节码 → RCE         
         ```
6. Spring 链核心要素详解
      1. 入口：Spring MVC 自动参数绑定【@RequestBody 注解触发自动反序列化】
      2. 触发方式：Web请求 → 框架自动解析
      3. 关键点：@RequestBody + Object类型【Spring链 = Jackson链的配置前提（多态支持）+ 触发入口（@RequestBody）】
      4. 依赖：spring-web + spring-beans + jackson
         spring-web（提供@RequestBody）【入口触发器】
         jackson-databind（提供多态解析）【实际解析器】
         spring-beans（提供参数绑定）【值绑定器】
7. ![](java-deserialization(ing)/2026-05-16-16-45-28.png)
## CC链
1. 核心原理：readObject() → 调用链 → Transformer.transform() → 反射执行任意方法
2. 关键特点：
   1. 直接反射：InvokerTransformer包装任意方法调用
   2. 链式组合：ChainedTransformer串联多个操作
   3. 无需额外配置：只要classpath中有CC依赖就可能触发
3. 限制条件
   1. CC1链：jdk8u71之前可用（AnnotationInvocationHandler修复）
   2. CC2/CC4：需要javassist（部分版本）
   3. CC6：无jdk版本限制
## 对比
![](java-deserialization(ing)/2026-05-16-16-35-58.png)