/* /tesis/?t=slug : üyelerin eklediği tesisin sayfası (anında yayın) */
(function () {
  "use strict";
  var $ = BD.$, el = BD.el, sb = BD.sb;
  var root = $("#tesis"), msg = $("#tesis-msg");
  var slug = (BD.qs("t") || "").toLowerCase().replace(/[^a-z0-9-]/g, "");

  (async function () {
    if (!slug) return notFound();
    var r = await sb.from("listings").select("*").eq("slug", slug).maybeSingle();
    $("#tesis-yukleniyor").hidden = true;
    if (r.error || !r.data) return notFound();
    var l = r.data;
    var s = await BD.session();
    var mine = s && s.user.id === l.owner;
    document.title = l.name + " – " + [l.neighborhood, l.district].filter(Boolean).join(", ") + " Bungalov | Bungalov Dünyası";
    var md = document.querySelector('meta[name="description"]');
    if (md) md.setAttribute("content", (l.summary || l.name).slice(0, 160));
    render(l, s, mine);
  })();

  function notFound() {
    $("#tesis-yukleniyor").hidden = true;
    root.hidden = false;
    root.appendChild(el("header", { class: "page-head" }, [
      el("h1", { text: "Tesis bulunamadı" }),
      el("p", {}, ["Bu tesis yayından kaldırılmış ya da bağlantı hatalı olabilir. ", el("a", { href: "/tesisler/", text: "Bütün tesislere" }), " göz atabilirsiniz."])
    ]));
  }

  function paragraphs(text) {
    return String(text || "").split(/\n\s*\n/).map(function (p) { return p.trim(); }).filter(Boolean)
      .map(function (p) { return el("p", { text: p.replace(/\s*\n\s*/g, " ") }); });
  }
  function ruleList(text) {
    var lines = String(text || "").split(/\n/).map(function (x) { return x.trim(); }).filter(Boolean);
    return el("ul", {}, lines.map(function (x) { return el("li", { text: x.replace(/^[-•*]\s*/, "") }); }));
  }

  function render(l, s, mine) {
    root.hidden = false;
    var place = [l.neighborhood, l.district].filter(Boolean).join(", ");
    var photos = l.photos || [];

    if (BD.qs("yeni") && mine) {
      var link = location.origin + "/tesis/?t=" + l.slug;
      var copyBtn = el("button", { type: "button", class: "btn line sm", text: "Bağlantıyı kopyala", onclick: function () {
        try { navigator.clipboard.writeText(link); copyBtn.textContent = "Kopyalandı"; } catch (e) {}
      } });
      root.appendChild(el("div", { class: "note ok-note" }, [
        el("p", {}, [el("strong", { text: "Tesisiniz yayında. " }), "Sayfanız şu an herkese açık. Bağlantıyı Instagram profilinize ya da WhatsApp durumunuza ekleyebilirsiniz."]),
        el("div", { class: "actions" }, [copyBtn, el("a", { class: "btn line sm", href: "/tesis-ekle/?id=" + l.id, text: "Düzenle" }), el("a", { class: "btn line sm", href: "/hesabim/", text: "Hesabım" })])
      ]));
    } else if (mine) {
      root.appendChild(el("div", { class: "note" }, [
        el("p", {}, [l.status === "yayinda" ? "Bu sizin tesisiniz. " : el("strong", { text: "Taslak: bu sayfayı yalnızca siz görüyorsunuz. " }),
          el("a", { href: "/tesis-ekle/?id=" + l.id, text: "Düzenle" })])
      ]));
    }

    root.appendChild(el("nav", { class: "crumbs", "aria-label": "Konum" }, [el("a", { href: "/", text: "Ana sayfa" }), " / ", el("a", { href: "/tesisler/", text: "Tesisler" }), " / ", l.name]));

    var tags = (l.amenities || []).slice(0, 6).map(function (a) { return el("li", { class: /ısıtma|jakuzi|şömine/i.test(a) ? "warm" : "", text: a }); });
    if (l.pets === "evet") tags.push(el("li", { text: "Evcil hayvan kabul edilir" }));
    var head = el("header", { class: "page-head" }, [
      el("h1", { text: l.name }),
      place ? el("p", { class: "place", style: "margin-top:10px", text: place }) : null,
      l.summary ? el("p", { text: l.summary }) : null,
      tags.length ? el("ul", { class: "tags", style: "margin-top:18px" }, tags) : null
    ]);
    var fav = favButton(l, s);
    if (fav) head.appendChild(el("div", { class: "fav-row" }, [fav]));
    root.appendChild(head);

    if (photos.length) {
      var cls = "gallery" + (photos.length === 1 ? " n1" : photos.length < 5 ? " few" : "");
      root.appendChild(el("div", { class: cls }, photos.slice(0, 9).map(function (ph, i) {
        return el("a", { href: BD.photoUrl(ph.path), target: "_blank", rel: "noopener" }, [
          el("img", { src: BD.photoUrl(ph.path), alt: (ph.alt ? ph.alt + " — " : "") + l.name, loading: i ? "lazy" : "eager" })]);
      })));
      if (photos.length > 9) {
        var more = el("details", { class: "more-photos" }, [el("summary", { text: "Bütün fotoğraflar (" + photos.length + ")" }),
          el("div", { class: "gallery" }, photos.slice(9).map(function (ph) {
            return el("a", { href: BD.photoUrl(ph.path), target: "_blank", rel: "noopener" }, [el("img", { src: BD.photoUrl(ph.path), alt: ph.alt || l.name, loading: "lazy" })]);
          }))]);
        root.appendChild(more);
      }
    }

    // Ana sütun
    var facts = [];
    if (l.units) facts.push(["Bungalov sayısı", String(l.units)]);
    if (l.capacity) facts.push(["Kapasite", l.capacity]);
    if (l.beds) facts.push(["Yatak", l.beds]);
    if (l.checkin || l.checkout) facts.push(["Giriş / çıkış", (l.checkin || "—") + " / " + (l.checkout || "—")]);
    var prose = el("div", { class: "prose" }, [
      facts.length ? el("dl", { class: "facts" }, facts.map(function (f) { return el("div", {}, [el("dt", { text: f[0] }), el("dd", { text: f[1] })]); })) : null
    ]);
    if (l.description) { prose.appendChild(el("h2", { text: "Tesis hakkında" })); paragraphs(l.description).forEach(function (p) { prose.appendChild(p); }); }
    if ((l.amenities || []).length) {
      prose.appendChild(el("h2", { text: "Olanaklar" }));
      prose.appendChild(el("ul", { class: "amen" }, l.amenities.map(function (a) { return el("li", { text: a }); })));
    }
    var rules = ruleList(l.rules);
    if (l.pets && BD.PETS[l.pets]) rules.appendChild(el("li", { text: BD.PETS[l.pets] + "." }));
    if (rules.children.length) { prose.appendChild(el("h2", { text: "Bilmeniz gerekenler" })); prose.appendChild(rules); }
    var q = BD.fullAddress(l);
    if (l.address || l.neighborhood) {
      prose.appendChild(el("h2", { text: "Konum" }));
      prose.appendChild(el("p", {}, [q + ". ", el("a", { href: BD.mapLink(l.name + ", " + q), rel: "noopener", target: "_blank", text: "Haritada aç" })]));
      prose.appendChild(el("div", { class: "map" }, [el("iframe", { src: BD.mapSrc(q), title: l.name + " konumu", loading: "lazy", referrerpolicy: "no-referrer-when-downgrade" })]));
    }
    prose.appendChild(el("p", { class: "disclose" }, ["Bu sayfadaki bilgiler ve fotoğraflar tesis sahibi tarafından eklendi. Fiyat ve müsaitlik için tesisle doğrudan görüşün. Hatalı ya da yanıltıcı bir bilgi görürseniz ",
      el("a", { href: "https://wa.me/905327222545?text=" + encodeURIComponent("Merhaba, Bungalov Dünyası'ndaki şu tesis sayfasıyla ilgili bildirim yapmak istiyorum: " + location.origin + "/tesis/?t=" + l.slug), rel: "noopener", text: "bize bildirin" }), "."]));

    // İletişim
    var aside = el("aside", { class: "aside", "aria-label": "İletişim" }, [
      el("h3", { text: "Müsaitlik ve fiyat" }),
      el("p", { text: "Fiyat ve boş tarihler için tesisle doğrudan iletişime geçin. Komisyon yok." })
    ]);
    var w = BD.digits(l.whatsapp || l.phone);
    if (l.booking_url) aside.appendChild(el("a", { class: "btn solid", href: withUtm(l.booking_url), rel: "noopener nofollow", target: "_blank", text: "Takvimi ve fiyatı gör" }));
    if (w.length >= 11) aside.appendChild(el("a", { class: "btn wa", rel: "noopener", href: "https://wa.me/" + w + "?text=" + encodeURIComponent("Merhaba, Bungalov Dünyası'ndan ulaşıyorum. " + l.name + " için müsaitlik sormak istiyorum: [giriş] – [çıkış], [kişi sayısı] kişi."), text: "WhatsApp'tan sor" }));
    var t = BD.digits(l.phone || l.whatsapp);
    if (t.length >= 11) aside.appendChild(el("a", { class: "btn line", href: "tel:+" + t, text: "Ara: " + (l.phone || l.whatsapp) }));
    var links = [];
    if (l.website) links.push(el("a", { href: withUtm(l.website), rel: "noopener nofollow", target: "_blank", text: "Web sitesi" }));
    if (l.instagram) links.push(el("a", { href: "https://instagram.com/" + encodeURIComponent(l.instagram), rel: "noopener nofollow", target: "_blank", text: "Instagram: @" + l.instagram }));
    if (links.length) {
      var lp = el("p", { style: "margin:14px 0 0;font-size:15px" });
      links.forEach(function (a, i) { if (i) lp.appendChild(document.createTextNode(" · ")); lp.appendChild(a); });
      aside.appendChild(lp);
    }
    root.appendChild(el("div", { class: "layout" }, [prose, aside]));
  }

  function withUtm(u) {
    var safe = BD.safeUrl(u);
    if (!safe) return "#";
    try { var x = new URL(safe); x.searchParams.set("utm_source", "bungalovdunyasi"); x.searchParams.set("utm_medium", "referral"); return x.href; } catch (e) { return safe; }
  }

  function favButton(l, s) {
    if (l.status !== "yayinda") return null;
    var on = false;
    var b = el("button", { type: "button", class: "fav", "aria-pressed": "false" });
    function paint() { b.setAttribute("aria-pressed", on ? "true" : "false"); b.textContent = on ? "♥ Favorilerinizde" : "♡ Favorilere ekle"; }
    paint();
    if (s) sb.from("favorites").select("listing_id").eq("listing_id", l.id).maybeSingle().then(function (r) { on = !!r.data; paint(); });
    b.addEventListener("click", async function () {
      if (!s) return BD.toLogin("kisisel");
      b.disabled = true;
      var r = on ? await sb.from("favorites").delete().eq("listing_id", l.id) : await sb.from("favorites").insert({ listing_id: l.id });
      b.disabled = false;
      if (r.error) return BD.msg(msg, BD.err(r.error), "bad");
      on = !on; paint();
    });
    return b;
  }
})();
