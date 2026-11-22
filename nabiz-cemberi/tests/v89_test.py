"""v89 albüm: önizleme gelir olarak (eşik altında eşikte verilecek hayran), eşikte "Hazır", onay düğmesi yerinde kalır ve
    uyarı altta; her albümün hayranı bir öncekinden %50 fazla (ALB_GROW).

    python build.py && python tests/v89_test.py
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
    b=pw.chromium.launch(executable_path=exe,args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch()
    er=[];p=b.new_page(viewport={'width':1366,'height':768});p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.muted=true;S.runEarned=6e6;S.bestWave=40;nb.unlVis();nb.setTab('album');nb.renderPanels()}");p.wait_for_timeout(400)
    t=p.inner_text('#aTxt')
    check('eşikte +10 hayran' in t and '×1 → ×1,5' in t,'eşik altında: eşikte verilecek hayran ve gelir (“%s”)'%t)
    p.evaluate("()=>{window.__nb.S.runEarned=2.4e7}");p.wait_for_timeout(300)
    t=p.inner_text('#aTxt')
    check(t.startswith('Hazır') and '+12 hayran' in t and '→ ×1,6' in t,'eşikte: Hazır + hayran + gelir (“%s”)'%t)
    bx0=p.locator('#aBtn').bounding_box()
    p.click('#aBtn');p.wait_for_timeout(200)
    bx1=p.locator('#aBtn').bounding_box();warn=p.locator('#aWarn')
    check(abs(bx0['x']-bx1['x'])<2 and abs(bx0['y']-bx1['y'])<2,'onayda düğme yerinde kalıyor (%s → %s)'%((round(bx0['x']),round(bx0['y'])),(round(bx1['x']),round(bx1['y']))))
    check(warn.count()==1 and 'kalır' in warn.inner_text(),'onay uyarısı altta ayrı satırda')
    p.click('#aBtn');p.wait_for_timeout(300)
    r=p.evaluate("()=>({n:window.__nb.S.albums.length,h:window.__nb.S.hayran,next:window.__nb.fansAt()})")
    check(r['n']==1 and r['h']==12,'ikinci dokunuş albümü çıkarıyor (%s)'%r)
    check(r['next']==15,'2. albümde eşikte +15 hayran (%%50 fazla) (%s)'%r['next'])
    check(p.locator('#aWarn').count()==0,'albümden sonra onay uyarısı kalmıyor')
    check(not er,'sayfa hatası yok %s'%er[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v89 geçti')
sys.exit(1 if fails else 0)
