"""v58: Baskın — her 5 dalgada (patron dalgası hariç) tek koldan kurye akını; canı oyuncunun gücüne göre, sızıntı küçük ve ölümcül değil.

    python build.py && python tests/v58_test.py
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
    p = b.new_page(viewport={'width': 1366, 'height': 768}); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.muted=true;S.bestWave=40;nb.recalc()}")
    q = p.evaluate("()=>[4,5,10,15,25,35].map(w=>window.__nb.waveComp(w).filter(x=>x.raid).length)")
    check(q == [0, 9, 0, 11, 0, 15], 'baskın yalnız 5, 15, 35… dalgalarda (patron dalgasında yok): akıncı sayıları %s' % q)
    # dalga 5: akıncıların canı oyuncu gücüne göre; sızıntı küçük, geri çekilme yok
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.lv.davul=30;nb.recalc();nb.setWave(5)}")
    r = p.evaluate("""()=>{const nb=window.__nb;let minHp=1,maxRaidHp=0,seen=0;const r0=nb.retreats;for(let i=0;i<70;i++){nb.ff(1);minHp=Math.min(minHp,nb.hpFrac());nb.enemies.forEach(e=>{if(e.raid){seen++;maxRaidHp=Math.max(maxRaidHp,e.hpMax)}});if(nb.S.wave>5)break}
      return {minHp,maxRaidHp,seen,ret:nb.retreats-r0,w:nb.S.wave,base:4*Math.pow(1.19,4)*0.5,dps:nb.dps()}}""")
    check(r['seen'] > 0 and r['maxRaidHp'] > r['base'] * 1.5, 'akıncılar geldi, canları sıradan kuryeden fazla (%.1f > %.1f)' % (r['maxRaidHp'], r['base']))
    check(r['ret'] == 0 and r['minHp'] >= 0.049, 'baskın geri çekilmeye yol açmadı, nabız tabanın altına inmedi (en düşük %%%d)' % round(r['minHp'] * 100))
    check(r['w'] >= 6, 'baskından sonra dalga ilerledi (dalga %d)' % r['w'])
    # zayıf oyuncu: nabız düşer ama ölmez
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.pat.A[0]=S.pat.A[0].map(()=>0);S.pat.A[0][0]=1;nb.recalc();nb.setHp(1);nb.setWave(15)}")
    r = p.evaluate("""()=>{const nb=window.__nb;let minHp=1;const r0=nb.retreats;let leaked=false;for(let i=0;i<60;i++){nb.ff(1);minHp=Math.min(minHp,nb.hpFrac());if(nb.S.wave!==15)break}return {minHp,ret:nb.retreats-r0}}""")
    check(r['minHp'] < 1, 'tek vuruşlu zayıf kurulumda nabız düştü (en düşük %%%d)' % round(r['minHp'] * 100))
    # v61: ilk baskında kısa öğretici
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;delete S.unl.raid;S.tipq=[];S.tutm=0;nb.recalc()}")
    cv = p.locator('#cv').bounding_box()
    if not p.evaluate("()=>window.__nb.playing"):
        p.mouse.click(cv['x'] + cv['width'] / 2, cv['y'] + cv['height'] / 2); p.wait_for_function("()=>window.__nb.playing", timeout=3000)
    p.evaluate("()=>window.__nb.setWave(5)"); p.wait_for_timeout(700)
    check(p.evaluate("()=>window.__nb.S.unl.raid===1") and p.evaluate("()=>document.getElementById('tutLT').textContent") == 'Baskın!' and p.is_visible('#tutLBtn'), 'ilk baskında “Baskın!” kısa öğreticisi')
    p.click('#tutLBtn'); p.wait_for_timeout(300)
    check(p.is_hidden('#tutL'), 'Anladım ile kapandı')
    p.evaluate("()=>window.__nb.setWave(15)"); p.wait_for_timeout(500)
    check(p.is_hidden('#tutL'), 'ikinci baskında tekrar çıkmadı')
    check(not errs, 'sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v58 geçti')
sys.exit(1 if fails else 0)
