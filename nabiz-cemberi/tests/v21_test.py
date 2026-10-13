"""v21: Nabız sıfırlanınca bir dalga geri; sahne katmanları gelire ×1,1 (Analiz'de de); otomatik geliştir menajerle.

    python build.py && python tests/v21_test.py
"""
import os, sys, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(R, 'dist')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
fails = []
def check(ok, what):
    print(('  ok  ' if ok else '  FAIL ') + what)
    if not ok: fails.append(what)

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    p = b.new_page(viewport={'width': 1280, 'height': 800}); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto('http://127.0.0.1:%d/' % PORT); p.wait_for_timeout(400)
    p.evaluate("()=>{const S=window.__nb.S;S.tut={s:0,done:true};S.bestWave=12;S.wave=10;S.nota=1e12}")
    p.evaluate("()=>window.__nb.retreatNow()"); p.wait_for_timeout(50)
    check(p.evaluate("()=>window.__nb.S.wave") == 9, 'Nabız sıfırlanınca dalga 10 → 9')
    p.evaluate("()=>{window.__nb.S.wave=1;window.__nb.retreatNow()}")
    check(p.evaluate("()=>window.__nb.S.wave") == 1, 'dalga 1’de geri gidilmez')
    check('bir dalga geri' in p.evaluate("()=>document.querySelector('[data-sec=siege] .info').textContent"), 'Kuşatma bilgisi doğru')
    # sahne katmanı ×1,1
    r = p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.stage={};nb.recalc();const r0=nb.rate(),g0=nb.globalM();S.stage.core=1;S.stage.wall=1;nb.recalc();return{ratio:nb.globalM()/g0,m:nb.stageM()}}")
    check(abs(r['ratio'] - 1.21) < 1e-6 and abs(r['m'] - 1.21) < 1e-6, 'iki katman gelire ×1,21 (×1,1 × ×1,1)')
    p.click('#stats'); p.wait_for_timeout(150)
    check('Sahne katmanları' in p.text_content('#anl'), 'Analiz çarpan dökümünde Sahne katmanları var')
    prod = p.evaluate("""()=>{const h=[...document.querySelectorAll('#anl h4')].find(x=>/Çarpan/.test(x.textContent));const vals=[];let el=h.nextElementSibling;while(el&&el.classList.contains('mr')){vals.push(parseFloat(el.querySelector('b').textContent.replace('×','').replace(',','.')));el=el.nextElementSibling}
      return {p:vals.reduce((a,b)=>a*b,1),top:parseFloat(h.querySelector('span').textContent.replace('×','').replace(',','.'))}}""")
    check(abs(prod['p'] - prod['top']) / prod['top'] < 0.03, 'döküm çarpımı Çarpan’a eşit (×%.2f / ×%.2f)' % (prod['p'], prod['top']))
    p.click('#anl [data-a=close]')
    # menajer adı
    p.evaluate("()=>{window.__nb.S.albMax=1;window.__nb.renderPanels()}")
    p.click('[data-act=tab][data-tab=album]'); p.wait_for_timeout(50)
    check('Menajer: otomatik geliştir' in p.text_content('#mnBox'), 'menajer kademesi: otomatik geliştir')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
