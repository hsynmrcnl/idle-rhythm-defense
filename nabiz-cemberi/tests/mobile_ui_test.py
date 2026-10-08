"""v13 telefon arayüzü: tek ekran sahne, 5 simgeli dock, sağ üstte Ayarlar, boş yere dokununca ritme vur.

    python build.py && python tests/mobile_ui_test.py
"""
import os, sys, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(R, 'dist'); OUT = os.path.join(R, 'tests', 'out')
os.makedirs(OUT, exist_ok=True)
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIST)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
H = functools.partial(Q, directory=DIST)
srv = socketserver.TCPServer(('127.0.0.1', 0), H); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:%d/' % PORT
fails = []
def check(ok, what):
    print(('  ok  ' if ok else '  FAIL ') + what)
    if not ok: fails.append(what)

def launch(pw):
    exe = '/opt/pw-browsers/chromium'
    return pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()

with sync_playwright() as pw:
    b = launch(pw)
    for w, h in [(375, 667), (390, 844), (412, 915)]:
        print('telefon %dx%d' % (w, h))
        ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=True, has_touch=True)
        p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.goto(URL); p.wait_for_timeout(600)
        tut = p.evaluate("()=>{const r=q=>document.querySelector(q).getBoundingClientRect().height;return {tut:r('#tut'),cv:r('#cv')}}")
        check(tut['cv'] >= 240, 'öğretici açıkken de sahne yeterince büyük (kart %dpx, canvas %dpx)' % (tut['tut'], tut['cv']))
        if w == 375: p.screenshot(path=os.path.join(OUT, 'v13_tutorial_375.png'))
        p.click('#tut [data-act=tutSkip]'); p.wait_for_timeout(150)
        m = p.evaluate("""()=>{const r=q=>document.querySelector(q).getBoundingClientRect();const cv=r('#cv');
          return {scroll:document.scrollingElement.scrollHeight-innerHeight,cvW:cv.width,cvH:cv.height,cvR:cv.right,vw:innerWidth,
          play:r('#play').bottom,dock:r('#dock').top,gear:r('#t-set').right,top:!!document.querySelector('.top h1').offsetParent,
          hidden:['#tap','#mute','#demo','#langBtn','.tabs'].every(q=>{const e=document.querySelector(q);return !e.offsetParent||getComputedStyle(e).display==='none'})}}""")
        check(m['scroll'] <= 0, 'sahne kaydırmasız (fazla %dpx)' % m['scroll'])
        check(abs(m['cvW'] - m['cvH']) < 1 and m['cvR'] <= m['vw'], 'canvas kare ve ekranda (%dx%d)' % (m['cvW'], m['cvH']))
        check(m['play'] <= m['dock'], 'Başlat dock’un üstünde')
        check(not m['top'] and m['hidden'], 'başlık, EN, Ritme vur, Ses, Örnek şarkı ve üst sekmeler gizli')
        check(m['gear'] >= m['vw'] - 20, 'Ayarlar sağ üstte')
        # boş yere dokun → ritme vur (çalmıyorken uyarı verir)
        cv = p.locator('#cv').bounding_box()
        p.mouse.click(cv['x'] + 6, cv['y'] + 6); p.wait_for_timeout(100)
        check('Önce müziği başlat' in p.inner_text('#msg'), 'boş yere dokunmak ritme vuruyor')
        if w == 390:
            p.screenshot(path=os.path.join(OUT, 'v13_stage.png'))
            # dock: 5 buton, aynı renk; aktif olan kendi neonunda
            n = p.locator('.dk').count(); check(n == 5, 'dock’ta 5 düğme (%d)' % n)
            for k, sub in [('studio', 'coll'), ('def', None), ('album', 'book'), ('look', None)]:
                p.click('#d-' + k); p.wait_for_timeout(120)
                st = p.evaluate("k=>({tab:document.getElementById('app').dataset.tab,cur:[...document.querySelectorAll('.dk')].filter(b=>b.getAttribute('aria-current')==='page').map(b=>b.id),col:[...document.querySelectorAll('.dk:not([aria-current])')].map(b=>getComputedStyle(b).color)})", k)
                check(st['tab'] == k and st['cur'] == ['d-' + k] and len(set(st['col'])) == 1, 'dock → %s, yalnız o parlıyor, diğerleri aynı renk' % k)
                if sub:
                    p.click('#p-%s .subnav [data-tab=%s]' % (k, sub)); p.wait_for_timeout(120)
                    st = p.evaluate("()=>({tab:document.getElementById('app').dataset.tab,cur:document.querySelector('.dk[aria-current]').id})")
                    check(st['tab'] == sub and st['cur'] == 'd-' + k, 'alt sekme %s, dock %s’de kalıyor' % (sub, k))
                    p.click('#d-stage'); p.click('#d-' + k); p.wait_for_timeout(80)
                    check(p.evaluate("()=>document.getElementById('app').dataset.tab") == sub, 'dock son alt sekmeyi hatırlıyor (%s)' % sub)
                    p.screenshot(path=os.path.join(OUT, 'v13_%s.png' % sub))
            # Ayarlar: dişli aç/kapa, örnek şarkı sahneye götürür, çip ile çıkılır
            def open_set():
                if p.evaluate("()=>document.getElementById('app').dataset.tab") != 'set': p.click('#t-set')
                p.wait_for_timeout(120)
            open_set()
            check(p.evaluate("()=>document.getElementById('app').dataset.tab") == 'set' and p.locator('#p-set [data-act=saveCode]').count() == 1, 'dişli Ayarlar’ı açıyor, Kayıt orada')
            p.screenshot(path=os.path.join(OUT, 'v13_set.png'), full_page=True)
            p.click('#p-set [data-act=demoGo][data-k="0"]'); p.wait_for_timeout(300)
            check(p.evaluate("()=>document.getElementById('app').dataset.tab==='stage'&&window.__nb.demoMode&&!document.getElementById('demoChip').hidden"), 'örnek şarkı sahnede çalıyor, çıkış çipi görünüyor')
            p.click('#demoChip'); p.wait_for_timeout(200)
            check(p.evaluate("()=>!window.__nb.demoMode&&document.getElementById('demoChip').hidden"), 'çip örnek şarkıdan çıkarıyor')
            # Ses ayarı
            open_set(); p.click('#setBox [data-act=mute][data-v="1"]'); p.wait_for_timeout(80)
            check(p.evaluate("()=>window.__nb.S.muted===true"), 'Ayarlar’dan ses kapanıyor')
            p.click('#setBox [data-act=mute][data-v="0"]')
            # öğretici: Savunma adımı dock simgesini vurguluyor
            open_set(); p.click('#p-set [data-act=tutRestart]')
            p.evaluate("()=>{window.__nb.S.tut.s=8}"); p.wait_for_timeout(400)
            check(p.locator('#d-def.tut-hi').count() == 1, 'öğretici Savunma adımında dock simgesi vurgulu')
            # İngilizce
            open_set()
            with p.expect_navigation(): p.click('#setBox [data-act=lang][data-v="en"]')
            p.wait_for_timeout(500)
            open_set()
            txt = p.inner_text('#p-set')
            check('SETTINGS' in txt, 'İngilizce başlıklar İngilizce büyük harfle (SETTİNGS değil)')
            check(all(k in txt.lower() for k in ('settings', 'language', 'demo songs', 'how to play?')), 'Ayarlar İngilizce')
            p.screenshot(path=os.path.join(OUT, 'v13_set_en.png'))
        check(not errs, 'sayfa hatası yok ' + ('; '.join(errs) if errs else ''))
        ctx.close()
    print('masaüstü 1280x800')
    ctx = b.new_context(viewport={'width': 1280, 'height': 800}); p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(600)
    d = p.evaluate("()=>({dock:getComputedStyle(document.getElementById('dock')).display,tabs:getComputedStyle(document.querySelector('.tabs')).display,tap:!!document.getElementById('tap').offsetParent,h1:getComputedStyle(document.querySelector('.top h1')).display})")
    check(d['dock'] == 'none' and d['tabs'] != 'none' and d['tap'] and d['h1'] != 'none', 'masaüstü düzeni aynı (dock yok, sekmeler ve düğmeler yerinde)')
    p.click('#t-set'); p.wait_for_timeout(100)
    check(p.evaluate("()=>!document.getElementById('p-set').hidden"), 'masaüstünde dişli Ayarlar’ı açıyor')
    p.click('#t-set'); p.wait_for_timeout(100)
    check(p.evaluate("()=>document.getElementById('app').dataset.tab") == 'studio', 'dişliye tekrar basınca önceki sekmeye dönüyor')
    p.screenshot(path=os.path.join(OUT, 'v13_desktop.png'))
    check(not errs, 'sayfa hatası yok ' + ('; '.join(errs) if errs else ''))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
