

import java.io.*;

public class ByteArrayUnserialization {
    public static class Person implements Serializable {
        private String name;
        private int age;
        private static final long serialVersionUID=1L;
        public Person(String name,int age){
            this.name=name;
            this.age=age;
        }
        @Override
        public String toString(){
            return "Person{name="+name+",age="+age+"}";

        }
    }
    
    public static void main(String[] args) throws IOException,ClassNotFoundException {
        Person p1=new Person("tom", 18);
        ByteArrayOutputStream baos =new ByteArrayOutputStream();
        ObjectOutputStream oos=new ObjectOutputStream(baos);
        oos.writeObject(p1);
        oos.flush();
        oos.close();
        byte[] data=baos.toByteArray();
        ByteArrayInputStream bais=new ByteArrayInputStream(data);
        ObjectInputStream ois=new ObjectInputStream(bais);
        Object obj=ois.readObject();
        ois.close();
        bais.close();
        Person p2=(Person)obj;
        System.out.println("originalObject:"+p1);
        System.out.println("restoredObject:"+p2);
        System.out.println("original==restored: " + (p1 == p2)); 

        
    }
    
}
