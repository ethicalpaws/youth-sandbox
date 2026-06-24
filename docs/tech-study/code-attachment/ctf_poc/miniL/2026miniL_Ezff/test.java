import org.apache.fury.Fury;
import org.apache.fury.config.Language;
import java.util.Base64;

public class test {
    public static void main(String[] args) {
        Fury fury = Fury.builder()
            .withLanguage(Language.JAVA)
            .requireClassRegistration(false)
            .withRefTracking(true)
            .build();

        String test = "hello";
        byte[] data = fury.serialize(test);
        String b64 = Base64.getEncoder().encodeToString(data);
        System.out.println("Test payload: " + b64);
        System.out.println("Length: " + b64.length());

        Object obj = fury.deserialize(data);
        System.out.println("Deserialized: " + obj);
    }
}