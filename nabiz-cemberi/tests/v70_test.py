"""v70: Cep LCD teması — Görünüm'de listede, alınınca uygulanıyor, LCD süzgeci ve 8-bit ses ayarı açık; 2 albümde ücretsiz açılır.

    python build.py && python tests/v70_test.py
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
    p = b.new_page(viewport={'width': 1280, 'height': 800})
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.nota=2e7;nb.recalc();nb.setTab('look');nb.renderPanels()}")
    check(p.locator('[data-id=lcd]').count() > 0, 'Cep LCD Görünüm’de listeleniyor')
    p.evaluate("()=>{window.__nb.S.themes.lcd=1;window.__nb.renderPanels()}")
    p.click('[data-act=theme][data-id=lcd]'); p.wait_for_timeout(300)
    st = p.evaluate("()=>{const S=window.__nb.S;return [S.theme,getComputedStyle(document.documentElement).getPropertyValue('--acc').trim()]}")
    check(st[0] == 'lcd' and st[1].lower() == '#9bbc0f', 'tema uygulandı, arayüz yeşil (%s)' % st)
    cv = p.locator('#cv').bounding_box(); p.mouse.click(cv['x'] + cv['width'] / 2, cv['y'] + cv['height'] / 2); p.wait_for_timeout(1500)
    check(not errs, 'LCD süzgeci ve 8-bit sesle çalarken sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v70 geçti')
sys.exit(1 if fails else 0)
