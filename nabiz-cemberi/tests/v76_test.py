"""v76: kısa öğretici açıkken Asistan çalışır; masaüstünde sekmeler kırpılmaz; Atla erken basılınca dörtlük kurulur.

    python build.py && python tests/v76_test.py
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
    # Atla 3. adımda
    p.keyboard.press('Enter'); p.wait_for_timeout(5600)
    p.evaluate("()=>{window.__nb.S.pat.A[0][0]=1}")  # 1 vuruşla atla (oyuncu turu: 3. adımda)
    st0 = p.evaluate("()=>window.__nb.tutStep")
    p.click('#tutSkipL'); p.wait_for_timeout(300)
    n = p.evaluate("()=>window.__nb.S.pat.A[0].filter(Boolean).length")
    check(n >= 4, 'öğretici erken atlanınca davulda en az dörtlük var (%d vuruş, adım %d)' % (n, st0))
    # Asistan kısa öğretici açıkken
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;nb.unlockAll();S.auto.asst=true;S.nota=1e5;S.tipq=['def'];S.tutm=0;nb.recalc()}")
    p.wait_for_timeout(400)
    r = p.evaluate("()=>{const nb=window.__nb,S=nb.S,open=!!nb.ovCur(),n0=S.nota;nb.asstReset();nb.autoTick();return [open,n0-S.nota]}")
    check(r[0] and r[1] > 0, 'kısa öğretici açıkken Asistan alım yaptı (%s)' % r)
    p.evaluate("()=>{const S=window.__nb.S;S.tipq=[];S.tutm=0;window.__nb.setTab('studio')}"); p.wait_for_timeout(300)
    t = p.evaluate("()=>{const bar=document.querySelector('.tabs').getBoundingClientRect();return [...document.querySelectorAll('.tabs .tab')].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect();return [e.textContent.trim(),r.left>=bar.left-1&&r.right<=bar.right+1]})}")
    check(len(t) >= 5 and all(ok for _, ok in t), 'masaüstünde bütün sekmeler tam görünüyor (%s)' % [n for n, ok in t if not ok])
    check(not errs, 'sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v76 geçti')
sys.exit(1 if fails else 0)
