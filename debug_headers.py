import requests

TARGET = "https://web.kelasdata.co.id/instructor-finder"

# Common browser headers to bypass simple WAF/Bot detection
HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1"
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safe/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    },
    { # Minimal curl-like but with browser UA
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0",
    }
]

def check_access():
    print(f"[*] Testing access to: {TARGET}")
    
    for i, headers in enumerate(HEADERS_LIST):
        print(f"\n[Test {i+1}] Headers: {headers.keys()}")
        try:
            r = requests.get(TARGET, headers=headers, timeout=15)
            print(f"    Status Code: {r.status_code}")
            print(f"    Length     : {len(r.text)}")
            if r.status_code == 200:
                print("    [+] SUCCESS! 200 OK received.")
                return headers
            elif r.status_code == 415:
                print("    [-] 415 Unsupported Media Type")
            else:
                print(f"    [-] Failed with status {r.status_code}")
        except Exception as e:
            print(f"    [!] Error: {e}")
            
    return None

if __name__ == "__main__":
    valid_headers = check_access()
    if valid_headers:
        print("\n[+] Found valid headers. Use these for dumping.")
        print(valid_headers)
    else:
        print("\n[-] All header combinations failed. Site might be blocking IP or requires specific cookie.")
