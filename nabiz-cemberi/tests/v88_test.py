"""v88: düşman haberi öncelikli (ezilmez); yatay öğretici pedi hedefler; bayat kısa öğretici düşer; Maks tek seferlik;
    EN sayı biçimi; kısa öğretici açıkken rakam kısayolları.

    python build.py && python tests/v88_test.py
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
SETUP="()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.muted=true;nb.miniGapT=0;nb.unlVis();nb.renderPanels()}"
with sync_playwright() as pw:
    exe='/opt/pw-browsers/chromium'
    b=pw.chromium.launch(executable_path=exe,args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch()
    er=[]
    # --- masaüstü
    p=b.new_page(viewport={'width':1366,'height':768});p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500);p.evaluate(SETUP)
    p.evaluate("""()=>{const nb=window.__nb,S=nb.S;S.bestWave=60;S.slots.forEach(id=>{if(id)S.lv[id]=40});S.def={nabiz:400,tamir:80,hasar:300,menzil:8};nb.recalc()}""")
    cv=p.locator('#cv').bounding_box();p.mouse.click(cv['x']+cv['width']/2,cv['y']+cv['height']/2);p.wait_for_timeout(400)
    # 1) ileri sarma sonrası düşman haberi, ardından gelen sıradan mesajla ezilmez
    m=p.evaluate("""()=>{const nb=window.__nb,S=nb.S;S.enemyTold={bolen:1,zirhsans:1};nb.setWave(18);document.getElementById('msg').textContent='';nb.ff(300);nb.retreatNow();return document.getElementById('msg').textContent}""")
    check('İyileşen' in m,'ileri sarma sonrası düşman haberi sıradan mesajla ezilmiyor (“%s”)'%m[:40])
    # 2) bayat kısa öğretici düşer
    r=p.evaluate("""()=>{const nb=window.__nb,S=nb.S,o=[];S.tipq=['def'];S.tutm=0;S.tipw={def:5};S.bestWave=12;o.push(!nb.ovCur()&&!S.tipq.length);
      S.tipq=['fam_tel'];S.famOpen.tel=1;o.push(!nb.ovCur()&&!S.tipq.length);
      S.tipq=['look'];S.tipw={look:12};S.tabSeen={look:12};o.push(!nb.ovCur()&&!S.tipq.length);
      S.tipq=['album'];S.tipw={album:1};S.bestWave=30;const c=nb.ovCur();o.push(!!c&&c.k==='album');
      S.tipq=['def'];S.tipw={def:30};S.tabSeen={};const d=nb.ovCur();o.push(!!d&&d.k==='def');return o}""")
    check(r[0],'4+ dalga bekleyen kısa öğretici düşüyor')
    check(r[1],'aile zaten açıksa aile kısa öğreticisi düşüyor')
    check(r[2],'oyuncu sekmeye kendisi girdiyse kısa öğretici düşüyor')
    check(r[3],'Albüm kısa öğreticisi bayatlasa da kalıyor')
    check(r[4],'taze kısa öğretici gösteriliyor')
    # 2b) Asistan kriz dışında da ucuz hayatta kalma alır (nota yığılmasın)
    k=p.evaluate("""()=>{const nb=window.__nb,S=nb.S;S.tipq=[];S.unl.def=1;S.def={};S.nota=1e7;nb.recalc();nb.setHp(1);let k=null;for(let i=0;i<8;i++){k=nb.asstPick(S.nota*0.25);if(!k||k.act==='def')break;nb.hintApplyK(k)}return k?{a:k.act,id:k.id}:null}""")
    check(k and k['a']=='def' and k['id'] in ('nabiz','tamir','menzil','kalkan'),'Asistan nabız tamken ucuz hayatta kalma alıyor (%s)'%k)
    # 3) kısa öğretici açıkken rakam kısayolu çalışır ve balonu kapatır
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tipq=['def'];S.tutm=0;S.tipw={def:S.bestWave};S.tabSeen={};nb.miniGapT=0;nb.setTab('studio')}");p.wait_for_timeout(600)
    shown=p.evaluate("()=>!document.getElementById('tutL').hidden")
    p.keyboard.press('4');p.wait_for_timeout(400)
    s=p.evaluate("()=>({tab:document.getElementById('app').dataset.tab,q:window.__nb.S.tipq.length})")
    check(shown and s['tab']=='def' and s['q']==0,'kısa öğretici açıkken 4 → Savunma, balon kapandı (%s, gösterildi %s)'%(s,shown))
    # 4) Maks tek seferlik
    p.evaluate("()=>{const S=window.__nb.S;S.tipq=[];S.nota=1e9;S.buy=0;window.__nb.setTab('studio');window.__nb.renderPanels()}");p.wait_for_timeout(300)
    p.locator('#slotList [data-act=lv]').first.click();p.wait_for_timeout(300)
    bm=p.evaluate("()=>({buy:window.__nb.S.buy,pr:document.querySelector('#buyMode [data-v=\"1\"]').getAttribute('aria-pressed')})")
    check(bm['buy']==1 and bm['pr']=='true','Maks bir alımdan sonra ×1’e dönüyor (%s)'%bm)
    # 5) EN sayı biçimi + Unlock
    en=p.evaluate("""()=>new Promise(r=>{const nb=window.__nb,S=nb.S;S.lang='en';S.nota=1534567;nb.renderPanels();nb.setTab('coll');setTimeout(()=>{const a=[...document.querySelectorAll('#collList [data-act=lv]')].map(x=>x.getAttribute('aria-label')||'').filter(x=>x)[0]||'';r({n:document.getElementById('sNota').textContent,a})},500)})""")
    check('1.53 M' in en['n'] and 'Mn' not in en['n'],'EN: nota İngilizce biçimde (“%s”)'%en['n'])
    check(en['a']=='' or en['a'].startswith('Unlock'),'EN: Koleksiyon Aç düğmesi “Unlock” (“%s”)'%en['a'][:30])
    p.close()
    # --- yatay öğretici pedi hedefler
    ctx=b.new_context(viewport={'width':844,'height':390},is_mobile=True,has_touch=True);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(700)
    p.locator('#tutBub .btn').last.click();p.wait_for_timeout(500)
    s0=p.evaluate("()=>window.__nb.tutStep")
    pad=p.locator('#pads [data-act=pad][data-s="0"]')
    vis=pad.count()>0 and pad.is_visible()
    if vis: pad.tap();p.wait_for_timeout(500)
    s1=p.evaluate("()=>({s:window.__nb.tutStep,v:window.__nb.S.pat.A[0][0]})")
    check(vis and s1['v']>0 and s1['s']>s0,'yatay öğretici: pede dokunmak ilk vuruşu koyuyor ve ilerletiyor (%s→%s, ped %s)'%(s0,s1,vis))
    ctx.close()
    check(not er,'sayfa hatası yok %s'%er[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v88 geçti')
sys.exit(1 if fails else 0)
