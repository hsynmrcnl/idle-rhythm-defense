"""v101 erken çağır, seçili yer işareti, dokunma hedefleri: güçlü oyuncuda yeni dalgada kalan düşmanlar azken “Erken çağır” çıkar,
basınca kalan kuyruk hemen gelir ve atlanan süre için nota verir; baskında ve dalga 8'den önce çıkmaz. Seçili yer alt çizgiyle de işaretli.
Masaüstü ve yatayda 32 px'ten küçük düğme yok.

    python build.py && python tests/v101_test.py
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
SMALL="""()=>[...document.querySelectorAll('button,[role=switch],select')].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect();return [Math.round(Math.min(r.width,r.height)),e.id||e.dataset.act||e.textContent.trim().slice(0,12)]}).filter(x=>x[0]<32)"""
with sync_playwright() as pw:
    exe='/opt/pw-browsers/chromium'
    b=pw.chromium.launch(executable_path=exe,args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch()
    er=[];p=b.new_page(viewport={'width':1366,'height':768});p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.muted=true;S.lv.davul=80;nb.recalc();nb.renderPanels()}")
    p.evaluate("()=>{const nb=window.__nb;if(!nb.playing)nb.startStop()}");p.wait_for_timeout(300)
    # dalga 3: kapalı
    p.evaluate("()=>{const nb=window.__nb;nb.S.bestWave=3;nb.setWave&&nb.setWave(3)}");p.wait_for_timeout(2500);p.evaluate("()=>window.__nb.callCheck()")
    check(p.is_hidden('#callChip'),'dalga 8’den önce Erken çağır yok')
    # dalga 12 (yeni, baskın değil): çıkar
    ok=False
    for _ in range(40):
        p.evaluate("()=>{const nb=window.__nb,S=nb.S;if(!nb.wave||nb.wave.n<12||nb.wave.done){S.bestWave=11;nb.startWave(12,nb.nowT())}}");p.wait_for_timeout(250);p.evaluate("()=>window.__nb.callCheck()")
        if p.is_visible('#callChip'): ok=True;break
    check(ok,'güçlü oyuncuda yeni dalgada Erken çağır görünüyor')
    if ok:
        n0=p.evaluate("()=>window.__nb.S.nota");q0=p.evaluate("()=>window.__nb.wave.queue.length")
        p.click('#callChip');p.wait_for_timeout(300)
        s=p.evaluate("()=>({n:window.__nb.S.nota,q:window.__nb.wave.queue.length,m:document.getElementById('msg').textContent})")
        check(s['n']>n0 and s['q']<q0 and 'erken' in s['m'],'basınca kalan kuyruk geldi, nota bonusu (%s, kuyruk %d → %d)'%(s['m'],q0,s['q']))
    # baskın: çıkmaz
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.bestWave=14;nb.startWave(15,nb.nowT())}");p.wait_for_timeout(2600);p.evaluate("()=>window.__nb.callCheck()")
    check(p.is_hidden('#callChip'),'baskında Erken çağır yok')
    # seçili yer işareti
    after=p.evaluate("()=>getComputedStyle(document.querySelector('#sb8 .sbt.sel'),'::after').height")
    check(after=='3px','seçili yer alt çizgiyle işaretli (%s)'%after)
    p.evaluate("()=>{if(window.__nb.playing)window.__nb.startStop()}")
    p.evaluate("()=>{const nb=window.__nb;nb.setTab('studio');nb.slotOpen(0)}");p.wait_for_timeout(300)
    sm=p.evaluate(SMALL)
    check(not sm,'masaüstünde 32 px altı düğme yok (%s)'%sm)
    p.close()
    ctx=b.new_context(viewport={'width':844,'height':390},is_mobile=True,has_touch=True);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;nb.renderPanels()}")
    bad=[]
    for t in ['studio','def','look','shop','set']:
        p.evaluate("t=>window.__nb.setTab(t)",t);p.wait_for_timeout(200);bad+=p.evaluate(SMALL)
    check(not bad,'yatayda 32 px altı düğme yok (%s)'%bad[:4])
    check(not er,'sayfa hatası yok '+'; '.join(er[:2]))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v101 geçti')
sys.exit(1 if fails else 0)
