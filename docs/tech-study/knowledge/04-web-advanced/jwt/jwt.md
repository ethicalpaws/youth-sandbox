

# JWT
## 什么是JWT
>JWT——JSON Web Token

JSON 网页令牌(JWT)是一种标准化格式,用于在系统之间发送密码学签名的 JSON 数据。理论上它们可以包含任何类型的数据,但最常用于发送用户信息(“声明”),作为身份验证、会话处理和访问控制机制的一部分

## JWT的格式
>JWT由三部分组成——header,payload,signature,由点号分隔
>
>JWT 的头部和有效载荷部分只是 base64编码的 JSON 对象

```
eyJraWQiOiI5MTM2ZGRiMy1jYjBhLTRhMTktYTA3ZS1lYWRmNWE0NGM4YjUiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTY0ODAzNzE2NCwibmFtZSI6IkNhcmxvcyBNb250b3lhIiwic3ViIjoiY2FybG9zIiwicm9sZSI6ImJsb2dfYXV0aG9yIiwiZW1haWwiOiJjYXJsb3NAY2FybG9zLW1vbnRveWEubmV0IiwiaWF0IjoxNTE2MjM5MDIyfQ.SYZBPIBg2CRjXAJ8vCER0LA_ENjII1JakvNQoP-Hw6GG1zfl4JyngsZReIfqRvIAEi5L4HV0q7_9qGhQZvy9ZdxEJbwTxRs_6Lb-fZTDpW6lKYNdMyjw45_alSCZ1fypsMWz_2mTpQzil0lOtps5Ei_z7mM7M8gCwe_AGpI53JxduQOaB5HkT5gVrv9cKu9CsW5MS6ZbqYXpGyOG5ehoxqm8DL5tFYaW3lB50ELxi0KsuTKEbD0t5BCl0aCR2MBJWAbN-xeLwEenaqBiwPVvKixYleeDQiBEIylFdNNIMviKRgXiYuAvMziVPbwSgkZVHeEdF5MQP1Oe2Spac-6IfA
```

- Header（头部）：声明了Token的类型（JWT）和签名算法（如HS256或RS256）。

- Payload（载荷）：这是核心信息区。服务器会把“用户ID”、“用户名”等非敏感信息放在这里。同时，它还会包含几个标准字段，其中最重要的是 exp（过期时间），用于控制Token的有效期。

- Signature（签名）：服务器将Header和Payload拼接后，用密钥（Secret）和指定的算法进行加密，生成一段字符串。这个签名是防篡改的关键。

    - 由于签名直接来自令牌的其余部分,因此更改一个节点或有效载荷的字节会导致签名不匹配。

    - 在不知道服务器秘密签名密钥的情况下,不应能够为给定的头部或有效载荷生成正确的签名。

## JWT认证流程

- 第一阶段：颁发Token（登录环节）
  
  - 用户发起登录请求：用户在客户端（如浏览器App）输入用户名和密码，通过HTTPS协议发送给服务器。

  - 服务器验证身份：服务器收到请求，查询数据库，验证用户名和密码是否匹配。

  - 生成JWT：验证通过后，服务器会创建一个JWT。
  
  - 返回Token给客户端：服务器将完整的JWT字符串发送给客户端。

  - 客户端存储Token：客户端（如浏览器的LocalStorage或Cookie）接收到JWT后，会将其保存起来，供后续请求使用。

