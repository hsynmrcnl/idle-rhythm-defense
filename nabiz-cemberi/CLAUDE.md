# Nabız Çemberi — Claude için proje notları

Tek sayfalık, kütüphanesiz bir tarayıcı oyunu: **idle rhythm defense**. Oyuncu 8 yerlik bir ritim sıralayıcıda kendi müziğini kurar; döngüdeki her vuruş hem nota (para) kazandırır hem de sahneye yaklaşan düşmanlara ateş eder. Tek geliştirici: Hüseyin. Cevaplar Türkçe.

## Çalışma kuralları (Hüseyin'in söyledikleri)
- Müzik/oyun fikirlerini **anında uygulama**: önce olur mu diye araştır, kısa bir öneri yaz, onay gelince uygula. Gerekirse önce küçük bir laboratuvar sayfasıyla göster.
- **Word belgesi oluşturma.** Öneri ve raporlar sohbette ya da repo içindeki markdown dosyalarında kalır.
- Elektro gitar oyunda kalır. Solo yapabilen her enstrümanın solosu olur.
- Saz sentez kalır (sesi beğenildi); saz için örnek kayıt arama.
- Akor/dolgu önerisini yeniden görmek isteyebilir: `docs/` içinde yoksa sohbet geçmişinden özetle.
- Kısa, madde madde, "önce sonuç" cevaplar. Uzun açıklamayı o istemeden yazma.

## Dosya düzeni
```
src/            kaynak parçalar; build.py bunları SIRAYLA tek dosyaya yapıştırır
  p1_head.html  işaretleme + CSS (+ <script>(()=>{ açılışı p2'nin başında)
  p2_data.js    veri: enstrümanlar (INS), temalar, ölçüler, gamlar, geliştirmeler (RUP, SOLO_TREE, SUP), akor yürüyüşleri (PROGS), dolgular, DEMOS
  p2b_i18n.js   EN sözlüğü + T() / i18n(): her yeni Türkçe metnin İngilizcesi buraya eklenir
  p3_state.js   durum (S), kayıt/yükleme, hesaplar (recalc, rate, dps), plan, akor, dolgu, solo geni (tickPow, analyzeSolo, soloMerge)
  p4_audio.js   Web Audio sentez: initAudio, GEN üreteçleri, soloVoice/soloPlay, zamanlayıcı (sched), startStop
  p4b_sf.js     örnek ses katmanı: sf/*.json paketleri (FluidR3 GM), sfVoice/sfSolo/sfDrum; yüklenemezse sentez
  p5_combat.js  düşmanlar, dalgalar, onStep (vuruş → nota + hasar), dolgu/geçiş/doruk
  p6_panels.js  paneller (renderPanels), sekmeler, telefon pedleri, öğretici, menajer, turne, demo, tıklama işleyicileri (data-act)
  p7_canvas.js  sahne çizimi (çember/şerit), solo sahnesi (drawSoloStage, sürükleme), WebGL son işlem, boot, window.__nb
sf/             örnek ses paketleri (JSON içinde base64 mp3); tools/build_sf.py üretir
assets/         PWA ikonları
tests/          Playwright testleri (python tests/run_all.py)
tools/          build_sf.py (örnek sesleri yeniden paketleme)
build.py        → dist/ (site + PWA) ve build/artifact.html (claude.ai artifact için iskeletsiz sürüm), build/chk.js
```

## Derleme ve test
```
python build.py                 # dist/ üretir; her değişiklikten sonra
node --check build/chk.js       # söz dizimi
python tests/run_all.py         # pip install playwright && playwright install chromium (bir kez)
python -m http.server -d dist   # yerelde oynamak için (örnek sesler file:// ile yüklenmez)
```
`main`e push → repo kökündeki `.github/workflows/pages.yml` derler ve Pages'e yayınlar: https://hsynmrcnl.github.io/idle-rhythm-defense/

