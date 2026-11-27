"""v102 açılış duyuruları ve simge düğmeler (oyuncu turu 20261125-1543): kısa öğreticide Atla geçilen açılışları tek satırda
yerleriyle duyurur; bayatlayıp düşen açılış da duyurulur (oyuncu o sekmeye girdiyse duyurulmaz).

    python build.py && python tests/v102_test.py
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
    er=[];ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=['def','look','anl'];S.tutm=0;nb.miniGapT=0;S.bestWave=14}");p.wait_for_timeout(700)
    check(p.is_visible('#tutL') and 'Savunma' in p.text_content('#tutLT'),'ilk kısa öğretici Savunma')
    p.wait_for_timeout(5200);p.click('#tutSkipL');p.wait_for_timeout(300)
    m=p.text_content('#msg')
    check('Açıldı' in m and 'Mağaza' in m and 'Analiz' in m and 'üst bilgiye dokun' in m,'Atla geçilenleri yerleriyle duyurdu (“%s”)'%m)
    # bayat düşen
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;document.getElementById('msg').textContent='';S.tipq=['ord'];S.tipw={ord:1};S.bestWave=20;S.tabSeen={};nb.miniGapT=0;nb.tutTick()}");p.wait_for_timeout(500)
    m=p.text_content('#msg')
    check('Siparişler' in m and 'sağ üst' in m,'bayat düşen Siparişler duyuruldu (“%s”)'%m)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;document.getElementById('msg').textContent='';nb.setTab('def');S.tipw={def:1};S.tabSeen={def:30};S.bestWave=30;S.tipq=['def'];nb.miniGapT=0;nb.tutTick()}");p.wait_for_timeout(500)
    check('Savunma' not in p.text_content('#msg'),'oyuncu Savunma’ya kendisi girdiyse duyurulmadı')
    # köşe düğmeleri yazılı; 5 dalga geri iki dokunuş
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tipq=[];S.tutm=0;S.unl.ord=1;S.wave=12;S.bestWave=12;nb.unlVis();nb.setTab('stage');nb.renderPanels()}");p.wait_for_timeout(300)
    check(p.text_content('#ordBtn').strip()=='Sipariş','Sipariş düğmesinde yazı var')
    p.evaluate("()=>window.__nb.setTab('def')");p.wait_for_timeout(300);p.tap('#defSub [data-v=dalga]');p.wait_for_timeout(200)
    p.tap('[data-act=waveBack]');p.wait_for_timeout(200)
    check(p.evaluate("()=>window.__nb.S.wave")==12 and 'Emin misin?' in p.text_content('#defStatus'),'ilk dokunuş dalgayı değiştirmedi, onay istiyor')
    p.tap('[data-act=waveBack]');p.wait_for_timeout(200)
    check(p.evaluate("()=>window.__nb.S.wave")==7,'ikinci dokunuşla 5 dalga geri')
    # uyum çipi dokununca açıklama
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.lv.trampet=1;S.lv.hihat=1;S.slots=['davul','trampet','hihat',null];nb.recalc();nb.setTab('studio');nb.renderPanels()}");p.wait_for_timeout(200)
    p.evaluate("()=>{const b=document.querySelector('#secBar [data-k=syn]');b&&b.click()}");p.wait_for_timeout(200)
    p.evaluate("()=>{const b=document.querySelector('[data-act=autoAll]');b&&b.click()}");p.wait_for_timeout(400)
    n=p.locator('#synChips [data-act=synInfo]').count()
    if n:
        p.locator('#synChips [data-act=synInfo]').first.tap();p.wait_for_timeout(200)
        check(len(p.text_content('#msg'))>15,'uyum çipine dokununca açıklama (“%s”)'%p.text_content('#msg')[:60])
    else: check(False,'Hepsini düzenle sonrası uyum çipi yok')
    check('FAZLA' in p.evaluate("()=>document.querySelector('.gloss').textContent"),'Terimler’de FAZLA var')
    check(not er,'sayfa hatası yok '+'; '.join(er[:2]))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v102 geçti')
sys.exit(1 if fails else 0)

