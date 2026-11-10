"""Kare süresi ve sıcak fonksiyonlar: 2D/3D, çok düşmanlı sahne, telefon boyu.

    python build.py && python tools/perf_olc.py      → kare ms (ort/p95) ve CPU profilinde en pahalı fonksiyonlar
"""
import os, json, threading, functools, http.server, socketserver, collections
from playwright.sync_api import sync_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(R, 'dist')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=DIST)); threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:%d/' % srv.server_address[1]
SEED = "v=>{const nb=window.__nb,S=nb.S;S.tut.done=true;nb.unlockAll();S.tipq=[];S.d3.own=1;S.d3.on=v;S.wave=30;S.bestWave=30;S.slots=['davul','trampet','hihat','bas','gitar','keman',null,null];S.lv={davul:30,trampet:20,hihat:20,bas:20,gitar:15,keman:15};localStorage.setItem('nabiz-cemberi-v3',JSON.stringify(S))}"
MEAS = """()=>new Promise(r=>{const d=[];let l=performance.now(),n=0;function f(t){d.push(t-l);l=t;if(++n<240)requestAnimationFrame(f);else{d.sort((a,b)=>a-b);r({avg:d.reduce((a,b)=>a+b,0)/d.length,p95:d[Math.floor(d.length*0.95)],en:window.__nb.enemies.length})}}requestAnimationFrame(f)})"""
exe = '/opt/pw-browsers/chromium'
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=exe, args=['--autoplay-policy=no-user-gesture-required']) if os.path.exists(exe) else pw.chromium.launch()
    for name, d3, vp, mob in (('masaüstü 2D', 0, {'width': 1366, 'height': 768}, False), ('masaüstü 3D', 1, {'width': 1366, 'height': 768}, False), ('telefon 3D', 1, {'width': 390, 'height': 844}, True)):
        ctx = b.new_context(viewport=vp, is_mobile=mob, has_touch=mob); p = ctx.new_page()
        p.goto(URL); p.wait_for_timeout(400); p.evaluate(SEED, d3); p.reload(); p.wait_for_timeout(500)
        cv = p.locator('#cv').bounding_box(); p.mouse.click(cv['x'] + cv['width'] / 2, cv['y'] + cv['height'] / 2); p.wait_for_timeout(5000)
        cdp = ctx.new_cdp_session(p); cdp.send('Profiler.enable'); cdp.send('Profiler.setSamplingInterval', {'interval': 200}); cdp.send('Profiler.start')
        m = p.evaluate(MEAS)
        prof = cdp.send('Profiler.stop')['profile']
        self_t = collections.Counter(); nodes = {n['id']: n for n in prof['nodes']}
        dt = prof['timeDeltas']
        for sid, d in zip(prof['samples'], dt): self_t[nodes[sid]['callFrame']['functionName'] or '(anon)'] += d
        tot = sum(self_t.values()) or 1
        top = [(k, round(v / tot * 100, 1)) for k, v in self_t.most_common(14) if k not in ('(idle)', '(program)')]
        print('%s: kare ort %.1f ms, p95 %.1f ms, düşman %d' % (name, m['avg'], m['p95'], m['en']))
        print('   en pahalı (öz süre %):', top[:10])
        ctx.close()
    b.close()
srv.shutdown()
