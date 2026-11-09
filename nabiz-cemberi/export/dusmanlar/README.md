# Nabız Çemberi — geometrik neon düşmanlar

Sekiz düşman, her biri içi dolu bir geometrik cisim: döner, vuruşa göre zıplar, neon ışır, ölünce üçgen parçalara ayrılıp dağılır. Görseller kodla çizilir; aynı veri üç biçimde var.

| id | ad | cisim | renk | dönüş hızı |
|---|---|---|---|---|
| memur | Memur | küp | #3ff2d2 | 1.1 |
| kurye | Kurye | dörtyüzlü | #ffb054 | 2.2 |
| stajyer | Stajyer | sekizyüzlü | #5ab0ff | 1.6 |
| avukat | Avukat | üçgen prizma | #b98bff | 0.9 |
| sansurcu | Sansürcü | yirmiyüzlü | #ff3fb4 | 1.1 |
| denetci | Denetçi | onikiyüzlü | #ffd166 | 0.7 |
| mudur | Müdür (boss) | yıldız | #ff5468 | 0.8 |
| ceo | CEO (boss) | elmas | #ff8ff0 | 0.6 |

## Dosyalar
- `geo_enemies.py` — Python, bağımlılık yok. `polygons(kind, x, y, size, t, beat=0)` görünen yüzleri arkadan öne `(noktalar, (r,g,b))` olarak verir; `burst(...)` + `step_burst(parts, dt)` ölüm parçaları. `python geo_enemies.py` pygame ile sekizini döndürür (tıkla: patlat).
- `geo_enemies.js` — tarayıcı/Node, bağımlılık yok. `GeoEnemies.draw(ctx, kind, x, y, size, t, {beat, flash, glow})`, `burst`, `drawBurst`.
- `geo_enemies.json` — ham veri: köşeler (birim küre), yüzler (sıralı köşe indisleri + dış normal), ışık yönü, renk, dönüş hızı. Başka bir dil/motor için.
- `png/` — şeffaf arka planlı hazır kareler (motorlar için):
  - `<id>.png` — 256×256 tek görsel
  - `<id>_donus_32kare_128px.png` — 8×4 ızgara, 32 kare, 128 px; tek eksende tam tur, kusursuz döngü
  - `<id>_patlama_12kare_128px.png` — 6×2 ızgara, 12 kare; ilk kare beyaz parlama, sonra parçalar dağılır
- `onizleme.png` — hepsi bir arada.

## Çizim kuralı (kendi motorunda yeniden yazmak istersen)
1. Dönüş matrisi `M = Rx(0.5) · Ry(t·spin) · Rz(0.6·t·spin)` (sprite'larda Rz = 0).
2. Köşeleri döndür, `size` ile ölçekle, ekrana koy (z atılır). Zıplama: `size × (1 + 0.18·sin(π·beat))`.
3. Normali döndür; `n.z > 0` olan yüzler görünür. Ortalama z'ye göre arkadan öne sırala.
4. Renk: `renk × (0.62 + 0.7·max(0, n·ışık))`, ışık `[-0.45, 0.55, 0.75]` (normalize). İnce beyaz kenar çizgisi.
5. Işıma: merkezde `2.3·size` yarıçaplı, rengin %42'sinden saydama inen radyal leke (toplamalı karışım).
