# Yapılacaklar (sosyal olmayanlar)

Oyun değerlendirmesinden çıkan liste. Paylaşma, sıralama ve başkalarının şarkıları kapsam dışı.

## 1. grup: hızlı kazanç — v16'da yapıldı
- [x] İnce tempo: ±1 BPM, satın alınan üst sınır içinde
- [x] Çarpan dökümü: istatistik çubuğuna dokun → Analiz
- [x] Geri al: desen, plan, akor, solo, ölçü, gam (30 adım; bedel birebir iade/tahsil)
- [x] Vuruş geri bildirimi: hasar sayıları, düşende +♪ (Görünüm'den kapatılır)
- [x] "Ne yapmalıyım": Analiz'de gelir ve savunma için sıradaki en verimli satın alma, tek dokunuşla al

## 2. grup: yapımcı araçları
- [ ] MIDI dışa aktarma (.mid): desen + plan + akor + solo — orta
- [ ] WAV kaydı: çalarken ana çıkış kaydı (gerçek zamanlı) — orta
- [ ] Reverb (oda/salon) gönderimi — küçük
- [ ] Basit mikser: enstrüman başına ses + pan (ses yolu değişir) — orta-büyük

## 3. grup: müzik içeriği (önce laboratuvar sayfasında dinle)
- [ ] Komalı Hicaz/Kürdi akordu (53-TET) — küçük-orta
- [ ] Zengin armoni: 7'li, sus, çevrim, yürüyen bas — orta
- [ ] 12/8 shuffle ölçüsü — küçük
- [ ] Hayalet nota (hafif vuruş) — orta

## 4. grup: oyun dengesi (önce ölçüm)
- [ ] Ekonomi simülasyonu (hızlı ileri sarma botu) — orta
- [ ] Kaybetme gerilimi — tasarım kararı Hüseyin'de
- [ ] Aktif savunma (odak hedefi / beceri) — tasarım kararı Hüseyin'de
- [ ] Idle–aktif denge — simülasyondan sonra

## Şimdilik yapılamaz
- Ney, zurna, tabla, gamelan, taiko için kaliteli kayıt: CC0 kaynak yok. Seçenek: sentezleri laboratuvarda iyileştirmek.

## v16 sırasında bulunan tutarsızlıklar (karar bekliyor)
- Görünüm → Sahne katmanları: metin "her biri gelire ×1,1 ekler" diyor, kodda böyle bir çarpan yok (`globalM` içinde sahne katmanı yok). Ya metin düzelir ya çarpan eklenir.
- Kuşatma bilgisi ve öğretici: "Nabız sıfırlanırsa dalga 5 geri gider" diyor, kod dalgayı %20 geri çekiyor (`retreat`: dalga × 0,8; dalga 10 → 8, dalga 50 → 40).
