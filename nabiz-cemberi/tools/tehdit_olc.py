"""Tehdit ölçümü: sıradan oyuncu (dalga 15'e kadar 10 sn'de bir en verimli geliştirmeyi notanın en çok yarısıyla alır, sonra yalnız Asistan)
için dalga dalga en düşük nabız, geri çekilme sayısı ve dalgaya varış dakikası. Karar: orta oyunda düşman güçlensin mi (docs/yapilacaklar.md).

    python build.py && python tools/tehdit_olc.py [dakika=30]
"""
import os, sys, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DIST = os.path.join(R, 'dist')
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 30
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); threading.Thread(target=srv.serve_forever, daemon=True).start()
SETUP = """()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};nb.unlockAll();S.tipq=[];S.muted=true;
 S.mn={lv:1,ins:1};S.auto={lv:true,ord:false,ins:true,alb:false,asst:false};S.am.k={lv:1,rup:1,srup:1,tempo:1,def:1};S.am.b=0.5;nb.recalc()}"""
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    p = b.new_page(); p.goto('http://127.0.0.1:%d/' % srv.server_address[1]); p.wait_for_timeout(400); p.evaluate(SETUP)
    W = {}; asst = False; r0 = 0
    for t in range(2, MIN * 60 + 1, 2):
        p.evaluate("()=>window.__nb.ff(2)")
        st = p.evaluate("()=>({w:window.__nb.S.wave,b:window.__nb.S.bestWave,r:window.__nb.retreats,hp:window.__nb.hpFrac(),n:window.__nb.S.nota})")
        d = W.setdefault(st['w'], {'t': t, 'hp': 1, 'ret': 0, 'sec': 0}); d['hp'] = min(d['hp'], st['hp']); d['sec'] += 2
        if st['r'] > r0: d['ret'] += st['r'] - r0; r0 = st['r']
        if not asst and st['b'] >= 15:
            asst = True; p.evaluate("()=>{const S=window.__nb.S;S.mn={};S.auto.asst=true}")
        if t % 10 == 0 and not asst: p.evaluate("()=>{const nb=window.__nb;nb.autoReset();nb.autoTick()}")
        if t % 20 == 0 and asst: p.evaluate("()=>{const nb=window.__nb;nb.asstReset();nb.autoTick()}")
    fin = p.evaluate("()=>({b:window.__nb.S.bestWave,n:window.__nb.S.nota,r:window.__nb.retreats})"); b.close()
srv.shutdown()
print('| dalga | ilk varış (dk) | geçen süre (sn) | en düşük nabız | geri çekilme |'); print('|---|---|---|---|---|')
for w in sorted(W):
    d = W[w]; print('| %d | %.1f | %d | %%%d | %d |' % (w, d['t'] / 60, d['sec'], round(d['hp'] * 100), d['ret']))
print('\n%d dk sonunda: en iyi dalga %d, toplam geri çekilme %d, elde ♪%d' % (MIN, fin['b'], fin['r'], fin['n']))
