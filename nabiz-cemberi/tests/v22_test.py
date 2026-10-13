"""v22: küçük temizlik — Kolay öğretici, Uyum ipucunda Uygula, telefon pedinde Sade/Hareketli/Yoğun, Kolay terimleri ve sade albüm/turne metni.

    python build.py && python tests/v22_test.py
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

SEED = """()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};window.__nb.unlockAll();S.ui='kolay';S.nota=1e9;S.bestWave=6;S.open={syn:1,rhy:1,pat:1};
  S.slots=['davul','trampet',null,null];S.lv={davul:5,trampet:3};S.rowm={};
  ['A','B','S','F'].forEach(k=>S.pat[k]=S.pat[k].map(r=>r.map(()=>0)));for(const s of [0,4,8,12])S.pat.A[0][s]=1;S.pat.A[1][0]=1;S.rowm.A1='m';nb.recalc();nb.renderPanels()}"""

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    p = b.new_page(viewport={'width': 1280, 'height': 800}); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(400)
    # v26: masaüstünde ilk adımda Stüdyo kapalı → hücreye dokunmayı anlatır; telefonda alttaki Yoğun'u da söyler (aşağıda)
    check('hücreye dokun' in p.text_content('#tutP') and 'Yoğun' not in p.text_content('#tutP'), 'masaüstünde ilk adım hücreye dokunmayı anlatıyor')
    p.click('#t-set'); p.wait_for_timeout(80); p.click('#setBox [data-act=ui][data-v=detay]'); p.wait_for_timeout(150)
    check('hücreye dokun: vuruş ekle' in p.text_content('#tutP'), 'Detaylı’da eski öğretici metni')
    p.evaluate(SEED); p.click('[data-act=tab][data-tab=studio]'); p.wait_for_timeout(50)
    t = p.text_content('#synChips')
    check('Backbeat' in t and p.locator('#synChips [data-act=tipApply]').count() == 1, 'ipucu Backbeat, Uygula düğmesi var')
    p.click('#synChips [data-act=tipApply]'); p.wait_for_timeout(80)
    row = p.evaluate("()=>window.__nb.S.pat.A[1].slice(0,16).join('')")
    check(row == '0000100000001000' and 'Backbeat' in p.text_content('#synChips .chips'), 'Uygula trampeti 2 ve 4’e yazdı, Backbeat tuttu (%s)' % row)
    check('Kıtayı temizle' in p.text_content('#slotAdd'), 'Kolay’da “Kıtayı temizle”')
    p.click('#stats'); p.wait_for_timeout(150)
    a = p.text_content('#anl')
    check('Ruh hâli' in a and 'Ritim tipi' in a and 'Groove · kıta' in a, 'Analiz’de Kolay terimleri')
    p.click('#anl [data-a=close]')
    p.evaluate("()=>{window.__nb.S.albMax=1;window.__nb.renderPanels()}")
    p.click('[data-act=tab][data-tab=album]'); p.wait_for_timeout(50)
    check('oyun baştan başlar' in p.text_content('#albumBox') and 'albümden sonra açılır' in p.text_content('#tourBox'), 'albüm ve turne metni sade')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    # telefon: Sahne pedinde seviye düğmeleri
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True); p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(400); p.evaluate(SEED); p.evaluate("()=>window.__nb.renderPanels()"); p.wait_for_timeout(100)
    check(p.locator('#pads [data-act=alvl]').count() == 3, 'telefon Sahne pedinde Sade · Hareketli · Yoğun')
    p.evaluate("()=>{document.querySelector('#pads [data-act=padNext]').click()}"); p.wait_for_timeout(50)
    p.tap('#pads [data-act=alvl][data-v="3"]'); p.wait_for_timeout(80)
    check(p.evaluate("()=>window.__nb.S.pat.A[1].slice(0,16).join('')") == '0000100000001000', 'pedden Yoğun trampet ritmini yazdı')
    sc = p.evaluate("()=>document.scrollingElement.scrollHeight-innerHeight")
    check(sc <= 0, 'Sahne hâlâ kaydırmasız')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    ctx.close()
    # EN
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True); p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(300)
    check('Yoğun' in p.text_content('#tutP'), 'telefonda Kolay öğretici alttaki Yoğun’u anlatıyor')
    p.evaluate("()=>{window.__nb.S.lang='en';window.__nb.S.tut={s:0,done:false};localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(window.__nb.S))}")
    with p.expect_navigation(): p.reload()
    p.wait_for_timeout(400)
    check('Dense' in p.text_content('#tutP') and 'Yoğun' not in p.text_content('#tutP'), 'Kolay öğretici İngilizce')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
