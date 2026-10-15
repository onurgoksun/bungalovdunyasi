#!/usr/bin/env python3
"""Bungalov Dünyası statik site üreticisi. Çalıştır: python3 build.py  → ./docs/"""
import html, json, os, re, shutil, datetime, urllib.request
from urllib.parse import quote

SITE = "https://bungalovdunyasi.com"
NAME = "Bungalov Dünyası"
WA = "905327222545"
TODAY = datetime.date.today().isoformat()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
UP = "https://labellabungalov.com/wp-content/uploads/2026/09/"
UTM = "utm_source=bungalovdunyasi&utm_medium=referral"


def wa(text):
    return f"https://wa.me/{WA}?text={quote(text)}"


def esc(s):
    return html.escape(s, quote=True)


LOGO_SVG = ('<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M3 28 16 4l13 24" fill="none" stroke="currentColor" '
            'stroke-width="2.6" stroke-linejoin="round"/><path d="M9.5 28 16 16l6.5 12" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linejoin="round"/><rect x="14" y="21" width="4" height="4.5" rx=".6" fill="#e39a3b"/></svg>')

# Temsili görseller — Unsplash Lisansı (ticari kullanım serbest, izin gerekmez)
PHOTOS = {
    "hero": ("https://images.unsplash.com/photo-1576874748772-584aa2bee2d4", "Akşam ışıkları yanan A-frame bungalov, orman içinde", "Cameron Stewart", "BU-tn41KnR8"),
    "pool": ("https://images.unsplash.com/photo-1768178540284-ab256d312e61", "Orman içinde küçük havuzlu A-frame bungalov", "Osman Espinoza Franco", "TJY-rtSJunI"),
    "snow": ("https://images.unsplash.com/photo-1638985787285-46f05ff063f2", "Karlı ormanda A-frame bungalov", "Michal Janek", "e9DkjLz5FuU"),
    "dog": ("https://images.unsplash.com/photo-1642387922923-cf4cacf42ae9", "Şöminenin önünde uzanan köpek", "Djordje Vukojicic", "51Fin-fJTNk"),
    "lake": ("https://images.unsplash.com/photo-1496060169243-453fde45943b", "Göl kıyısında sisli orman", "Sam Ferrara", "iecJiKe_RNg"),
    "inside": ("https://images.unsplash.com/photo-1631941392209-70cad44ecfb7", "Şömineli ahşap bungalov iç mekânı", "Hans", "_k0Pyd1uMEc"),
    "forestlake": ("https://images.unsplash.com/photo-1623681193221-261b6578180e", "Ağaçların arasından görünen göl", "Ruben Hanssen", "ODAKeAbL2tc"),
    "firepit": ("https://images.unsplash.com/photo-1782226796423-8d72656a332c", "Akşam ışıklı ahşap bungalov ve ateş çukuru", "Jonathan Adams", "wcpofj_J3mc"),
    "stars": ("https://images.unsplash.com/photo-1761674255792-1e75af5ccf33", "Yıldızlı gecede ışıkları yanan A-frame bungalov", "Jimy Antoun", "KP2j49M3rZU"),
    "fireplace": ("https://images.unsplash.com/photo-1696860740767-f4211c9209f4", "Taş şömineli geniş oturma odası", "Clay Banks", "Qry84CsaA9o"),
}


def ux(key, w, h):
    return f"{PHOTOS[key][0]}?auto=format&fit=crop&w={w}&h={h}&q=72"


def credit(key):
    _, _, who, pid = PHOTOS[key]
    return f'Temsili görsel. Fotoğraf: <a href="https://unsplash.com/photos/{pid}" rel="noopener">{esc(who)}</a>, Unsplash'


def cover(key):
    return (f'<figure class="cover"><img src="{ux(key, 1600, 800)}" srcset="{ux(key, 800, 400)} 800w, {ux(key, 1600, 800)} 1600w" '
            f'sizes="(max-width: 1120px) 100vw, 1080px" alt="{esc(PHOTOS[key][1])}" width="1600" height="800">'
            f'<figcaption>{credit(key)}</figcaption></figure>')

NAV = [("/tesisler/", "Tesisler"), ("/rehber/", "Rehber"), ("/uygulama/", "İşletmeciler için"), ("/hakkimizda/", "Hakkımızda")]


def _hash(*paths):
    import hashlib
    h = hashlib.sha1()
    for base in paths:
        full = os.path.join(os.path.dirname(os.path.abspath(__file__)), base)
        files = [full] if os.path.isfile(full) else sorted(os.path.join(d, f) for d, _, fs in os.walk(full) for f in fs)
        for fp in files:
            with open(fp, "rb") as f:
                h.update(f.read())
    return h.hexdigest()[:8]


JSV = _hash("src/js", "src/iller.json")      # dosya değişince tarayıcı önbelleği yenilenir
CSSV = _hash("src/style.css")
SB_JS = "/js/vendor/supabase-2.117.0.js"


def fit_title(title, limit=60):
    # Google ~60 karakterden uzun başlıkları keser; sığmıyorsa site adı ekini at.
    for suf in (" | " + NAME, " – " + NAME):
        if len(title) > limit and title.endswith(suf):
            return title[: -len(suf)]
    return title


def page(path, title, desc, body, schema=None, active=None, og_image=None, scripts=None, noindex=False, og_type="website"):
    title = fit_title(title)
    canonical = SITE + path
    js = ""
    if scripts:
        geo = f'<script src="/js/iller.js?v={JSV}"></script>\n' if "tesis-form" in scripts else ""
        js = geo + f'<script src="{SB_JS}"></script>\n<script src="/js/core.js?v={JSV}"></script>\n' + \
            "".join(f'<script src="/js/{n}.js?v={JSV}"></script>\n' for n in scripts)
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    nav = "".join(
        f'<a href="{h}"{" aria-current=\"page\"" if active == h else ""}>{t}</a>' for h, t in NAV)
    ld = ""
    for s in (schema or []):
        ld += f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>\n'
    og = og_image or ux("hero", 1200, 630)
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:locale" content="tr_TR">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og}">
<meta name="theme-color" content="#15302b">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700&family=Literata:opsz,wght@7..72,400;7..72,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css?v={CSSV}">
<link rel="preconnect" href="https://images.unsplash.com">
{ld}</head>
<body>
<a class="skip" href="#icerik">İçeriğe geç</a>
<header class="top"><div class="wrap">
  <a class="logo" href="/">{LOGO_SVG}{NAME}</a>
  <nav class="nav" aria-label="Ana menü">{nav}<a id="acct-link" class="acct" href="/uye/">Giriş yap</a><a class="owner" href="/tesis-ekle/">Tesisinizi ekleyin</a></nav>
</div></header>
<main id="icerik">
{body}
</main>
<footer class="foot"><div class="wrap">
  <div>
    <a class="logo" href="/">{LOGO_SVG}{NAME}</a>
    <p>Türkiye'de bungalov arayanlar için sade bir rehber. Rezervasyonu doğrudan tesisle yaparsınız; araya komisyon girmez.</p>
  </div>
  <div>
    <h4>Sayfalar</h4>
    <ul><li><a href="/tesisler/">Tesisler</a></li><li><a href="/rehber/">Rehber</a></li><li><a href="/hakkimizda/">Hakkımızda</a></li><li><a href="/tesis-ekle/">Tesisinizi ekleyin</a></li><li><a href="/uye/">Üye girişi</a></li></ul>
  </div>
  <div>
    <h4>İletişim</h4>
    <ul><li><a href="{wa('Merhaba, Bungalov Dünyası hakkında yazıyorum.')}" rel="noopener">WhatsApp ile yazın</a></li><li><a href="tel:+{WA}">0532 722 25 45</a></li><li><a href="/kvkk/">Kişisel veriler (KVKK)</a></li><li><a href="/uyelik-kosullari/">Üyelik koşulları</a></li></ul>
  </div>
  <p class="small">© {datetime.date.today().year} {NAME}. Tesis bilgileri tesislerin kendi beyanına dayanır; fiyat ve müsaitlik için tesisle görüşün.</p>
</div></footer>
<script>try{{if(localStorage.getItem("sb-sbqjblbiwivytybtlxdi-auth-token")){{var a=document.getElementById("acct-link");a.textContent="Hesabım";a.href="/hesabim/"}}}}catch(e){{}}</script>
{js}<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "e4d1630b9947485b835f8b18c6dd0d75"}}'></script>
</body>
</html>
"""


def write(path, content):
    fp = os.path.join(OUT, path.strip("/"), "index.html") if path.endswith("/") else os.path.join(OUT, path.lstrip("/"))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)


def crumbs(items):
    parts = ['<a href="/">Ana sayfa</a>'] + [f'<a href="{h}">{t}</a>' if h else esc(t) for h, t in items]
    return '<nav class="crumbs" aria-label="Konum">' + " / ".join(parts) + "</nav>"


def crumbs_ld(items):
    els = [{"@type": "ListItem", "position": 1, "name": "Ana sayfa", "item": SITE + "/"}]
    for i, (h, t) in enumerate(items, start=2):
        el = {"@type": "ListItem", "position": i, "name": t}
        if h:
            el["item"] = SITE + h
        els.append(el)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": els}


# ---------------------------------------------------------------- Tesisler
LABELLA = {
    "slug": "labella-bungalov",
    "name": "Labella Bungalov",
    "area": "Memnuniye Mahallesi, Sapanca, Sakarya",
    "province": "Sakarya", "district": "Sapanca",
    "summary": "Orman içinde beş bağımsız A-frame bungalov. Her birinin kendine ait ısıtmalı açık havuzu, sıcak jakuzisi, şöminesi ve terası var.",
    "tags": [("Özel havuz", ""), ("Isıtmalı havuz", "warm"), ("Sıcak jakuzi", "warm"), ("Şömine", "warm"),
             ("4+1 kişilik", ""), ("Evcil hayvan: önceden sorun", "")],
    "shots": [("labella-bungalov-sapanca-6-819x1024.webp", "A-frame bungalov ve özel havuz, havadan"),
              ("labella-bungalov-sapanca-38-733x1024.webp", "Gece aydınlatmalı A-frame bungalov ve havuz"),
              ("labella-bungalov-sapanca-27-733x1024.webp", "Bungalov iç mekânı, oturma alanı")],
    "gallery": [("labella-bungalov-sapanca-14-819x1024.webp", "Havadan bungalovlar ve özel havuzlar"),
                ("labella-bungalov-sapanca-39-733x1024.webp", "A-frame bungalov ve özel yüzme havuzu"),
                ("labella-bungalov-sapanca-32-733x1024.webp", "Salon oturma grubu"),
                ("labella-bungalov-sapanca-28-733x1024.webp", "Çift kişilik yatak odası"),
                ("labella-bungalov-sapanca-36-819x1024.webp", "Ateş çukuru ve havuz, gece havadan"),
                ("labella-bungalov-sapanca-33-819x1024.webp", "Teras oturma alanında akşam"),
                ("labella-bungalov-sapanca-10-819x1024.webp", "Çim bahçe, salıncak ve mangal"),
                ("labella-bungalov-sapanca-40-733x1024.webp", "Havuz şelalesi, gece")],
    "site": "https://labellabungalov.com/",
    "booking": "https://labellabungalov.com/rezervasyon/",
    "phone": "+905327222545", "phone_txt": "0532 722 25 45",
    "phone2": "+905465408966", "phone2_txt": "0546 540 89 66",
    "address": {"street": "Memnuniye Mahallesi, Memnuniye Sokak No 132", "locality": "Sapanca", "region": "Sakarya"},
}


def fac_row(f):
    shots = "".join(f'<img src="{UP}{s}" alt="{esc(a)} — {esc(f["name"])}" loading="lazy" width="733" height="1024">'
                    for s, a in f["shots"])
    tags = "".join(f'<li class="{c}">{esc(t)}</li>' for t, c in f["tags"])
    url = f'/tesisler/{f["slug"]}/'
    return f"""<article class="fac" data-slug="{f['slug']}">
  <a class="shots" href="{url}" tabindex="-1" aria-hidden="true">{shots}</a>
  <div>
    <h3><a href="{url}">{esc(f["name"])}</a></h3>
    <p class="place">{esc(f["area"])}</p>
    <p>{esc(f["summary"])}</p>
    <ul class="tags" aria-label="Öne çıkan olanaklar">{tags}</ul>
    <div class="actions"><a class="btn solid" href="{url}">Bungalovu incele</a><a class="btn line" href="{f['booking']}?{UTM}" rel="noopener">Müsaitlik ve fiyat</a></div>
  </div>
