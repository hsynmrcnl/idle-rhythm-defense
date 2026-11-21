"""v84: yeni düşman tanıtımı EŞİKTE (ilk spawn beklenmez) ve ileri sarmada biriktirilip sonunda gösterilir;
    Asistan kriz anında Tamir'i öncelikli alır.

    python build.py && python tests/v84_test.py
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
    er=[];p=b.new_page(viewport={'width':1100,'height':760});p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500)
    # güçlü oyuncu: ileri sarmada geri çekilmeden ilerlesin (zayıf/susturuk oyuncu dalga düşürür, eşik geçilmez)
    p.evaluate("""()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.muted=true;S.bestWave=60;
      S.slots.forEach(id=>{if(id)S.lv[id]=40});S.def={nabiz:400,tamir:80,hasar:300,menzil:8};nb.recalc()}""")
    cv=p.locator('#cv').bounding_box();p.mouse.click(cv['x']+cv['width']/2,cv['y']+cv['height']/2);p.wait_for_timeout(400)
    # 1) EŞİKTE: Bölünen eşiği d12 — tam d12'de tanıtılıyor (eski d15 değil)
    m=p.evaluate("()=>new Promise(res=>{const nb=window.__nb;nb.S.enemyTold={};document.getElementById('msg').textContent='';nb.setWave(12);setTimeout(()=>res(document.getElementById('msg').textContent),900)})")
    check('Bölünen' in m,'Bölünen eşiği d12’de tanıtılıyor (“%s”)'%m[:40])
    # 2) d11'de (eşik altı) tanıtım yok
    m0=p.evaluate("()=>new Promise(res=>{const nb=window.__nb;nb.S.enemyTold={};document.getElementById('msg').textContent='';nb.setWave(11);setTimeout(()=>res(document.getElementById('msg').textContent),900)})")
    check('Bölünen' not in m0,'eşik altında (d11) tanıtım yok')
    # 3) İLERİ SARMADA: biriktirilip sonunda gösterilir (idle oyuncu hiç görmüyordu)
    mff=p.evaluate("""()=>{const nb=window.__nb,S=nb.S;S.enemyTold={bolen:1,zirhsans:1};nb.setWave(18);document.getElementById('msg').textContent='';nb.ff(300);return {msg:document.getElementById('msg').textContent,w:S.wave}}""")
    check(mff['w']>=20 and ('İyileşen' in mff['msg'] or 'Yokken' in mff['msg']),'ileri sarmada yeni düşman sonunda gösteriliyor (d%d, “%s”)'%(mff['w'],mff['msg'][:40]))
    # 4) çoklu eşik ileri sarmada birleşik mesaj (10 → 30+ birden çok eşik geçilir)
    mc=p.evaluate("""()=>{const nb=window.__nb,S=nb.S;S.enemyTold={};nb.setWave(11);document.getElementById('msg').textContent='';nb.ff(500);return {msg:document.getElementById('msg').textContent,w:S.wave}}""")
    check('Yokken' in mc['msg'] or 'İyileşen' in mc['msg'] or 'Zırhlı' in mc['msg'] or 'Bölünen' in mc['msg'],'çoklu eşik ileri sarmada haber veriliyor (d%d, “%s”)'%(mc['w'],mc['msg'][:50]))
    # 5) Asistan kriz anında Tamir'i öncelikli alır (nabız <%35)
    tamir=p.evaluate("""()=>{const nb=window.__nb,S=nb.S;S.unl.def=1;S.nota=5e7;S.def={};nb.recalc();nb.setHp(0.1);const k=nb.asstPick(1e7);return k?k.id:null}""")
    check(tamir=='tamir','kriz anında Asistan Tamir’i seçiyor (%s)'%tamir)
    check(not er,'sayfa hatası yok %s'%er[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v84 geçti')
sys.exit(1 if fails else 0)
