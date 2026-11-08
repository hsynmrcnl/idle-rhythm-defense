# Ekonomi simülasyonu

Yeni oyun, Kolay, otomatik müzik açık. Bot her 10 sn'de Analiz önerisiyle (autoBuyPick, harcama sınırı %90) en fazla iki şey alır, boş yere en ucuz açık enstrümanı koyar. Süre oyun içi dakika; hızlı ileri sarma (ffSim). Araç: `tools/ekonomi_sim.py 60`.

## Şarj ve patlama açık (3D geliştirmesi var)

| dk | dalga (en iyi) | nota/sn | hasar/sn | enstrüman | toplam seviye | geri çekilme | patlama | vurgulu adım |
|---|---|---|---|---|---|---|---|---|
| 1 | 3 (3) | 11 | 16 | 1/4 | 11 | 0 | 0 | 0 |
| 2 | 5 (5) | 23 | 28 | 1/4 | 17 | 0 | 0 | 0 |
| 5 | 11 (11) | 515 | 535 | 4/4 | 42 | 0 | 0 | 0 |
| 10 | 23 (23) | 2,9 B | 3,5 B | 5/5 | 94 | 0 | 0 | 0 |
| 15 | 34 (34) | 13,4 B | 12,5 B | 7/7 | 132 | 0 | 0 | 1 |
| 20 | 45 (45) | 45,6 B | 31,2 B | 7/7 | 188 | 0 | 3 | 1 |
| 30 | 53 (55) | 100,9 B | 78,6 B | 7/7 | 292 | 4 | 10 | 1 |
| 45 | 61 (61) | 193,1 B | 172,5 B | 9/9 | 346 | 13 | 24 | 2 |
| 60 | 64 (64) | 201,1 B | 216,3 B | 9/9 | 346 | 25 | 44 | 2 |

## Şarj kapalı

| dk | dalga (en iyi) | nota/sn | hasar/sn | enstrüman | toplam seviye | geri çekilme | patlama | vurgulu adım |
|---|---|---|---|---|---|---|---|---|
| 1 | 3 (3) | 11 | 16 | 1/4 | 11 | 0 | 0 | 0 |
| 2 | 5 (5) | 23 | 28 | 1/4 | 17 | 0 | 0 | 0 |
| 5 | 11 (11) | 541 | 535 | 4/4 | 42 | 0 | 0 | 0 |
| 10 | 23 (23) | 3,1 B | 3,5 B | 5/5 | 94 | 0 | 0 | 0 |
| 15 | 34 (34) | 18,1 B | 13,0 B | 7/7 | 136 | 0 | 0 | 1 |
| 20 | 45 (45) | 49,4 B | 32,0 B | 7/7 | 193 | 0 | 0 | 1 |
| 30 | 54 (54) | 108,8 B | 79,7 B | 7/7 | 295 | 3 | 0 | 1 |
| 45 | 58 (59) | 194,4 B | 172,5 B | 9/9 | 346 | 13 | 0 | 2 |
| 60 | 60 (61) | 200,0 B | 216,3 B | 9/9 | 346 | 25 | 0 | 2 |

Sayfa hatası: yok · ölçüm 19 sn

## v35 kararları ve sonrası
- Otomatik desen, Darbe rolündeki vuruş enstrümanının (ör. davul) ölçü başını vurgulu yazar. Şarj artık kendiliğinden doluyor: 60 dakikada 44 patlama, dakikada yaklaşık bir; en iyi dalga 61'den 64'e çıktı.
- Otomatik geliştirme, bütün yerler doluyken ve yeni yer önerilen geliştirmenin üç katından ucuzsa sahneye yer açar. 45. dakikada 9 yer dolu; dakika 30'da gelir iki katı (100 B'ye karşı 74 B).
- Duvar dalga ~50'den ~60'a kaydı. Tıkanma şimdi 45. dakikada (toplam seviye 346): bütün yerler dolu, seviyeler sınırda. Bundan sonrası albüm (yeni dönem) kararı, bot albüm çıkarmıyor.
