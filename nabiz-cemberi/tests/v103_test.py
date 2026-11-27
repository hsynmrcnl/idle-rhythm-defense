"""v103 arayüz paketi (oyuncu turu 20261127-1719): uyum açıklaması çipin altında, dalga gezinmesi yazılı, güç/sn, kullanılan özelliğin kısa öğreticisi düşer.

    python build.py && python tests/v103_test.py
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
    b=pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    er=[];ctx=b.new_context(viewport={'width':375,'height':667},is_mobile=True,has_touch=True);p=ctx.new_page();p.on('pageerror',lambda e:er.append(str(e)))
    p.goto(URL);p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.lv.trampet=3;S.lv.hihat=2;S.slots=['davul','trampet','hihat',null];S.wave=12;S.bestWave=15;nb.recalc();nb.renderPanels()}");p.wait_for_timeout(300)
    # uyum açıklaması Müzik ekranında, çipin altında
    p.evaluate("()=>window.__nb.setTab('studio')");p.wait_for_timeout(200);p.evaluate("()=>document.querySelector('#secBar [data-k=syn]').click()")
    p.evaluate("()=>{const b=document.querySelector('[data-act=autoAll]');b&&b.click()}");p.wait_for_timeout(400)
    check(p.locator('.syninfo.dim').count()==1,'çip seçilmeden yönlendirme satırı')
    p.locator('#synChips [data-act=synInfo]').first.tap();p.wait_for_timeout(300)
    check(p.locator('#synChips .chip.sel').count()==1 and p.locator('.syninfo:not(.dim)').count()==1,'dokunulan çip seçili, açıklaması altında')
    bg=p.evaluate("()=>getComputedStyle(document.querySelector('#synChips .chip.sel')).backgroundColor")
    check('128' not in bg and bg!='rgb(239, 239, 239)','çip zemini gri değil (%s)'%bg)
    # dalga gezinmesi yazılı, kartı genişletmiyor
    p.evaluate("()=>window.__nb.setTab('def')");p.wait_for_timeout(200);p.tap('#defSub [data-v=dalga]');p.wait_for_timeout(300)
    t=p.text_content('.wnav')
    check('Dalga' in t and '‹ 5' in t and '5 ›' in t,'dalga gezinmesi “Dalga ‹ 5 … 5 ›” (%s)'%t.strip())
    # üstteki güç/sn adı
    check('güç/sn' in p.text_content('[data-sec=siege]'),'Dalga durumu “güç/sn” diyor')
    # sekme değiştiren bayat kısa öğretici: kullanılan özelliğin öğreticisi düşer
    p.evaluate("()=>{const nb=window.__nb;nb.collOpen();nb.collClose()}");p.wait_for_timeout(200)
    st=p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tipq=['coll'];S.tutm=0;nb.miniGapT=0;nb.tutTick();return S.tipq.length}");p.wait_for_timeout(300)
    check(st==0 and not p.is_visible('#tutL'),'Koleksiyon zaten kullanıldıysa kısa öğreticisi gelmiyor')
    check(not er,'sayfa hatası yok '+(er[0] if er else ''))
    b.close()
srv.shutdown()
print('hepsi geçti' if not fails else 'BAŞARISIZ: %d'%len(fails));sys.exit(1 if fails else 0)
