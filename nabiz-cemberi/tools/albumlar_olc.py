"""Art arda albümler: album_olc.py'nin oyuncu modeli (dalga 15'e kadar 10 sn'de bir en verimli geliştirme, sonra Asistan),
eşik dolar dolmaz albüm çıkarır. Her albümün dakikası, hayranı, dalgası ve gelir çarpanı. ALB_GROW karşılaştırması için.

    python build.py && python tools/albumlar_olc.py [dakika=90] [alb_grow=0.5]
"""
import os, sys, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DIST = os.path.join(R, 'dist')
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 90
GROW = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); threading.Thread(target=srv.serve_forever, daemon=True).start()
SETUP = """(g)=>{const nb=window.__nb,S=nb.S;nb.albGrow=g;S.tut={s:0,done:true};nb.unlockAll();S.tipq=[];S.muted=true;
 S.mn={lv:1,ins:1};S.auto={lv:true,ord:false,ins:true,alb:false,asst:false};S.am.k={lv:1,rup:1,srup:1,tempo:1,def:1};S.am.b=0.5;nb.recalc()}"""
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    p = b.new_page(); p.goto('http://127.0.0.1:%d/' % srv.server_address[1]); p.wait_for_timeout(400); p.evaluate(SETUP, GROW)
    asst = False; out = []; last = 0
    for t in range(2, MIN * 60 + 1, 2):
        p.evaluate("()=>window.__nb.ff(2)")
        st = p.evaluate("()=>{const S=window.__nb.S;return {e:S.runEarned,th:1.5e7*Math.pow(4,S.albums.length),w:S.wave,b:S.bestWave,n:S.albums.length,h:S.hayran}}")
        if not asst and st['b'] >= 15: asst = True; p.evaluate("()=>{const S=window.__nb.S;S.mn={};S.auto.asst=true}")
        if t % 10 == 0 and not asst: p.evaluate("()=>{const nb=window.__nb;nb.autoReset();nb.autoTick()}")
        if t % 20 == 0 and asst: p.evaluate("()=>{const nb=window.__nb;nb.asstReset();nb.autoTick()}")
        if st['e'] >= st['th']:
            w = st['w']; p.evaluate("()=>window.__nb.releaseAlbum()")
            h = p.evaluate("()=>window.__nb.S.hayran")
            out.append((round(t / 60, 1), round((t - last) / 60, 1), st['n'] + 1, h - st['h'], h, w, round(1 + 0.05 * h, 2))); last = t
    b.close()
srv.shutdown()
print('### ALB_GROW=%s · %d dk\n' % (GROW, MIN))
print('| albüm | dakika | süre (dk) | +hayran | hayran | çıkarken dalga | gelir ×hayran |\n|---|---|---|---|---|---|---|')
for m, d, n, f, h, w, g in out: print('| %d | %s | %s | %d | %d | %d | ×%s |' % (n, str(m).replace('.', ','), str(d).replace('.', ','), f, h, w, str(g).replace('.', ',')))
if not out: print('| – | albüm yok | | | | | |')
