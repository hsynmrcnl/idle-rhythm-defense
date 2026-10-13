"""v17: zengin armoni (7'li, add9, sus4 çözülmesi, tek oktava katlanmış sesler, yürüyen bas) ve Üçlü'ye dönüş ayarı.

    python build.py && python tests/v17_test.py
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
def near(a, b, tol=0.6):
    return len(a) == len(b) and all(abs(x - y) < tol for x, y in zip(a, b))

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    p = b.new_page(viewport={'width': 1280, 'height': 800}); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto('http://127.0.0.1:%d/' % PORT); p.wait_for_timeout(500)
    p.evaluate("()=>{const S=window.__nb.S;S.tut={s:0,done:true};S.scale='minor';S.meter='m44';window.__nb.recalc()}")
    check(p.evaluate("()=>window.__nb.S.harm") == 'zengin', 'varsayılan armoni zengin')
    q = lambda s: p.evaluate("(s)=>({f:window.__nb.chordFreqsAt(0,s),l:window.__nb.chordLabel(0,s),w:window.__nb.walkSemi(0,s)})", s)
    # minör pop: Am F C G → Am7 Fmaj7 Cmaj7 G7sus4→G7, sesler A3–G#4 aralığında
    exp = {0: ('Am7', [220, 261.63, 329.63, 392]), 4: ('Fmaj7', [220, 261.63, 329.63, 349.23]), 8: ('Cmaj7', [246.94, 261.63, 329.63, 392]),
           12: ('G7sus4', [261.63, 293.66, 349.23, 392]), 14: ('G7', [246.94, 293.66, 349.23, 392])}
    for s, (lab, fr) in exp.items():
        r = q(s)
        check(r['l'] == lab and near(r['f'], fr), 'adım %d: %s %s' % (s, r['l'], [round(x, 1) for x in r['f']]))
    # yürüyen bas: kök, beşli, sonraki köke (F) ölçekten komşu G
    w = [q(s)['w'] for s in (0, 1, 2, 3)]
    check(w == [0, 0, 7, -2], 'bas Am üstünde A A E G → F (%s)' % w)
    # hicaz: A B♭ Gm A → A7 B♭maj7 Gm7 A7 (tonikte sus yok)
    p.evaluate("()=>{window.__nb.S.scale='hicaz';window.__nb.recalc()}")
    labs = [q(s)['l'] for s in (0, 4, 8, 12)]
    check(labs == ['A7', 'B♭maj7', 'Gm7', 'A7'], 'hicaz pop: %s' % ' '.join(labs))
    # makam demi ('5') iki modda da aynı
    p.evaluate("()=>{const S=window.__nb.S;S.up.akor=1;S.prog=Array(8).fill('root');window.__nb.recalc()}")
    r = q(0)
    check(r['l'] == 'A5' and len(r['f']) == 3, 'hicaz dem akoru değişmiyor (%s)' % r['l'])
    # Üçlü: eski kök konumu, bas hep kökte
    p.evaluate("()=>{const S=window.__nb.S;S.scale='minor';S.up={};S.prog=Array(8).fill('pop');S.harm='uclu';window.__nb.recalc()}")
    r0, r3 = q(0), q(3)
    check(r0['l'] == 'Am' and near(r0['f'], [220, 261.63, 329.63]) and r3['w'] == 0, 'Üçlü modda Am kök konumda, bas kökte')
    # Görünüm'den seçim, albümden sonra da kalır
    p.evaluate("()=>{window.__nb.S.harm='zengin';window.__nb.renderPanels()}")
    p.click('[data-act=tab][data-tab=look]'); p.wait_for_timeout(50)
    p.click('[data-act=harm][data-v=uclu]'); p.wait_for_timeout(50)
    check(p.evaluate("()=>window.__nb.S.harm") == 'uclu', 'Görünüm → Armoni → Üçlü')
    p.evaluate("()=>{const S=window.__nb.S;S.runEarned=1e30}")
    p.click('[data-act=tab][data-tab=album]'); p.click('#aBtn'); p.wait_for_timeout(100)
    check(p.evaluate("()=>window.__nb.S.harm") == 'uclu' and p.evaluate("()=>window.__nb.S.albums.length") == 1, 'armoni seçimi albümden sonra kalıyor')
    p.click('[data-act=tab][data-tab=look]'); p.click('[data-act=harm][data-v=zengin]')
    # örnek şarkılar zengin armoniyle hatasız çalıyor
    p.click('#demo'); p.wait_for_timeout(2500)
    check(p.evaluate("()=>window.__nb.playing"), 'örnek şarkı çalıyor')
    p.click('#demo2'); p.wait_for_timeout(2500)
    p.click('#demo'); p.wait_for_timeout(100)
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    # EN
    p.evaluate("()=>{window.__nb.S.lang='en';localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(window.__nb.S))}")
    with p.expect_navigation(): p.reload()
    p.wait_for_timeout(300)
    p.click('[data-act=tab][data-tab=look]'); p.wait_for_timeout(50)
    t = p.text_content('#fxBox')
    check('Harmony' in t and 'Rich' in t and 'Triads' in t and 'Armoni' not in t, 'Armoni satırı İngilizce')
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
