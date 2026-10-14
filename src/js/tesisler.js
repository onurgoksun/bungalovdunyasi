/* /tesisler/ : sayfa üretildikten sonra eklenen tesisleri de listeye kat */
(function () {
  "use strict";
  var $ = BD.$, $$ = BD.$$, el = BD.el, sb = BD.sb;
  var box = $("#uye-tesisler");
  if (!box) return;
  var known = {};
  $$("[data-slug]").forEach(function (e) { known[e.dataset.slug] = 1; });

  sb.from("listings").select("slug,name,summary,district,neighborhood,amenities,pets,photos")
    .eq("status", "yayinda").order("created_at", { ascending: false }).limit(200)
    .then(function (r) {
      if (r.error || !r.data) return;
      r.data.forEach(function (l) {
        if (known[l.slug]) return;
        box.appendChild(row(l, "/tesis/?t=" + encodeURIComponent(l.slug)));
      });
    });

  function row(l, url) {
    var ph = (l.photos || []).slice(0, 3);
    var shots = el("a", { class: "shots" + (ph.length < 3 ? " one" : ""), href: url, tabindex: "-1", "aria-hidden": "true" },
      (ph.length < 3 ? ph.slice(0, 1) : ph).map(function (p) { return el("img", { src: BD.photoUrl(p.path), alt: "", loading: "lazy" }); }));
    var tags = (l.amenities || []).slice(0, 5).map(function (a) { return el("li", { class: /ısıtma|jakuzi|şömine/i.test(a) ? "warm" : "", text: a }); });
    if (l.pets === "evet") tags.push(el("li", { text: "Evcil hayvan kabul edilir" }));
    return el("article", { class: "fac", "data-slug": l.slug }, [
      shots,
      el("div", {}, [
        el("h3", {}, [el("a", { href: url, text: l.name })]),
        el("p", { class: "place", text: [l.neighborhood, l.district].filter(Boolean).join(", ") }),
        l.summary ? el("p", { text: l.summary }) : null,
        tags.length ? el("ul", { class: "tags", "aria-label": "Öne çıkan olanaklar" }, tags) : null,
        el("div", { class: "actions" }, [el("a", { class: "btn solid", href: url, text: "Tesisi incele" })])
      ])
    ]);
  }
})();
