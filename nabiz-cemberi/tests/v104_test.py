"""v104 ekonomi (oyuncu turu 20261127-1719): Davul hasarı Sv12 sonrası 0,4/seviye, Prova kısa öğreticisi ve yeni işareti, Mağaza’da ucuz sahne katmanları üstte.

    python build.py && python tests/v104_test.py
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
    er=[];ctx=b.new_context(viewport={'width':375,'height':667},is_mobile=True,has_touch=True);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.unl.prova=0;S.tipq=[];S.tutm=0;nb.miniGapT=0;S.bestWave=31;S.nota=5e5;nb.recalc();nb.renderPanels()}");p.wait_for_timeout(200)
    r=p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.slots=['davul',null,null,null];const d=l=>{S.lv.davul=l;nb.recalc();return nb.dps()},r0=nb.rate();S.lv.davul=12;nb.recalc();const r12=nb.rate();return [d(12)/d(6),d(24)/d(12),r12]}")
    check(abs(r[0]-2)<0.01,'Davul hasarı Sv12’ye kadar seviyeyle doğru orantılı (%.2f)'%r[0])
    check(abs(r[1]-(12+12*0.4)/12)<0.01,'Davul hasarı Sv12 sonrası seviye başına 0,4 (%.2f)'%r[1])
    p.evaluate("()=>window.__nb.unlCheck()");p.wait_for_timeout(600)
    check(p.is_visible('#tutL') and 'Prova' in p.text_content('#tutLT'),'dalga 30’da Prova kısa öğreticisi')
    p.evaluate("()=>window.__nb.setTab('def')");p.wait_for_timeout(700)
    check(p.is_visible('#tutL') and p.locator('#defList .dtile[data-id=prova]').is_visible(),'Prova kutusu gösteriliyor')
    check('yeni' in p.text_content('#defList .dtile[data-id=prova]'),'alınmamış Prova “yeni” işaretli')
    p.evaluate("()=>{window.__nb.S.tipq=[];window.__nb.S.tutm=0;window.__nb.setTab('shop')}");p.wait_for_timeout(300)
    h=p.evaluate("()=>[...document.querySelectorAll('#p-shop section h2')].map(e=>e.textContent)")
    check(h and h[0]=='Sahne katmanları','Mağaza’da ilk bölüm Sahne katmanları (%s)'%h)
    check(not er,'sayfa hatası yok '+(er[0] if er else ''))
    b.close()
srv.shutdown()
print('hepsi geçti' if not fails else 'BAŞARISIZ: %d'%len(fails));sys.exit(1 if fails else 0)
