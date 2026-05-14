import java.io.FileInputStream;
import java.io.ObjectInputStream;

public class testysoserial {
    public static void main(String[] args) throws Exception {
        FileInputStream fis=new FileInputStream("payload.ser");
        ObjectInputStream ois=new ObjectInputStream(fis);
        ois.readObject();
        ois.close();
        fis.close();
    }

}
