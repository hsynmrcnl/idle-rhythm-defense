"""v25: Ayarlar → Oyunu sıfırla. İki dokunuş; kayıt silinir, sayfa yeniden açılır, her şey ilk açılıştaki gibi (öğretici dahil).

    python build.py && python tests/v25_test.py
"""
import os, sys, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(R, 'dist')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:%d/' % PORT
fails = []
def check(ok, what):
    print(('  ok  ' if ok else '  FAIL ') + what)
    if not ok: fails.append(what)

# ilerlemiş bir oyun: albüm, menajer, öğretici bitmiş, Detaylı, otomatikler kapalı, açılmış bölümler
SEED = """()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};window.__nb.unlockAll();S.ui='detay';S.nota=5e8;S.total=9e8;S.wave=30;S.bestWave=40;S.kills=999;
  S.albums=[{n:'X',f:5,b:120,w:20}];S.albMax=1;S.hayran=5;S.mn={lv:1};S.am.yeni=false;S.open={syn:1,rhy:1,pat:1};S.famOpen.tel=1;S.lv.bas=10;S.muted=true;
  nb.renderPanels();localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}"""

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    for w, h in [(390, 844), (1280, 800)]:
        print('%dx%d' % (w, h))
        mob = w <= 700
        ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob)
        p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.goto(URL); p.wait_for_timeout(400); p.evaluate(SEED)
        p.reload(); p.wait_for_timeout(400)
        check(p.evaluate("()=>window.__nb.S.albums.length") == 1, 'ilerlemiş kayıt yüklü')
        p.click('#t-set'); p.wait_for_timeout(100)
        btn = '#p-set [data-act=reset]'
        check(p.is_visible(btn) and p.inner_text(btn) == 'Oyunu sıfırla', 'Ayarlar’da “Oyunu sıfırla” görünüyor')
        p.click(btn); p.wait_for_timeout(100)
        check('Emin misin' in p.inner_text(btn) and p.evaluate("()=>window.__nb.S.albums.length") == 1, 'ilk dokunuş yalnız onay istiyor, bir şey silinmiyor')
        with p.expect_navigation(): p.click(btn)
        p.wait_for_timeout(600)
        st = p.evaluate("""()=>{const S=window.__nb.S;return {al:S.albums.length,amax:S.albMax||0,tot:S.total,kills:S.kills,wave:S.bestWave,ui:S.ui,mn:Object.keys(S.mn).length,
          yeni:S.am.yeni,open:Object.keys(S.open).length,fam:Object.keys(S.famOpen),muted:S.muted,lv:S.lv,tut:S.tut,lang:S.lang}}""")
        check(st['al'] == 0 and st['amax'] == 0 and st['tot'] < 100 and st['kills'] == 0 and st['wave'] == 1, 'ilerleme sıfırlandı (%s)' % st)
        check(st['ui'] == 'kolay' and st['mn'] == 0 and st['yeni'] is True and st['open'] == 0 and st['fam'] == ['vur'] and st['muted'] is False and st['lv'] == {'davul': 1}, 'ayarlar ve açılanlar ilk açılıştaki gibi')
        check(st['tut'] == {'s': 0, 'done': False} and p.is_visible('#tut') and 'Hoş geldin' in p.inner_text('#tutT'), 'öğretici baştan başlıyor')
        if mob:
            check(p.evaluate("()=>document.getElementById('app').dataset.tab") == 'stage', 'telefonda sahneyle açılıyor')
        p.wait_for_timeout(5500)
        sv = p.evaluate("()=>{const d=JSON.parse(localStorage.getItem('nabiz-cemberi-v3')||'null');return d&&{al:d.albums.length,tot:d.total}}")
        check(sv is None or (sv['al'] == 0 and sv['tot'] < 100), 'eski kayıt geri yazılmadı (%s)' % sv)
        check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
        ctx.close()
    # İngilizce
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True); p = ctx.new_page()
    p.goto(URL); p.wait_for_timeout(300)
    p.evaluate("()=>{const S=window.__nb.S;S.lang='en';S.tut={s:0,done:true};localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}")
    p.reload(); p.wait_for_timeout(400); p.click('#t-set'); p.wait_for_timeout(100)
    t = p.inner_text('#p-set')
    check('Reset the game' in t and 'Everything is erased' in t and 'sıfırla' not in t.lower(), 'sıfırlama İngilizce')
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
