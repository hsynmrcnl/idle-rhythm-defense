"""v85: EN modunda dalga/patron mesajları tam İngilizce, kilitli Analiz etiketi; fareyle tuvale dokununca bayat klavye
    hücre mesajı yok; kısa öğreticinin ilk balonu neyin açıldığını söylüyor.

    python build.py && python tests/v85_test.py
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
TR=set('çğıöşüÇĞİÖŞÜ')
with sync_playwright() as pw:
    exe='/opt/pw-browsers/chromium'
    b=pw.chromium.launch(executable_path=exe,args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch()
    er=[];p=b.new_page(viewport={'width':1100,'height':760});p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500)
    # 1) fareyle tuvale dokununca "Yer 1 · ... · adım 1" bayat mesajı çıkmıyor
    p.evaluate("()=>{const S=window.__nb.S;S.tut.done=true;window.__nb.unlockAll();S.tipq=[];S.tutm=0;S.muted=true;document.getElementById('msg').textContent=''}")
    cv=p.locator('#cv').bounding_box();p.mouse.click(cv['x']+cv['width']*0.5,cv['y']+cv['height']*0.15);p.wait_for_timeout(300)
    m=p.inner_text('#msg')
    check('adım 1' not in m or 'Yer' not in m,'fare dokunuşu bayat klavye hücre mesajı yazmıyor (“%s”)'%m[:40])
    # klavye odağında yine söylüyor (Tab ile)
    p.evaluate("()=>{document.activeElement&&document.activeElement.blur();document.getElementById('msg').textContent=''}")
    ok=False
    for i in range(40):
        p.keyboard.press('Tab')
        if p.evaluate("()=>document.activeElement&&document.activeElement.id==='cv'"):ok=True;break
    m2=p.inner_text('#msg')
    check(ok and 'Yer' in m2,'klavye odağında hücre mesajı sürüyor (“%s”)'%m2[:40])
    # 2) EN: dalga/patron mesajları ve kilitli Analiz etiketi Türkçe harf içermiyor
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.lang='en';S.bestWave=60;nb.renderPanels()}");p.wait_for_timeout(300)
    got=p.evaluate("""()=>{const r=[];const W={2:1,4:1,6:1,9:1,15:1,21:1};const el=document.getElementById('msg');const nb=window.__nb;
      for(const w of [2,4,6,9,15,21,10,25,50]){el.textContent='';nb.S.enemyTold={bolen:1,iyilesen:1,zirhsans:1};nb.setWave(w);r.push(el.textContent)}return r}""")
    bad=[x for x in got if x and any(c in TR for c in x)]
    check(not bad,'EN modunda dalga/patron mesajları İngilizce %s'%bad[:2])
    lab=p.evaluate("()=>new Promise(r=>{const nb=window.__nb,S=nb.S;S.bestWave=5;S.wave=5;S.unl.anl=0;nb.unlVis();setTimeout(()=>r(document.getElementById('stats').getAttribute('aria-label')||''),400)})")
    check(lab.startswith('Analysis') and 'dalga' not in lab and 'unlocks at wave' in lab,'kilitli Analiz etiketi İngilizce (“%s”)'%lab)
    check(not er,'sayfa hatası yok %s'%er[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v85 geçti')
sys.exit(1 if fails else 0)