- 第二阶段：使用Token（访问资源环节）
  
  - 客户端携带Token发送请求：当用户要访问一个需要登录才能查看的页面或数据时，客户端会在HTTP请求的 Authorization 请求头中加上Token，格式通常是 Bearer <JWT字符串>。

  - 服务器拦截并验证Token：服务器的后端服务（或中间件）会拦截这个请求，并执行以下关键校验步骤：

    - 格式校验：检查Header中是否有 Authorization 字段，以及Token是否以 Bearer 开头。

    - 结构解析：尝试将Token按点号拆分为三部分，如果不是三段，则直接拒绝。

    - 签名验真（最关键）：服务器用自己存储的密钥，对接收到的Header和Payload重新计算一次签名，并与Token自带的签名进行比对。

      - 若一致，说明Token在传输过程中未被篡改，且确实是由本服务器颁发的。

      - 若不一致，直接拒绝请求。

    - 有效期检查：解析Payload中的 exp（过期时间）字段，与当前服务器时间比较。如果当前时间已超过过期时间，则判定Token失效，返回401错误（未授权）。

  - 获取用户信息并处理业务：所有校验通过后，服务器会认为这个请求是可信的。此时，它会直接从Payload中取出用户ID等信息，而无需再去查询数据库。利用这些信息，服务器就能执行具体的业务逻辑（如查询该用户的订单、修改资料等）。

  - 返回响应结果：服务器将处理后的数据返回给客户端。

## JWT vs JWE vs JWS
JWT 的规格实际上非常有限。它仅将信息(“权利声明”)定义为可以在双方之间传输的JSON对象。实际上,JWT 并未真正被用作独立实体。JWT 规范通过 JSON Web 签名(JWS)和 JSON Web 加密(JWE)规范来扩展,这些规范定义了实际实现 JWT 的具体方法。 

换句话说,JWT通常是JWS或JWE。当人们使用“JWT”这个术语时,它们几乎总是指JWS。JWE 非常相似,只是令牌的实际内容是加密的,而不仅仅是编码的。 

## JWT攻击
### 什么是JWT攻击
>JWT 攻击涉及用户向服务器发送修改后的 JWT,以实现恶意目标。通常,此目标是通过冒充另一位已经过身份验证的用户来绕过身份验证和访问控制。 

### JWT攻击的影响是什么
>JWT攻击的影响通常很严重。如果攻击者能够创建具有任意值的有效token,他们可以升级自身权限或冒充其他用户,完全掌控账户。
### JWT攻击漏洞是如何产生的
>JWT的签名没有得到正确验证。这使得攻击者能够篡改通过令牌有效载荷传递给应用程序的值。即使签名经过了可靠的验证,其是否真正可信,仍需在很大程度上依赖服务器的密钥,而密钥仍是一个秘密。如果该密钥以某种方式被泄露,或可能被猜测或被蛮力攻击,攻击者可以为任意令牌生成有效的签名,从而破坏整个机制。 
>
>服务器通常不会存储其发布的JWT的任何信息。相反,每个token都是完全独立的实体。这具有一些优点,但也带来了一个根本性问题——服务器实际上对令牌的原始内容,甚至对原始签名内容一无所知。因此,如果服务器无法正确验证签名,则无法阻止攻击者对令牌的其余部分进行任意更改。

### 接受任意签名
> JWT库通常提供一种用于验证令牌的方法,另一种则仅用于解码。例如,Node.js 库jsonwebtoken有verify()和decode()。

>然而有时,开发者会混淆这两种方法,只将传入的token传递给decode()方法，这实际上意味着应用程序完全无法验证签名。 

**题目描述**
![](jwt/2026-07-24-09-30-47.png)

**解题过程**
*登录已有账号*
![](jwt/2026-07-24-09-37-04.png)

*抓包查看token*
![](jwt/2026-07-24-09-38-15.png)

*解码token*
![](jwt/2026-07-24-09-40-09.png)

*篡改token*
![](jwt/2026-07-24-10-43-24.png)

*携带伪造的token访问/admin*
![](jwt/2026-07-24-10-43-08.png)

*冒充admin执行恶意操作*
![](jwt/2026-07-24-10-44-53.png)

### 接受无签名token
>在JSON Web Token (JWT) 的上下文中，none是一个特殊的算法标识。如果服务器配置不当，接受了alg=none的令牌，攻击者就可以伪造任意身份，彻底绕过认证，这和WAF的检测规则是不同层面的安全问题。
>
>原理：JWT头部定义了签名算法alg。当alg被设为none时，JWT标准要求服务器不验证签名。如果服务器未禁用此算法，攻击者只需将头部alg改为none，篡改payload内容，并去掉签名部分（保留末尾的点.），即可构造一个"有效"令牌
>JWT 可以使用多种不同算法进行签名,但也可以保持无符号。在这种情况下,alg参数设置为none,由于这存在明显危险,服务器通常会拒绝没有签名的代币。然而,由于这种过滤依赖于字符串解析,有时可以使用经典的混淆技术绕过这些滤镜,例如混合大小写和编码

