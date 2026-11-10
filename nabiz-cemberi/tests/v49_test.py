"""v49: Asistan — dalga 15'te ücretsiz açılır, notanın en çok %25'iyle geliştirme alır, menajer gelince kaybolur; kısa öğreticisi Otomatik satırını gösterir.

    python build.py && python tests/v49_test.py
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
    for ph in (1, 0):
        print('telefon' if ph else 'masaüstü')
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True) if ph else b.new_context(viewport={'width': 1366, 'height': 768})
        p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.goto(URL); p.wait_for_timeout(500)
        # dalga 14: asistan yok
        p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;S.tipq=[];S.wave=14;S.bestWave=14;S.kills=50;S.total=1e4;S.nota=1e5;S.lv.trampet=1;S.slots[1]='trampet';nb.unlCheck(true);S.tipq=[];localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}")
        p.reload(); p.wait_for_timeout(500)
        check(not p.evaluate("()=>!!window.__nb.S.unl.asst"), 'dalga 14: asistan kilitli')
        # dalga 15: açılır, kısa öğretici
        p.evaluate("()=>{const S=window.__nb.S;S.wave=15;S.bestWave=15;window.__nb.unlCheck()}")
        p.wait_for_timeout(300)
        check(p.evaluate("()=>!!window.__nb.S.unl.asst&&window.__nb.S.tipq.includes('asst')"), 'dalga 15: asistan açıldı, kısa öğretici sırada')
        # kısa öğreticiyi baştan sona oyna (önceki sıradakiler Atla ile değil, yalnız asst bıraktır)
        p.evaluate("()=>{const S=window.__nb.S;S.tipq=['asst'];S.tutm=0;window.__nb.tutTick()}"); p.wait_for_timeout(400)
        seen = []
        for i in range(6):
            t = p.evaluate("()=>{const L=document.getElementById('tutL');return L&&!L.hidden?document.getElementById('tutLT').textContent:''}")
            if not t: break
            seen.append(t)
            if p.is_visible('#tutLBtn'):
                p.click('#tutLBtn')
            else:
                hb = p.locator('#tutHole').bounding_box()
                p.mouse.click(hb['x'] + hb['width'] / 2, hb['y'] + hb['height'] / 2)
            p.wait_for_timeout(500)
        check(any('Asistan' in s for s in seen) and not p.evaluate("()=>window.__nb.S.tipq.includes('asst')"), 'kısa öğretici bitti (%s)' % ' → '.join(seen))
        check(p.locator('#autoBox [data-k=asst]').count() == 1 and p.get_attribute('#autoBox [data-k=asst]', 'aria-checked') == 'true', 'Otomatik kartında Asistan anahtarı açık')
        # alım: %25 sınırı
        r = p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.nota=1e5;const n0=S.nota,k=nb.asstPick();nb.asstReset();nb.autoTick();return {c:k&&k.cost,d:n0-S.nota}}")
        check(r['c'] and r['c'] <= 25000 and r['d'] >= r['c'] * 0.99, 'asistan aldı, sınır içinde (♪%s)' % r['c'])
        r = p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.nota=10;const n0=S.nota;nb.asstReset();nb.autoTick();return n0-S.nota}")
        check(r == 0, 'nota azken almaz')
        # kapat
        p.click('#autoBox [data-k=asst]') if p.is_visible('#autoBox [data-k=asst]') else p.evaluate("()=>document.querySelector('#autoBox [data-k=asst]').click()")
        r = p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.nota=1e5;const n0=S.nota;nb.asstReset();nb.autoTick();return {off:S.auto.asst,d:n0-S.nota}}")
        check(r['off'] is False and r['d'] == 0, 'kapalıyken almaz')
        # açıkken öneri çipi gizli; kapalıyken görünebilir
        p.evaluate("()=>{const S=window.__nb.S;S.auto.asst=true}")
        p.evaluate("()=>window.__nb.renderPanels()")
        cv = p.locator('#cv').bounding_box()
        if ph: p.evaluate("()=>window.__nb.setTab('stage')"); p.wait_for_timeout(300); cv = p.locator('#cv').bounding_box()
        p.evaluate("()=>{if(!window.__nb.playing)document.querySelector('#cv')}")
        p.mouse.click(cv['x'] + cv['width'] / 2, cv['y'] + cv['height'] / 2)
        p.wait_for_function("()=>window.__nb.playing", timeout=3000)
        p.evaluate("()=>{window.__nb.S.nota=1e6;window.__nb.hintStall();window.__nb.hintCheck()}")
        check(p.is_hidden('#hintChip'), 'asistan açıkken öneri çipi yok')
        p.evaluate("()=>{window.__nb.S.auto.asst=false;window.__nb.hintStall();window.__nb.hintCheck()}")
        check(p.is_visible('#hintChip'), 'asistan kapalıyken öneri çipi var')
        # menajer gelince asistan biter
        p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.auto.asst=true;S.mn.lv=1;nb.renderPanels()}")
        check(p.locator('#autoBox [data-k=asst]').count() == 0 and not p.evaluate("()=>window.__nb.asstOn()"), 'menajer alınınca asistan satırı yok')
        # EN
        p.evaluate("()=>{const nb=window.__nb,S=nb.S;delete S.mn.lv;S.lang='en';nb.renderPanels()}")
        check('Assistant' in p.text_content('#autoBox'), 'İngilizce: Assistant')
        check(not errs, 'sayfa hatası yok %s' % errs[:2])
        ctx.close()
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v49 geçti')
sys.exit(1 if fails else 0)
