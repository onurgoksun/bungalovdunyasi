#!/usr/bin/env python3
"""Bungalov Dünyası statik site üreticisi. Çalıştır: python3 build.py  → ./docs/"""
import html, json, os, shutil, datetime
from urllib.parse import quote

SITE = "https://bungalovdunyasi.tr"
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

NAV = [("/tesisler/", "Tesisler"), ("/rehber/", "Rehber"), ("/hakkimizda/", "Hakkımızda")]


def page(path, title, desc, body, schema=None, active=None, og_image=None):
    canonical = SITE + path
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
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
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
<link rel="stylesheet" href="/style.css?v=2">
<link rel="preconnect" href="https://images.unsplash.com">
{ld}</head>
<body>
<a class="skip" href="#icerik">İçeriğe geç</a>
<header class="top"><div class="wrap">
  <a class="logo" href="/">{LOGO_SVG}{NAME}</a>
  <nav class="nav" aria-label="Ana menü">{nav}<a class="owner" href="/tesis-ekle/">Tesisinizi ekleyin</a></nav>
</div></header>
<main id="icerik">
{body}
</main>
<footer class="foot"><div class="wrap">
  <div>
    <a class="logo" href="/">{LOGO_SVG}{NAME}</a>
    <p>Sapanca ve çevresinde bungalov arayanlar için sade bir rehber. Rezervasyonu doğrudan tesisle yaparsınız; araya komisyon girmez.</p>
  </div>
  <div>
    <h4>Sayfalar</h4>
    <ul><li><a href="/tesisler/">Tesisler</a></li><li><a href="/rehber/">Rehber</a></li><li><a href="/hakkimizda/">Hakkımızda</a></li><li><a href="/tesis-ekle/">Tesisinizi ekleyin</a></li></ul>
  </div>
  <div>
    <h4>İletişim</h4>
    <ul><li><a href="{wa('Merhaba, Bungalov Dünyası hakkında yazıyorum.')}" rel="noopener">WhatsApp ile yazın</a></li><li><a href="tel:+{WA}">0532 722 25 45</a></li></ul>
  </div>
  <p class="small">© {datetime.date.today().year} {NAME}. Tesis bilgileri tesislerin kendi beyanına dayanır; fiyat ve müsaitlik için tesisle görüşün.</p>
</div></footer>
<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "e4d1630b9947485b835f8b18c6dd0d75"}}'></script>
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
    "area": "Memnuniye Mahallesi, Sapanca",
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
    return f"""<article class="fac">
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
  <p><strong>Sapanca'da bungalov işletiyor musunuz?</strong>Tesisinizi ücretsiz ekleyin. Misafirler size doğrudan ulaşır, komisyon ödemezsiniz.</p>
  <a class="btn solid" href="/tesis-ekle/">Tesisinizi ekleyin</a>
</div>"""

# ---------------------------------------------------------------- Rehber yazıları
GUIDES = []


GUIDE_IMG = {"sapanca-bungalov-kiralamadan-once-sorulacak-sorular": "pool", "kisin-sapanca-bungalov-isitmali-havuz-jakuzi-somine": "snow", "evcil-hayvanla-sapanca-bungalov": "dog"}


def guide(slug, title, seo_title, desc, minutes, body, faq=None):
    GUIDES.append(dict(slug=slug, title=title, seo_title=seo_title, desc=desc, minutes=minutes, body=body, faq=faq or [], img=GUIDE_IMG[slug]))


ASK_MSG = ("Merhaba, Bungalov Dünyası'ndan ulaşıyorum. [giriş tarihi] – [çıkış tarihi] arası [kişi sayısı] kişi için "
           "müsaitliğinizi öğrenmek istiyorum. Havuz ısıtmalı mı, jakuzi sıcak mı ve fiyata neler dahil?")

