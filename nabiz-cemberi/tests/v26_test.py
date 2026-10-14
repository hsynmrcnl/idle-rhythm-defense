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
    card = lambda: p.evaluate("()=>document.getElementById('tut').hidden?'':document.getElementById('tutT').textContent")
    check(dock() == ['stage'] and p.is_visible('#t-set'), 'yeni oyunda dock’ta yalnız Sahne, Ayarlar dişlisi var (%s)' % dock())
    check(card() == 'Hoş geldin' and 'Öğretici 1 / 3' in p.text_content('#tutN'), 'öğretici 3 adım, ilk adım Hoş geldin')
    p.tap('#stats'); p.wait_for_timeout(150)
    check(not p.evaluate("()=>window.__nb.anlOn") and 'Analiz 4' in p.inner_text('#msg'), 'Analiz henüz kapalı, ne zaman açılacağı yazıyor')
    p.screenshot(path=os.path.join(OUT, 'v26_start.png'))
    # örnek şarkıda her şey görünür, çıkınca geri gizlenir
    p.click('#t-set'); p.click('#p-set [data-act=demoGo][data-k="0"]'); p.wait_for_timeout(300)
    check(len(dock()) == 5, 'örnek şarkıda bütün sekmeler görünüyor')
    p.click('#demoChip'); p.wait_for_timeout(200)
    check(dock() == ['stage'] and card() == 'Hoş geldin', 'örnek şarkıdan çıkınca yine yalnız Sahne, öğretici yerinde (%s)' % dock())
    # öğreticinin son adımı: ilk susturucu → Stüdyo açılır, kart gelir, dock simgesi parlar
    p.evaluate("()=>{const S=window.__nb.S;S.tut.s=2;S.kills=1}"); p.wait_for_timeout(400)
    check(card() == 'Yeni: Stüdyo' and dock() == ['stage', 'studio'] and p.locator('#d-studio.tut-hi').count() == 1, 'ilk susturucuyla Stüdyo açıldı, kart ve parlayan simge (%s)' % card())
    check(p.evaluate("()=>window.__nb.S.tut.done") is True, 'baştaki öğretici bitti')
    p.screenshot(path=os.path.join(OUT, 'v26_studio_card.png'))
    p.tap('#d-studio'); p.wait_for_timeout(200)
    st = p.evaluate("""()=>({tab:document.getElementById('app').dataset.tab,coll:!document.querySelector('#p-studio .subnav [data-tab=coll]').hidden,
      hi:document.querySelector('.tut-hi')&&document.querySelector('.tut-hi').id,sec:[...document.querySelectorAll('#secBar .sb')].map(e=>e.dataset.k),
      all:!!document.querySelector('[data-act=autoAll]'),inPanel:document.getElementById('tut').parentElement.id})""")
    check(st['tab'] == 'studio' and not st['coll'] and st['sec'] == ['sahne'] and not st['all'], 'Stüdyo’da yalnız Sahne; Koleksiyon, Otomatik, Hepsini düzenle henüz yok (%s)' % st)
    check(st['hi'] == 'lvb-davul' and st['inPanel'] == 'p-studio', 'kart Stüdyo’ya taşındı, Davul’un seviye düğmesini gösteriyor')
    p.evaluate("()=>{window.__nb.S.nota=1e4}"); p.wait_for_timeout(200)
    p.tap('#lvb-davul'); p.wait_for_timeout(400)
    check(card() == '', 'seviye alınca kart kapandı')
    # ♪ 150 → Koleksiyon
    p.evaluate("()=>{window.__nb.S.total=200}"); p.wait_for_timeout(400)
    check(card() == 'Yeni: Koleksiyon' and p.is_visible('#p-studio .subnav [data-tab=coll]'), 'kazanç 150’yi geçince Koleksiyon açıldı')
    p.tap('#p-studio .subnav [data-tab=coll]'); p.wait_for_timeout(150)
    p.tap('#collList [data-act=lv][data-id=trampet]'); p.wait_for_timeout(500)
    check(card() == 'Yeni: Uyum ve Otomatik', 'ikinci enstrümanla Uyum ve Otomatik kartı (%s)' % card())
    p.tap('#p-coll .subnav [data-tab=studio]'); p.wait_for_timeout(150)
    sec = p.evaluate("()=>[...document.querySelectorAll('#secBar .sb')].map(e=>e.dataset.k)")
    check(sec == ['sahne', 'auto', 'syn'] and p.locator('[data-act=autoAll]').count() == 1, 'Otomatik, Uyum ve Hepsini düzenle geldi (%s)' % sec)
    # dalga 3: sırayla Ritme vur, Savunma, Tempo kartları
    p.evaluate("()=>{window.__nb.S.bestWave=3}"); p.wait_for_timeout(400)
    seq = [card()]
    for k in range(3):
        p.tap('#tutNext'); p.wait_for_timeout(250); seq.append(card())
    check(seq == ['Yeni: Uyum ve Otomatik', 'Ritme vur', 'Yeni: Savunma', 'Yeni: Tempo'], 'kartlar sırayla geliyor (%s)' % seq)
    check(dock() == ['stage', 'studio', 'def'] and p.locator('#p-def [data-sec=ord]').is_hidden(), 'Savunma açıldı, Siparişler henüz kapalı (%s)' % dock())
    p.tap('#tutNext'); p.wait_for_timeout(200)
    # dalga 4: Analiz
    p.evaluate("()=>{window.__nb.S.bestWave=4}"); p.wait_for_timeout(400)
    check(card() == 'Yeni: Analiz' and p.locator('#d-stage.tut-hi').count() == 1, 'dalga 4’te Analiz kartı; başka sekmedeyken Sahne simgesi parlıyor')
    p.tap('#d-stage')
    try: p.wait_for_selector('#stats.tut-hi', timeout=2000)  # vurgu tutCheck aralığında gelir; ağır çizimde 300 ms yetmeyebiliyor
    except Exception: pass
    check(p.locator('#stats.tut-hi').count() == 1, 'Sahne’de üst bilgi parlıyor')
    p.tap('#stats'); p.wait_for_timeout(300)
    check(p.evaluate("()=>window.__nb.anlOn") and card() == '', 'üst bilgiye dokununca Analiz açıldı, kart kapandı')
    p.tap('#stats'); p.wait_for_timeout(100)
    # dalga 8 ve albüm eşiğinin yarısı: Görünüm ve Albüm
    p.evaluate("()=>{const S=window.__nb.S;S.bestWave=8;S.runEarned=1e9}"); p.wait_for_timeout(400)
    for k in range(8):
        if card() == '': break
        p.tap('#tutNext'); p.wait_for_timeout(150)
    found = p.evaluate("()=>Object.keys(window.__nb.S.found).length")
    p.tap('#d-album'); p.wait_for_timeout(150)
    check(dock() == ['stage', 'studio', 'def', 'album', 'look'] and found > 0 and p.is_visible('#p-album .subnav [data-tab=book]'), 'Görünüm ve Albüm açıldı; kalıp bulunduğu için Kitap Albüm’le geldi (%s)' % dock())
    # kaydet, yeniden aç: açılanlar kalır
    p.evaluate("()=>{const S=window.__nb.S;S.tipq=['look'];localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}")
    p.reload(); p.wait_for_timeout(500)
    check(dock() == ['stage', 'studio', 'def', 'album', 'look'] and card() == 'Yeni: Görünüm', 'yeniden açınca açılanlar ve bekleyen kart yerinde')
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
    check(tabs() == ['studio'] and p.is_visible('#p-studio') and not p.is_visible('#p-lock') and card() == 'Yeni: Stüdyo', 'ilk susturucuyla Stüdyo sekmesi açıldı')
    p.screenshot(path=os.path.join(OUT, 'v26_desktop.png'))
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    p.close()

    # ---------- eski kayıt: koşulu tutanlar sessiz açılır ----------
    print('eski kayıt')
    old = """{"v":3,"slots":["davul","trampet","hihat",null],"lv":{"davul":20,"trampet":10,"hihat":5},"pat":{"A":[[1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0]],"B":[],"S":[],"F":[]},
      "bestWave":12,"wave":10,"kills":500,"total":5e6,"albums":[{"n":"X","f":3,"b":100,"w":10}],"found":{"four":1},"famOpen":{"vur":1,"tel":1},"tut":{"s":9,"done":true},"open":{"syn":1,"rhy":1,"pat":1}}"""
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
    t1 = card() + ' ' + p.text_content('#tutP')
    p.tap('#tutNext'); p.wait_for_timeout(200)
    t2 = card() + ' ' + p.text_content('#tutP')
    check('New: Studio' in t1 and 'level up the Drum' in t1 and 'New family: Strings' in t2 and 'Collection' in t2, 'kartlar İngilizce: %s | %s' % (t1[:40], t2[:40]))
    check(not any(w in t1 + t2 for w in ('Yeni', 'Stüdyo', 'ailesi')), 'Türkçe kalmadı')
    check(not errs, 'sayfa hatası yok ' + '; '.join(errs))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d' % len(fails) if fails else 'hepsi geçti')
sys.exit(1 if fails else 0)
