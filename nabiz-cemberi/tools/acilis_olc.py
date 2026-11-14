"""Açılış takvimi ve tehdit: üç oyuncu modeli, dakika dakika dalga, en düşük nabız, geri çekilme ve açılan bölümler.
  pasif  : öğretici Atla ile geçilmiş (dörtlük davul), hiçbir şey almaz (Asistan açılırsa o çalışır)
  tutumlu: 20 sn'de bir notanın %25'iyle en verimli alım (Asistan mantığı, baştan)
  hizli  : 10 sn'de bir notanın %50'siyle otomatik geliştirme (tools/album_olc.py modeli), dalga 15'ten sonra Asistan

    python build.py && python tools/acilis_olc.py [dakika=40]
"""
import os, sys, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DIST = os.path.join(R, 'dist')
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 40
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = """()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};S.unl={studio:1,coll:1,tap:1};S.tipq=[];S.muted=true;S.pat.A[0]=S.pat.A[0].map((v,i)=>i%4===0?1:0);nb.recalc()}"""
def fmt(n):
    for v, s in ((1e12, ' T'), (1e9, ' Mr'), (1e6, ' Mn'), (1e3, ' B')):
        if n >= v: return ('%.1f' % (n / v)).replace('.', ',') + s
    return str(int(n))
def run(model):
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        p = b.new_page(); p.goto('http://127.0.0.1:%d/' % srv.server_address[1]); p.wait_for_timeout(400); p.evaluate(BASE)
        if model == 'hizli': p.evaluate("()=>{const S=window.__nb.S;S.mn={lv:1,ins:1};S.auto={lv:true,ord:false,ins:true,alb:false,asst:false};S.am.k={lv:1,rup:1,srup:1,tempo:1,def:1};S.am.b=0.5}")
        asst = False; rows = []; seen = set(); opened = []; mhp = 1; ret0 = p.evaluate("()=>window.__nb.retreats")
        for t in range(2, MIN * 60 + 1, 2):
            p.evaluate("()=>{window.__nb.ff(2);window.__nb.unlCheck();window.__nb.S.tipq=[]}")
            st = p.evaluate("()=>({w:window.__nb.S.wave,b:window.__nb.S.bestWave,h:window.__nb.hpFrac(),u:Object.keys(window.__nb.S.unl).filter(k=>window.__nb.S.unl[k]),r:window.__nb.rate(),e:window.__nb.S.runEarned,ret:window.__nb.retreats})")
            mhp = min(mhp, st['h'])
            for k in st['u']:
                if k not in seen: seen.add(k); opened.append((t / 60, st['b'], k))
            if model == 'hizli':
                if not asst and st['b'] >= 15: asst = True; p.evaluate("()=>{const S=window.__nb.S;S.mn={};S.auto.asst=true}")
                if t % 10 == 0 and not asst: p.evaluate("()=>{const nb=window.__nb;nb.autoReset();nb.autoTick()}")
            if model == 'tutumlu' and t % 20 == 0:
                p.evaluate("()=>{const nb=window.__nb,S=nb.S;let left=S.nota*0.25;for(let i=0;i<40;i++){const k=nb.asstPick(left);if(!k)break;const n0=S.nota;nb.hintApplyK(k);const sp=n0-S.nota;if(sp<=0)break;left-=sp}}")
            if (model != 'hizli' or asst) and t % 20 == 0 and model != 'tutumlu': p.evaluate("()=>{const nb=window.__nb;if(nb.asstOn()){nb.asstReset();nb.autoTick()}}")
            if t % 60 == 0: rows.append((t // 60, st['w'], st['b'], round(mhp * 100), st['ret'] - ret0, st['r'], st['e'])); mhp = 1
        b.close()
    return rows, opened
for model in (sys.argv[2:] or ['pasif', 'tutumlu', 'hizli']):
    rows, opened = run(model)
    print('\n### %s\n' % model)
    print('| dk | dalga | en iyi | en düşük nabız | geri çekilme (toplam) | gelir/sn | dönem kazancı |'); print('|---|---|---|---|---|---|---|')
    for m, w, bw, h, rt, r, e in rows:
        if m <= 10 or m % 5 == 0: print('| %d | %d | %d | %%%d | %d | %s | ♪%s |' % (m, w, bw, h, rt, fmt(r), fmt(e)))
    print('\nAçılışlar: ' + ' · '.join('%s (%.1f dk, d%d)' % (k, t, w) for t, w, k in opened if k not in ('studio', 'coll', 'tap')))
srv.shutdown()