guide(
    "sapanca-bungalov-kiralamadan-once-sorulacak-sorular",
    "Sapanca'da bungalov kiralamadan önce sorulacak 12 soru",
    "Sapanca'da Bungalov Kiralamadan Önce Sorulacak 12 Soru",
    "Havuz gerçekten özel mi, ısıtmalı mı, jakuzi sıcak mı, iptal koşulları ne? Sapanca'da bungalov kiralamadan önce tesise sormanız gereken 12 soru.",
    6,
    f"""
<p>Fotoğraflar birbirine benziyor: ahşap bir A-frame, önünde mavi bir havuz, gece yanan ışıklar. Farkı ilanın küçük harflerinde ya da hiç yazılmayan ayrıntılarda bulursunuz. Aşağıdaki sorular, rezervasyon yapmadan önce tesisle beş dakikalık bir yazışmada netleştirmeniz gerekenler.</p>

<h2>Havuz ve jakuzi</h2>
<ul class="checklist">
<li><strong>Havuz bungalova özel mi, ortak mı?</strong> "Havuzlu bungalov" ilanlarının bir kısmında havuz birkaç bungalov arasında ortaktır. Özel havuzda alanı yalnızca sizin grubunuz kullanır.</li>
<li><strong>Havuz ısıtmalı mı, hangi aylarda?</strong> Isıtmalı havuz ilkbahar ve sonbaharda büyük fark yaratır. Isıtmanın hangi aylarda çalıştığını, ek ücret olup olmadığını ve suyun yaklaşık kaç derecede tutulduğunu sorun.</li>
<li><strong>Jakuzi içeride mi, dışarıda mı, sıcak mı?</strong> Banyodaki jakuzili küvet ile açık havadaki sıcak jakuzi çok farklı deneyimlerdir. Dış jakuzinin kışın da sıcak çalışıp çalışmadığını öğrenin.</li>
</ul>

<h2>Bungalovun kendisi</h2>
<ul class="checklist">
<li><strong>Kaç kişi kalabiliyor, yatak düzeni nasıl?</strong> "4+1" genellikle dört yetişkin ve bir ek yatak ya da çocuk anlamına gelir. Yatakların çift kişilik mi, tek kişilik mi olduğunu sorun.</li>
<li><strong>Mutfakta neler var?</strong> Ocak, buzdolabı, tencere-tava, çay ve kahve makinesi gibi temel donanımı kontrol edin. Kendi yemeğinizi yapacaksanız bu soru önemlidir.</li>
<li><strong>Şömine var mı, odun dahil mi?</strong> Odunlu şöminede odunun fiyata dahil olup olmadığını, şöminesi olmayan bungalovlarda ise ısınmanın nasıl sağlandığını sorun.</li>
<li><strong>Giriş ve çıkış saatleri ne?</strong> Sapanca'da giriş genellikle öğleden sonra, çıkış öğleden önce yapılır. Erken giriş ya da geç çıkış mümkünse önceden konuşun.</li>
</ul>

<h2>Kurallar ve ödeme</h2>
<ul class="checklist">
<li><strong>Evcil hayvan kabul ediliyor mu?</strong> Kabul eden tesisler genellikle boyut ve sayı sınırı koyar, bazıları ek temizlik ücreti alır. Ayrıntılar için <a href="/rehber/evcil-hayvanla-sapanca-bungalov/">evcil hayvanla bungalov rehberine</a> bakabilirsiniz.</li>
<li><strong>Kapora ve iptal koşulları neler?</strong> Kaporanın ne kadar olduğunu, iptal ederseniz kaç gün öncesine kadar iade edildiğini ve tarih değişikliğinin mümkün olup olmadığını yazılı olarak alın.</li>
<li><strong>Mangal ve ateş çukuru kullanılabiliyor mu?</strong> Mangal malzemesi, kömür ve ızgaranın tesis tarafından sağlanıp sağlanmadığını sorun.</li>
</ul>

<h2>Konum ve ulaşım</h2>
<ul class="checklist">
<li><strong>Bungalovlar arasında mesafe ne kadar?</strong> Gizlilik sizin için önemliyse komşu bungalovun terasından havuzunuzun görünüp görünmediğini sorun, mümkünse genel görünüm fotoğrafı isteyin.</li>
<li><strong>Otopark ve yol durumu nasıl?</strong> Aracınızı bungalova yakın park edebilecek misiniz? Kışın tesis yolunun karda nasıl olduğunu öğrenin.</li>
</ul>

<h2>Hazır mesaj</h2>
<p>Tesise WhatsApp'tan şu mesajı tarihlerinizi doldurarak gönderebilirsiniz:</p>
<div class="note"><p>{esc(ASK_MSG)}</p></div>

<h2>Doğrudan tesisle konuşmak</h2>
<p>Büyük rezervasyon sitelerinde tesis, her rezervasyon için komisyon öder. Doğrudan iletişimde bu maliyet olmadığı için birçok tesis tarih değişikliği, erken giriş ya da uzun konaklama gibi konularda daha esnek davranabilir. Bu rehberdeki tesislerin hepsiyle doğrudan iletişim kurabilirsiniz.</p>
""",
    faq=[("Sapanca'da bungalov havuzu özel mi oluyor?",
          "Tesise göre değişir. Bazı tesislerde her bungalovun kendine ait havuzu vardır, bazılarında havuz birkaç bungalov arasında ortaktır. Rezervasyondan önce havuzun bungalova özel olup olmadığını sorun."),
         ("Bungalovda 4+1 ne demek?",
          "Genellikle dört yetişkin ve bir ek yatak ya da çocuk için yer olduğu anlamına gelir. Yatak düzenini tesise ayrıca sorun.")])