**题目描述**

![](jwt/2026-08-09-09-56-26.png)

**解题过程**

*访问/admin接口*

![](jwt/2026-08-09-10-10-41.png)

*伪造无签名token*

![](jwt/2026-08-09-10-16-37.png)

*访问delete接口*

![](jwt/2026-08-09-10-17-43.png)
![](jwt/2026-08-09-10-19-19.png)

### 弱密钥暴力破解 (Weak Secret Brute-Force)
>原理：针对使用对称加密算法（如 HS256）的JWT，其安全性完全依赖于密钥（Secret）的强度。如果开发者使用了弱密钥（如 secret、password 或留空），攻击者就可以在本地进行高强度的离线计算。
>
- 工具与技巧：

  - Hashcat模式：-m 16500 专门用于破解JWT。由于是本地运算，不受网络延迟限制，配合GPU可以在极短时间内跑完数亿级别的字典。

  - 规则扩展：除了固定字典，攻击者常结合 --rules 规则（如大小写变形、数字后缀）来爆破 admin、test 等变种。

  - “字符级”暴力：若密钥极短（如单个字符），可完全不依赖字典，直接遍历ASCII码空间。

- hashcat.exe -a 0 =m 16500 <jwt> <wordlist> --show

**题目描述**

![](jwt/2026-08-09-11-20-54.png)

**解题过程**

*登录后抓包获取jwt*

![](jwt/2026-08-09-11-26-38.png)

```
eyJraWQiOiJjNTdlZGFmZC0yOWYwLTRjZGMtOGQ3MS05YzgzODM2NzY5ZWQiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc4NjI0OTM2Niwic3ViIjoid2llbmVyIn0.ovUMepw6FdX4mT5BiXbq2gASOCp68D3hag6v3CuI6v4
```
*hashcat暴力破解*

```
hashcat.exe -a 0 -m 16500 "eyJraWQiOiJjNTdlZGFmZC0yOWYwLTRjZGMtOGQ3MS05YzgzODM2NzY5ZWQiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc4NjI0OTM2Niwic3ViIjoid2llbmVyIn0.ovUMepw6FdX4mT5BiXbq2gASOCp68D3hag6v3CuI6v4" E:\youth-sandbox\docs\tech-study\arsenal\wordlist\jwt.secrets.list.txt
```

![](jwt/2026-08-09-11-31-50.png)

*秘钥：secret1*

*对秘钥进行base64编码*

![](jwt/2026-08-09-11-44-43.png)

*burp中新建秘钥*

![](jwt/2026-08-09-11-46-51.png)

*使用刚刚生成的秘钥签名伪造jwt*

![](jwt/2026-08-09-11-48-33.png)

*使用伪造的jwt访问/admin接口*

![](jwt/2026-08-09-11-52-32.png)
![](jwt/2026-08-09-11-54-04.png)

### 头部参数注入 (Header Parameter Injections)
>这是JWT攻击中最危险、变种最多的部分。其核心逻辑是：既然服务器要验证签名，那么我直接告诉服务器“用我的公钥来验证我的签名”

#### jwk (JSON Web Key) 注入
>机制：在头部直接嵌入一个完整的公钥对象。
>
>攻击动作：攻击者本地生成一对RSA密钥，用私钥签发恶意JWT，将公钥放入 jwk 头。若服务器信任该参数，则验证通过。
>
>进阶绕过：部分服务器只检查 jwk 是否存在而不验证来源，插件（如Burp的JWT Editor）能自动生成匹配的 kid 和签名，一键完成攻击。

**示例**

