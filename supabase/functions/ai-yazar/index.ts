// Bungalov Dünyası · tesis yazıları için yapay zekâ yardımcısı (Supabase Edge Function)
// Gerekli gizli değişken: ANTHROPIC_API_KEY  (Edge Functions → Secrets)
// Yalnızca giriş yapmış kurumsal üyeler kullanabilir; günlük kullanım sınırı vardır.
import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { withSupabase } from "jsr:@supabase/server@^1";

const DAILY_LIMIT = 30;
const MODEL = "claude-haiku-5-5";

const TASKS: Record<string, string> = {
  summary: "Tesis için en fazla 2 cümle, 250 karakteri geçmeyen kısa bir tanıtım yaz. Tesisi listede öne çıkaran somut özelliklerden bahset.",
  description: "Tesis sayfası için 3-5 kısa paragraflık bir açıklama yaz (toplam 120-250 kelime). Bungalovları, olanakları, konumu ve kimler için uygun olduğunu anlat. Paragraflar arasında boş satır bırak.",
  rules: "Tesis kuralları için kısa ve nazik maddeler yaz (her satır '- ' ile başlasın, en fazla 8 madde). Giriş-çıkış saatleri ve evcil hayvan bilgisi verildiyse onları kullan.",
  improve: "Aşağıdaki metni anlamını ve bilgilerini koruyarak düzelt: yazım ve noktalama hatalarını gider, daha akıcı ve okunaklı yap. Yeni bilgi ekleme. Satır ve paragraf yapısını koru.",
};

const SYSTEM = `Sen Sapanca ve çevresindeki bungalov tesisleri için Türkçe tanıtım metinleri yazan bir yardımcısın.
Kurallar:
- Yalnızca kullanıcının verdiği bilgileri kullan. Verilmeyen hiçbir özelliği, mesafeyi, fiyatı ya da ödülü uydurma.
- Sade, samimi ve güven veren bir dil kullan; "eşsiz", "muhteşem", "unutulmaz", "cennetten bir köşe" gibi abartılı kalıplar kullanma.
- Okuyucuya "siz" diye hitap et. Emoji, başlık, markdown kullanma.
- Yalnızca istenen metni yaz; açıklama, giriş cümlesi ya da tırnak ekleme.`;

const json = (body: unknown, status = 200) => Response.json(body, { status });
const clean = (v: unknown, max = 600) => String(v ?? "").replace(/\s+/g, " ").trim().slice(0, max);

export default {
  fetch: withSupabase({ auth: "user" }, async (req, ctx) => {
    if (req.method !== "POST") return json({ error: "Yalnızca POST" }, 405);
    const apiKey = Deno.env.get("ANTHROPIC_API_KEY");
    if (!apiKey) return json({ error: "Yapay zekâ yardımcısı henüz etkin değil." }, 503);

    // deno-lint-ignore no-explicit-any
    const claims: any = ctx.jwtClaims ?? ctx.userClaims ?? {};
    const uid = String(claims.sub ?? claims.id ?? "");
    if (!uid) return json({ error: "Önce giriş yapın." }, 401);

    const { data: prof } = await ctx.supabase.from("site_profiles").select("kind").eq("id", uid).maybeSingle();
    if (!prof || prof.kind !== "kurumsal") return json({ error: "Yardımcı yalnızca kurumsal üyeler içindir." }, 403);

    let body: Record<string, unknown>;
    try { body = await req.json(); } catch { return json({ error: "Geçersiz istek" }, 400); }
    const task = String(body.task || "");
    if (!TASKS[task]) return json({ error: "Bilinmeyen görev" }, 400);

    const { data: ok, error: le } = await ctx.supabaseAdmin.rpc("ai_take", { p_user: uid, p_limit: DAILY_LIMIT });
    if (le) { console.error("ai_take", le); return json({ error: "Yardımcı şu an yanıt veremiyor." }, 500); }
    if (!ok) return json({ error: `Günlük ${DAILY_LIMIT} kullanım hakkınız doldu. Yarın tekrar deneyin.` }, 429);

    const f = (body.fields || {}) as Record<string, unknown>;
    const facts = [
      ["Tesis adı", clean(f.name, 80)],
      ["İlçe / semt", [clean(f.district, 40), clean(f.neighborhood, 60)].filter(Boolean).join(" / ")],
      ["Bungalov sayısı", clean(f.units, 10)],
      ["Kapasite", clean(f.capacity, 80)],
      ["Yatak düzeni", clean(f.beds, 120)],
      ["Olanaklar", Array.isArray(f.amenities) ? (f.amenities as unknown[]).slice(0, 40).map((x) => clean(x, 40)).join(", ") : ""],
      ["Evcil hayvan", clean(f.pets, 20)],
      ["Giriş saati", clean(f.checkin, 10)],
      ["Çıkış saati", clean(f.checkout, 10)],
      ["Sahibinin notları", clean(f.notes, 800)],
    ].filter(([, v]) => v).map(([k, v]) => `${k}: ${v}`).join("\n");
    const text = String(body.text ?? "").trim().slice(0, 6000);

    const userMsg = task === "improve"
      ? `${TASKS[task]}\n\nMetin:\n${text}`
      : `${TASKS[task]}\n\nTesis bilgileri:\n${facts || "(bilgi girilmemiş)"}${text ? `\n\nSahibinin mevcut taslağı (varsa yararlan):\n${text}` : ""}`;

    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "x-api-key": apiKey, "anthropic-version": "2023-06-01", "content-type": "application/json" },
      body: JSON.stringify({ model: MODEL, max_tokens: 900, system: SYSTEM, messages: [{ role: "user", content: userMsg }] }),
    });
    if (!r.ok) {
      console.error("anthropic", r.status, await r.text());
      return json({ error: "Yardımcı şu an yanıt veremiyor, biraz sonra tekrar deneyin." }, 502);
    }
    const j = await r.json();
    // deno-lint-ignore no-explicit-any
    const out = (j.content || []).filter((c: any) => c.type === "text").map((c: any) => c.text).join("").trim();
    return json({ text: out });
  }),
};
