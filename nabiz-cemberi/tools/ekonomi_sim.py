"""Ekonomi simülasyonu: yeni oyun, Kolay, otomatik müzik açık; bot her 10 sn'lik hızlı ileri sarmada
Analiz'in önerisiyle (menajerin otomatik geliştir mantığı, autoBuyPick) en fazla iki şey alır, boş yere enstrüman koyar.
Dakika dakika dalga, nota/sn, hasar/sn, geri çekilme ve şarj patlamasını yazar. Şarj açık ve kapalı iki koşu karşılaştırılır.

    python build.py && python tools/ekonomi_sim.py [dakika]      → docs/ekonomi_sim.md
"""
import os, sys, json, threading, functools, http.server, socketserver, time
from playwright.sync_api import sync_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DIST = os.path.join(R, 'dist')
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 60
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
SETUP = """own=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};nb.unlockAll();S.muted=true;S.d3.own=own;
 S.mn={lv:1,ord:1,ins:1};S.auto={lv:true,ord:true,ins:true,alb:false};S.am.k={lv:1,rup:1,srup:1,tempo:1,def:1};S.am.b=0.9;nb.recalc()}"""
MINUTE = """()=>{const nb=window.__nb,S=nb.S;let ret=0,w0=S.wave;for(let k=0;k<6;k++){nb.ff(10);if(S.wave<w0)ret++;w0=S.wave;for(let j=0;j<2;j++){nb.autoReset();nb.autoTick()}}
 return {wave:S.wave,best:S.bestWave,nota:S.nota,run:S.runEarned,rate:nb.rate(),dps:nb.dps(),kills:S.kills,ins:S.slots.filter(Boolean).length,slots:S.slots.length,ret,blast:nb.blastN,acc:S.pat.A.slice(0,S.slots.length).reduce((a,r)=>a+r.filter(v=>v===2).length,0),lv:Object.values(S.lv).reduce((a,b)=>a+b,0)}}"""
def run(b, own):
    ctx = b.new_context(viewport={'width': 1280, 'height': 800}); page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)))
    page.goto('http://127.0.0.1:%d/' % PORT); page.wait_for_timeout(400)
    page.evaluate(SETUP, own)
    rows = []
    for m in range(1, MIN + 1):
        r = page.evaluate(MINUTE); r['min'] = m; rows.append(r)
    ctx.close(); return rows
def fmt(n):
    for v, s in ((1e12, ' T'), (1e9, ' Mr'), (1e6, ' Mn'), (1e3, ' B')):
        if n >= v: return ('%.1f' % (n / v)).replace('.', ',') + s
    return str(int(n))
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    errs = []; t0 = time.time(); A = run(b, 1); B = run(b, 0)
    b.close()
srv.shutdown()
marks = [m for m in (1, 2, 5, 10, 15, 20, 30, 45, 60, 90, 120) if m <= MIN]
out = ['# Ekonomi simülasyonu', '', 'Yeni oyun, Kolay, otomatik müzik açık. Bot her 10 sn\'de Analiz önerisiyle (autoBuyPick, harcama sınırı %%90) en fazla iki şey alır, boş yere en ucuz açık enstrümanı koyar. Süre oyun içi dakika; hızlı ileri sarma (ffSim). Araç: `tools/ekonomi_sim.py %d`.' % MIN, '']
for name, rows in (('Şarj ve patlama açık (3D geliştirmesi var)', A), ('Şarj kapalı', B)):
    out += ['## ' + name, '', '| dk | dalga (en iyi) | nota/sn | hasar/sn | enstrüman | toplam seviye | geri çekilme | patlama | vurgulu adım |', '|---|---|---|---|---|---|---|---|---|']
    ret = 0
    for r in rows:
        ret += r['ret']
        if r['min'] in marks: out.append('| %d | %d (%d) | %s | %s | %d/%d | %d | %d | %d | %d |' % (r['min'], r['wave'], r['best'], fmt(r['rate']), fmt(r['dps']), r['ins'], r['slots'], r['lv'], ret, r['blast'], r['acc']))
    out.append('')
out += ['Sayfa hatası: ' + ('; '.join(errs[:3]) if errs else 'yok') + ' · ölçüm %.0f sn' % (time.time() - t0), '']
open(os.path.join(R, 'docs', 'ekonomi_sim.md'), 'w').write('\n'.join(out))
json.dump({'A': A, 'B': B}, open(os.path.join(R, 'build', 'ekonomi_sim.json'), 'w'))
print('\n'.join(out))
