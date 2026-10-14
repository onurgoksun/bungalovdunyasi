/* /uye/ : giriş, üye olma, Google, profil tamamlama, şifre sıfırlama */
(function () {
  "use strict";
  var $ = BD.$, $$ = BD.$$, sb = BD.sb;
  var next = BD.safeNext(BD.qs("sonra")) || "";
  var kind = BD.qs("tur") === "kisisel" ? "kisisel" : (BD.qs("tur") === "kurumsal" ? "kurumsal" : "");
  var msg = $("#uye-msg");

  function show(id) {
    $$(".uye-panel").forEach(function (p) { p.hidden = p.id !== id; });
    $$(".tabs button").forEach(function (b) { b.setAttribute("aria-selected", b.dataset.panel === id ? "true" : "false"); });
    $(".tabs").hidden = !(id === "p-giris" || id === "p-kayit");
    BD.msg(msg, "");
  }
  function setKind(k, scope) {
    kind = k;
    $$(".kind input", scope).forEach(function (i) { i.checked = i.value === k; });
    $$(".only-kurumsal", scope).forEach(function (e) { e.hidden = k !== "kurumsal"; });
    $$(".only-kurumsal input", scope).forEach(function (i) { i.required = k === "kurumsal"; });
  }
  function goNext(profile) {
    if (next) { location.href = next; return; }
    location.href = "/hesabim/";
  }

  $$(".tabs button").forEach(function (b) { b.addEventListener("click", function () { show(b.dataset.panel); }); });
  ["#p-kayit", "#p-tamamla"].forEach(function (sel) {
    var scope = $(sel);
    $$(".kind input", scope).forEach(function (i) { i.addEventListener("change", function () { setKind(i.value, scope); }); });
  });

  // Giriş
  $("#f-giris").addEventListener("submit", async function (e) {
    e.preventDefault();
    var btn = e.submitter; btn.disabled = true;
    var r = await sb.auth.signInWithPassword({ email: $("#g-email").value.trim(), password: $("#g-sifre").value });
    btn.disabled = false;
    if (r.error) return BD.msg(msg, BD.err(r.error), "bad");
    await afterAuth();
  });

  // Üye ol
  $("#f-kayit").addEventListener("submit", async function (e) {
    e.preventDefault();
    if (!kind) return BD.msg(msg, "Üyelik türünü seçin.", "bad");
    if ($("#k-sifre").value.length < 8) return BD.msg(msg, "Şifre en az 8 karakter olmalı.", "bad");
    if (!$("#k-kvkk").checked) return BD.msg(msg, "Devam etmek için üyelik koşullarını ve aydınlatma metnini onaylayın.", "bad");
    var btn = e.submitter; btn.disabled = true;
    var meta = { kind: kind, full_name: $("#k-ad").value.trim(), phone: $("#k-tel").value.trim(), company: $("#k-firma").value.trim() };
    var r = await sb.auth.signUp({
      email: $("#k-email").value.trim(), password: $("#k-sifre").value,
      options: { data: meta, emailRedirectTo: location.origin + "/uye/" + (next ? "?sonra=" + encodeURIComponent(next) : "") }
    });
    btn.disabled = false;
    if (r.error) return BD.msg(msg, BD.err(r.error), "bad");
    if (!r.data.session) {
      show("p-dogrula");
      $("#dogrula-email").textContent = $("#k-email").value.trim();
      return;
    }
    await saveProfile(meta);
    goNext();
  });

  // Google (sağlayıcı açık değilse düğmeleri gizle)
  if (!BD.GOOGLE) $$(".btn-google, .or").forEach(function (e) { e.hidden = true; });
  $$(".btn-google").forEach(function (b) {
    b.addEventListener("click", async function () {
      try { sessionStorage.setItem("bd_kind", kind || ""); } catch (e) {}
      var r = await sb.auth.signInWithOAuth({
        provider: "google",
        options: { redirectTo: location.origin + "/uye/" + (next ? "?sonra=" + encodeURIComponent(next) : "") }
      });
      if (r.error) BD.msg(msg, BD.err(r.error), "bad");
    });
  });

  // Profil tamamlama (Google ile ilk giriş ya da eksik profil)
  $("#f-tamamla").addEventListener("submit", async function (e) {
    e.preventDefault();
    if (!kind) return BD.msg(msg, "Üyelik türünü seçin.", "bad");
    if (!$("#t-kvkk").checked) return BD.msg(msg, "Devam etmek için üyelik koşullarını ve aydınlatma metnini onaylayın.", "bad");
    var btn = e.submitter; btn.disabled = true;
    var err = await saveProfile({ kind: kind, full_name: $("#t-ad").value.trim(), phone: $("#t-tel").value.trim(), company: $("#t-firma").value.trim() });
    btn.disabled = false;
    if (err) return BD.msg(msg, BD.err(err), "bad");
    goNext();
  });

  // Şifre sıfırlama
  $("#sifre-unuttum").addEventListener("click", function (e) { e.preventDefault(); show("p-sifre"); $("#s-email").value = $("#g-email").value; });
  $("#f-sifre").addEventListener("submit", async function (e) {
    e.preventDefault();
    var btn = e.submitter; btn.disabled = true;
    var r = await sb.auth.resetPasswordForEmail($("#s-email").value.trim(), { redirectTo: location.origin + "/uye/?yeni-sifre=1" });
    btn.disabled = false;
    if (r.error) return BD.msg(msg, BD.err(r.error), "bad");
    BD.msg(msg, "Şifre yenileme bağlantısı e-posta adresinize gönderildi.", "ok");
  });
  $("#f-yeni").addEventListener("submit", async function (e) {
    e.preventDefault();
    if ($("#y-sifre").value.length < 8) return BD.msg(msg, "Şifre en az 8 karakter olmalı.", "bad");
    var r = await sb.auth.updateUser({ password: $("#y-sifre").value });
    if (r.error) return BD.msg(msg, BD.err(r.error), "bad");
    BD.msg(msg, "Şifreniz değişti.", "ok");
    setTimeout(function () { afterAuth(); }, 800);
  });
  $$(".back-giris").forEach(function (a) { a.addEventListener("click", function (e) { e.preventDefault(); show("p-giris"); }); });

  async function saveProfile(meta) {
    var s = await BD.session();
    if (!s) return "Oturum bulunamadı";
    var row = { id: s.user.id, kind: meta.kind, full_name: meta.full_name || "", phone: meta.phone || "",
      company: meta.kind === "kurumsal" ? (meta.company || "") : "", kvkk_ok_at: new Date().toISOString() };
    var r = await sb.from("site_profiles").upsert(row, { onConflict: "id" });
    return r.error || null;
  }

  async function afterAuth() {
    var s = await BD.session();
    if (!s) return;
    var p = await BD.profile();
    if (p) return goNext(p);
    // E-posta ile kayıt olmuşsa bilgiler hesapta duruyor: profili kendiliğinden oluştur
    var md = s.user.user_metadata || {};
    if (md.kind === "kurumsal" || md.kind === "kisisel") {
      var err = await saveProfile(md);
      if (!err) return goNext();
    }
    // Google ile ilk giriş: tür ve bilgileri sor
    var stored = ""; try { stored = sessionStorage.getItem("bd_kind") || ""; } catch (e) {}
    show("p-tamamla");
    $("#t-ad").value = md.full_name || md.name || "";
    setKind(stored || kind || "", $("#p-tamamla"));
  }

  // Başlangıç
  (async function () {
    if (BD.qs("yeni-sifre")) {
      sb.auth.onAuthStateChange(function (ev) { if (ev === "PASSWORD_RECOVERY") show("p-yeni"); });
      show("p-yeni");
      return;
    }
    show(kind ? "p-kayit" : "p-giris");
    setKind(kind, $("#p-kayit"));
    if (BD.qs("code") || location.hash.indexOf("access_token") >= 0) {
      // OAuth / e-posta doğrulama dönüşü: oturumun kurulmasını bekle
      for (var i = 0; i < 20 && !(await BD.session()); i++) await new Promise(function (r) { setTimeout(r, 250); });
    }
    if (await BD.session()) await afterAuth();
  })();
})();
