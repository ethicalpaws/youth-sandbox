import hmac
import hashlib
import binascii

def main():
    # 1. 获取密钥
    key_hex = input("请输入16字节的十六进制密钥: ").strip()
    if len(key_hex) != 32:
        print("错误：密钥必须是32位十六进制字符串（16字节）")
        return
    key = binascii.unhexlify(key_hex)

    # 2. 获取待加密数据
    data_hex = input("请输入待加密的十六进制数据: ").strip()
    if len(data_hex) % 2 != 0:
        print("错误：十六进制数据长度必须是偶数")
        return
    data_bytes = binascii.unhexlify(data_hex)

    # 3. 直接对二进制数据进行 HMAC-MD5 计算
    hmac_md5 = hmac.new(key, data_bytes, hashlib.md5)
    result_hex = hmac_md5.hexdigest()

    print(f"\n[+] HMAC-MD5 结果 (Hex): {result_hex}")

    # 4. 尝试提取并解码可读部分（仅用于分析，不影响计算结果）
    print("\n[*] 尝试提取可读信息（跳过前28字节头部）...")
    try:
        # NTLM TargetInfo 的头部通常是 28 字节，后面是 AV_Pairs
        # 我们尝试从第 28 字节开始解码
        payload = data_bytes[28:] 
        # 使用 errors='ignore' 忽略无法解码的二进制部分
        plaintext = payload.decode('utf-16-le', errors='ignore')
        # 过滤掉不可打印字符
        readable = ''.join(c for c in plaintext if c.isprintable())
        print(f"    可读字符串: {readable}")
    except Exception as e:
        print(f"    提取失败: {e}")

if __name__ == "__main__":
    main()