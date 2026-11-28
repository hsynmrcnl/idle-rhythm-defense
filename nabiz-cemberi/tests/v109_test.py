"""v109 toplu al: nota birikince öneri çipi ve Analiz düğmesi notanın %90’ına kadar en verimli alımları yapar.

    python build.py && python tests/v109_test.py
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
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.auto.asst=false;S.nota=60000;S.bestWave=9;S.slots=['davul',null,null,null];S.lv.davul=12;nb.recalc();nb.renderPanels();nb.startStop()}");p.wait_for_timeout(3600)
    check(p.is_visible('#hintChip') and 'Toplu al' in p.text_content('#hintChip'),'nota birikince Toplu al çipi (%s)'%p.text_content('#hintChip'))
    r0=p.evaluate("()=>window.__nb.rate()")
    p.tap('#hintChip');p.wait_for_timeout(500)
    st=p.evaluate("()=>{const S=window.__nb.S;return [S.nota,S.slots.filter(Boolean).length,window.__nb.rate()]}")
    check(st[0]<60000*0.2 and st[1]>=3 and st[2]>r0*2,'toplu alım notayı harcadı, yeni enstrüman koydu, gelir arttı (%s)'%st)
    check('Toplu alım' in p.text_content('#msg'),'toplu alım mesajı')
    # Analiz'de düğme
    p.evaluate("()=>{const S=window.__nb.S;S.nota=5e5;window.__nb.anlToggle(true)}");p.wait_for_timeout(300)
    check(p.locator('#anl [data-a=bulk]').count()==1,'Analiz’de Toplu al düğmesi')
    n0=p.evaluate("()=>window.__nb.S.nota");p.tap('#anl [data-a=bulk]');p.wait_for_timeout(400)
    check(p.evaluate("()=>window.__nb.S.nota")<n0*0.5,'Analiz’den toplu alım')
    ctx.close()
    check(not er,'sayfa hatası yok '+(er[0] if er else ''))
    b.close()
srv.shutdown()
print('hepsi geçti' if not fails else 'BAŞARISIZ: %d'%len(fails));sys.exit(1 if fails else 0)
