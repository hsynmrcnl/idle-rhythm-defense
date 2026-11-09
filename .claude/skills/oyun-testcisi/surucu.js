#!/usr/bin/env node
/* surucu.js — oyun testçisi sürücüsü (9 Kasım 2026; tasarım zindan2/tasarim/OYUN-TESTCISI-2026-11.md §1.1). OYUNDAN BAĞIMSIZ.
   Bir persona ajanının oyunu adım adım oynaması için AÇIK KALAN bir Chrome oturumu: arka planda yerel HTTP sunucusu (127.0.0.1, rastgele port),
   komutlar Bash'ten tek satır. Dışarı veri yok (yalnız yerel dosya ya da profilin verdiği adres).
   KULLANIM
     node surucu.js ac <oturum> --profil <profil.js> [--boy telefon|masaustu|yatay|GENxYUK[m]] [--tohum N] [--dizin <çıktı>]
     node surucu.js <oturum> gor                   metin gözlem: ekran özeti + numaralı tıklanabilir öğeler (@N) + profilin oyun bilgisi + son uyarılar
     node surucu.js <oturum> cek [ad]              ekran çekimi → PNG yolu (ajan Read ile bakar)
     node surucu.js <oturum> tik <@N|~yazı|=yazı|seçici|x,y>   fare tıklaması · dokun <…> dokunma (mobil boy)
                                                   ~yazı: görünen öğelerde yazısı İÇEREN ilk öğe (ekran kaysa da doğru öğe; @N kayabilir) · =yazı: tam eşleşme
     node surucu.js <oturum> bas <@N|…> <ms>       basılı tut (uzun bas; mobilde dokunarak)
     node surucu.js <oturum> surukle <…> <…>       sürükle (kaynak → hedef; hedef "dx,dy" de olabilir: "+0,-200")
     node surucu.js <oturum> tus <Tab|Enter|Escape|…>   · yaz <metin>
     node surucu.js <oturum> bekle <sn>            gerçek zaman bekle (≤ 120)
     node surucu.js <oturum> ilerle <oyun-sn>      profilin hızlandırma kancası (yoksa "yok" der)
     node surucu.js <oturum> hatalar               sayfa hataları (yakalanmamış istisna, console.error)
     node surucu.js <oturum> kapat
   Her komut <dizin>/adimlar.jsonl'a yazılır (tekrarlanabilirlik, kanıt). Persona test kancası kullanamaz: keyfi JS komutu YOK. */
"use strict";
const fs = require("fs"), path = require("path"), http = require("http"), { spawn } = require("child_process");
const OTURUM_KOK = process.env.OT_KOK || path.join(require("os").tmpdir(), "oyun-testcisi");

function oturumDosya(ad) { return path.join(OTURUM_KOK, ad + ".json"); }
function argAl(a, ad, vars) { const i = a.indexOf(ad); return i >= 0 && a[i + 1] != null ? a[i + 1] : vars; }

/* ---------------- istemci ---------------- */
async function istemci(ad, komut, args) {
  let o; try { o = JSON.parse(fs.readFileSync(oturumDosya(ad), "utf8")); } catch (e) { console.log("✖ oturum yok: " + ad + " (önce: surucu.js ac " + ad + " --profil …)"); process.exit(1); }
  const govde = JSON.stringify({ komut, args });
  const sonuc = await new Promise((coz, red) => {
    const r = http.request({ host: "127.0.0.1", port: o.port, path: "/", method: "POST", headers: { "content-type": "application/json" }, timeout: 180000 }, res => {
      let d = ""; res.on("data", c => d += c); res.on("end", () => coz(d)); });
    r.on("error", red); r.on("timeout", () => r.destroy(new Error("zaman aşımı"))); r.end(govde); }).catch(e => "✖ sürücüye ulaşılamadı: " + e.message);
  process.stdout.write(String(sonuc).replace(/\n?$/, "\n"));
}

