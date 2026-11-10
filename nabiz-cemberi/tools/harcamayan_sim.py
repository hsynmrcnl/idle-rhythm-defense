"""Harcamayan oyuncu simülasyonu (docs/denge_d15.md ölçüm planı).
Yeni oyun, Kolay, otomatik müzik; ilk 3 oyun-dakikası menajer mantığıyla (autoBuyPick) harcar, sonra:
  A) hiç harcamaz   B) yalnız harcama ipucuna dokunur (ilerleme 2 dk durunca ya da son 60 sn'de geri çekilme olunca, 30 sn'de bir)
  C) hiç dokunmaz, v49 Asistan açık (dalga 15'ten sonra 20 sn'de bir, notanın en çok %25'i).

    python build.py && python tools/harcamayan_sim.py [dakika]
"""
import os, sys, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DIST = os.path.join(R, 'dist')
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 30
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); threading.Thread(target=srv.serve_forever, daemon=True).start()
SETUP = """()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};nb.unlockAll();S.tipq=[];S.muted=true;S.d3.own=1;
 S.mn={lv:1,ord:1,ins:1};S.auto={lv:true,ord:true,ins:true,alb:false,asst:false};S.am.k={lv:1,rup:1,srup:1,tempo:1,def:1};S.am.b=0.9;nb.recalc()}"""
def run(b, mode):
    ctx = b.new_context(); p = ctx.new_page(); p.goto('http://127.0.0.1:%d/' % srv.server_address[1]); p.wait_for_timeout(400)
    p.evaluate(SETUP); rows = []; best_t = 0; best = 0; ret_t = -999; hints = 0; ret0 = 0
    for sec in range(0, MIN * 60, 10):
        p.evaluate("()=>window.__nb.ff(10)")
        t = sec + 10
        if t <= 180:
            p.evaluate("()=>{const nb=window.__nb;for(let j=0;j<2;j++){nb.autoReset();nb.autoTick()}}")
        elif t == 190:
            p.evaluate("()=>{const S=window.__nb.S;S.mn={ord:1,ins:1};S.auto={ord:false,ins:false,alb:false,asst:false}}")  # oyuncu artık harcamıyor
        st = p.evaluate("()=>({w:window.__nb.S.wave,b:window.__nb.S.bestWave,r:window.__nb.retreats,n:window.__nb.S.nota,rate:window.__nb.rate()})")
        if st['b'] > best: best, best_t = st['b'], t
        if st['r'] > ret0: ret0, ret_t = st['r'], t
        if mode == 'C' and t > 180 and t % 20 == 0 and st['b'] >= 15:
            p.evaluate("()=>{const nb=window.__nb;nb.S.auto.asst=true;nb.asstReset();nb.autoTick()}")
        if mode == 'B' and t > 180 and t % 30 == 0 and (t - best_t > 120 or t - ret_t < 60):
            while p.evaluate("()=>window.__nb.hintSim()"): hints += 1
        if t % 60 == 0: rows.append((t // 60, st['w'], st['b'], st['n'], st['rate'], st['r'], hints))
    ctx.close(); return rows
def fmt(n):
    for v, s in ((1e12, ' T'), (1e9, ' Mr'), (1e6, ' Mn'), (1e3, ' B')):
        if n >= v: return ('%.1f' % (n / v)).replace('.', ',') + s
    return str(int(n))
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    A = run(b, 'A'); B = run(b, 'B'); C = run(b, 'C'); b.close()
srv.shutdown()
print('| dk | A: dalga (en iyi) | A: nota | A: geri | B: dalga (en iyi) | B: nota | B: geri | B: öneri alımı | C: dalga (en iyi) | C: nota | C: geri |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for a, c, d in zip(A, B, C):
    if a[0] in (3, 5, 10, 15, 20, 25, 30, 45, 60):
        print('| %d | %d (%d) | %s | %d | %d (%d) | %s | %d | %d | %d (%d) | %s | %d |' % (a[0], a[1], a[2], fmt(a[3]), a[5], c[1], c[2], fmt(c[3]), c[5], c[6], d[1], d[2], fmt(d[3]), d[5]))
