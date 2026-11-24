"""v79: nota birikince Görünüm'de alınabilecek en ucuz şey (3D sahne / tema) bir kez haber verilir, Görünüm sekmesinde rozet.

    python build.py && python tests/v79_test.py
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
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.d3.own=0;S.nota=5e5;nb.setTab('studio');nb.autoTick()}")
    check('3D' not in p.inner_text('#msg'), 'nota fiyatın 2 katına ulaşmadan haber yok')
    p.evaluate("()=>{const nb=window.__nb;nb.S.nota=1.2e6;nb.autoTick()}"); p.wait_for_timeout(100)
    check('3D sahne' in p.inner_text('#msg') and p.is_visible('#shopBadge'), 'nota birikince 3D sahne haber verildi, Görünüm’de rozet (“%s”)' % p.inner_text('#msg'))
    p.evaluate("()=>{window.__nb.setTab('shop')}"); p.wait_for_timeout(100)
    check(p.is_hidden('#shopBadge'), 'Mağaza açılınca rozet kalktı')
    p.evaluate("()=>{const nb=window.__nb;document.getElementById('msg').textContent='';nb.autoTick()}")
    check('3D' not in p.inner_text('#msg'), 'aynı şey ikinci kez haber verilmiyor')
    check(not errs, 'sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v79 geçti')
sys.exit(1 if fails else 0)