guide(
    "kisin-sapanca-bungalov-isitmali-havuz-jakuzi-somine",
    "Kışın Sapanca'da bungalov: ısıtmalı havuz, jakuzi ve şömine",
    "Kışın Sapanca'da Bungalov: Isıtmalı Havuz, Jakuzi ve Şömine Rehberi",
    "Sapanca'da kış tatili için bungalov seçerken ısıtmalı havuz, sıcak jakuzi, şömine ve ulaşım konusunda bilmeniz gerekenler.",
    5,
    """
<p>Sapanca'yı yazın göl kenarı için seçenler kadar, kışın şömine başında birkaç gün geçirmek için gelenler de çok. Kış tatilinde bungalovu yaz tatilinden farklı kriterlerle seçmek gerekir: havuzun mavisi değil, suyun sıcaklığı ve içerinin ne kadar çabuk ısındığı önemlidir.</p>

<h2>Sapanca'da kış nasıl geçer?</h2>
<p>Sapanca'da kışlar genellikle serin ve yağışlı geçer. Yüksek kesimlerde ve hemen yanındaki Kartepe'de kar sık görülür. Yani ateşin başında oturup dışarıda yağan karı izlemek mümkün, ama yolda da hazırlıklı olmak gerekir.</p>

<h2>Isıtmalı havuz: neyi sormalı?</h2>
<p>"Isıtmalı havuz" ifadesi tesisten tesise farklı şeyler anlatabilir. Kışın gidecekseniz şunları netleştirin:</p>
<ul>
<li>Isıtma kış aylarında da çalışıyor mu, yoksa sadece ilkbahar ve sonbaharda mı?</li>
<li>Su yaklaşık kaç dereceye kadar ısıtılıyor?</li>
<li>Isıtma fiyata dahil mi, ek ücretli mi?</li>
<li>Havuz açık mı, üstü kapalı mı? Açık havuzda havuzdan çıkıp içeri girene kadar geçen yol kısa olmalı.</li>
</ul>

<h2>Sıcak jakuzi</h2>
<p>Kışın en çok aranan özellik açık havada sıcak jakuzidir. Soğuk havada sıcak suyun içinde oturmak, ısıtmalı havuzdan bile daha keyifli olabilir. Jakuzinin terasta mı, banyoda mı olduğunu ve kullanmadan ne kadar önce ısıtılması gerektiğini sorun.</p>

<h2>Şömine ve ısınma</h2>
<ul>
<li><strong>Şömine:</strong> Odunlu şömine atmosfer yaratır. Odunun fiyata dahil olup olmadığını ve yeterli odun bırakılıp bırakılmadığını öğrenin.</li>
<li><strong>Asıl ısınma:</strong> Şömine çoğu zaman ek ısıtıcıdır. Bungalovun klima, kombi ya da yerden ısıtmayla ısınıp ısınmadığını sorun; A-frame yapılarda yüksek tavan nedeniyle bu daha da önemlidir.</li>
</ul>

<h2>Ulaşım</h2>
<p>Kar yağdığında tesise giden yol rampalıysa zorlaşabilir. Yola çıkmadan önce tesisi arayıp yol durumunu sorun, aracınızda kış lastiği olduğundan emin olun.</p>

<h2>Kışın çevrede ne yapılır?</h2>
<ul>
<li><strong>Kartepe:</strong> Kayak ve kar keyfi için günübirlik gidilebilecek en yakın yer.</li>
<li><strong>Maşukiye:</strong> Şelaleleri, dere kenarındaki alabalık restoranları ve yürüyüş yollarıyla bilinir.</li>
<li><strong>Göl kenarı:</strong> Soğuk ama güneşli bir günde Sapanca Gölü kıyısında yürümek, kalabalık yaz günlerinden çok daha sakindir.</li>
</ul>

<div class="note warm"><p>Isıtmalı havuz, sıcak jakuzi ve şöminenin üçü birden olan bungalovlar kış hafta sonlarında erken doluyor. Tarihiniz belliyse birkaç hafta önceden sormanızı öneririz.</p></div>
""",
    faq=[("Sapanca'da kışın havuza girilir mi?",
          "Havuz ısıtmalıysa ve ısıtma kış aylarında da çalışıyorsa girilebilir. Isıtmanın hangi aylarda çalıştığını ve suyun kaç dereceye kadar ısıtıldığını tesise sorun."),
         ("Kışın Sapanca'ya ulaşım zor mu?",
          "Ana yollar genellikle açıktır, ancak kar yağdığında tesislere giden rampalı yollar zorlaşabilir. Yola çıkmadan önce tesisten yol durumunu öğrenin ve kış lastiği kullanın.")])

