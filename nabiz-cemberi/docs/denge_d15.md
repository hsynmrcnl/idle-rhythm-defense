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

## Ölçüm 3 — orta oyunda tehdit (v57, `tools/tehdit_olc.py`)
Sıradan oyuncu modeli: dalga 15'e kadar 10 sn'de bir en verimli geliştirme (notanın en çok yarısı), sonra yalnız Asistan. 2 sn'lik adımlarla dalga dalga en düşük nabız ve geri çekilme.

- Dalga 1–29: her koşuda nabız %100, geri çekilme 0; dalga başına ~24–30 sn (düşman doğma süresi belirliyor, oyuncu hep fazlasıyla güçlü). İlk ~12,5 dakika tehdit yok.
- Sonrası koşudan koşuya çok değişiyor: bir koşuda dalga 30'dan itibaren her dalgada bir geri çekilme (30 dk'da dalga 47, 19 geri çekilme); iki başka koşuda 16. dakikada dalga 38'e kadar hâlâ %100 ve 0 geri çekilme.
- Denenen tek ayar: Denetçi (10'luk dalga patronu) canı 14 → 40 ve 70. Dalga 10/20/30'da nabız yine %100; tek başına patron canı gerilim yaratmıyor.

Sonuç: tehdit ikili (ya hiç yok ya duvar); düşman can artışını (×1,19) oynatmak yalnız duvarın yerini kaydırır, arada “nabız düşüp toparlanan” bir bant oluşturmaz. Bu bir sayı ayarı değil tasarım kararı (ör. sızıntı hasarını küçültüp sızıntıyı sıklaştırmak, patronların yanında koruma dalgası, dalga içi “baskın” anları). Karar Hüseyin'de; sayılar değiştirilmedi.

## Ölçüm 4 — Baskın (v58, `tools/tehdit_olc.py 14`)
Her 5 dalgada (patron dalgası hariç) tek koldan kurye akını; toplam canı oyuncunun `RAID_T` saniyelik hasarı kadar. Sızan akıncı nabzın %6'sını alır, geri çekilme olmaz.

| RAID_T | dalga 5 | dalga 15 | dalga 25* | geri çekilme (14 dk) | en iyi dalga |
|---|---|---|---|---|---|
| 5, 10, 16 | %100 | %100 | %100 | 0 | 33 |
| **24 (seçilen)** | %94 | %52 | %70 | 0 | 33 |

\* Dalga 25 patron (Müdür) dalgası, baskın yok; %70 dalga 15'teki baskından kalan nabızdı (nabız kendiliğinden dolmuyor). Bunun üzerine baskının aldığı nabız dalga bitince geri veriliyor. İlerleme hızı değişmedi (14 dk'da yine dalga 33).

## Ölçüm 5 — ilk albüme varış (v61, `tools/album_olc.py 60`)
Aynı sıradan oyuncu modeli. Albüm eşiği ♪15 Mn (dönem kazancı); Albüm sekmesi eşiğin yarısında açılır.

| dk | en iyi dalga | dönem kazancı | eşiğe oran |
|---|---|---|---|
| 10 | 22 | ♪660 B | %4 |
| 15 | 35 | ♪3,8 Mn | %25 |
| 20 | 44 | ♪13,8 Mn | %92 |
| 25 | 45 | ♪29,9 Mn | %199 |
| 40 | 45 | ♪131 Mn | %877 |
| 60 | 53 | ♪261 Mn | %1737 |

- Albüm sekmesi 17,7. dk'da açılıyor, ilk albüm 20,4. dk'da çıkarılabiliyor; bu model dalga 45 duvarına da aynı anda (~22. dk) varıyor: albüm duvarın çözümü olarak doğru yerde.
- Model hızlı oyuncu (düzenli harcıyor). Oyuncu turunda İlerleme takipçisi 25. dk'da dalga 23'teydi ve Albüm sekmesini görmedi; daha yavaş oyuncuda ilk albüm muhtemelen 30–40. dk.
- Eşik değiştirilmedi. Risk: duvarda bekleyen oyuncu albümü bilmiyor (sekme ancak eşiğin yarısında açılıyor, öneri çipi albüm önermiyor).

## Ölçüm 6 · Albüm sonrası toparlanma (`tools/toparlanma_olc.py`, v67)

Oyuncu turu 20261112-0404'te İlerleme takipçisi albümden sonra 300 oyun-sn'de dalga 6'daydı (ilk koşuda aynı sürede 11). Model (album_olc ile aynı): ilk albüm 18,2. dk, +10 hayran.

| dk | 1. koşu dalga | gelir/sn | albüm sonrası dalga | gelir/sn |
|---|---|---|---|---|
| 1 | 3 | 6 | 3 | 6 |
| 3 | 6 | 52 | 6 | 101 |
| 5 | 11 | 287 | 11 | 743 |
| 8 | 17 | 1,5 B | 18 | 5,0 B |
| 10 | 22 | 2,6 B | 24 | 7,8 B |
| 12 | 28 | 5,3 B | 29 | 17,9 B |

- Gelir albümden sonra 2–3 kat, ama **dalga hızı aynı**: dalgalar zamanla ilerliyor (≈2,3 dalga/dk), güç fazlası dalgayı hızlandırmıyor. Oyuncu albümden sonra aynı 20 dakikayı yeniden yürüyor; "toparlanma yavaş" hissi bundan.
- Oyuncu turundaki dalga 6 / 11 farkı modelde yok (modelde iki koşu aynı hızda); oradaki fark büyük olasılıkla oyuncunun elle oynaması ve `ilerle` kullanımı.
