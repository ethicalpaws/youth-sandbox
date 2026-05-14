import java.io.*;
public class FileUnserialization {


    public static class Person implements Serializable{
        private String name;
        private int age;
        private static final long serialVersionUID=1L;
        public Person(String name,int age){
            this.name=name;
            this.age=age;
        }
        @Override
        public String toString(){
            return "Person{name:"+name+",age:"+age+"}";
        }
    }
    public static void main(String[] args) throws IOException,ClassNotFoundException{
        Person p1=new Person("tom", 18);
        FileOutputStream fos=new FileOutputStream("1.bin");
        ObjectOutputStream oos=new ObjectOutputStream(fos);
        oos.writeObject(p1);
        oos.flush();
        oos.close();
        System.out.println("save:ok");
        FileInputStream fis=new FileInputStream("1.bin");
        ObjectInputStream ois=new ObjectInputStream(fis);
        Object obj=ois.readObject();
        Person p2=(Person)obj;
        ois.close();
        System.out.println("restore:ok");
        System.out.println("originalObject:"+p1);
        System.out.println("restoredObject:"+p2);
        System.out.println("original==restored: " + (p1 == p2));   
    }
}
