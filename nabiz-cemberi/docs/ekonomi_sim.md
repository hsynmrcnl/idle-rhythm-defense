# Ekonomi simülasyonu

Yeni oyun, Kolay, otomatik müzik açık. Bot her 10 sn'de Analiz önerisiyle (autoBuyPick, harcama sınırı %90) en fazla iki şey alır, boş yere en ucuz açık enstrümanı koyar. Süre oyun içi dakika; hızlı ileri sarma (ffSim). Araç: `tools/ekonomi_sim.py 60`.

## Şarj ve patlama açık (3D geliştirmesi var)

| dk | dalga (en iyi) | nota/sn | hasar/sn | enstrüman | toplam seviye | geri çekilme | patlama | vurgulu adım |
|---|---|---|---|---|---|---|---|---|
| 1 | 3 (3) | 11 | 16 | 1/4 | 11 | 0 | 0 | 0 |
| 2 | 5 (5) | 23 | 28 | 1/4 | 17 | 0 | 0 | 0 |
| 5 | 11 (11) | 548 | 690 | 4/4 | 41 | 0 | 0 | 0 |
| 10 | 23 (23) | 4,5 B | 5,0 B | 4/4 | 94 | 0 | 0 | 0 |
| 15 | 34 (34) | 14,5 B | 8,6 B | 4/4 | 135 | 0 | 0 | 0 |
| 20 | 44 (44) | 34,4 B | 19,3 B | 4/4 | 172 | 0 | 0 | 0 |
| 30 | 48 (48) | 74,2 B | 34,5 B | 4/4 | 228 | 7 | 0 | 0 |
| 45 | 50 (50) | 94,3 B | 60,9 B | 4/4 | 243 | 19 | 0 | 0 |
| 60 | 52 (53) | 97,4 B | 76,4 B | 4/4 | 243 | 30 | 0 | 0 |

## Şarj kapalı

| dk | dalga (en iyi) | nota/sn | hasar/sn | enstrüman | toplam seviye | geri çekilme | patlama | vurgulu adım |
|---|---|---|---|---|---|---|---|---|
| 1 | 3 (3) | 11 | 16 | 1/4 | 11 | 0 | 0 | 0 |
| 2 | 5 (5) | 23 | 28 | 1/4 | 17 | 0 | 0 | 0 |
| 5 | 11 (11) | 541 | 535 | 4/4 | 42 | 0 | 0 | 0 |
| 10 | 23 (23) | 3,0 B | 3,7 B | 4/4 | 93 | 0 | 0 | 0 |
| 15 | 34 (34) | 11,9 B | 8,1 B | 4/4 | 127 | 0 | 0 | 0 |
| 20 | 44 (44) | 28,0 B | 18,1 B | 4/4 | 160 | 0 | 0 | 0 |
| 30 | 46 (48) | 60,5 B | 33,9 B | 4/4 | 221 | 8 | 0 | 0 |
| 45 | 48 (48) | 79,8 B | 54,4 B | 4/4 | 243 | 21 | 0 | 0 |
| 60 | 53 (53) | 86,5 B | 68,2 B | 4/4 | 243 | 31 | 0 | 0 |

Sayfa hatası: yok · ölçüm 14 sn

## Bulgular (60 dk)
- **Şarj hiç dolmuyor:** Otomatik desenlerde (Kolay, Hepsini düzenle, menajerin koyduğu enstrümanlar) hiç vurgulu adım yok, Alan rolündeki enstrümanlar da ucuz değil. Patlama 60 dakikada 0 kez oldu; iki koşu aynı. Oyuncu elle vurgu koymadıkça özellik görünmüyor.
- **Hızlı başlangıç:** 5. dk dalga 11, 10. dk dalga 23, 20. dk dalga 44. İlk 20 dakikada hiç geri çekilme yok.
- **Duvar dalga 48–53'te:** 30. dakikadan sonra dakikada yaklaşık bir geri çekilme; 60. dakikada en iyi dalga 53. Dalga 50 CEO dalgası.
- **Satın alma 45. dakikada tıkanıyor:** Toplam seviye 243'te donuyor. Bot sahne yeri (5.–8. yer) almıyor; otomatik geliştirmede yer açma yok, enstrüman sayısı 4'te kalıyor.
