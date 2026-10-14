/* Statik tesis sayfalarında favori düğmesi ve sahibine "Düzenle" bağlantısı */
(function () {
  "use strict";
  var el = BD.el, sb = BD.sb;
  var slot = document.getElementById("fav-slot");
  if (!slot) return;
  var slug = slot.dataset.slug;

  (async function () {
    var r = await sb.from("listings").select("id,owner").eq("slug", slug).maybeSingle();
    if (!r.data) return;
    var l = r.data, s = await BD.session(), on = false;
    var b = el("button", { type: "button", class: "fav", "aria-pressed": "false" });
    function paint() { b.setAttribute("aria-pressed", on ? "true" : "false"); b.textContent = on ? "♥ Favorilerinizde" : "♡ Favorilere ekle"; }
    paint();
    slot.appendChild(b);
    if (s && s.user.id === l.owner) slot.appendChild(el("a", { class: "btn line sm", href: "/tesis-ekle/?id=" + l.id, text: "Düzenle" }));
    if (s) { var f = await sb.from("favorites").select("listing_id").eq("listing_id", l.id).maybeSingle(); on = !!f.data; paint(); }
    b.addEventListener("click", async function () {
      if (!s) return BD.toLogin("kisisel");
      b.disabled = true;
      var x = on ? await sb.from("favorites").delete().eq("listing_id", l.id) : await sb.from("favorites").insert({ listing_id: l.id });
      b.disabled = false;
      if (!x.error) { on = !on; paint(); }
    });
  })();
})();
