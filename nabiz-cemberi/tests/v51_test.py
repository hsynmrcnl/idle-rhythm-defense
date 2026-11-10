"""v51: otomatik davul nefese sığar (vurgu dahil, “çok yoğun” cezası yok); ana öğretici baştan sona yalnız klavyeyle geçilir.

    python build.py && python tests/v51_test.py
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
LOAD = "()=>{const r=window.__nb.S.pat.A[0];let n=0;for(const v of r)if(v)n+=v===2?2:1;return n}"

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe, args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch()
    for ph in (0, 1):
        print('telefon' if ph else 'masaüstü (yalnız klavye)')
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True) if ph else b.new_context(viewport={'width': 1366, 'height': 768})
        p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.goto(URL); p.wait_for_timeout(600)
        if not ph:
            seen = set()
            for k in range(260):
                s = p.evaluate("()=>window.__nb.S.tut.done?-1:window.__nb.tutStep")
                if s < 0: break
                seen.add(s)
                stp = p.evaluate("s=>{const t=window.__nb.TUT[s];return {kind:t.kind,rv:!!t.rv}}", s)
                if stp['kind'] == 'auto': p.wait_for_timeout(300); continue
                p.keyboard.press('Space' if stp['rv'] else 'Enter'); p.wait_for_timeout(137 if stp['rv'] else 300)
            check(p.evaluate("()=>window.__nb.S.tut.done"), 'ana öğretici yalnız klavyeyle bitti (%d adım görüldü)' % len(seen))
        else:
            p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;S.tipq=[];nb.unlockAll();S.tipq=[];S.nota=1e5;nb.renderPanels()}")
        for lv, name in ((3, 'Yoğun'), (2, 'Hareketli'), (1, 'Sade')):
            p.evaluate("v=>{const b=document.querySelector('[data-act=alvl][data-i=\"0\"][data-v=\"'+v+'\"]')||document.querySelector('[data-act=alvl][data-i=\"0\"]');window.__nb.S.nota=1e5;b.click()}", lv); p.wait_for_timeout(150)
            ld = p.evaluate(LOAD)
            check(ld <= 5 and p.evaluate("()=>window.__nb.S.pat.A[0][0]") >= 1, 'Davul %s: yük %d ≤ nefes 5' % (name, ld))
        p.evaluate("()=>document.querySelector('[data-act=alvl][data-i=\"0\"][data-v=\"3\"]').click()"); p.wait_for_timeout(150)
        check(p.evaluate("()=>window.__nb.S.pat.A[0][0]") == 2, 'Yoğun davulda ölçü başı vurgulu (şarj dolar)')
        check(p.locator('#p-studio .nb.over').count() == 0, 'Stüdyo’da “çok yoğun” uyarısı yok')
        check(p.locator('#slotList [data-act=alvl][data-i="0"]').count() == 1 and 'Otomatik ritim' in p.text_content('#slotList [data-act=alvl][data-i="0"]'), 'Davul’da tek “Otomatik ritim” düğmesi (v55)')
        check(not errs, 'sayfa hatası yok %s' % errs[:2])
        ctx.close()
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v51 geçti')
sys.exit(1 if fails else 0)
