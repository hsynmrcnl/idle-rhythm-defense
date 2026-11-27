"""v99 dalga can tabanı (kule savunma denetimi): güçlü oyuncuda normal dalganın toplam canı en az hasar/sn × yayılım × 0,6,
patron dalgasında × 1,3; zayıf oyuncuda eski can (taban yalnız yukarı iter); baskın canları değişmez.

    python build.py && python tests/v99_test.py
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
BASE="()=>{const nb=window.__nb,S=nb.S;S.tut={s:0,done:true};S.unl={studio:1,coll:1,tap:1};S.tipq=[];S.muted=true;S.pat.A[0]=S.pat.A[0].map((v,i)=>i%4===0?1:0);nb.recalc()}"
with sync_playwright() as pw:
    exe='/opt/pw-browsers/chromium'
    b=pw.chromium.launch(executable_path=exe) if os.path.exists(exe) else pw.chromium.launch()
    er=[]
    # zayıf oyuncu: dalga 1–3 eski formül (4·1,19^(w-1)·tür canı)
    p=b.new_page();p.on('pageerror',lambda e:er.append(str(e)));p.goto(URL);p.wait_for_timeout(400);p.evaluate(BASE)
    dw=p.evaluate("()=>window.__nb.dps()*window.__nb.globalMDmg()");bar=p.evaluate("()=>60/window.__nb.S.bpm*4")
    p.evaluate("()=>window.__nb.ff(70)")
    w1=p.evaluate("()=>window.__nb.WHP[1]")
    check(w1 and w1<=200,'zayıf oyuncuda dalga 1 canı küçük kalıyor (%.1f; güçlüde binlerce)'%(w1 or 0))
    p.close()
    # güçlü oyuncu: taban devrede
    p=b.new_page();p.on('pageerror',lambda e:er.append(str(e)));p.goto(URL);p.wait_for_timeout(400);p.evaluate(BASE)
    p.evaluate("()=>{const nb=window.__nb,S=nb.S;S.lv.davul=60;nb.recalc()}")
    d=p.evaluate("()=>window.__nb.dps()*window.__nb.globalMDmg()")
    p.evaluate("()=>{const nb=window.__nb;for(let i=0;i<70;i++)nb.ff(5)}");p.wait_for_timeout(100)
    W=p.evaluate("()=>window.__nb.WHP")
    w3=float(W.get('3',0)); w10=float(W.get('10',0))
    check(w3>=0.6*6*bar*d*0.98,'normal dalga canı ≥ 0,6 × hasar/sn × yayılım (%.0f ≥ %.0f)'%(w3,0.6*6*bar*d))
    check(w10>=1.3*7*bar*d*0.98 and w10>0,'patron dalgası canı ≥ 1,3 × hasar/sn × yayılım (%.0f ≥ %.0f)'%(w10,1.3*7*bar*d))
    check(p.evaluate("()=>window.__nb.S.bestWave")>=10 and p.evaluate("()=>window.__nb.retreats")==0,'güçlü oyuncu geri çekilmeden ilerliyor (en iyi dalga %d)'%p.evaluate("()=>window.__nb.S.bestWave"))
    check(not er,'sayfa hatası yok '+'; '.join(er[:2]))
    b.close()
srv.shutdown()
print('BAŞARISIZ: %d'%len(fails) if fails else 'v99 geçti')
sys.exit(1 if fails else 0)