/* ---------------- sunucu ---------------- */
async function sunucu(ad, profilYol, boyAd, tohum, dizin) {
  const pw = require("playwright");
  const profil = require(path.resolve(profilYol)), pdir = path.dirname(path.resolve(profilYol));
  const boylar = Object.assign({ masaustu: "1366x768", telefon: "390x844m", yatay: "844x390m" }, profil.boylar || {});
  const boy = boylar[boyAd] || boyAd || boylar.masaustu;
  const m = /^(\d+)x(\d+)(m?)$/.exec(boy); if (!m) throw new Error("boy anlaşılmadı: " + boy);
  const W = +m[1], H = +m[2], mobil = m[3] === "m";
  fs.mkdirSync(dizin, { recursive: true });
  const gunluk = fs.createWriteStream(path.join(dizin, "adimlar.jsonl"), { flags: "a" });
  const hatalar = [], uyarilar = [];
  const tarayici = await pw.chromium.launch({ args: ["--no-sandbox", "--disable-dev-shm-usage"] });
  const bag = await tarayici.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1, isMobile: mobil, hasTouch: mobil });
  const sayfa = await bag.newPage();
  sayfa.on("pageerror", e => hatalar.push(String(e && e.message || e).slice(0, 300)));
  sayfa.on("console", c => { if (c.type() === "error") hatalar.push(c.text().slice(0, 300)); });
  if (profil.oncesi) await sayfa.addInitScript(profil.oncesi);
  const url = profil.ac.url || ("file://" + path.resolve(pdir, profil.ac.dosya));
  await sayfa.goto(url, { waitUntil: "load", timeout: 120000 });
  if (profil.kayitSifirla) { await sayfa.evaluate(profil.kayitSifirla); await sayfa.reload({ waitUntil: "load" }); }
  if (profil.tohumla && tohum != null) await sayfa.evaluate(`(${profil.tohumla})(${+tohum})`).catch(() => {});
  if (profil.hazir) await sayfa.waitForFunction(profil.hazir, null, { timeout: 60000 }).catch(() => {});
  let cekN = 0, ogeler = [];
  const cdp = await bag.newCDPSession(sayfa);

  /* gözlem: oyundan bağımsız kısım (numaralı görünür öğeler) + profilin oyun bilgisi */
  async function tara() {
    return sayfa.evaluate(() => {
      const gorunur = el => { const r = el.getBoundingClientRect(); if (r.width < 4 || r.height < 4) return null; if (r.bottom < 0 || r.right < 0 || r.top > innerHeight || r.left > innerWidth) return null;
        const s = getComputedStyle(el); if (s.visibility === "hidden" || s.display === "none" || +s.opacity < 0.05 || s.pointerEvents === "none") return null;
        const x = Math.max(1, Math.min(innerWidth - 1, r.left + r.width / 2)), y = Math.max(1, Math.min(innerHeight - 1, r.top + r.height / 2));
        const ust = document.elementFromPoint(x, y); if (ust && ust !== el && !el.contains(ust) && !ust.contains(el)) return null;   /* üstü örtülü */
        return { x: Math.round(x), y: Math.round(y), w: Math.round(r.width), h: Math.round(r.height) }; };
      const sec = 'button, a[href], input, select, textarea, [role=button], [role=switch], [role=tab], [onclick], [data-zt], .site, .itile, .eqslot, .tab';
      const L = []; const yazi = el => (el.getAttribute("aria-label") || el.innerText || el.value || el.title || "").replace(/\s+/g, " ").trim().slice(0, 60);
      for (const el of document.querySelectorAll(sec)) { const k = gorunur(el); if (!k) continue; const t = yazi(el); if (!t && !el.id) continue;
        L.push({ t: t || "#" + el.id, id: el.id || "", dis: !!el.disabled, ...k }); if (L.length >= 60) break; }
      const basliklar = [...document.querySelectorAll("h1,h2,h3,.askt,.tut-t")].filter(e => gorunur(e)).map(e => e.innerText.trim()).filter(Boolean).slice(0, 6);
      window.__otOge = L; return { L, basliklar, baslik: document.title };
    });
  }
  async function gor() {
    const g = await tara();
    ogeler = g.L;
    let oyun = ""; if (profil.gozlem) oyun = await sayfa.evaluate(profil.gozlem).catch(e => "(profil gözlemi hata: " + e.message + ")");
    const yeniHata = hatalar.length; const satir = [];
    satir.push("EKRAN: " + (g.basliklar.join(" · ") || g.baslik) + (oyun ? "\nOYUN: " + oyun : ""));
    satir.push("ÖĞELER (tik/dokun @N):");
    g.L.forEach((o, i) => satir.push("  @" + (i + 1) + " " + JSON.stringify(o.t) + (o.dis ? " [kapalı]" : "") + " (" + o.x + "," + o.y + ")"));
    if (yeniHata) satir.push("SAYFA HATASI: " + yeniHata + " (ayrıntı: hatalar)");
    return satir.join("\n");
  }
  async function nokta(hedef) {
    if (/^[~=]/.test(hedef)) {   /* yazıyla seç: "~head back" (içerir, büyük/küçük harf duyarsız) · "=Head back" (tam) — o anki ekrandan taze tarama */
      const q = hedef.slice(1).trim().toLowerCase(), tam = hedef[0] === "=", L = (await tara()).L;
      const o = L.find(x => tam ? x.t.toLowerCase() === q : x.t.toLowerCase().includes(q));
      if (!o) throw new Error("yazıyla bulunamadı: " + hedef + " (görünenler: " + L.slice(0, 12).map(x => x.t).join(" | ") + ")");
      return [o.x, o.y]; }
    if (/^@\d+$/.test(hedef)) { const o = ogeler[+hedef.slice(1) - 1]; if (!o) throw new Error("öğe yok: " + hedef + " (önce gor)"); return [o.x, o.y]; }
    const xy = /^(-?\d+),(-?\d+)$/.exec(hedef); if (xy) return [+xy[1], +xy[2]];
    const el = await sayfa.$(hedef); if (!el) throw new Error("seçici bulunamadı: " + hedef);
    const b = await el.boundingBox(); if (!b) throw new Error("görünmüyor: " + hedef); return [b.x + b.width / 2, b.y + b.height / 2];
  }
  async function dokun(x, y, ms) {
    const nk = [{ x, y, id: 1 }];
    await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: nk });
    if (ms) await sayfa.waitForTimeout(ms);
    await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  }
  const KOMUT = {
    gor: async () => gor(),
    cek: async a => { cekN++; const f = path.join(dizin, String(cekN).padStart(3, "0") + (a[0] ? "-" + a[0].replace(/[^\w-]/g, "") : "") + ".png");
      await sayfa.screenshot({ path: f }); return "ÇEKİM: " + f; },
    tik: async a => { const [x, y] = await nokta(a[0]); if (mobil) await dokun(x, y); else await sayfa.mouse.click(x, y); await sayfa.waitForTimeout(250); return "ok tik " + a[0]; },
    dokun: async a => { const [x, y] = await nokta(a[0]); await dokun(x, y); await sayfa.waitForTimeout(250); return "ok dokun " + a[0]; },
    bas: async a => { const [x, y] = await nokta(a[0]), ms = Math.min(5000, +a[1] || 600);
      if (mobil) await dokun(x, y, ms); else { await sayfa.mouse.move(x, y); await sayfa.mouse.down(); await sayfa.waitForTimeout(ms); await sayfa.mouse.up(); }
      await sayfa.waitForTimeout(250); return "ok bas " + a[0] + " " + ms + " ms"; },
    surukle: async a => { const [x, y] = await nokta(a[0]); let h = a[1] || ""; let tx, ty; const d = /^\+(-?\d+),(-?\d+)$/.exec(h);
      if (d) { tx = x + +d[1]; ty = y + +d[2]; } else [tx, ty] = await nokta(h);
      if (mobil) { await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x, y, id: 1 }] });
        for (let i = 1; i <= 10; i++) await cdp.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x: x + (tx - x) * i / 10, y: y + (ty - y) * i / 10, id: 1 }] });
        await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] }); }
      else { await sayfa.mouse.move(x, y); await sayfa.mouse.down(); await sayfa.mouse.move(tx, ty, { steps: 10 }); await sayfa.mouse.up(); }
      await sayfa.waitForTimeout(250); return "ok sürükle"; },
    tus: async a => { await sayfa.keyboard.press(a[0]); await sayfa.waitForTimeout(150); return "ok tuş " + a[0]; },
    yaz: async a => { await sayfa.keyboard.type(a.join(" ").slice(0, 200)); return "ok yaz"; },
    bekle: async a => { const sn = Math.max(0, Math.min(120, +a[0] || 1)); await sayfa.waitForTimeout(sn * 1000); return "ok bekle " + sn + " sn"; },
    ilerle: async a => { if (!profil.ilerle) return "yok: bu oyunun hızlandırma kancası yok (bekle kullan)";
      const sn = Math.max(0, Math.min(3600, +a[0] || 10)); await sayfa.evaluate(`(${profil.ilerle})(${sn})`); return "ok ilerle " + sn + " oyun-sn"; },
    hatalar: async () => hatalar.length ? hatalar.map((h, i) => (i + 1) + ". " + h).join("\n") : "sayfa hatası yok",
    kapat: async () => { setTimeout(async () => { try { await tarayici.close(); } catch (e) { } try { fs.unlinkSync(oturumDosya(ad)); } catch (e) { } process.exit(0); }, 100); return "kapandı"; },
  };
  let son = Date.now();
  const srv = http.createServer((req, res) => { let d = ""; req.on("data", c => d += c); req.on("end", async () => {
    son = Date.now(); let cevap; const t0 = Date.now(); let j = {};
    try { j = JSON.parse(d); const f = KOMUT[j.komut]; if (!f) throw new Error("bilinmeyen komut: " + j.komut); cevap = await f(j.args || []); }
    catch (e) { cevap = "✖ " + e.message; }
    gunluk.write(JSON.stringify({ t: new Date().toISOString(), komut: j.komut, args: j.args, ms: Date.now() - t0, sonuc: String(cevap).slice(0, 200) }) + "\n");
    res.end(String(cevap)); }); });
  srv.listen(0, "127.0.0.1", () => {
    fs.mkdirSync(OTURUM_KOK, { recursive: true });
    fs.writeFileSync(oturumDosya(ad), JSON.stringify({ port: srv.address().port, pid: process.pid, dizin, boy, profil: profilYol }));
    process.stdout.write("HAZIR\n");
  });
  setInterval(() => { if (Date.now() - son > 30 * 60000) KOMUT.kapat(); }, 60000);   /* 30 dk boşta kalırsa kapanır */
}

