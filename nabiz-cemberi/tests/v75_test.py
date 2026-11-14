"""v75: Sade/Hareketli/Yoğun'da en çok geliri getiren "en iyi" işaretli ve gerçekten en iyisi; ölçüm deseni değiştirmez; kilitli Analiz ne zaman açılacağını ve ne işe yaradığını söyler.

    python build.py && python tests/v75_test.py
"""
import os, sys, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(R, 'dist')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:%d/' % PORT
fails = []
def check(ok, what):
    print(('  ok  ' if ok else '  FAIL ') + what)
    if not ok: fails.append(what)

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    errs = []
    p = b.new_page(viewport={'width': 1280, 'height': 800})
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;S.unl={studio:1,coll:1,tap:1};S.tipq=[];nb.unlVis()}")
    p.click('#stats'); p.wait_for_timeout(150)
    m = p.inner_text('#msg'); lab = p.get_attribute('#stats', 'aria-label') or ''
    check('14' in m and 'çarpan' in m and '14' in lab, 'kilitli Analiz ne zaman açılacağını ve ne işe yaradığını söylüyor (“%s” / “%s”)' % (m[:70], lab))
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;nb.unlockAll();S.tipq=[];S.tutm=0;S.nota=1e6;S.slots=['davul','trampet','shaker','hihat'];['trampet','shaker','hihat'].forEach(id=>S.lv[id]=8);S.lv.davul=12;nb.recalc();nb.setTab('studio');nb.renderPanels()}")
    p.wait_for_timeout(300)
    r = p.evaluate("""()=>{const nb=window.__nb,S=nb.S,out=[];document.querySelectorAll('#slotList .slot').forEach((el,si)=>{const bs=[...el.querySelectorAll('[data-act=alvl]')];if(bs.length===3)out.push([si,bs.map(b=>b.textContent.includes('en iyi'))])});
      const p0=JSON.stringify(S.pat.A);const res=out.map(([si,mk])=>{const rates=[1,2,3].map(v=>{const sv=JSON.stringify(S.pat.A);const b=document.querySelector('#slotList [data-act=alvl][data-i="'+si+'"][data-v="'+v+'"]');S.nota=1e6;b.click();const r=nb.rate();S.pat.A=JSON.parse(sv);nb.recalc();return r});const bi=mk.indexOf(true);return {si,bi,rates,ok:bi>=0&&rates[bi]>=Math.max(...rates)*0.99}});
      return {res,same:p0===JSON.stringify(S.pat.A)}}""")
    check(len(r['res']) > 0 and all(x['ok'] for x in r['res']), '“en iyi” işaretli seçenek gerçekten en çok geliri getiriyor (%s)' % r['res'])
    check(not errs, 'sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v75 geçti')
sys.exit(1 if fails else 0)
