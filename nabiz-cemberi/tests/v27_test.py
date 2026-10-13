"""v27: 3D sahne. Deneme süresince geliştirme herkeste alınmış ve 3D açık gelir. Ritimler zeminden yükselen sütunlar,
saldırılar merkezden ışın; 3D'de sahneye dokunmak ritim yerleştirmez (Ritme vur), 2D'de yerleştirir. Sağ üstteki düğme
(telefonda Ayarlar dişlisinin altında) 3D/2D değiştirir; Görünüm'de aynı seçenek ve satın alınan merkez görünümleri.
Vurgulu adımlar ve Alan rolü merkezi şarj eder (ölçü başına en çok 1/12); dolunca patlama: 10 sn'lik hasar, patrona yarısı.

    python build.py && python tests/v27_test.py
"""
import os, sys, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(R, 'dist'); OUT = os.path.join(R, 'tests', 'out')
os.makedirs(OUT, exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:%d/' % PORT
fails = []
def check(ok, what):
    print(('  ok  ' if ok else '  FAIL ') + what)
    if not ok: fails.append(what)

SEED = """()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};nb.unlockAll();S.nota=1e4;S.muted=true;
  localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}"""
# 2D'de 0. halkanın s. hücresinin ekran konumu (çember düzeni, neon: dönme yok)
CELL = """s=>{const nb=window.__nb,L=nb.L,b=document.getElementById('cv').getBoundingClientRect(),R=L/2,ph=L<480,rIn=(ph?0.15:0.2)*R,rOut=0.74*R,
  t=(rOut-rIn)/nb.S.slots.length,r=rIn+0.5*t,a=-Math.PI/2+(s+0.5)*2*Math.PI/16,OX=(b.width-L)/2,OY=(b.height-L)/2;return [b.left+OX+R+Math.cos(a)*r,b.top+OY+R+Math.sin(a)*r]}"""
# boş olmayan piksel oranı: sahne gerçekten çiziliyor mu
INK = """()=>{const c=window.__nb.scene,x=c.getContext('2d'),d=x.getImageData(0,0,c.width,c.height).data,b=[d[0],d[1],d[2]];let n=0,k=0;
  for(let i=0;i<d.length;i+=4*37){k++;if(Math.abs(d[i]-b[0])+Math.abs(d[i+1]-b[1])+Math.abs(d[i+2]-b[2])>40)n++}return n/k}"""

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()

    # ---------- telefon ----------
    print('telefon 390x844')
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(400)
    d3 = p.evaluate("()=>window.__nb.S.d3")
    check(d3['own'] == 1 and d3['on'] == 1 and d3['core'] == 'kristal', 'yeni oyunda 3D geliştirmesi alınmış (deneme) ve açık (%s)' % d3)
    p.wait_for_timeout(200)
    check(not p.evaluate("()=>window.__nb.D3") and not p.is_visible('#v3d'), 'ilk öğretici sürerken sahne 2D (halkaya dokunarak ritim yazdırır), düğme gizli')
    p.evaluate(SEED); p.reload(); p.wait_for_timeout(500)
    check(p.evaluate("()=>window.__nb.D3") and p.evaluate("()=>window.__nb.is3D()"), 'sahne 3D çiziliyor')
    check(p.evaluate(INK) > 0.05, 'sahnede çizim var (%.2f)' % p.evaluate(INK))
    g = p.evaluate("()=>{const r=q=>document.querySelector(q).getBoundingClientRect(),a=r('#t-set'),v=r('#v3d');return {gr:a.right,gb:a.bottom,vr:v.right,vt:v.top,vw:v.width,pr:document.getElementById('v3d').getAttribute('aria-pressed')}}")
    check(p.is_visible('#v3d') and abs(g['gr'] - g['vr']) < 4 and g['vt'] >= g['gb'] and g['vw'] >= 36 and g['pr'] == 'true',
          '3D düğmesi Ayarlar dişlisinin altında, basılı (%s)' % g)
    # 3D'de sahneye dokunmak ritim yerleştirmez, Ritme vur olur
    x, y = p.evaluate(CELL, 2)
    before = p.evaluate("()=>window.__nb.S.pat.A[0].slice(0,16)")
    p.mouse.click(x, y); p.wait_for_timeout(150)
    check(p.evaluate("()=>window.__nb.S.pat.A[0].slice(0,16)") == before and 'müziği başlat' in p.inner_text('#msg'), '3D’de halkaya dokunmak vuruş koymuyor, Ritme vur oluyor')
    # orta düğme 3D'de de başlatır / durdurur
    cv = p.locator('#cv').bounding_box(); cx, cy = cv['x'] + cv['width'] / 2, cv['y'] + cv['height'] / 2
    p.mouse.click(cx, cy); p.wait_for_timeout(300)
    check(p.evaluate("()=>window.__nb.playing"), '3D’de ortadaki kristal (▶) başlatıyor')
    p.wait_for_timeout(1500); p.screenshot(path=os.path.join(OUT, 'v27_3d_phone.png'))
    o = p.evaluate("()=>{const c=window.__nb.coreScreen(),L=window.__nb.L;return {dx:Math.abs(c[0]-L/2),dy:Math.abs(c[1]-L/2),L}}")
    check(o['dx'] < 1 and o['dy'] < 0.03 * o['L'], 'kristal karenin ortasında, başlat düğmesi yerinde (%s)' % o)
    p.mouse.click(cx, cy); p.wait_for_timeout(300)
    check(not p.evaluate("()=>window.__nb.playing"), 'kristale yeniden dokununca duruyor')
    # 2D'ye geç: dokunuş vuruş koyar
    p.click('#v3d'); p.wait_for_timeout(200)
    check(p.evaluate("()=>window.__nb.S.d3.on") == 0 and not p.evaluate("()=>window.__nb.D3") and p.get_attribute('#v3d', 'aria-pressed') == 'false', 'düğme 2D’ye geçiriyor')
    x, y = p.evaluate(CELL, 2)
    p.mouse.click(x, y); p.wait_for_timeout(150)
    check(p.evaluate("()=>window.__nb.S.pat.A[0][2]") == 1, '2D’de halkaya dokunmak vuruş koyuyor')
    p.screenshot(path=os.path.join(OUT, 'v27_2d_phone.png'))
    p.click('#v3d'); p.wait_for_timeout(200)
    check(p.evaluate("()=>window.__nb.S.d3.on") == 1, 'düğme 3D’ye geri alıyor')
    p.reload(); p.wait_for_timeout(400)
    check(p.evaluate("()=>window.__nb.S.d3.on") == 1 and p.evaluate("()=>window.__nb.S.pat.A[0][2]") == 1, 'seçim ve vuruş kayıtta kalıyor')

    # Görünüm: 3D/2D ve merkez görünümleri
    p.click('#d-look'); p.wait_for_timeout(200)
    t = p.inner_text('#d3Box')
    check(all(k in t for k in ('3D', '2D', 'Kristal', 'Küre', 'Güneş', 'Plak', 'Kullanılıyor')) and '5 Mn' in t and '50 Mn' in t and '500 Mn' in t,
          'Görünüm’de 3D/2D ve merkezler (Küre ♪5 Mn, Güneş ♪50 Mn, Plak ♪500 Mn)')
    check(p.evaluate("()=>document.querySelector('#d3Box [data-act=coreBuy][data-id=kure]').classList.contains('poor')"), 'nota yetmezken Küre soluk')
    p.evaluate("()=>{window.__nb.S.nota=6e6;window.__nb.renderPanels()}")
    n0 = p.evaluate("()=>window.__nb.S.nota")
    p.click('#d3Box [data-act=coreBuy][data-id=kure]'); p.wait_for_timeout(150)
    s3 = p.evaluate("()=>window.__nb.S.d3")
    check(s3['core'] == 'kure' and s3['cores'].get('kure') == 1 and abs(n0 - p.evaluate("()=>window.__nb.S.nota") - 5e6) < 1, 'Küre satın alındı, merkezde (♪ 5 Mn düştü)')
    p.click('#d3Box [data-act=core][data-id=kristal]'); p.wait_for_timeout(100)
    check(p.evaluate("()=>window.__nb.S.d3.core") == 'kristal', 'alınan merkezler arasında geçiş ücretsiz')
    p.click('#d3Box [data-act=d3view][data-v="0"]'); p.wait_for_timeout(100)
    check(p.evaluate("()=>window.__nb.S.d3.on") == 0, 'Görünüm’den de 2D seçiliyor')
    p.click('#d3Box [data-act=d3view][data-v="1"]'); p.wait_for_timeout(100)
    # her merkez görünümü hatasız çiziliyor
    for k in ('kure', 'gunes', 'plak'):
        p.evaluate("k=>{const S=window.__nb.S;S.d3.cores[k]=1;S.d3.core=k}", k)
        p.click('#d-stage'); p.wait_for_timeout(250)
        p.locator('#cv').screenshot(path=os.path.join(OUT, 'v27_core_%s.png' % k))
    p.evaluate("()=>{window.__nb.S.d3.core='kristal'}")
    # şerit düzeninde 3D yok, düğme gizli
    p.evaluate("()=>{const S=window.__nb.S;S.layout='strip'}"); p.wait_for_timeout(250)
    check(not p.evaluate("()=>window.__nb.D3") and not p.is_visible('#v3d'), 'şerit düzeninde 3D yok, düğme gizli')
    p.evaluate("()=>{const S=window.__nb.S;S.layout='circle'}"); p.wait_for_timeout(250)
    # geliştirme yokken düğme gizli, Görünüm'de satın alma
    p.evaluate("()=>{const S=window.__nb.S;S.d3.own=0;window.__nb.renderPanels()}"); p.wait_for_timeout(250)
    check(not p.is_visible('#v3d') and not p.evaluate("()=>window.__nb.D3"), 'geliştirme yokken düğme gizli, sahne 2D')
    p.click('#d-look'); p.wait_for_timeout(150)
    check(p.is_visible('#d3Box [data-act=d3buy]') and '500.000' in p.inner_text('#d3Box'), 'Görünüm’de 3D sahne ♪ 500.000 ile satın alınır')
    p.evaluate("()=>{window.__nb.S.nota=1e6;window.__nb.renderPanels()}")
    p.click('#d3Box [data-act=d3buy]'); p.wait_for_timeout(150)
    check(p.evaluate("()=>window.__nb.S.d3.own") == 1 and p.evaluate("()=>window.__nb.S.nota") < 6e5, 'satın alınca açılıyor')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    ctx.close()

    # ---------- şarj ve patlama ----------
    print('şarj')
    ctx = b.new_context(viewport={'width': 1280, 'height': 800}); p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(300); p.evaluate(SEED); p.reload(); p.wait_for_timeout(400)
    SET = """(o)=>{const nb=window.__nb,S=nb.S;S.slots=[o.id,null,null,null];S.lv={};S.lv[o.id]=3;S.edit='A';S.bpm=120;S.bmax=120;const P=S.pat.A;for(let i=0;i<P.length;i++)P[i].fill(0);
      for(let s=0;s<16;s++)if(o.st.includes(s))P[0][s]=o.v;S.pat.B[0].fill(0);nb.recalc();nb.charge=0;return nb.blastN}"""
    n0 = p.evaluate(SET, {'id': 'davul', 'v': 1, 'st': list(range(0, 16, 2))})
    p.evaluate("()=>window.__nb.ff(8)")
    check(p.evaluate("()=>window.__nb.charge") == 0, 'vurgusuz davul şarj etmiyor')
    n0 = p.evaluate(SET, {'id': 'davul', 'v': 2, 'st': list(range(16))})
    p.evaluate("()=>window.__nb.ff(12)")
    c = p.evaluate("()=>window.__nb.charge")
    check(0.4 <= c <= 0.6 and p.evaluate("()=>window.__nb.blastN") == n0, 'vurgular şarj ediyor, ölçü başına en çok 1/12 (6 ölçüde %.2f)' % c)
    p.evaluate("()=>window.__nb.ff(14)")
    check(p.evaluate("()=>window.__nb.blastN") == n0 + 1 and p.evaluate("()=>window.__nb.charge") < 0.35, 'şarj dolunca merkez patladı (en az 12 ölçüde bir)')
    n0 = p.evaluate(SET, {'id': 'zil', 'v': 1, 'st': [0, 8]})
    p.evaluate("()=>window.__nb.ff(4)")
    c = p.evaluate("()=>window.__nb.charge")
    check(0.15 <= c <= 0.21, 'Alan rolü (Zil) vurgusuz da şarj ediyor (2 ölçüde %.2f)' % c)
    # patlama: herkese 10 sn'lik hasar, patrona yarısı
    p.evaluate(SET, {'id': 'davul', 'v': 2, 'st': list(range(0, 16, 4))})
    r = p.evaluate("""()=>{const nb=window.__nb,E=nb.enemies;E.length=0;const mk=(ty,boss)=>({ty,hp:1e9,hpMax:1e9,d:0.9,a:0.2,sp:0,slow:0,slowT:0,stun:0,dot:0,dotT:0,flash:0,w:1,boss,lastSp:0,wob:0,id:Math.random(),waved:true});
      E.push(mk('memur',false),mk('denetci',true));const d=nb.dps()*10*nb.tourM(),n=nb.blastN;nb.charge=0.5;nb.blast();const o={d,a:1e9-E[0].hp,b:1e9-E[1].hp,dn:nb.blastN-n,ch:nb.charge};E.length=0;return o}""")
    check(r['d'] > 0 and abs(r['a'] / r['d'] - 1) < 1e-6 and abs(r['b'] / r['d'] - 0.5) < 1e-6 and r['dn'] == 1 and r['ch'] == 0,
          'patlama: düşmana 10 sn’lik hasar, patrona yarısı, şarj sıfırlanır (%s)' % r)
    # geliştirme yokken şarj yok
    p.evaluate("()=>{window.__nb.S.d3.own=0}")
    n0 = p.evaluate(SET, {'id': 'davul', 'v': 2, 'st': list(range(16))})
    p.evaluate("()=>window.__nb.ff(6)")
    check(p.evaluate("()=>window.__nb.charge") == 0, 'geliştirme yokken şarj işlemiyor')
    p.evaluate("()=>{window.__nb.S.d3.own=1}")
    # masaüstünde düğme sahnenin sağ üstünde; patlama karesi
    check(p.is_visible('#v3d'), 'masaüstünde 3D düğmesi sahnede')
    cv = p.locator('#cv').bounding_box(); p.mouse.click(cv['x'] + cv['width'] / 2, cv['y'] + cv['height'] / 2); p.wait_for_timeout(1500)
    p.evaluate("()=>{window.__nb.charge=0.99}"); p.wait_for_timeout(2500)
    check(p.evaluate("()=>window.__nb.blastN") >= 1, 'çalarken şarj dolunca patlıyor')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    ctx.close()

    # ---------- solo sahnesi: çalarken 3D, düzenlerken 2D ----------
    print('solo')
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True); p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(300)
    p.evaluate("""()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};nb.unlockAll();S.nota=1e6;S.muted=true;S.slots=['davul','trampet','gitar',null];S.lv={davul:3,trampet:2,gitar:3};
      S.up.solo=1;S.up.sdevir=1;S.up.suzun=1;S.up.sef=1;S.plan=Array(8).fill('solo');S.solo={2:1};
      S.solos={2:{notes:[{t:0,len:4,r:0,art:'none'},{t:8,len:6,r:5,art:'vib'},{t:20,len:4,r:3,art:'none'}],style:'hendrix'}};localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}""")
    p.reload(); p.wait_for_timeout(400)
    cv = p.locator('#cv').bounding_box(); cx, cy = cv['x'] + cv['width'] / 2, cv['y'] + cv['height'] / 2
    p.mouse.click(cx, cy); p.wait_for_timeout(1800)
    st = p.evaluate("()=>({sv:window.__nb.soloView(),now:window.__nb.soloNow,d3:window.__nb.D3})")
    check(st['sv'] == 2 and st['now'] == 2 and st['d3'], 'solo çalarken solo sahnesi 3D (%s)' % st)
    check(p.evaluate(INK) > 0.05 and p.is_visible('#v3d'), 'solo sahnesi çiziliyor, 3D düğmesi yerinde')
    p.locator('#cv').screenshot(path=os.path.join(OUT, 'v27_solo3d.png'))
    n0 = p.evaluate("()=>JSON.stringify(window.__nb.S.solos[2].notes)")
    p.mouse.click(cv['x'] + cv['width'] * 0.8, cy); p.wait_for_timeout(150)
    check(p.evaluate("()=>JSON.stringify(window.__nb.S.solos[2].notes)") == n0 and p.evaluate("()=>window.__nb.playing"), '3D solo sahnesine dokunmak nota koymuyor, müzik sürüyor')
    p.evaluate("()=>window.__nb.setEdit('S')"); p.wait_for_timeout(250)
    check(not p.evaluate("()=>window.__nb.D3") and p.is_visible('#soloChip') and not p.is_visible('#v3d'), 'solo düzenlerken sahne 2D, Solodan çık çipi var')
    p.click('#soloChip'); p.wait_for_timeout(250)
    check(p.evaluate("()=>window.__nb.S.edit") != 'S' and p.evaluate("()=>window.__nb.D3"), 'Solodan çıkınca 3D geri geliyor')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    ctx.close()

    # ---------- İngilizce ----------
    print('EN')
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True); p = ctx.new_page()
    p.goto(URL); p.wait_for_timeout(300)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.lang='en';S.tut={s:0,done:true};nb.unlockAll();localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}")
    p.reload(); p.wait_for_timeout(400); p.click('#d-look'); p.wait_for_timeout(150)
    t = p.inner_text('#p-look').lower()
    check(all(k in t for k in ('3d stage', 'center', 'crystal', 'orb', 'sun', 'record', 'in use', 'tap beat')) and 'kristal' not in t and 'merkez' not in t, '3D bölümü İngilizce')
    check('tap: 2D' in (p.get_attribute('#v3d', 'title') or ''), 'düğme açıklaması İngilizce')
    ctx.close()
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
