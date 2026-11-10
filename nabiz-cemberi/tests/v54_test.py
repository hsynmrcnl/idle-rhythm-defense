"""v54: öğretici Atla sonrası hazır davul ritmi; Ritme vur adımı 3 ıskadan sonra geçer; Boşluk yalnız Ritme vur; Asistan bir turda çoklu alım; hızlı ileri sarma sonrası oyun donmaz.

    python build.py && python tests/v54_test.py
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
    errs = []
    # 1) Atla → hazır ritim
    ctx = b.new_context(viewport={'width': 1366, 'height': 768}); p = ctx.new_page()
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(500)
    p.keyboard.press('Enter'); p.wait_for_timeout(5600)
    check(p.evaluate("()=>window.__nb.S.pat.A[0].filter(Boolean).length") == 0, 'Başla’dan sonra desen boş')
    p.click('#tutSkipL'); p.wait_for_timeout(300)
    check(p.evaluate("()=>window.__nb.S.tut.done&&window.__nb.S.pat.A[0].filter(Boolean).length") == 4 and p.evaluate("()=>window.__nb.rate()") > 0, 'Atla sonrası dörtlük davul ritmi kuruldu, gelir var')
    ctx.close()
    # 2) Ritme vur: ıskalar ve Boşluk
    ctx = b.new_context(viewport={'width': 1366, 'height': 768}); p = ctx.new_page()
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(500)
    for k in range(80):
        stp = p.evaluate("()=>{const t=window.__nb.TUT[window.__nb.tutStep];return {kind:t.kind,rv:!!t.rv}}")
        if stp['rv']: break
        if stp['kind'] != 'auto': p.keyboard.press('Enter')
        p.wait_for_timeout(300)
    s0 = p.evaluate("()=>window.__nb.tutStep")
    for k in range(12):
        p.keyboard.press('Space'); p.wait_for_timeout(60)
    p.wait_for_timeout(400)
    s1 = p.evaluate("()=>window.__nb.tutStep")
    check(s1 > s0 and p.evaluate("()=>window.__nb.S.lv.davul") == 1 and p.evaluate("()=>window.__nb.TUT[window.__nb.tutStep].kind") == 'tap', 'Boşluk’a art arda basmak Ritme vur’u geçirdi ama Yükselt adımını atlatmadı (%d → %d)' % (s0, s1))
    p.keyboard.press('Enter'); p.wait_for_timeout(400)
    check(p.evaluate("()=>window.__nb.tutStep") == s1 + 1 and p.evaluate("()=>window.__nb.S.lv.davul") == 2, 'Yükselt adımı Enter ile ilerliyor')
    # 3) Asistan çoklu alım + ileri sarma
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.auto.asst=true;S.nota=1e6;nb.recalc()}")
    r = p.evaluate("()=>{const nb=window.__nb,S=nb.S,n0=S.nota,l0=JSON.stringify([S.lv,S.def,S.up,S.slots]);nb.asstReset();nb.autoTick();return {sp:n0-S.nota,ch:l0!==JSON.stringify([S.lv,S.def,S.up,S.slots]),m:document.getElementById('msg').textContent}}")
    check(r['ch'] and 1.5e4 < r['sp'] <= 2.5e5 + 1, 'Asistan bir turda bütçesinin çoğunu harcadı (♪%d ≤ 250.000; “%s”)' % (r['sp'], r['m'][:50]))
    if not p.evaluate("()=>window.__nb.playing"):
        cv = p.locator('#cv').bounding_box(); p.mouse.click(cv['x'] + cv['width'] / 2, cv['y'] + cv['height'] / 2); p.wait_for_function("()=>window.__nb.playing", timeout=3000)
    p.evaluate("()=>{window.__nb.S.auto.asst=false;window.__nb.ff(300)}")
    k0 = p.evaluate("()=>window.__nb.S.kills"); p.wait_for_timeout(6000)
    st = p.evaluate("()=>({k:window.__nb.S.kills,e:window.__nb.enemies.length})")
    check(st['k'] > k0 or st['e'] > 0, 'ileri sarmadan sonra oyun akıyor (6 sn’de %d ölüm, %d düşman)' % (st['k'] - k0, st['e']))
    check(not errs, 'sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v54 geçti')
sys.exit(1 if fails else 0)
