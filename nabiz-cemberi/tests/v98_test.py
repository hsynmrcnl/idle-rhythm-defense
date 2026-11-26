"""v98 sayfa yığını ve odak (game-ui-ux denetimi + oyuncu turu 20261125-1543): sayfa açılınca odak içinde, Escape ile kapanınca
açan düğmede; telefonda sekme değişince sahnedeki sayfalar kapanır; Analiz açılınca sayfalar kapanır; açık sayfanın üstüne yeni kısa
öğretici gelmez; boş yerde 16 adım yok, “Koleksiyon’u aç” düğmesi var; bayat sekme metinleri yok.

    python build.py && python tests/v98_test.py
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
SEED="()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;S.tut.step=99;nb.unlockAll();S.tipq=[];S.tutm=0;S.nota=5e6;S.lv.trampet=1;S.slots=['davul','trampet',null,null];S.unl.ord=1;nb.recalc();nb.renderPanels()}"
IN="sel=>{const a=document.activeElement,c=document.querySelector(sel);return !!(c&&a&&c.contains(a))}"
with sync_playwright() as pw:
    exe='/opt/pw-browsers/chromium'
    b=pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    er=[]
    # masaüstü: klavye
    p=b.new_page(viewport={'width':1366,'height':768});p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500);p.evaluate(SEED);p.wait_for_timeout(300)
    p.focus('#sb8 [data-i="0"]');p.keyboard.press('Enter');p.wait_for_timeout(250)
    check(p.evaluate("()=>window.__nb.iOpen") and p.evaluate(IN,'#iSheet'),'Enter ile açılan enstrüman panelinde odak içeride')
    p.keyboard.press('Escape');p.wait_for_timeout(200)
    check(not p.evaluate("()=>window.__nb.iOpen") and p.evaluate("()=>document.activeElement&&document.activeElement.matches('#sb8 [data-i=\"0\"]')"),'Escape ile kapandı, odak açan yer düğmesine döndü')
    p.focus('#collBtn');p.keyboard.press('Enter');p.wait_for_timeout(250)
    check(p.evaluate(IN,'#cSheet') and p.evaluate("()=>document.activeElement.dataset.act==='lv'"),'Koleksiyon açılınca odak ilk Aç düğmesinde')
    p.keyboard.press('Escape');p.wait_for_timeout(200)
    check(p.evaluate("()=>document.activeElement&&document.activeElement.id==='collBtn'"),'Koleksiyon kapanınca odak Koleksiyon düğmesine döndü')
    p.evaluate("()=>window.__nb.slotOpen(0)");p.wait_for_timeout(150);p.click('#stats');p.wait_for_timeout(250)
    check(not p.evaluate("()=>window.__nb.iOpen") and p.evaluate(IN,'#anl'),'Analiz açılınca panel kapandı, odak Analiz’de')
    p.keyboard.press('Escape');p.wait_for_timeout(150)
    # açık sayfanın üstüne kısa öğretici gelmez
    p.evaluate("()=>{const nb=window.__nb;nb.collOpen();nb.miniGapT=0;nb.S.tipq=['tap'];nb.S.tutm=0}");p.wait_for_timeout(400)
    check(p.is_hidden('#tutL'),'Koleksiyon açıkken yeni kısa öğretici beklemede')
    p.evaluate("()=>window.__nb.collClose()");p.wait_for_timeout(500)
    check(p.is_visible('#tutL'),'Koleksiyon kapanınca kısa öğretici geldi')
    p.evaluate("()=>{const S=window.__nb.S;S.tipq=[];S.tutm=0}");p.wait_for_timeout(200)
    # boş yer
    p.evaluate("()=>window.__nb.slotOpen(2)");p.wait_for_timeout(200)
    e=p.evaluate("()=>({pads:document.querySelectorAll('#pads .pad').length,btn:!!document.querySelector('#iAct [data-act=collOpen]')})")
    check(e['pads']==0 and e['btn'],'boş yerde 16 adım yok, Koleksiyon’u aç düğmesi var (%s)'%e)
    p.click('#iAct [data-act=collOpen]');p.wait_for_timeout(250)
    check(p.is_visible('#cSheet') and not p.evaluate("()=>window.__nb.iOpen"),'Koleksiyon’u aç Koleksiyon sayfasını açtı')
    p.evaluate("()=>window.__nb.collClose()")
    html=p.evaluate("()=>document.documentElement.innerHTML")
    check('Albüm sekmesinden' not in html and 'Koleksiyon sekmesine' not in html,'bayat sekme metinleri yok')
    p.close()
    # telefon: sekme değişince sayfa kapanır
    ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500);p.evaluate(SEED);p.wait_for_timeout(300)
    p.tap('#sb8 [data-i="1"]');p.wait_for_timeout(250)
    check(p.evaluate("()=>window.__nb.iOpen"),'telefonda panel açıldı')
    p.tap('#d-def');p.wait_for_timeout(250);p.tap('#d-stage');p.wait_for_timeout(250)
    check(not p.evaluate("()=>window.__nb.iOpen"),'Savunma’ya gidip dönünce panel kapalı')
    p.tap('#collBtn');p.wait_for_timeout(250);p.tap('#d-set');p.wait_for_timeout(250);p.tap('#d-stage');p.wait_for_timeout(250)
    check(p.is_hidden('#cSheet'),'Ayarlar’a gidip dönünce Koleksiyon kapalı')
    check(not er,'sayfa hatası yok '+'; '.join(er[:2]))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v98 geçti')
sys.exit(1 if fails else 0)

