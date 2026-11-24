"""v97 Mağaza: Görünüm'deki alımlar (3D sahne, Temalar, Sahne katmanları) ayrı Mağaza sekmesinde; telefonda alt çubukta
    kendi düğmesi (d-shop), masaüstünde Mağaza sekmesi, kısayol 8; Görünüm'de Düzen ve Efekt laboratuvarı kalır;
    alınabilir görünüm haberi Mağaza'yı işaretler; Görünüm kısa öğreticisi Mağaza'yı gösterir.

    python build.py && python tests/v97_test.py
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
TAB="()=>document.getElementById('app').dataset.tab"
with sync_playwright() as pw:
    exe='/opt/pw-browsers/chromium'
    b=pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    er=[]
    ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500)
    p.evaluate("()=>{const S=window.__nb.S;S.tut.done=true;S.tut.step=99;S.tipq=[]}");p.wait_for_timeout(200)
    check(p.is_hidden('#d-shop'),'yeni oyunda Mağaza düğmesi yok')
    p.evaluate("()=>{const nb=window.__nb;nb.unlockAll();nb.S.tipq=[];nb.S.tutm=0}");p.wait_for_timeout(300)
    dk=p.evaluate("()=>[...document.querySelectorAll('.dk')].filter(b=>!b.hidden).map(b=>b.id)")
    check(dk==['d-stage','d-def','d-look','d-shop','d-set'],'alt çubukta beş düğme, Mağaza Ayarlar’dan önce (%s)'%dk)
    p.tap('#d-shop');p.wait_for_timeout(250)
    sh=p.evaluate("()=>({tab:document.getElementById('app').dataset.tab,cur:document.querySelector('.dk[aria-current]').id,ids:['d3Box','themeList','stageList'].map(i=>!!document.querySelector('#p-shop #'+i)),vis:!document.getElementById('p-shop').hidden})")
    check(sh['tab']=='shop' and sh['cur']=='d-shop' and all(sh['ids']) and sh['vis'],'Mağaza açılıyor: 3D sahne, Temalar, Sahne katmanları (%s)'%sh)
    lk=p.evaluate("()=>({lay:!!document.querySelector('#p-look #layoutBox'),fx:!!document.querySelector('#p-look #fxBox'),th:!!document.querySelector('#p-look #themeList')})")
    check(lk['lay'] and lk['fx'] and not lk['th'],'Görünüm’de Düzen ve Efekt kalıyor, Temalar yok (%s)'%lk)
    p.tap('#d-set');p.wait_for_timeout(150);p.tap('#d-set');p.wait_for_timeout(150)
    check(p.evaluate(TAB)=='shop','Ayarlar’a ikinci dokunuş Mağaza’ya dönüyor')
    # alınabilir görünüm haberi Mağaza'yı işaretler
    p.evaluate("()=>window.__nb.setTab('stage')");p.wait_for_timeout(100)
    p.evaluate("()=>{document.getElementById('shopBadge').hidden=false;window.__nb.renderPanels()}");p.wait_for_timeout(300)
    check(p.evaluate("()=>!document.querySelector('#d-shop .dot').hidden"),'Mağaza işaretliyken alt çubuk düğmesinde nokta')
    p.tap('#d-shop');p.wait_for_timeout(300)
    check(p.evaluate("()=>document.getElementById('shopBadge').hidden&&document.querySelector('#d-shop .dot').hidden"),'Mağaza açılınca nokta kalkıyor')
    # kısa öğretici
    p.evaluate("()=>{const nb=window.__nb;nb.setTab('stage');nb.S.tipq=['look'];nb.S.tutm=0;nb.miniGapT=0;nb.tutTick&&nb.tutTick()}");p.wait_for_timeout(600)
    check('Mağaza' in p.text_content('#tutLT'),'Görünüm kısa öğreticisi Mağaza’yı gösteriyor (%s)'%p.text_content('#tutLT'))
    ctx.close()
    # masaüstü: sekme ve kısayol
    d=b.new_page(viewport={'width':1280,'height':800});d.on('pageerror',lambda e:er.append(str(e)))
    d.goto(URL);d.wait_for_timeout(500)
    d.evaluate("()=>{const nb=window.__nb;nb.S.tut.done=true;nb.unlockAll();nb.S.tipq=[];nb.S.tutm=0}");d.wait_for_timeout(300)
    tabs=d.evaluate("()=>[...document.querySelectorAll('.tabs .tab:not(.mob)')].filter(e=>!e.hidden&&e.offsetParent).map(e=>e.dataset.tab)")
    check(tabs[-1:]==['shop'],'masaüstünde Mağaza sekmesi en sağda (%s)'%tabs)
    d.keyboard.press('8');d.wait_for_timeout(150)
    check(d.evaluate(TAB)=='shop','8 → Mağaza')
    check(not er,'sayfa hatası yok '+'; '.join(er))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v97 geçti')
sys.exit(1 if fails else 0)
