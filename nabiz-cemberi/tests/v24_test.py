"""v24: tam ekran sahne, sade üst bilgi + nabız çubuğu, solodan çıkış, nota araçları simgesi,
Stüdyo/Koleksiyon sabit üst bar (bölüm düğmeleri, aile simgeleri), sıkı Kuşatma, tek Otomatik bölümü.

    python build.py && python tests/v24_test.py
"""
import os, sys, threading, functools, http.server, socketserver
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

SEED = """()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};S.ui='kolay';S.nota=5e6;S.wave=12;S.bestWave=15;S.famOpen.tel=1;S.open={syn:1,rhy:1,pat:1};
  S.slots=['davul','trampet','hihat','bas'];S.lv={davul:30,trampet:22,hihat:11,bas:8,clap:3};S.def={hasar:3,menzil:2,nabiz:2};nb.renderPanels()}"""
SOLO = """()=>{const nb=window.__nb,S=nb.S;S.up.solo=1;S.up.sdevir=1;S.up.suzun=1;S.slots[2]='gitar';S.lv.gitar=2;S.solo={2:1};
  S.solos={2:{notes:[{t:0,len:3,r:0,art:'none'},{t:6,len:1,r:2,art:'none'}],style:'hendrix'}};nb.renderPanels()}"""

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()

    # ---------- telefon ----------
    for w, h in [(375, 667), (390, 844)]:
        print('telefon %dx%d' % (w, h))
        ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=True, has_touch=True)
        p = ctx.new_page(); errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.goto(URL); p.wait_for_timeout(500); p.evaluate(SEED); p.wait_for_timeout(200)
        # tam ekran sahne: tuval kenardan kenara, oyun karesi ortada, köşeye dokunmak tuvale gider
        m = p.evaluate("""()=>{const c=document.getElementById('cv').getBoundingClientRect(),e=document.elementFromPoint(c.left+4,c.top+c.height/2);
          return {l:c.left,w:c.width,h:c.height,vw:innerWidth,L:window.__nb.L,hit:e&&e.id}}""")
        check(m['l'] == 0 and abs(m['w'] - m['vw']) < 1 and m['hit'] == 'cv', 'tuval kenardan kenara, kenara dokunmak tuvale gidiyor (%s)' % m)
        check(m['h'] >= m['w'] - 1 and abs(m['L'] - min(m['w'], m['h'])) < 1, 'tuval sahne alanının tamamı, oyun karesi ortada (%dx%d, kare %d)' % (m['w'], m['h'], m['L']))
        # üst bilgi: kaymaz, Nota en büyük, nabız ince bir çubuk
        st = p.evaluate("""()=>{const s=document.getElementById('stats'),f=q=>parseFloat(getComputedStyle(document.querySelector(q)).fontSize);
          return {ov:s.scrollWidth-s.clientWidth,h:s.getBoundingClientRect().height,nota:f('#sNota'),rate:f('#sRate'),bar:document.getElementById('stNabiz').getBoundingClientRect().height}}""")
        check(st['ov'] <= 0 and st['h'] < 56, 'üst bilgi tek satır, kaymıyor (yükseklik %dpx)' % st['h'])
        check(st['nota'] > st['rate'] * 1.4 and st['bar'] <= 4, 'önem sırası: Nota büyük, gelir küçük; nabız %dpx çubuk' % st['bar'])
        p.evaluate("()=>{const nb=window.__nb;nb.core.hp=nb.core.hp/2;nb.core.sh=0}"); p.wait_for_timeout(500)
        fr = p.evaluate("()=>[document.getElementById('sHpBar').getBoundingClientRect().width/document.getElementById('stNabiz').getBoundingClientRect().width,parseInt(document.getElementById('sHp').textContent)/100]")
        check(fr[1] < 0.9 and abs(fr[0] - fr[1]) < 0.03, 'nabız çubuğu Nabız’la kısalıyor (%.2f / %.2f)' % tuple(fr))
        p.tap('#stats'); p.wait_for_timeout(150)
        check(p.evaluate("()=>window.__nb.anlOn"), 'üst bilgiye dokununca Analiz açılıyor')
        p.tap('#stats'); p.wait_for_timeout(100)
        # solo sahnesi: çip ile çıkış; nota seçili değilken araç çubuğu yok, seçince neon simge, açınca sahne daralmıyor
        p.evaluate(SOLO); p.evaluate("()=>window.__nb.setEdit('S')"); p.wait_for_timeout(200)
        check(p.is_visible('#soloChip') and p.evaluate("()=>window.__nb.soloView()") >= 0, 'solo sahnesinde “Solodan çık” çipi görünüyor')
        check(p.locator('#pads .padtb').count() == 0 and 'Nota seçili değil' not in p.inner_text('#pads') and not p.is_visible('#soloTbWrap'), 'nota seçili değilken araç satırı yok, sahne daralmıyor')
        cv0 = p.evaluate("()=>document.getElementById('cv').getBoundingClientRect().height")
        p.tap('#pads [data-act=spad][data-t="0"]'); p.wait_for_timeout(150)
        check(p.is_visible('#pads .sotg') and not p.is_visible('#soloTbStage'), 'nota seçince neon simge geliyor, panel kapalı')
        p.tap('#pads .sotg'); p.wait_for_timeout(250)
        tb = p.evaluate("""()=>{const a=document.getElementById('soloTbStage').getBoundingClientRect(),g=document.querySelector('#pads .sotg').getBoundingClientRect();
          return {vis:a.width>0,right:a.right,gl:g.left,left:a.left,cv:document.getElementById('cv').getBoundingClientRect().height}}""")
        check(tb['vis'] and tb['right'] <= tb['gl'] + 1 and tb['left'] >= 0 and abs(tb['cv'] - cv0) < 1, 'simgeye dokununca panel sola açılıyor, tuval aynı boyda (%s)' % tb)
        check(p.locator('#soloTbStage [data-act=soloDel]').count() == 1, 'panelde nota araçları (sil, teknik)')
        if w == 390: p.screenshot(path=os.path.join(OUT, 'v24_solo_tools.png'))
        p.tap('#soloChip'); p.wait_for_timeout(200)
        check(p.evaluate("()=>window.__nb.S.edit") == 'A' and not p.is_visible('#soloChip') and p.evaluate("()=>window.__nb.soloView()") < 0, 'çip soloyu kapatıp önceki desene döndürüyor')
        if w == 390: p.screenshot(path=os.path.join(OUT, 'v24_stage.png'))
        # Stüdyo: sabit üst bar, bölüm düğmeleri tek bölüm gösterir
        p.click('#d-studio'); p.wait_for_timeout(150)
        if p.evaluate("()=>document.getElementById('app').dataset.tab") != 'studio': p.click('#p-coll .subnav [data-tab=studio]'); p.wait_for_timeout(100)
        shown = lambda: p.evaluate("()=>[...document.querySelectorAll('#p-studio [data-sec]')].filter(e=>e.offsetParent).map(e=>e.dataset.sec)")
        check(shown() == ['sahne'], 'Stüdyo açılınca yalnız Sahne görünüyor (%s)' % shown())
        btns = p.evaluate("()=>[...document.querySelectorAll('#secBar .sb')].map(e=>e.dataset.k)")
        check(btns[:2] == ['sahne', 'auto'] and 'rhy' in btns and 'syn' in btns, 'üst barda bölüm düğmeleri (%s)' % btns)
        p.tap('#secBar [data-k=auto]'); p.wait_for_timeout(100)
        check(shown() == ['auto'], 'Otomatik düğmesi yalnız Otomatik bölümünü açıyor (%s)' % shown())
        p.tap('#secBar [data-k=sahne]'); p.wait_for_timeout(100)
        p.evaluate("()=>{document.getElementById('rack').scrollTop=400}"); p.wait_for_timeout(100)
        sk = p.evaluate("()=>{const t=document.querySelector('#p-studio .topbar').getBoundingClientRect(),r=document.getElementById('rack').getBoundingClientRect();return {t:t.top,r:r.top,st:document.getElementById('rack').scrollTop}}")
        check(sk['st'] > 0 and abs(sk['t'] - sk['r']) < 2, 'aşağı kayınca üst bar sabit kalıyor (%s)' % sk)
        o = p.evaluate("()=>[...document.querySelectorAll('#p-studio *')].filter(e=>e.offsetParent&&e.getBoundingClientRect().right>innerWidth+1).map(e=>e.className).slice(0,4)")
        check(not o, 'Stüdyo yana taşmıyor %s' % o)
        # öğretici seviye adımı gizli bölümdeki düğmeyi vurguluyorsa o bölüme geçer
        p.tap('#secBar [data-k=auto]'); p.wait_for_timeout(80)
        p.evaluate("()=>{const S=window.__nb.S;S.lv.davul=1;S.tut={s:3,done:false};window.__nb.renderPanels()}")
        try: p.wait_for_selector('#lvb-davul.tut-hi', state='visible', timeout=2500)
        except Exception: pass
        check(p.is_visible('#lvb-davul') and shown() == ['sahne'], 'öğretici vurguladığı düğmenin bölümünü açıyor (%s)' % shown())
        p.evaluate("()=>{const S=window.__nb.S;S.lv.davul=30;S.tut={s:0,done:true};window.__nb.renderPanels()}")
        # Koleksiyon: aile simgeleri, kilitli ailede koşullar, açık ailede sıkı satır
        p.click('#p-studio .subnav [data-tab=coll]'); p.wait_for_timeout(120)
        fb = p.evaluate("()=>[...document.querySelectorAll('#famBar .sb')].map(e=>[e.dataset.f,e.classList.contains('locked'),e.textContent.trim()])")
        check(len(fb) == 6 and all(t == '' for _, _, t in fb) and [l for _, l, _ in fb] == [False, False, True, True, True, True], 'altı aile yazısız simgeyle, kilitliler işaretli (%s)' % fb)
        ir = p.evaluate("""()=>{const r=document.querySelector('#collList .irow .own').closest('.irow'),nm=r.querySelector('.nm').getBoundingClientRect(),o=r.querySelector('.own').getBoundingClientRect(),ie=r.querySelector('.ie').getBoundingClientRect();
          return {same:Math.abs((o.top+o.bottom)/2-(nm.top+nm.bottom)/2)<14,right:o.right>innerWidth-40,ie:ie.left>nm.left,h:r.getBoundingClientRect().height,n:document.querySelectorAll('#collList .irow').length}}""")
        check(ir['same'] and ir['right'] and ir['ie'] and ir['h'] < 64 and ir['n'] == 12, '“Sahnede” başlık hizasında en sağda, etki adın yanında, satır %dpx' % ir['h'])
        p.tap('#famBar [data-f=tus]'); p.wait_for_timeout(100)
        t = p.inner_text('#collList')
        check('albüm' in t and p.locator('#collList [data-act=openFam][data-f=tus]').count() == 1 and p.locator('#collList .irow').count() == 0, 'kilitli aileye dokununca açılma koşulları ve Aileyi aç')
        if w == 390: p.screenshot(path=os.path.join(OUT, 'v24_coll_locked.png'))
        p.tap('#famBar [data-f=vur]'); p.wait_for_timeout(80)
        if w == 390: p.screenshot(path=os.path.join(OUT, 'v24_coll.png'))
        # Savunma: Kuşatma iki satır, ekran kaymıyor
        p.click('#d-def'); p.wait_for_timeout(200)
        d = p.evaluate("()=>{const r=document.getElementById('rack');return {sc:r.scrollHeight-r.clientHeight,h:document.querySelector('[data-sec=siege]').getBoundingClientRect().height,o:window.__nb.S.orders.filter(o=>o.tpl).length}}")
        check(d['h'] < 120 and d['sc'] <= 0, 'Kuşatma kısa (%dpx), Savunma kaymıyor (fazla %dpx, %d sipariş)' % (d['h'], d['sc'], d['o']))
        check('düşman' in p.inner_text('#defStatus') and 'Bu dalga' in p.evaluate("()=>document.querySelector('[data-sec=siege] .info').textContent"), 'dalga içeriği ⓘ’da')
        if w == 375: p.screenshot(path=os.path.join(OUT, 'v24_def_375.png'))
        check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
        ctx.close()

    # ---------- Otomatik (masaüstü) ----------
    print('Otomatik')
    p = b.new_page(viewport={'width': 1280, 'height': 900}); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(400); p.evaluate(SEED); p.wait_for_timeout(100)
    check(p.locator('[data-sec=auto] [data-act=amTog][data-k=yeni]').count() == 1 and p.locator('#slotAdd [data-act=autoUp]').count() == 0, 'Otomatik bölümü var; Sahne kartında eski Otomatik geliştir satırı yok')
    # yeni enstrüman ritmi: kapalıyken boş, açıkken ritimle (Kolay/Detaylı'dan bağımsız)
    p.click('[data-act=amTog][data-k=yeni]'); p.wait_for_timeout(50)
    check(p.evaluate("()=>window.__nb.S.am.yeni") is False, 'anahtar kapatıyor')
    p.evaluate("()=>{const S=window.__nb.S;S.slots.push(null);window.__nb.renderPanels()}")
    p.click('[data-act=tab][data-tab=coll]'); p.click('#collList [data-act=place][data-id=clap]'); p.wait_for_timeout(80)
    row = lambda i: p.evaluate("i=>window.__nb.S.pat.A[i].slice(0,16).join('')", i)
    check(row(4).count('1') == 0, 'kapalıyken sahneye giren el çırpma boş geliyor')
    p.evaluate("()=>{const S=window.__nb.S;S.slots[4]=null;S.ui='detay';window.__nb.renderPanels()}")
    p.click('[data-act=tab][data-tab=studio]'); p.click('[data-act=amTog][data-k=yeni]'); p.wait_for_timeout(50)
    p.click('[data-act=tab][data-tab=coll]'); p.click('#collList [data-act=place][data-id=clap]'); p.wait_for_timeout(80)
    check(row(4).count('1') >= 1, 'açıkken Detaylı’da da ritimle geliyor (%s)' % row(4))
    p.evaluate("()=>{const S=window.__nb.S;S.ui='kolay';window.__nb.renderPanels()}")
    p.click('[data-act=tab][data-tab=studio]'); p.wait_for_timeout(50)
    # Başka öneri: farklı dizilim, davul vuruş başları korunur
    p.click('[data-act=autoAll]'); p.wait_for_timeout(80)
    a0 = p.evaluate("()=>JSON.stringify(window.__nb.S.pat.A.slice(0,5).map(r=>r.slice(0,16)))")
    seen = set([a0]); kept = True
    for k in range(4):
        p.click('[data-act=autoAlt]'); p.wait_for_timeout(80)
        seen.add(p.evaluate("()=>JSON.stringify(window.__nb.S.pat.A.slice(0,5).map(r=>r.slice(0,16)))"))
        kept = kept and all(p.evaluate("()=>window.__nb.S.pat.A[0]")[s] for s in (0, 4, 8, 12))
    check(len(seen) >= 3 and kept, 'Başka öneri her seferinde farklı dizilim (%d farklı), davul vuruş başlarında kalıyor' % len(seen))
    check('Başka öneri' in p.inner_text('#msg') and '/sn' in p.inner_text('#msg'), 'öneri mesajı geliri gösteriyor: ' + p.inner_text('#msg'))
    # menajer: türler ve harcama sınırı
    p.evaluate("()=>{const S=window.__nb.S;S.albums=[{n:'X',f:1,b:100,w:10}];S.albMax=1;S.mn.lv=1;S.auto.lv=true;S.def={};window.__nb.renderPanels()}")
    check(p.locator('[data-act=amK]').count() >= 4 and p.locator('[data-act=amB]').count() == 3, 'Geliştirme için tür ve harcama sınırı seçenekleri')
    for k in ('lv', 'rup', 'srup'):
        if p.locator('[data-act=amK][data-k=%s][aria-pressed=true]' % k).count(): p.click('[data-act=amK][data-k=%s]' % k)
    p.click('[data-act=amK][data-k=def]'); p.click('[data-act=amB][data-v="0.25"]'); p.wait_for_timeout(50)
    k = p.evaluate("()=>window.__nb.S.am.k")
    check(not k['lv'] and not k['rup'] and not k['tempo'] and k['def'] and p.evaluate("()=>window.__nb.S.am.b") == 0.25, 'yalnız Savunma seçildi, sınır %%25 (%s)' % k)
    # 2 sn'lik gerçek menajer döngüsü de çalışıyor: ölçümü tek seferde al, sonra elle bir tur çalıştır
    s0, n0, d0 = p.evaluate("()=>{const nb=window.__nb,S=nb.S,r=[JSON.stringify([S.lv,S.up]),S.nota,Object.values(S.def).reduce((a,b)=>a+b,0)];nb.autoReset();nb.autoTick();return r}")
    s1, n1, dd = p.evaluate("()=>{const S=window.__nb.S;return [JSON.stringify([S.lv,S.up]),S.nota,Object.values(S.def).reduce((a,b)=>a+b,0)]}")
    dd -= d0
    check(dd == 1 and s0 == s1 and 0 < n0 - n1 <= n0 * 0.25 + 1, 'menajer yalnız savunma aldı, sınırı aşmadı (♪ %d)' % (n0 - n1))
    p.click('[data-act=amTog][data-k=mn_lv]'); p.wait_for_timeout(50)
    check(p.evaluate("()=>window.__nb.S.auto.lv") is False and p.locator('[data-act=amK]').count() == 0, 'Geliştirme kapanınca seçenekler gizleniyor')
    # solo sahnesinden Esc ile çıkış (masaüstü)
    p.evaluate(SOLO); p.evaluate("()=>window.__nb.setEdit('S')"); p.wait_for_timeout(100)
    check(p.is_visible('#soloChip'), 'masaüstünde de çip görünüyor')
    p.keyboard.press('Escape'); p.wait_for_timeout(100)
    check(p.evaluate("()=>window.__nb.S.edit") == 'A', 'Esc soloyu kapatıyor')
    p.screenshot(path=os.path.join(OUT, 'v24_desktop.png'))
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    # eski Detaylı kayıt: müzik otomatikleri kapalı başlar
    old = p.evaluate("""()=>{const S=JSON.parse(JSON.stringify(window.__nb.S));delete S.am;S.ui='detay';return JSON.stringify(S)}""")
    p.close(); p = b.new_page(viewport={'width': 1280, 'height': 900})
    p.add_init_script("localStorage.setItem('nabiz-cemberi-v3', %s)" % repr(old))
    p.goto(URL); p.wait_for_timeout(400)
    check(p.evaluate("()=>JSON.stringify([window.__nb.S.am.yeni,window.__nb.S.am.nakarat,window.__nb.S.am.solo,window.__nb.S.am.b])") == '[false,false,false,0.5]', 'eski Detaylı kayıtta müzik otomatikleri kapalı')
    p.close()

    # ---------- İngilizce ----------
    print('EN')
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(300); p.evaluate(SEED)
    p.evaluate("()=>{const S=window.__nb.S;S.lang='en';S.albums=[{n:'X',f:1,b:100,w:10}];S.albMax=1;S.mn.lv=1;S.up.akor=1;localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}")
    p.reload(); p.wait_for_timeout(400)
    st = p.inner_text('#stats')
    check('/s' in st and '/sn' not in st and 'WAVE' in st.upper(), 'üst bilgi İngilizce: ' + st.replace('\n', ' '))
    p.click('#d-studio'); p.wait_for_timeout(100)
    if p.evaluate("()=>document.getElementById('app').dataset.tab") != 'studio': p.click('#p-coll .subnav [data-tab=studio]')
    p.tap('#secBar [data-k=auto]'); p.wait_for_timeout(100)
    t = p.inner_text('#autoBox') + ' ' + p.inner_text('#secBar')
    left = [x for x in ['Yeni enstrüman', 'Akorlar', 'Menajer', 'Neyi alsın', 'Harcama', 'Seviye', 'Savunma', 'Geliştirme', 'Otomatik', 'Ruh hâli', 'Uyum'] if x in t]
    check('New instrument rhythm' in t and 'what to buy' in t.lower() and not left, 'Otomatik ve bölüm çubuğu İngilizce %s' % left)
    p.click('#p-studio .subnav [data-tab=coll]'); p.wait_for_timeout(100)
    t = p.inner_text('#p-coll')
    check('On stage' in t and 'Percussion' in t and 'Sahnede' not in t, 'Koleksiyon İngilizce')
    p.click('#d-def'); p.wait_for_timeout(100)
    t = p.inner_text('#defStatus')
    check('enemies' in t and 'dmg/s' in t and 'düşman' not in t, 'Kuşatma İngilizce: ' + t.replace('\n', ' '))
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
