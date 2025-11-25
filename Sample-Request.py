import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ---- Static Variables ----
BASE = "https://0a9800c304a0809880d22b2f003b00f8.web-security-academy.net"
LOGIN_URL = BASE + "/login"
ACCOUNT_URL = BASE + "/my-account"
DATA = {"username": "wiener", "password": "peter"}

# ---- Session + Proxy ----
s = requests.Session()
s.verify = False
s.proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}

# ---- Login ----
print("Logging in...")
resp = s.post(LOGIN_URL, data=DATA)
print("[+] Login status:", resp.status_code)

print("[+] Cookies set:")
for c in s.cookies:
    print("   ", c.name, "=", c.value)

# ---- Authenticated Request ----
print("\n[*] Fetching account page using session cookies...")
r = s.get(ACCOUNT_URL)
print("[+] Account page status:", r.status_code)
print("[+] Response length:", len(r.text))
