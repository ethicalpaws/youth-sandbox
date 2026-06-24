package com.example;

import java.io.FileInputStream;
import java.io.ObjectInputStream;

public class TestDeserialize {
    public static void main(String[] args) throws Exception {
        // ✅ 正确：读取 .ser 文件
        ObjectInputStream ois = new ObjectInputStream(
            new FileInputStream("E:/youth-sandbox/docs/tech/code/java_deserialization_code/ysoserial/payload.ser")
        );
        ois.readObject();  // 触发 CC2 链
        ois.close();
        System.out.println("反序列化完成，无异常");
    }
}