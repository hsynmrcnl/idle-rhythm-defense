"""v67: Escape bilgi kutusunu ve Ayarlar'ı kapatır; örnek şarkıdan girilen sekmeye dönülür; Aç düğmesinin erişilebilir adı; Dalga durumu başlığı.

    python build.py && python tests/v67_test.py
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
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    errs = []
    p = b.new_page(viewport={'width': 1366, 'height': 768})
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;nb.setTab('def');nb.renderPanels()}")
    check(p.evaluate("()=>document.querySelector('[data-sec=siege] .ht').textContent").startswith('Dalga durumu'), 'Savunma’nın ilk kartı “Dalga durumu”')
    p.click('[data-sec=siege] [data-act=info]'); p.wait_for_timeout(100)
    check(p.is_visible('[data-sec=siege] .info'), 'bilgi kutusu açık')
    p.keyboard.press('Escape'); p.wait_for_timeout(100)
    check(not p.is_visible('[data-sec=siege] .info'), 'Escape bilgi kutusunu kapattı')
    p.click('#t-set'); p.wait_for_timeout(150)
    check(p.is_visible('#p-set'), 'Ayarlar açık')
    p.keyboard.press('Escape'); p.wait_for_timeout(150)
    check(not p.is_visible('#p-set') and p.is_visible('#p-def'), 'Escape Ayarlar’ı kapatıp Savunma’ya döndü')
    p.evaluate("()=>{const nb=window.__nb;nb.setTab('coll')}"); p.wait_for_timeout(100)
    lab = p.locator('#collList .irow.locked button').first.get_attribute('aria-label') or ''
    check(lab.startswith('Aç') and len(lab) > 8 and '♪' in lab, 'Aç düğmesinin adı enstrümanı söylüyor: “%s”' % lab)
    p.evaluate("()=>{const nb=window.__nb;nb.setTab('book');nb.enterDemo(0)}"); p.wait_for_timeout(300)
    p.evaluate("()=>window.__nb.setTab('look')"); p.wait_for_timeout(150)
    p.keyboard.press('Escape'); p.wait_for_timeout(300)
    check(not p.evaluate("()=>window.__nb.demoMode") and p.is_visible('#p-book'), 'örnek şarkıdan çıkınca girilen sekmeye (Kitap) dönüldü')
    check(not errs, 'sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v67 geçti')
sys.exit(1 if fails else 0)
