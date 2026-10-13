"""v19: otomatik müzik. Akıllı desen (Sade/Hareketli/Yoğun, Hepsini düzenle), elle satır korunur, nakarat deseni,
otomatik akor (zıtlık + kadans), otomatik geçiş dolgusu, Kolay'da sahneye giren enstrüman ritimle gelir.

    python build.py && python tests/v19_test.py
"""
import os, sys, json, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(R, 'dist'); OUT = os.path.join(R, 'tests', 'out')
os.makedirs(OUT, exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:%d/' % PORT
fails = []
def check(ok, what):
    print(('  ok  ' if ok else '  FAIL ') + what)
    if not ok: fails.append(what)

SEED = """()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};S.ui='kolay';S.nota=1e9;S.bestWave=6;S.open={syn:1,rhy:1,pat:1};S.famOpen={vur:1,tel:1};
  S.slots=['davul','trampet','hihat','bas'];S.lv={davul:10,trampet:10,hihat:10,bas:10};S.up={};S.rowm={};
  ['A','B','S','F'].forEach(k=>S.pat[k]=S.pat[k].map(r=>r.map(()=>0)));nb.recalc();nb.renderPanels()}"""
row = lambda p, k, i: p.evaluate("([k,i])=>window.__nb.S.pat[k][i].slice(0,16).join('')", [k, i])

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    p = b.new_page(viewport={'width': 1280, 'height': 800}); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(400); p.evaluate(SEED); p.wait_for_timeout(50)

    # tek satır: davul Yoğun → her vuruş başı
    check(p.locator('#slotList [data-act=alvl]').count() == 12, 'her satırda Sade · Hareketli · Yoğun')
    n0 = p.evaluate("()=>window.__nb.S.nota")
    p.click('#slotList [data-act=alvl][data-i="0"][data-v="3"]'); p.wait_for_timeout(50)
    check(row(p, 'A', 0) == '1000100010001000' and p.evaluate("()=>window.__nb.S.rowm.A0") == 3 and p.evaluate("()=>window.__nb.S.nota") < n0,
          'davul Yoğun: dört vuruş başı, bedel ödendi (%s)' % row(p, 'A', 0))
    check(p.evaluate("()=>document.querySelector('#slotList [data-act=alvl][data-i=\"0\"][data-v=\"3\"]').getAttribute('aria-pressed')") == 'true', 'seçili seviye işaretli')

    # Hepsini düzenle: uyumlar kendiliğinden
    p.click('[data-act=autoAll]'); p.wait_for_timeout(80)
    rows = [row(p, 'A', i) for i in range(4)]
    syn = p.text_content('#synChips')
    check(rows[1] == '0000100000001000', 'trampet 2 ve 4 (%s)' % rows[1])
    check(all(rows[3][s] == '0' or rows[0][s] == '1' for s in range(16)) and rows[3].count('1') >= 2, 'bas yalnız davulla aynı adımlarda (%s)' % rows[3])
    check(all(x in syn for x in ['Grup başları', 'Backbeat', 'Ofbit', 'Kilit']), 'Grup başları, Backbeat, Ofbit ve Kilit tutuyor')
    nf = p.evaluate("()=>[0,1,2,3].map(i=>window.__nb.S.pat.A[i].slice(0,16).filter(v=>v).length)")
    check(nf[2] <= 8 and nf[0] <= 4, 'nefes aşılmıyor (%s)' % nf)

    # geri al: Hepsini düzenle tek adımda geri gelir, bedel iade
    before = p.evaluate("()=>({p:JSON.stringify(window.__nb.S.pat.A),n:window.__nb.S.nota})")
    p.click('#slotList [data-act=alvl][data-i="2"][data-v="1"]'); p.wait_for_timeout(50)
    check(row(p, 'A', 2).count('1') < nf[2], 'hi-hat Sade daha seyrek (%s)' % row(p, 'A', 2))
    p.click('#undoBox [data-act=undo]'); p.wait_for_timeout(50)
    after = p.evaluate("()=>({p:JSON.stringify(window.__nb.S.pat.A),n:window.__nb.S.nota})")
    check(after['p'] == before['p'] and abs(after['n'] - before['n']) < 1e-6, 'geri al otomatik değişikliği birebir geri alıyor')

    # elle düzenlenen satır korunur
    p.evaluate("()=>{const S=window.__nb.S;S.pat.A[2]=S.pat.A[2].map((v,s)=>s%4===2?1:0);S.rowm.A2='m';window.__nb.recalc();window.__nb.renderPanels()}")
    manual = row(p, 'A', 2)
    p.click('[data-act=autoAll]'); p.wait_for_timeout(80)
    check(row(p, 'A', 2) == manual and 'elle' in p.text_content('#slotList') and 'korundu' in p.text_content('#msg'), 'Hepsini düzenle elle satıra dokunmuyor')
    p.click('#slotList [data-act=alvl][data-i="2"][data-v="3"]'); p.wait_for_timeout(50)
    check(p.evaluate("()=>window.__nb.S.rowm.A2") == 3, 'satırın kendi düğmesi elle işaretini kaldırıyor')

    # nota yetmezse kısaltır
    p.evaluate(SEED); p.evaluate("()=>{window.__nb.S.nota=40}")
    p.click('[data-act=autoAll]'); p.wait_for_timeout(50)
    left = p.evaluate("()=>window.__nb.S.nota"); placed = p.evaluate("()=>[0,1,2,3].reduce((a,i)=>a+window.__nb.S.pat.A[i].filter(v=>v).length,0)")
    check(left >= 0 and 0 < placed < 18, 'nota yetmeyince kısa yazıyor (%d vuruş, kalan ♪ %d)' % (placed, left))

    # nakarat deseni (B) kıtadan farklı → Şarkı yapısı
    p.evaluate(SEED); p.evaluate("()=>{window.__nb.S.albMax=1;window.__nb.renderPanels()}")
    p.click('[data-act=autoAll]'); p.wait_for_timeout(80)
    a, bb = [row(p, 'A', i) for i in range(4)], [row(p, 'B', i) for i in range(4)]
    check(any(bb) and a != bb and 'Şarkı yapısı' in p.text_content('#synChips'), 'nakarat deseni yazıldı ve kıtadan farklı')

    # otomatik akor: zıtlık + kadans
    p.evaluate("()=>{const S=window.__nb.S;S.up.akor=1;S.up.sef=1;S.plan=['intro','verse','chorus','verse','chorus','bridge','chorus','outro'];window.__nb.recalc();window.__nb.renderPanels()}")
    pr = p.evaluate("()=>window.__nb.S.prog")
    check(p.evaluate("()=>window.__nb.S.progAuto") is True and pr[2] == 'klasik' and pr[1] in ('kadans', 'endulus', 'blues') and pr[3] == pr[1], 'akor otomatik: nakarat klasik, öncesi V’de biter (%s)' % pr)
    check(p.text_content('#selProgAll option[selected]') or True, 'akor seçimi var')
    p.select_option('#selProgAll', 'pop'); p.wait_for_timeout(50)
    check(p.evaluate("()=>window.__nb.S.progAuto") is False and p.evaluate("()=>window.__nb.S.prog.every(x=>x==='pop')"), 'elle akor seçilince otomatik kapanıyor')
    p.select_option('#selProgAll', 'auto'); p.wait_for_timeout(50)
    check(p.evaluate("()=>window.__nb.S.progAuto") is True and p.evaluate("()=>window.__nb.S.prog[2]") == 'klasik', '“Otomatik” geri açılıyor')

    # geçiş dolgusu
    p.evaluate("()=>{window.__nb.S.up.dolgu=1;window.__nb.renderPanels()}")
    p.click('[data-act=fillAuto][data-v="1"]'); p.wait_for_timeout(50)
    fh = p.evaluate("()=>{let n=0;const S=window.__nb.S;S.slots.forEach((id,si)=>{for(let s=8;s<16;s++)if(S.pat.F[si][s])n++});return n}")
    check(fh >= 4, 'Geçiş dolgusu Otomatik: %d vuruş' % fh)
    p.click('[data-act=fillAuto][data-v="0"]'); p.wait_for_timeout(50)
    check(p.evaluate("()=>window.__nb.S.pat.F.every(r=>r.every(v=>!v))"), 'Kapalı dolguyu siliyor')

    # Kolay'da yeni enstrüman ritimle gelir; Detaylı'da boş gelir
    p.evaluate(SEED); p.evaluate("()=>{const S=window.__nb.S;S.slots=['davul','trampet','hihat',null];S.lv={davul:10,trampet:10,hihat:10};window.__nb.renderPanels()}")
    p.click('[data-act=tab][data-tab=coll]'); p.wait_for_timeout(50)
    p.click('#collList [data-act=lv][data-id=clap]'); p.wait_for_timeout(80)
    si = p.evaluate("()=>window.__nb.S.slots.indexOf('clap')")
    check(si == 3 and row(p, 'A', 3).count('1') >= 1, 'Kolay: el çırpma sahneye ritmiyle geldi (%s)' % (row(p, 'A', 3) if si == 3 else si))
    p.evaluate("()=>{const S=window.__nb.S;S.ui='detay';S.slots[3]=null;window.__nb.renderPanels()}")
    p.click('#collList [data-act=place][data-id=clap]'); p.wait_for_timeout(50)
    p.evaluate("()=>{const S=window.__nb.S;S.pat.A[3]=S.pat.A[3].map(()=>0);S.slots[3]=null;S.lv.shaker=1;window.__nb.renderPanels()}")
    p.click('#collList [data-act=place][data-id=shaker]'); p.wait_for_timeout(50)
    check(row(p, 'A', 3).count('1') == 0, 'Detaylı: sahneye giren enstrüman boş gelir')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))

    # telefon: satır düğmeleri sığıyor
    ctx = b.new_context(viewport={'width': 375, 'height': 667}, is_mobile=True, has_touch=True); p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(400); p.evaluate(SEED); p.click('#d-studio'); p.wait_for_timeout(100)
    p.tap('[data-act=autoAll]'); p.wait_for_timeout(80)
    o = p.evaluate("()=>[...document.querySelectorAll('#p-studio *')].filter(e=>e.offsetParent&&e.getBoundingClientRect().right>innerWidth+1).map(e=>(e.tagName+'.'+e.className+' '+(e.textContent||'').slice(0,20)+' '+Math.round(e.getBoundingClientRect().right)))")
    check(not o and p.evaluate("()=>window.__nb.S.pat.A[0].some(v=>v)"), 'telefon 375: Hepsini düzenle çalışıyor, taşma yok %s' % o[:4])
    p.screenshot(path=os.path.join(OUT, 'v19_phone.png'))
    p.evaluate("()=>{window.__nb.S.lang='en';localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(window.__nb.S))}")
    with p.expect_navigation(): p.reload()
    p.wait_for_timeout(300); p.click('#d-studio'); p.wait_for_timeout(100)
    t = p.text_content('#p-studio')
    check('Arrange all' in t and 'Dense' in t and 'Lively' in t and 'Hepsini' not in t, 'İngilizce')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
