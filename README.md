# BruteForce — HTTP Form Login Attacker

```
╔══════════════════════════════════════════════════════╗
║   ██████╗ ██████╗ ██╗   ██╗████████╗███████╗        ║
║   ██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝        ║
║   ██████╔╝██████╔╝██║   ██║   ██║   █████╗          ║
║   ██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝          ║
║   ██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗        ║
║   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝        ║
║         HTTP Form Login Brute Force Tool             ║
║              @#9002111185000# Edition                ║
╚══════════════════════════════════════════════════════╝
```

Interactive, menu-driven HTTP form brute force tool.
Multi-threaded. Proxy support. Two attack modes.

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

## Run

```bash
python brute.py
```

---

## Main Menu

```
  ┌─────────────────────────────────────┐
  │            MAIN MENU                │
  ├─────────────────────────────────────┤
  │  [1]  Password Brute Force          │
  │       (Known username, try passwords│
  │                                     │
  │  [2]  Username + Password Attack    │
  │       (Try both from files)         │
  │                                     │
  │  [0]  Exit                          │
  └─────────────────────────────────────┘
```

---

## Mode 1 — Password Brute Force

You know the username. Tool tries passwords from a wordlist.

**Prompts (in order):**

```
Target Login URL     →  http://target.com/login.php
Username / Email     →  admin@target.com
Password Wordlist    →  rockyou.txt
Username field name  →  email         (default)
Password field name  →  pass          (default)
Failure string       →  invalid password  (default)
Threads              →  10            (default)
Delay (seconds)      →  0             (default)
Proxy URL            →  (leave blank to skip)
```

---

## Mode 2 — Username + Password Attack

You have both a username list and a password list.
Tool tries every combination.

**Prompts (in order):**

```
Target Login URL     →  http://target.com/login.php
Username List File   →  usernames.txt
Password Wordlist    →  rockyou.txt
Username field name  →  email         (default)
Password field name  →  pass          (default)
Failure string       →  invalid password  (default)
Threads              →  10            (default)
Delay (seconds)      →  0             (default)
Proxy URL            →  (leave blank to skip)
```

---

## How to Find Form Field Names

Open browser DevTools → Network tab → submit a wrong login → inspect the POST request body.

Example POST body:
```
email=test%40mail.com&pass=wrongpass&remember=1
```

So: `-uf email` and `-pf pass`

---

## How to Find the Failure String

Submit a wrong password. Look at the page response for a unique string:

| Site | Failure String |
|------|---------------|
| Custom panel | `Invalid credentials` |
| WordPress | `incorrect password` |
| cPanel | `Login Attempt Failed` |
| phpMyAdmin | `Access denied` |

---

## Output

```
[---] #1      admin@target.com:123456               [HTTP 200]
[---] #2      admin@target.com:password             [HTTP 200]
[---] #3      admin@target.com:admin123             [HTTP 200]
[HIT] #4      admin@target.com:letmein2024          [HTTP 302]

══════════════════════════════════════════════════════
  [+] CRACKED!
  URL      : http://target.com/login.php
  Username : admin@target.com
  Password : letmein2024
══════════════════════════════════════════════════════
```

Hit saved to `cracked.txt`:
```
http://target.com/login.php | admin@target.com | letmein2024
```

---

## Recommended Wordlists

| Wordlist | Size | Use Case |
|----------|------|----------|
| `rockyou.txt` | 14M | General accounts |
| `darkweb2017.txt` | 1.4M | Leaked passwords |
| `common-passwords.txt` | 100K | Fast scan |
| Custom list | Any | Targeted attack |

Get SecLists:
```bash
git clone https://github.com/danielmiessler/SecLists
```

---

## Tips

- Use Burp Suite to inspect POST requests before attacking
- Set `-d 1` or `-d 2` delay if target has rate limiting
- Reduce threads to `1` or `2` for slow/protected targets
- Use proxy (`http://127.0.0.1:8080`) with Burp for traffic inspection
- `rockyou.txt` covers most common passwords

---

## File Structure

```
bruteforce/
├── brute.py          # Main tool (interactive)
├── README.md         # This file
├── requirements.txt  # Dependencies
├── .gitignore        # Ignores cracked.txt and wordlists
└── cracked.txt       # Auto-generated when a hit is found
```

---

*Built by Ochena Gamer 👿 — @#9002111185000#*
