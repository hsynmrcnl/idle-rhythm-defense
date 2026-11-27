"""v78: sahneye klavyeyle odaklanıp oklarla hücre seçme, Enter ile vuruş koyma/kaldırma; seçili hücre okunur.

    python build.py && python tests/v78_test.py
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
    errs = []
    p = b.new_page(viewport={'width': 1280, 'height': 800})
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.unl.look=0;S.tipq=[];S.tutm=0;S.nota=1e5;S.slots=['davul','trampet',null,null];S.lv.trampet=1;S.pat.A[1]=S.pat.A[1].map(()=>0);nb.recalc();nb.renderPanels()}")
    check(p.evaluate("()=>document.getElementById('cv').tabIndex") == 0, 'sahne Tab ile odaklanabilir')
    p.focus('#cv'); p.wait_for_timeout(100)
    m0 = p.inner_text('#msg')
    check('Yer 1' in m0 and 'adım 1' in m0, 'odaklanınca seçili hücre okunuyor (“%s”)' % m0)
    for k in ['ArrowRight', 'ArrowRight', 'ArrowDown']: p.keyboard.press(k); p.wait_for_timeout(60)
    m1 = p.inner_text('#msg')
    check('Yer 2' in m1 and 'Trampet' in m1 and 'adım 3' in m1 and 'vuruş yok' in m1, 'oklar hücreyi taşıyor (“%s”)' % m1)
    p.keyboard.press('Enter'); p.wait_for_timeout(150)
    v = p.evaluate("()=>window.__nb.S.pat.A[1][2]")
    check(v and 'vuruş var' in p.inner_text('#msg'), 'Enter vuruş koydu (%s · “%s”)' % (v, p.inner_text('#msg')))
    p.keyboard.press('Enter'); p.wait_for_timeout(150)
    check(not p.evaluate("()=>window.__nb.S.pat.A[1][2]"), 'Enter yeniden basınca vuruş kalktı')
    p.keyboard.press('ArrowUp'); p.keyboard.press('ArrowUp'); p.wait_for_timeout(60)
    check('Yer 2' in p.inner_text('#msg'), 'yukarı/aşağı yalnız dolu sahne yerlerinde döner (“%s”)' % p.inner_text('#msg'))
    check(not errs, 'sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v78 geçti')
sys.exit(1 if fails else 0)
