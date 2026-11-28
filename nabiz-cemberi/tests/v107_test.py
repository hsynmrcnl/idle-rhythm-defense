"""v107 küçükler (oyuncu turu 20261127-1719): panel başlığında rol, Analiz üstünde köşe düğmeleri, Shaker %0, yer açınca Tam kadro.

    python build.py && python tests/v107_test.py
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
    p.goto(URL);p.wait_for_timeout(600)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.nota=5e6;S.lv.trampet=3;S.lv.shaker=2;S.slots=['davul','trampet','shaker',null];S.unl.ord=1;nb.recalc();nb.renderPanels();nb.unlVis()}");p.wait_for_timeout(300)
    # panel başlığında rol kırpılmaz
    p.evaluate("()=>window.__nb.slotOpen(2)");p.wait_for_timeout(300)
    rb=p.locator('#padName .role').bounding_box();nb_=p.locator('#padName').bounding_box()
    check(rb and rb['x']+rb['width']<=nb_['x']+nb_['width']+1,'panel başlığında rol etiketi tam görünüyor')
    # Analiz açıkken köşe düğmeleri gizli
    p.evaluate("()=>{window.__nb.slotClose();window.__nb.anlToggle(true)}");p.wait_for_timeout(300)
    check(not p.is_visible('#corner') and p.is_visible('#anl'),'Analiz açıkken Sipariş/Kitap köşesi gizli')
    p.evaluate("()=>window.__nb.anlToggle(false)");p.wait_for_timeout(200)
    check(p.is_visible('#corner'),'Analiz kapanınca köşe geri geliyor')
    # Shaker tabloda %0 değil rol adı
    p.evaluate("()=>{window.__nb.setTab('def')}");p.tap('#defSub [data-v=dalga]');p.wait_for_timeout(800)
    t=p.text_content('#istat')
    check('Destek' in t,'Shaker hasar tablosunda “Destek” (%s)'%t[:120])
    # Yer açılınca Tam kadro uyarısı
    m=p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.slots=['davul','trampet','shaker','davul'];S.pat.A=S.pat.A.map(r=>r.map((v,i)=>i%4===0?1:0));nb.recalc();nb.setTab('stage');nb.slotOpen(4)}");p.wait_for_timeout(1200)
    p.evaluate("()=>{window._ms=[];new MutationObserver(()=>window._ms.push(document.getElementById('msg').textContent)).observe(document.getElementById('msg'),{childList:true,characterData:true,subtree:true});}");p.tap('#iSheet [data-act=addslot]');p.wait_for_timeout(300)
    m=' | '.join(p.evaluate("()=>window._ms"))
    check('Tam kadro' in m,'yer açılınca Tam kadro uyarısı (“%s”)'%m)
    check(not er,'sayfa hatası yok '+(er[0] if er else ''))
    b.close()
srv.shutdown()
print('hepsi geçti' if not fails else 'BAŞARISIZ: %d'%len(fails));sys.exit(1 if fails else 0)