guide(
    "evcil-hayvanla-sapanca-bungalov",
    "Evcil hayvanla Sapanca'da bungalov tatili",
    "Evcil Hayvanla Sapanca'da Bungalov Tatili: Bilmeniz Gerekenler",
    "Köpeğiniz ya da kedinizle Sapanca'da bungalov tatili planlıyorsanız tesise sormanız gerekenler, yanınıza almanız gerekenler ve bungalov kuralları.",
    4,
    """
<p>Bungalov, evcil hayvanla tatil için otelden çok daha uygundur: kendi girişiniz, bahçeniz ve terasınız vardır, koridorda başka misafirle karşılaşmazsınız. Ama her tesis evcil hayvan kabul etmez, kabul edenlerin de kuralları farklıdır.</p>

<h2>Rezervasyondan önce sorun</h2>
<ul>
<li>Evcil hayvan kabul ediliyor mu? İlanda yazmıyorsa mutlaka sorun.</li>
<li>Boyut, cins ya da sayı sınırı var mı?</li>
<li>Ek temizlik ücreti ya da depozito alınıyor mu?</li>
<li>Bahçe çitle çevrili mi? Köpeğiniz serbest dolaşacaksa bu önemli.</li>
</ul>

<h2>Bungalov içinde genel kurallar</h2>
<ul>
<li><strong>Havuz:</strong> Hijyen nedeniyle çoğu tesis hayvanların havuza girmesine izin vermez. Havuz kenarında dikkatli olun.</li>
<li><strong>Yatak ve koltuk:</strong> Kendi battaniyenizi getirin, hayvanınızı yatak ve koltuklara çıkarmayın.</li>
<li><strong>Yalnız bırakmak:</strong> Bungalovda yalnız bırakmanın uygun olup olmadığını tesise sorun.</li>
<li><strong>Bahçe:</strong> Tuvalet ihtiyacını bahçede karşılıyorsa mutlaka toplayın.</li>
</ul>

<h2>Yanınıza alın</h2>
<ul>
<li>Mama, mama ve su kabı</li>
<li>Tasma, gezdirme kayışı ve tanıdık bir oyuncak</li>
<li>Yatağı ya da battaniyesi</li>
<li>Dışkı poşetleri ve havlu</li>
<li>Aşı karnesi ve varsa düzenli kullandığı ilaçları</li>
</ul>

<h2>Yolda ve çevrede</h2>
<p>İstanbul'dan Sapanca'ya yolculuk trafiğe göre birkaç saat sürebilir. Arada mola verin, su verin. Göl kenarı ve orman yolları yürüyüş için güzeldir. Kalabalık alanlarda ve köy yollarında tasmayı çıkarmayın.</p>

<div class="note"><p>Evcil hayvanla geleceğinizi rezervasyon sırasında mutlaka belirtin. Haber vermeden gelmek hem tesisle hem diğer misafirlerle sorun yaşatabilir.</p></div>
""",
    faq=[("Sapanca'da evcil hayvan kabul eden bungalov var mı?",
          "Evet, bazı tesisler evcil hayvan kabul ediyor. Genellikle boyut ve sayı sınırı ya da ek temizlik ücreti uygulanır. Rezervasyondan önce tesise sorun."),
         ("Köpeğim havuza girebilir mi?",
          "Çoğu tesis hijyen nedeniyle hayvanların havuza girmesine izin vermez. Kuralı tesise önceden sorun.")])


