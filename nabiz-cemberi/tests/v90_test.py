"""v90 ana ekran: 8 sahne yeri şeridi (MAXSLOTS 8), enstrüman paneli (pedler, ‹ › kapalılar dahil, Yükselt, değiştir),
    kapalı yerde fiyat panelde ve nota yetince yanıp sönme, Koleksiyon sayfası (yalnız Aç); telefon, masaüstü, yatay.

    python build.py && python tests/v90_test.py
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
SETUP="""(n)=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.muted=true;S.nota=n;S.slots=['davul','trampet','hihat',null];S.lv.trampet=3;S.lv.hihat=2;nb.recalc();nb.unlVis();nb.setTab('stage');nb.renderPanels()}"""
with sync_playwright() as pw:
    exe='/opt/pw-browsers/chromium'
    b=pw.chromium.launch(executable_path=exe,args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch()
    er=[]
    for nm,vp,mob in [('telefon',(390,844),True),('masaüstü',(1366,768),False),('yatay',(844,390),True)]:
        ctx=b.new_context(viewport={'width':vp[0],'height':vp[1]},is_mobile=mob,has_touch=mob);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
        p.goto(URL);p.wait_for_timeout(500);p.evaluate(SETUP,30000);p.wait_for_timeout(400)
        g=p.evaluate("()=>{const bs=[...document.querySelectorAll('#sb8 .sbt')];return {n:bs.length,lock:bs.filter(b=>b.classList.contains('lock')).length,empty:bs.filter(b=>b.classList.contains('empty')).length,vis:bs.every(b=>b.offsetParent&&b.getBoundingClientRect().width>20),can:!!document.querySelector('#sb8 .sbt.can'),price:document.getElementById('sb8').textContent.includes('♪'),par:document.getElementById('slotBar').parentNode.id||document.getElementById('slotBar').parentNode.className}}")
        check(g['n']==8 and g['lock']==4 and g['empty']==1 and g['vis'],'%s: 8 yer düğmesi (4 kapalı, 1 boş), hepsi görünür (%s)'%(nm,g))
        check(g['can'] and not g['price'],'%s: nota yetince sıradaki kapalı yer yanıp sönüyor, şeritte fiyat yok'%nm)
        if nm=='yatay': check(g['par']=='rack','yatay: şerit sağ panelin altında (%s)'%g['par'])
        p.click('#sb8 [data-i="1"]');p.wait_for_timeout(300)
        s=p.evaluate("()=>{const sh=document.getElementById('iSheet'),r=sh.getBoundingClientRect();return {vis:!sh.hidden&&r.height>50,pads:document.querySelectorAll('#pads .pad').length,up:(document.querySelector('#iAct [data-lvq]')||{}).textContent||'',sel:!!document.querySelector('#iAct select[data-slot=\"1\"]'),x:r.x}}")
        check(s['vis'] and s['pads']==16 and s['up'].startswith('Yükselt +') and s['sel'],'%s: dolu yer paneli — 16 adım, Yükselt, enstrüman değiştir (%s)'%(nm,{k:s[k] for k in ('pads','up','sel')}))
        if nm=='yatay': check(s['x']>=844*0.45,'yatay: panel sağ kolonda (x %d)'%s['x'])
        v0=p.evaluate("()=>window.__nb.S.pat.A[1][3]");p.click('#pads [data-act=pad][data-s="3"]');p.wait_for_timeout(200)
        check(p.evaluate("()=>window.__nb.S.pat.A[1][3]")!=v0,'%s: paneldeki ped vuruş koyuyor'%nm)
        for _ in range(3): p.click('#iSheet [data-act=sbNext]');p.wait_for_timeout(100)
        lk=p.inner_text('#iLock')
        check('kapalı' in lk and 'Aç' in lk and '2.000' in lk and p.evaluate("()=>document.getElementById('pads').hidden"),'%s: ‹ › kapalı yere geçiyor, fiyat panelde (“%s”)'%(nm,lk[:40].replace('\n',' ')))
        p.click('#iLock [data-act=addslot]');p.wait_for_timeout(300)
        a=p.evaluate("()=>({n:window.__nb.S.slots.length,sel:!!document.querySelector('#iAct select[data-slot=\"4\"]')})")
        check(a['n']==5 and a['sel'],'%s: Aç yeri açıyor, panel boş yerde kalıyor (%s)'%(nm,a))
        p.keyboard.press('Escape');p.wait_for_timeout(150)
        check(p.evaluate("()=>document.getElementById('iSheet').hidden"),'%s: Escape paneli kapatıyor'%nm)
        p.click('#collBtn');p.wait_for_timeout(300)
        c=p.evaluate("()=>({fh:document.getElementById('famBar').offsetHeight,rows:document.querySelectorAll('#cSheet .irow').length,txt:document.getElementById('cSheet').textContent})")
        check(c['fh']>30 and c['rows']>3 and 'Sahnede' not in c['txt'] and 'Yedekte' not in c['txt'] and 'Sahneye koy' not in c['txt'],'%s: Koleksiyon sayfası aile simgeleriyle, yalnız Aç (%s)'%(nm,{k:c[k] for k in ('fh','rows')}))
        h1=p.evaluate("()=>document.getElementById('cSheet').offsetHeight");p.click('#famBar [data-f="tel"]');p.wait_for_timeout(250);h2=p.evaluate("()=>document.getElementById('cSheet').offsetHeight")
        check(abs(h1-h2)<2 and 'Tel' in p.inner_text('#cHead'),'%s: aile değişince sayfa boyu sabit, başlık güncel (%d/%d)'%(nm,h1,h2))
        p.click('#cSheet [data-act=collClose]');p.wait_for_timeout(200)
        check(p.evaluate("()=>document.getElementById('famBar').closest('#p-coll')!=null"),'%s: kapanınca aile çubuğu Koleksiyon sekmesine dönüyor'%nm)
        ctx.close()
    check(not er,'sayfa hatası yok %s'%er[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v90 geçti')
sys.exit(1 if fails else 0)
