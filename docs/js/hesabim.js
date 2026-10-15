/* /hesabim/ : profil, tesislerim (kurumsal), favorilerim (kişisel) */
(function () {
  "use strict";
  var $ = BD.$, el = BD.el, sb = BD.sb;
  var msg = $("#hesap-msg");
  var STATUS = { yayinda: ["Yayında", "ok"], taslak: ["Taslak", "mute"], kaldirildi: ["Yayından kaldırıldı", "bad"] };

  (async function () {
    var s = await BD.session();
    if (!s) return BD.toLogin();
    var p = await BD.profile();
    if (!p) { location.href = "/uye/?sonra=/hesabim/"; return; }
    $("#hesap-yukleniyor").hidden = true;
    $("#hesap").hidden = false;
    $("#h-email").textContent = s.user.email || "";
    $("#h-tur").textContent = p.kind === "kurumsal" ? "Kurumsal üye (tesis sahibi)" : "Kişisel üye";
    $("#h-ad").value = p.full_name || "";
    $("#h-tel").value = p.phone || "";
    $("#h-firma").value = p.company || "";
    $("#h-firma-satir").hidden = p.kind !== "kurumsal";
    $("#kurumsal-bolum").hidden = p.kind !== "kurumsal";
    $("#kisisel-bolum").hidden = p.kind === "kurumsal";
    if (p.kind === "kurumsal") loadListings(s.user.id); else loadFavorites();

    $("#f-profil").addEventListener("submit", async function (e) {
      e.preventDefault();
      var r = await sb.from("site_profiles").update({ full_name: $("#h-ad").value.trim(), phone: $("#h-tel").value.trim(), company: $("#h-firma").value.trim() }).eq("id", s.user.id);
      BD.msg(msg, r.error ? BD.err(r.error) : "Bilgileriniz kaydedildi.", r.error ? "bad" : "ok");
    });
    $("#kurumsala-gec").addEventListener("click", async function () {
      var r = await sb.from("site_profiles").update({ kind: "kurumsal" }).eq("id", s.user.id);
      if (r.error) return BD.msg(msg, BD.err(r.error), "bad");
      location.href = "/tesis-ekle/";
    });
    $("#cikis").addEventListener("click", async function () { await sb.auth.signOut(); location.href = "/"; });
  })();

  async function loadListings(uid) {
    var box = $("#tesislerim");
    var r = await sb.from("listings").select("id,slug,name,status,province,district,neighborhood,photos,updated_at,removed_reason").eq("owner", uid).order("updated_at", { ascending: false });
    box.textContent = "";
    if (r.error) return BD.msg(msg, BD.err(r.error), "bad");
    if (!r.data.length) {
      box.appendChild(el("div", { class: "empty" }, [
        el("p", { text: "Henüz tesis eklemediniz. İlk tesisinizi ekleyin; fotoğraflarınızı, olanaklarınızı ve iletişim bilgilerinizi girin, sayfanız hemen yayına girsin." }),
        el("a", { class: "btn solid", href: "/tesis-ekle/", text: "Tesis ekle" })]));
      return;
    }
    r.data.forEach(function (l) {
      var st = STATUS[l.status] || ["", ""];
      var cover = (l.photos || [])[0];
      var row = el("article", { class: "my-row" }, [
        cover ? el("img", { src: BD.photoUrl(cover.path), alt: "", loading: "lazy" }) : el("div", { class: "ph" }),
        el("div", { class: "my-main" }, [
          el("h3", { text: l.name }),
          el("p", { class: "place", text: BD.place(l) }),
          el("span", { class: "pill " + st[1], text: st[0] }),
          l.status === "kaldirildi" && l.removed_reason ? el("p", { class: "small bad", text: "Sebep: " + l.removed_reason }) : null
        ]),
        el("div", { class: "my-actions" }, [
          l.status === "yayinda" ? el("a", { class: "btn line sm", href: "/tesis/?t=" + encodeURIComponent(l.slug), text: "Görüntüle" }) : null,
          l.status === "yayinda" ? el("button", { class: "btn line sm", type: "button", text: "Rozet", onclick: function () { toggleBadge(row, l); } }) : null,
          el("a", { class: "btn solid sm", href: "/tesis-ekle/?id=" + encodeURIComponent(l.id), text: "Düzenle" }),
          l.status !== "kaldirildi" ? el("button", { class: "btn line sm", type: "button", text: l.status === "yayinda" ? "Taslağa al" : "Yayınla",
            onclick: async function () {
              var to = l.status === "yayinda" ? "taslak" : "yayinda";
              var u = await sb.from("listings").update({ status: to }).eq("id", l.id);
              if (u.error) return BD.msg(msg, BD.err(u.error), "bad");
              loadListings(uid);
            } }) : null
        ])
      ]);
      box.appendChild(row);
    });
  }

  // Partner rozeti: tesisin sitesine eklenecek kod
  function toggleBadge(row, l) {
    var old = row.querySelector(".badge-box");
    if (old) { old.remove(); return; }
    var target = "https://bungalovdunyasi.com/tesisler/" + l.slug + "/";
    var styles = [["muhur", "Mühür", 120, 120], ["partner", "Koyu", 220, 61], ["partner-acik", "Açık", 220, 61]];
    var ta = el("textarea", { rows: "3", readonly: true });
    var prev = el("div", { class: "badge-row", style: "margin:10px 0" });
    function set(st) {
      ta.value = '<a href="' + target + '" target="_blank" rel="noopener" title="Bungalov Dünyası partner tesis"><img src="https://bungalovdunyasi.com/rozet/' + st[0] + '.svg" alt="Bungalov Dünyası Partner Tesis" width="' + st[2] + '" height="' + st[3] + '"></a>';
    }
    styles.forEach(function (st) {
      prev.appendChild(el("button", { type: "button", class: "mini", title: st[1], onclick: function () { set(st); } }, [el("img", { src: "/rozet/" + st[0] + ".svg", alt: st[1], style: "height:44px;width:auto" })]));
    });
    set(styles[0]);
    var copy = el("button", { type: "button", class: "btn solid sm", text: "Kodu kopyala", onclick: function () {
      ta.select(); try { navigator.clipboard.writeText(ta.value); } catch (e) { document.execCommand("copy"); }
      copy.textContent = "Kopyalandı";
    } });
    row.appendChild(el("div", { class: "badge-box" }, [
      el("p", { class: "small", style: "margin:0", text: "Rozeti sitenizin alt kısmına ya da iletişim sayfasına ekleyin. Tıklayan misafir tesisinizin Bungalov Dünyası sayfasına gelir. Bir görünüm seçin, kodu kopyalayıp sitenize yapıştırın (WordPress'te \"Özel HTML\" bloğuna)." }),
      prev, ta, el("div", { class: "actions" }, [copy, el("a", { class: "btn line sm", href: "/rozet/", target: "_blank", text: "Rozet ne demek?" })])
    ]));
  }

  async function loadFavorites() {
    var box = $("#favorilerim");
    var r = await sb.from("favorites").select("listing_id, listings(id,slug,name,province,district,neighborhood,photos,status)").order("created_at", { ascending: false });
    box.textContent = "";
    if (r.error) return BD.msg(msg, BD.err(r.error), "bad");
    var items = r.data.filter(function (f) { return f.listings && f.listings.status === "yayinda"; });
    if (!items.length) {
      box.appendChild(el("div", { class: "empty" }, [
        el("p", { text: "Favori tesisiniz yok. Tesis sayfalarındaki kalp işaretiyle beğendiğiniz yerleri buraya ekleyebilirsiniz." }),
        el("a", { class: "btn solid", href: "/tesisler/", text: "Tesislere göz atın" })]));
      return;
    }
    items.forEach(function (f) {
      var l = f.listings, cover = (l.photos || [])[0];
      box.appendChild(el("article", { class: "my-row" }, [
        cover ? el("img", { src: BD.photoUrl(cover.path), alt: "", loading: "lazy" }) : el("div", { class: "ph" }),
        el("div", { class: "my-main" }, [el("h3", { text: l.name }), el("p", { class: "place", text: BD.place(l) })]),
        el("div", { class: "my-actions" }, [
          el("a", { class: "btn solid sm", href: "/tesis/?t=" + encodeURIComponent(l.slug), text: "Görüntüle" }),
          el("button", { class: "btn line sm", type: "button", text: "Favorilerden çıkar", onclick: async function () {
            await sb.from("favorites").delete().eq("listing_id", l.id); loadFavorites();
          } })
        ])
      ]));
    });
  }
})();
