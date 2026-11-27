"""v100 Prova ve duvar mesajı: Prova dalga 30'dan önce görünmez, sonra Savunma › Geliştirme'de; her seviye gelir ve hasar ×1,04;
Analiz çarpan dökümünde; albümde sıfırlanır. Albüm hazırken geri çekilme mesajı albümü söyler.

    python build.py && python tests/v100_test.py
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
    er=[];p=b.new_page(viewport={'width':1366,'height':768});p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.nota=1e7;S.bestWave=20;nb.recalc();nb.setTab('def');nb.renderPanels()}");p.wait_for_timeout(200)
    p.evaluate("()=>{const b=document.querySelector('#defSub [data-v=gel],#defSub button:nth-child(2)');b&&b.click()}");p.wait_for_timeout(200)
    check(p.locator('#defList [data-id=prova]').count()==0,'dalga 20’de Prova görünmüyor')
    p.evaluate("()=>{const nb=window.__nb;nb.S.bestWave=30;nb.renderPanels()}");p.wait_for_timeout(200)
    check(p.locator('#defList [data-id=prova]').count()==1,'dalga 30’da Prova Geliştirme’de')
    r0=p.evaluate("()=>[window.__nb.rate(),window.__nb.dps()]")
    p.evaluate("()=>document.querySelector('#defList [data-id=prova]').click()");p.wait_for_timeout(200)
    r1=p.evaluate("()=>[window.__nb.rate(),window.__nb.dps(),window.__nb.S.def.prova]")
    check(r1[2]==1 and abs(r1[0]/r0[0]-1.04)<0.005 and abs(r1[1]/r0[1]-1.04)<0.005,'Prova 1: gelir ve hasar ×1,04 (%s → %s)'%(r0,r1))
    c2=p.evaluate("()=>+document.querySelector('#defList [data-id=prova]').dataset.cost")
    check(abs(c2-2e5*1.35)<2,'ikinci seviye ♪270.000 (%s)'%c2)
    p.evaluate("()=>{window.__nb.setTab('stage');document.getElementById('stats').click()}");p.wait_for_timeout(300)
    check('Prova 1' in p.inner_text('#anl'),'Analiz çarpan dökümünde Prova')
    p.keyboard.press('Escape')
    # duvar mesajı
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.unl.album=1;S.runEarned=1e9;nb.retreatNow()}");p.wait_for_timeout(300)
    m=p.inner_text('#msg')
    check('albüm hazır' in m and 'Savunma › Albüm' in m,'albüm hazırken geri çekilme albümü söylüyor (“%s”)'%m)
    # albümde sıfırlanır, dalga 30 görülmüş olduğundan görünür kalır
    p.evaluate("()=>window.__nb.releaseAlbum()");p.wait_for_timeout(300)
    check(not p.evaluate("()=>window.__nb.S.def.prova"),'albümde Prova sıfırlandı')
    check(not er,'sayfa hatası yok '+'; '.join(er[:2]))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v100 geçti')
sys.exit(1 if fails else 0)
