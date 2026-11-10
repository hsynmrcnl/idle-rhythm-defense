"""v48: harcama ipucu — ilerleme durup nota birikince sahnede öneri çipi, dokununca alır.

    python build.py && python tests/v48_test.py
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
        p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.wave=15;S.bestWave=15;S.nota=1e5;localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}")
        p.reload(); p.wait_for_timeout(500)
        cv = p.locator('#cv').bounding_box(); p.mouse.click(cv['x'] + cv['width'] / 2, cv['y'] + cv['height'] / 2)
        p.wait_for_function("()=>window.__nb.playing", timeout=3000)
        p.evaluate("()=>window.__nb.hintCheck()")
        check(p.is_hidden('#hintChip'), 'ilerleme sürerken öneri yok')
        p.evaluate("()=>{window.__nb.hintStall();window.__nb.hintCheck()}")
        check(p.is_visible('#hintChip') and 'Öneri' in p.text_content('#hintChip'), 'ilerleme durup nota birikince öneri çipi çıktı (%s)' % p.text_content('#hintChip'))
        k = p.evaluate("()=>window.__nb.hintK&&{act:window.__nb.hintK.act,cost:window.__nb.hintK.cost}")
        n0 = p.evaluate("()=>window.__nb.S.nota")
        p.click('#hintChip'); p.wait_for_timeout(300)
        check(n0 - p.evaluate("()=>window.__nb.S.nota") >= k['cost'] * 0.99 and p.evaluate("()=>window.__nb.playing"), 'dokununca öneri alındı (%s), müzik sürüyor' % k)
        p.evaluate("()=>{const nb=window.__nb;nb.setHp(0.3);nb.hintStall();nb.hintCheck()}")
        check(p.evaluate("()=>window.__nb.hintK&&window.__nb.hintK.act") == 'def', 'nabız düşükken savunma öneriliyor')
        p.evaluate("()=>{const nb=window.__nb;nb.S.nota=10;nb.hintStall();nb.hintCheck()}")
        check(p.is_hidden('#hintChip'), 'nota yetmezse öneri yok')
        p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.nota=1e5;S.mn={lv:1};S.auto={lv:true};nb.hintStall();nb.hintCheck()}")
        check(p.is_hidden('#hintChip'), 'menajerin otomatik geliştirmesi açıkken öneri yok')
        check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
        ctx.close()
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
