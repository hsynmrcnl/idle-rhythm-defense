"""v68: hızlı geçiş — en iyi dalganın gerisindeyken dalga hızlı akar; sızma ya da baskında normal hız; en iyi dalgada normal.

    python build.py && python tests/v68_test.py
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
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.muted=true;S.lv.davul=40;S.bestWave=1;nb.recalc()}")
    def waves(sec, best):
        return p.evaluate("([s,b])=>{const nb=window.__nb,S=nb.S;S.bestWave=b;nb.setWave(1);const w0=S.wave;nb.ff(s);return S.wave-w0}", [sec, best])
    n_norm = waves(60, 1)
    n_fast = waves(60, 40)
    check(n_fast >= n_norm * 1.6 and n_fast > n_norm, 'en iyi dalganın gerisinde dalgalar hızlı (60 sn: %d dalga, normalde %d)' % (n_fast, n_norm))
    st = p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.bestWave=40;nb.setWave(3);nb.ff(0.5);const a=nb.fastNow;nb.wave.leaked=true;nb.ff(0.5);return [a,nb.fastNow]}")
    check(st[0] and not st[1], 'düşman sızınca o dalga normal hıza döner (%s)' % st)
    st = p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.bestWave=40;nb.setWave(5);nb.ff(0.5);return [nb.wave.raid,nb.fastNow]}")
    check(not (st[0] and st[1]), 'baskın dalgası normal hızda (%s)' % st)
    check(not errs, 'sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v68 geçti')
sys.exit(1 if fails else 0)