# ---------------------------------------------------------------- Sayfalar
def build_home():
    find = "".join(f'<a href="{h}">{t}</a>' for h, t in [
        ("/tesisler/", "Özel havuzlu"),
        ("/rehber/kisin-sapanca-bungalov-isitmali-havuz-jakuzi-somine/", "Kış için: jakuzi ve şömine"),
        ("/rehber/evcil-hayvanla-sapanca-bungalov/", "Evcil hayvanla"),
        ("/rehber/sapanca-bungalov-kiralamadan-once-sorulacak-sorular/", "İlk kez kiralayacağım")])
    body = f"""
<section class="hero">
  <img class="hero-img" src="{ux('hero', 1920, 1100)}" srcset="{ux('hero', 900, 1100)} 900w, {ux('hero', 1920, 1100)} 1920w" sizes="100vw" alt="{esc(PHOTOS['hero'][1])}" fetchpriority="high">
  <div class="wrap">
    <div class="copy">
      <h1>Sapanca'da bungalov, fotoğrafın ötesiyle.</h1>
      <p class="lead">Havuz gerçekten özel mi, jakuzi kışın sıcak mı, şömine yanıyor mu? Tesisleri ayrıntısıyla anlatıyor, sizi doğrudan tesisle buluşturuyoruz.</p>
      <div class="find" aria-label="Ne arıyorsunuz?">{find}</div>
    </div>
    <p class="hero-credit">{credit('hero')}</p>
  </div>
</section>

<section class="block"><div class="wrap">
  <div class="head"><h2>Tesisler</h2><p>Her tesisi tek tek tanıyoruz. Listeye yalnızca gerçek fotoğrafı ve net bilgisi olan bungalovlar giriyor.</p></div>
  {fac_row(LABELLA)}
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
    write("/", page("/", "Sapanca Bungalov Rehberi | Özel Havuzlu, Jakuzili Bungalovlar – Bungalov Dünyası",
                    "Sapanca'da özel havuzlu, ısıtmalı havuzlu, jakuzili ve şömineli bungalovlar. Tesisleri ayrıntısıyla tanıyın, rezervasyonu komisyonsuz doğrudan tesisle yapın.",
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
      <li>Fotoğraflı, ayrıntılı tesis sayfası</li>
      <li>Ücretsiz Bungalov Yönetim uygulaması: takvim, rezervasyon ve misafir mesajları tek yerde</li>
      <li>Kendi web sitenize ekleyebileceğiniz rezervasyon sayfası</li>
    </ul>
    <p style="margin-top:20px"><a class="btn ember" href="/tesis-ekle/">Nasıl eklenir?</a></p>
  </div>
</div></section>"""


def build_facilities():
    items = [("/tesisler/", "Tesisler")]
    body = f"""
<div class="wrap">{crumbs([(None, "Tesisler")])}
<header class="page-head"><h1>Sapanca bungalov tesisleri</h1>
<p>Listeye yalnızca gerçek fotoğrafı ve net bilgisi olan tesisleri ekliyoruz. Fiyat ve müsaitlik için tesisle doğrudan görüşürsünüz.</p></header>
</div>
<section class="block" style="padding-top:12px"><div class="wrap">
  {fac_row(LABELLA)}
  {SLOT}
</div></section>
"""
    write("/tesisler/", page("/tesisler/", "Sapanca Bungalov Tesisleri – Bungalov Dünyası",
                             "Sapanca'da özel havuzlu, jakuzili ve şömineli bungalov tesisleri. Fotoğraflar, olanaklar ve doğrudan iletişim bilgileri.",
                             body, [crumbs_ld([("/tesisler/", "Tesisler")])], active="/tesisler/"))


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
<div class="wrap">{crumbs([("/tesisler/", "Tesisler"), (None, f["name"])])}
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
    write(path, page(path, "Labella Bungalov – Sapanca Özel Havuzlu, Jakuzili A-Frame Bungalov | Bungalov Dünyası",
                     "Sapanca Memnuniye'de 5 bağımsız A-frame bungalov: ısıtmalı özel havuz, sıcak jakuzi, şömine, 4+1 kişilik. Fotoğraflar, olanaklar ve doğrudan iletişim.",
                     body, [lodging, crumbs_ld([("/tesisler/", "Tesisler"), (path, f["name"])])], active="/tesisler/",
                     og_image=UP + f["shots"][0][0]))


