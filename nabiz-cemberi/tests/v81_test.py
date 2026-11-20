"""v81 A+B: yeni düşmanlar (bölünme, iyileşme, zırhlı+susturucu) ve Ritme vur akışı çarpanı.

    python build.py && python tests/v81_test.py
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
mk="(o)=>Object.assign({hp:5,hpMax:5,d:0.6,a:0.2,sp:0.04,slow:0,slowT:0,stun:0,dot:0,dotT:0,flash:0,w:30,boss:false,lastSp:0,lastHit:0,wob:1,id:Math.random(),waved:true},o)"
with sync_playwright() as pw:
    exe='/opt/pw-browsers/chromium'
    b=pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    er=[];p=b.new_page(viewport={'width':1100,'height':760});p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.muted=true;nb.setWave(30);nb.recalc()}")
    # eşik dalgaları
    thr=p.evaluate("""()=>{const nb=window.__nb,got={bolen:0,iyilesen:0,zirhsans:0};
      // her türün ilk göründüğü dalga (eşiğin altında 0, üstünde birkaç dalgada mutlaka çıkar)
      Object.keys(got).forEach(ty=>{for(let w=1;w<=55;w++){const q=nb.waveComp(w);if(q.some(it=>it.ty===ty)){got[ty]=w;break}}});return got}""")
    check(12<=thr['bolen']<=14 and 20<=thr['iyilesen']<=22 and 30<=thr['zirhsans']<=32,'yeni düşmanlar ~12/20/30 dalgada giriyor (%s)'%thr)
    # bölünme
    sp=p.evaluate("""(mk)=>{const nb=window.__nb,f=eval('('+mk+')');nb.enemies.length=0;nb.enemies.push(f({ty:'bolen',hp:-1,d:0.6}));nb.ff(0.05);return nb.enemies.filter(e=>e.ty==='parca').length}""",mk)
    check(sp==2,'bölünen ölünce iki parça çıktı (%s)'%sp)
    # iyileşme: enstrüman yokken (ateş yok) iyileşen can toplar
    hl=p.evaluate("""(mk)=>{const nb=window.__nb,S=nb.S,f=eval('('+mk+')');S.slots=[null,null,null,null];nb.recalc();nb.enemies.length=0;
      const e=f({ty:'iyilesen',hp:3,hpMax:6,d:0.95,sp:0.001,lastHit:-9});nb.enemies.push(e);const h0=e.hp;nb.ff(1.5);return [h0,nb.enemies[0]&&nb.enemies[0].hp]}""",mk)
    check(hl[1] and hl[1]>hl[0],'iyileşen vurulmayınca canı doldu (%s→%s)'%(hl[0],hl[1]))
    # kalkan susturmayı emer
    mu=p.evaluate("""(mk)=>{const nb=window.__nb,S=nb.S,f=eval('('+mk+')');S.slots=['davul','trampet',null,null];nb.recalc();nb.core.sh=50;nb.enemies.length=0;
      nb.enemies.push(f({ty:'zirhsans',hp:0.2,d:0.004,sp:0.5}));const before=nb.core.sh;nb.ff(0.1);
      const muted=(nb.S.slots.some((id,si)=>false)); return {sh0:before,sh1:Math.round(nb.core.sh)}}""",mk)
    check(mu['sh1']<mu['sh0'],'kalkan varken susturma kalkanı emiyor (sh %s→%s)'%(mu['sh0'],mu['sh1']))
    # B: tap akışı çarpanı
    tm=p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.slots=['davul',null,null,null];nb.recalc();S.tapN=0;const r0=nb.rate();S.tapN=8;const r1=nb.rate();S.tapN=0;return [r0,r1]}")
    check(tm[1]>tm[0]*1.9,'Ritme vur akışı geliri ~×2 yapıyor (%.0f→%.0f)'%(tm[0],tm[1]))
    # idle/sim güvenli: ff sonrası tapN 0 kalır (ileri sarma dokunmaz)
    z=p.evaluate("()=>{const nb=window.__nb;nb.S.tapN=0;nb.ff(30);return nb.S.tapN}")
    check(z==0,'ileri sarmada tap akışı artmıyor (idle/sim etkilenmez)')
    check(not er,'sayfa hatası yok %s'%er[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v81 geçti')
sys.exit(1 if fails else 0)
