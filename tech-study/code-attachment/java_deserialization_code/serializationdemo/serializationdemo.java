import java.io.*;
public class serializationdemo {
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
            return "Person{name="+name+",age="+age+"}";
        }
    }


        public static void main(String[] args) throws IOException {
        
            Person p=new Person("张三", 18);    
            ByteArrayOutputStream baos=new ByteArrayOutputStream();
            System.out.println("original size:"+baos.size());
            ObjectOutputStream oos=new ObjectOutputStream(baos);
            oos.writeObject(p);
            oos.flush();
            oos.close();
            byte[] data=baos.toByteArray();
            System.out.println("bytesize="+data.length);
            for (int i=0;i<Math.min(10,data.length);i++){
                System.out.printf("%02X", data[i]);
            }
        }

}