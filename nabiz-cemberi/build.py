"""Nabız Çemberi derleme: src/ parçalarını tek sayfaya birleştirir, dist/ klasörünü (site + PWA) üretir.

    python build.py            → dist/  (index.html, sw.js, manifest, ikonlar, sf/)  +  build/artifact.html, build/chk.js
    node --check build/chk.js  → söz dizimi kontrolü (CI de yapar)

Parça sırası önemli: her parça aynı kapalı fonksiyonun içine art arda yazılır (p2_data.js açar, p7_canvas.js kapatır).
"""
import os,re,shutil,time,sys
R=os.path.dirname(os.path.abspath(__file__))
SRC=os.path.join(R,'src');DIST=os.path.join(R,'dist');BLD=os.path.join(R,'build')
PARTS=['p1_head.html','p2_data.js','p2b_i18n.js','p3_state.js','p4_audio.js','p4b_sf.js','p5_combat.js','p6_panels.js','p7_canvas.js']
def read(p):
    with open(p,encoding='utf-8') as f:return f.read()
def write(p,s):
    os.makedirs(os.path.dirname(p),exist_ok=True)
    with open(p,'w',encoding='utf-8',newline='\n') as f:f.write(s)
page=''.join(read(os.path.join(SRC,f)) for f in PARTS)
stamp=time.strftime('%Y%m%d-%H%M%S',time.gmtime())
# --- artifact / tek dosya sürümü (iskeletsiz; claude.ai artifact bunu kendi iskeletine sarar)
write(os.path.join(BLD,'artifact.html'),page)
write(os.path.join(BLD,'chk.js'),re.search(r'<script>(.*)</script>',page,re.S).group(1))
# --- site (dist/): PWA başlığı + sayfa + service worker kaydı
head='''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#07060f">
<meta name="description" content="Nabız Çemberi: ritimlerle kendi müziğini yap, döngün Sessizlik A.Ş.'ye karşı sahneyi savunsun. Idle rhythm defense.">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="mobile-web-app-capable" content="yes">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-192.png">
<style>html,body{margin:0}[hidden]{display:none!important}img{max-width:100%}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>
</head>
<body>
'''
tail='''
<script>if('serviceWorker' in navigator&&location.protocol!=='file:'){window.addEventListener('load',()=>{navigator.serviceWorker.register('sw.js').catch(()=>{})})}</script>
</body>
</html>
'''
if os.path.isdir(DIST):shutil.rmtree(DIST)
os.makedirs(DIST)
write(os.path.join(DIST,'index.html'),head+page+tail)
write(os.path.join(DIST,'manifest.webmanifest'),'''{
  "name": "Nabız Çemberi",
  "short_name": "Nabız",
  "description": "Idle rhythm defense: ritimlerle kendi müziğini yap, döngün sahneyi savunsun.",
  "start_url": "./index.html",
  "scope": "./",
  "display": "standalone",
  "orientation": "any",
  "background_color": "#07060f",
  "theme_color": "#07060f",
  "lang": "tr",
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
  ]
}
''')
write(os.path.join(DIST,'sw.js'),'''/* Nabız Çemberi service worker. Kabuk: ağ önce, yoksa önbellek (her derleme yeni kabuk). Örnek sesler ve yazı tipleri: önbellek önce. */
const SHELL='nabiz-shell-'''+stamp+'''',DATA='nabiz-data-v2';
const FILES=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(SHELL).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==SHELL&&k!==DATA).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET')return;
 if(u.origin===location.origin&&/\\/sf\\/.+\\.json$/.test(u.pathname)||/fonts\\.(googleapis|gstatic)\\.com/.test(u.href)){e.respondWith(caches.open(DATA).then(async c=>{const hit=await c.match(e.request);if(hit)return hit;try{const res=await fetch(e.request);if(res&&(res.ok||res.type==='opaque'))c.put(e.request,res.clone());return res}catch(err){return hit||Response.error()}}));return}
 if(u.origin===location.origin){e.respondWith(fetch(e.request).then(res=>{if(res&&res.ok)caches.open(SHELL).then(c=>c.put(e.request,res.clone()));return res}).catch(()=>caches.match(e.request).then(r=>r||caches.match('./index.html'))))}
});
''')
for f in ['icon-192.png','icon-512.png']:shutil.copy(os.path.join(R,'assets',f),os.path.join(DIST,f))
shutil.copytree(os.path.join(R,'sf'),os.path.join(DIST,'sf'))
write(os.path.join(DIST,'.nojekyll'),'')
n=sum(os.path.getsize(os.path.join(dp,f)) for dp,_,fs in os.walk(DIST) for f in fs)
print('dist/ hazır · %d dosya · %.1f MB · kabuk %s'%(sum(len(fs) for _,_,fs in os.walk(DIST)),n/1e6,stamp))
if '--zip' in sys.argv:  # itch.io / Netlify için tek zip: python build.py --zip
    import zipfile
    zp=os.path.join(R,'nabiz-cemberi-site.zip')
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
        for dp,_,fs in os.walk(DIST):
            for f in fs:z.write(os.path.join(dp,f),os.path.relpath(os.path.join(dp,f),DIST))
    print('zip:',zp,'%.1f MB'%(os.path.getsize(zp)/1e6))
