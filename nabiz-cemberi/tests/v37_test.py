"""v37: kaybetme gerilimi (boğuk müzik, kalp atışı, kurtuluş, geri çekilme) ve şarjı elle patlatma.

    python build.py && python tests/v37_test.py
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
        p.evaluate("v=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};nb.unlockAll();S.d3.own=1;S.d3.on=v;S.wave=3;S.bestWave=3;localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}", d3)
        p.reload(); p.wait_for_timeout(400)
        cv = p.locator('#cv').bounding_box(); cx, cy = cv['x'] + cv['width'] / 2, cv['y'] + cv['height'] / 2
        p.mouse.click(cx, cy); p.wait_for_timeout(800)
        # gerilim
        check(p.evaluate("()=>window.__nb.dangerF") > 15000, 'nabız doluyken müzik açık')
        h0 = p.evaluate("()=>window.__nb.dngSnd")
        p.evaluate("()=>{const nb=window.__nb;nb.enemies.length=0;nb.setHp(0.1)}"); p.wait_for_timeout(2600)
        st = p.evaluate("()=>({f:window.__nb.dangerF,h:window.__nb.dngSnd})")
        check(st['f'] < 3000, 'nabız %%10: müzik boğuldu (%d Hz)' % st['f'])
        check(st['h'] - h0 >= 2, 'kalp atışı çalıyor (%d)' % (st['h'] - h0))
        p.evaluate("()=>window.__nb.setHp(0.8)"); p.wait_for_timeout(250)
        check(p.evaluate("()=>window.__nb.saveFx") > 0, '%50 üstüne dönünce kurtuluş parlaması')
        p.wait_for_timeout(800)
        check(p.evaluate("()=>window.__nb.dangerF") > 15000, 'kurtulunca müzik açıldı')
        w0 = p.evaluate("()=>window.__nb.S.wave"); p.evaluate("()=>window.__nb.retreatNow()"); p.wait_for_timeout(200)
        check(p.evaluate("()=>window.__nb.tapeGray") > 0 and p.evaluate("()=>window.__nb.S.wave") == w0 - 1 and p.evaluate("()=>window.__nb.saveFx") == 0, 'geri çekilme: gri ekran, dalga geri, kurtuluş sayılmıyor')
        # elle patlat
        p.wait_for_timeout(1800)
        p.evaluate("()=>{const nb=window.__nb;nb.charge=1;nb.chReady=0}")
        n0 = p.evaluate("()=>window.__nb.blastN"); pl = p.evaluate("()=>window.__nb.playing")
        p.mouse.click(cx, cy)
        p.wait_for_timeout(150)
        check(p.evaluate("()=>window.__nb.blastN") == n0 + 1 and p.evaluate("()=>window.__nb.chReady") < 0 and p.evaluate("()=>window.__nb.playing") == pl, 'dolu şarjda merkeze dokunmak patlatır, müzik durmaz')
        check(p.evaluate("()=>window.__nb.blastM") in (1, 1.5), 'patlama çarpanı 1 ya da 1,5')
        # ayar kapalı
        p.click('#t-set'); p.wait_for_timeout(100); p.click('#p-set [data-act=tens][data-v="0"]'); p.wait_for_timeout(100)
        h1 = p.evaluate("()=>window.__nb.dngSnd"); p.evaluate("()=>window.__nb.setHp(0.1)"); p.wait_for_timeout(1500)
        check(p.evaluate("()=>window.__nb.S.tens") is False and p.evaluate("()=>window.__nb.dngSnd") == h1 and p.evaluate("()=>window.__nb.dangerF") > 15000, 'Ayarlar → Gerilim efektleri kapalıyken sessiz')
        check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
        ctx.close()
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
