"""v91 Savunma·Albüm: alt sekmeler (Dalga · Geliştirme · Albüm), eski album sekmesi Savunma › Albüm'e yönlenir,
    plak düğmesi Kitap; enstrüman istatistikleri (yer başına hasar/sn, pay, öldürme, ♪/sn; Alan dahil).

    python build.py && python tests/v91_test.py
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
VIS="()=>{const v=id=>{const e=document.getElementById(id);return !!(e&&e.offsetParent)};return {siege:v('defStatus'),istat:v('istat'),ord:v('orderList'),dup:v('defList'),alb:v('albumBox'),mn:v('mnBox'),tour:v('tourBox')}}"
with sync_playwright() as pw:
    exe='/opt/pw-browsers/chromium'
    b=pw.chromium.launch(executable_path=exe,args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch()
    er=[]
    for nm,vp,mob in [('telefon',(390,844),True),('masaüstü',(1366,768),False)]:
        ctx=b.new_context(viewport={'width':vp[0],'height':vp[1]},is_mobile=mob,has_touch=mob);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
        p.goto(URL);p.wait_for_timeout(500)
        p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.muted=true;S.slots=['davul','trampet','hihat','zil'];Object.assign(S.lv,{davul:12,trampet:6,hihat:4,zil:3});S.pat.A[1]=S.pat.A[1].map((v,i)=>i%8===4?1:0);S.pat.A[2]=S.pat.A[2].map((v,i)=>i%2?1:0);S.pat.A[3]=S.pat.A[3].map((v,i)=>i%4===0?1:0);S.bestWave=20;nb.recalc();nb.unlVis();nb.setTab('def');nb.renderPanels()}");p.wait_for_timeout(300)
        bs=p.evaluate("()=>[...document.querySelectorAll('#defSub [data-act=dsub]')].filter(b=>b.offsetParent).map(b=>b.textContent)")
        check(bs==['Dalga','Geliştirme','Albüm'],'%s: Savunma alt sekmeleri görünür (%s)'%(nm,bs))
        v=p.evaluate(VIS);check(v['siege'] and v['istat'] and not v['ord'] and not v['dup'] and not v['alb'],'%s: Dalga — durum ve enstrümanlar (%s)'%(nm,v))
        p.click('#defSub [data-v=gel]');p.wait_for_timeout(150);v=p.evaluate(VIS)
        check(v['dup'] and v['ord'] and not v['siege'] and not v['alb'],'%s: Geliştirme — geliştirmeler ve siparişler (siparişler 3. adımda sağ üst düğmeye)'%nm)
        p.click('#defSub [data-v=alb]');p.wait_for_timeout(150);v=p.evaluate(VIS)
        check(v['alb'] and v['mn'] and v['tour'] and not v['dup'] and not v['siege'],'%s: Albüm — albüm, menajer, turne'%nm)
        p.evaluate("()=>{window.__nb.setTab('studio');window.__nb.setTab('album')}");p.wait_for_timeout(150)
        t=p.evaluate("()=>({tab:document.getElementById('app').dataset.tab,sub:document.getElementById('p-def').dataset.sub})")
        check(t=={'tab':'def','sub':'alb'},'%s: eski album sekmesi Savunma › Albüm’e yönleniyor (%s)'%(nm,t))
        if mob:
            d=p.evaluate("()=>{const d=document.getElementById('d-album');return d.getAttribute('aria-label')}")
            p.click('#d-album');p.wait_for_timeout(150)
            check(d=='Kitap' and p.evaluate("()=>document.getElementById('app').dataset.tab")=='book','telefon: plak düğmesi Kitap’ı açıyor (%s)'%d)
        else:
            check(not p.evaluate("()=>!!document.getElementById('t-album').offsetParent"),'masaüstü: ayrı Albüm sekmesi yok')
        # istatistik: çal, ileri sar, tablo dolu; Alan (Zil) hasarı da sayılıyor
        cv=p.locator('#cv').bounding_box();p.evaluate("()=>window.__nb.setTab('def')")
        p.evaluate("()=>{const nb=window.__nb;nb.setWave(14)}")
        if not p.evaluate("()=>window.__nb.playing"):
            p.evaluate("()=>window.__nb.setTab(window.innerWidth<701?'stage':'studio')");p.wait_for_timeout(200)
            cv=p.locator('#cv').bounding_box();p.mouse.click(cv['x']+cv['width']/2,cv['y']+cv['height']/2);p.wait_for_timeout(200)
        p.evaluate("()=>{const nb=window.__nb;nb.setWave(14);nb.ff(20);nb.setTab('def')}");p.wait_for_timeout(200)
        p.click('#defSub [data-v=dalga]');p.wait_for_timeout(700)
        rows=p.evaluate("()=>[...document.querySelectorAll('#istat tbody tr')].map(r=>[...r.cells].map(c=>c.textContent.trim()))")
        names=[r[0] for r in rows]
        zil=[r for r in rows if r[0]=='Zil']
        pays=sum(int(r[2].replace('%','')) for r in rows)
        check(names==['Davul','Trampet','Hi-hat','Zil'],'%s: tabloda her sahne yeri (%s)'%(nm,names))
        check(zil and zil[0][1] not in ('0',''),'%s: Alan (Zil) hasarı sayılıyor (%s)'%(nm,zil))
        check(95<=pays<=105 and all(r[4] not in ('0','') for r in rows),'%s: paylar ~%%100 (%d), her yer nota kazandırıyor'%(nm,pays))
        ctx.close()
    # albüm kilitliyken Albüm alt sekmesi gizli
    p=b.new_page(viewport={'width':1366,'height':768});p.on('pageerror',lambda e:er.append(str(e)));p.goto(URL);p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.unl.album=0;S.bestWave=10;S.runEarned=0;S.tipq=[];nb.unlVis();nb.setTab('def');nb.renderPanels()}");p.wait_for_timeout(200)
    check(not p.evaluate("()=>!!document.getElementById('dsubAlb').offsetParent"),'albüm kilitliyken Albüm alt sekmesi yok')
    check(not er,'sayfa hatası yok %s'%er[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v91 geçti')
sys.exit(1 if fails else 0)