def build_guides():
    body = f"""
<div class="wrap">{crumbs([(None, "Rehber")])}
<header class="page-head"><h1>Sapanca bungalov rehberi</h1>
<p>Bungalov seçerken neye bakmalı, hangi mevsimde ne beklemeli, nelere dikkat etmeli? Kısa ve somut yazılar.</p></header>
<div class="prose" style="max-width:none">{guide_list()}</div>
</div>
"""
    write("/rehber/", page("/rehber/", "Sapanca Bungalov Rehberi: Seçim, Kış Tatili, Evcil Hayvan | Bungalov Dünyası",
                           "Sapanca'da bungalov kiralamadan önce bilmeniz gerekenler: sorulacak sorular, kışın ısıtmalı havuz ve jakuzi, evcil hayvanla tatil.",
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
                   "inLanguage": "tr", "image": ux(g["img"], 1200, 630), "datePublished": TODAY, "dateModified": TODAY, "mainEntityOfPage": SITE + path,
                   "author": {"@type": "Organization", "name": NAME, "url": SITE + "/"},
                   "publisher": {"@type": "Organization", "name": NAME, "url": SITE + "/"}},
                  crumbs_ld([("/rehber/", "Rehber"), (path, g["title"])])]
        if g["faq"]:
            schema.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in g["faq"]]})
        write(path, page(path, g["seo_title"] + " | Bungalov Dünyası", g["desc"], body, schema, active="/rehber/", og_image=ux(g["img"], 1200, 630)))


def build_owner():
    msg = wa("Merhaba, Sapanca'daki bungalov tesisimi Bungalov Dünyası'na eklemek istiyorum. Tesis adı: [ ], bungalov sayısı: [ ].")
    body = f"""
<div class="wrap">{crumbs([(None, "Tesisinizi ekleyin")])}
<header class="page-head"><h1>Tesisinizi ücretsiz ekleyin</h1>
<p>Sapanca ve çevresinde bungalov işletiyorsanız tesisinizi rehbere ekleyelim. Misafir size doğrudan ulaşır; komisyon ya da listeleme ücreti yok.</p></header>
{cover("inside")}
<div class="layout">
<div class="prose">
  <h2>Ne kazanırsınız?</h2>
  <ul>
    <li><strong>Tesis sayfası:</strong> Fotoğraflarınız, olanaklarınız, kurallarınız ve doğrudan iletişim butonlarınız.</li>
    <li><strong>Doğrudan misafir:</strong> Misafir WhatsApp'tan ya da telefonla size yazar. Rezervasyonu ve ödemeyi kendiniz yönetirsiniz.</li>
    <li><strong>Bungalov Yönetim uygulaması, ücretsiz:</strong> Bungalovlarınızın doluluk takvimi, rezervasyon ve kapora takibi, misafire hazır WhatsApp mesajları, çıkış sonrası misafir anketi. Windows, Android, iPhone ve iPad'de çalışır.</li>
    <li><strong>Kendi rezervasyon sayfanız:</strong> Misafirin boş tarihleri görüp talep bırakabildiği, kendi sitenize ve Instagram'ınıza ekleyebileceğiniz bir sayfa.</li>
  </ul>
  <h2>Nasıl eklenir?</h2>
  <ol>
    <li>Aşağıdaki butondan bize WhatsApp'tan yazın.</li>
    <li>Tesisinizin fotoğraflarını ve temel bilgilerini (bungalov sayısı, kapasite, havuz, jakuzi, şömine, kurallar) gönderin.</li>
    <li>Sayfanızı hazırlayıp onayınıza sunarız. Onaylarsanız yayına alırız.</li>
  </ol>
  <h2>Ölçütlerimiz</h2>
  <ul>
    <li>Fotoğraflar tesisin kendisine ait ve güncel olmalı.</li>
    <li>Olanaklar doğru yazılmalı: "ısıtmalı havuz" yazıyorsa havuz gerçekten ısıtılıyor olmalı.</li>
    <li>Misafirlerden gelen ciddi şikâyetlerde tesisle konuşur, gerekirse listeden çıkarırız.</li>
  </ul>
  <div class="note"><p>Şimdilik yalnızca Sapanca ve yakın çevresindeki (Kartepe, Maşukiye) tesisleri ekliyoruz.</p></div>
</div>
<aside class="aside" aria-label="Başvuru">
  <h3>Başvuru</h3>
  <p>Tesisinizin adını ve bungalov sayısını yazmanız yeterli. Size dönüş yaparız.</p>
  <a class="btn wa" href="{msg}" rel="noopener">WhatsApp'tan başvurun</a>
  <a class="btn line" href="tel:+{WA}">Ara: 0532 722 25 45</a>
</aside>
</div>
</div>
"""
    write("/tesis-ekle/", page("/tesis-ekle/", "Bungalov Tesisinizi Ücretsiz Ekleyin – Bungalov Dünyası",
                               "Sapanca'da bungalov tesisinizi Bungalov Dünyası'na ücretsiz ekleyin. Komisyonsuz doğrudan misafir ve ücretsiz Bungalov Yönetim uygulaması.",
                               body, [crumbs_ld([("/tesis-ekle/", "Tesisinizi ekleyin")])]))


