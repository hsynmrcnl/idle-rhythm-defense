# itch.io yükleme ve sayfa düzeni

## 1. Paketi üret
```
python build.py && python tools/itch_paketi.py
→ build/nabiz-cemberi-itch.zip   (içinde index.html en üstte, sf/, ikonlar)
```
Bu paket oyun kodunu **terser** ile küçültüp değişken/fonksiyon adlarını bozar ve yorumları siler.
Tek `index.html` (CSS + JS gömülü) + `sf/` ses paketleri.

## 2. Kopyalanamazlık — gerçekçi sınır
Tarayıcı oyununun kodu çalışması için istemciye iner; **tam kopyalanamaz yapılamaz.** Yapılan:
- Kod okunmaz (küçültülmüş + adlar bozulmuş + yorumsuz).
- itch.io'da **indirme sunulmaz**, yalnız tarayıcıda oynanır (dosya indirtilmez).
- Sonuç: kaynağı yalnız geliştirici araçlarıyla ve okunmaz hâliyle görebilirler; kolayca alıp düzenleyemezler.
İleride daha güçlü istersen: lisans/telif notu (eklendi, banner), ve kritik dengeyi sunucuya taşımak (bu oyun tek sayfa, sunucusuz; gerekmez).

## 3. itch.io yükleme ayarları
- **Uploads:** `nabiz-cemberi-itch.zip` → “This file will be played in the browser” işaretle.
- **Kind of project:** HTML.
- **Embed options:** Manually set size yerine **Fullscreen butonu açık** + **Mobile friendly** açık (oyun duyarlı; her boyda çalışır). Viewport örn. 960×600 ver, “Automatically start” kapalı.
- **Orientation:** Default (hem dikey hem yatay destekli).
- **Download:** Kapalı — yalnız “Play in browser”. (Kodun indirilmemesi için önemli.)
- **Pricing:** Free / “No payments” ya da bağış (isteğe bağlı).
- **Genre:** Rhythm; **Tags:** idle, rhythm, music, tower-defense, incremental, minimalist, neon, turkish.
- **Community:** Comments açık.

## 4. Mağaza sayfası metni (kopyala-yapıştır)

**Başlık:** Nabız Çemberi
**Kısa açıklama (tagline):** Kendi müziğini kur; her vuruş hem para hem silah.

> Sessizlik A.Ş. şehri susturmaya geliyor. Tek savunman bir ritim.
>
> Çemberdeki hücrelere vuruş koy: döngün döndükçe her vuruş hem **nota (para)** kazandırır hem de sahneye yürüyen susturuculara **ateş eder**. Kurduğun ritim ne kadar iyiyse savunman o kadar güçlü — müzik ile oyun aynı şey.
>
> **Ne var:**
> - 42 enstrüman, roller ve uyum çarpanları — ister elle kur, ister “Otomatik ritim”e bırak
> - Dalgalar, patronlar ve 5 dalgada bir gelen **baskınlar**
> - **Albüm** çıkar: oyun baştan başlar ama hayranlar kalıcı; her şey hızlanır
> - Kalıp kitabı, solo editörü, ses masası, şarkı paylaşma
> - Altı tema (neon, siberpunk, lo-fi, synthwave, Anadolu psikedelik, **Cep LCD**), 2D/3D sahne
> - Telefon, tablet ve masaüstü — klavyeyle de tam oynanır
>
> Arkada açık bırak, ara sıra bak: döngün sen yokken de çalar.

**Alt not (sayfanın dibine):** © Hüseyin. İzinsiz kopyalanamaz / dağıtılamaz.

## 5. itch tema renkleri (Edit theme → kutulara yapıştır)
Oyunun neon temasıyla uyumlu:
- Background: `#07060f`
- Text: `#ece9ff`
- Link: `#3ff2d2`
- Link hover: `#ff3fb4`
- Button background: `#3ff2d2`  · Button text: `#03201b`
- (İsteğe bağlı) sayfa arka planı için koyu düz renk, “Dark” tema tabanı.

Kapak görseli (630×500) ve ekran görüntüleri için oyunun mevcut çekimleri kullanılabilir;
sayfa düzeninin önizlemesi ayrı bir mockup olarak hazırlandı.