```
{
    "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG",
    "typ": "JWT",
    "alg": "RS256",
    "jwk": {
        "kty": "RSA",
        "e": "AQAB",
        "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG",
        "n": "yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9m"
    }
}
```

**题目描述**

![](jwt/2026-08-09-12-09-19.png)

**解题过程**

*生成新的RSA秘钥对*

![](jwt/2026-08-09-12-28-58.png)

*抓包伪造jwt*

![](jwt/2026-08-09-12-10-05.png)

*使用伪造的jwt访问/admin接口*

![](jwt/2026-08-09-12-33-22.png)
![](jwt/2026-08-09-12-35-43.png)

#### jku (JWK Set URL) 注入
>机制：服务器根据该URL去远程获取包含公钥的JSON文件。
>
>攻击路径：攻击者搭建一个公网服务，托管一个包含自己公钥的 jwks.json，将 jku 指向该地址。

- 绕过SSRF限制：即便服务器限制只能从 https://trusted.com 获取，攻击者也可以利用：

  - 开放重定向：https://trusted.com/redirect?url=evil.com

  - URL解析差异：https://trusted.com@evil.com 或使用 \ 分隔符绕过正则匹配。

**题目描述**

![](jwt/2026-08-09-13-22-14.png)

**解题过程**

*新建秘钥对，复制公钥*

![](jwt/2026-08-09-13-29-30.png)

*在恶意服务器配置jwk集*

![](jwt/2026-08-09-14-36-54.png)

*伪造jwt，使用相同kid的jwk生成签名*

![](jwt/2026-08-09-14-34-45.png)

```
{
"keys": [
{
    "kty": "RSA",
    "e": "AQAB",
    "kid": "a855e9d9-d6ea-4575-9d4d-9557575fa4cd",
    "n": "wNPibqDAETPCsh4Iq5QZqZvqJuTV8N66lnDMxIa5if0zWhs_EyosRFDSxN18mtkUpsXvLAwT-JfACHNEB1bj66NbdZoxEYvwljUHT8vBa-flhs4mwLrC0zEaYtsuHdrou5Q2Qb3co_V_7WEnKCmh9gs0KclJcVjS5c793tQ8QZILo0ZXVci_JR78MRasVSMOzSHX7d5cb5UKaIwmCdHQo99-mKHGWWjAdpDLM6aZn8aHzrAd6KIvm4WnLLIEkw6GnSnlKAQxwEc1uwfRRI4qYEDmzPgGDbl_9S6BOM9GMXgFa51sbkfNIPOSDiSyXRtv97PsFBOvaS8m1gMfhWASMQ"
}
]
}
```

*使用伪造的jwt访/admin接口*

![](jwt/2026-08-09-14-34-06.png)
![](jwt/2026-08-09-14-36-42.png)


#### kid (Key ID) 路径遍历与注入
>机制：kid 用于在服务器文件系统或数据库中查找密钥文件。

**攻击手法**

- 文件读取攻击：若服务器存在路径遍历漏洞（如 ../../../../dev/null），且使用对称加密（HS256），则会发生“空密钥签名”的灾难性后果。同理，指向 /proc/self/environ 或日志文件也可能泄露密钥。

- SQL注入攻击：若 kid 用于查询数据库（如 SELECT key FROM keys WHERE kid='<input>'），攻击者可通过 ' OR 1=1 -- 

- 理论上可以用任何文件来执行,但最简单的方法之一就是使用/dev/null在大多数Linux系统中都存在。由于这是一个空文件,因此读取它返回一个空字符串。因此,使用空字符串签名令牌将获得有效的签名

**题目描述**

![](jwt/2026-08-09-15-27-21.png)

**解题过程**

*新建对称密钥伪造kid和k*

![](jwt/2026-08-09-15-42-55.png)

```
{
    "kty": "oct",
    "kid": "..\/..\/..\/..\/..\/..\/..\/..\/dev\/null",
    "k": ""
}
```

*使用伪造的秘钥生成签名*

![](jwt/2026-08-09-15-44-13.png)

