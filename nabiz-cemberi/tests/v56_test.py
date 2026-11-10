"""v56: örnek şarkı çıkışı — çip masaüstünde de sahnede, Escape çıkarır, EN'de düğme çevrili.

    python build.py && python tests/v56_test.py
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
    for vp, mob in (({'width': 1366, 'height': 768}, False), ({'width': 390, 'height': 844}, True)):
        print('telefon' if mob else 'masaüstü')
        ctx = b.new_context(viewport=vp, is_mobile=mob, has_touch=mob); p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.goto(URL); p.wait_for_timeout(500)
        p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.lang='en';localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}"); p.reload(); p.wait_for_timeout(600)
        check(p.is_hidden('#demoChip'), 'kendi oyununda çip yok')
        p.evaluate("()=>window.__nb.enterDemo(0)"); p.wait_for_timeout(500)
        bb = p.locator('#demoChip').bounding_box()
        check(p.is_visible('#demoChip') and bb['y'] < vp['height'] * 0.5 and 'exit' in p.text_content('#demoChip'), 'örnek şarkıda çip sahnenin üstünde görünür (%d,%d)' % (bb['x'], bb['y']))
        if not mob: check(p.text_content('#demo') == 'Back to your game', 'İngilizcede “Back to your game”')
        if mob: p.tap('#demoChip')
        else: p.keyboard.press('Escape')
        p.wait_for_timeout(300)
        check(not p.evaluate("()=>window.__nb.demoMode") and p.is_hidden('#demoChip'), 'çıkıldı (%s)' % ('çipe dokunarak' if mob else 'Escape ile'))
        check(not errs, 'sayfa hatası yok %s' % errs[:2])
        ctx.close()
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v56 geçti')
sys.exit(1 if fails else 0)
