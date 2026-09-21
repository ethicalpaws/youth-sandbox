from Crypto.Cipher import AES
ivstr="AmberGateIV!!v16"
keystr="AmberGateCBC!k16"

iv=ivstr.encode('utf-8')
key=keystr.encode('utf-8')  
newAES=AES.new(key,AES.MODE_CBC,iv)
chex="8390eb56579999d67b2534fb8939322f2356c235f1aefbcda10c21160d565862"
cstr=bytes.fromhex(chex)
padding_decrypted=newAES.decrypt(cstr)
padding_len=padding_decrypted[-1]
clean_decrypted=padding_decrypted[:-padding_len]
print(clean_decrypted.decode('utf-8'))