## Kod gelenekleri
- Tek kapalı fonksiyon, `'use strict'`; parçalar birbirinin fonksiyonlarını doğrudan kullanır (hoisting). Yeni parça eklersen `build.py` PARTS sırasına koy.
- Kısa, yoğun satırlar; yorumlar Türkçe. Yeni kullanıcı metinleri Türkçe yazılır ve `p2b_i18n.js`'deki EN sözlüğüne eklenir (tam cümle anahtarı).
- Tıklamalar `data-act` ile `#rack` üzerinde tek dinleyicide; durum `S` içinde, `save()` localStorage'a yazar (`nabiz-cemberi-v3`). `normalizeS()` eski kayıtları taşır: yeni alan eklerken buraya varsayılan koy.
- Sayısal denge: `recalc()` → `rate()`/`dps()`; nota ve hasar çarpanları `planAvg`, `tourM`, `contrastM` gibi fonksiyonlarda. Değiştirince testlerdeki beklenen değerleri kontrol et.
- Testler `window.__nb` hata ayıklama arayüzünü kullanır (p7 sonunda). Yeni özellik için oraya getter/fonksiyon ekle ve `tests/` altına bir Playwright testi yaz.
- Telefon düzeni: `isPhone()` (≤700px) ve canvas'ta `PH()`; her yeni panel iki düzende de denenir (tests/mobile_test.py, tests/mobile_ui_test.py).
- Telefon arayüzü (v13): Sahne tek ekran, kaydırmasız (canvas kalan yüksekliğe göre küçülür); başlık gizli, sağ üstte Ayarlar dişlisi (`#t-set`, sekme `set`). Altta 5 simgeli dock (`.dk`, `DOCK` eşlemesi): Sahne · Stüdyo|Koleksiyon · Savunma · Albüm|Kitap · Görünüm; ikili gruplarda panelin üstünde `.subnav`. Seçili simge kendi `--nc` renginde parlar, diğerleri aynı soluk renkte. Başlat/durdur: halkanın ortasındaki düğme, tek dokunuş (`orbHit`, `drawOrb`, yay `orbK`; durgunken içi arka plan renginde neon ▶, dokununca yaylanarak BPM göbeğine küçülür); telefonda alttaki Başlat yok. Ritme vur: sahnede boş yere dokunmak. Dil, ses, örnek şarkılar, öğretici ve kayıt Ayarlar'da (`renderSet`). Görünüm ayrı sekme kalır, büyüyecek.
- Kartlar (v14): Stüdyo, Koleksiyon ve Savunma bölümleri `section.block.card[data-sec]`; başlıkta `.ht` + ⓘ (`data-act="info"`), açıklama `.info` içinde gizli. Yeni bölüm metni yazarken uzun açıklamayı karta değil ⓘ'ya koy.
- Stüdyo açılma sırası: `GATES`/`SEC_GATE` (p6). Sahne baştan; Uyum+Groove 2. enstrümanla; Ritim stüdyosu en iyi dalga 3; Desen/ölçü/gam dalga 5; Şarkı planı `S.up.sef`; Solo `S.up.solo`. Açılanlar `S.open`'da kalıcı (albüm ve turne `keep` listelerinde), yükleme ve açılışta `secCheck(true)` sessiz açar, oyunda açılınca "Yeni" etiketi + Stüdyo noktası.
- Telefonda sayfa gövdesi kaymaz; sekmeler `#rack` içinde kayar, konumu `scrollMem`'de. Savunma 390×844'te kaydırmasız sığacak şekilde tasarlandı (testte ölçülüyor).
- Ses: her yeni enstrümanın `v` nesnesi bir GEN üretecini seçer; örnek kaydı varsa `p4b_sf.js` SF_PROG/SF_DRUM'a eşle, ses seviyesi SF_GAIN/SF_DGAIN ile dengelenir.

## Sürüm notu
Üst köşedeki etiket `p6_panels.js` içinde (`'v14 · '`); yayınlarken artır. Telefonda Ayarlar'ın en altında görünür.
