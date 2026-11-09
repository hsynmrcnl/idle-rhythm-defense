"""v46: yatay telefon (844×390) — sayfa kaymaz, sahne yükseklik kadar, panel kendi içinde kayar, dişli erişilebilir, öğretici çalışır.

    python build.py && python tests/v46_test.py
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
    for vp in ({'width': 844, 'height': 390}, {'width': 740, 'height': 360}):
        print('yatay %dx%d' % (vp['width'], vp['height']))
        ctx = b.new_context(viewport=vp, is_mobile=True, has_touch=True); p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.goto(URL); p.wait_for_timeout(600)
        m = p.evaluate("()=>{const c=document.getElementById('cv').getBoundingClientRect();return {sh:document.documentElement.scrollHeight,ih:innerHeight,ch:c.height,cb:c.bottom,ctl:getComputedStyle(document.querySelector('.stage .controls')).display}}")
        check(m['sh'] <= m['ih'] + 1, 'sayfa kaymıyor (%s)' % m)
        check(m['ch'] >= vp['height'] * 0.7 and m['cb'] <= vp['height'] + 1 and m['ctl'] == 'none', 'sahne ekran yüksekliğinin çoğu, düğme satırı gizli')
        st = lambda: p.evaluate("()=>window.__nb.tutStep")
        p.click('#tutLBtn'); p.wait_for_timeout(400)
        for k in range(5):
            r = p.evaluate("()=>{const h=document.getElementById('tutHole').getBoundingClientRect();return [h.left+h.width/2,h.top+h.height/2]}")
            p.wait_for_timeout(350); r = p.evaluate("()=>{const h=document.getElementById('tutHole').getBoundingClientRect();return [h.left+h.width/2,h.top+h.height/2]}")
            p.mouse.click(r[0], r[1]); p.wait_for_timeout(450)
        check(st() >= 6 and p.evaluate("()=>window.__nb.playing"), 'yatayda öğretici dört hücre ve ▶ ile ilerliyor (adım %d)' % st())
        p.evaluate("()=>{const nb=window.__nb;nb.S.tut.done=true;nb.unlockAll();nb.S.tipq=[]}"); p.wait_for_timeout(300)
        check(p.is_visible('#t-set'), 'dişli görünüyor')
        p.click('#t-set'); p.wait_for_timeout(200)
        check(p.is_visible('#p-set'), 'dişli Ayarlar’ı açıyor')
        rk = p.evaluate("()=>{const r=document.getElementById('rack');return [r.scrollHeight>r.clientHeight,getComputedStyle(r).overflowY]}")
        check(rk[1] == 'auto', 'panel kendi içinde kayar (%s)' % rk)
        check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
        ctx.close()
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
