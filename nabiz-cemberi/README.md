# Nabız Çemberi

Idle rhythm defense: 8 yerlik bir ritim sıralayıcıda kendi müziğini kur; döngüdeki her vuruş hem nota kazandırır hem de sahneye yaklaşan Sessizlik A.Ş. düşmanlarına ateş eder. 42 enstrüman, akor yürüyüşü, dolgu, sahne devri soloları (teknikler, düet, seyir), albüm ve dünya turnesi, altı tema, Türkçe/İngilizce. Tek sayfa HTML + CSS + JS, kütüphane yok; gerçek enstrüman kayıtları (FluidR3 GM) `sf/` içinde.

**Oyna:** https://hsynmrcnl.github.io/idle-rhythm-defense/ (GitHub Pages açılınca bu adres çalışır)

## Klasörler
| Yol | Ne |
|---|---|
| `src/` | kaynak parçalar; `build.py` bunları tek sayfaya birleştirir (sıra: p1 → p7) |
| `sf/` | örnek ses paketleri (JSON içinde base64 mp3, enstrüman başına bir dosya, toplam ~7 MB) |
| `assets/` | PWA ikonları |
| `tests/` | Playwright testleri (`python tests/run_all.py`) |
| `tools/build_sf.py` | örnek sesleri yeniden paketleme (normalde gerekmez) |
| `docs/` | tasarım notları |
| `../.github/workflows/pages.yml` | (repo kökünde) her `main` push'unda derleyip GitHub Pages'e yayınlar |
| `CLAUDE.md` | Claude (Cowork / Claude Code) için proje notları ve çalışma kuralları |

## Yerelde çalıştırma
```
python build.py                # dist/ üretir (index.html + sw.js + manifest + ikonlar + sf/)
python -m http.server -d dist  # http://localhost:8000  (örnek sesler file:// ile yüklenmez, sunucu gerekir)
```
Derleme Python 3.9+ ister, başka bir şey istemez. Söz dizimi kontrolü: `node --check build/chk.js`.

## Testler
```
pip install playwright
playwright install chromium
python build.py && python tests/run_all.py
```
Her takım kendi başına da çalışır: `python tests/v7_test.py`. Ekran görüntüleri `tests/out/` içine düşer.

## Yayınlama
- **GitHub Pages:** Settings → Pages → Source: *GitHub Actions*. Sonra her `main` push'u otomatik yayınlanır (Actions sekmesinde "Yayınla" işi).
- **itch.io / Netlify / herhangi statik sunucu:** `python build.py --zip` → `nabiz-cemberi-site.zip`; `index.html` açılış dosyası. HTTPS gerekir (PWA ve service worker için).
- **Telefona kurulum (PWA):** HTTPS'ten açınca "Ana ekrana ekle"; ilk ziyaretten sonra çevrimdışı da açılır, örnek sesler önbelleğe alınır.
- **claude.ai artifact:** `build/artifact.html` iskeletsiz sürümdür; `sf/` klasörü artifact dosyası olarak yanında yayınlanır.

## Kayıt
Kayıt tarayıcıda `localStorage` içinde durur (`nabiz-cemberi-v3`). Ayarlar'daki (sağ üstteki dişli) "Kodu üret ve kopyala" ile başka cihaza taşınır.

## Lisanslar
Üçüncü taraf bileşenler `LICENSES.md` içinde (FluidR3 GM ve WebAudioFont: MIT; yazı tipleri: OFL). Oyunun kendi lisansı için kök dizine `LICENSE` ekle.
