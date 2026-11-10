"""v57: yatay telefonda öğretici balonu hedefin karşı yarısında; öğreticide Tab balonun içinde kalır; panel yeniden çizilince klavye odağı aynı düğmede.

    python build.py && python tests/v57_test.py
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
GEO = "()=>{const r=e=>{const b=e.getBoundingClientRect();return [b.x,b.y,b.width,b.height]};return {h:r(document.getElementById('tutHole')),b:r(document.getElementById('tutBub'))}}"

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe, args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch()
    errs = []
    # yatay telefon: hücre adımlarında balon sağ yarıda
    ctx = b.new_context(viewport={'width': 844, 'height': 390}, is_mobile=True, has_touch=True); p = ctx.new_page()
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(600); p.keyboard.press('Enter'); p.wait_for_timeout(500)
    bad = []
    for k in range(4):
        g = p.evaluate(GEO)
        if not (g['h'][0] + g['h'][2] / 2 < 422 and g['b'][0] >= 422 - 1): bad.append((k, g))
        p.keyboard.press('Enter'); p.wait_for_timeout(450)
    check(not bad, 'yatayda dört hücre adımında balon sahnenin dışında, sağ yarıda %s' % bad[:1])
    ctx.close()
    # masaüstü: Tab balonda kalır
    ctx = b.new_context(viewport={'width': 1366, 'height': 768}); p = ctx.new_page()
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(600)
    ids = []
    for k in range(4):
        p.keyboard.press('Tab'); p.wait_for_timeout(60); ids.append(p.evaluate("()=>document.activeElement&&document.activeElement.id"))
    check(all(i in ('tutLBtn', 'tutSkipL', 'tutBub') for i in ids), 'öğreticide Tab balonun içinde kalıyor (%s)' % ids)
    p.keyboard.press('Enter'); p.wait_for_timeout(400)
    check(p.evaluate("()=>window.__nb.tutStep") >= 1, 'Enter yine ilerletiyor')
    # odak korunur
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.nota=1e5;S.lv.hihat=1;S.slots[1]='hihat';nb.recalc();nb.renderPanels()}"); p.wait_for_timeout(300)
    p.focus('#slotList [data-act=alvl][data-i="1"][data-v="2"]'); p.keyboard.press('Enter'); p.wait_for_timeout(250)
    a = p.evaluate("()=>{const e=document.activeElement;return e&&e.dataset?[e.dataset.act,e.dataset.i,e.dataset.v]:null}")
    check(a == ['alvl', '1', '2'] and p.evaluate("()=>window.__nb.S.rowm.A1") == 2, 'Hareketli’ye Enter sonrası odak aynı düğmede (%s)' % a)
    p.focus('#lvb-davul'); p.keyboard.press('Enter'); p.wait_for_timeout(250)
    check(p.evaluate("()=>document.activeElement&&document.activeElement.id") == 'lvb-davul', 'Yükselt’e Enter sonrası odak aynı düğmede')
    check(not errs, 'sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v57 geçti')
sys.exit(1 if fails else 0)
