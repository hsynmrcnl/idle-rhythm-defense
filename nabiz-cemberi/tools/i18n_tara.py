"""EN modunda görünür Türkçe metin tarayıcı: her sekme ve Stüdyo bölümü, Ayarlar, Analiz, kısa öğretici balonu.

    python build.py && python tools/i18n_tara.py      → Türkçe kalan metinler (her biri bir satır, nerede görüldüğüyle)
"""
import os, re, sys, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(R, 'dist')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:%d/' % srv.server_address[1]
TR = re.compile(r"[çğıöşüÇĞİÖŞÜ]|\b(ve|bir|için|ile|yok|var|dalga|yer|enstrüman|aç|kapalı|açık|sahne|dokun|kalkan|hasar|menzil|seviye|vuruş)\b")
NAMES = {"Türkçe", "İstanbul", "Kürdi makam", "Demo song 1 · Gece Vardiyası", "Demo song 2 · Boğaz’da Düet"}
GRAB = """()=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
 while(n=w.nextNode()){const t=n.textContent.trim();if(!t)continue;const e=n.parentElement;if(!e||e.closest('script,style'))continue;
  const r=e.getBoundingClientRect(),cs=getComputedStyle(e);if(!r.width||!r.height||cs.visibility==='hidden'||e.closest('[hidden]'))continue;out.push(t)}
 document.querySelectorAll('[aria-label],[title]').forEach(e=>{if(e.closest('[hidden]'))return;['aria-label','title'].forEach(a=>{const v=e.getAttribute(a);if(v)out.push('['+a+'] '+v)})});return out}"""
seen = {}
with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    for vp, mob in (({'width': 1366, 'height': 900}, False), ({'width': 390, 'height': 844}, True)):
        ctx = b.new_context(viewport=vp, is_mobile=mob, has_touch=mob); p = ctx.new_page()
        p.goto(URL); p.wait_for_timeout(500)
        p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.lang='en';S.ui='kolay';S.nota=1e6;S.bestWave=30;S.up.sef=1;S.up.solo=1;localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}")
        p.reload(); p.wait_for_timeout(600)
        def grab(where):
            for t in p.evaluate(GRAB):
                if TR.search(t) and t not in NAMES: seen.setdefault(t, set()).add(where + (' (telefon)' if mob else ''))
        for ui in ('kolay', 'detay'):
            p.evaluate("u=>{window.__nb.S.ui=u;window.__nb.renderPanels()}", ui); p.wait_for_timeout(150)
            for t in ('stage', 'studio', 'coll', 'def', 'album', 'book', 'look', 'set'):
                p.evaluate("t=>window.__nb.setTab(t)", t); p.wait_for_timeout(150)
                if t == 'studio' and mob:
                    for k in p.evaluate("()=>[...document.querySelectorAll('#secBar .sb')].map(e=>e.dataset.k)"):
                        p.click('#secBar [data-k=%s]' % k); p.wait_for_timeout(80); grab('studio/' + k + '/' + ui)
                grab(t + '/' + ui)
        p.evaluate("()=>window.__nb.setTab('stage')"); p.click('#stats'); p.wait_for_timeout(200); grab('analiz')
        for k in ('def', 'desk', 'blast', 'fam_tel'):
            p.evaluate("k=>{const S=window.__nb.S;S.tipq=[k];S.tutm=0}", k); p.wait_for_timeout(300); grab('mini/' + k)
        p.evaluate("()=>{window.__nb.S.tipq=[]}")
        ctx.close()
    b.close()
srv.shutdown()
for t, w in sorted(seen.items(), key=lambda x: sorted(x[1])[0]):
    print('%-70s  %s' % (t[:70], ', '.join(sorted(w))[:90]))
print(len(seen), 'metin')
