/* oyun-profil.js — Nabız Çemberi için oyun testçisi profili (skill: .claude/skills/oyun-testcisi, kaynak hsynmrcnl/play-test).
   Sürücü oyundan bağımsız; oyuna özel her şey burada. Önce derle: python3 nabiz-cemberi/build.py (→ nabiz-cemberi/dist/index.html).
   file:// ile açılır: örnek ses paketleri yüklenmez, oyun sentezle çalar (oynanış aynı). */
module.exports = {
  ad: "Nabız Çemberi",
  ac: { dosya: "nabiz-cemberi/dist/index.html" },          /* bu dosyaya göre yol */
  boylar: { masaustu: "1366x768", telefon: "390x844m", yatay: "844x390m" },
  cikti: "nabiz-cemberi/build/oyuncu",                     /* git dışı (build/ yok sayılır) */
  derle: "python3 nabiz-cemberi/build.py",                 /* depo kökünden */
  rapor: { artifact: null },                               /* tek kalıcı rapor sayfası (ilk turda yazılır) */
  kayitSifirla: "localStorage.clear()",                    /* her persona yeni oyuncu olarak başlar (zorunlu öğreticiyle) */
  hazir: "() => !!window.__nb && document.readyState === 'complete'",
  /* oyun bilgisi (gözlemin OYUN satırı): sekme, nota, dalga, nabız, çalıyor mu, öğretici adımı, son mesaj */
  gozlem: `(() => {
    const nb = window.__nb; if (!nb) return 'yükleniyor';
    const S = nb.S, p = [];
    p.push('sekme ' + (document.getElementById('app') || {}).dataset?.tab);
    p.push('nota ' + Math.floor(S.nota));
    p.push('dalga ' + S.wave + ' (en iyi ' + S.bestWave + ')');
    try { p.push('nabız %' + Math.round(nb.hpFrac() * 100)); } catch (e) {}
    p.push(nb.playing ? 'müzik çalıyor' : 'müzik durgun');
    p.push('düşman ' + nb.enemies.length);
    const L = document.getElementById('tutL');
    if (L && !L.hidden) p.push('öğretici "' + document.getElementById('tutLN').textContent + ' · ' + document.getElementById('tutLT').textContent + '"');
    const m = document.getElementById('msg'); if (m && m.textContent.trim()) p.push('mesaj "' + m.textContent.trim().slice(0, 120) + '"');
    return p.join(' · ');
  })()`,
  /* idle oyuncu için zaman atlama (oyun saniyesi; yalnız Idle ve İlerleme takipçisi kullanır) */
  ilerle: "(sn) => { if (window.__nb && window.__nb.ff) window.__nb.ff(sn); }",
  hedefler: [
    "İlk 5 dk: zorunlu öğreticiyi bitir (dört vuruş, ▶, ilk düşman, Ritme vur, Stüdyo, Yükselt, Yoğun, Trampet, Hepsini düzenle)",
    "İlk 15 dk: dalga 10'u geç; açılan bölümlerin kısa öğreticilerini (Savunma, Tempo, Görünüm) bitir; bir savunma geliştirmesi al",
    "İlk 30 dk: dalga 20'ye yaklaş, Ses masasını aç, şarkıyı paylaş bağlantısı üret; albüm eşiğini gör",
  ],
  sozluk: "Nota (♪) = para; vuruş = çemberdeki hücre (döngüde her vuruş nota kazandırır ve düşmana ateş eder); " +
    "Nabız = can (sıfırlanırsa bir dalga geri); ▶ = ortadaki başlat/durdur; Ritme vur = ibre vuruştayken sahneye dokunmak (seri bonusu); " +
    "Stüdyo = enstrüman yükseltme ve ritim; Koleksiyon = yeni enstrümanlar; Sade/Hareketli/Yoğun = oyun ritmi senin yerine yazar; " +
    "Hepsini düzenle = enstrümanları uydurur (uyum çarpanı); Şarj = kristal dolar, dokununca patlar; Albüm = prestij (oyun baştan, hayranlar kalıcı).",
  yasak: ["__nb", "unlockAll", "localStorage", "ff("],      /* test kancaları: personalar kullanmaz */
};