*使用伪造的jwt访问/admin接口*

![](jwt/2026-08-09-15-44-49.png)
![](jwt/2026-08-09-15-45-29.png)

#### 其他可利用参数

- cty (Content Type)：如果将类型改为 application/x-java-serialized-object 或 text/xml，后端反序列化或XML解析器可能触发远程代码执行（RCE）或XXE（XML外部实体注入）攻击。

- x5c (X.509证书链)：类似于 jwk，传递证书而非公钥。历史上著名的漏洞（如CVE-2017-2800）利用该参数进行堆溢出攻击。
****

### 算法混淆攻击 (Algorithm Confusion)
> 原理：服务器本应使用非对称算法（RS256）验证签名（公钥解密，私钥加密）。但攻击者将头部 alg 改为对称算法（HS256），并尝试将公钥当作对称密钥来签名。
>
>关键条件：攻击者必须能获取到服务器的公钥（通常通过 /.well-known/jwks.json 获取）。当服务器试图用公钥（被误当成HMAC密钥）去验证攻击者用相同公钥签名的token时，验证会通过。
>
>变种：CVE-2026-22817（Hono框架）正是利用了这种非对称转对称的逻辑缺陷。

**对称 vs 非对称算法对比**

| 特性 | 对称算法 (HS256) | 非对称算法 (RS256) |
|------|------------------|-------------------|
| 密钥类型 | 单一密钥（对称） | 公钥 + 私钥（非对称） |
| 签名方 | 服务器（用密钥签名） | 服务器（用私钥签名） |
| 验证方 | 服务器（用同一密钥验证） | 任何人（用公钥验证） |
| 密钥保密性 | 必须绝对保密 | 私钥保密，公钥公开 |
| 攻击关键 | 爆破弱密钥 | 诱使服务器用公钥验证 HS256 |

**完整攻击流程**

*Step 1: 获取服务器公钥*

- 方式 A：标准 JWKS 端点

- 方式 B：从 X.509 证书中提取

- 方式 C：从多个 JWT 中推导

*Step 2: 将公钥转换为 HMAC 兼容格式*

*Step 3: 伪造 JWT*

*Step 4: 使用公钥签名JWT*

**题目描述**

![](jwt/2026-08-09-14-56-20.png)

**解题过程**

*通过标准端点暴露公钥*

![](jwt/2026-08-09-14-58-25.png)

```json
{"keys":[{"kty":"RSA","e":"AQAB","use":"sig","kid":"701e9483-362e-4ce9-aa72-bf11fa6f8670","alg":"RS256","n":"ySpgp58nh6fMXdKxnol2mSSMBGmb29o1qoOgOlBw5srM-2CTSZhHLTUmFYov5P9AOlHDP_HhFKwwdBu7-pls9WqaBKRSPbT3qLBuPovJxvH8pbMwjYjyEmNK0CwGYB4LC6o40V60R-nUqLPWZfXKG5Fo4vrbFHfmI8FZqhZWotat_YUZ03-5wB0ZSesmXCOf6tVgCkkMyaBBK8vMZwbvSuGHrnYa3o_BX204ccrlii0fUcjLr_ncT3xrRy8dVRHBWG2O_qJcH-TRblVCg9OMdsm87bTsHIxmev2J3H418Rtke-6VVTgNmiGJvQufmGORjpLRcDHWDPax0I7drSPc2w"}]}
```

*将公钥转换为合适的格式*

- 新建RSA秘钥，将刚刚获得的服务器上的公钥复制上去

  ![](jwt/2026-08-09-15-03-52.png)

- 将刚刚新建的RSA公钥保存为PEM格式

  ![](jwt/2026-08-09-15-05-09.png)

- 将保存的PEM格式公钥进行base64编码

  ![](jwt/2026-08-09-15-15-02.png)

*新建对称秘钥将k值替换为合适格式的公钥*

![](jwt/2026-08-09-15-09-23.png)

*伪造jwt算法，使用新建的对称密钥算法签名*
## 如何防止JWT攻击

