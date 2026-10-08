"""v16: ince tempo, Analiz paneli (öneri + çarpan dökümü), geri al, hasar sayıları.

    python build.py && python tests/v16_test.py
"""
import os, sys, re, threading, functools, http.server, socketserver
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

# öğretici kapalı, birkaç enstrüman ve bölüm açık bir kayıt
SEED = """()=>{const S=window.__nb.S;S.tut={s:0,done:true};S.nota=1e6;S.bestWave=6;S.open={syn:1,rhy:1,pat:1};
  S.slots=['davul','trampet','hihat',null];S.lv={davul:5,trampet:3,hihat:2};
  for(const s of [0,4,8,12])S.pat.A[0][s]=1;S.pat.A[1][4]=1;S.pat.A[1][12]=1;for(const s of [2,6,10,14])S.pat.A[2][s]=1;
  S.bpm=100;S.bmax=120;window.__nb.recalc();window.__nb.renderPanels()}"""

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()

    # ---------- masaüstü ----------
    print('masaüstü 1280x800')
    p = b.new_page(viewport={'width': 1280, 'height': 800}); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(500); p.evaluate(SEED); p.wait_for_timeout(100)
    S = lambda expr: p.evaluate('()=>window.__nb.S.' + expr)

    # ince tempo
    p.click('[data-act=tempoFine][data-v="1"]'); p.wait_for_timeout(50)
    check(S('bpm') == 101, '+1 BPM: 100 → 101')
    p.click('[data-act=tempoFine][data-v="-1"]'); p.click('[data-act=tempoFine][data-v="-1"]'); p.wait_for_timeout(50)
    check(S('bpm') == 99, '−1 BPM iki kez: 99')
    p.evaluate("()=>{window.__nb.S.bpm=118;window.__nb.renderPanels()}")
    p.click('[data-act=tempo]'); p.wait_for_timeout(50)
    check(S('bpm') == 120 and S('bmax') == 120, '+10 sınırı aşmaz, ücretsiz: 118 → 120')
    check(p.is_disabled('[data-act=tempoFine][data-v="1"]'), 'üst sınırda +1 kapalı')
    n0 = S('nota'); p.click('[data-act=tempo]'); p.wait_for_timeout(50)
    check(S('bmax') == 130 and S('bpm') == 130 and S('nota') < n0, '+10 ödemeli: sınır 130, tempo 130')

    # geri al (Ctrl+Z ve düğme): bedel birebir iade
    check(p.evaluate("()=>window.__nb.undoN") == 0 and p.is_disabled('#undoBox [data-act=undo]'), 'başta geri alınacak bir şey yok, düğme kapalı')
    # halkayı temizle (iade alır), sonra geri al (iadeyi geri öder)
    before = p.evaluate("()=>({pat:JSON.stringify(window.__nb.S.pat.A),n:window.__nb.S.nota})")
    p.click('#slotList [data-act=clearRow][data-i="2"]'); p.wait_for_timeout(50)
    mid = p.evaluate("()=>({pat:JSON.stringify(window.__nb.S.pat.A),n:window.__nb.S.nota,u:window.__nb.undoN})")
    check(mid['pat'] != before['pat'] and mid['n'] > before['n'] and mid['u'] == 1, 'halka temizlendi, iade alındı, geri al yığınında 1 adım')
    check(not p.is_disabled('#undoBox [data-act=undo]'), 'geri al düğmesi açıldı')
    p.keyboard.press('Control+z'); p.wait_for_timeout(50)
    aft = p.evaluate("()=>({pat:JSON.stringify(window.__nb.S.pat.A),n:window.__nb.S.nota,u:window.__nb.undoN})")
    check(aft['pat'] == before['pat'] and abs(aft['n'] - before['n']) < 1e-6 and aft['u'] == 0, 'Ctrl+Z desen ve notayı birebir geri getirdi')
    # ölçü değişimi geri alınır
    sc0 = S('scale'); opts = p.evaluate("()=>[...document.querySelectorAll('#selScale option')].filter(o=>!o.disabled).map(o=>o.value)")
    other = [o for o in opts if o != sc0]
    if other:
        p.select_option('#selScale', other[0]); p.wait_for_timeout(50)
        p.click('#undoBox [data-act=undo]'); p.wait_for_timeout(50)
        check(S('scale') == sc0, 'gam değişimi geri alındı (%s → %s → %s)' % (sc0, other[0], S('scale')))
    # satın alma geri alınmaz
    lv0 = S("lv.davul"); u0 = p.evaluate("()=>window.__nb.undoN")
    p.click('#lvb-davul'); p.wait_for_timeout(50)
    check(S("lv.davul") > lv0 and p.evaluate("()=>window.__nb.undoN") == u0, 'seviye satın alma geri al yığınına girmiyor')

    # Analiz paneli
    st0 = p.evaluate("()=>JSON.stringify([window.__nb.S.lv,window.__nb.S.up,window.__nb.S.def,window.__nb.S.bpm,window.__nb.S.bmax])")
    r0 = p.evaluate("()=>window.__nb.rate()")
    p.click('#stats'); p.wait_for_timeout(150)
    check(p.is_visible('#anl') and p.evaluate("()=>window.__nb.anlOn"), 'istatistik çubuğuna basınca Analiz açılıyor')
    txt = p.text_content('#anl')
    check('Sıradaki en verimli adım' in txt and 'Gelir' in txt and 'Savunma' in txt, 'öneri satırları var')
    st1 = p.evaluate("()=>JSON.stringify([window.__nb.S.lv,window.__nb.S.up,window.__nb.S.def,window.__nb.S.bpm,window.__nb.S.bmax])")
    check(st0 == st1 and abs(p.evaluate("()=>window.__nb.rate()") - r0) < 1e-9 * max(1, r0), 'adaylar denendikten sonra durum ve gelir aynı')
    # çarpan dökümünün çarpımı üstteki Çarpan'a eşit
    prod = p.evaluate("""()=>{const h=[...document.querySelectorAll('#anl h4')].find(x=>/Çarpan/.test(x.textContent));
      const vals=[];let el=h.nextElementSibling;while(el&&el.classList.contains('mr')){vals.push(parseFloat(el.querySelector('b').textContent.replace('×','').replace(',','.')));el=el.nextElementSibling}
      return {p:vals.reduce((a,b)=>a*b,1),top:parseFloat(h.querySelector('span').textContent.replace('×','').replace(',','.')),bar:parseFloat(document.getElementById('sMult').textContent.replace('×','').replace(',','.'))}}""")
    check(abs(prod['p'] - prod['top']) / prod['top'] < 0.03 and abs(prod['top'] - prod['bar']) < 0.011, 'çarpan dökümü toplamı Çarpan’a eşit (×%.2f · ×%.2f · ×%.2f)' % (prod['p'], prod['top'], prod['bar']))
    sug = p.evaluate("()=>{const r=window.__nb.anlRank();return r.inc?{act:r.inc.act,id:r.inc.id,cost:r.inc.cost,dr:r.inc.dr}:null}")
    check(sug is not None and sug['dr'] > 0, 'gelir önerisi var: %s' % (sug and (sug['act'] + ' ' + str(sug['id']))))
    if sug:
        n0 = S('nota'); lvb = p.evaluate("()=>JSON.stringify(window.__nb.S.lv)"); upb = p.evaluate("()=>JSON.stringify(window.__nb.S.up)")
        p.click('#anl [data-a=buy][data-i="0"]'); p.wait_for_timeout(100)
        spent = n0 - S('nota')
        changed = p.evaluate("()=>JSON.stringify(window.__nb.S.lv)") != lvb or p.evaluate("()=>JSON.stringify(window.__nb.S.up)") != upb or sug['act'] in ('tempo', 'def')
        check(changed and abs(spent - sug['cost']) <= max(1, sug['cost'] * 0.02), '“Al” öneriyi tam fiyatına aldı (♪ %d)' % spent)
    p.click('#anl [data-a=close]'); p.wait_for_timeout(50)
    check(not p.is_visible('#anl'), '× ile kapanıyor')
    p.screenshot(path=os.path.join(OUT, 'v16_desktop.png'))

    # hasar sayıları: örnek şarkıda düşman vurulunca sayılar çıkıyor; kapatınca çıkmıyor
    p.click('#demo'); p.wait_for_timeout(300)
    seen = 0
    for _ in range(40):
        seen = max(seen, p.evaluate("()=>window.__nb.pops.length"))
        if seen: break
        p.wait_for_timeout(250)
    check(seen > 0, 'vurulan düşmanın üstünde hasar sayısı çıkıyor')
    p.click('[data-act=tab][data-tab=look]'); p.wait_for_timeout(50)
    p.click('[data-act=dnum][data-v="0"]'); p.wait_for_timeout(600)
    check(p.evaluate("()=>window.__nb.S.dnum") is False and p.evaluate("()=>window.__nb.pops.length") == 0, 'Görünüm’den kapatılınca sayı yok')
    p.click('[data-act=dnum][data-v="1"]')
    check(p.evaluate("()=>window.__nb.undoN") == 0, 'örnek şarkıya girince geri al sıfırlandı')
    p.click('#demo'); p.wait_for_timeout(100)
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))

    # ---------- telefon ----------
    for w, h in [(375, 667), (390, 844)]:
        print('telefon %dx%d' % (w, h))
        ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=True, has_touch=True)
        p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.goto(URL); p.wait_for_timeout(500); p.evaluate(SEED); p.wait_for_timeout(100)
        # pedden vuruş ekle → ped başlığındaki geri al ile birebir iade
        p.evaluate("()=>{window.__nb.renderPanels()}")
        free = p.evaluate("()=>{const a=window.__nb.S.pat.A[0];for(let s=0;s<16;s++)if(!a[s])return s;return -1}")
        n0 = p.evaluate("()=>window.__nb.S.nota")
        p.click('#pads [data-act=pad][data-s="%d"]' % free); p.wait_for_timeout(50)
        n1 = p.evaluate("()=>window.__nb.S.nota")
        check(p.evaluate("()=>window.__nb.S.pat.A[0][%d]" % free) == 1 and n1 < n0, 'pedden vuruş eklendi (♪ %d)' % (n0 - n1))
        check(p.is_visible('#pads [data-act=undo]') and not p.is_disabled('#pads [data-act=undo]'), 'ped başlığında geri al düğmesi')
        p.click('#pads [data-act=undo]'); p.wait_for_timeout(50)
        check(p.evaluate("()=>window.__nb.S.pat.A[0][%d]" % free) == 0 and abs(p.evaluate("()=>window.__nb.S.nota") - n0) < 1e-6, 'geri al vuruşu kaldırdı, bedel tam iade')
        # çalarken gelir akarken de iade yalnız düzenlemenin bedeli
        cv = p.locator('#cv').bounding_box()
        p.mouse.click(cv['x'] + cv['width'] / 2, cv['y'] + cv['height'] / 2); p.wait_for_timeout(300)
        p.click('#pads [data-act=pad][data-s="%d"]' % free)
        p.wait_for_timeout(1500)
        d = p.evaluate("""()=>{const a=window.__nb.S.nota;document.querySelector('#pads [data-act=undo]').click();return window.__nb.S.nota-a}""")
        check(d > 0 and d < 1e5, 'çalarken geri al: aradaki gelir sayılmadan bedel iade (♪ %.0f)' % d)
        # Analiz paneli telefonda sahnenin üstünde, sayfa kaymıyor
        p.tap('#stats'); p.wait_for_timeout(200)
        m = p.evaluate("""()=>{const a=document.getElementById('anl').getBoundingClientRect(),d=document.getElementById('dock').getBoundingClientRect();
          return {vis:!document.getElementById('anl').hidden,top:a.top,bot:a.bottom,dock:d.top,right:a.right,vw:innerWidth,scroll:document.scrollingElement.scrollHeight-innerHeight}}""")
        check(m['vis'] and m['right'] <= m['vw'] and m['top'] > 0, 'Analiz telefonda açılıyor, ekrana sığıyor')
        check(m['bot'] <= m['dock'] + 1, 'Analiz dock’un üstünde bitiyor (%d ≤ %d)' % (m['bot'], m['dock']))
        check(m['scroll'] <= 0, 'sayfa kaymıyor')
        if w == 390: p.screenshot(path=os.path.join(OUT, 'v16_phone_anl.png'))
        p.click('#d-def'); p.wait_for_timeout(100)
        check(not p.evaluate("()=>window.__nb.anlOn"), 'başka sekmeye geçince Analiz kapanıyor')
        check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
        ctx.close()

    # ---------- İngilizce ----------
    print('EN')
    p = b.new_page(viewport={'width': 390, 'height': 844}); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(300); p.evaluate(SEED)
    p.evaluate("()=>{window.__nb.S.lang='en';localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(window.__nb.S))}")
    with p.expect_navigation(): p.reload()
    p.wait_for_timeout(400)
    p.click('#stats'); p.wait_for_timeout(150)
    t = p.text_content('#anl')
    check('Most efficient next step' in t and 'Income' in t and 'Beat streak' in t and 'Buy' in t, 'Analiz İngilizce')
    tr_left = [w for w in ['Sıradaki', 'Gelir', 'Savunma', 'Kalıp kitabı', 'Ritim serisi', 'kendini', 'ücretsiz', 'Her dalga'] if w in t]
    check(not tr_left, 'Analiz’de Türkçe kalmadı ' + ','.join(tr_left))
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
