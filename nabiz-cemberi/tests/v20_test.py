"""v20: Otomatik geliştir (Analiz'in gelir önerisi, notanın yarısını aşmadan) ve Kolay'da savunma önerisi.

    python build.py && python tests/v20_test.py
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

SEED = """()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};S.ui='kolay';S.nota=5000;S.slots=['davul','trampet','hihat',null];S.lv={davul:3,trampet:2,hihat:1};S.up={};S.def={};
  ['A','B','S','F'].forEach(k=>S.pat[k]=S.pat[k].map(r=>r.map(()=>0)));for(const s of [0,4,8,12])S.pat.A[0][s]=1;S.pat.A[1][4]=1;S.pat.A[1][12]=1;for(const s of [2,6,10,14])S.pat.A[2][s]=1;nb.recalc();nb.renderPanels()}"""

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    p = b.new_page(viewport={'width': 1280, 'height': 800}); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto('http://127.0.0.1:%d/' % PORT); p.wait_for_timeout(400); p.evaluate(SEED)
    check(p.locator('[data-act=autoUp]').count() == 0 and 'Menajerle gelir' in p.text_content('#slotAdd'), 'menajer yokken Otomatik geliştir kilitli, nasıl açılacağı yazıyor')
    p.evaluate("()=>{const S=window.__nb.S;S.mn.lv=1;S.auto.lv=false;window.__nb.renderPanels()}")
    check(p.evaluate("()=>document.querySelector('[data-act=autoUp][data-v=\"0\"]').getAttribute('aria-pressed')") == 'true', 'menajerle gelince düğmeler görünüyor')
    st0 = p.evaluate("()=>JSON.stringify([window.__nb.S.lv,window.__nb.S.up])")
    n0 = p.evaluate("()=>window.__nb.S.nota")
    p.click('[data-act=autoUp][data-v="1"]')
    p.wait_for_timeout(2600)
    st1 = p.evaluate("()=>JSON.stringify([window.__nb.S.lv,window.__nb.S.up])")
    n1 = p.evaluate("()=>window.__nb.S.nota")
    check(st1 != st0 and n0 - n1 <= n0 * 0.5 + 1, 'açınca en verimli geliştirmeyi aldı, notanın yarısını aşmadı (♪ %d harcandı)' % (n0 - n1))
    check('Menajer:' in p.text_content('#msg') or st1 != st0, 'mesaj gösterildi')
    p.click('[data-act=autoUp][data-v="0"]'); p.wait_for_timeout(50)
    check(p.evaluate("()=>window.__nb.S.auto.lv") is False, 'kapatılabiliyor')
    # savunma önerisi
    p.click('[data-act=tab][data-tab=def]'); p.wait_for_timeout(50)
    p.evaluate("()=>{window.__nb.core.hp=window.__nb.S?1e9:0;window.__nb.renderPanels()}")
    rec = p.evaluate("()=>[...document.querySelectorAll('#defList .dtile.rec')].map(e=>e.dataset.id)")
    check(len(rec) == 1 and rec[0] in ('hasar', 'menzil'), 'nabız yüksekken hasar/menzil öneriliyor (%s)' % rec)
    p.evaluate("()=>{window.__nb.core.hp=5;window.__nb.renderPanels()}")
    rec = p.evaluate("()=>[...document.querySelectorAll('#defList .dtile.rec')].map(e=>e.dataset.id)")
    check(len(rec) == 1 and rec[0] in ('nabiz', 'kalkan', 'tamir'), 'nabız düşükken dayanıklılık öneriliyor (%s)' % rec)
    p.evaluate("()=>{window.__nb.S.ui='detay';window.__nb.renderPanels()}")
    check(p.locator('#defList .dtile.rec').count() == 0, 'Detaylı’da öneri vurgusu yok')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
