"""v86 erişilebilirlik: rakam kısayolları (1–7 sekmeler, 0 Ayarlar, 9 Analiz), .seg düğmelerinde içe odak halkası,
    tuval odak halkası, sıradan .chip yazısı --muted.

    python build.py && python tests/v86_test.py
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
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.muted=true;nb.unlVis();nb.renderPanels()}");p.wait_for_timeout(300)
    st=lambda:p.evaluate("()=>({tab:document.getElementById('app').dataset.tab,f:document.activeElement&&document.activeElement.id})")
    p.keyboard.press('4');p.wait_for_timeout(250);s=st()
    check(s['tab']=='def' and s['f']=='t-def','4 → Savunma, odak sekme düğmesinde (%s)'%s)
    p.keyboard.press('2');p.wait_for_timeout(250);s=st()
    check(s['tab']=='studio' and s['f']=='t-studio','2 → Stüdyo (%s)'%s)
    p.keyboard.press('0');p.wait_for_timeout(250);s=st()
    check(s['tab']=='set','0 → Ayarlar (%s)'%s)
    p.keyboard.press('0');p.wait_for_timeout(250);s=st()
    check(s['tab']=='studio','0 tekrar → önceki sekme (%s)'%s)
    p.keyboard.press('1');p.wait_for_timeout(250);s=st()
    check(s['f']=='cv','1 masaüstünde sahne tuvalini odaklar (%s)'%s)
    oc=p.evaluate("()=>getComputedStyle(document.getElementById('cv')).outlineStyle")
    check(oc=='solid','tuval klavye odağında halka görünür (%s)'%oc)
    p.keyboard.press('9');p.wait_for_timeout(300)
    check(p.evaluate("()=>window.__nb.anlOn"),'9 → Analiz açılır')
    p.keyboard.press('Escape');p.wait_for_timeout(200)
    # kilitli sekme: mesaj verir, geçmez
    p.evaluate("()=>{const S=window.__nb.S;S.unl.book=0;S.unl.album=0;window.__nb.unlVis()}");p.wait_for_timeout(150)
    p.evaluate("()=>document.getElementById('msg').textContent=''")
    p.keyboard.press('5');p.wait_for_timeout(250);s=st()
    check(s['tab']!='book' and 'henüz' in p.inner_text('#msg'),'kilitli sekme kısayolu geçmez, haber verir (%s)'%s)
    # yazı alanında rakam kısayol değil
    p.keyboard.press('0');p.wait_for_timeout(250)
    p.focus('#saveCode');p.keyboard.press('3');p.wait_for_timeout(200);s=st()
    check(s['tab']=='set','yazı alanında rakam sekme değiştirmiyor (%s)'%s)
    p.keyboard.press('Escape');p.wait_for_timeout(200)
    # .seg odak halkası içe (kırpılmasın)
    p.evaluate("()=>window.__nb.setTab('studio')");p.wait_for_timeout(250)
    off=p.evaluate("""()=>{const b=[...document.querySelectorAll('.seg button')].find(x=>x.offsetParent);if(!b)return null;b.focus();return (b.matches(':focus-visible')?'':'(fv yok) ')+getComputedStyle(b).outlineOffset}""")
    check(off is not None and off.startswith('-'),'.seg düğmesinde odak halkası içe (%s)'%off)
    col=p.evaluate("""()=>{const c=document.querySelector('.chip:not(.on)');if(!c)return 'yok';const m=getComputedStyle(document.documentElement).getPropertyValue('--muted').trim();const d=document.createElement('span');d.style.color=m;document.body.appendChild(d);const mc=getComputedStyle(d).color;d.remove();return getComputedStyle(c).color===mc?'muted':getComputedStyle(c).color}""")
    check(col in ('muted','yok'),'sıradan .chip yazısı --muted (%s)'%col)
    check(not er,'sayfa hatası yok %s'%er[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v86 geçti')
sys.exit(1 if fails else 0)
