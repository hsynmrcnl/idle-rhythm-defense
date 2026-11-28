"""v110 oyuncu turu 20261128-1511: Toplu al çipi Asistan açıkken de, mesaj ne alındığını söyler, çip mesajın üstünde; Durdu mesajı; kısa öğretici balonu.

    python build.py && python tests/v110_test.py
"""
import os, sys, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));DIST=os.path.join(R,'dist')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
srv=socketserver.TCPServer(('127.0.0.1',0),functools.partial(Q,directory=DIST));PORT=srv.server_address[1]
threading.Thread(target=srv.serve_forever,daemon=True).start()
URL='http://127.0.0.1:%d/'%PORT
fails=[]
def check(ok,what):
    print(('  ok  ' if ok else '  FAIL ')+what)
    if not ok: fails.append(what)
with sync_playwright() as pw:
    exe='/opt/pw-browsers/chromium'
    b=pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    er=[]
    ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(700)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.auto.asst=true;S.unl.asst=1;S.nota=60000;S.bestWave=9;S.slots=['davul',null,null,null];S.lv.davul=12;nb.recalc();nb.renderPanels();nb.startStop()}");p.wait_for_timeout(3600)
    check(p.evaluate("()=>window.__nb.asstOn()") and p.is_visible('#hintChip') and 'Toplu al' in p.text_content('#hintChip'),'Asistan açıkken de Toplu al çipi')
    p.tap('#hintChip');p.wait_for_timeout(500)
    m=p.text_content('#msg')
    check('Yeni:' in m and '→' in m and '/sn' in m,'mesaj neyin alındığını ve gelir/sn önce→sonra söylüyor (%s)'%m)
    p.evaluate("()=>{const S=window.__nb.S;S.nota=60000;window.__nb.hintCheck&&window.__nb.hintCheck()}");p.wait_for_timeout(3600)
    if p.is_visible('#hintChip'):
        cb=p.locator('#hintChip').bounding_box();mb=p.locator('#msg').bounding_box()
        check(cb['y']+cb['height']<=mb['y']+mb['height']-50 or cb['y']+cb['height']<=mb['y'],'çip mesaj satırının üstünde')
    # Durdu mesajı başlatınca siliniyor
    p.wait_for_timeout(2600)  # toplu alım mesajının önceliği (msgP 6 sn) bitsin
    p.evaluate("()=>{window.__nb.startStop()}");p.wait_for_timeout(200)
    check('Durdu' in p.text_content('#msg'),'durdurunca Durdu mesajı')
    p.evaluate("()=>{window.__nb.startStop()}");p.wait_for_timeout(200)
    check('Durdu' not in p.text_content('#msg'),'başlatınca Durdu mesajı silindi')
    # kısa öğretici balonu büyük hedefte üstte
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tipq=['tap'];S.tutm=0;nb.miniGapT=0;nb.setTab('stage')}");p.wait_for_timeout(800)
    bb=p.locator('#tutBub').bounding_box();sb=p.locator('#slotBar').bounding_box()
    check(bb['y']+bb['height']<sb['y'],'Ritme vur kısa öğreticisinin balonu 8 yer şeridini örtmüyor')
    ctx.close()
    # tempo tuzağı: otomatik alım tempoyu temanın aralığından çıkarmaz
    ctx=b.new_context();p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(600)
    bpm=p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.bpm=130;S.bmax=130;S.nota=1e4;S.lv.trampet=3;S.slots=['davul','trampet',null,null];nb.recalc();for(let i=0;i<30;i++){const k=nb.asstPick(1e9);if(!k)break;nb.hintApplyK(k)}return S.bpm}")
    check(bpm<=130,'Asistan/Toplu al tempoyu Neon aralığının (90–130) dışına itmiyor (%s)'%bpm)
    ctx.close()
    check(not er,'sayfa hatası yok '+(er[0] if er else ''))
    b.close()
srv.shutdown()
print('hepsi geçti' if not fails else 'BAŞARISIZ: %d'%len(fails));sys.exit(1 if fails else 0)