</article>"""


SLOT = f"""<div class="slot">
  <p><strong>Bungalov tesisi mi işletiyorsunuz?</strong>Hangi ilde olursa olsun tesisinizi ücretsiz ekleyin. Misafirler size doğrudan ulaşır, komisyon ödemezsiniz.</p>
  <a class="btn solid" href="/tesis-ekle/">Tesisinizi ekleyin</a>
</div>"""

# ---------------------------------------------------------------- Rehber yazıları
GUIDES = []
CONTENT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content", "rehber")
# Rehber yazıları content/rehber/*.json dosyalarından okunur (en yeni en üstte).
for _fn in sorted(os.listdir(CONTENT)):
    if not _fn.endswith(".json"):
        continue
    with open(os.path.join(CONTENT, _fn), encoding="utf-8") as _f:
        _d = json.load(_f)
    if _d.get("draft"):
        continue
    if _d["image"] not in PHOTOS:
        raise SystemExit(f"{_fn}: bilinmeyen görsel anahtarı {_d['image']!r} (PHOTOS içinden seçin)")
    GUIDES.append(dict(slug=_d["slug"], title=_d["title"], seo_title=_d["seo_title"], desc=_d["description"],
                       minutes=_d["minutes"], body=_d["body"], img=_d["image"], date=_d["date"],
                       faq=[(x["q"], x["a"]) for x in _d.get("faq", [])],
                       bolge=_d.get("bolge", "sakarya/sapanca")))
GUIDES.sort(key=lambda g: (g["date"], g["slug"]), reverse=True)

# ---------------------------------------------------------------- Üyelerin eklediği tesisler
# Yayındaki ilanlar Supabase'den okunur ve content/ilanlar.json'a yazılır. Okunamazsa (ağ yoksa)
# son kaydedilen liste kullanılır. GitHub Actions düzenli aralıklarla yeniden üretir.
SB_URL = "https://sbqjblbiwivytybtlxdi.supabase.co"
SB_KEY = "sb_publishable_YeZQ1VWS7RrQMxW5Ubrykg_7q_k0N9A"
LISTINGS_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content", "ilanlar.json")
RESERVED = {"labella-bungalov"}


def load_listings():
    cols = ("slug,name,summary,description,province,district,neighborhood,address,units,capacity,beds,amenities,pets,checkin,checkout,"
            "rules,phone,whatsapp,website,booking_url,instagram,photos,created_at,updated_at")
    url = f"{SB_URL}/rest/v1/listings?status=eq.yayinda&select={cols}&order=created_at.desc&limit=1000"
    try:
        req = urllib.request.Request(url, headers={"apikey": SB_KEY, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r)
        if not isinstance(data, list):
            raise ValueError("beklenmeyen yanıt")
        with open(LISTINGS_CACHE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
        print(f"ilanlar: {len(data)} (Supabase)")
    except Exception as e:  # ağ yoksa son kayıt
        data = []
        if os.path.exists(LISTINGS_CACHE):
            with open(LISTINGS_CACHE, encoding="utf-8") as f:
                data = json.load(f)
        print(f"ilanlar: {len(data)} (önbellek; Supabase okunamadı: {type(e).__name__})")
    out = []
    for l in data:
        slug = str(l.get("slug") or "")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug) or slug in RESERVED:
            continue
        l["photos"] = [p for p in (l.get("photos") or []) if isinstance(p, dict) and isinstance(p.get("path"), str)]
        out.append(l)
    return out


LISTINGS = load_listings()

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "iller.json"), encoding="utf-8") as _f:
    GEO = json.load(_f)
_TR = str.maketrans({"ç": "c", "ğ": "g", "ı": "i", "İ": "i", "ö": "o", "ş": "s", "ü": "u", "â": "a", "î": "i", "û": "u",
                     "Ç": "c", "Ğ": "g", "Ö": "o", "Ş": "s", "Ü": "u", "I": "i"})


def tr_slug(x):
    return re.sub(r"[^a-z0-9]+", "-", str(x or "").translate(_TR).lower()).strip("-")


def norm_place(x):
    """İl / ilçe adını derli toplu yazar (ör. 'sapanca ' → 'Sapanca')."""
    x = re.sub(r"\s+", " ", str(x or "")).strip()
    if not x:
        return ""
    for il in GEO["iller"]:
        if tr_slug(il) == tr_slug(x):
            return il
    first = {"i": "İ", "ı": "I"}.get(x[0], x[0].upper())
    return first + x[1:]


for _l in LISTINGS:
    _l["province"] = norm_place(_l.get("province"))
    _l["district"] = norm_place(_l.get("district"))

# Bölge sayfaları: tesisi olan her il ve ilçe için otomatik üretilir.
REGION_INTRO = {
    ("Sakarya", "Sapanca"): ("Sapanca bungalovları",
                             "Sapanca Gölü çevresi, İstanbul'a yakınlığı ve ormanlık yamaçlarıyla Türkiye'de bungalov tatilinin en yaygın olduğu yerlerden biri. "
                             "Özel havuzlu, jakuzili ve şömineli bungalovların çoğu gölü çevreleyen mahallelerde. Aşağıdaki tesislerle rezervasyonu doğrudan, komisyonsuz yaparsınız."),
}


def region_path(il, ilce=None):
    return f"/bolge/{tr_slug(il)}/" + (f"{tr_slug(ilce)}/" if ilce else "")


REGIONS = {}   # (il, ilçe) -> {"listings": [...], "labella": bool}
for _l in LISTINGS:
    if _l["province"] and _l["district"] and tr_slug(_l["province"]) and tr_slug(_l["district"]):
        REGIONS.setdefault((_l["province"], _l["district"]), {"listings": [], "labella": False})["listings"].append(_l)
REGIONS.setdefault(("Sakarya", "Sapanca"), {"listings": [], "labella": False})["labella"] = True
PROVINCES = {}
for (_il, _ilce), _r in REGIONS.items():
    PROVINCES.setdefault(_il, []).append(_ilce)


def region_count(key):
    r = REGIONS[key]
    return len(r["listings"]) + (1 if r["labella"] else 0)


def region_chips(current=None):
    keys = sorted(REGIONS, key=lambda k: (-region_count(k), k[1]))
    return "".join(f'<a href="{region_path(*k)}"{" aria-current=\"page\"" if k == current else ""}>{esc(k[1])}<small>{esc(k[0])} · {region_count(k)}</small></a>'
                   for k in keys)
PETS = {"evet": "Evcil hayvan kabul edilir", "hayir": "Evcil hayvan kabul edilmez", "sor": "Evcil hayvan için önceden sorun"}


def photo_url(path):
    return f"{SB_URL}/storage/v1/object/public/tesis-foto/" + "/".join(quote(x) for x in path.split("/"))


def safe_url(u):
    u = str(u or "").strip()
    if not u:
        return ""
    if not re.match(r"https?://", u, re.I):
        u = "https://" + u
    return u if re.match(r"https?://[^\s\"'<>]+$", u, re.I) else ""


def with_utm(u):
    u = safe_url(u)
    return (u + ("&" if "?" in u else "?") + UTM) if u else ""


def digits(p):
    d = re.sub(r"\D", "", str(p or ""))
    if len(d) == 11 and d[0] == "0":
        d = "9" + d
    if len(d) == 10:
        d = "90" + d
    return d


def place_of(l):
    return ", ".join(x for x in [l.get("neighborhood"), l.get("district"), l.get("province")] if x)


def full_address(l):
    return ", ".join(x.strip() for x in [l.get("address") or "", l.get("neighborhood") or "", l.get("district") or "", l.get("province") or ""] if x.strip())


def is_warm(a):
    return bool(re.search(r"ısıtma|jakuzi|şömine", a, re.I))


def listing_row(l):
    url = f'/tesisler/{l["slug"]}/'
    ph = l["photos"][:3]
    use = ph if len(ph) == 3 else ph[:1]
    shots = "".join(f'<img src="{photo_url(p["path"])}" alt="" loading="lazy">' for p in use)
    tags = [f'<li class="{"warm" if is_warm(a) else ""}">{esc(a)}</li>' for a in (l.get("amenities") or [])[:5]]
    if l.get("pets") == "evet":
        tags.append("<li>Evcil hayvan kabul edilir</li>")
    summary = f'<p>{esc(l["summary"])}</p>' if l.get("summary") else ""
    tag_html = f'<ul class="tags" aria-label="Öne çıkan olanaklar">{"".join(tags)}</ul>' if tags else ""
    return f"""<article class="fac" data-slug="{esc(l['slug'])}" data-il="{esc(l.get('province') or '')}">
  <a class="shots{'' if len(ph) == 3 else ' one'}" href="{url}" tabindex="-1" aria-hidden="true">{shots}</a>
  <div>
    <h3><a href="{url}">{esc(l["name"])}</a></h3>
    <p class="place">{esc(place_of(l))}</p>
    {summary}
    {tag_html}
    <div class="actions"><a class="btn solid" href="{url}">Tesisi incele</a></div>
  </div>
