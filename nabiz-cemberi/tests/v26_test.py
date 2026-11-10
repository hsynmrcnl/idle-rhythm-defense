"""v26: aşamalı açılış. Yeni oyunda yalnız Sahne; Stüdyo, Koleksiyon, Savunma, Analiz, Görünüm, Albüm, Kitap
oynadıkça açılır, her açılışta kısa bir kart çıkar. Eski kayıtta koşulu tutanlar sessiz açılır.

    python build.py && python tests/v26_test.py
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

with sync_playwright() as pw:
    exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()

    # ---------- telefon: yeni oyun baştan ----------
    print('telefon 390x844')
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(500)
    dock = lambda: p.evaluate("()=>[...document.querySelectorAll('.dk')].filter(d=>!d.hidden).map(d=>d.id.slice(2))")
    card = lambda: p.evaluate("()=>document.getElementById('tutL').hidden?'':document.getElementById('tutLT').textContent")
    mk = lambda: p.evaluate("()=>window.__nb.S.tipq[0]||''")
    drop = lambda: p.evaluate("()=>{const S=window.__nb.S;S.tipq=[];S.tutm=0}")
    def hole_tap():
        prev = None
        for k in range(30):
            r = p.evaluate("()=>{const h=document.getElementById('tutHole').getBoundingClientRect();return [Math.round(h.left+h.width/2),Math.round(h.top+h.height/2)]}")
            if r == prev: break
            prev = r; p.wait_for_timeout(120)
        p.mouse.click(r[0], r[1]); p.wait_for_timeout(400)
    check(dock() == ['stage'] and p.is_visible('#t-set'), 'yeni oyunda dock’ta yalnız Sahne, Ayarlar dişlisi var (%s)' % dock())
    check('Hoş geldin' in p.text_content('#tutLT') and 'Öğretici 1 / 13' in p.text_content('#tutLN'), 'zorunlu öğretici 13 adım, ilk adım Hoş geldin')
    p.tap('#stats'); p.wait_for_timeout(150)
    check(not p.evaluate("()=>window.__nb.anlOn"), 'öğretici sürerken üst bilgiye dokunmak bir şey açmıyor')
    p.screenshot(path=os.path.join(OUT, 'v26_start.png'))
    # öğretici atlanır (Atla 5 sn sonra); sonra açılış kartları eskisi gibi
    p.wait_for_timeout(5200); p.tap('#tutSkipL'); p.wait_for_timeout(200)
    check(p.evaluate("()=>window.__nb.S.tut.done") is True and p.is_hidden('#tutL'), 'Atla ile öğretici kapandı')
    # örnek şarkıda her şey görünür, çıkınca geri gizlenir
    p.click('#t-set'); p.click('#p-set [data-act=demoGo][data-k="0"]'); p.wait_for_timeout(300)
    check(len(dock()) == 5, 'örnek şarkıda bütün sekmeler görünüyor')
    p.click('#demoChip'); p.wait_for_timeout(200)
    check(dock() == ['stage'], 'örnek şarkıdan çıkınca yine yalnız Sahne (%s)' % dock())
    p.tap('#stats'); p.wait_for_timeout(150)
    check(not p.evaluate("()=>window.__nb.anlOn") and 'Analiz 14' in p.inner_text('#msg'), 'Analiz henüz kapalı, ne zaman açılacağı yazıyor')
    p.evaluate("()=>{const S=window.__nb.S;S.kills=1}"); p.wait_for_timeout(400)
    check(mk() == 'studio' and card() == 'Yeni: Stüdyo' and dock() == ['stage', 'studio'], 'ilk susturucuyla Stüdyo açıldı, kısa öğretici başladı (%s)' % card())
    p.screenshot(path=os.path.join(OUT, 'v26_studio_card.png'))
    hole_tap()
    st = p.evaluate("""()=>({tab:document.getElementById('app').dataset.tab,coll:!document.querySelector('#p-studio .subnav [data-tab=coll]').hidden,
      sec:[...document.querySelectorAll('#secBar .sb')].map(e=>e.dataset.k),all:!!document.querySelector('[data-act=autoAll]')})""")
    check(st['tab'] == 'studio' and not st['coll'] and st['sec'] == ['sahne'] and not st['all'], 'Stüdyo’da yalnız Sahne; Koleksiyon, Otomatik, Hepsini düzenle henüz yok (%s)' % st)
    check(card() == 'Yükselt', 'ikinci adım Davul’un seviye düğmesi')
    lv0 = p.evaluate("()=>window.__nb.S.lv.davul"); hole_tap()
    check(p.evaluate("()=>window.__nb.S.lv.davul") > lv0 and card() == '', 'seviye alınca kısa öğretici bitti')
    p.evaluate("()=>{window.__nb.S.total=200}"); p.wait_for_timeout(400)
    check(mk() == 'coll' and p.is_visible('#p-studio .subnav [data-tab=coll]'), 'kazanç 150’yi geçince Koleksiyon açıldı')
    drop(); p.wait_for_timeout(200)
    p.tap('#p-studio .subnav [data-tab=coll]'); p.wait_for_timeout(150)
    p.evaluate("()=>{window.__nb.S.nota=1e4}"); p.tap('#collList [data-act=lv][data-id=trampet]'); p.wait_for_timeout(500)
    check(mk() == 'syn', 'ikinci enstrümanla Uyum kısa öğreticisi (%s)' % mk())
    drop(); p.wait_for_timeout(200)
    p.tap('#p-coll .subnav [data-tab=studio]'); p.wait_for_timeout(150)
    sec = p.evaluate("()=>[...document.querySelectorAll('#secBar .sb')].map(e=>e.dataset.k)")
    check(sec == ['sahne', 'auto', 'syn'] and p.locator('[data-act=autoAll]').count() == 1, 'Otomatik, Uyum ve Hepsini düzenle geldi (%s)' % sec)
    p.evaluate("()=>{window.__nb.S.bestWave=8}")
    try: p.wait_for_function("()=>window.__nb.S.tipq.length>=3", timeout=4000)
    except Exception: pass
    q = p.evaluate("()=>window.__nb.S.tipq.slice()")
    check(q[:3] == ['tap', 'def', 'rhy'], 'kısa öğreticiler sırada: Ritme vur, Savunma, Tempo (%s)' % q)
    drop(); p.wait_for_timeout(200)
    check(dock() == ['stage', 'studio', 'def'] and p.locator('#p-def [data-sec=ord]').is_hidden(), 'Savunma açıldı, Siparişler henüz kapalı (%s)' % dock())
    p.evaluate("()=>{window.__nb.S.bestWave=14}"); p.wait_for_timeout(400)
    p.evaluate("()=>{const S=window.__nb.S;S.tipq=S.tipq.filter(k=>k==='anl');S.tutm=0}"); p.wait_for_timeout(300)
    check(card() == 'Yeni: Analiz', 'dalga 14’te Analiz kısa öğreticisi')
    hole_tap(); hole_tap()
    check(p.evaluate("()=>window.__nb.anlOn"), 'üst bilgiye dokununca Analiz açıldı')
    p.click('#tutLBtn'); p.wait_for_timeout(300)
    check(card() == '', 'Analiz öğreticisi bitti')
    p.tap('#stats'); p.wait_for_timeout(100)
    p.evaluate("()=>{const S=window.__nb.S;S.bestWave=20;S.runEarned=1e9}"); p.wait_for_timeout(400)
    drop(); p.wait_for_timeout(200)
    found = p.evaluate("()=>Object.keys(window.__nb.S.found).length")
    p.tap('#d-album'); p.wait_for_timeout(150)
    check(dock() == ['stage', 'studio', 'def', 'album', 'look'] and found > 0 and p.is_visible('#p-album .subnav [data-tab=book]'), 'Görünüm ve Albüm açıldı; kalıp bulunduğu için Kitap Albüm’le geldi (%s)' % dock())
    # kaydet, yeniden aç: açılanlar kalır
    p.evaluate("()=>{const S=window.__nb.S;S.tipq=['look'];localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}")
    p.reload(); p.wait_for_timeout(500)
    check(dock() == ['stage', 'studio', 'def', 'album', 'look'] and card() == 'Yeni: Görünüm', 'yeniden açınca açılanlar ve bekleyen öğretici yerinde (%s)' % card())
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    ctx.close()

    # ---------- masaüstü ----------
    print('masaüstü 1280x800')
    p = b.new_page(viewport={'width': 1280, 'height': 800}); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(500)
    tabs = lambda: p.evaluate("()=>[...document.querySelectorAll('.tabs .tab:not(.mob)')].filter(e=>!e.hidden).map(e=>e.dataset.tab)")
    check(tabs() == [] and p.is_visible('#p-lock') and not p.is_visible('#p-studio') and not p.is_visible('#tap'), 'yeni oyunda sekme yok, Stüdyo yerine bekleme notu, Ritme vur düğmesi yok')
    p.evaluate("()=>{window.__nb.S.tut.done=true;window.__nb.S.kills=1}"); p.wait_for_timeout(400)
    check(tabs() == ['studio'] and p.is_visible('#p-studio') and not p.is_visible('#p-lock') and mk() == 'studio', 'ilk susturucuyla Stüdyo sekmesi açıldı, kısa öğretici sırada')
    p.screenshot(path=os.path.join(OUT, 'v26_desktop.png'))
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    p.close()

    # ---------- eski kayıt: koşulu tutanlar sessiz açılır ----------
    print('eski kayıt')
    old = """{"v":3,"slots":["davul","trampet","hihat",null],"lv":{"davul":20,"trampet":10,"hihat":5},"pat":{"A":[[1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0]],"B":[],"S":[],"F":[]},
      "bestWave":20,"wave":10,"kills":500,"total":5e6,"albums":[{"n":"X","f":3,"b":100,"w":10}],"found":{"four":1},"famOpen":{"vur":1,"tel":1},"tut":{"s":9,"done":true},"open":{"syn":1,"rhy":1,"pat":1}}"""
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True); p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.add_init_script("localStorage.setItem('nabiz-cemberi-v3', %s)" % repr(old))
    p.goto(URL); p.wait_for_timeout(500)
    u = p.evaluate("()=>Object.keys(window.__nb.S.unl).sort()")
    check(all(k in u for k in ('studio', 'coll', 'syn', 'def', 'anl', 'ord', 'look', 'album', 'mn', 'book')) and 'plan' not in u, 'eski kayıtta ilerlemeye göre açık (%s)' % u)
    check(len(dock()) == 5 and card() == '' and p.evaluate("()=>window.__nb.S.tipq.length") == 0, 'eski kayıtta kart yağmuru yok, dock tam')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    ctx.close()

    # ---------- İngilizce ----------
    print('EN')
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True); p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_timeout(300)
    p.evaluate("()=>{const S=window.__nb.S;S.lang='en';S.tut={s:0,done:true};S.kills=1;S.tipq=[];localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}")
    p.reload(); p.wait_for_timeout(500)
    p.evaluate("()=>{window.__nb.S.tipq=['studio','fam_tel'];window.__nb.renderPanels()}"); p.wait_for_timeout(300)
    t1 = card() + ' ' + p.text_content('#tutLP')
    p.evaluate("()=>{const S=window.__nb.S;S.tipq.shift();S.tutm=0}"); p.wait_for_timeout(300)
    t2 = card() + ' ' + p.text_content('#tutLP')
    check(('New: Studio' in t1 or 'Upgrade' in t1) and 'New family' in t2 and 'Collection' in t2, 'kartlar İngilizce: %s | %s' % (t1[:40], t2[:40]))
    check(not any(w in t1 + t2 for w in ('Yeni', 'Stüdyo', 'ailesi')), 'Türkçe kalmadı')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
