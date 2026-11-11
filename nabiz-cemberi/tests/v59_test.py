"""v59: Koleksiyon kısa öğreticisi sayfayı/listeyi kaydırıp kilitlemez; ekrandan uzun hedefte oyuncu kaydırabilir; öğreticiden sonra satın alınır.

    python build.py && python tests/v59_test.py
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
ST = "()=>{const h=document.getElementById('tutHole').getBoundingClientRect();return {sy:Math.round(scrollY),rack:Math.round(document.getElementById('rack').scrollTop),hy:h.y,hh:h.height,vh:innerHeight,hid:document.getElementById('tutL').hidden}}"

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    for name, vp, mob in (('telefon 360x640', {'width': 360, 'height': 640}, True), ('masaüstü', {'width': 1366, 'height': 768}, False)):
        print(name)
        ctx = b.new_context(viewport=vp, is_mobile=mob, has_touch=mob); p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.goto(URL); p.wait_for_timeout(500)
        p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;S.unl={studio:1,coll:1,syn:1,tap:1};S.nota=5000;S.total=9000;S.tipq=['coll'];S.tutm=0;nb.unlVis();nb.setTab(innerWidth<=700?'stage':'studio');nb.tutTick()}"); p.wait_for_timeout(500)
        for i in range(4):
            if p.evaluate("()=>document.getElementById('tutLT').textContent") == 'Koleksiyon' and p.is_visible('#tutLBtn'): break
            h = p.locator('#tutHole').bounding_box()
            (p.touchscreen.tap if mob else p.mouse.click)(h['x'] + h['width'] / 2, h['y'] + h['height'] / 2); p.wait_for_timeout(600)
        s = p.evaluate(ST)
        check(s['sy'] == 0 and s['rack'] == 0, 'Koleksiyon adımında sayfa ve liste kaymadı (sayfa %d, liste %d)' % (s['sy'], s['rack']))
        check(0 <= s['hy'] and s['hy'] + s['hh'] <= s['vh'] and s['hh'] < s['vh'] * 0.5, 'vurgu ekranın içinde ve küçük (%d px)' % s['hh'])
        p.click('#tutLBtn'); p.wait_for_timeout(400)
        check(p.evaluate(ST)['hid'], 'Anladım ile kapandı')
        n0 = p.evaluate("()=>window.__nb.S.nota")
        p.evaluate("()=>document.querySelector('#collList [data-act=lv][data-id=trampet]').click()"); p.wait_for_timeout(300)
        check(p.evaluate("()=>window.__nb.S.lv.trampet") == 1 and p.evaluate("()=>window.__nb.S.nota") < n0, 'öğreticiden sonra Trampet satın alındı')
        # ekrandan uzun hedef: oyuncu kaydırabilir (her karede geri çekilmez)
        p.evaluate("()=>{const nb=window.__nb,S=nb.S;nb.unlockAll();S.tipq=['look'];S.tutm=0;nb.unlVis();nb.tutTick()}"); p.wait_for_timeout(500)
        for i in range(4):
            if p.is_visible('#tutLBtn'): break
            h = p.locator('#tutHole').bounding_box()
            (p.touchscreen.tap if mob else p.mouse.click)(h['x'] + h['width'] / 2, h['y'] + h['height'] / 2); p.wait_for_timeout(600)
        sc = "()=>{const r=document.getElementById('rack');const el=(innerWidth<=700||r.scrollHeight>r.clientHeight+4)?r:document.scrollingElement;const a=el.scrollTop;el.scrollTop=a+160;return [a,el.scrollTop]}"
        a = p.evaluate(sc); p.wait_for_timeout(500)
        after = p.evaluate("()=>{const r=document.getElementById('rack');return Math.max(r.scrollTop,document.scrollingElement.scrollTop)}")
        check(a[1] == a[0] or after >= a[1] - 2, 'uzun hedefte oyuncunun kaydırması geri alınmıyor (%s → %d)' % (a, after))
        s = p.evaluate(ST)
        check(s['hy'] >= 0 and s['hy'] + s['hh'] <= s['vh'] + 1, 'uzun hedefte vurgu ekrana kırpıldı (%d..%d / %d)' % (s['hy'], s['hy'] + s['hh'], s['vh']))
        check(not errs, 'sayfa hatası yok %s' % errs[:2])
        ctx.close()
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v59 geçti')
sys.exit(1 if fails else 0)
