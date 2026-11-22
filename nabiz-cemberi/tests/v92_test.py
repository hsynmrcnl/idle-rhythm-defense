"""v92 yeni ana ekran adım 3+4: dock dört düğme (Sahne · Savunma·Albüm · Müzik·Görünüm · Ayarlar), Müzik | Görünüm alt
    gezinmesi, sağ üstte Sipariş/Kitap düğmeleri (açılınca görünür, hazır/yeni olunca yanar) ve sayfaları, Koleksiyon sayfası
    (sekme yok), ana öğretici yeni yapıyla baştan sona.

    python build.py && python tests/v92_test.py
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
    b=pw.chromium.launch(executable_path=exe,args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch()
    er=[]
    # --- telefon: ana öğretici baştan sona dokunarak
    ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(600)
    seen=[]
    for k in range(60):
        st=p.evaluate("()=>{const nb=window.__nb;if(nb.S.tut.done)return null;const s=nb.TUT[nb.tutStep];return {t:s.t,kind:s.kind,rv:!!s.rv}}")
        if st is None: break
        if not seen or seen[-1]!=st['t']: seen.append(st['t'])
        if st['kind']=='btn': p.click('#tutLBtn');p.wait_for_timeout(350);continue
        if st['kind']=='auto': p.evaluate("()=>{const nb=window.__nb;nb.ff(2)}");p.wait_for_timeout(300);continue
        if st['rv']: p.evaluate("()=>{window.__nb.S.seri=1}");p.wait_for_timeout(400);continue
        h=p.evaluate("()=>{const r=document.getElementById('tutHole').getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2,r.width]}")
        if h[2]<4: p.wait_for_timeout(250);continue
        p.mouse.click(h[0],h[1]);p.wait_for_timeout(450)
    done=p.evaluate("()=>window.__nb.S.tut.done")
    want=['Davul','Yükselt','Otomatik ritim','Koleksiyon','Trampet','Müzik','Hepsini düzenle','Artık sende']
    check(done and all(w in seen for w in want),'telefon: ana öğretici yeni yapıyla dokunarak bitti (%s)'%seen)
    r=p.evaluate("()=>{const S=window.__nb.S;return {tr:S.lv.trampet||0,slots:S.slots.filter(Boolean).length,syn:!!S.unl.syn}}")
    check(r['tr']>0 and r['slots']>=2 and r['syn'],'öğretici sonunda Trampet sahnede, Uyum açık (%s)'%r)
    # --- telefon: dock, alt gezinme, sayfalar
    lk=p.evaluate("()=>{const nb=window.__nb,S=nb.S;nb.unlockAll();S.tipq=[];S.tutm=0;S.muted=true;S.unl.ord=0;S.unl.book=0;S.unl.album=0;S.found={};S.bestWave=1;S.runEarned=0;nb.unlVis();nb.setTab('stage');nb.renderPanels();return [document.getElementById('ordBtn').hidden,document.getElementById('bookBtn').hidden]}");p.wait_for_timeout(300)
    dk=p.evaluate("()=>[...document.querySelectorAll('.dk')].filter(d=>d.offsetParent).map(d=>d.id)")
    check(dk==['d-stage','d-def','d-look','d-set'] and not p.is_visible('#t-set'),'telefon: dock dört düğme, sağ üstte dişli yok (%s)'%dk)
    check(lk==[True,True],'Sipariş/Kitap kilitliyken düğme yok (%s)'%lk)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.unl.ord=1;S.unl.book=1;S.unl.album=1;S.bestWave=30;nb.unlVis()}");p.wait_for_timeout(200)
    check(p.is_visible('#ordBtn') and p.is_visible('#bookBtn'),'açılınca sağ üstte Sipariş ve Kitap düğmeleri')
    p.click('#d-look');p.wait_for_timeout(150);t1=p.evaluate(TAB)
    p.click('#p-studio .subnav [data-tab=look]');p.wait_for_timeout(150);t2=p.evaluate(TAB)
    cur=p.evaluate("()=>document.querySelector('.dk[aria-current]').id")
    check(t1=='studio' and t2=='look' and cur=='d-look','Müzik·Görünüm: önce Müzik, alt gezinmeyle Görünüm, dock aynı (%s/%s)'%(t1,t2))
    p.evaluate("()=>window.__nb.setTab('coll')");p.wait_for_timeout(250)
    check(p.evaluate(TAB)=='stage' and p.is_visible('#cSheet'),'telefonda Koleksiyon başka sekmeden açılınca Sahne’ye geçip sayfayı açıyor')
    p.keyboard.press('Escape');p.wait_for_timeout(100)
    p.evaluate("()=>{document.getElementById('bookBadge').hidden=false;window.__nb.renderPanels()}");p.wait_for_timeout(250)
    check(p.evaluate("()=>document.getElementById('bookBtn').classList.contains('glow')"),'Kitap’ta yeni varken düğme yanıyor')
    p.click('#bookBtn');p.wait_for_timeout(250)
    check(p.is_visible('#bSheet') and not p.evaluate("()=>document.getElementById('bookBtn').classList.contains('glow')") and 'Kalıp kitabı' in p.text_content('#bSheet'),'Kitap sayfası açılıyor, düğme sönüyor')
    p.keyboard.press('Escape');p.wait_for_timeout(100);check(not p.is_visible('#bSheet'),'Escape Kitap sayfasını kapatıyor')
    p.click('#ordBtn');p.wait_for_timeout(250)
    check(p.is_visible('#oSheet') and p.locator('#orderList .ord, #orderList > *').count()>0,'Siparişler sayfası listeyle açılıyor')
    p.click('#oSheet [data-act=sheetClose]');p.wait_for_timeout(100)
    p.click('#d-set');p.wait_for_timeout(120);a=p.evaluate(TAB);p.click('#d-set');p.wait_for_timeout(120);c=p.evaluate(TAB)
    check(a=='set' and c!='set','dock’ta Ayarlar; ikinci dokunuş geri döndürüyor (%s→%s)'%(a,c))
    ctx.close()
    # --- masaüstü
    p=b.new_page(viewport={'width':1366,'height':768});p.on('pageerror',lambda e:er.append(str(e)));p.goto(URL);p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.muted=true;nb.unlVis();nb.renderPanels()}");p.wait_for_timeout(300)
    tb=p.evaluate("()=>[...document.querySelectorAll('.tabs .tab')].filter(b=>b.offsetParent).map(b=>b.dataset.tab)")
    check(tb==['studio','def','look'] and p.inner_text('#t-studio').startswith('Müzik') and p.is_visible('#t-set'),'masaüstü: sekmeler Müzik · Savunma · Görünüm, dişli üstte (%s)'%tb)
    check(p.is_visible('#ordBtn') and p.is_visible('#bookBtn') and p.is_visible('#collBtn'),'masaüstü: Sipariş/Kitap sağ üstte, Koleksiyon şeridin üstünde')
    p.keyboard.press('5');p.wait_for_timeout(200);check(p.is_visible('#bSheet'),'5 Kitap sayfasını açıyor')
    p.keyboard.press('3');p.wait_for_timeout(200);check(p.is_visible('#cSheet') and not p.is_visible('#bSheet'),'3 Koleksiyon sayfasını açıyor (diğeri kapanıyor)')
    check(not er,'sayfa hatası yok %s'%er[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v92 geçti')
sys.exit(1 if fails else 0)
