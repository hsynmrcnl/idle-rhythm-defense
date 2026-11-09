"""itch.io (ve benzeri) için yükleme paketi ve ekran görüntüleri.

    python tools/yayin_paketi.py      → build/nabiz-cemberi-web.zip, docs/yayin/*.png

Zip'in kökünde index.html var (itch.io HTML5 oyunu bunu ister). Ekran görüntüleri örnek şarkı çalarken alınır.
"""
import os, sys, zipfile, subprocess, threading, functools, http.server, socketserver
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.run([sys.executable, os.path.join(R, 'build.py')], check=True, stdout=subprocess.DEVNULL)
DIST, OUT = os.path.join(R, 'dist'), os.path.join(R, 'docs', 'yayin')
zp = os.path.join(R, 'build', 'nabiz-cemberi-web.zip')
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(DIST):
        for f in files:
            p = os.path.join(root, f); z.write(p, os.path.relpath(p, DIST))
print('zip:', zp, round(os.path.getsize(zp) / 1e6, 1), 'MB')
from playwright.sync_api import sync_playwright
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:%d/' % srv.server_address[1]
SEED = "()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.bestWave=30;S.wave=24;localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}"
shots = [('masaustu_3d', {'width': 1280, 'height': 720}, False, 1, 0), ('masaustu_2d', {'width': 1280, 'height': 720}, False, 0, 1),
         ('telefon_sahne', {'width': 390, 'height': 844}, True, 1, 0), ('telefon_ogretici', {'width': 390, 'height': 844}, True, 0, 0)]
exe = '/opt/pw-browsers/chromium'
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=exe, args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    for name, vp, mob, d3, demo2 in shots:
        ctx = b.new_context(viewport=vp, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1); p = ctx.new_page()
        p.goto(URL); p.wait_for_timeout(600)
        if name == 'telefon_ogretici':
            p.click('#tutLBtn'); p.wait_for_timeout(900)
        else:
            p.evaluate(SEED); p.evaluate("v=>{window.__nb.S.d3.on=v}", d3); p.reload(); p.wait_for_timeout(500)
            p.evaluate("k=>{document.querySelector('#t-set')&&0}", 0)
            p.evaluate("k=>{const b=[...document.querySelectorAll('[data-act=demoGo]')].find(x=>x.dataset.k==String(k));if(b)b.click()}", demo2)
            p.wait_for_timeout(7000)
        p.screenshot(path=os.path.join(OUT, name + '.png')); ctx.close()
    # kapak 630×500
    ctx = b.new_context(viewport={'width': 630, 'height': 500}); p = ctx.new_page(); p.goto(URL); p.wait_for_timeout(500)
    p.evaluate(SEED); p.evaluate("()=>{window.__nb.S.d3.on=1}"); p.reload(); p.wait_for_timeout(500)
    p.evaluate("()=>{const b=document.querySelector('[data-act=demoGo]');if(b)b.click()}"); p.wait_for_timeout(7000)
    p.locator('#cv').screenshot(path=os.path.join(OUT, 'kapak_kaynak.png')); ctx.close()
    b.close()
srv.shutdown()
print('ekran görüntüleri:', OUT)
