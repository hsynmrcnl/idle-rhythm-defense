---
name: oyun-testcisi
description: Oyunu 10 farklı oyuncu tipinde (persona) yapay oyuncu ajanlarıyla başsız Chrome'da GERÇEKTEN oynatıp öncelik sıralı bulgu raporu çıkaran oyun testi turu — oyundan bağımsız, oyuna özel kısım tek bir profil dosyasında. Hüseyin "oyuncu turu koş", "oyun testçisi", "oyuncu ajanları", "playtest", "oyunu test ettir", "/oyun-testcisi" dediğinde kullan. Pahalıdır (10 sonnet ajanı, ~45–60 dk): yalnız açıkça istenince koş, kendiliğinden başlatma.
---

# Oyun testçisi turu

Kaynak tasarım: `zindan2/tasarim/OYUN-TESTCISI-2026-11.md` (Hymn of Ash deposunda; BAGLAM 171). Dosyalar bu klasörde:
`surucu.js` (açık kalan Chrome oturumu), `personalar.md` (sabit 10 persona). Oyuna özel her şey **profilde** (Hymn: `zindan2/oyun-profil.js`).
Dışarı veri yok: yerel Chrome (ortamdaki Playwright), yerel dosyalar.

## 1. Hazırlık
1. Profili bul: kullanıcı verdiyse o; yoksa sırayla `zindan2/oyun-profil.js`, `oyun-profil.js`, `.oyun-testcisi/profil.js`. Profilin `ad`, `sozluk`, `hedefler`,
   `boylar`, `cikti`, `ilerle` (var mı) alanlarını oku.
2. Oyunu derle (profilde `derle` varsa onu koş; Hymn: `node zindan2/kur.js`).
3. Tur kimliği: `T=$(date -u +%Y%m%d-%H%M)`; çıktı kökü `<profil klasörü>/<profil.cikti>/<T>/` (Hymn: `zindan2/insa/oyuncu/<T>/`, git dışı). Tohum: 7 (ya da kullanıcının verdiği).
4. Seçim: varsayılan 10 persona, iki dalga (1–5, 6–10). Kullanıcı "yalnız 2,4,8" ya da "hepsi birden" dediyse ona uy.
5. İş panosu varsa (Hymn: CLAUDE.md "İŞ PANOSU") bir satır aç: "Oyuncu turu <T>".

## 2. Dalga (her persona bir alt ajan)
Her dalgada personaları **tek mesajda, paralel** Agent çağrılarıyla başlat (`model: "sonnet"`, arka planda). Brif = §4 ortak kurallar + `personalar.md`'deki
o personanın bölümü + profilin `ad`/`sozluk`/`hedefler` + değişkenler: `SURUCU=<bu klasör>/surucu.js`, `PROFIL=<profil yolu>`,
`OTURUM=<T>-p<N>`, `DIZIN=<çıktı kökü>/p<N>-<ad>`, `TOHUM`. Dalganın bütün ajanları bitince (bildirimleri bekle; yoklama yapma) sonraki dalga.
Makine yükü: aynı anda en çok 5 Chrome (persona 4 ve 8 iki oturum açar: sırayla açıp kapatsınlar).

## 3. Sentez (ana oturum)
1. Her `DIZIN/rapor.md`'yi oku. Aynı bulguyu birleştir (kaç persona gördü, hangileri). Önem (1 kritik · 2 önemli · 3 küçük) × sıklık ile sırala.
   "Güzel" bulguları ayrı listede tut. Tek personanın gördüğü ve yeniden üretilmeyen bulguyu "tekil" diye işaretle.
