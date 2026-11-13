"""Albüm sonrası toparlanma: ilk koşu ile albümden sonraki koşu dakika dakika (en iyi dalga değil, o anki dalga ve gelir).
Model tools/album_olc.py ile aynı (dalga 15'e kadar 10 sn'de bir otomatik geliştirme, sonra Asistan). Albüm eşik dolunca çıkarılır.

    python build.py && python tools/toparlanma_olc.py [dakika=12]
"""
import os, sys, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DIST = os.path.join(R, 'dist')
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 12
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); threading.Thread(target=srv.serve_forever, daemon=True).start()
SETUP = """()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};nb.unlockAll();S.tipq=[];S.muted=true;
 S.mn={lv:1,ins:1};S.auto={lv:true,ord:false,ins:true,alb:false,asst:false};S.am.k={lv:1,rup:1,srup:1,tempo:1,def:1};S.am.b=0.5;nb.recalc()}"""
def fmt(n):
    for v, s in ((1e12, ' T'), (1e9, ' Mr'), (1e6, ' Mn'), (1e3, ' B')):
        if n >= v: return ('%.1f' % (n / v)).replace('.', ',') + s
    return str(int(n))
def run(p, secs, asst, rows, stop_album=False):
    for t in range(2, secs + 1, 2):
        p.evaluate("()=>window.__nb.ff(2)")
        st = p.evaluate("()=>({e:window.__nb.S.runEarned,w:window.__nb.S.wave,b:window.__nb.S.bestWave,r:window.__nb.rate(),th:window.__nb.albumTh?window.__nb.albumTh():0,n:Object.keys(window.__nb.S.lv).length})")
        if not asst[0] and st['b'] >= 15: asst[0] = True; p.evaluate("()=>{const S=window.__nb.S;S.mn={};S.auto.asst=true}")
        if t % 10 == 0 and not asst[0]: p.evaluate("()=>{const nb=window.__nb;nb.autoReset();nb.autoTick()}")
        if t % 20 == 0 and asst[0]: p.evaluate("()=>{const nb=window.__nb;nb.asstReset();nb.autoTick()}")
        if rows is not None and t % 60 == 0 and len(rows) < MIN: rows.append((t // 60, st['w'], st['r'], st['n']))
        if stop_album and st['e'] >= 1.5e7: return t
    return secs
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    p = b.new_page(); p.goto('http://127.0.0.1:%d/' % srv.server_address[1]); p.wait_for_timeout(400); p.evaluate(SETUP)
    asst = [False]; r1 = []
    t1 = run(p, 3600, asst, r1, stop_album=True)
    fans = p.evaluate("()=>{const nb=window.__nb;nb.releaseAlbum();return nb.S.hayran}")
    r2 = []; run(p, MIN * 60, asst, r2)
    b.close()
srv.shutdown()
print('İlk albüm %.1f dk, +%d hayran\n' % (t1 / 60, fans))
print('| dk | 1. koşu dalga | gelir/sn | enstrüman | albüm sonrası dalga | gelir/sn | enstrüman |'); print('|---|---|---|---|---|---|---|')
for a, c in zip(r1, r2): print('| %d | %d | %s | %d | %d | %s | %d |' % (a[0], a[1], fmt(a[2]), a[3], c[1], fmt(c[2]), c[3]))