</article>"""


def paras(text):
    out = []
    for p in re.split(r"\n\s*\n", text or ""):
        if p.strip():
            out.append("<p>" + esc(re.sub(r"\s*\n\s*", " ", p.strip())) + "</p>")
    return "".join(out)


def listing_crumbs(l, self_path=None):
    items = [("/tesisler/", "Tesisler")]
    il, ilce = l.get("province"), l.get("district")
    if (il, ilce) in REGIONS:
        items += [(region_path(il), il), (region_path(il, ilce), ilce)]
    return items + [(self_path, l["name"])]


def build_listing(l):
    path = f'/tesisler/{l["slug"]}/'
    photos = l["photos"]
    name = l["name"]
    place = place_of(l)
    tags = [f'<li class="{"warm" if is_warm(a) else ""}">{esc(a)}</li>' for a in (l.get("amenities") or [])[:6]]
    if l.get("pets") == "evet":
        tags.append("<li>Evcil hayvan kabul edilir</li>")
    gcls = "gallery" + (" n1" if len(photos) == 1 else " few" if len(photos) < 5 else "")
    gal = "".join(f'<a href="{photo_url(p["path"])}" target="_blank" rel="noopener"><img src="{photo_url(p["path"])}" '
                  f'alt="{esc((p.get("alt") + " — ") if p.get("alt") else "")}{esc(name)}" loading="{"eager" if i == 0 else "lazy"}"></a>'
                  for i, p in enumerate(photos[:9]))
    more = ""
    if len(photos) > 9:
        rest = "".join(f'<a href="{photo_url(p["path"])}" target="_blank" rel="noopener"><img src="{photo_url(p["path"])}" alt="{esc(p.get("alt") or name)}" loading="lazy"></a>' for p in photos[9:])
        more = f'<details class="more-photos"><summary>Bütün fotoğraflar ({len(photos)})</summary><div class="gallery">{rest}</div></details>'
    facts = []
    if l.get("units"):
        facts.append(("Bungalov sayısı", str(l["units"])))
    if l.get("capacity"):
        facts.append(("Kapasite", l["capacity"]))
    if l.get("beds"):
        facts.append(("Yatak", l["beds"]))
    if l.get("checkin") or l.get("checkout"):
        facts.append(("Giriş / çıkış", f'{l.get("checkin") or "—"} / {l.get("checkout") or "—"}'))
    facts_html = ('<dl class="facts">' + "".join(f"<div><dt>{esc(a)}</dt><dd>{esc(b)}</dd></div>" for a, b in facts) + "</dl>") if facts else ""
    desc = f'<h2>Tesis hakkında</h2>{paras(l.get("description"))}' if l.get("description") else ""
    amen = ""
    if l.get("amenities"):
        amen = '<h2>Olanaklar</h2><ul class="amen">' + "".join(f"<li>{esc(a)}</li>" for a in l["amenities"]) + "</ul>"
    rules = [re.sub(r"^[-•*]\s*", "", x.strip()) for x in (l.get("rules") or "").split("\n") if x.strip()]
    if l.get("pets") in PETS:
        rules.append(PETS[l["pets"]] + ".")
    rules_html = ('<h2>Bilmeniz gerekenler</h2><ul>' + "".join(f"<li>{esc(r)}</li>" for r in rules) + "</ul>") if rules else ""
    q = full_address(l)
    loc = ""
    if l.get("address") or l.get("neighborhood"):
        loc = (f'<h2>Konum</h2><p>{esc(q)}. <a href="https://www.google.com/maps/search/?api=1&amp;query={quote(name + ", " + q)}" rel="noopener" target="_blank">Haritada aç</a></p>'
               f'<div class="map"><iframe src="https://maps.google.com/maps?q={quote(q)}&amp;z=14&amp;output=embed" title="{esc(name)} konumu" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>')
    report = wa(f"Merhaba, Bungalov Dünyası'ndaki şu tesis sayfasıyla ilgili bildirim yapmak istiyorum: {SITE}{path}")
    btns = ""
    if l.get("booking_url") and with_utm(l["booking_url"]):
        btns += f'<a class="btn solid" href="{esc(with_utm(l["booking_url"]))}" rel="noopener nofollow" target="_blank">Takvimi ve fiyatı gör</a>'
    w = digits(l.get("whatsapp") or l.get("phone"))
    if len(w) >= 11:
        msg = quote(f"Merhaba, Bungalov Dünyası'ndan ulaşıyorum. {name} için müsaitlik sormak istiyorum: [giriş] – [çıkış], [kişi sayısı] kişi.")
        btns += f'<a class="btn wa" href="https://wa.me/{w}?text={msg}" rel="noopener">WhatsApp\'tan sor</a>'
    t = digits(l.get("phone") or l.get("whatsapp"))
    if len(t) >= 11:
        btns += f'<a class="btn line" href="tel:+{t}">Ara: {esc(l.get("phone") or l.get("whatsapp"))}</a>'
    links = []
    if l.get("website") and safe_url(l["website"]):
        links.append(f'<a href="{esc(with_utm(l["website"]))}" rel="noopener nofollow" target="_blank">Web sitesi</a>')
    if l.get("instagram"):
        ig = re.sub(r"[^A-Za-z0-9._]", "", l["instagram"])
        if ig:
            links.append(f'<a href="https://instagram.com/{ig}" rel="noopener nofollow" target="_blank">Instagram: @{ig}</a>')
    links_html = f'<p style="margin:14px 0 0;font-size:15px">{" · ".join(links)}</p>' if links else ""
    body = f"""
<div class="wrap">{crumbs(listing_crumbs(l))}
<header class="page-head"><h1>{esc(name)}</h1>
{f'<p class="place" style="margin-top:10px">{esc(place)}</p>' if place else ""}
{f'<p>{esc(l["summary"])}</p>' if l.get("summary") else ""}
{f'<ul class="tags" style="margin-top:18px">{"".join(tags)}</ul>' if tags else ""}
<div class="fav-row" id="fav-slot" data-slug="{esc(l['slug'])}"></div>
</header>
{f'<div class="{gcls}">{gal}</div>' if photos else ""}{more}
<div class="layout">
<div class="prose">
  {facts_html}
  {desc}
  {amen}
  {rules_html}
  {loc}
  <p class="disclose">Bu sayfadaki bilgiler ve fotoğraflar tesis sahibi tarafından eklendi. Fiyat ve müsaitlik için tesisle doğrudan görüşün. Hatalı ya da yanıltıcı bir bilgi görürseniz <a href="{report}" rel="noopener">bize bildirin</a>.</p>
</div>
<aside class="aside" aria-label="İletişim">
  <h3>Müsaitlik ve fiyat</h3>
  <p>Fiyat ve boş tarihler için tesisle doğrudan iletişime geçin. Komisyon yok.</p>
  {btns}
  {links_html}
</aside>
</div>
</div>
"""
    lodging = {"@context": "https://schema.org", "@type": "LodgingBusiness", "name": name, "url": SITE + path,
               "address": {"@type": "PostalAddress", "addressLocality": l.get("district") or "", "addressRegion": l.get("province") or "", "addressCountry": "TR"}}
    if l.get("summary"):
        lodging["description"] = l["summary"]
    if photos:
        lodging["image"] = [photo_url(p["path"]) for p in photos[:5]]
    if t:
        lodging["telephone"] = "+" + t
    if l.get("address"):
        lodging["address"]["streetAddress"] = ", ".join(x for x in [l["address"], l.get("neighborhood")] if x)
    if l.get("checkin"):
        lodging["checkinTime"] = l["checkin"]
    if l.get("checkout"):
        lodging["checkoutTime"] = l["checkout"]
    if l.get("units"):
        lodging["numberOfRooms"] = l["units"]
    if l.get("amenities"):
        lodging["amenityFeature"] = [{"@type": "LocationFeatureSpecification", "name": a, "value": True} for a in l["amenities"]]
    where = ", ".join(x for x in [l.get("district"), l.get("province")] if x)
    title = f"{name} – {where + ' ' if where else ''}Bungalov | Bungalov Dünyası"
    desc_meta = (l.get("summary") or f"{name}: fotoğraflar, olanaklar ve doğrudan iletişim bilgileri.")[:160]
    write(path, page(path, title, desc_meta, body, [lodging, crumbs_ld(listing_crumbs(l, path))],
                     active="/tesisler/", og_image=photo_url(photos[0]["path"]) if photos else None, scripts=["fav"]))


# ---------------------------------------------------------------- Sayfalar
def build_home():
    find = "".join(f'<a href="{h}">{t}</a>' for h, t in [
        (region_path("Sakarya", "Sapanca"), "Sapanca"),
        ("/rehber/kisin-sapanca-bungalov-isitmali-havuz-jakuzi-somine/", "Kış için: jakuzi ve şömine"),
        ("/rehber/evcil-hayvanla-sapanca-bungalov/", "Evcil hayvanla"),
        ("/rehber/sapanca-bungalov-kiralamadan-once-sorulacak-sorular/", "İlk kez kiralayacağım")])
    body = f"""
<section class="hero">
  <img class="hero-img" src="{ux('hero', 1920, 1100)}" srcset="{ux('hero', 900, 1100)} 900w, {ux('hero', 1920, 1100)} 1920w" sizes="100vw" alt="{esc(PHOTOS['hero'][1])}" fetchpriority="high">
  <div class="wrap">
    <div class="copy">
      <h1>Bungalov tatili, fotoğrafın ötesiyle.</h1>
      <p class="lead">Havuz gerçekten özel mi, jakuzi kışın sıcak mı, şömine yanıyor mu? Türkiye'deki bungalov tesislerini ayrıntısıyla anlatıyor, sizi doğrudan tesisle buluşturuyoruz.</p>
      <div class="find" aria-label="Ne arıyorsunuz?">{find}</div>
    </div>
    <p class="hero-credit">{credit('hero')}</p>
  </div>
</section>

<section class="block"><div class="wrap">
  <div class="head"><h2>Bölgeler</h2><p>Rehbere Sapanca'daki tesislerle başladık. Karadeniz yaylalarından Ege ve Akdeniz kıyısına, yeni bölgeler tesis sahipleri katıldıkça ekleniyor.</p></div>
  <nav class="regions" aria-label="Bölgeler">{region_chips()}<a class="add" href="/tesis-ekle/">+ Bölgenizdeki tesisi ekleyin</a></nav>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap">
  <div class="head"><h2>Tesisler</h2><p>Listeye yalnızca gerçek fotoğrafı ve net bilgisi olan bungalovlar giriyor.</p></div>
  <div class="fac-list">
  {fac_row(LABELLA)}
  {"".join(listing_row(l) for l in LISTINGS[:3])}
  </div>
  {f'<p class="more-link"><a class="btn line" href="/tesisler/">Bütün tesisler ({len(LISTINGS) + 1})</a></p>' if len(LISTINGS) > 3 else ""}
  {SLOT}
</div></section>

<section class="block mist"><div class="wrap">
  <div class="head"><h2>Rehber</h2><p>Bungalov seçerken işinize yarayacak kısa ve somut yazılar.</p></div>
  {guide_list()}
</div></section>

{owner_band()}
"""
    schema = [{"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE + "/", "inLanguage": "tr"},
              {"@context": "https://schema.org", "@type": "Organization", "name": NAME, "url": SITE + "/",
               "logo": SITE + "/favicon.svg",
               "contactPoint": {"@type": "ContactPoint", "telephone": "+" + WA, "contactType": "customer support", "areaServed": "TR", "availableLanguage": "Turkish"}}]
    write("/", page("/", "Bungalov Dünyası: Havuzlu, Jakuzili ve Şömineli Bungalovlar",
                    "Türkiye'de özel havuzlu, jakuzili ve şömineli bungalovlar. Tesisleri ayrıntısıyla tanıyın, rezervasyonu komisyonsuz doğrudan tesisle yapın.",
                    body, schema))


def guide_list():
    items = "".join(f'<li><a href="/rehber/{g["slug"]}/"><img src="{ux(g["img"], 360, 240)}" alt="" loading="lazy" width="180" height="120"><h3>{esc(g["title"])}</h3><p>{esc(g["desc"])}</p><span class="min">{g["minutes"]} dk okuma</span></a></li>' for g in GUIDES)
    return f'<ul class="guides">{items}</ul>'


def owner_band():
    return f"""<section class="band"><div class="wrap">
  <div>
    <h2>Bungalov işletiyorsanız</h2>
    <p>Tesisinizi Bungalov Dünyası'na ücretsiz ekleyin. Misafir size doğrudan WhatsApp'tan ya da telefonla ulaşır; araya komisyon girmez.</p>
  </div>
  <div>
    <ul>
      <li>Ücretsiz üye olun, tesisinizi kendiniz ekleyin; sayfanız hemen yayında</li>
      <li>Ücretsiz Bungalov Yönetim uygulaması: takvim, rezervasyon ve misafir mesajları tek yerde</li>
      <li>Kendi web sitenize ekleyebileceğiniz rezervasyon sayfası</li>
    </ul>
    <p class="actions" style="margin-top:20px"><a class="btn ember" href="/tesis-ekle/">Tesisinizi ekleyin</a><a class="btn ghost-light" href="/uygulama/">Uygulamayı inceleyin</a></p>
  </div>
