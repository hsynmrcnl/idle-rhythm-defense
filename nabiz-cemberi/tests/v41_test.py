"""v41: zorunlu öğretici — spot ışığı, hedef dışı dokunuş engeli, 13 adım, 5 sn sonra Atla, Ayarlar’dan geçici oyunda yeniden başlatma.

    python build.py && python tests/v41_test.py
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

def hole(p):
    return p.evaluate("()=>{const h=document.getElementById('tutHole').getBoundingClientRect();return [h.left+h.width/2,h.top+h.height/2,h.width]}")
with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe, args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch()
    for ph in (1, 0):
        print('telefon' if ph else 'masaüstü')
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True) if ph else b.new_context(viewport={'width': 1280, 'height': 800})
        p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.goto(URL); p.wait_for_timeout(600)
        st = lambda: p.evaluate("()=>window.__nb.tutStep")
        n = lambda: p.evaluate("()=>window.__nb.TUT[window.__nb.tutStep]?window.__nb.TUT[window.__nb.tutStep].n:99")
        check(p.is_visible('#tutBub') and st() == 0 and not p.is_visible('#tutSkipL'), 'yeni oyunda öğretici katmanı açık, Atla henüz yok')
        p.mouse.click(5, 400); p.wait_for_timeout(200)
        check(st() == 0, 'karartılmış yere dokunmak ilerletmiyor')
        p.click('#tutLBtn'); p.wait_for_timeout(400)
        if ph: p.screenshot(path=os.path.join(R, 'build', 'v41_tut.png'))
        p.mouse.click(5, 400); p.wait_for_timeout(200)
        check(st() == 1 and p.evaluate("()=>window.__nb.S.pat.A[0].every(v=>!v)"), 'hücre adımında dışarı dokunmak hücre eklemiyor')
        for k in range(4):
            x, y, w = hole(p); p.mouse.click(x, y); p.wait_for_timeout(450)
        check(st() == 5 and p.evaluate("()=>window.__nb.S.pat.A[0].filter(Boolean).length") == 4, 'dört hücre sırayla dolduruldu (adım %d)' % st())
        x, y, w = hole(p); p.mouse.click(x, y); p.wait_for_timeout(400)
        check(p.evaluate("()=>window.__nb.playing") and n() == 5, '▶ ile müzik başladı, Nota adımı')
        p.click('#tutLBtn'); p.wait_for_timeout(300)
        check(n() == 6, 'ilk düşman adımı (izleme)')
        for k in range(60):
            if n() != 6: break
            p.wait_for_timeout(500)
        check(n() == 7 and p.evaluate("()=>window.__nb.S.kills") >= 1, 'ilk düşman düştü, Ritme vur adımı')
        check(p.is_visible('#tutSkipL'), '5 sn sonra Atla göründü')
        x, y, w = hole(p); cx = x + w * 0.42; cy = y - w * 0.42 if ph else y - w * 0.42
        for k in range(40):
            if n() != 7: break
            p.mouse.click(x - w * 0.45, y - w * 0.45); p.wait_for_timeout(137)
        check(n() >= 8 and p.evaluate("()=>window.__nb.playing"), 'Ritme vur tutturuldu, müzik durmadı')
        for want in range(10):
            if n() == 13: break
            x, y, w = hole(p); p.wait_for_timeout(350); x, y, w = hole(p); p.mouse.click(x, y); p.wait_for_timeout(500)
        check(n() == 13, 'arayüz adımları tamam (adım %s)' % n())
        s = p.evaluate("()=>{const S=window.__nb.S;return {lv:S.lv.davul,tr:S.lv.trampet,sl:S.slots.filter(Boolean).length,rm:S.rowm.A0}}")
        check(s['lv'] >= 2 and s['tr'] >= 1 and s['sl'] == 2 and s['rm'] == 3, 'Yükselt, Yoğun, Trampet ve Hepsini düzenle yapıldı (%s)' % s)
        p.click('#tutLBtn'); p.wait_for_timeout(300)
        check(p.evaluate("()=>window.__nb.S.tut.done") and p.is_hidden('#tutL'), 'Oyna ile öğretici bitti, katman kapandı')
        # v42 kısa öğreticiler: dalga 6'da Savunma, sonra Tempo (dalga 8)
        p.evaluate("()=>{const S=window.__nb.S;S.bestWave=8;S.nota=Math.max(S.nota,1e4)}"); p.wait_for_timeout(500)
        lab = lambda: p.evaluate("()=>document.getElementById('tutL').hidden?'':document.getElementById('tutLN').textContent+' | '+document.getElementById('tutLT').textContent")
        seen = []
        for k in range(14):
            l = lab()
            if not l: break
            seen.append(l)
            if p.is_visible('#tutLBtn'): p.click('#tutLBtn')
            else:
                p.wait_for_timeout(350); x, y, w = hole(p); p.mouse.click(x, y)
            p.wait_for_timeout(450)
        check(any('Savunma' in x for x in seen) and any('Tempo' in x for x in seen) and lab() == '', 'Savunma ve Tempo kısa öğreticileri sırayla oynandı (%s)' % seen)
        check(p.evaluate("()=>window.__nb.S.tipq.length") == 0, 'eski kart yok, sıra boş')
        # yeniden başlat: geçici oyunda, Atla ile kayıt geri gelir
        p.evaluate("()=>{const S=window.__nb.S;S.bestWave=9;S.wave=9}")
        p.evaluate("()=>window.__nb.tutSandbox()"); p.wait_for_timeout(300)
        check(p.evaluate("()=>window.__nb.tutSand") and p.evaluate("()=>window.__nb.S.bestWave") <= 1 and p.is_visible('#tutBub'), 'Ayarlar’dan yeniden başlatınca temiz geçici oyun')
        p.wait_for_timeout(5300); p.click('#tutSkipL'); p.wait_for_timeout(300)
        check(not p.evaluate("()=>window.__nb.tutSand") and p.evaluate("()=>window.__nb.S.bestWave") == 9 and p.evaluate("()=>window.__nb.S.lv.trampet") >= 1, 'Atla ile kendi oyununa döndü')
        check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
        ctx.close()
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
