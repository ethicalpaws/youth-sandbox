from Crypto.Cipher import AES
import base64
keystr="TeaLeafKey!AES16"

miwenb64="IuTvzRnjs/vGtpd8h1bzFgwvimiQGFIUfTPI85QbLf4="
miwen=base64.b64decode(miwenb64)
key=keystr.encode('utf-8')
newAES=AES.new(key,AES.MODE_ECB)
padding_mingwen=newAES.decrypt(miwen)
pad_len=padding_mingwen[-1]
mingwen=padding_mingwen[:-pad_len]
mingwenstr=mingwen.decode('utf-8')
print(mingwenstr)