def build_about():
    body = f"""
<div class="wrap">{crumbs([(None, "Hakkımızda")])}
<header class="page-head"><h1>Hakkımızda</h1>
<p>Bungalov Dünyası, Sapanca'da bungalov arayanların fotoğrafların ötesini görmesi için hazırlanan bir rehber.</p></header>
{cover("lake")}
<div class="prose">
  <p>Sapanca'da bungalov ilanları birbirine çok benziyor. Hangisinin havuzu gerçekten özel, hangisinin jakuzisi kışın sıcak, hangisinde evcil hayvan kabul ediliyor, çoğu zaman ancak tesise sorarak öğrenebiliyorsunuz. Bu rehberi o soruların cevaplarını baştan yazmak için hazırlıyoruz.</p>
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
                               "Bungalov Dünyası, Sapanca'da bungalov arayanlar için hazırlanan bağımsız ve komisyonsuz bir rehber.",
                               body, [crumbs_ld([("/hakkimizda/", "Hakkımızda")])], active="/hakkimizda/"))


def build_404():
    body = """
<div class="wrap"><header class="page-head" style="padding:72px 0">
<h1>Bu sayfa bulunamadı</h1>
<p>Aradığınız sayfa taşınmış ya da silinmiş olabilir. <a href="/">Ana sayfaya</a> dönebilir ya da <a href="/rehber/">rehbere</a> göz atabilirsiniz.</p>
</header></div>
"""
    html_ = page("/404.html", "Sayfa bulunamadı – Bungalov Dünyası", "Aradığınız sayfa bulunamadı.", body)
    html_ = html_.replace('<link rel="canonical" href="https://bungalovdunyasi.com/404.html">', '<meta name="robots" content="noindex">')
    write("/404.html", html_)


def build_meta():
    urls = ["/", "/tesisler/", "/tesisler/labella-bungalov/", "/rehber/"] + [f'/rehber/{g["slug"]}/' for g in GUIDES] + ["/tesis-ekle/", "/hakkimizda/"]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n"
    write("/sitemap.xml", sm)
    write("/robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    write("/CNAME", "bungalovdunyasi.tr\n")
    write("/.nojekyll", "")
    fav = LOGO_SVG.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"').replace("currentColor", "#15302b")
    write("/favicon.svg", fav)
    shutil.copy(os.path.join(os.path.dirname(OUT), "src", "style.css"), os.path.join(OUT, "style.css"))


if __name__ == "__main__":
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    build_home(); build_facilities(); build_labella(); build_guides(); build_owner(); build_about(); build_404(); build_meta()
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print(f"{n} dosya → {OUT}")