</div></section>"""


def build_facilities():
    body = f"""
<div class="wrap">{crumbs([(None, "Tesisler")])}
<header class="page-head"><h1>Bungalov tesisleri</h1>
<p>Listeye yalnızca gerçek fotoğrafı ve net bilgisi olan tesisleri ekliyoruz. Fiyat ve müsaitlik için tesisle doğrudan görüşürsünüz.</p></header>
<nav class="regions" aria-label="Bölgeler">{region_chips()}</nav>
</div>
<section class="block" style="padding-top:28px"><div class="wrap">
  <div id="uye-tesisler" class="fac-list">
  {fac_row(LABELLA)}
  {"".join(listing_row(l) for l in LISTINGS)}
  </div>
  {SLOT}
</div></section>
"""
    write("/tesisler/", page("/tesisler/", "Bungalov Tesisleri: Özel Havuzlu, Jakuzili, Şömineli – Bungalov Dünyası",
                             "Türkiye'de özel havuzlu, jakuzili ve şömineli bungalov tesisleri. Fotoğraflar, olanaklar ve doğrudan iletişim bilgileri.",
                             body, [crumbs_ld([("/tesisler/", "Tesisler")])], active="/tesisler/", scripts=["tesisler"]))


def build_regions():
    """Tesisi olan her il ve ilçe için bölge sayfası."""
    for (il, ilce), r in REGIONS.items():
        path = region_path(il, ilce)
        title, intro = REGION_INTRO.get((il, ilce), (f"{ilce} bungalovları", f"{ilce} ({il}) bölgesindeki bungalov tesisleri. Fotoğraflarına, olanaklarına ve kurallarına bakın; rezervasyonu doğrudan tesisle, komisyonsuz yapın."))
        rows = (fac_row(LABELLA) if r["labella"] else "") + "".join(listing_row(l) for l in r["listings"])
        guides = [g for g in GUIDES if g["bolge"] == f"{tr_slug(il)}/{tr_slug(ilce)}"]
        g_html = ""
        if guides:
            items = "".join(f'<li><a href="/rehber/{g["slug"]}/"><img src="{ux(g["img"], 360, 240)}" alt="" loading="lazy" width="180" height="120"><h3>{esc(g["title"])}</h3><p>{esc(g["desc"])}</p><span class="min">{g["minutes"]} dk okuma</span></a></li>' for g in guides)
            g_html = f'<section class="block mist"><div class="wrap"><div class="head"><h2>{esc(ilce)} rehberi</h2></div><ul class="guides">{items}</ul></div></section>'
        n = region_count((il, ilce))
        body = f"""
<div class="wrap">{crumbs([("/tesisler/", "Tesisler"), (region_path(il), il), (None, ilce)])}
<header class="page-head"><h1>{esc(title)}</h1><p>{esc(intro)}</p></header>
<nav class="regions" aria-label="Bölgeler">{region_chips((il, ilce))}</nav>
</div>
<section class="block" style="padding-top:28px"><div class="wrap">
  <div class="fac-list">{rows}</div>
  <div class="slot">
    <p><strong>{esc(ilce)}'da bungalov mu işletiyorsunuz?</strong>Tesisinizi ücretsiz ekleyin; bu sayfada hemen yer alsın.</p>
    <a class="btn solid" href="/tesis-ekle/">Tesisinizi ekleyin</a>
  </div>
</div></section>
{g_html}
"""
        write(path, page(path, f"{ilce} Bungalov: Özel Havuzlu, Jakuzili Tesisler – Bungalov Dünyası",
                         f"{ilce}, {il} bölgesinde {n} bungalov tesisi: fotoğraflar, olanaklar ve doğrudan iletişim. Rezervasyon komisyonsuz, doğrudan tesisle.",
                         body, [crumbs_ld([("/tesisler/", "Tesisler"), (region_path(il), il), (path, ilce)])], active="/tesisler/"))
    for il, ilceler in PROVINCES.items():
        path = region_path(il)
        rows = ""
        for ilce in sorted(ilceler):
            r = REGIONS[(il, ilce)]
            rows += (fac_row(LABELLA) if r["labella"] else "") + "".join(listing_row(l) for l in r["listings"])
        n = sum(region_count((il, x)) for x in ilceler)
        chips = "".join(f'<a href="{region_path(il, x)}">{esc(x)}<small>{region_count((il, x))} tesis</small></a>' for x in sorted(ilceler))
        body = f"""
<div class="wrap">{crumbs([("/tesisler/", "Tesisler"), (None, il)])}
<header class="page-head"><h1>{esc(il)} bungalovları</h1><p>{esc(il)} ilindeki bungalov tesisleri. İlçeye göre bakabilir, rezervasyonu doğrudan tesisle yapabilirsiniz.</p></header>
<nav class="regions" aria-label="İlçeler">{chips}</nav>
</div>
<section class="block" style="padding-top:28px"><div class="wrap">
  <div class="fac-list">{rows}</div>
  {SLOT}
</div></section>
"""
        write(path, page(path, f"{il} Bungalov Tesisleri – Bungalov Dünyası",
                         f"{il} ilinde {n} bungalov tesisi: {', '.join(sorted(ilceler))}. Fotoğraflar, olanaklar ve doğrudan iletişim.",
                         body, [crumbs_ld([("/tesisler/", "Tesisler"), (path, il)])], active="/tesisler/"))


def build_labella():
    f = LABELLA
    path = f'/tesisler/{f["slug"]}/'
    gal = "".join(f'<img src="{UP}{s}" alt="{esc(a)} — {esc(f["name"])}" loading="{"eager" if i == 0 else "lazy"}" width="733" height="1024">'
                  for i, (s, a) in enumerate([f["shots"][0]] + f["gallery"]))
    tags = "".join(f'<li class="{c}">{esc(t)}</li>' for t, c in f["tags"])
    amen = ["Bungalova özel açık yüzme havuzu (ısıtmalı)", "Terasta sıcak jakuzi", "Şömine", "Tam donanımlı mutfak", "Klima",
            "Smart TV", "Ücretsiz Wi-Fi", "Barbekü ve mangal alanı", "Ateş çukuru", "Bahçe salıncağı", "Orman manzarası", "Özel otopark"]
    amen_html = "".join(f"<li>{esc(a)}</li>" for a in amen)
    ask = wa(f"Merhaba, Bungalov Dünyası'ndan ulaşıyorum. Labella Bungalov için müsaitlik sormak istiyorum: [giriş] – [çıkış], [kişi sayısı] kişi.")
    body = f"""
<div class="wrap">{crumbs([("/tesisler/", "Tesisler"), (region_path("Sakarya"), "Sakarya"), (region_path("Sakarya", "Sapanca"), "Sapanca"), (None, f["name"])])}
<header class="page-head"><h1>{esc(f["name"])}</h1>
<p>{esc(f["summary"])}</p>
<ul class="tags" style="margin-top:18px">{tags}</ul></header>
<div class="gallery">{gal}</div>
<div class="layout">
<div class="prose">
  <dl class="facts">
    <div><dt>Bungalov sayısı</dt><dd>5 bağımsız A-frame</dd></div>
    <div><dt>Kapasite</dt><dd>4+1 kişi</dd></div>
    <div><dt>Yatak</dt><dd>1 çift, 2 tek</dd></div>
    <div><dt>Kullanım alanı</dt><dd>~65 m²</dd></div>
    <div><dt>Giriş / çıkış</dt><dd>14:00 / 11:30</dd></div>
  </dl>
  <h2>Bungalovlar</h2>
  <p>Labella Bungalov, Sapanca'nın Memnuniye Mahallesi'nde ormanla çevrili bir alanda beş bağımsız A-frame bungalovdan oluşuyor. Bungalovların hepsi aynı tipte: alt katta salon ve mutfak, bir çift kişilik ve bir iki tek yataklı oda, önünde geniş bir teras ve yalnızca o bungalovu kullananlara ait bir havuz.</p>
  <p>Havuzlar ısıtmalı ve her bungalovun terasında sıcak jakuzi var. Serin akşamlar için içeride şömine bulunuyor. Bu üçlü, tesisi özellikle ilkbahar, sonbahar ve kış için uygun hale getiriyor.</p>
  <h2>Olanaklar</h2>
  <ul class="amen">{amen_html}</ul>
  <h2>Bilmeniz gerekenler</h2>
  <ul>
    <li>Giriş saati 14:00, çıkış saati 11:30.</li>
    <li>Evcil hayvanla gelmek istiyorsanız uygunluk ve koşulları rezervasyondan önce sorun.</li>
    <li>Kış aylarında gelecekseniz havuz ısıtması ve yol durumu için tesisle önceden konuşun.</li>
  </ul>
  <h2>Konum</h2>
  <p>{esc(f["address"]["street"])}, {esc(f["address"]["locality"])} / {esc(f["address"]["region"])}. <a href="https://www.google.com/maps/search/?api=1&query={quote('Labella Bungalov Sapanca')}" rel="noopener">Haritada aç</a></p>
  <p class="disclose">Açıklık notu: Bungalov Dünyası ve Labella Bungalov aynı ekip tarafından işletiliyor. Rehberdeki diğer tesislere de aynı ölçütleri uyguluyoruz: gerçek fotoğraf ve doğru bilgi.</p>
</div>
<aside class="aside" aria-label="İletişim">
  <h3>Müsaitlik ve fiyat</h3>
  <p>Fiyat ve boş tarihler için tesisle doğrudan iletişime geçin. Komisyon yok.</p>
  <a class="btn solid" href="{f['booking']}?{UTM}" rel="noopener">Takvimi ve fiyatı gör</a>
  <a class="btn wa" href="{ask}" rel="noopener">WhatsApp'tan sor</a>
  <a class="btn line" href="tel:{f['phone']}">Ara: {f['phone_txt']}</a>
  <p style="margin:14px 0 0;font-size:15px">Diğer hat: <a href="tel:{f['phone2']}">{f['phone2_txt']}</a></p>
</aside>
</div>
</div>
"""
    lodging = {
        "@context": "https://schema.org", "@type": "LodgingBusiness", "name": f["name"], "url": f["site"],
        "description": f["summary"], "telephone": f["phone"],
        "image": [UP + s for s, _ in [f["shots"][0]] + f["gallery"][:4]],
        "address": {"@type": "PostalAddress", "streetAddress": f["address"]["street"], "addressLocality": f["address"]["locality"],
                    "addressRegion": f["address"]["region"], "addressCountry": "TR"},
        "checkinTime": "14:00", "checkoutTime": "11:30", "numberOfRooms": 5,
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": a, "value": True} for a in amen],
    }
    write(path, page(path, "Labella Bungalov Sapanca: Özel Havuzlu, Jakuzili A-Frame",
                     "Sapanca Memnuniye'de 5 bağımsız A-frame bungalov: ısıtmalı özel havuz, sıcak jakuzi, şömine, 4+1 kişilik. Fotoğraflar, olanaklar ve doğrudan iletişim.",
                     body, [lodging, crumbs_ld([("/tesisler/", "Tesisler"), (region_path("Sakarya"), "Sakarya"), (region_path("Sakarya", "Sapanca"), "Sapanca"), (path, f["name"])])], active="/tesisler/",
                     og_image=UP + f["shots"][0][0]))


def build_guides():
    body = f"""
