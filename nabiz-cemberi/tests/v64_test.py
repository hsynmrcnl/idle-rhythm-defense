"""v64: sahne doluyken Aç düğmesi sahne yeri de ekler; öneri/Asistan adayı yer+enstrüman; 10 yer doluysa yedeğe yazar.

    python build.py && python tests/v64_test.py
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
    p = b.new_page(viewport={'width': 1366, 'height': 768})
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(500)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.tutm=0;S.nota=1e9;S.slots=S.slots.map((v,i)=>v||['davul','bas','zil','el'].find(id=>!S.slots.includes(id))||v);"
               "S.slots.forEach(id=>{if(id&&!S.lv[id])S.lv[id]=1});nb.recalc();nb.setTab('coll');nb.renderPanels()}")
    st = p.evaluate("()=>({full:!window.__nb.S.slots.includes(null),n:window.__nb.S.slots.length})")
    check(st['full'], 'sahne dolu (%d yer)' % st['n'])
    btn = p.locator('#collList button[data-slot="1"]').first
    check(btn.count() == 1 and 'sahne yeri' in btn.inner_text(), 'Aç düğmesi yer de ekliyor: “%s”' % (btn.inner_text() if btn.count() else '-'))
    r = p.evaluate("()=>{const nb=window.__nb,S=nb.S,b=document.querySelector('#collList button[data-slot=\"1\"]'),id=b.dataset.id,c=+b.dataset.cost,n0=S.nota,l0=S.slots.length;b.click();return {id,c,sp:n0-S.nota,l:S.slots.length-l0,on:S.slots.includes(id),m:document.getElementById('msg').textContent,lv:JSON.stringify(S.lv)}}")
    check(r['l'] == 1 and r['on'] and r['c'] <= r['sp'] <= r['c'] + 100, 'tek ödemeyle yer açıldı ve %s sahneye girdi (♪%d)' % (r['id'], r['sp']))
    k = p.evaluate("()=>{const nb=window.__nb,S=nb.S;const k=nb.asstPick(1e12);return k&&k.slot?k:null}")
    check(k is not None and 'sahne yeri' in k['n'], 'sahne doluyken yeni enstrüman adayı yer de ekliyor (%s)' % (k and k['n']))
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;while(S.slots.length<10)S.slots.push('davul');nb.renderPanels()}")
    t = p.locator('#collList .irow.locked button').first.inner_text()
    check('yedeğe' in t and p.locator('#collList button[data-slot="1"]').count() == 0, '10 yer doluyken düğme yedeğe yazıyor: “%s”' % t)
    check(p.evaluate("()=>{const k=window.__nb.asstPick(1e12);return !(k&&k.act==='lv'&&k.id&&!window.__nb.S.lv[k.id])}"), '10 yer doluyken Asistan yeni enstrüman almıyor')
    check(not errs, 'sayfa hatası yok %s' % errs[:2])
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'v64 geçti')
sys.exit(1 if fails else 0)
