"""v87 yatay telefon (B2): ped sırası Stüdyo'da sağ panelin altında yapışkan şerit, sahne küçülmez; sekmeler tek satır
    ve yapışkan; dikeye dönünce pedler sahnedeki yerine döner.

    python build.py && python tests/v87_test.py
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
M="""()=>{const pd=document.getElementById('slotBar'),q=pd.querySelector('.sbt'),c=document.getElementById('cv').getBoundingClientRect(),
 tabs=[...document.querySelectorAll('.rack .tabs .tab')].filter(t=>t.offsetParent),ts=document.querySelector('.rack .tabs').getBoundingClientRect(),
 pr=pd.getBoundingClientRect(),rk=document.getElementById('rack').getBoundingClientRect();
 return {par:pd.parentNode.id||pd.parentNode.className,vis:!!pd.offsetParent&&pr.height>0,pad:q&&q.offsetParent?[Math.round(q.getBoundingClientRect().width),Math.round(q.getBoundingClientRect().height)]:null,
  cv:Math.round(Math.min(c.width,c.height)),rows:new Set(tabs.map(t=>Math.round(t.getBoundingClientRect().top))).size,tabsTop:Math.round(ts.top),
  padBottom:Math.round(pr.bottom),rackBottom:Math.round(rk.bottom),tab:document.getElementById('app').dataset.tab}}"""
with sync_playwright() as pw:
    exe='/opt/pw-browsers/chromium'
    b=pw.chromium.launch(executable_path=exe,args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch()
    er=[]
    for (w,h,mincv,minpw) in [(844,390,320,44),(740,360,290,34)]:
        ctx=b.new_context(viewport={'width':w,'height':h},is_mobile=True,has_touch=True);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
        p.goto(URL);p.wait_for_timeout(500)
        p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.muted=true;nb.unlVis();nb.setTab('studio');nb.renderPanels()}");p.wait_for_timeout(400)
        m=p.evaluate(M);tag='%dx%d'%(w,h)
        check(m['par']=='rack' and m['vis'],'%s: 8 yer şeridi sağ panelde görünür (%s)'%(tag,m['par']))
        check(m['pad'] and m['pad'][0]>=minpw-14 and m['pad'][1]>=40,'%s: yer düğmesi dokunulabilir boyda (%s)'%(tag,m['pad']))
        check(m['cv']>=mincv,'%s: sahne küçülmedi (%d px)'%(tag,m['cv']))
        check(abs(m['padBottom']-m['rackBottom'])<=4,'%s: yer şeridi panelin altına yapışık (%d/%d)'%(tag,m['padBottom'],m['rackBottom']))
        check(m['rows']==1,'%s: sekmeler tek satır (%d)'%(tag,m['rows']))
        # pede dokun → vuruş değişir
        v0=p.evaluate("()=>{const S=window.__nb.S;return S.pat[S.edit][0][2]||0}")
        p.evaluate("()=>window.__nb.slotOpen(0)");p.wait_for_timeout(200);p.locator('#pads .pad').nth(2).click();p.wait_for_timeout(250);p.evaluate("()=>window.__nb.slotClose()")
        v1=p.evaluate("()=>{const S=window.__nb.S;return S.pat[S.edit][0][2]||0}")
        check(v0!=v1,'%s: pede dokununca vuruş değişiyor (%s→%s)'%(tag,v0,v1))
        # Savunma'da ped yok
        p.evaluate("()=>window.__nb.setTab('def')");p.wait_for_timeout(300);m=p.evaluate(M)
        check(m['vis'],'%s: Savunma sekmesinde de yer şeridi var (ana ekranın parçası, v90)'%tag)
        # Ayarlar kaydırılınca sekmeler üstte
        p.evaluate("()=>window.__nb.setTab('set')");p.wait_for_timeout(250)
        p.evaluate("()=>{document.getElementById('rack').scrollTop=500}");p.wait_for_timeout(250);m=p.evaluate(M)
        check(m['tabsTop']>=0,'%s: Ayarlar kaydırılınca sekme çubuğu görünür (top %d)'%(tag,m['tabsTop']))
        # dikeye dön → ped sahnedeki yerine
        p.set_viewport_size({'width':390,'height':844});p.wait_for_timeout(500)
        p.evaluate("()=>{window.__nb.setTab('stage');window.__nb.renderPanels()}");p.wait_for_timeout(300);m=p.evaluate(M)
        check(m['par']!='rack','%s → dikey: yer şeridi sahnedeki yerine döndü (%s)'%(tag,m['par']))
        ctx.close()
    check(not er,'sayfa hatası yok %s'%er[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v87 geçti')
sys.exit(1 if fails else 0)