<div class="wrap">{crumbs([(None, "Rehber")])}
<header class="page-head"><h1>Bungalov rehberi</h1>
<p>Bungalov seçerken neye bakmalı, hangi mevsimde ne beklemeli, nelere dikkat etmeli? Kısa ve somut yazılar.</p></header>
<div class="prose" style="max-width:none">{guide_list()}</div>
</div>
"""
    write("/rehber/", page("/rehber/", "Bungalov Rehberi: Sapanca, Kış Tatili, Balayı, Evcil Hayvan",
                           "Bungalov kiralamadan önce bilmeniz gerekenler: sorulacak sorular, kışın ısıtmalı havuz ve jakuzi, evcil hayvanla tatil ve bölge rehberleri.",
                           body, [crumbs_ld([("/rehber/", "Rehber")])], active="/rehber/"))
    for g in GUIDES:
        path = f'/rehber/{g["slug"]}/'
        faq_html = ""
        if g["faq"]:
            faq_html = "<h2>Sık sorulanlar</h2>" + "".join(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in g["faq"])
        others = "".join(f'<li><a href="/rehber/{o["slug"]}/">{esc(o["title"])}</a></li>' for o in GUIDES if o is not g)
        body = f"""
<div class="wrap">{crumbs([("/rehber/", "Rehber"), (None, g["title"])])}
<header class="page-head"><h1>{esc(g["title"])}</h1><p>{esc(g["desc"])}</p><div class="meta">{g["minutes"]} dk okuma</div></header>
{cover(g["img"])}
<div class="layout">
<article class="prose">
{g["body"]}
{faq_html}
</article>
<aside class="aside" aria-label="Önerilen">
  <h3>Bu özelliklere sahip bir tesis</h3>
  <p><a href="/tesisler/labella-bungalov/">Labella Bungalov</a>: ısıtmalı özel havuz, sıcak jakuzi ve şömine, Sapanca Memnuniye.</p>
  <a class="btn solid" href="/tesisler/labella-bungalov/">Bungalovu incele</a>
  <h3 style="margin-top:26px">Diğer yazılar</h3>
  <ul style="padding-left:1.1em;margin:0">{others}</ul>
</aside>
</div>
</div>
"""
        schema = [{"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["desc"],
                   "inLanguage": "tr", "image": ux(g["img"], 1200, 630), "datePublished": g["date"], "dateModified": g["date"], "mainEntityOfPage": SITE + path,
                   "author": {"@type": "Organization", "name": NAME, "url": SITE + "/"},
                   "publisher": {"@type": "Organization", "name": NAME, "url": SITE + "/"}},
                  crumbs_ld([("/rehber/", "Rehber"), (path, g["title"])])]
        if g["faq"]:
            schema.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in g["faq"]]})
        write(path, page(path, g["seo_title"] + " | Bungalov Dünyası", g["desc"], body, schema, active="/rehber/", og_image=ux(g["img"], 1200, 630), og_type="article"))


def field(id_, label, kind="text", hint="", attrs="", wide=False):
    """Form alanı: etiket + girdi + isteğe bağlı açıklama."""
    h = f'<small class="hint">{hint}</small>' if hint else ""
    if kind == "textarea":
        inp = f'<textarea id="{id_}" {attrs}></textarea>'
    elif kind == "select":
        inp = f'<select id="{id_}">{attrs}</select>'
    else:
        inp = f'<input id="{id_}" type="{kind}" {attrs}>'
    return f'<label class="fld{" wide" if wide else ""}" for="{id_}"><span>{label}</span>{inp}{h}</label>'


def counter(target):
    return f'<div class="ai-bar"><span class="count" id="{target}-n"></span></div>'


KVKK_LINE = ('<a href="/uyelik-kosullari/" target="_blank">Üyelik koşullarını</a> kabul ediyorum, '
             '<a href="/kvkk/" target="_blank">aydınlatma metnini</a> okudum.')
GOOGLE_SVG = ('<svg viewBox="0 0 48 48" aria-hidden="true" width="20" height="20"><path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3 0 5.8 1.1 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/>'
              '<path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3 0 5.8 1.1 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/>'
              '<path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-7.9l-6.5 5C9.5 39.6 16.2 44 24 44z"/>'
              '<path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z"/></svg>')


def kind_cards(name):
    return f"""<fieldset class="kind"><legend>Üyelik türü</legend>
  <label class="kind-card"><input type="radio" name="{name}" value="kurumsal"><span><strong>Kurumsal üyelik</strong>Tesis sahibiyim. Tesisimi ekleyip yönetmek istiyorum.</span></label>
  <label class="kind-card"><input type="radio" name="{name}" value="kisisel"><span><strong>Kişisel üyelik</strong>Tatil için bungalov arıyorum. Beğendiklerimi kaydetmek istiyorum.</span></label>
</fieldset>"""


def build_member():
    body = f"""
<div class="wrap">{crumbs([(None, "Üyelik")])}
<div class="auth-grid">
<section class="auth-card">
  <div class="tabs" role="tablist"><button type="button" role="tab" data-panel="p-giris">Giriş yap</button><button type="button" role="tab" data-panel="p-kayit">Üye ol</button></div>
  <div id="uye-msg" class="msg" role="status" hidden></div>

  <div id="p-giris" class="uye-panel">
    <h1>Giriş yapın</h1>
    <button type="button" class="btn-google">{GOOGLE_SVG}Google ile devam edin</button>
    <p class="or"><span>ya da e-posta ile</span></p>
    <form id="f-giris">
      {field("g-email", "E-posta", "email", attrs='required autocomplete="email"')}
      {field("g-sifre", "Şifre", "password", attrs='required autocomplete="current-password"')}
      <div class="form-actions"><button class="btn solid" type="submit">Giriş yap</button><a href="#" id="sifre-unuttum">Şifremi unuttum</a></div>
    </form>
  </div>

  <div id="p-kayit" class="uye-panel" hidden>
    <h1>Ücretsiz üye olun</h1>
    <form id="f-kayit">
      {kind_cards("kind")}
      <button type="button" class="btn-google">{GOOGLE_SVG}Google ile üye olun</button>
      <p class="or"><span>ya da e-posta ile</span></p>
      {field("k-ad", "Ad soyad", attrs='required autocomplete="name" maxlength="80"')}
      <div class="only-kurumsal" hidden>
        {field("k-firma", "Tesisinizin adı", hint="Birden fazla tesisiniz varsa virgülle ayırın.", attrs='maxlength="200" placeholder="ör. Göl Evi Bungalov"')}
        {field("k-tel", "Cep telefonu", "tel", attrs='autocomplete="tel" maxlength="20" placeholder="05xx xxx xx xx"')}
      </div>
      {field("k-email", "E-posta", "email", attrs='required autocomplete="email"')}
      {field("k-sifre", "Şifre", "password", hint="En az 8 karakter.", attrs='required minlength="8" autocomplete="new-password"')}
      <label class="chk-line"><input type="checkbox" id="k-kvkk"><span>{KVKK_LINE}</span></label>
      <div class="form-actions"><button class="btn solid" type="submit">Üye ol</button></div>
    </form>
  </div>

  <div id="p-tamamla" class="uye-panel" hidden>
    <h1>Son bir adım</h1>
    <p>Hesabınız oluştu. Üyelik türünüzü seçip bilgilerinizi tamamlayın.</p>
    <form id="f-tamamla">
      {kind_cards("kind2")}
      {field("t-ad", "Ad soyad", attrs='required autocomplete="name" maxlength="80"')}
      <div class="only-kurumsal" hidden>
        {field("t-firma", "Tesisinizin adı", hint="Birden fazla tesisiniz varsa virgülle ayırın.", attrs='maxlength="200"')}
        {field("t-tel", "Cep telefonu", "tel", attrs='autocomplete="tel" maxlength="20"')}
      </div>
      <label class="chk-line"><input type="checkbox" id="t-kvkk"><span>{KVKK_LINE}</span></label>
      <div class="form-actions"><button class="btn solid" type="submit">Devam</button></div>
    </form>
  </div>

  <div id="p-sifre" class="uye-panel" hidden>
    <h1>Şifrenizi mi unuttunuz?</h1>
    <p>E-posta adresinizi yazın, şifrenizi yenilemeniz için bir bağlantı gönderelim.</p>
    <form id="f-sifre">
      {field("s-email", "E-posta", "email", attrs='required autocomplete="email"')}
      <div class="form-actions"><button class="btn solid" type="submit">Bağlantı gönder</button><a href="#" class="back-giris">Girişe dön</a></div>
    </form>
  </div>

  <div id="p-yeni" class="uye-panel" hidden>
    <h1>Yeni şifre</h1>
    <form id="f-yeni">
      {field("y-sifre", "Yeni şifreniz", "password", hint="En az 8 karakter.", attrs='required minlength="8" autocomplete="new-password"')}
      <div class="form-actions"><button class="btn solid" type="submit">Şifreyi kaydet</button></div>
    </form>
  </div>

  <div id="p-dogrula" class="uye-panel" hidden>
    <h1>E-postanızı doğrulayın</h1>
    <p><strong id="dogrula-email"></strong> adresine bir doğrulama bağlantısı gönderdik. Bağlantıya tıkladığınızda üyeliğiniz tamamlanır ve kaldığınız yerden devam edersiniz.</p>
    <p class="hint">E-posta birkaç dakika içinde gelmezse gereksiz (spam) klasörüne bakın.</p>
    <p><a href="#" class="back-giris">Girişe dön</a></p>
  </div>
</section>

<aside class="auth-side">
  <h2>Tesis sahipleri için</h2>
  <ul class="ticks">
    <li>Tesisinizi kendiniz ekleyin; kaydettiğiniz anda yayında</li>
    <li>Fotoğraflar, olanaklar, kurallar ve harita konumu</li>
    <li>Misafir size doğrudan ulaşır, komisyon yok</li>
    <li>Ücretsiz <a href="/uygulama/">Bungalov Yönetim</a> uygulaması</li>
  </ul>
  <h2>Tatilciler için</h2>
  <ul class="ticks">
    <li>Beğendiğiniz bungalovları favorilerinize kaydedin</li>
    <li>Rezervasyonu doğrudan tesisle, komisyonsuz yapın</li>
  </ul>
</aside>
</div>
</div>
"""
    write("/uye/", page("/uye/", "Giriş yap / Üye ol – Bungalov Dünyası", "Bungalov Dünyası'na ücretsiz üye olun: tesis sahipleri tesisini ekler, tatilciler favorilerini kaydeder.",
                        body, scripts=["uye"], noindex=True))


def build_account():
    app_msg = wa("Merhaba, Bungalov Dünyası kurumsal üyesiyim. Bungalov Yönetim uygulamasını kurmak istiyorum.")
    body = f"""
