"""Arayüz denetimi (game-ui-ux yeteneğinin kontrolleri): her ekran/sayfa açılınca odak içinde mi, kapanınca açana dönüyor mu,
ekran boyu taraması (taşma, kırpılma, örtüşme), yazı boyu dağılımı, kontrast (oyun bilgisi taşıyan yazı ≥4,5:1).

    python build.py && python tools/arayuz_olc.py      # çekimler build/arayuz/
"""
import os, sys, threading, functools, http.server, socketserver, json
from playwright.sync_api import sync_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DIST = os.path.join(R, 'dist'); OUT = os.path.join(R, 'build', 'arayuz'); os.makedirs(OUT, exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:%d/' % srv.server_address[1]
SEED = """()=>{const nb=window.__nb,S=nb.S;S.tut.done=true;S.tut.step=99;nb.unlockAll();S.tipq=[];S.tutm=0;S.nota=5e6;S.lv.trampet=1;S.lv.hihat=1;S.slots=['davul','trampet','hihat',null,null];S.unl.ord=1;nb.recalc();nb.renderPanels()}"""
# açılan ekranlar: [ad, açma (JS), kap (seçici), kapatma]
SCREENS = [
 ('Enstrüman paneli', "()=>window.__nb.slotOpen(0)", '#iSheet', 'Escape'),
 ('Boş yer paneli', "()=>window.__nb.slotOpen(3)", '#iSheet', 'Escape'),
 ('Koleksiyon', "()=>window.__nb.collOpen()", '#cSheet', 'Escape'),
 ('Siparişler', "()=>document.getElementById('ordBtn').click()", '#oSheet', 'Escape'),
 ('Kitap', "()=>{window.__nb.S.unl.book=1;window.__nb.unlVis();document.getElementById('bookBtn').click()}", '#bSheet', 'Escape'),
 ('Analiz', "()=>document.getElementById('stats').click()", '#anl', 'Escape'),
]
FOCUS = """sel=>{const a=document.activeElement,c=document.querySelector(sel);return {inside:!!(c&&a&&c.contains(a)),act:a?(a.id||a.tagName+'.'+(a.className||'')).slice(0,40):null}}"""
TABS = ['studio', 'def', 'look', 'shop', 'set']
SIZES = [('telefon', 390, 844, True), ('kucuk-telefon', 360, 640, True), ('yatay', 844, 390, True), ('laptop', 1280, 720, False), ('masaustu', 1366, 768, False), ('ultrawide', 2560, 1080, False)]
CHECK = """()=>{const W=innerWidth,H=innerHeight,o=[],sz={},lum=c=>{const m=c.match(/[\\d.]+/g);if(!m)return null;const [r,g,b]=m.slice(0,3).map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*r+.7152*g+.0722*b},
 bgOf=e=>{for(;e;e=e.parentElement){const c=getComputedStyle(e).backgroundColor;const m=c.match(/[\\d.]+/g);if(m&&(m.length<4||+m[3]>0.5))return c}return getComputedStyle(document.body).backgroundColor};
 let low=[];document.querySelectorAll('body *').forEach(e=>{if(!e.offsetParent&&getComputedStyle(e).position!=='fixed')return;const r=e.getBoundingClientRect();if(!r.width||!r.height)return;
  if(r.right>W+1&&getComputedStyle(e).overflow==='visible'&&!e.closest('[class*=tabs],#secBar,.stats'))o.push((e.id||e.className||e.tagName)+'').toString();
  const tx=[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());if(!tx)return;const cs=getComputedStyle(e);if(cs.visibility==='hidden'||+cs.opacity<0.3)return;
  const f=Math.round(parseFloat(cs.fontSize));sz[f]=(sz[f]||0)+1;const L1=lum(cs.color),L2=lum(bgOf(e));if(L1==null||L2==null)return;const cr=(Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);
  if(cr<4.5&&!e.closest('[disabled],.poor,.locked,.lock'))low.push([Math.round(cr*10)/10,f,(e.textContent||'').trim().slice(0,28),(e.id||e.className||e.tagName)+''])});
 const n=Object.values(sz).reduce((a,b)=>a+b,0),sm=Object.entries(sz).filter(([k])=>+k<12).reduce((a,[k,v])=>a+v,0);
 return {over:[...new Set(o)].slice(0,8),small:n?Math.round(sm/n*100):0,sizes:sz,low:low.sort((a,b)=>a[0]-b[0]).slice(0,10),lowN:low.length,scroll:document.scrollingElement.scrollWidth>W+1}}"""
rep = {'odak': [], 'boy': []}
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    # 1) odak: masaüstünde klavye kullanıcısı gibi
    p = b.new_page(viewport={'width': 1366, 'height': 768}); p.goto(URL); p.wait_for_timeout(500); p.evaluate(SEED); p.wait_for_timeout(300)
    for ad, ac, kap, cl in SCREENS:
        p.evaluate("()=>{document.getElementById('play').focus()}")
        p.evaluate(ac); p.wait_for_timeout(250)
        f1 = p.evaluate(FOCUS, kap)
        tabs = 0
        for i in range(25):
            p.keyboard.press('Tab'); tabs += 1
            if p.evaluate(FOCUS, kap)['inside']: break
        else: tabs = None
        p.keyboard.press(cl); p.wait_for_timeout(200)
        back = p.evaluate("()=>document.activeElement&&(document.activeElement.id||document.activeElement.tagName)")
        rep['odak'].append(dict(ekran=ad, acilinca_icinde=f1['inside'], odak=f1['act'], tab_ile=tabs, kapaninca=back))
    # sekmeler arası geçişte açık sayfa kalıyor mu (ekran yığını)
    p.evaluate("()=>{window.__nb.slotOpen(0)}"); p.wait_for_timeout(150); p.evaluate("()=>window.__nb.setTab('def')"); p.wait_for_timeout(150)
    rep['yigin_panel_sekmede_acik'] = p.evaluate("()=>window.__nb.iOpen")
    p.evaluate("()=>{window.__nb.slotClose();window.__nb.collOpen()}"); p.wait_for_timeout(150); p.evaluate("()=>window.__nb.setTab('set')"); p.wait_for_timeout(150)
    rep['yigin_koleksiyon_ayarlarda_acik'] = p.evaluate("()=>!document.getElementById('cSheet').hidden")
    p.close()
    # 2) boy taraması
    for ad, w, h, mob in SIZES:
        ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob); p = ctx.new_page(); p.goto(URL); p.wait_for_timeout(500); p.evaluate(SEED); p.wait_for_timeout(300)
        rows = {}
        for t in (['stage'] + TABS):
            p.evaluate("t=>window.__nb.setTab(t)", t); p.wait_for_timeout(200)
            rows[t] = p.evaluate(CHECK)
            if t in ('stage', 'shop'): p.screenshot(path=os.path.join(OUT, '%s-%s.png' % (ad, t)))
        p.evaluate("()=>{window.__nb.setTab('stage');window.__nb.slotOpen(0)}"); p.wait_for_timeout(250); rows['panel'] = p.evaluate(CHECK); p.screenshot(path=os.path.join(OUT, '%s-panel.png' % ad))
        tgt = p.evaluate("""()=>[...document.querySelectorAll('button,[role=switch],select')].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect();return [Math.round(Math.min(r.width,r.height)),(e.id||e.dataset.act||e.textContent.trim().slice(0,14))]}).filter(x=>x[0]<32)""")
        rep['boy'].append(dict(boy=ad, wh='%dx%d' % (w, h), sayfa_kayar=any(r['scroll'] for r in rows.values()), tasan={k: v['over'] for k, v in rows.items() if v['over']}, kucuk_yazi_yuzde={k: v['small'] for k, v in rows.items()},
                               dusuk_kontrast={k: v['lowN'] for k, v in rows.items()}, kontrast_ornek=rows['stage']['low'][:5] + rows['def']['low'][:3], kucuk_hedef=len(tgt), kucuk_hedef_ornek=tgt[:8]))
        ctx.close()
    b.close()
json.dump(rep, open(os.path.join(OUT, 'arayuz_olc.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False, indent=1))
srv.shutdown()
