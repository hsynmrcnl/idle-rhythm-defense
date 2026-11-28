"""Dalga baskısı (kule savunma yeteneğinin eğri denetimi, oyunun içinden ölçülmüş hâli).
Her ilk kez oynanan dalga için: gönderilen toplam can (WHP), oyuncunun etkin hasar/sn'si (dps × globalMDmg),
dalga süresi → baskı = can / (hasar/sn × süre). 1'in üstü duvar, 0,6–0,95 hedef bant, altı kolay.
Ayrıca en düşük nabız, geri çekilme, bekleyen nota (gelirin kaç saniyesi), Davul'un hasar payı.
Oyuncu modelleri tools/acilis_olc.py ile aynı: pasif, tutumlu, hizli.

    python build.py && python tools/baski_olc.py [dakika=40] [model ...]
"""
import os, sys, threading, functools, http.server, socketserver, json
from playwright.sync_api import sync_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DIST = os.path.join(R, 'dist')
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 40
# deney anahtarları (ortam değişkeni): DVK=Davul yavaşlama eşiği, ASSTW=Asistan açılış dalgası, BULK=her 30 sn notanın bu kesrini en verimli alımlara harca (toplu harca)
DVK = os.environ.get('DVK'); ASSTW = os.environ.get('ASSTW'); BULK = float(os.environ.get('BULK', '0')); TAG = os.environ.get('TAG', '')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = """()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};S.unl={studio:1,coll:1,tap:1};S.tipq=[];S.muted=true;S.pat.A[0]=S.pat.A[0].map((v,i)=>i%4===0?1:0);nb.recalc()}"""
SNAP = """()=>{const nb=window.__nb,S=nb.S,A=nb.STA.rd;let tot=0,dv=0;S.slots.forEach((id,i)=>{tot+=A[i]||0;if(id==='davul')dv+=A[i]||0});
 return {w:S.wave,b:S.bestWave,h:nb.hpFrac(),d:nb.dps()*nb.globalMDmg(),r:nb.rate(),n:S.nota,ret:nb.retreats,dv:tot>0?dv/tot:0,whp:nb.WHP,ins:S.slots.filter(Boolean).length}}"""
def run(model):
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        p = b.new_page(); p.goto('http://127.0.0.1:%d/' % srv.server_address[1]); p.wait_for_timeout(400); p.evaluate(BASE)
        if DVK: p.evaluate('v=>{window.__nb.dvK=v}', int(DVK))
        if ASSTW: p.evaluate('v=>{window.__nb.UNL_W.asst=v}', int(ASSTW))
        if model == 'hizli': p.evaluate("()=>{const S=window.__nb.S;S.mn={lv:1,ins:1};S.auto={lv:true,ord:false,ins:true,alb:false,asst:false};S.am.k={lv:1,rup:1,srup:1,tempo:1,def:1};S.am.b=0.5}")
        asst = False; waves = {}; cur = None; best = 0
        for t in range(2, MIN * 60 + 1, 2):
            p.evaluate("()=>{window.__nb.ff(2);window.__nb.unlCheck();window.__nb.S.tipq=[]}")
            s = p.evaluate(SNAP)
            if model == 'hizli':
                if not asst and s['b'] >= 15: asst = True; p.evaluate("()=>{const S=window.__nb.S;S.mn={};S.auto.asst=true}")
                if t % 10 == 0 and not asst: p.evaluate("()=>{const nb=window.__nb;nb.autoReset();nb.autoTick()}")
            if model == 'tutumlu' and t % 20 == 0:
                p.evaluate("()=>{const nb=window.__nb,S=nb.S;let left=S.nota*0.25;for(let i=0;i<40;i++){const k=nb.asstPick(left);if(!k)break;const n0=S.nota;nb.hintApplyK(k);const sp=n0-S.nota;if(sp<=0)break;left-=sp}}")
            if (model != 'hizli' or asst) and t % 20 == 0 and model != 'tutumlu': p.evaluate("()=>{const nb=window.__nb;if(nb.asstOn()){nb.asstReset();nb.autoTick()}}")
            if BULK and t % 30 == 0: p.evaluate("f=>{const nb=window.__nb,S=nb.S;let left=S.nota*f;for(let i=0;i<60;i++){const k=nb.asstPick(left);if(!k)break;const n0=S.nota;nb.hintApplyK(k);const sp=n0-S.nota;if(sp<=0)break;left-=sp}}", BULK)
            w = s['w']
            if cur and w != cur['w']:
                cur['dur'] = t - cur['t0']; cur['hp'] = float(s['whp'].get(str(cur['w']), 0)); waves.setdefault(cur['w'], cur); cur = None
            if cur is None and w > best:
                best = w; cur = {'w': w, 't0': t, 'd': s['d'], 'mh': 1, 'r': s['r'], 'n': s['n'], 'dv': s['dv'], 'ins': s['ins'], 'ret0': s['ret'], 'min': t / 60}
            if cur: cur['mh'] = min(cur['mh'], s['h']); cur['ret'] = s['ret'] - cur['ret0']
        b.close()
    out = []
    for w in sorted(waves):
        c = waves[w]
        pr = c['hp'] / max(1e-9, c['d'] * c['dur']) if c['dur'] else 0
        out.append(dict(w=w, dk=round(c['min'], 1), baski=round(pr, 2), nabiz=round(c['mh'] * 100), geri=c['ret'], banka=round(c['n'] / max(1e-9, c['r'])), davul=round(c['dv'] * 100), ens=c['ins'], sure=c['dur']))
    return out
res = {}
for model in (sys.argv[2:] or ['pasif', 'tutumlu', 'hizli']):
    rows = run(model); res[model] = rows
    print('\n### %s\n' % model)
    print('| dalga | dk | baskı | en düşük nabız | geri çekilme | bekleyen nota (sn gelir) | Davul payı | enstrüman | süre sn |'); print('|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        if r['w'] <= 5 or r['w'] % 5 == 0 or r['baski'] > 1 or r['geri']: print('| %(w)d | %(dk)s | %(baski).2f | %%%(nabiz)d | %(geri)d | %(banka)d | %%%(davul)d | %(ens)d | %(sure)d |' % r)
    ps = [r['baski'] for r in rows if r['w'] > 2]
    if ps:
        lo = sum(1 for x in ps if x < 0.6); band = sum(1 for x in ps if 0.6 <= x <= 0.95); hi = sum(1 for x in ps if x > 0.95)
        print('\nBant: kolay (<0,6) %d · hedef (0,6–0,95) %d · duvar/sınır (>0,95) %d · son dalga %d' % (lo, band, hi, rows[-1]['w']))
json.dump(res, open(os.path.join(R, 'build', 'baski_olc_%s%s.json' % ('_'.join(res), TAG)), 'w'), ensure_ascii=False, indent=1)
srv.shutdown()