<div class="wrap">{crumbs([(None, "Hesabım")])}
<p id="hesap-yukleniyor" class="loading">Yükleniyor…</p>
<div id="hesap" hidden>
<header class="page-head"><h1>Hesabım</h1><p><span id="h-email"></span> · <span id="h-tur"></span></p></header>
<div id="hesap-msg" class="msg" role="status" hidden></div>
<div class="layout">
<div class="acct-main">
  <section id="kurumsal-bolum" hidden>
    <div class="head"><h2>Tesislerim</h2><a class="btn solid" href="/tesis-ekle/">+ Yeni tesis ekle</a></div>
    <div id="tesislerim" class="my-list"><p class="loading">Yükleniyor…</p></div>
    <div class="note"><p><strong>Bungalov Yönetim uygulaması size ücretsiz.</strong> Rezervasyon takvimi, kapora takibi, hazır WhatsApp mesajları ve ayın hesabı tek yerde. <a href="/uygulama/">Uygulamayı inceleyin</a> ya da kurulum için <a href="{app_msg}" rel="noopener">bize yazın</a>, birlikte kuralım.</p></div>
  </section>
  <section id="kisisel-bolum" hidden>
    <div class="head"><h2>Favorilerim</h2></div>
    <div id="favorilerim" class="my-list"><p class="loading">Yükleniyor…</p></div>
    <div class="note"><p>Bungalov tesisiniz mi var? <button type="button" id="kurumsala-gec" class="linkish">Kurumsal üyeliğe geçin</button>, tesisinizi ücretsiz ekleyin.</p></div>
  </section>
</div>
<aside class="aside">
  <h3>Bilgilerim</h3>
  <form id="f-profil">
    {field("h-ad", "Ad soyad", attrs='maxlength="80" autocomplete="name"')}
    {field("h-tel", "Telefon", "tel", attrs='maxlength="20" autocomplete="tel"')}
    <div id="h-firma-satir">{field("h-firma", "Tesis adları", attrs='maxlength="200"')}</div>
    <button class="btn solid" type="submit">Kaydet</button>
  </form>
  <button type="button" id="cikis" class="btn line">Çıkış yap</button>
  <p class="hint" style="margin-top:14px">Hesabınızı silmek için <a href="{wa('Merhaba, Bungalov Dünyası hesabımı silmek istiyorum. E-posta adresim: ')}" rel="noopener">bize yazın</a>.</p>
</aside>
</div>
</div>
</div>
"""
    write("/hesabim/", page("/hesabim/", "Hesabım – Bungalov Dünyası", "Bungalov Dünyası üyelik hesabınız.", body, scripts=["hesabim"], noindex=True))


def build_owner():
    opts_il = '<option value="">İl seçin</option>'
    opts_p = '<option value="sor">Önceden sorulsun</option><option value="evet">Kabul edilir</option><option value="hayir">Kabul edilmez</option>'
    body = f"""
<div class="wrap">{crumbs([("/hesabim/", "Hesabım"), (None, "Tesis ekle")])}
<header class="page-head"><h1 id="form-baslik">Tesisinizi ekleyin</h1>
<p>Bilgileri doldurun, fotoğraflarınızı yükleyin. Kaydettiğiniz anda sayfanız yayına girer; istediğiniz zaman düzenleyebilirsiniz.</p></header>
<p id="form-yukleniyor" class="loading">Yükleniyor…</p>
<div id="kisisel-uyari" class="note" hidden><p>Tesis eklemek için kurumsal üyelik gerekiyor. <a href="/hesabim/">Hesabım</a> sayfasından tek tıkla kurumsal üyeliğe geçebilirsiniz.</p></div>

<form id="tesis-form" class="tform" novalidate hidden>
<section class="fsec">
  <h2><span>1</span> Temel bilgiler</h2>
  {field("f-name", "Tesisin adı", attrs='required maxlength="80" placeholder="ör. Göl Evi Bungalov"', wide=True)}
  {field("f-summary", "Kısa tanıtım", "textarea", hint="Listede ve sayfanın başında görünür. 1-2 cümle.", attrs='rows="3" maxlength="300" data-max="300"', wide=True)}
  {counter("f-summary")}
  <div class="grid3">
    {field("f-units", "Bungalov sayısı", "number", attrs='min="1" max="200" inputmode="numeric"')}
    {field("f-capacity", "Kapasite", attrs='maxlength="80" placeholder="ör. 2+1 kişi"')}
    {field("f-beds", "Yatak düzeni", attrs='maxlength="120" placeholder="ör. 1 çift kişilik, 1 çekyat"')}
  </div>
</section>

<section class="fsec">
  <h2><span>2</span> Olanaklar</h2>
  <p class="hint">Tesisinizde gerçekten olanları işaretleyin. Isıtmalı yazdıysanız havuz gerçekten ısıtılıyor olmalı.</p>
  <div id="amenities" class="chk-grid"></div>
  <div class="grid3">{field("f-pets", "Evcil hayvan", "select", attrs=opts_p)}</div>
</section>

<section class="fsec">
  <h2><span>3</span> Tanıtım yazısı</h2>
  {field("f-description", "Açıklama", "textarea", hint="Bungalovları, olanakları, çevreyi ve kimlere uygun olduğunu anlatın. Paragraflar arasında boş satır bırakın.", attrs='rows="10" maxlength="6000" data-max="6000"', wide=True)}
  {counter("f-description")}
</section>

<section class="fsec">
  <h2><span>4</span> Fotoğraflar</h2>
  <p class="hint">En fazla 20 fotoğraf. İlk fotoğraf kapak olur. Fotoğraflar yüklenirken otomatik küçültülür. Yalnızca tesisinize ait fotoğrafları kullanın.</p>
  <div class="photo-bar"><button type="button" id="photo-pick" class="btn line">+ Fotoğraf ekle</button><span id="photo-count" class="count"></span><span id="photo-status" class="count"></span></div>
  <input type="file" id="photo-input" accept="image/jpeg,image/png,image/webp" multiple hidden>
  <div id="photos" class="photo-grid"></div>
</section>

<section class="fsec">
  <h2><span>5</span> Adres ve konum</h2>
  <div class="grid3">
    {field("f-province", "İl", "select", attrs=opts_il)}
    {field("f-district", "İlçe", attrs='maxlength="40" list="ilceler" autocomplete="off" placeholder="ör. Sapanca"')}
    {field("f-neighborhood", "Mahalle / köy", attrs='maxlength="80" placeholder="ör. Kırkpınar"')}
  </div>
  <datalist id="ilceler"></datalist>
  {field("f-address", "Açık adres", attrs='maxlength="300" placeholder="Sokak, numara"', wide=True)}
  <div class="map-prev"><iframe id="map-frame" title="Harita önizlemesi" loading="lazy" referrerpolicy="no-referrer-when-downgrade" hidden></iframe><p id="map-empty">Adresi yazdığınızda harita burada görünür.</p></div>
  <p class="hint">Harita yanlış yeri gösteriyorsa adrese mahalle ya da köy adını ekleyin. <a id="map-link" href="https://www.google.com/maps" target="_blank" rel="noopener">Google Haritalar'da aç</a></p>
</section>

<section class="fsec">
  <h2><span>6</span> Kurallar</h2>
  <div class="grid3">
    {field("f-checkin", "Giriş saati", "time")}
    {field("f-checkout", "Çıkış saati", "time")}
  </div>
  {field("f-rules", "Tesis kuralları", "textarea", hint="Her kuralı ayrı satıra yazın.", attrs='rows="6" maxlength="2000" data-max="2000" placeholder="- Sessiz saatler 23:00 – 08:00&#10;- İçeride sigara içilmez"', wide=True)}
  {counter("f-rules")}
</section>

<section class="fsec">
  <h2><span>7</span> İletişim</h2>
  <p class="hint">Misafirler size bu bilgilerle doğrudan ulaşır. Telefon ya da WhatsApp numarasından en az biri gerekli.</p>
  <div class="grid2">
    {field("f-phone", "Telefon", "tel", attrs='maxlength="20" placeholder="05xx xxx xx xx"')}
    {field("f-whatsapp", "WhatsApp numarası", "tel", attrs='maxlength="20" placeholder="05xx xxx xx xx"')}
    {field("f-website", "Web siteniz", "url", attrs='maxlength="200" placeholder="www.ornek.com"')}
    {field("f-booking-url", "Rezervasyon / takvim sayfanız", "url", attrs='maxlength="300" placeholder="Varsa"')}
    {field("f-instagram", "Instagram kullanıcı adı", attrs='maxlength="60" placeholder="@kullaniciadi"')}
  </div>
</section>

<label class="chk-line"><input type="checkbox" id="f-onay"><span>Bilgilerin doğru olduğunu, fotoğrafların bana ait olduğunu ya da kullanma hakkım bulunduğunu onaylıyorum.</span></label>
<div id="form-msg" class="msg" role="status" hidden></div>
<div class="form-actions sticky-actions">
  <button type="submit" id="kaydet" class="btn solid">Kaydet ve yayınla</button>
  <button type="submit" id="taslak" class="btn line">Taslak olarak kaydet</button>
  <a id="goruntule" class="btn line" target="_blank" hidden>Sayfayı görüntüle</a>
  <button type="button" id="sil" class="btn danger-line" hidden>Tesisi sil</button>
</div>
<div id="sil-onay" class="note warm" hidden><p>Tesis sayfası ve fotoğrafları kalıcı olarak silinecek. Emin misiniz?</p>
  <div class="actions"><button type="button" id="sil-evet" class="btn danger">Evet, sil</button><button type="button" id="sil-hayir" class="btn line">Vazgeç</button></div></div>
</form>
</div>
"""
    write("/tesis-ekle/", page("/tesis-ekle/", "Tesisinizi Ekleyin – Bungalov Dünyası",
                               "Bungalov tesisinizi Bungalov Dünyası'na ücretsiz ekleyin: fotoğraflar, olanaklar, konum ve doğrudan iletişim.",
                               body, scripts=["tesis-form"], noindex=True))


def build_listing_shell():
    body = """
<div class="wrap">
<p id="tesis-yukleniyor" class="loading" style="padding:60px 0">Yükleniyor…</p>
<div id="tesis-msg" class="msg" role="status" hidden></div>
<div id="tesis" hidden></div>
</div>
"""
    write("/tesis/", page("/tesis/", "Tesis – Bungalov Dünyası", "Bungalov tesisi: fotoğraflar, olanaklar ve doğrudan iletişim.",
                          body, scripts=["tesis"], noindex=True, active="/tesisler/"))


def build_legal():
    contact = f'<a href="{wa("Merhaba, kişisel verilerimle ilgili başvuru yapmak istiyorum.")}" rel="noopener">WhatsApp</a> ya da <a href="tel:+{WA}">0532 722 25 45</a>'
    kvkk = f"""
