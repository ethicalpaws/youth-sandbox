import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import java.util.Scanner;

public class Log4j2ServerDemo {
    private static final Logger logger = LogManager.getLogger(Log4j2ServerDemo.class);
    
    public static void main(String[] args) {
        // 开启远程加载（用于低版本JDK测试，高版本JDK需要配合反序列化利用）
        System.setProperty("com.sun.jndi.ldap.object.trustURLCodebase", "true");
        //System.setProperty("com.sun.jndi.rmi.object.trustURLCodebase", "true");
        
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== Log4j2 JNDI 注入测试环境 ===");
        System.out.println("当前JDK版本: " + System.getProperty("java.version"));
        System.out.println("输入 payload 进行测试（输入 'exit' 退出）\n");
        
        while (true) {
            System.out.print("Payload > ");
            String payload = scanner.nextLine();
            
            if ("exit".equalsIgnoreCase(payload)) {
                System.out.println("退出测试");
                break;
            }
            
            if (payload.isEmpty()) {
                continue;
            }
            
            System.out.println("📝 即将记录日志: " + payload);
            System.out.println("🚀 触发漏洞...");
            
            try {
                // 触发漏洞
                logger.error("用户输入: {}", payload);
                System.out.println("✅ 日志已记录，请观察恶意服务器是否有响应\n");
            } catch (Exception e) {
                System.out.println("❌ 发生异常: " + e.getMessage());
                e.printStackTrace();
            }
        }
        
        scanner.close();
    }
}