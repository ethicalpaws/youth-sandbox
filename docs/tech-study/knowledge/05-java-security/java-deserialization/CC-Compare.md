---
title: CC链对比分析
description: Commons Collections CC1-CC7 各链多维对比，包括入口点、跳板、JDK限制、CC版本、执行方式等
tags: [cc1, cc2, cc3, cc4, cc5, cc6, cc7, deserialization, compare]
status: 已完成
finish-date: 2026-05-30
difficulty: 中等
---

## CC1、CC5、CC6、CC7 多维度详细对比

| 维度 | CC1 | CC5 | CC6 | CC7 |
|------|-----|-----|-----|-----|
| **入口点** | AnnotationInvocationHandler | BadAttributeValueExpException | HashMap | Hashtable |
| **入口点来源** | sun.reflect.annotation (JDK内部) | javax.management (JMX组件) | java.util (基础集合) | java.util (基础集合) |
| **入口类特点** | 动态代理处理器，实现了 InvocationHandler 和 Serializable | 处理属性值异常，其 readObject() 会调用 valObj.toString() | 最常用的Map实现，readObject() 会重建内部存储，遍历所有键值对 | 古老的Map实现，readObject() 逻辑与 HashMap 略有不同 |
| **关键跳板对象** | LazyMap | TiedMapEntry | TiedMapEntry | AbstractMap (通过 Hashtable 的 reconstitutionPut) |
| **跳板方法** | LazyMap.get() | TiedMapEntry.toString() → getValue() → LazyMap.get() | TiedMapEntry.hashCode() → getValue() → LazyMap.get() | AbstractMap.equals() (通过 Hashtable 调用) |
| **入口点如何触发跳板** | readObject() 中遍历 memberValues，调用 entrySet()，触发代理，最终调用 LazyMap.get() | readObject() 中调用 valObj.toString() | readObject() 中重建Map时，会计算每个键的 hashCode() | readObject() 中重建Map时，会调用 equals() 方法来定位键值对 |
| **命令执行方式** | InvokerTransformer → Runtime.exec() | 同 CC1 | 同 CC1 | 同 CC1 |
| **JDK 版本限制** | JDK 8u71 及以下 | 无限制 | 无限制 | 无限制 |
| **CC 版本限制** | commons-collections 3.1-3.2.1 | 同 CC1 | 同 CC1 | 同 CC1 |
| **调用链长度** | 最长 (涉及动态代理) | 较短 (直接从 TiedMapEntry 开始) | 较短 (直接从 TiedMapEntry 开始) | 中等 |
| **利用思路核心** | 通过动态代理，巧妙地将 entrySet() 调用转换为 LazyMap.get() | 利用 TiedMapEntry 作为桥梁，将 toString() 调用导向 LazyMap.get() | 同 CC5，但触发点是 hashCode() | 利用 Hashtable 反序列化时的特殊逻辑触发 equals() |
| **攻击链稳定性** | 低 (受JDK版本影响，且动态代理链路复杂) | 较高 (依赖的基础类稳定) | 最高 (HashMap 使用最广，触发稳定) | 较高 (Hashtable 较稳定) |
| **依赖库特殊性** | 无 | 无 | 无 | 无 |
| **学习价值** | 最高 (帮助理解动态代理和反序列化入口构造) | 较高 (理解 TiedMapEntry 的适配器模式) | 高 (理解 HashMap 作为通用入口的妙用) | 中 (作为 CC6 的备选和补充) |
| **实战价值** | 低 (JDK限制严重，仅在特定老环境有用) | 高 (无JDK限制，依赖CC库即可) | 最高 (通用性强，实战首选) | 高 (可作为 CC6 被WAF拦截时的备选) |
| **是否可绕过 Runtime 限制** | 否 | 否 | 否 | 否 |
| **通用性** | 低 | 高 | 最高 | 高 |

---

## CC2、3、4对比

| 维度 | CC2链 | CC3链 | CC4链 |
|------|-------|-------|-------|
| **入口点** |PriorityQueue |AnnotationInvocationHandler |PriorityQueue|
| **入口来源** |java.util (JDK集合类) |sun.reflect.annotation (JDK内部) |java.util (JDK集合类) |
| **JDK限制** |无限制 |<=jdk8u71 |无限制 |
| **CC版本** |4.0 |3.1-3.2.1 |4.0 |
| **关键跳板** |TransformingComparator.compare() |LazyMap.get() |TransformingComparator.compare() |
| **跳板所在包** |org.apache.commons.collections4.comparators |org.apache.commons.collections.map |org.apache.commons.collections4.comparators |
| **核心Transformer** |InvokerTransformer |InstantiateTransformer |InstantiateTransformer |
| **调用newTransformer方式** |反射方法调用 |TrAXFilter构造方法调用 |TrAXFilter构造方法调用 |
| **命令执行方式** |加载恶意字节码 |加载恶意字节码 |加载恶意字节码 |
| **调用链长度** |中等 |较长（涉及动态代理） |中等 |
| **利用思路核心** |用PriorityQueue反序列化触发compare，直接调用newTransformer |用AnnotationInvocationHandler动态代理触发LazyMap.get()，通过InstantiateTransformer实例化TrAXFilter间接调用newTransformer |用PriorityQueue反序列化触发compare，直接调用newTransformer |

