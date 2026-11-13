"""v44: oyuncu turu düzeltmeleri — masaüstünde Şarj kısa öğreticisi, klavyeyle öğretici, Ritme vur her dokunuş, Atla balonda, örnek şarkı dönüşü, kod yükleme bildirimi.

    python build.py && python tests/v44_test.py
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
    ctx = b.new_context(viewport={'width': 1366, 'height': 768}); p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(600)
    st = lambda: p.evaluate("()=>window.__nb.tutStep")
    check(p.evaluate("()=>document.activeElement&&document.activeElement.id") == 'tutLBtn', 'odak balondaki düğmede')
    for k in range(6):
        p.keyboard.press('Enter'); p.wait_for_timeout(350)
    check(st() >= 6 and p.evaluate("()=>window.__nb.playing") and p.evaluate("()=>window.__nb.S.pat.A[0].filter(Boolean).length") == 4, 'klavyeyle Başla, dört hücre ve ▶ geçildi (adım %d)' % st())
    check(p.evaluate("()=>{const s=document.getElementById('tutSkipL'),b=document.getElementById('tutBub');return b.contains(s)}"), 'Atla balonun içinde')
    p.evaluate("()=>{const nb=window.__nb;nb.S.kills=Math.max(1,nb.S.kills);nb.S.tut.s=8}"); p.wait_for_timeout(400)
    cv = p.locator('#cv').bounding_box()
    for k in range(40):
        if st() != 8: break
        p.mouse.click(cv['x'] + cv['width'] * 0.5, cv['y'] + cv['height'] * 0.12); p.wait_for_timeout(131)
    check(st() > 8 and 'boş' not in p.inner_text('#msg'), 'Ritme vur: sahneye dokunmak sayıldı, “boş yer” mesajı yok')
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;S.tipq=['blast'];S.tutm=0;nb.chReady=0;nb.charge=1}"); p.wait_for_timeout(500)
    check(p.text_content('#tutLT') == 'Elle patlat' and p.text_content('#tutLN') == 'Yeni', 'masaüstünde “Sahneye dön” atlandı, Elle patlat adımı açık (sayaç yerine Yeni)')
    n0 = p.evaluate("()=>window.__nb.blastN"); p.keyboard.press('Enter'); p.wait_for_timeout(400)
    check(p.evaluate("()=>window.__nb.blastN") == n0 + 1 and p.is_hidden('#tutL') and p.evaluate("()=>window.__nb.playing"), 'Enter ile patladı, kısa öğretici bitti, müzik sürüyor')
    p.evaluate("()=>{const S=window.__nb.S;S.tipq=['def','rhy','look'];S.tutm=0}"); p.wait_for_timeout(5600)
    p.click('#tutSkipL'); p.wait_for_timeout(300)
    check(p.evaluate("()=>window.__nb.S.tipq.length") == 0 and p.is_hidden('#tutL'), 'Atla sıradaki bütün kısa öğreticileri geçti')
    p.evaluate("()=>{const S=window.__nb.S;S.unl={studio:1,coll:1,syn:1,tap:1};window.__nb.unlVis()}")
    p.click('#t-set'); p.wait_for_timeout(150); p.click('#p-set [data-act=demoGo][data-k="0"]'); p.wait_for_timeout(400)
    p.click('#t-album'); p.wait_for_timeout(200); p.click('#demo'); p.wait_for_timeout(400)
    check(p.evaluate("()=>document.getElementById('app').dataset.tab") == 'set' and p.is_hidden('#p-lock'), 'örnek şarkıdan Albüm’deyken dönünce girilen sekme (Ayarlar) açık, boş panel yok (v67)')
    p.fill('#saveCode', 'bozuk@@@kod')
    p.click('#p-set [data-act=loadCode]'); p.wait_for_timeout(100); p.click('#p-set [data-act=loadCode]'); p.wait_for_timeout(400)
    check('Yüklenemedi' in p.inner_text('#saveInfo'), 'bozuk kodda Ayarlar’da hata yazıyor (%s)' % p.inner_text('#saveInfo')[:60])
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    ctx.close(); b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
