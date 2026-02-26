import requests, socket, ssl, re, threading
import dns.resolver, whois
from colorama import Fore, init
from datetime import datetime

init(autoreset=True)

# 💀 NS INFO-X ORIGINAL BANNER 💀
print(Fore.RED + r"""
███╗   ██╗███████╗     ██╗███╗   ██╗███████╗ ██████╗       ██╗  ██╗
████╗  ██║██╔════╝     ██║████╗  ██║██╔════╝██╔═══██╗      ╚██╗██╔╝
██╔██╗ ██║███████╗     ██║██╔██╗ ██║█████╗  ██║   ██║█████╗ ╚███╔╝
██║╚██╗██║╚════██║     ██║██║╚██╗██║██╔══╝  ██║   ██║╚════╝ ██╔██╗
██║ ╚████║███████║     ██║██║ ╚████║██║     ╚██████╔╝      ██╔╝ ██╗
╚═╝  ╚═══╝╚══════╝     ╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝       ╚═╝  ╚═╝

💀 NS INFO-X — CYBER RECON FRAMEWORK 💀
👑 Founder: Naitik Soni
🔥 NS Indian Cyber Army’s
⚡ GOD ∞ Domain Intelligence Suite
""")

target = input("Target domain: ").strip()
base_url = "https://" + target

report = f"NS INFO X GOD REPORT\nTarget: {target}\nTime: {datetime.now()}\n\n"

# ---------- DOMAIN RESOLVE ----------
try:
    ip = socket.gethostbyname(target)
    print(Fore.CYAN + f"[IP] {ip}")
    report += f"[IP] {ip}\n"
except:
    print(Fore.RED + "❌ Domain not reachable")
    report += "[IP] Not resolved\n"
    ip = None

# ---------- GEO ----------
if ip:
    try:
        geo = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        g = f"{geo.get('country')} | {geo.get('org')}"
        print(Fore.CYAN + "[GEO]", g)
        report += f"[GEO] {g}\n"
    except:
        pass

# ---------- WHOIS ----------
print(Fore.CYAN + "\n[DOMAIN INFO]")
report += "\n[DOMAIN INFO]\n"

try:
    w = whois.whois(target)
    for line in [f"Registrar: {w.registrar}",
                 f"Created: {w.creation_date}",
                 f"Expires: {w.expiration_date}"]:
        print(line)
        report += line + "\n"
except:
    pass

# ---------- DNS ----------
print(Fore.CYAN + "\n[DNS RECORDS]")
report += "\n[DNS RECORDS]\n"

for t in ["A","MX","NS","TXT"]:
    try:
        for r in dns.resolver.resolve(target, t):
            line=f"{t}: {r}"
            print(line)
            report += line + "\n"
    except:
        pass

# ---------- HTTP ----------
html=""
try:
    r=requests.get(base_url,timeout=7)
    html=r.text

    print(Fore.CYAN + "\n[HEADERS]")
    report += "\n[HEADERS]\n"

    for k,v in r.headers.items():
        line=f"{k}: {v}"
        print(line)
        report += line + "\n"
except:
    pass

# ---------- JS LINKS ONLY ----------
print(Fore.CYAN + "\n[JS FILES]")
report += "\n[JS FILES]\n"

js=set()

for j in re.findall(r'src=["\'](.*?\.js)', html):
    if not j.startswith("http"):
        j = base_url + "/" + j.lstrip("/")
    js.add(j)

for j in re.findall(r'https?://[^\s"\']+\.js', html):
    js.add(j)

if js:
    for x in js:
        print(Fore.GREEN + x)
        report += x + "\n"
else:
    print("No external JS found")
    report += "No external JS found\n"

# ---------- FAST PORT SCAN ----------
print(Fore.CYAN + "\n[TOP PORTS]")
report += "\n[TOP PORTS]\n"

for p in [21,22,80,443,3306,8080,8443]:
    s=socket.socket()
    s.settimeout(0.5)
    if ip and s.connect_ex((target,p))==0:
        print(Fore.GREEN + f"OPEN {p}")
        report += f"OPEN {p}\n"
    s.close()

# ---------- SUBDOMAINS ----------
print(Fore.CYAN + "\n[COMMON SUBDOMAINS]")
report += "\n[COMMON SUBDOMAINS]\n"

subs=["www","mail","dev","api","admin","test","stage","beta","portal"]
for sub in subs:
    d=f"{sub}.{target}"
    try:
        socket.gethostbyname(d)
        print(Fore.GREEN + d)
        report += d + "\n"
    except:
        pass

# ---------- ROBOTS ----------
try:
    rob=requests.get(base_url+"/robots.txt",timeout=5)
    if rob.status_code==200:
        print(Fore.CYAN+"\n[robots.txt]")
        print(rob.text[:600])
        report += "\n[robots.txt]\n" + rob.text[:600] + "\n"
except:
    pass

# ---------- ADMIN PATH HUNTER ----------
print(Fore.CYAN + "\n[INTERESTING PATHS]")
report += "\n[INTERESTING PATHS]\n"

paths=["admin","login","dashboard",".git",".env","backup","cpanel","phpmyadmin"]

for p in paths:
    url=f"{base_url}/{p}"
    try:
        if requests.get(url,timeout=4).status_code in [200,403]:
            print(Fore.GREEN + url)
            report += url + "\n"
    except:
        pass

# ---------- PARAMETERS ----------
print(Fore.CYAN + "\n[PARAMETERS]")
report += "\n[PARAMETERS]\n"

for p in re.findall(r'\?[a-zA-Z0-9_]+=+', html):
    print(Fore.GREEN + p)
    report += p + "\n"

# ---------- WAYBACK ----------
print(Fore.CYAN + "\n[WAYBACK URLS]")
report += "\n[WAYBACK URLS]\n"

try:
    wb=requests.get(
        f"https://web.archive.org/cdx/search/cdx?url=*.{target}/*&output=text&fl=original&collapse=urlkey",
        timeout=10
    ).text.splitlines()[:60]

    for u in wb:
        print(Fore.GREEN + u)
        report += u + "\n"
except:
    pass

# ---------- SSL ----------
print(Fore.CYAN + "\n[SSL INFO]")
report += "\n[SSL INFO]\n"

try:
    ctx=ssl.create_default_context()
    with ctx.wrap_socket(socket.socket(),server_hostname=target) as s:
        s.connect((target,443))
        cert=s.getpeercert()
        info=str(cert.get("subject"))
        print(info)
        report += info + "\n"
except:
    pass

# ---------- SAVE REPORT ----------
name=f"NS_INFOX_GOD_{target}.txt"

with open(name,"w",encoding="utf-8") as f:
    f.write(report)

print(Fore.GREEN + f"\n✔ FULL REPORT SAVED: {name}")
print(Fore.RED + "\n💀 NS INFO-X GOD ∞ SCAN COMPLETE ⚡")
