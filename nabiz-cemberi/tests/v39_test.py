"""v39: şarkı paylaşma bağlantısı (#s=…): açan kişi şarkıyı dinler, “kendi oyunun” ile kendi oyununa geçer.

    python build.py && python tests/v39_test.py
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
    # gönderen
    ctx = b.new_context(viewport={'width': 1280, 'height': 800}, permissions=['clipboard-read', 'clipboard-write'])
    p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(300)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};nb.unlockAll();S.slots=['davul','bas','piyano',null];S.lv={davul:5,bas:3,piyano:2};S.bpm=112;localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}")
    p.reload(); p.wait_for_timeout(400)
    p.evaluate("()=>{const S=window.__nb.S;S.pat.A[0].fill(0);[0,4,8,12].forEach(s=>S.pat.A[0][s]=1);S.pat.A[1].fill(0);S.pat.A[1][0]=2;S.pat.A[2].fill(0);S.pat.A[2][6]=1}")
    code = p.evaluate("async()=>await window.__nb.zipJson(window.__nb.songOf())")
    check(len(code) < 1500 and code[0] in '12', 'bağlantı kısa (%d karakter)' % len(code))
    p.click('#t-set'); p.wait_for_timeout(150); p.click('#p-set [data-act=share]'); p.wait_for_timeout(300)
    url = p.evaluate("()=>document.getElementById('shareUrl').value")
    check(url.startswith(URL) and '#s=' in url, 'Ayarlar → Paylaş bağlantı üretir')
    check(not errs, 'gönderen: sayfa hatası yok ' + '; '.join(errs))
    ctx.close()
    # alan: yeni oyuncu
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(url); p.wait_for_timeout(900)
    st = p.evaluate("()=>{const nb=window.__nb;return {sh:nb.shareOn,sl:nb.S.slots.slice(0,3),bpm:nb.S.bpm,a0:nb.S.pat.A[0].join(''),pl:nb.playing}}")
    check(st['sh'] and st['sl'] == ['davul', 'bas', 'piyano'] and st['bpm'] == 112 and st['a0'].startswith('1000100010001000') and st['pl'], 'yeni oyuncu bağlantıyı açınca şarkı çalıyor (%s)' % st)
    check(p.is_visible('#demoChip') and 'Paylaşılan' in p.inner_text('#demoChip'), 'sahnede “Paylaşılan şarkı · kendi oyunun” düğmesi')
    p.click('#demoChip'); p.wait_for_timeout(300)
    st = p.evaluate("()=>({sh:window.__nb.shareOn,h:location.hash,sl:window.__nb.S.slots.filter(Boolean).length,saved:!!localStorage.getItem('nabiz-cemberi-v3')})")
    check(not st['sh'] and st['h'] == '' and st['sl'] <= 1, 'kendi oyununa geçti, adres temizlendi (%s)' % st)
    check(not errs, 'alan: sayfa hatası yok ' + '; '.join(errs))
    # bozuk bağlantı
    p.goto(URL + '#s=2bozukveri'); p.wait_for_timeout(700)
    check(not p.evaluate("()=>window.__nb.shareOn") and p.evaluate("()=>location.hash") == '', 'bozuk bağlantı oyunu bozmuyor')
    check(p.evaluate("()=>window.__nb.songOk({v:1,slots:['yok'],meter:'m44',scale:'minor',bpm:100})") is False, 'bilinmeyen enstrüman reddediliyor')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    ctx.close()
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