/* ---------------- giriş ---------------- */
(async () => {
  const a = process.argv.slice(2);
  if (a[0] === "ac") {
    const ad = a[1], profil = argAl(a, "--profil"), boy = argAl(a, "--boy", "masaustu"), tohum = argAl(a, "--tohum", null);
    const dizin = path.resolve(argAl(a, "--dizin", path.join(OTURUM_KOK, ad)));
    if (!ad || !profil) { console.log("kullanım: surucu.js ac <oturum> --profil <profil.js> [--boy …] [--tohum N] [--dizin …]"); process.exit(1); }
    if (a.includes("--sunucu")) return sunucu(ad, profil, boy, tohum, dizin);
    const c = spawn(process.execPath, [__filename, ...a, "--sunucu"], { detached: true, stdio: ["ignore", "pipe", "pipe"] });
    let cikti = "";
    const bitti = await new Promise(coz => {
      const t = setTimeout(() => coz(false), 150000);
      c.stdout.on("data", d => { cikti += d; if (/HAZIR/.test(cikti)) { clearTimeout(t); coz(true); } });
      c.stderr.on("data", d => { cikti += d; });
      c.on("exit", () => { clearTimeout(t); coz(false); });
    });
    if (!bitti) { console.log("✖ açılamadı:\n" + cikti.slice(-1500)); process.exit(1); }
    c.unref(); c.stdout.destroy(); c.stderr.destroy();
    console.log("✔ oturum " + ad + " açık · " + boy + " · çıktı " + dizin + "\n  sonraki: node " + path.relative(process.cwd(), __filename) + " " + ad + " gor");
    process.exit(0);
  }
  if (a.length < 2) { console.log(fs.readFileSync(__filename, "utf8").split("*/")[0]); process.exit(1); }
  await istemci(a[0], a[1], a.slice(2));
})();