---

## CC1~CC7调用链对比
### 核心对比

| 链 | 入口点 | 关键跳板 | 核心 Transformer | 命令执行方式 | CC版本 | JDK限制 |
|----|--------|----------|------------------|--------------|--------|---------|
| CC1-Lazy |AnnotationInvocationHandler.entryMapSet() |LazyMap.get() |InvokerTransformer |Runtime.exec() |CC3.1-3.2.1 |<=JDK8u71 |
| CC1-Trans |AnnotationInvocationHandler.checkSetValue() |TransformedMap.checkSetValue() |InvokerTransformer |Runtime.exec() |CC3.1-3.2.1 |<=JDK8u71 |
| CC2 |PriorityQueue.heapify() |TransformerComparator.compare() |InstantiateTransformer |加载恶意字节码 |CC4.0 |无 |
| CC3 |AnnotationInvocationHandler.entryMapSet() |LazyMap.get() |InvokerTransformer |加载恶意字节码 |CC3.1-3.2.1 |<=JDK8u71 |
| CC4 |PriorityQueue.heapify() |TransformerComparator.compare() |InstantiateTransformer |加载恶意字节码 |CC4.0 |无 |
| CC5 |BadAttributeValueExpException |TiedMapEntry.toString() |InvokerTransformer |Runtime.exec() |CC3.1-3.2.1 |无 |
| CC6 |HashMap.hash() |LazyMap.get() |InvokerTransformer |Runtime.exec() |CC3.1-3.2.1 |无 |
| CC7 |HashTable.reConstitutionPut() |AbstractMap.equals() |InvokerTransformer |Runtime.exec() |CC3.1-3.2.1 |无 |

---

### 按技术路线分类

| 路线 | 链 | 执行方式 | 特点 |
|------|----|----------|------|
| 命令执行型 |CC1,5,6,7 |Runtime.exec() |简单直接，通过反射执行系统命令 |
| 字节码加载型 |CC2,3,4 |加载恶意字节码 |更隐蔽，绕过命令黑名单，通过加载恶意类执行 |

---

### 核心差异总结

| 对比维度 | CC1 (两种) | CC2 | CC3 | CC4 | CC5 | CC6 | CC7 |
|----------|------------|-----|-----|-----|-----|-----|-----|
| **入口类** |AnnotationInvocationHandler |PriorityQueue |AnnotationInvocationHandler |PriorityQueue |BadAttributeValueExpException |HashMap |HashTable |
| **入口稳定性** |差(JDK限制) |好 |差(JDK限制) |好 |好 |最好 |好 |
| **跳板对象** |LazyMap / TransformedMap|TransformingComparator |LazyMap |TransformingComparator |TiedMapEntry |TiedMapEntry |AbstractMap |
| **触发方法** |get() / setValue() |compare() |hashCode() |compare() |toString() |get() |equals() |
| **Transformer类型** |InvokerTransformer |InstantiateTransformer |InvokerTransformer |InstantiateTransformer |InvokerTransformer |InvokerTransformer |InvokerTransformer |
| **是否需要 TrAXFilter** |否 |否 |是 |是 |否 |否 |否 |
| **命令执行方式** |Runtime.exec() |TemplatesImpl |TemplatesImpl |TemplatesImpl |Runtime.exec() |Runtime.exec() |Runtime.exec() |
| **CC版本** |3.x |4.0 |3.x |4.0 |3.x |3.x |3.x |
| **JDK限制** |≤8u71 |无 |≤8u71 |无 |无 |无 |无 |

---

### 关键知识点总结
#### 入口分类

| 类型 | 入口类 | 对应链 | JDK限制 |
|------|--------|--------|---------|
| JDK内部类入口 |AnnotationInvocationHandler |1,3 |<=jdk8u71 |
| 集合类入口 |HashMap、HashTable、PriorityQueue |2,4，6，7 |无 |
| 异常类入口 |BadAttributeValueExpException |5 |无 |

#### 跳板分类

| 类型 | 跳板类 触发方法 | 对应链 |
|------|----------|--------|
| Map触发 |LazyMap.get()、TransformedMap.setValue()、AbstractMap.equals() |1,7 |
| Comparator触发 |TransformingComparator.compare() |2,3,4 |
| 通用方法触发 |toString()、hashCode() |5,6 |

#### 两条技术路线

| 路线 | 核心机制 | 对应链 |
|------|----------|--------|
| 命令执行型 |InvokerTransformer → Runtime.exec() |1,5,6,7 |
| 字节码加载型 |TemplatesImpl + TrAXFilter |2,3,4 |

#### 版本限制

| CC版本 | 对应链 |
|--------|--------|
| commons-collections 3.x |1,3,5,6,7 | 
| commons-collections 4.0 |2,4 |

#### JDK限制

| 限制 | 入口类 | 对应链 |
|------|--------|--------|
| JDK ≤ 8u71 |AnnotationInvocationHandler |1,3 |
| 无限制 |其他 |2,4,5,6,7 |

---

## CC1~CC7调用链汇总图
```mermaid

```

---

