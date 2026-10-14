// Bungalov Dünyası · tesis yazıları için yapay zekâ yardımcısı
// Supabase Edge Function. Gerekli gizli değişken: ANTHROPIC_API_KEY
// Yalnızca giriş yapmış kurumsal üyeler kullanabilir; günlük sınır vardır.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.4";

const ALLOWED = ["https://bungalovdunyasi.tr", "https://www.bungalovdunyasi.tr", "https://bungalovdunyasi.com", "https://www.bungalovdunyasi.com"];
const DAILY_LIMIT = 30;
const MODEL = "claude-haiku-5-5";

const TASKS: Record<string, string> = {
  summary: "Tesis için en fazla 2 cümle, 250 karakteri geçmeyen kısa bir tanıtım yaz. Tesisi listede öne çıkaran somut özelliklerden bahset.",
  description: "Tesis sayfası için 3-5 kısa paragraflık bir açıklama yaz (toplam 120-250 kelime). Bungalovları, olanakları, konumu ve kimler için uygun olduğunu anlat. Paragraflar arasında boş satır bırak.",
  rules: "Tesis kuralları için kısa ve nazik maddeler yaz (her satır '- ' ile başlasın, en fazla 8 madde). Giriş-çıkış saatleri ve evcil hayvan bilgisi verildiyse onları kullan.",
  improve: "Aşağıdaki metni anlamını ve bilgilerini koruyarak düzelt: yazım ve noktalama hatalarını gider, daha akıcı ve okunaklı yap. Yeni bilgi ekleme.",
};

const SYSTEM = `Sen Sapanca ve çevresindeki bungalov tesisleri için Türkçe tanıtım metinleri yazan bir yardımcısın.
Kurallar:
- Yalnızca kullanıcının verdiği bilgileri kullan. Verilmeyen hiçbir özelliği, mesafeyi, fiyatı ya da ödülü uydurma.
- Sade, samimi ve güven veren bir dil kullan; "eşsiz", "muhteşem", "unutulmaz", "cennetten bir köşe" gibi abartılı kalıplar kullanma.
- Okuyucuya "siz" diye hitap et. Emoji, başlık, markdown kullanma.
- Yalnızca istenen metni yaz; açıklama, giriş cümlesi ya da tırnak ekleme.`;

function cors(origin: string | null) {
  const o = origin && ALLOWED.includes(origin) ? origin : ALLOWED[0];
  return {
    "Access-Control-Allow-Origin": o,
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary": "Origin",
  };
}

function reply(body: unknown, status: number, origin: string | null) {
  return new Response(JSON.stringify(body), { status, headers: { ...cors(origin), "Content-Type": "application/json" } });
}

function clean(v: unknown, max = 600): string {
  return String(v ?? "").replace(/\s+/g, " ").trim().slice(0, max);
}

Deno.serve(async (req) => {
  const origin = req.headers.get("Origin");
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors(origin) });
  if (req.method !== "POST") return reply({ error: "Yalnızca POST" }, 405, origin);

  const url = Deno.env.get("SUPABASE_URL")!;
  const service = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const apiKey = Deno.env.get("ANTHROPIC_API_KEY");
  if (!apiKey) return reply({ error: "Yapay zekâ yardımcısı henüz etkin değil." }, 503, origin);

  const jwt = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  const admin = createClient(url, service, { auth: { persistSession: false } });
  const { data: u, error: ue } = await admin.auth.getUser(jwt);
  if (ue || !u?.user) return reply({ error: "Önce giriş yapın." }, 401, origin);
  const uid = u.user.id;

  const { data: prof } = await admin.from("site_profiles").select("kind").eq("id", uid).maybeSingle();
  if (!prof || prof.kind !== "kurumsal") return reply({ error: "Yardımcı yalnızca kurumsal üyeler içindir." }, 403, origin);

  let body: Record<string, unknown>;
  try { body = await req.json(); } catch { return reply({ error: "Geçersiz istek" }, 400, origin); }
  const task = String(body.task || "");
  if (!TASKS[task]) return reply({ error: "Bilinmeyen görev" }, 400, origin);

  const { data: ok } = await admin.rpc("ai_take", { p_user: uid, p_limit: DAILY_LIMIT });
  if (!ok) return reply({ error: `Günlük ${DAILY_LIMIT} kullanım hakkınız doldu. Yarın tekrar deneyin.` }, 429, origin);

  const f = (body.fields || {}) as Record<string, unknown>;
  const facts = [
    ["Tesis adı", clean(f.name, 80)],
    ["İlçe / semt", [clean(f.district, 40), clean(f.neighborhood, 60)].filter(Boolean).join(" / ")],
    ["Bungalov sayısı", clean(f.units, 10)],
    ["Kapasite", clean(f.capacity, 80)],
    ["Yatak düzeni", clean(f.beds, 120)],
    ["Olanaklar", Array.isArray(f.amenities) ? (f.amenities as unknown[]).map((x) => clean(x, 40)).join(", ") : ""],
    ["Evcil hayvan", clean(f.pets, 20)],
    ["Giriş saati", clean(f.checkin, 10)],
    ["Çıkış saati", clean(f.checkout, 10)],
    ["Sahibinin notları", clean(f.notes, 800)],
  ].filter(([, v]) => v).map(([k, v]) => `${k}: ${v}`).join("\n");
  const text = clean(body.text, 6000);

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
    return reply({ error: "Yardımcı şu an yanıt veremiyor, biraz sonra tekrar deneyin." }, 502, origin);
  }
  const j = await r.json();
  const out = (j.content || []).filter((c: { type: string }) => c.type === "text").map((c: { text: string }) => c.text).join("").trim();
  return reply({ text: out }, 200, origin);
});
