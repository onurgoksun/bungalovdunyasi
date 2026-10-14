/* Bungalov Dünyası · üyelik ortak kodu (supabase-js UMD'den sonra yüklenir) */
(function () {
  "use strict";
  var URL_ = "https://sbqjblbiwivytybtlxdi.supabase.co";
  var KEY = "sb_publishable_YeZQ1VWS7RrQMxW5Ubrykg_7q_k0N9A";
  var sb = window.supabase.createClient(URL_, KEY, {
    auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true, flowType: "pkce" }
  });

  var BD = window.BD = {
    sb: sb,
    URL: URL_,
    KEY: KEY,
    BUCKET: "tesis-foto",
    AMENITIES: ["Özel havuz", "Isıtmalı havuz", "Ortak havuz", "Açık hava jakuzisi", "İç mekân jakuzisi", "Şömine",
      "Tam donanımlı mutfak", "Klima", "Yerden ısıtma", "Wi-Fi", "Smart TV", "Mangal / barbekü", "Ateş çukuru",
      "Bahçe", "Göl manzarası", "Orman manzarası", "Özel otopark", "Kahvaltı imkânı", "Çocuklara uygun", "Engelli erişimine uygun"],
    DISTRICTS: ["Sapanca", "Kartepe", "Serdivan", "Diğer"],
    PETS: { evet: "Evcil hayvan kabul edilir", hayir: "Evcil hayvan kabul edilmez", sor: "Evcil hayvan için önceden sorun" }
  };

  BD.$ = function (s, r) { return (r || document).querySelector(s); };
  BD.$$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  BD.el = function (tag, attrs, kids) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) return;
      if (k === "text") e.textContent = v;
      else if (k === "class") e.className = v;
      else if (k.slice(0, 2) === "on") e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? "" : v);
    });
    (kids || []).forEach(function (c) { if (c) e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return e;
  };
  BD.qs = function (k) { return new URLSearchParams(location.search).get(k); };
  BD.safeNext = function (v) { return v && /^\/[a-z0-9\-\/]*\/?(\?[a-z0-9=&\-_.%]*)?$/i.test(v) ? v : ""; };
  BD.photoUrl = function (path) { return URL_ + "/storage/v1/object/public/tesis-foto/" + path.split("/").map(encodeURIComponent).join("/"); };
  BD.safeUrl = function (u) {
    u = String(u || "").trim();
    if (!u) return "";
    if (!/^https?:\/\//i.test(u)) u = "https://" + u;
    try { var x = new URL(u); return /^https?:$/.test(x.protocol) ? x.href : ""; } catch (e) { return ""; }
  };
  BD.digits = function (p) {
    var d = String(p || "").replace(/\D/g, "");
    if (d.length === 11 && d[0] === "0") d = "9" + d;
    if (d.length === 10) d = "90" + d;
    return d;
  };
  BD.slugify = function (s) {
    var map = { "ç": "c", "ğ": "g", "ı": "i", "İ": "i", "ö": "o", "ş": "s", "ü": "u", "â": "a", "î": "i", "û": "u" };
    return String(s || "").toLocaleLowerCase("tr").replace(/[çğıİöşüâîû]/g, function (c) { return map[c] || c; })
      .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 70) || "tesis";
  };
  BD.mapSrc = function (q) { return "https://maps.google.com/maps?q=" + encodeURIComponent(q) + "&z=14&output=embed"; };
  BD.mapLink = function (q) { return "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(q); };
  BD.fullAddress = function (l) {
    return [l.address, l.neighborhood, l.district, "Sakarya"].filter(function (x) { return x && String(x).trim(); }).join(", ");
  };

  BD.session = async function () {
    var r = await sb.auth.getSession();
    return r.data.session || null;
  };
  BD.profile = async function () {
    var s = await BD.session();
    if (!s) return null;
    var r = await sb.from("site_profiles").select("*").eq("id", s.user.id).maybeSingle();
    return r.data || null;
  };
  BD.toLogin = function (kind) {
    var next = location.pathname + location.search;
    location.href = "/uye/?sonra=" + encodeURIComponent(next) + (kind ? "&tur=" + kind : "");
  };
  BD.msg = function (box, text, kind) {
    if (!box) return;
    box.textContent = text || "";
    box.className = "msg" + (kind ? " " + kind : "");
    box.hidden = !text;
    if (text && kind === "bad") {
      var r = box.getBoundingClientRect();
      if (r.top < 70 || r.bottom > window.innerHeight) box.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  };
  BD.err = function (e) {
    var m = (e && (e.message || e.error_description || e.msg)) || String(e || "");
    var tr = {
      "Invalid login credentials": "E-posta ya da şifre hatalı.",
      "User already registered": "Bu e-posta ile zaten bir hesap var. Giriş yapın.",
      "Email not confirmed": "E-posta adresiniz henüz doğrulanmadı. Gelen kutunuzdaki bağlantıya tıklayın.",
      "Password should be at least 6 characters.": "Şifre en az 8 karakter olmalı.",
      "Signups not allowed for this instance": "Şu an yeni üyelik alınamıyor.",
      "duplicate key value violates unique constraint \"listings_slug_key\"": "Bu adla bir tesis zaten var; adı biraz değiştirin."
    };
    if (/provider is not enabled|Unsupported provider/i.test(m)) return "Google ile giriş henüz hazır değil. Şimdilik e-posta ile devam edin.";
    if (/Failed to fetch|NetworkError|Load failed/i.test(m)) return "Bağlantı kurulamadı. İnternetinizi kontrol edip tekrar deneyin.";
    if (/row-level security/i.test(m)) return "Bu işlem için yetkiniz yok. Kurumsal üyelikle giriş yaptığınızdan emin olun.";
    if (/Payload too large|exceeded the maximum allowed size/i.test(m)) return "Fotoğraf çok büyük (en fazla 3 MB).";
    if (/rate limit/i.test(m)) return "Çok fazla deneme yapıldı. Birkaç dakika sonra tekrar deneyin.";
    return tr[m] || m || "Bir sorun oluştu, tekrar deneyin.";
  };

  // Üst menüdeki giriş / hesabım bağlantısı
  async function header() {
    var a = document.getElementById("acct-link");
    if (!a) return;
    var s = await BD.session();
    if (s) { a.textContent = "Hesabım"; a.href = "/hesabim/"; }
  }
  header();
})();
