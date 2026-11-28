"""v108 oyuncu turu 20261128-1311: öğretici balonları, dalga −5/+5, panelde şerit başlığı, sade uyum metni, P kısayolu, panel açıkken alt düğmeler, Koleksiyon odağı.

    python build.py && python tests/v108_test.py
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
    # öğretici 8–11: balon paneli/şeridi örtmez (telefon)
    ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(800)
    for k in [9,10,11,12,13]:
        p.evaluate("k=>{const nb=window.__nb,S=nb.S;S.tut.s=k;S.kills=1;nb.tutTick()}",k);p.wait_for_timeout(600)
        bb=p.locator('#tutBub').bounding_box();hb=p.locator('#tutHole').bounding_box()
        check(bb['y']+bb['height']<=hb['y'],'öğretici %s: balon hedefin üstünde, örtmüyor'%p.text_content('#tutLT'))
    ctx.close()
    ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(600)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.wave=12;S.bestWave=15;S.slots=['davul','trampet','hihat',null];S.lv.trampet=2;S.lv.hihat=2;nb.recalc();nb.renderPanels()}");p.wait_for_timeout(300)
    # dalga gezinmesi −5/+5
    p.evaluate("()=>window.__nb.setTab('def')");p.tap('#defSub [data-v=dalga]');p.wait_for_timeout(300)
    t=p.text_content('.wnav');check('−5' in t and '+5' in t,'dalga gezinmesi −5 / +5 (%s)'%t.strip())
    # boş yer paneli açıkken şerit başlığı sızmıyor
    p.evaluate("()=>{window.__nb.setTab('stage');window.__nb.slotOpen(3)}");p.wait_for_timeout(300)
    check(p.evaluate("()=>getComputedStyle(document.querySelector('#slotBar .sbh')).visibility")=='hidden','panel açıkken 8 yer başlığı gizli')
    p.evaluate("()=>window.__nb.slotClose()");p.wait_for_timeout(200)
    check(p.evaluate("()=>getComputedStyle(document.querySelector('#slotBar .sbh')).visibility")=='visible','panel kapanınca başlık geri geliyor')
    # uyum açıklaması enstrüman adı ve adım numarası söylüyor
    m=p.evaluate("()=>window.__nb.synPlain('Bir Keskin 2. ve 4. grup başında')")
    check('Trampet' in m and '5·13' in m,'uyum açıklaması sade (%s)'%m)
    ctx.close()
    # masaüstü: P başlat/durdur, panel açıkken alt düğmeler Tab dışı, Koleksiyon Aç sonrası odak
    ctx=b.new_context(viewport={'width':1366,'height':768});p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(600)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.nota=1e6;nb.recalc();nb.renderPanels()}");p.wait_for_timeout(300)
    p.keyboard.press('p');p.wait_for_timeout(300);on=p.evaluate("()=>window.__nb.playing")
    p.keyboard.press('p');p.wait_for_timeout(300)
    check(on and not p.evaluate("()=>window.__nb.playing"),'P başlatıp durduruyor')
    p.evaluate("()=>window.__nb.slotOpen(0)");p.wait_for_timeout(200)
    check(p.evaluate("()=>document.querySelector('.controls').inert"),'panel açıkken alt düğmeler odak dışı')
    p.evaluate("()=>window.__nb.slotClose()");p.wait_for_timeout(200)
    check(not p.evaluate("()=>document.querySelector('.controls').inert"),'panel kapanınca alt düğmeler geri')
    p.keyboard.press('3');p.wait_for_timeout(400)
    p.evaluate("()=>{const b=document.querySelector('#collList [data-act=lv]:not([disabled])');b&&b.focus()}")
    p.keyboard.press('Enter');p.wait_for_timeout(400)
    f=p.evaluate("()=>{const a=document.activeElement;return a&&a!==document.body&&!!a.closest('#cSheet')}")
    check(f,'Koleksiyon’da Aç sonrası odak sayfada kalıyor')
    ctx.close()
    check(not er,'sayfa hatası yok '+(er[0] if er else ''))
    b.close()
srv.shutdown()
print('hepsi geçti' if not fails else 'BAŞARISIZ: %d'%len(fails));sys.exit(1 if fails else 0)
