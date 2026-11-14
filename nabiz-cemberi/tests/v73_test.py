"""v73: takılan oyuncuya Asistan (3 geri çekilme, dalga ≥6, Uyum şartı yok) ve sahnede anlatan kısa öğretici; Albüm sekmesi dalga 25'te; ileri sarmada susturma süreleri geri alınır.

    python build.py && python tests/v73_test.py
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
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;S.unl={studio:1,coll:1,tap:1};S.tipq=[];S.tutm=0;S.bestWave=8;nb.setWave(8)}")
    p.evaluate("()=>{const nb=window.__nb;nb.retreatNow();nb.retreatNow();nb.unlCheck()}")
    check(not p.evaluate("()=>!!window.__nb.S.unl.asst"), '2 geri çekilmede Asistan yok')
    p.evaluate("()=>{const nb=window.__nb;nb.retreatNow();nb.unlCheck();nb.S.tipq=nb.S.tipq.filter(k=>k==='asst');nb.S.tutm=0}"); p.wait_for_timeout(500)
    st = p.evaluate("()=>[!!window.__nb.S.unl.asst,window.__nb.asstOn(),document.getElementById('tutLT').textContent,!document.getElementById('tutL').hidden]")
    check(st[0] and st[1] and st[3] and 'Asistan' in st[2], 'takılan oyuncuya Asistan geldi, kısa öğretici sahnede (%s)' % st)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tipq=[];S.tutm=0;S.bestWave=25;nb.unlCheck()}")
    check(p.evaluate("()=>!!window.__nb.S.unl.album"), 'Albüm sekmesi dalga 25’te açıldı')
    r = p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.slots=['davul',null,null,null];S.pat.A[0]=S.pat.A[0].map((v,i)=>i%2===0?1:0);S.lv.davul=5;nb.recalc();const e0=S.runEarned;nb.ff(60);const e1=S.runEarned;nb.ff(60);return [e1-e0,S.runEarned-e1]}")
    check(r[1] > r[0] * 0.3, 'ardışık ileri sarmalarda gelir sürüyor (%s)' % r)
    check(not errs, 'sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v73 geçti')
sys.exit(1 if fails else 0)
