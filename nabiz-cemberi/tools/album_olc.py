"""İlk albüme varış: sıradan oyuncu modeli (tools/tehdit_olc.py ile aynı: dalga 15'e kadar 10 sn'de bir en verimli geliştirme, notanın en çok yarısı; sonra Asistan).
Dakika dakika dönem kazancı (runEarned) / albüm eşiği (albumTh), dalga ve gelir. Albüm sekmesi eşiğin yarısında açılır.

    python build.py && python tools/album_olc.py [dakika=60]
"""
import os, sys, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DIST = os.path.join(R, 'dist')
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 60
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); threading.Thread(target=srv.serve_forever, daemon=True).start()
SETUP = """()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};nb.unlockAll();S.tipq=[];S.muted=true;
 S.mn={lv:1,ins:1};S.auto={lv:true,ord:false,ins:true,alb:false,asst:false};S.am.k={lv:1,rup:1,srup:1,tempo:1,def:1};S.am.b=0.5;nb.recalc()}"""
def fmt(n):
    for v, s in ((1e12, ' T'), (1e9, ' Mr'), (1e6, ' Mn'), (1e3, ' B')):
        if n >= v: return ('%.1f' % (n / v)).replace('.', ',') + s
    return str(int(n))
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    p = b.new_page(); p.goto('http://127.0.0.1:%d/' % srv.server_address[1]); p.wait_for_timeout(400); p.evaluate(SETUP)
    th = p.evaluate("()=>1.5e7"); asst = False; rows = []; half = full = None
    for t in range(2, MIN * 60 + 1, 2):
        p.evaluate("()=>window.__nb.ff(2)")
        st = p.evaluate("()=>({e:window.__nb.S.runEarned,w:window.__nb.S.wave,b:window.__nb.S.bestWave,r:window.__nb.rate()})")
        if not asst and st['b'] >= 15: asst = True; p.evaluate("()=>{const S=window.__nb.S;S.mn={};S.auto.asst=true}")
        if t % 10 == 0 and not asst: p.evaluate("()=>{const nb=window.__nb;nb.autoReset();nb.autoTick()}")
        if t % 20 == 0 and asst: p.evaluate("()=>{const nb=window.__nb;nb.asstReset();nb.autoTick()}")
        if half is None and st['e'] >= th / 2: half = t
        if full is None and st['e'] >= th: full = t
        if t % 300 == 0: rows.append((t // 60, st['b'], st['e'], st['r']))
    b.close()
srv.shutdown()
print('| dk | en iyi dalga | dönem kazancı | eşiğe oran | gelir/sn |'); print('|---|---|---|---|---|')
for m, w, e, r in rows: print('| %d | %d | ♪%s | %%%d | %s |' % (m, w, fmt(e), round(100 * e / th), fmt(r)))
print('\nAlbüm sekmesi (eşiğin yarısı): %s · ilk albüm çıkarılabilir: %s' % ('%.1f dk' % (half / 60) if half else 'yok', '%.1f dk' % (full / 60) if full else 'yok (%d dk içinde)' % MIN))
