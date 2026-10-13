"""Yeni (CC0) kayıt seti: paketler yüklenir, enstrümanlar onlarla çalar, Görünüm'den Klasik'e dönülür.

    python build.py && python tests/sf_cc0_test.py
"""
import os, sys, json, threading, functools, http.server, socketserver
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

PACKS = sorted(k[:-5] for k in os.listdir(os.path.join(DIST, 'sf')) if k.startswith('c_') and k.endswith('.json'))
with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    p = b.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto('http://127.0.0.1:%d/' % PORT); p.wait_for_timeout(500)
    check(len(PACKS) >= 14, 'dist/sf içinde %d CC0 paketi' % len(PACKS))
    res = p.evaluate("""async keys=>{const nb=window.__nb;nb.voice('davul');const out={};
      for(const k of keys){await nb.sfLoad(k);const s=nb.SF[k];out[k]=[s.st,s.zones.length]}return out}""", PACKS)
    for k in PACKS:
        st, n = res[k]
        check(st == 'ok' and n > 0, '%s yüklendi ve çözüldü (%d bölge)' % (k, n))
    # yeni set varsayılan: enstrümanlar c_ paketleriyle çalar
    played = p.evaluate("""()=>{const nb=window.__nb,r={};for(const id of ['piyano','keman','cello','harp','bas','trompet','tuba','flut','sakso','klavsen','kalimba','steel','didger'])r[id]=nb.sfVoice(id,0);
      for(const id of ['davul','trampet','hihat','darbuka','bendir','gong','clap','zil','tom','shaker','kasik'])r[id]=nb.sfDrum(id);return r}""")
    for k, v in played.items():
        check(v is True, '%s yeni setle çalıyor' % k)
    check(p.evaluate("()=>window.__nb.sfKeyOf('keman')") == 'c_keman' and p.evaluate("()=>window.__nb.sfKeyOf('timbal')") == '0470', 'eşleme: keman → c_keman, timbal klasikte (0470)')
    # Görünüm → Klasik
    p.evaluate("()=>{document.querySelector('[data-act=tab][data-tab=look]').click()}"); p.wait_for_timeout(100)
    p.click('[data-act=sfset][data-v=klasik]'); p.wait_for_timeout(100)
    check(p.evaluate("()=>window.__nb.S.sfset") == 'klasik' and p.evaluate("()=>window.__nb.sfKeyOf('keman')") == '0400' and p.evaluate("()=>window.__nb.sfKeyOf('didger')") is None,
          'Klasik seçilince FluidR3 paketine dönüyor, didgeridoo sentez')
    p.click('[data-act=sfset][data-v=yeni]'); p.wait_for_timeout(100)
    check(p.evaluate("()=>window.__nb.S.sfset") == 'yeni', 'Yeni’ye geri dönülüyor')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
