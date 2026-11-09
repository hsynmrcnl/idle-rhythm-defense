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
