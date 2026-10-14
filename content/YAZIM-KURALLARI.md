# Bungalov Dünyası — rehber yazısı kuralları

Bu dosya, rehber yazılarını yazan kişi ya da otomatik görev içindir.

## Dosya
- Her yazı `content/rehber/<slug>.json` dosyasıdır. Örnek için mevcut üç dosyaya bakın.
- Alanlar: `slug`, `title` (sayfa başlığı, cümle düzeninde), `seo_title` (60 karakteri geçmesin, " | Bungalov Dünyası" otomatik eklenir), `description` (140-160 karakter), `minutes` (okuma süresi, ~200 kelime/dk), `image` (build.py içindeki PHOTOS anahtarlarından biri), `date` (YYYY-MM-DD, yayın günü), `body` (HTML), `faq` (2-3 adet `{"q","a"}`). İsteğe bağlı `bolge`: yazı belirli bir ilçeyle ilgiliyse `il-slug/ilce-slug` (ör. `sakarya/sapanca`, `istanbul/sile`); verilmezse `sakarya/sapanca` sayılır. Genel (bölgeden bağımsız) yazılarda `"bolge": "genel"` yazın. Yazı, o bölgenin sayfasında (`/bolge/<il>/<ilçe>/`) listelenir.
- `body` içinde yalnızca şu etiketler: `p`, `h2`, `h3`, `ul`, `ol`, `li`, `strong`, `a`, `div class="note"`, `div class="note warm"`, `ul class="checklist"`. `h1` kullanmayın (başlık otomatik).
- İç bağlantılar `/rehber/<slug>/`, `/tesisler/labella-bungalov/`, `/bolge/sakarya/sapanca/`, `/tesis-ekle/` biçiminde. En az bir ilgili rehber yazısına bağlantı verin.

## Kapsam
- Site Türkiye genelindeki bungalov tesislerini kapsar; ilk ve en ayrıntılı bölge Sapanca. Başka bölgeler hakkında yazarken de aynı doğruluk kurallarına uyun.

## Dil ve ton
- Türkçe, sade, samimi ama abartısız. "Siz" diye hitap edin.
- 700-1100 kelime. Kısa paragraflar, somut öneriler, okuyucunun tesise sorabileceği sorular.
- Satış dili yok ("eşsiz", "muhteşem", "unutulmaz deneyim" gibi kalıplar kullanmayın). Emoji yok.
- Yazının sonunda okuyucuyu doğrudan tesisle konuşmaya ya da ilgili yazıya yönlendirin.

## Doğruluk
- Uydurma bilgi yok. Mesafe, süre, tren seferi, kayak merkezi, mevsim gibi gerçek dünya bilgilerini yazmadan önce web aramasıyla doğrulayın; emin değilseniz "yaklaşık", "trafiğe göre değişir" gibi ihtiyatlı yazın ya da hiç yazmayın.
- Fiyat yazmayın; zorunluysa kaynağı belli genel bir aralık verin ve "tesisten güncel fiyatı isteyin" deyin.
- Restoran, kafe ya da başka bir işletmenin adını vermeyin (Labella hariç). Tesis önerisi yalnızca Labella Bungalov olabilir ve şu açıklık notuyla birlikte: "Bungalov Dünyası ve Labella Bungalov aynı ekip tarafından işletiliyor."
- Labella hakkında yalnızca şu doğrulanmış bilgileri kullanın: Sapanca Memnuniye Mahallesi; 5 bağımsız A-frame bungalov; her birinde ısıtmalı özel açık havuz, terasta sıcak jakuzi, şömine, tam donanımlı mutfak, klima, Smart TV, Wi-Fi, barbekü/mangal, ateş çukuru, özel otopark; 4+1 kişilik (1 çift + 2 tek yatak, ~65 m²); giriş 14:00, çıkış 11:30; evcil hayvan için önceden sorulmalı.
- Rakip tesisler hakkında olumsuz bir şey yazmayın.

## Yayın
- `python3 build.py` hatasız çalışmalı; `docs/` güncellenir.
- `content/SIRA.md` içindeki satırı `[x]` yapın ve satırın sonuna yayın tarihini ekleyin.
