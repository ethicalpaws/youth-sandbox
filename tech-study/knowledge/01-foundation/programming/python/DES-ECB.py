from Crypto.Cipher import DES
import binascii

def main():
    # 1. 获取密钥
    key_hex = input("请输入16位十六进制密钥（例如：5020546A34BA3CA4）：").strip()
    if len(key_hex) != 16:
        print("错误：密钥必须是16位十六进制字符串（8字节）")
        return
    
    try:
        key = binascii.unhexlify(key_hex) # 把密钥的十六进制字符串转为真正的8字节数据
    except:
        print("错误：密钥必须是有效的十六进制字符")
        return

    # 2. 获取明文
    plaintext_hex = "4B47532140232425"  # 你的16位十六进制明文
    print(f"明文 (Hex String): {plaintext_hex}")
    
    # ================= 核心修正区域 =================
    # 将十六进制字符串转换为真正的 8 字节二进制数据
    # 而不是直接用 .encode('utf-8') 转换文本
    try:
        data = binascii.unhexlify(plaintext_hex) 
    except:
        print("错误：明文必须是有效的十六进制字符串")
        return
        
    if len(data) != 8:
        print(f"错误：明文转换后长度为 {len(data)} 字节，必须刚好是 8 字节。")
        return
    # ===============================================

    # 3. 使用 ECB 模式加密，不进行填充
    cipher = DES.new(key, DES.MODE_ECB)
    ciphertext = cipher.encrypt(data)

    # 输出结果（转回十六进制字符串）
    encrypted_hex = binascii.hexlify(ciphertext).decode()
    print(f"加密结果 (Hex): {encrypted_hex}")
    print(f"密文长度: {len(ciphertext)} 字节 ({len(encrypted_hex)} 位十六进制)")

    # 4. 验证解密
    decipher = DES.new(key, DES.MODE_ECB)
    decrypted_bytes = decipher.decrypt(ciphertext)
    # 解密后，把字节转回十六进制字符串显示
    decrypted_hex = binascii.hexlify(decrypted_bytes).decode()
    print(f"解密验证 (Hex): {decrypted_hex}")

if __name__ == "__main__":
    main()