2. Kanıt: her bulguya 1 çekim yolu ve yeniden üretim adımları (persona raporundan).
3. `<çıktı kökü>/RAPOR.md` yaz (git dışı): özet (3–5 satır), öncelik sıralı bulgular, persona özetleri (persona başına 2–3 satır), süre/eylem sayıları.
4. Rapor sayfası (tek kalıcı Artifact; BAGLAM 171): profilde `rapor.artifact` adresi varsa onu GÜNCELLE (önce `Artifact read`), yoksa yeni yayınla ve adresi
   profile yaz. Sayfa: son turun bulguları üstte (tür ve persona süzgeci), önceki turlar "Geçmiş" bölümünde (kısa özet + tarih). Çekimleri gömme
   (16 MB sınırı): en önemli ≤ 12 çekimi küçültüp ekle (`files`), gerisi yolla anılır. Artifact tasarım kurallarına uy (artifact-design skill'i).
5. Kayıt: proje günlüğüne kısa girdi (Hymn: GUNLUK + iş panosu satırı "bitti"); bulgular başka oturumların işiyse (görsel, denge, oyun) kullanıcıya sor,
   onaylarsa o oturumların gelen kutusuna yaz (Hymn: CLAUDE.md GÖNDER kuralı).

## 4. Persona brifinin ortak kuralları (her ajana aynen ver)
- Sen bir **oyuncusun**, geliştirici değil. Oyunu yalnız sürücü komutlarıyla oyna: `node $SURUCU $OTURUM <komut>`. Başka hiçbir yolla sayfaya dokunma;
  oyunun dosyalarını okuma; test kancası kullanma (profilin `yasak` listesi).
- Başla: `node $SURUCU ac $OTURUM --profil $PROFIL --boy <personanın boyu> --tohum $TOHUM --dizin $DIZIN`. Bitir: `node $SURUCU $OTURUM kapat` (her durumda).
- Döngü: `gor` → karar ver (personana göre) → bir eylem (`tik @N`, `dokun @N`, `bas @N 700`, `surukle`, `tus`, `yaz`, `bekle`, `ilerle` yalnız izinliyse) → `gor`.
  Her 6–8 eylemde ya da garip bir şey görünce `cek <kısa-ad>` ve PNG'ye Read ile bak. Eylem bütçesini ve süreyi aşma.
- Hedefi YAZIYLA seçmeyi tercih et: `dokun "~set out"` (yazısı içeren), `tik "=Verse I"` (tam). `@N` numaraları ekran değişince kayar (pilotta yanlış
  düğmeye basıldı); `@N` yalnız aynı yazılı birden çok öğe varsa ve hemen önceki `gor`'dan. Ekran değişmiyorsa 3 denemeden sonra başka bir şey dene ve not et.
- Not tut (`$DIZIN/notlar.md`): kısa zaman damgalı gözlemler. `hatalar` komutunu en az 3 kez ve sonda oku.
- Sonda `$DIZIN/rapor.md` yaz (≤ 40 satır): 1) ne yaptın (5 satır), 2) **bulgular** — her biri tek satır:
  `[tür: hata|anlaşılmıyor|takıldım|güçlü|zayıf|sıkıcı|telefon|erişilebilirlik|güzel] [önem 1–3] ne · nerede · yeniden üretim (kısa) · çekim yolu`,
  3) tek cümle genel his, 4) eylem sayısı ve süre. Kullanıcıya dönen yanıtın yalnız rapor yolunu ve bulgu sayısını içersin.

## 5. Yeni bir oyuna ekleme
Oyun deposuna bu klasörü koy: `git clone --depth 1 https://github.com/hsynmrcnl/play-test.git /tmp/play-test && bash /tmp/play-test/guncelle.sh` (sonra yenilemek: `bash .claude/skills/oyun-testcisi/guncelle.sh`; ortak kaynak `hsynmrcnl/play-test`, BAGLAM 171) ve bir profil yaz:
`ad`, `ac` ({dosya} ya da {url}), `boylar`, `cikti`, `kayitSifirla`, `hazir`, `gozlem` (oyun bilgisi: ekran, para, can…; kısa metin), isteğe bağlı `ilerle`
(zaman atlama), `tohumla`, `derle`, `hedefler`, `sozluk`, `yasak`, `rapor.artifact`. Örnek: Hymn of Ash'in `zindan2/oyun-profil.js`'i.
