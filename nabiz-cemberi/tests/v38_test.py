"""v38: Ses masası — dışa aktarma (WAV, MIDI) ücretsiz; yankı ve ses karıştırıcı satın alınır.

    python build.py && python tests/v38_test.py
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
    for ph in (1, 0):
        print('telefon' if ph else 'masaüstü')
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, accept_downloads=True) if ph else b.new_context(viewport={'width': 1280, 'height': 800}, accept_downloads=True)
        p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.goto(URL); p.wait_for_timeout(300)
        p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};nb.unlockAll();S.wave=19;S.bestWave=19;S.nota=1e6;S.slots=['davul','bas',null,null];S.lv={davul:2,bas:2};localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}")
        p.reload(); p.wait_for_timeout(400)
        check(p.evaluate("()=>document.querySelector('#p-studio [data-sec=desk]').hidden") is True, 'dalga 20 öncesi Ses masası kapalı')
        p.evaluate("()=>{const S=window.__nb.S;S.bestWave=20}"); p.wait_for_timeout(400)
        p.evaluate("()=>window.__nb.setTab('studio')")
        p.wait_for_timeout(200)
        if ph:
            p.click('#secBar [data-k=desk]'); p.wait_for_timeout(150)
        check(p.is_visible('#deskBox [data-act=midi]') and p.is_visible('#deskBox [data-act=deskBuy][data-k=rv]'), 'dalga 20: Ses masası açık, dışa aktarma ücretsiz, yankı satılık')
        mb = p.evaluate("()=>Array.from(window.__nb.midiBytes())")
        hdr = bytes(mb[:4]).decode(); ntr = mb[10] * 256 + mb[11]; non = sum(1 for k in range(len(mb) - 2) if (mb[k] & 0xF0) == 0x90 and mb[k + 2] > 0)
        k = 14; ok = True
        while k < len(mb):
            if bytes(mb[k:k + 4]) != b'MTrk': ok = False; break
            k += 8 + (mb[k + 4] << 24 | mb[k + 5] << 16 | mb[k + 6] << 8 | mb[k + 7])
        check(ok and k == len(mb), 'MIDI parçaları düzgün (MTrk uzunlukları tutuyor)')
        check(hdr == 'MThd' and ntr == 3 and non > 4, 'MIDI: başlık, tempo izi + 2 enstrüman izi, notalar (%d iz, ~%d nota)' % (ntr, non))
        with p.expect_download() as dl: p.click('#deskBox [data-act=midi]')
        check(dl.value.suggested_filename.endswith('.mid'), 'MIDI indiriliyor (%s)' % dl.value.suggested_filename)
        n0 = p.evaluate("()=>window.__nb.S.nota")
        p.click('#deskBox [data-act=deskBuy][data-k=rv]'); p.wait_for_timeout(100)
        check(p.evaluate("()=>window.__nb.S.desk.rv") == 1 and n0 - p.evaluate("()=>window.__nb.S.nota") >= 250000 - 1 and p.is_visible('#deskBox [data-act=rv][data-v=katedral]'), 'yankı ♪250.000 ile alındı, seçenekler göründü')
        p.click('#deskBox [data-act=rv][data-v=katedral]'); p.wait_for_timeout(100)
        p.evaluate("()=>window.__nb.ensureAudio&&window.__nb.ensureAudio()")
        p.click('#deskBox [data-act=deskBuy][data-k=mx]'); p.wait_for_timeout(100)
        check(p.evaluate("()=>window.__nb.S.desk.mx") == 1 and p.locator('#deskBox .mxr').count() == 2, 'ses karıştırıcı alındı, her dolu yer bir satır')
        p.click('#deskBox [data-act=mixM][data-i="1"]'); p.wait_for_timeout(80)
        p.locator('#deskBox input[data-mix="0"]').fill('50'); p.wait_for_timeout(80)
        check(p.evaluate("()=>[window.__nb.mixV(0),window.__nb.mixV(1)]") == [0.5, 0], 'sürgü %50, susturma 0')
        dps0 = p.evaluate("()=>window.__nb.dps()")
        check(dps0 > 0, 'susturulan enstrüman hasarı değiştirmiyor (dps %.1f)' % dps0)
        with p.expect_download(timeout=20000) as dl:
            p.evaluate("()=>window.__nb.recWav(1)")
            p.wait_for_timeout(200)
            check(p.evaluate("()=>window.__nb.recOn") is True, 'kayıt başladı')
        check(dl.value.suggested_filename.endswith('.wav') and p.evaluate("()=>window.__nb.recN") == 1, 'WAV indirildi (%s)' % dl.value.suggested_filename)
        import struct
        raw = open(dl.value.path(), 'rb').read(); smp = struct.unpack('<%dh' % ((len(raw) - 44) // 2), raw[44:44 + ((len(raw) - 44) // 2) * 2]); pk = max(abs(x) for x in smp)
        check(len(raw) > 100000 and raw[:4] == b'RIFF' and pk > 300, 'WAV geçerli ve sessiz değil (%d bayt, tepe %d)' % (len(raw), pk))
        check(p.evaluate("()=>window.__nb.rvKey") == 'katedral' and p.evaluate("()=>window.__nb.rvWet") > 0.5, 'Katedral yankısı çalıyor')
        p.click('#deskBox [data-act=mixReset]'); p.wait_for_timeout(80)
        check(p.evaluate("()=>[window.__nb.mixV(0),window.__nb.mixV(1)]") == [1, 1], 'Sıfırla hepsini %100 yapar')
        check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
        ctx.close()
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
