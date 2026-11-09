# Zorunlu öğretici planı (taslak)

Amaç: yeni oyuncu ilk 3–4 dakikada oyunun çekirdeğini **eliyle yaparak** öğrensin; yanlış yere dokunup kaybolmasın. Bugünkü öğretici 3 adım ve serbest (kart + vurgu, “Anladım” ile geçilebiliyor); aşamalı açılış kartları da serbest.

## İşleyiş
- **Spot ışığı katmanı** (`#tutLayer`): ekranın tamamı %60 karartılır, yalnız hedef öğe aydınlık kalır (delik + nabız gibi atan halka + parmak/ok simgesi). Konuşma balonu hedefin yanında, ekrana sığacak tarafta.
- **Tıklama zorunluluğu:** hedefin dışındaki her dokunuş, tuş ve kaydırma engellenir (document üzerinde yakalama evresinde). Yanlış yere dokununca hedef bir kez sallanır, balon “Buraya dokun” der.
- **Tuval hedefleri:** halkadaki hücre ve ortadaki ▶ için delik tuvalin üstünde hesaplanır (`cellPos`, `orbAt` → sayfa koordinatı); 2D ve 3D'de çalışır.
- **İlerleme eyleme bağlı:** adım ancak istenen iş yapılınca geçer (hücre dolar, müzik başlar, seviye artar…). Yalnız bilgi adımlarında “Devam” düğmesi var.
- **Oyun öğreticiye göre akar:** öğretici dalgasında tek, yavaş düşman; satın alma adımlarından önce yetecek kadar nota verilir; düşmanlar adım beklerken durur.
- **Dayanıklılık:** hedef başka sekmedeyse önce o sekmeye götüren adım gelir; ekran döner ya da boyut değişirse delik yeniden hesaplanır; sayfa yenilenirse kaldığı adımdan sürer (`S.tut.s`).
- **Atla:** karar senin (aşağıda).

## Adımlar (telefon ve masaüstü aynı sıra)
**A · İlk ses**
1. Karşılama balonu, tek düğme “Başla” (ses izni için gereken ilk dokunuş).
2. Halkada parlayan 1. hücreye dokun → davul vuruşu duyulur.
3. 5., 9. ve 13. hücreler sırayla parlar → dörtlük ritim kurulur.
4. Ortadaki ▶'ye dokun → müzik başlar, ibre döner.
5. Üstteki nota sayısı aydınlanır: “Her vuruş nota kazandırır.” (Devam)

**B · İlk savaş**
6. Tek yavaş Memur gelir: “Vuruşların düşmana ateş eder.” Düşünce kendiliğinden geçer.
7. Ritme vur: “İbre vuruşun üstündeyken sahneye dokun.” Bir kez tutturmak yeter (pencere normalin iki katı).

**C · Geliştirme**
8. Alttaki Stüdyo simgesine dokun.
9. Davul'un Yükselt düğmesine dokun.
10. Yoğun'a dokun → ritim kendiliğinden yazılır.

**D · İkinci enstrüman**
11. Koleksiyon'a dokun → Trampet'in Aç düğmesine dokun.
12. Stüdyo'da Hepsini düzenle'ye dokun → uyum çarpanı görünür.
13. Sahne'ye dön: “Artık sende. Yeni bölümler açıldıkça kısa kartlar gelir.” → Oyna.

Sonrası bugünkü gibi: açılış kartları (Savunma, Tempo…) serbest kalır ama aynı spot ışığıyla, karartmasız gösterilir.

## Teknik
- `TUT2` dizisi: `{id, hedef: ()=>seçici | tuval dikdörtgeni, tür: 'dokun'|'otomatik'|'devam', koşul, hazırla: ()=>{sekme, nota, dalga}, metin, telefon metni}`.
- Yeni: `tutLayer` (delik, halka, balon), `tutRect()` (DOM ya da tuval hedefi), yakalama evresinde engelleyici, öğretici dalgası (`startWave` özel içerik).
- Mevcut `TUT`/`curCard`/`tutShow` yerine geçer; `UNLK` kartları aynı katmanı karartmasız kullanır.
- “Öğreticiyi yeniden başlat” (Ayarlar): kaydı bozmamak için örnek şarkı gibi geçici bir kopya üzerinde çalışır, bitince kendi oyununa döner.
- Test: her adım için “dışarı dokununca ilerlemiyor, hedefe dokununca ilerliyor”; telefon, masaüstü, 3D, EN; yenileyince kaldığı adımdan sürüyor.

## Kararlar (Hüseyin)
1. Atla: hiç yok · 4. adımdan sonra küçük “Atla” · yalnız Ayarlar'dan.
2. Uzunluk: 13 adım (~3 dk) uygun mu, kısaltılsın mı?
3. Önce laboratuvarda spot ışığı ve ilk 5 adım gösterilsin mi?
