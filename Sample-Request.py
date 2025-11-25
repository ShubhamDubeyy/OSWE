import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

proxy = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

print(requests.get("https://example.com", proxies=proxy, verify=False).text)
print(requests.post("https://example.com/login", data={"a":1}, proxies=proxy, verify=False).text)
