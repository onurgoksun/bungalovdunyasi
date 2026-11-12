"""Değişen sayfaları IndexNow ile Bing, Yandex ve diğer arama motorlarına bildirir.
Kullanım: python3 tools/indexnow.py <eski_commit> <yeni_commit>
(Google IndexNow kullanmıyor; Google site haritasından okur.)"""
import json, re, subprocess, sys, urllib.request

src = open("build.py", encoding="utf-8").read()
KEY = re.search(r'INDEXNOW_KEY = "([0-9a-f]+)"', src).group(1)
SITE = "https://bungalovdunyasi.com"
old, new = sys.argv[1], sys.argv[2]
if not old or set(old) == {"0"}:
    old = new + "~1"
files = subprocess.run(["git", "diff", "--name-only", old, new, "--", "docs"], capture_output=True, text=True).stdout.split()
urls = []
for f in files:
    if not f.endswith("index.html"):
        continue
    page = open(f, encoding="utf-8").read() if __import__("os").path.exists(f) else ""
    if 'name="robots" content="noindex"' in page:
        continue
    urls.append(SITE + "/" + f[len("docs/"):-len("index.html")])
urls = sorted(set(urls))[:1000]
if not urls:
    print("Bildirilecek sayfa yok")
    sys.exit(0)
body = json.dumps({"host": "bungalovdunyasi.com", "key": KEY, "keyLocation": f"{SITE}/{KEY}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow:", r.status, len(urls), "sayfa")
except urllib.error.HTTPError as e:
    print("IndexNow hata:", e.code, e.read()[:300])
for u in urls:
    print(" ", u)
