"""v105 öğretici hücre adımları (oyuncu turu 20261127-1719): 48 px dokunma alanı, delikteki her dokunuş doğru hücre, balon halkanın altında, ▶ adımında alttaki Başlat.

    python build.py && python tests/v105_test.py
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
    for (w,h) in [(375,667),(390,844)]:
        ctx=b.new_context(viewport={'width':w,'height':h},is_mobile=True,has_touch=True);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
        p.goto(URL);p.wait_for_timeout(900);p.tap('#tutLBtn');p.wait_for_timeout(500)
        hb=p.locator('#tutHole').bounding_box()
        check(hb['width']>=46,'%d: hücre adımında dokunma alanı ≥48 px (%d)'%(w,hb['width']))
        res=[]
        for k in range(4):
            hb=p.locator('#tutHole').bounding_box()
            p.touchscreen.tap(hb['x']+hb['width']/2+18,hb['y']+hb['height']/2-14);p.wait_for_timeout(450)
            if k==1:
                bub=p.locator('#tutBub').bounding_box();cv=p.locator('#cv').bounding_box();L=min(cv['width'],cv['height'])
                check(bub['y']>=cv['y']+cv['height']/2+L/2*0.9-2,'%d: balon halkanın altında (%d)'%(w,bub['y']))
            res.append(p.evaluate("()=>window.__nb.S.pat.A[0].filter(Boolean).length"))
        check(res==[1,2,3,4],'%d: kenara yakın dokunuşlar da doğru hücreyi koyuyor, silmiyor (%s)'%(w,res))
        check('Başlat' in p.text_content('#tutLT'),'%d: ▶ adımına geçti'%w)
        ctx.close()
    # masaüstü: ▶ adımında alttaki Başlat da çalışır
    ctx=b.new_context(viewport={'width':1366,'height':768});p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(900);p.click('#tutLBtn');p.wait_for_timeout(400)
    for k in range(4):
        p.evaluate("()=>{}");hb=p.locator('#tutHole').bounding_box();p.mouse.click(hb['x']+hb['width']/2,hb['y']+hb['height']/2);p.wait_for_timeout(400)
    check('Başlat' in p.text_content('#tutLT'),'masaüstü: ▶ adımı')
    if p.is_visible('#play'):
        p.click('#play');p.wait_for_timeout(500)
        check(p.evaluate("()=>window.__nb.playing") and 'Başlat' not in p.text_content('#tutLT'),'alttaki Başlat ▶ adımını geçiyor')
    check(not er,'sayfa hatası yok '+(er[0] if er else ''))
    b.close()
srv.shutdown()
print('hepsi geçti' if not fails else 'BAŞARISIZ: %d'%len(fails));sys.exit(1 if fails else 0)
