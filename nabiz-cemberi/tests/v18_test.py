"""v18: Kolay / Detaylı Stüdyo. Herkes Kolay'da başlar; kart başına "Detay ›"; sade adlar ve seçimler.

    python build.py && python tests/v18_test.py
"""
import os, sys, json, threading, functools, http.server, socketserver
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

SEED = """()=>{const S=window.__nb.S;S.tut={s:0,done:true};window.__nb.unlockAll();S.nota=1e9;S.bestWave=6;S.open={syn:1,rhy:1,pat:1};S.famOpen.tel=1;
  S.slots=['davul','trampet','hihat','keman'];S.lv={davul:5,trampet:3,hihat:2,keman:2,bas:1};
  for(const s of [0,4,8,12])S.pat.A[0][s]=1;S.pat.A[1][4]=1;S.pat.A[1][12]=1;for(const s of [2,6,10,14])S.pat.A[2][s]=1;S.pat.A[3][3]=1;S.pat.A[3][11]=1;
  S.bpm=100;S.bmax=120;S.up.sef=1;S.up.akor=1;S.up.solo=1;window.__nb.recalc();window.__nb.renderPanels()}"""

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()

    # eski kayıt (ui alanı yok) da Kolay'a geçer
    print('eski kayıt')
    ctx = b.new_context(viewport={'width': 1280, 'height': 800}); p = ctx.new_page()
    p.goto(URL); p.wait_for_timeout(300)
    oldsave = p.evaluate("()=>{const d=JSON.parse(JSON.stringify(window.__nb.S));delete d.ui;delete d.det;d.tut={s:0,done:true};return JSON.stringify(d)}")
    ctx.close()
    ctx = b.new_context(viewport={'width': 1280, 'height': 800}); p = ctx.new_page()
    p.add_init_script("try{if(!sessionStorage.getItem('seeded')){localStorage.setItem('nabiz-cemberi-v3',%s);sessionStorage.setItem('seeded','1')}}catch(e){}" % json.dumps(oldsave))
    p.goto(URL); p.wait_for_timeout(400)
    check(p.evaluate("()=>window.__nb.S.ui") == 'kolay' and p.evaluate("()=>window.__nb.S.tut.done") is True, 'eski kayıt (ui alanı yok) Kolay’da açılıyor')
    ctx.close()

    print('masaüstü 1280x800')
    p = b.new_page(viewport={'width': 1280, 'height': 800}); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(400)
    check(p.evaluate("()=>window.__nb.S.ui") == 'kolay', 'yeni oyun Kolay’da başlıyor')
    p.evaluate(SEED); p.wait_for_timeout(100)
    # Sahne: sade satır
    m = p.evaluate("""()=>({clear:document.querySelectorAll('#slotList [data-act=clearRow]').length,needle:document.querySelectorAll('#slotList [data-act=needle]').length,
      roles:[...document.querySelectorAll('#slotList .role')].map(e=>e.textContent),bars:document.querySelectorAll('#slotList .nb').length,lv:!!document.getElementById('lvb-davul')})""")
    check(m['clear'] == 0 and m['needle'] == 0 and m['lv'], 'Sahne sade: temizle ve ibre düğmesi yok, seviye düğmesi var')
    check(set(m['roles']) <= {'Saldırı', 'Alan', 'Koruma', 'Destek', 'Gelir'} and m['bars'] >= 3, 'roller sade etiketli, nefes çubukları var (%s)' % m['roles'])
    # Detay › yalnız o kartı açar
    p.click('[data-sec=sahne] > .dl'); p.wait_for_timeout(50)
    check(p.evaluate("()=>document.querySelectorAll('#slotList [data-act=clearRow]').length") >= 3 and p.evaluate("()=>window.__nb.S.det.sahne") == 1, 'Sahne’de Detay › tam görünümü açıyor')
    check(p.evaluate("()=>!!document.getElementById('bpmR')"), 'diğer kartlar Kolay kalıyor (tempo sürgüsü)')
    p.click('[data-sec=sahne] > .dl'); p.wait_for_timeout(50)
    check(p.evaluate("()=>document.querySelectorAll('#slotList [data-act=clearRow]').length") == 0, '‹ Sade görünüm geri dönüyor')
    # Ritim stüdyosu: sürgü, sınır, en çok iki geliştirme
    r = p.evaluate("()=>{const e=document.getElementById('bpmR');return{max:+e.max,min:+e.min,tiles:document.querySelectorAll('#rhyList .tile').length}}")
    check(r['min'] == 70 and r['max'] == 120 and 1 <= r['tiles'] <= 2, 'tempo sürgüsü 70–120, önerilen %d geliştirme' % r['tiles'])
    p.evaluate("()=>{const e=document.getElementById('bpmR');e.value=112;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}"); p.wait_for_timeout(50)
    check(p.evaluate("()=>window.__nb.S.bpm") == 112, 'sürgü tempoyu 112 yapıyor')
    n0 = p.evaluate("()=>window.__nb.S.nota"); p.click('[data-act=tempoMax]'); p.wait_for_timeout(50)
    check(p.evaluate("()=>window.__nb.S.bmax") == 130 and p.evaluate("()=>window.__nb.S.nota") < n0 and p.evaluate("()=>+document.getElementById('bpmR').max") == 130, 'sınırı yükselt: 130, ödendi')
    # Desen, ölçü, gam: ruh hâli ve ritim tipi
    p.click('[data-act=scale][data-v=major]'); p.wait_for_timeout(50)
    check(p.evaluate("()=>window.__nb.S.scale") == 'major', 'Ruh hâli → Neşeli = majör')
    check(p.is_disabled('[data-act=scale][data-v=hicaz]') and p.is_disabled('[data-act=meter][data-v=m98]'), 'Doğulu ve Roman havası albümle açılıyor (kilitli)')
    p.click('[data-act=scale][data-v=minor]')
    # Şarkı planı: hazır yapı ve tek akor seçimi
    p.click('#planBox [data-act=preset][data-v=club]'); p.wait_for_timeout(50)
    check(p.evaluate("()=>JSON.stringify(window.__nb.S.plan)") == json.dumps(['intro', 'build', 'drop', 'verse', 'build', 'drop', 'solo', 'outro']).replace(' ', ''), 'Şarkı yapısı → Kulüp')
    p.select_option('#selProgAll', 'klasik'); p.wait_for_timeout(50)
    check(p.evaluate("()=>window.__nb.S.prog.every(x=>x==='klasik')"), 'Akorlar → bütün bölümler aynı yürüyüş')
    # Uyum: Groove kartı birleşik, ipucu var
    u = p.evaluate("()=>({groove:document.querySelector('[data-sec=groove]').hidden,txt:document.getElementById('synChips').textContent})")
    check(u['groove'] and 'Groove' in u['txt'] and 'Sıradaki' in u['txt'], 'Uyum ve Groove tek kart, sıradaki uyum ipucu var')
    # Solo: Solo düğmesi melodik enstrümana solo yazar
    p.click('#slotList [data-act=solo][data-i="3"]'); p.wait_for_timeout(80)
    check(p.evaluate("()=>(window.__nb.S.solos[3]||{notes:[]}).notes.length") > 0 and 'Yeniden yaz' in p.text_content('#soloBox'), 'Solo açılınca keman solosu kendiliğinden yazılıyor')
    # Koleksiyon sade
    p.click('[data-act=tab][data-tab=coll]'); p.wait_for_timeout(50)
    t = p.text_content('#collList')
    check('nefes' not in t and 'Saldırı' in t, 'Koleksiyon sade: değerler yok, sade rol')
    # Görünüm: efekt laboratuvarı Detay'da
    p.click('[data-act=tab][data-tab=look]'); p.wait_for_timeout(50)
    check(p.locator('#fxBox [data-act=sfset]').count() == 0, 'Görünüm Kolay: ince ayarlar gizli')
    p.click('[data-sec=fx] > .dl'); p.wait_for_timeout(50)
    check(p.locator('#fxBox [data-act=sfset]').count() == 2, 'Efekt laboratuvarı Detay ile açılıyor')
    # Ayarlar → Detaylı: her şey açık, Detay bağlantısı yok
    p.click('#t-set'); p.wait_for_timeout(50)
    p.click('#setBox [data-act=ui][data-v=detay]'); p.wait_for_timeout(80)
    p.click('[data-act=tab][data-tab=studio]'); p.wait_for_timeout(50)
    d = p.evaluate("()=>({dl:document.querySelectorAll('#rack .dl').length,groove:document.querySelector('[data-sec=groove]').hidden,sel:!!document.getElementById('selMeter')})")
    check(d['dl'] == 0 and not d['groove'] and d['sel'], 'Detaylı: Groove kartı ve ölçü listesi görünür, Detay bağlantısı yok')
    p.click('#t-set'); p.click('#setBox [data-act=ui][data-v=kolay]'); p.wait_for_timeout(50)
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))

    # ---------- telefon ----------
    for w, h in [(375, 667), (390, 844)]:
        print('telefon %dx%d' % (w, h))
        ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=True, has_touch=True)
        p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.goto(URL); p.wait_for_timeout(400); p.evaluate(SEED); p.wait_for_timeout(100)
        p.click('#d-studio'); p.wait_for_timeout(150)
        o = p.evaluate("""()=>{const rk=document.getElementById('rack');const over=[...rk.querySelectorAll('#p-studio *')].filter(e=>e.offsetParent&&e.getBoundingClientRect().right>innerWidth+1).map(e=>e.className||e.tagName).slice(0,4);
          return{over,sw:document.scrollingElement.scrollWidth-innerWidth,rsw:rk.scrollWidth-rk.clientWidth}}""")
        check(not o['over'] and o['sw'] <= 0 and o['rsw'] <= 0, 'Stüdyo Kolay ekrana sığıyor, yana kaymıyor %s' % o['over'])
        if w == 390:
            p.screenshot(path=os.path.join(OUT, 'v18_phone_studio.png'), full_page=False)
            p.evaluate("()=>{document.getElementById('rack').scrollTop=600}"); p.wait_for_timeout(100)
            p.screenshot(path=os.path.join(OUT, 'v18_phone_studio2.png'), full_page=False)
        check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
        ctx.close()

    # ---------- İngilizce ----------
    print('EN')
    p = b.new_page(viewport={'width': 1280, 'height': 800}); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(300); p.evaluate(SEED)
    p.evaluate("()=>{window.__nb.S.lang='en';localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(window.__nb.S))}")
    with p.expect_navigation(): p.reload()
    p.wait_for_timeout(400)
    t = p.text_content('#p-studio')
    check('Mood' in t and 'Rhythm type' in t and 'Details ›' in t and 'Sad' in t, 'Kolay Stüdyo İngilizce')
    left = [x for x in ['Ruh hâli', 'Ritim tipi', 'Detay ›', 'Hüzünlü', 'Sıradaki', 'Saldırı'] if x in t]
    check(not left, 'Türkçe kalmadı ' + ','.join(left))
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
