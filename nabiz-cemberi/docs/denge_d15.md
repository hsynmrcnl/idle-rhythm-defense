# Dalga 15 duvarı — öneri (karar Hüseyin'de)

## Ne görüldü (oyuncu turu 20261109-1945)
- İlerleme takipçisi: dalga 15'te ~10 oyun-dakika takıldı; nabız %30 ↔ %100 salınım, geri çekilmeler; ♪24 Bin harcanmadan birikti. Oyun harcamaya yönlendirmedi.
- Idle: 900 oyun-sn beklemede dalga 18 → 17; "ne yapmalıyım" ipucu yok, menajer önerisi yok.
- Build meraklısı: savunma pahalı ve gereksiz hissediyor (dalga 10'a kadar nabız hiç düşmedi).
- Aceleci: tersine oyunu fazla kolay buldu (Atla + Yoğun + bekleme ile dalga 20).
- Bot simülasyonu (otomatik geliştirme açık, `docs/ekonomi_sim.md`): duraksama yok, dalga 15'e ~7. dakikada varıyor.

**Sonuç:** sayılar tek başına sorun değil (harcayan oyuncu geçiyor); sorun **harcamayan oyuncunun yönlendirilmemesi** ve otomasyonun ancak 1. albümden sonra gelmesi.

## Seçenekler
1. **Harcama ipucu (önerilen, küçük):** nota birikip ilerleme durunca (en iyi dalga 2 dk değişmedi ya da geri çekilme oldu, elde en ucuz önerinin ≥3 katı nota var) üst bilgide parlayan bir öneri çipi: "Öneri: Hasar +1 · ♪1.500". Dokununca alır. Öneri Analiz'in sıralamasından (`anlRank`), nabız düşükse savunmadan (`defRec`). Kolay ve Detaylı'da aynı.
2. **Erken asistan (orta):** dalga 15'te ücretsiz "Asistan: otomatik geliştir" — yalnız ucuz geliştirmeler, harcama sınırı %25, Otomatik kartında anahtar. Menajer gelince tam sürüme döner. Idle oyuncunun duvarını kaldırır.
3. **Sayı ayarı (büyük, en son):** dalga 12–20 arası düşman can artışını (×1,19/dalga) biraz yumuşatmak ya da savunma maliyet artışını (×1,8/sv) ×1,6'ya çekmek. Aceleci'nin "fazla kolay" gözlemiyle çelişir; 1 ve 2'den sonra ölçülerek karar verilmeli.

## Ölçüm planı
- Ekonomi botuna "harcamayan oyuncu" kipi: yalnız ilk 3 dakika elle alır, sonra bekler. 1 ve 2'nin dalga 15–20 süresine etkisini dakika dakika ölç.
- Sonra ikinci oyuncu turu (yalnız Idle, İlerleme, Acemi personaları) ile doğrula.

## Ölçüm 1 — harcama ipucu (v48, `tools/harcamayan_sim.py 30`)
İlk 3 dk menajer mantığıyla harcar, sonra A) hiç harcamaz, B) yalnız öneri çipine dokunur (ilerleme 2 dk durunca ya da geri çekilmeden sonra).

| dk | A: dalga (en iyi) | A: nota | A: geri | B: dalga (en iyi) | B: nota | B: geri | B: öneri alımı |
|---|---|---|---|---|---|---|---|
| 10 | 19 (19) | 51,1 B | 0 | 19 (19) | 50,9 B | 0 | 0 |
| 15 | 18 (20) | 94,0 B | 3 | 25 (25) | 230,0 B | 1 | 39 |
| 20 | 20 (20) | 136,4 B | 5 | 30 (31) | 846,8 B | 3 | 56 |
| 30 | 20 (20) | 221,3 B | 11 | 31 (32) | 2,5 Mn | 11 | 71 |

Sonuç: harcamayan oyuncu dalga 20'de duvara takılıyor (♪221 B kullanılmadan duruyor); yalnız öneriye dokunan dalga 32'ye çıkıyor. B'de de 25. dakikadan sonra ilerleme yavaşlıyor → seçenek 2 (asistan) o boşluğu doldurmalı.

## Ölçüm 2 — Asistan (v49, `tools/harcamayan_sim.py 30`)
İlk 3 dk aynı; sonra A) hiç harcamaz, B) yalnız öneri çipine dokunur, C) hiç dokunmaz, Asistan açık (dalga 15'ten sonra 20 sn'de bir, notanın en çok %25'i).

| dk | A: dalga (en iyi) | A: geri | B: dalga (en iyi) | B: geri | B: öneri alımı | C: dalga (en iyi) | C: nota | C: geri |
|---|---|---|---|---|---|---|---|---|
| 10 | 19 (19) | 0 | 22 (22) | 0 | 0 | 19 (19) | 60,6 B | 0 |
| 15 | 20 (20) | 2 | 28 (28) | 1 | 82 | 24 (25) | 168,2 B | 1 |
| 20 | 18 (20) | 6 | 35 (36) | 2 | 129 | 27 (28) | 342,0 B | 3 |
| 30 | 20 (20) | 11 | 42 (42) | 7 | 179 | 33 (34) | 486,9 B | 7 |

Sonuç: hiçbir şeye dokunmayan oyuncu da Asistan'la dalga 20 duvarını geçiyor (30. dk'da 34). Öneriye dokunan hâlâ daha hızlı (%25 sınırı yok) — etkileşim ödüllendiriliyor. Not: koşular arası oynaklık büyük (B bu koşuda 42, Ölçüm 1'de 32; ilk 3 dk bile farklı), sonuçlar yön gösterir, kesin sayı değil.

**Seçenek 3 (sayı ayarı):** 1 ve 2 birlikte harcamayan/az etkileşen oyuncunun duvarını kaldırdı; Aceleci'nin "fazla kolay" gözlemiyle çelişmemek için şimdilik sayılara dokunmamayı öneriyorum. İkinci oyuncu turunda (Idle, İlerleme, Acemi) yeniden bakılmalı.
