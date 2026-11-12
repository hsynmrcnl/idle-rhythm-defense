"""v63: kısa öğretici dalgayı durdurmaz, dışına dokunmak kapatır ve dokunuş yerine ulaşır, Escape kapatır;
albüm iki dokunuşla; geçersiz kayıt kodu onay sormadan reddedilir; albüm çipi eşiğin 3 katında ilerleme sürerken de; sekme adı rozeti okumaz.

    python build.py && python tests/v63_test.py
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

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe, args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch()
    p = b.new_page(viewport={'width': 1366, 'height': 768}); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.muted=true;S.nota=1e5;nb.recalc();nb.renderPanels()}")
    check(p.get_attribute('#studBadge', 'aria-hidden') == 'true', 'Stüdyo sekmesinin “yeni” rozeti ekran okuyucuya okunmaz')
    cv = p.locator('#cv').bounding_box(); p.mouse.click(cv['x'] + cv['width'] / 2, cv['y'] + cv['height'] / 2)
    p.wait_for_function("()=>window.__nb.playing", timeout=3000)
    # kısa öğretici dalgayı durdurmaz
    p.evaluate("()=>{const S=window.__nb.S;S.tipq=['look'];S.tutm=0;window.__nb.tutTick()}"); p.wait_for_timeout(300)
    t0 = p.evaluate("()=>window.__nb.wave&&window.__nb.wave.startT"); p.wait_for_timeout(1500)
    t1 = p.evaluate("()=>window.__nb.wave&&window.__nb.wave.startT")
    check(p.is_visible('#tutL') and t0 == t1, 'kısa öğretici açıkken dalga sürüyor (startT %s → %s)' % (t0, t1))
    # dışına tıkla: kapanır ve tıklama yerine ulaşır
    lv0 = p.evaluate("()=>window.__nb.S.lv.davul")
    p.evaluate("()=>window.__nb.setTab('studio')"); p.wait_for_timeout(200)
    p.evaluate("()=>{const S=window.__nb.S;S.tipq=['look'];S.tutm=1;window.__nb.tutTick()}"); p.wait_for_timeout(300)
    bb = p.locator('#lvb-davul').bounding_box()
    p.mouse.click(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2); p.wait_for_timeout(300)
    check(p.is_hidden('#tutL') and p.evaluate("()=>window.__nb.S.lv.davul") > lv0, 'kısa öğreticinin dışına dokunmak onu kapattı ve Yükselt işledi (Sv %d → %d)' % (lv0, p.evaluate("()=>window.__nb.S.lv.davul")))
    p.evaluate("()=>{const S=window.__nb.S;S.tipq=['look','book'];S.tutm=0;window.__nb.tutTick()}"); p.wait_for_timeout(300)
    p.keyboard.press('Escape'); p.wait_for_timeout(300)
    check(p.evaluate("()=>window.__nb.S.tipq.join(',')") == 'book', 'Escape yalnız o kısa öğreticiyi kapattı, sıradaki kaldı')
    p.evaluate("()=>{const S=window.__nb.S;S.tipq=[];S.tutm=0;window.__nb.tutTick()}")
    # ana öğretici hâlâ kilitli
    check(p.evaluate("()=>{const nb=window.__nb;return nb.TUT.length>0}"), 'ana öğretici değişmedi (v41/v44/v51 testleri ayrıca doğruluyor)')
    # albüm iki dokunuş
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.runEarned=2e7;nb.setTab('album');nb.renderPanels()}"); p.wait_for_timeout(200)
    p.click('#aBtn'); p.wait_for_timeout(200)
    check(p.evaluate("()=>window.__nb.S.runEarned") >= 2e7 and 'Emin' in p.text_content('#aBtn'), 'ilk dokunuş albümü çıkarmadı, onay istedi')
    p.click('#aBtn'); p.wait_for_timeout(300)
    check(p.evaluate("()=>window.__nb.S.albums.length") == 1, 'ikinci dokunuşta albüm çıktı')
    # albüm çipi 3x eşikte, ilerleme sürerken
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.unl.album=1;S.tipq=[];S.runEarned=2e9;nb.hintCheck()}")
    check(p.is_visible('#hintChip') and 'Albüm' in p.text_content('#hintChip'), 'eşiğin çok üstünde, ilerleme durmadan albüm çipi (%s)' % p.text_content('#hintChip'))
    # geçersiz kayıt kodu
    p.evaluate("()=>window.__nb.setTab('set')"); p.wait_for_timeout(200)
    p.fill('#saveCode', 'garip@@kod'); p.click('[data-act=loadCode]'); p.wait_for_timeout(300)
    check('Yüklenemedi' in p.text_content('#saveInfo') and 'Tekrar' not in p.text_content('[data-act=loadCode]'), 'geçersiz kod onay sormadan reddedildi (%s)' % p.text_content('#saveInfo'))
    check(not errs, 'sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v63 geçti')
sys.exit(1 if fails else 0)
