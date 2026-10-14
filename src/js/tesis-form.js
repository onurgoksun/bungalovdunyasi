/* /tesis-ekle/ : kurumsal üyenin tesis oluşturma / düzenleme formu */
(function () {
  "use strict";
  var $ = BD.$, $$ = BD.$$, el = BD.el, sb = BD.sb;
  var msg = $("#form-msg");
  var uid = null, editing = null, photos = [], session = null, removedPaths = [];
  var MAX_PHOTOS = 20;

  (async function () {
    session = await BD.session();
    if (!session) return BD.toLogin("kurumsal");
    var p = await BD.profile();
    if (!p) { location.href = "/uye/?tur=kurumsal&sonra=" + encodeURIComponent(location.pathname + location.search); return; }
    uid = session.user.id;
    $("#form-yukleniyor").hidden = true;
    if (p.kind !== "kurumsal") { $("#kisisel-uyari").hidden = false; return; }
    buildAmenities();
    $("#tesis-form").hidden = false;
    var id = BD.qs("id");
    if (id) {
      var r = await sb.from("listings").select("*").eq("id", id).eq("owner", uid).maybeSingle();
      if (r.error || !r.data) { BD.msg(msg, "Tesis bulunamadı ya da size ait değil.", "bad"); return; }
      editing = r.data;
      fill(editing);
      $("#form-baslik").textContent = "Tesisi düzenle";
      $("#kaydet").textContent = "Değişiklikleri kaydet";
      $("#sil").hidden = false;
      if (editing.status === "kaldirildi") {
        BD.msg(msg, "Bu tesis yayından kaldırıldı" + (editing.removed_reason ? " (" + editing.removed_reason + ")" : "") + ". Düzenlemek için bize WhatsApp'tan yazın.", "bad");
        $("#kaydet").disabled = true; $("#taslak").disabled = true;
      }
      if (editing.status === "yayinda") { var v = $("#goruntule"); v.href = "/tesis/?t=" + encodeURIComponent(editing.slug); v.hidden = false; }
    } else if (p.company) {
      $("#f-name").value = p.company.split(/[,;\n]/)[0].trim();
      $("#f-phone").value = p.phone || "";
      $("#f-whatsapp").value = p.phone || "";
    }
    updateMap(); counters();
  })();

  function buildAmenities() {
    var box = $("#amenities");
    BD.AMENITIES.forEach(function (a, i) {
      box.appendChild(el("label", { class: "chk" }, [el("input", { type: "checkbox", value: a, id: "am-" + i }), el("span", { text: a })]));
    });
  }

  var FIELDS = ["name", "summary", "description", "district", "neighborhood", "address", "units", "capacity", "beds", "pets",
    "checkin", "checkout", "rules", "phone", "whatsapp", "website", "booking_url", "instagram"];

  function fill(l) {
    FIELDS.forEach(function (k) { var i = $("#f-" + k.replace("_", "-")); if (i) i.value = l[k] == null ? "" : l[k]; });
    $$("#amenities input").forEach(function (c) { c.checked = (l.amenities || []).indexOf(c.value) >= 0; });
    photos = (l.photos || []).slice();
    renderPhotos();
  }

  function collect() {
    var o = {};
    FIELDS.forEach(function (k) { var i = $("#f-" + k.replace("_", "-")); o[k] = i ? i.value.trim() : ""; });
    o.units = o.units ? parseInt(o.units, 10) : null;
    o.amenities = $$("#amenities input:checked").map(function (c) { return c.value; });
    o.website = BD.safeUrl(o.website);
    o.booking_url = BD.safeUrl(o.booking_url);
    o.instagram = o.instagram.replace(/^@/, "").replace(/^https?:\/\/(www\.)?instagram\.com\//i, "").replace(/\/.*$/, "").slice(0, 60);
    o.photos = photos;
    return o;
  }

  // ---------------------------------------------------------------- Harita önizlemesi
  var mapTimer = null;
  function updateMap() {
    clearTimeout(mapTimer);
    mapTimer = setTimeout(function () {
      var q = BD.fullAddress({ address: $("#f-address").value, neighborhood: $("#f-neighborhood").value, district: $("#f-district").value });
      var frame = $("#map-frame");
      if (!$("#f-address").value.trim() && !$("#f-neighborhood").value.trim()) { frame.hidden = true; $("#map-empty").hidden = false; return; }
      frame.hidden = false; $("#map-empty").hidden = true;
      if (frame.dataset.q !== q) { frame.dataset.q = q; frame.src = BD.mapSrc(q); }
      $("#map-link").href = BD.mapLink(q);
    }, 600);
  }
  ["#f-address", "#f-neighborhood", "#f-district"].forEach(function (s) { $(s).addEventListener("input", updateMap); $(s).addEventListener("change", updateMap); });

  // ---------------------------------------------------------------- Karakter sayaçları
  function counters() {
    $$("[data-max]").forEach(function (t) {
      var c = $("#" + t.id + "-n");
      if (c) c.textContent = t.value.length + " / " + t.dataset.max;
    });
  }
  $$("[data-max]").forEach(function (t) { t.addEventListener("input", counters); });

  // ---------------------------------------------------------------- Fotoğraflar
  function renderPhotos() {
    var box = $("#photos");
    box.textContent = "";
    photos.forEach(function (ph, i) {
      var card = el("div", { class: "photo" + (i === 0 ? " cover" : "") }, [
        el("img", { src: BD.photoUrl(ph.path), alt: ph.alt || "" }),
        i === 0 ? el("span", { class: "badge", text: "Kapak" }) : null,
        el("input", { type: "text", maxlength: "120", placeholder: "Kısa açıklama (ör. havuz ve teras)", value: ph.alt || "", "aria-label": "Fotoğraf açıklaması",
          oninput: function (e) { photos[i].alt = e.target.value; } }),
        el("div", { class: "photo-actions" }, [
          i > 0 ? el("button", { type: "button", class: "mini", text: "Kapak yap", onclick: function () { photos.unshift(photos.splice(i, 1)[0]); renderPhotos(); } }) : null,
          i > 0 ? el("button", { type: "button", class: "mini", "aria-label": "Sola taşı", text: "←", onclick: function () { var t = photos[i - 1]; photos[i - 1] = photos[i]; photos[i] = t; renderPhotos(); } }) : null,
          i < photos.length - 1 ? el("button", { type: "button", class: "mini", "aria-label": "Sağa taşı", text: "→", onclick: function () { var t = photos[i + 1]; photos[i + 1] = photos[i]; photos[i] = t; renderPhotos(); } }) : null,
          el("button", { type: "button", class: "mini danger", text: "Sil", onclick: function () {
            removedPaths.push(photos.splice(i, 1)[0].path);
            renderPhotos();
          } })
        ])
      ]);
      box.appendChild(card);
    });
    $("#photo-count").textContent = photos.length + " / " + MAX_PHOTOS;
    $("#photo-pick").disabled = photos.length >= MAX_PHOTOS;
  }

  function resize(file) {
    return new Promise(function (resolve, reject) {
      var img = new Image();
      var url = URL.createObjectURL(file);
      img.onload = function () {
        var max = 1800, w = img.naturalWidth, h = img.naturalHeight;
        var k = Math.min(1, max / Math.max(w, h));
        var c = document.createElement("canvas");
        c.width = Math.round(w * k); c.height = Math.round(h * k);
        c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url);
        c.toBlob(function (b) {
          if (b && b.type === "image/webp") return resolve({ blob: b, ext: "webp", type: "image/webp" });
          c.toBlob(function (j) { j ? resolve({ blob: j, ext: "jpg", type: "image/jpeg" }) : reject(new Error("Fotoğraf işlenemedi")); }, "image/jpeg", 0.85);
        }, "image/webp", 0.82);
      };
      img.onerror = function () { URL.revokeObjectURL(url); reject(new Error(file.name + " açılamadı (JPG, PNG ya da WEBP seçin)")); };
      img.src = url;
    });
  }

  $("#photo-input").addEventListener("change", async function (e) {
    var files = Array.prototype.slice.call(e.target.files || []).slice(0, MAX_PHOTOS - photos.length);
    e.target.value = "";
    if (!files.length) return;
    var st = $("#photo-status");
    for (var i = 0; i < files.length; i++) {
      st.textContent = "Yükleniyor: " + (i + 1) + " / " + files.length;
      try {
        var out = await resize(files[i]);
        var path = uid + "/" + (editing ? editing.id : "yeni") + "/" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7) + "." + out.ext;
        var up = await sb.storage.from(BD.BUCKET).upload(path, out.blob, { contentType: out.type, cacheControl: "31536000", upsert: false });
        if (up.error) throw up.error;
        photos.push({ path: path, alt: "" });
        renderPhotos();
      } catch (err) {
        BD.msg(msg, BD.err(err), "bad");
      }
    }
    st.textContent = "";
  });
  $("#photo-pick").addEventListener("click", function () { $("#photo-input").click(); });

  // ---------------------------------------------------------------- Kaydet
  var RESERVED = ["labella-bungalov", "tesis", "yeni"];
  async function uniqueSlug(name) {
    var base = BD.slugify(name), s = base;
    if (base.length < 3) base = s = "tesis-" + base;
    for (var n = 2; n < 30; n++) {
      if (RESERVED.indexOf(s) >= 0) { s = base + "-" + n; continue; }
      var r = await sb.from("listings").select("id").eq("slug", s).maybeSingle();
      if (!r.data || (editing && r.data.id === editing.id)) return s;
      s = base + "-" + n;
    }
    return base + "-" + Date.now().toString(36);
  }

  $("#tesis-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    BD.msg(msg, "");
    var o = collect();
    if (o.name.length < 2) return BD.msg(msg, "Tesis adını yazın.", "bad");
    if (!o.phone && !o.whatsapp) return BD.msg(msg, "Misafirlerin size ulaşabilmesi için telefon ya da WhatsApp numarası girin.", "bad");
    if (!photos.length) return BD.msg(msg, "En az bir fotoğraf ekleyin.", "bad");
    if (!$("#f-onay").checked) return BD.msg(msg, "Bilgilerin ve fotoğrafların doğru ve size ait olduğunu onaylayın.", "bad");
    var btn = $("#kaydet"); btn.disabled = true;
    var draft = e.submitter && e.submitter.id === "taslak";
    try {
      var r;
      if (editing) {
        if (o.name !== editing.name) o.slug = await uniqueSlug(o.name);
        if (draft) o.status = "taslak"; else if (editing.status !== "kaldirildi") o.status = "yayinda";
        r = await sb.from("listings").update(o).eq("id", editing.id).select().single();
      } else {
        o.slug = await uniqueSlug(o.name);
        o.status = draft ? "taslak" : "yayinda";
        r = await sb.from("listings").insert(o).select().single();
        if (r.error && r.error.code === "23505") {
          o.slug = o.slug.slice(0, 70) + "-" + Math.random().toString(36).slice(2, 6);
          r = await sb.from("listings").insert(o).select().single();
        }
      }
      if (r.error) throw r.error;
      editing = r.data;
      if (removedPaths.length) { var rm = removedPaths.filter(function (p) { return p.indexOf(uid + "/") === 0; }); removedPaths = []; if (rm.length) sb.storage.from(BD.BUCKET).remove(rm); }
      if (r.data.status === "yayinda") {
        location.href = "/tesis/?t=" + encodeURIComponent(r.data.slug) + "&yeni=1";
      } else {
        BD.msg(msg, "Taslak kaydedildi. Hazır olduğunuzda Yayınla'ya basın.", "ok");
      }
    } catch (err) {
      BD.msg(msg, BD.err(err), "bad");
    } finally {
      btn.disabled = false;
    }
  });

  // Silme
  $("#sil").addEventListener("click", async function () {
    if (!editing) return;
    var box = $("#sil-onay");
    box.hidden = false;
  });
  $("#sil-evet").addEventListener("click", async function () {
    if (!editing) return;
    var paths = (editing.photos || []).map(function (p) { return p.path; });
    var r = await sb.from("listings").delete().eq("id", editing.id);
    if (r.error) return BD.msg(msg, BD.err(r.error), "bad");
    if (paths.length) await sb.storage.from(BD.BUCKET).remove(paths);
    location.href = "/hesabim/";
  });
  $("#sil-hayir").addEventListener("click", function () { $("#sil-onay").hidden = true; });
})();
