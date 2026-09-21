# claude配置burp mcp
  
  1. 确认环境

  - BurpSuite 已启动，且 MCP 扩展已启用（Extender → MCP → 勾选 Running）
  - 确认 BurpSuite 监听 port 9876

  2. 删除旧的错误配置

  claude mcp remove burp

  3. 添加正确的配置

  关键：不用 cmd /c，直接用 java 命令：

  claude mcp add -t stdio burp --scope user -- "java路径" "-jar" "mcp-proxy.jar路径" "--sse-url" "http://127.0.0.1:9876"

  实际命令：
  claude mcp add -t stdio burp --scope user -- "C:\Program Files\Eclipse Adoptium\jdk-21.0.10.7-hotspot\bin\java.exe" "-jar" "E:\tools\burp-mcp\mcp-proxy.jar" "--sse-url" "http://127.0.0.1:9876"

  4. 验证

  claude mcp list

  看到 ✔ Connected 即成功。

**需要在** mcp-proxy.jar 同目录下创建 .mcp.json：
.mcp.json
       1 {
       2   "mcpServers": {
       3     "burp": {
       4       "command": "java",
       5       "args": [
       6         "-jar",
       7         "mcp-proxy.jar",
       8         "--sse-url",
       9         "http://127.0.0.1:9876"
      10       ]
      }

