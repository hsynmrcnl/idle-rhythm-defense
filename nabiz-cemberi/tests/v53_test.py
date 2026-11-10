"""v53: boş sahne yeri varken öneri çipi ve Asistan önce yeni enstrüman açar; dil değişince açık sekme korunur.

    python build.py && python tests/v53_test.py
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
    ctx = b.new_context(viewport={'width': 1366, 'height': 768}); p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;S.tipq=[];S.unl={studio:1,coll:1,tap:1};S.nota=5000;nb.recalc()}")
    n = p.evaluate("()=>window.__nb.hintSim()")
    check('Yeni' in n and p.evaluate("()=>window.__nb.S.slots.filter(Boolean).length") == 2, 'öneri: boş yer varken yeni enstrüman açıldı ve sahneye kondu (%s)' % n)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.unl.asst=1;S.unl.syn=1;nb.unlCheck(true);S.tipq=[];S.tutm=0;S.auto.asst=true;S.nota=1e5;nb.asstReset();nb.autoTick()}")
    check(p.evaluate("()=>window.__nb.S.slots.filter(Boolean).length") >= 3, 'Asistan: boş yere yeni enstrüman koydu')
    p.evaluate("()=>{const S=window.__nb.S;S.slots=S.slots.map(x=>x||'davul');window.__nb.recalc()}")
    n = p.evaluate("()=>{window.__nb.S.nota=1e5;return window.__nb.hintSim()}")
    check(n and 'Yeni' not in n, 'yer doluyken eski öneri (%s)' % n)
    # dil
    p.evaluate("()=>{const nb=window.__nb;nb.unlockAll();nb.S.tipq=[];nb.unlVis();nb.setTab('def')}"); p.wait_for_timeout(200)
    p.click('#langBtn'); p.wait_for_load_state('load'); p.wait_for_timeout(700)
    check(p.evaluate("()=>document.getElementById('app').dataset.tab") == 'def' and p.evaluate("()=>window.__nb.S.lang") == 'en', 'dil değişince Savunma sekmesi açık kaldı')
    p.click('#langBtn'); p.wait_for_load_state('load'); p.wait_for_timeout(700)
    check(p.evaluate("()=>document.getElementById('app').dataset.tab") == 'def' and p.evaluate("()=>window.__nb.S.lang") == 'tr', 'geri dönünce de aynı sekme')
    p.reload(); p.wait_for_timeout(600)
    check(p.evaluate("()=>document.getElementById('app').dataset.tab") == 'studio', 'normal yenilemede varsayılan sekme')
    check(not errs, 'sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v53 geçti')
sys.exit(1 if fails else 0)
