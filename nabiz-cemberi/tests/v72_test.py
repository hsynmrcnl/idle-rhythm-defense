"""v72: kısa öğreticiler arası bekleme, Ayarlar'dan kilitli sekmeye düşmeme, aile öğreticisinde ilk enstrüman adımı, Terimler'de yeni terimler.

    python build.py && python tests/v72_test.py
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
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=['def','rhy'];S.tutm=0;nb.setTab('studio')}")
    p.wait_for_timeout(400)
    check(p.is_visible('#tutL'), 'ilk kısa öğretici açık')
    p.keyboard.press('Escape'); p.wait_for_timeout(400)
    st = p.evaluate("()=>[window.__nb.S.tipq.length,!!window.__nb.ovCur(),window.__nb.miniGapT>Date.now()]")
    check(st[0] == 1 and not st[1] and st[2] and p.is_hidden('#tutL'), 'ilki kapanınca sıradaki hemen gelmiyor, bekliyor (%s)' % st)
    p.evaluate("()=>{window.__nb.miniGapT=0}"); p.wait_for_timeout(400)
    check(p.is_visible('#tutL'), 'bekleme bitince sıradaki geliyor')
    p.evaluate("()=>{const S=window.__nb.S;S.tipq=[];S.tutm=0}"); p.wait_for_timeout(200)
    p.evaluate("()=>window.__nb.setTab('def')"); p.click('#t-set'); p.wait_for_timeout(150)
    p.evaluate("()=>{const nb=window.__nb;delete nb.S.unl.def;nb.unlVis()}")
    p.keyboard.press('Escape'); p.wait_for_timeout(200)
    check(p.is_hidden('#p-lock') and p.is_visible('#p-studio'), 'Ayarlar’dan dönülecek sekme kilitliyse Stüdyo açılıyor')
    p.evaluate("()=>{const nb=window.__nb;nb.S.unl.def=1;nb.unlVis();nb.setTab('set')}"); p.wait_for_timeout(150)
    g = p.evaluate("()=>[...document.querySelectorAll('.gloss dt')].map(e=>e.textContent)")
    check('Hayran' in g and 'Şarj' in g and p.evaluate("()=>document.querySelector('.gloss').open"), 'Terimler açık ve yeni terimler var (%d)' % len(g))
    check(not errs, 'sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v72 geçti')
sys.exit(1 if fails else 0)
