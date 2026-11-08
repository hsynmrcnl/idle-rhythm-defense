"""v31–v34: geometrik düşmanlar (şekiller, yüzler), doğma animasyonu, ölünce parçalar, ritimli ölüm sesi.

    python build.py && python tests/v31_test.py
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
    b = pw.chromium.launch(executable_path=exe, args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch()
    for d3 in (1, 0):
        print('3D' if d3 else '2D')
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.goto(URL); p.wait_for_timeout(300)
        p.evaluate("v=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};nb.unlockAll();S.muted=true;S.d3.on=v;S.wave=10;S.bestWave=10;localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}", d3)
        p.reload(); p.wait_for_timeout(400)
        if d3:
            g = p.evaluate("()=>{const G=window.__nb.GEO;return Object.fromEntries(Object.entries(G).map(([k,v])=>[k,[v.V.length,v.F.length]]))}")
            want = {'kup': 6, 'tetra': 4, 'okta': 8, 'ikosa': 20, 'dodeka': 12, 'prizma': 5, 'elmas': 12, 'yildiz': 24}
            check(all(g[k][1] == n for k, n in want.items()), 'sekiz cismin yüz sayıları doğru (%s)' % g)
        cv = p.locator('#cv').bounding_box(); p.mouse.click(cv['x'] + cv['width'] / 2, cv['y'] + cv['height'] / 2)
        p.wait_for_timeout(3500)
        st = p.evaluate("()=>{const E=window.__nb.enemies;return {n:E.length,sp0:E.filter(e=>e.sp0!=null).length,boss:E.filter(e=>e.boss).length,D3:window.__nb.D3}}")
        check(st['n'] > 0 and st['sp0'] == st['n'] and st['D3'] == bool(d3), 'çizilen her düşmanın doğma anı var (%s)' % st)
        k0, s0 = p.evaluate("()=>[window.__nb.S.kills,window.__nb.killSnd]")
        p.evaluate("()=>{window.__nb.enemies.forEach(e=>e.hp=0.001);window.__nb.blast()}"); p.wait_for_timeout(120)
        k1, s1, fr = p.evaluate("()=>[window.__nb.S.kills,window.__nb.killSnd,window.__nb.frags.length]")
        check(k1 - k0 >= 2 and fr > 0, 'ölenler parçalara ayrıldı (%d ölüm, %d parça)' % (k1 - k0, fr))
        check(1 <= s1 - s0 <= 2, 'aynı anda ölen %d düşman için tek ölüm sesi (%d ses; arada doğal bir ölüm olabilir)' % (k1 - k0, s1 - s0))
        p.evaluate("()=>window.__nb.ff(20)")
        check(p.evaluate("()=>window.__nb.killSnd") - s1 <= 1 and p.evaluate("()=>window.__nb.frags.length") < 500, 'hızlı ileri sarma ses ve parça biriktirmiyor')
        check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
        ctx.close()
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