<div class="wrap">{crumbs([(None, "Kişisel verilerin korunması")])}
<header class="page-head"><h1>Kişisel verilerin korunması aydınlatma metni</h1><p>6698 sayılı Kişisel Verilerin Korunması Kanunu (KVKK) kapsamında, üyelerimizin ve ziyaretçilerimizin kişisel verilerini nasıl işlediğimizi açıklıyoruz.</p></header>
<div class="prose">
  <h2>Veri sorumlusu</h2>
  <p>Bungalov Dünyası (bungalovdunyasi.com), Sapanca / Sakarya. İletişim: {contact}.</p>
  <h2>Hangi verileri işliyoruz?</h2>
  <ul>
    <li><strong>Üyelik bilgileri:</strong> ad soyad, e-posta adresi, telefon numarası (kurumsal üyelerde), tesis adları, üyelik türü, şifrenizin geri döndürülemez özeti.</li>
    <li><strong>Google ile girişte:</strong> Google hesabınızın adı ve e-posta adresi.</li>
    <li><strong>Tesis bilgileri:</strong> kurumsal üyelerin eklediği tesis adı, adresi, iletişim bilgileri, açıklamaları ve fotoğrafları. Bu bilgiler tesis sayfasında herkese açık yayımlanır.</li>
    <li><strong>Favoriler:</strong> kişisel üyelerin kaydettiği tesisler.</li>
    <li><strong>Teknik bilgiler:</strong> oturumun açık kalması için tarayıcınızda tutulan oturum anahtarı. Ziyaret istatistiklerini çerez kullanmayan Cloudflare Web Analytics ile, kişiyi tanımlamadan tutarız.</li>
  </ul>
  <h2>Hangi amaçla?</h2>
  <ul>
    <li>Üyelik hesabınızı oluşturmak ve giriş yapmanızı sağlamak,</li>
    <li>Kurumsal üyelerin tesis sayfalarını yayımlamak ve misafirlerin tesisle doğrudan iletişim kurmasını sağlamak,</li>
    <li>Favorilerinizi saklamak,</li>
    <li>Hesabınızla ilgili zorunlu bildirimleri (e-posta doğrulama, şifre yenileme) göndermek,</li>
    <li>Kötüye kullanımı önlemek ve hukuki yükümlülüklerimizi yerine getirmek.</li>
  </ul>
  <h2>Hukuki sebep</h2>
  <p>Verileriniz, üyelik sözleşmesinin kurulması ve ifası (KVKK m. 5/2-c), hukuki yükümlülüklerimiz (m. 5/2-ç), tesis sayfalarında sizin tarafınızdan alenileştirilmesi (m. 5/2-d) ve meşru menfaatimiz (m. 5/2-f) hukuki sebeplerine dayanılarak işlenir.</p>
  <h2>Kimlere ve nereye aktarılır?</h2>
  <p>Verileriniz satılmaz ve reklam amacıyla paylaşılmaz. Hizmeti sunabilmek için aşağıdaki hizmet sağlayıcılardan yararlanırız; bu sağlayıcıların sunucuları yurt dışında bulunabilir:</p>
  <ul>
    <li><strong>Supabase</strong> (veritabanı, üyelik ve fotoğraf depolama),</li>
    <li><strong>GitHub Pages</strong> ve <strong>Cloudflare</strong> (sitenin yayımlanması ve ziyaret istatistikleri),</li>
    <li><strong>Google</strong> (yalnızca Google ile giriş yaptığınızda ve harita önizlemesi için).</li>
  </ul>
  <p>Yurt dışına aktarım, KVKK m. 9'da öngörülen şartlara uygun olarak yapılır.</p>
  <h2>Ne kadar süre saklanır?</h2>
  <p>Üyelik bilgileriniz hesabınız açık kaldığı sürece saklanır. Hesabınızı sildiğinizde üyelik bilgileriniz, tesis sayfalarınız, fotoğraflarınız ve favorileriniz silinir; yasal saklama yükümlülüğü olan kayıtlar bu süre boyunca tutulur.</p>
  <h2>Haklarınız</h2>
  <p>KVKK m. 11 uyarınca kişisel verilerinizin işlenip işlenmediğini öğrenme, bilgi talep etme, düzeltilmesini ya da silinmesini isteme, aktarıldığı kişileri bilme, itiraz etme ve zararın giderilmesini talep etme haklarına sahipsiniz. Başvurularınızı {contact} üzerinden iletebilirsiniz; en geç 30 gün içinde yanıtlarız.</p>
  <p class="disclose">Son güncelleme: 14 Ekim 2026</p>
</div>
</div>
"""
    write("/kvkk/", page("/kvkk/", "KVKK Aydınlatma Metni – Bungalov Dünyası", "Bungalov Dünyası kişisel verilerin korunması aydınlatma metni.", kvkk))
    terms = f"""
<div class="wrap">{crumbs([(None, "Üyelik koşulları")])}
<header class="page-head"><h1>Üyelik koşulları</h1><p>Bungalov Dünyası'na üye olarak aşağıdaki koşulları kabul etmiş olursunuz.</p></header>
<div class="prose">
  <h2>Hizmet</h2>
  <p>Bungalov Dünyası, Türkiye'deki bungalov tesislerini tanıtan ücretsiz bir rehberdir. Rezervasyon ve ödeme misafir ile tesis arasında doğrudan yapılır; Bungalov Dünyası bu işlemlerin tarafı değildir ve komisyon almaz.</p>
  <h2>Üyelik türleri</h2>
  <ul>
    <li><strong>Kurumsal üyelik</strong>, bungalov tesisi işleten ya da tesis adına yetkili kişiler içindir. Kurumsal üyeler tesis sayfası oluşturabilir ve düzenleyebilir.</li>
    <li><strong>Kişisel üyelik</strong>, tatil için tesis arayanlar içindir. Kişisel üyeler tesisleri favorilerine kaydedebilir.</li>
  </ul>
  <h2>Kurumsal üyelerin sorumlulukları</h2>
  <ul>
    <li>Yalnızca işlettiğiniz ya da yetkili olduğunuz tesisleri ekleyebilirsiniz.</li>
    <li>Tesis bilgileri doğru ve güncel olmalıdır. Olanaklar gerçeği yansıtmalıdır; örneğin "ısıtmalı havuz" yazıyorsa havuz gerçekten ısıtılıyor olmalıdır.</li>
    <li>Fotoğraflar tesisin kendisine ait olmalı; başkasına ait ya da telif hakkı size ait olmayan görseller kullanılmamalıdır.</li>
    <li>Sayfalarda fiyat garantisi, yanıltıcı kampanya, hakaret, kişisel veri ya da yasa dışı içerik yer alamaz.</li>
    <li>Tesis sayfasındaki içerikten ve misafirlerle yaptığınız anlaşmalardan siz sorumlusunuz.</li>
  </ul>
  <h2>Yayından kaldırma</h2>
  <p>Bu koşullara aykırı, yanıltıcı ya da misafirlerden ciddi şikâyet alan sayfaları önceden haber vermeksizin yayından kaldırabilir, gerekirse üyeliği sonlandırabiliriz.</p>
  <h2>Hesabın kapatılması</h2>
  <p>Hesabınızı istediğiniz zaman kapatabilirsiniz. Bunun için {contact} üzerinden bize yazmanız yeterli.</p>
  <h2>Değişiklikler</h2>
  <p>Bu koşulları güncelleyebiliriz. Önemli değişiklikleri sitede duyururuz.</p>
  <p class="disclose">Son güncelleme: 14 Ekim 2026. Kişisel verilerinizin nasıl işlendiği için <a href="/kvkk/">aydınlatma metnine</a> bakın.</p>
</div>
</div>
"""
    write("/uyelik-kosullari/", page("/uyelik-kosullari/", "Üyelik Koşulları – Bungalov Dünyası", "Bungalov Dünyası kurumsal ve kişisel üyelik koşulları.", terms))


# ---------------------------------------------------------------- Uygulama tanıtımı
APP_FEATURES = [
    ("takvim", "Bütün bungalovlar tek ekranda",
     "Hangi bungalov dolu, kim bugün geliyor, kimin çıkışı var, iki haftalık panoda bir bakışta görürsünüz. Sağdaki <strong>Bugün</strong> paneli ödemesi kalanları, gelecekleri ve çıkış yapacakları sıralar.",
     ["Airbnb ve Booking rezervasyonları takvim bağlantısıyla kendiliğinden gelir", "Aynı geceye iki rezervasyon girilemez", "Hafta sonu hava durumuna göre fiyat hatırlatması"]),
    ("form", "Rezervasyonu bir dakikada girin",
     "Misafirin adını, bungalovu ve tarihleri seçin. Hafta içi, hafta sonu ve bayram gecelerinin fiyatı kendiliğinden hesaplanır; gece gece dökümü formda görünür.",
     ["Kapora ve kalan ödeme takibi", "Ek yatak, kahvaltı gibi ek hizmetler", "Sendika ve kampanya indirimleri"]),
    ("whatsapp", "Misafire hazır WhatsApp mesajları",
     "Onay, giriş hatırlatması, kalan ödeme, teşekkür ve anket mesajları misafirin adı, tarihleri ve tutarıyla hazır gelir. Dilerseniz düzenler, tek tuşla WhatsApp'ta açarsınız.",
     ["Mesajı WhatsApp'tan siz gönderirsiniz", "Yazım derdi ve unutma yok"]),
    ("cikis", "Çıkışta misafiri değerlendirin",
     "Misafir ayrılırken bungalovu nasıl bıraktığını, kurallara uyup uymadığını ve tekrar ağırlamak isteyip istemediğinizi işaretlersiniz. Bir dahaki rezervasyonda bu bilgi karşınıza çıkar.",
     ["Yıldızla puan ve not", "Kara liste", "Çıkış sonrası misafire memnuniyet anketi, cevaplar uygulamada"]),
    ("fiyat", "Bayramlar ve tatiller fiyatınızda",
     "Resmi tatiller, bayramlar, arefeler ve okul tatilleri takvimde hazır. Hangisine özel gün fiyatı uygulanacağını tek dokunuşla seçersiniz.",
     ["Hafta içi, hafta sonu ve özel gün fiyatı", "Uzun konaklamaya gece gece artan indirim", "Belirli tarihler için kampanya"]),
    ("hesap", "Ayın kârını her an bilin",
     "Gelen para, giden para, kasadaki tutar ve misafirlerden henüz alınmayan ödemeler tek sayfada. Elektrik, temizlik, bakım gibi giderleri kendi kategorilerinizle girersiniz.",
     ["Aylık kâr/zarar", "Alınan ve alınacak ödemeler ayrı", "Geçen ayın giderlerini tek tuşla kopyalama"]),
    ("piyasa", "Rakip fiyatlarını takip edin",
     "Aynı tarihler için Airbnb, Tatil Sepeti, Booking, Etstur ve Tatilbudur aramalarını tek tıkla açın. Gördüğünüz fiyatları kaydedin; piyasa ortalaması ve sizin konumunuz hesaplanır.",
     ["Hafta sonu ve bayram için hızlı tarih seçimi", "En düşük, en yüksek ve ortalama"]),
]

APP_EXTRAS = [
    ("Bilgisayar, telefon, tablet", "Windows bilgisayarda, Android telefonda, iPhone ve iPad'de çalışır."),
    ("Bütün cihazlar aynı bilgiyi görür", "Bir cihazda girilen rezervasyon birkaç saniye içinde diğerlerine gelir."),
    ("Ekip için ayrı kullanıcılar", "Siz yönetici olursunuz; çalışanlarınıza kendi kullanıcı adlarını ve yetkilerini verirsiniz."),
    ("İnternet kesilse de çalışır", "Çevrimdışıyken girdikleriniz bağlantı gelince kendiliğinden eşitlenir."),
    ("Kendi rezervasyon sayfanız", "Misafirin boş tarihleri görüp talep bıraktığı sayfa. Web sitenize ve Instagram'ınıza eklersiniz; talepler uygulamaya düşer."),
    ("Kendini güncelleyen uygulama", "Yeni özellikler geldiğinde uygulama size sorar ve tek tuşla güncellenir."),
]

APP_FAQ = [
    ("Uygulama gerçekten ücretsiz mi?", "Evet. Bungalov Dünyası'na kurumsal üye olan tesisler uygulamayı ücretsiz kullanır. Kurulum ya da aylık ücret yok."),
    ("Verilerim kimde duruyor?", "Rezervasyonlarınız ve misafir bilgileriniz tesisinize ait bulut hesabında durur. Başka bir tesis sizin verinizi göremez. Uygulama her gün yedek de alır."),
    ("Bilgisayar kullanmayı pek bilmiyorum, zorlanır mıyım?", "Uygulama bilgisayara alışık olmayanlar düşünülerek sade tasarlandı. İlk açılışta kısa bir tur adım adım gösterir; kurulumu da sizinle birlikte yaparız."),
    ("Airbnb ve Booking'deki rezervasyonlarım ne olacak?", "Ayarlar'a ilanınızın takvim bağlantısını eklersiniz; o ilanlardaki rezervasyonlar 30 dakikada bir uygulamaya gelir. Elle rezervasyon girdiğinizde Airbnb'de tarihi kapatmanız için hatırlatma çıkar."),
    ("Kaç bungalovum olursa kullanabilirim?", "Bungalov sayısı sınırı yok. Bungalov ekleyip çıkarabilir, adlarını değiştirebilirsiniz."),
]


def build_app():
    msg = wa("Merhaba, Bungalov Yönetim uygulamasını tesisim için kullanmak istiyorum. Tesis adı: [ ], bungalov sayısı: [ ].")
    shot = lambda n, alt, eager=False: (f'<img src="/img/uygulama/{n}.webp" srcset="/img/uygulama/{n}-720.webp 720w, /img/uygulama/{n}.webp 1440w" '
                                        f'sizes="(max-width: 860px) 100vw, 640px" width="1440" height="900" alt="{esc(alt)}" loading="{"eager" if eager else "lazy"}">')
    rows = ""
    for i, (n, h, p, pts) in enumerate(APP_FEATURES):
        li = "".join(f"<li>{esc(x)}</li>" for x in pts)
        rows += f"""<section class="feat{' flip' if i % 2 else ''}">
  <figure class="screen">{shot(n, h + ' — Bungalov Yönetim ekranı (örnek veriler)')}</figure>
  <div class="feat-text"><h2>{esc(h)}</h2><p>{p}</p><ul class="ticks">{li}</ul></div>
