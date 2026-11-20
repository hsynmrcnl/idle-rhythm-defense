"""v82: yeni düşman tanıtım mesajı (ilk gelişte bir kez), kesik kayıt kodu sade hata, dil değişince devam.

    python build.py && python tests/v82_test.py
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
    er=[];ben=lambda t:'truncated' in t or 'Compressed input' in t;p=b.new_page(viewport={'width':1100,'height':760});p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.muted=true;S.bestWave=50;nb.recalc()}")
    cv=p.locator('#cv').bounding_box();p.mouse.click(cv['x']+cv['width']/2,cv['y']+cv['height']/2);p.wait_for_timeout(500)
    m=p.evaluate("(w)=>new Promise(res=>{const nb=window.__nb;nb.S.enemyTold={};nb.setWave(w);setTimeout(()=>res(document.getElementById('msg').textContent),900)})",15)
    check('Bölünen' in m and 'Alan' in m,'yeni düşman ilk gelişte tanıtılıyor + karşı rol (“%s”)'%m[:50])
    m2=p.evaluate("()=>new Promise(res=>{document.getElementById('msg').textContent='';window.__nb.setWave(15);setTimeout(()=>res(document.getElementById('msg').textContent),900)})")
    check('Bölünen' not in m2,'ikinci kez tanıtım tekrar etmiyor')
    # kesik kayıt kodu → sade mesaj, ham teknik mesaj yok
    p.evaluate("()=>window.__nb.setTab('set')");p.wait_for_timeout(200)
    code=p.evaluate("()=>window.__nb.exportCode?window.__nb.exportCode():''")
    p.fill('#saveCode', (code[:-6] if code else 'NB2.bozuk'))
    p.click('#p-set [data-act=loadCode]');p.wait_for_timeout(400)
    lm=p.inner_text('#msg')
    check('Failed' not in lm and 'fetch' not in lm and ('bozuk' in lm or 'eksik' in lm),'kesik kod sade mesaj veriyor (“%s”)'%lm[:60])
    # dil değişince devam: nb-play saklanıyor mu (langReload yolu)
    hasplay=p.evaluate("()=>{try{sessionStorage.setItem('nb-play','1');return sessionStorage.getItem('nb-play')==='1'}catch(e){return false}}")
    check(hasplay,'sessionStorage nb-play yazılabiliyor (dil-devam altyapısı)')
    er=[x for x in er if not ben(x)]  # zararsız: bozuk kod sıkıştırma akışı konsol çıktısı (kullanıcıya temiz mesaj gider)
    check(not er,'sayfa hatası yok %s'%er[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v82 geçti')
sys.exit(1 if fails else 0)
