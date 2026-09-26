import hashlib
import binascii

# 你提供的 UTF-16 LE 十六进制字符串（补全末尾的 00）
hex_str = input("请输入 UTF-16 LE 十六进制字符串：")
# 1. 将十六进制转为字节
utf16_bytes = binascii.unhexlify(hex_str)

# 2. 解码回明文看看是不是 Admin@123（用于验证）
try:
    plaintext = utf16_bytes.decode('utf-16-le')
    print(f"解码后的明文: {plaintext}")
except Exception as e:
    print(f"解码错误: {e}")

# 3. 计算 NTLM Hash (MD4)
ntlm_hash = hashlib.new('md4', utf16_bytes).hexdigest()
print(f"NTLM Hash: {ntlm_hash}")