</section>
"""
    extras = "".join(f'<div class="extra"><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for t, d in APP_EXTRAS)
    faq = "".join(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in APP_FAQ)
    body = f"""
<section class="app-hero"><div class="wrap">
  {crumbs([(None, "Bungalov Yönetim")])}
  <div class="app-hero-grid">
    <div class="app-hero-copy">
      <p class="kicker">Bungalov işletmecileri için ücretsiz uygulama</p>
      <h1>Defter, Excel ve WhatsApp arasında koşturmaya son.</h1>
      <p class="lead">Bungalov Yönetim; rezervasyonu, kaporayı, misafir mesajlarını ve ayın hesabını tek yerde tutar. Sapanca'da beş bungalovluk bir işletme, kendi ihtiyacı için geliştirdi ve her gün kullanıyor.</p>
      <div class="actions"><a class="btn ember" href="/uye/?tur=kurumsal">Ücretsiz üye olun</a><a class="btn ghost-light" href="#ozellikler">Neler yapıyor?</a></div>
    </div>
    <figure class="screen hero-screen">{shot("takvim", "Bungalov Yönetim takvim ekranı: beş bungalovun iki haftalık doluluk panosu (örnek veriler)", True)}</figure>
  </div>
</div></section>

<section class="block pains"><div class="wrap">
  <div class="head"><h2>Tanıdık geliyor mu?</h2></div>
  <div class="pain-grid">
    <p>Aynı hafta sonuna iki misafir yazılmış, biri telefonda, biri Airbnb'de.</p>
    <p>Kimin kaporası geldi, kim girişte ödeyecek, deftere bakmadan hatırlanmıyor.</p>
    <p>Bayram fiyatını değiştirmeyi unutup tatili hafta içi fiyatına vermişsiniz.</p>
    <p>Ay sonunda elektrik, temizlik, erzak derken kâr mı ettik zarar mı, bilen yok.</p>
  </div>
</div></section>

<div class="wrap" id="ozellikler">
{rows}
</div>

<section class="block mist"><div class="wrap">
  <div class="head"><h2>Ayrıca</h2></div>
  <div class="extras">{extras}</div>
</div></section>

<section class="block"><div class="wrap narrow">
  <h2>Neden ücretsiz?</h2>
  <p>Bungalov Dünyası, Türkiye'deki bungalovları misafirle komisyonsuz buluşturmaya çalışan bir rehber. Rehbere katılan tesislerin işini kolaylaştırmak bizim de işimize yarıyor: düzenli çalışan tesis, memnun misafir demek. Uygulamayı da bu yüzden rehberdeki tesislere ücretsiz veriyoruz.</p>
  <p class="disclose">Açıklık notu: Uygulamayı geliştiren ve Bungalov Dünyası'nı hazırlayan ekip, Sapanca'da Labella Bungalov'u işletiyor. Ekran görüntüleri örnek verilerle hazırlandı; gerçek misafir bilgisi içermez.</p>
  <h2>Sık sorulanlar</h2>
  {faq}
</div></section>

<section class="band"><div class="wrap">
  <div><h2>Tesisinizde deneyelim</h2><p>Kurumsal üye olun, tesisinizi rehbere ekleyin. Uygulamanın kurulumunu birlikte yapalım, ilk rezervasyonları beraber girelim.</p></div>
  <div class="actions"><a class="btn ember" href="/uye/?tur=kurumsal">Ücretsiz üye olun</a><a class="btn ghost-light" href="{msg}" rel="noopener">WhatsApp'tan sorun</a></div>
</div></section>
"""
    schema = [{"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Bungalov Yönetim",
               "applicationCategory": "BusinessApplication", "operatingSystem": "Windows, Android, iOS, iPadOS",
               "description": "Bungalov işletmecileri için rezervasyon takvimi, kapora takibi, WhatsApp mesajları, fiyat ve gelir-gider yönetimi.",
               "offers": {"@type": "Offer", "price": "0", "priceCurrency": "TRY"},
               "screenshot": [SITE + "/img/uygulama/" + n + ".webp" for n, *_ in APP_FEATURES],
               "publisher": {"@type": "Organization", "name": NAME, "url": SITE + "/"}},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                  {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in APP_FAQ]},
              crumbs_ld([("/uygulama/", "Bungalov Yönetim")])]
    write("/uygulama/", page("/uygulama/", "Bungalov Yönetim: Ücretsiz Bungalov Rezervasyon Uygulaması",
                             "Rezervasyon takvimi, kapora takibi, hazır WhatsApp mesajları, bayram fiyatları ve gelir-gider tek uygulamada. Bungalov Dünyası'ndaki tesislere ücretsiz.",
                             body, schema, active="/uygulama/", og_image=SITE + "/img/uygulama/takvim.webp"))


def build_about():
    body = f"""
<div class="wrap">{crumbs([(None, "Hakkımızda")])}
<header class="page-head"><h1>Hakkımızda</h1>
<p>Bungalov Dünyası, bungalov arayanların fotoğrafların ötesini görmesi için hazırlanan bir rehber.</p></header>
{cover("lake")}
<div class="prose">
  <p>Bungalov ilanları birbirine çok benziyor. Hangisinin havuzu gerçekten özel, hangisinin jakuzisi kışın sıcak, hangisinde evcil hayvan kabul ediliyor, çoğu zaman ancak tesise sorarak öğrenebiliyorsunuz. Bu rehberi o soruların cevaplarını baştan yazmak için hazırlıyoruz.</p>
  <p>İlk bölgemiz, bungalov tatilinin en yaygın olduğu yerlerden biri olan Sapanca. Türkiye'nin başka bölgelerindeki tesisler de üye olup kendi sayfalarını oluşturdukça rehbere ekleniyor.</p>
  <h2>Nasıl çalışıyoruz?</h2>
  <ul>
    <li><strong>Aracı değiliz.</strong> Rezervasyonu ve ödemeyi doğrudan tesisle yaparsınız. Biz araya girmiyoruz, komisyon almıyoruz.</li>
    <li><strong>Gerçek bilgi.</strong> Tesis sayfalarındaki fotoğraflar ve olanaklar tesislerin kendisinden gelir. Yanlış bir bilgi görürseniz bize yazın.</li>
    <li><strong>Açıklık.</strong> Bungalov Dünyası'nı Sapanca'da Labella Bungalov'u işleten ekip hazırlıyor. Bunu her ilgili sayfada belirtiyoruz.</li>
  </ul>
  <h2>İletişim</h2>
  <p>Öneri, düzeltme ya da tesis eklemek için <a href="{wa('Merhaba, Bungalov Dünyası hakkında yazıyorum.')}" rel="noopener">WhatsApp'tan yazabilir</a> ya da <a href="tel:+{WA}">0532 722 25 45</a> numarasını arayabilirsiniz.</p>
</div>
</div>
"""
    write("/hakkimizda/", page("/hakkimizda/", "Hakkımızda – Bungalov Dünyası",
                               "Bungalov Dünyası, Türkiye'de bungalov arayanlar için hazırlanan bağımsız ve komisyonsuz bir rehber.",
                               body, [crumbs_ld([("/hakkimizda/", "Hakkımızda")])], active="/hakkimizda/"))


def build_404():
    body = """
<div class="wrap"><header class="page-head" style="padding:72px 0">
<h1>Bu sayfa bulunamadı</h1>
<p>Aradığınız sayfa taşınmış ya da silinmiş olabilir. <a href="/">Ana sayfaya</a> dönebilir ya da <a href="/rehber/">rehbere</a> göz atabilirsiniz.</p>
</header></div>
"""
    write("/404.html", page("/404.html", "Sayfa bulunamadı – Bungalov Dünyası", "Aradığınız sayfa bulunamadı.", body, noindex=True))


def build_meta():
    newest = max([g["date"] for g in GUIDES] + ["2026-10-13"])
    urls = [("/", newest), ("/tesisler/", max([str(l.get("updated_at") or "")[:10] for l in LISTINGS] + ["2026-10-13"])), ("/tesisler/labella-bungalov/", "2026-10-13"), ("/rehber/", newest)] + \
        [(f'/rehber/{g["slug"]}/', g["date"]) for g in GUIDES] + [(f'/tesisler/{l["slug"]}/', str(l.get("updated_at") or "")[:10] or TODAY) for l in LISTINGS] + \
        [("/uygulama/", "2026-10-14"), ("/hakkimizda/", "2026-10-13"), ("/kvkk/", "2026-10-14"), ("/uyelik-kosullari/", "2026-10-14")] + \
        [(region_path(*k), max([str(l.get("updated_at") or "")[:10] for l in r["listings"]] + ["2026-10-14"])) for k, r in REGIONS.items()] + \
        [(region_path(il), "2026-10-14") for il in PROVINCES]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n"
    write("/sitemap.xml", sm)
    write("/robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    write("/CNAME", "bungalovdunyasi.com\n")
    write("/.nojekyll", "")
    fav = LOGO_SVG.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"').replace("currentColor", "#15302b")
    write("/favicon.svg", fav)
    shutil.copy(os.path.join(os.path.dirname(OUT), "src", "style.css"), os.path.join(OUT, "style.css"))
    shutil.copytree(os.path.join(os.path.dirname(OUT), "src", "img"), os.path.join(OUT, "img"))
    shutil.copytree(os.path.join(os.path.dirname(OUT), "src", "js"), os.path.join(OUT, "js"))
    write("/js/iller.js", "window.BD_ILLER = " + json.dumps(GEO, ensure_ascii=False) + ";\n")


if __name__ == "__main__":
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    build_home(); build_facilities(); build_labella(); build_guides(); build_owner(); build_app(); build_about(); build_404()
    build_member(); build_account(); build_listing_shell(); build_legal(); build_regions()
    for _l in LISTINGS:
        build_listing(_l)
    build_meta()
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print(f"{n} dosya → {OUT}")
