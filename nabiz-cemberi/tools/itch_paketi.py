"""itch.io paketi: oyunu tek klasöre indirger, oyun kodunu terser ile küçültüp okunmaz yapar,
service worker / PWA kaydını çıkarır (itch iframe'inde gerekmez), sf/ ve ikonları kopyalar, zip'ler.

NOT: Tarayıcı oyununun kodu istemciye iner; TAM kopyalanamaz yapılamaz. Bu paket kodu küçültüp
değişken adlarını bozarak okumayı/çalmayı ciddi biçimde zorlaştırır. itch.io'da yüklerken oyunu
"Kickstarter/HTML - play in browser" seç, "This file will be played in the browser" işaretle ve
indirme SUNMA (yalnız oyna). Böylece dosya indirilmez, kaynak yalnız geliştirici araçlarıyla ve
okunmaz hâliyle görülebilir.

    python build.py && python tools/itch_paketi.py
    → build/nabiz-cemberi-itch.zip  (içinde index.html en üstte)
"""
import os, re, subprocess, shutil, sys, zipfile, json
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(R, 'dist'); OUT = os.path.join(R, 'dist_itch'); BLD = os.path.join(R, 'build')
subprocess.run([sys.executable, os.path.join(R, 'build.py')], check=True, cwd=R, stdout=subprocess.DEVNULL)
html = open(os.path.join(DIST, 'index.html'), encoding='utf-8').read()

scripts = re.findall(r'<script>(.*?)</script>', html, re.S)
assert scripts, 'script bulunamadı'
game = scripts[0]
nin = len(game)
# terser ile küçült + değişken adlarını boz (üst düzey değişkenler korunur; IIFE içi hepsi mangle)
terser = os.path.join(R, 'node_modules', '.bin', 'terser')
gin = os.path.join(BLD, 'game_in.js'); open(gin, 'w', encoding='utf-8').write(game)
proc = subprocess.run([terser, gin, '--compress', 'passes=2', '--mangle',
                       '--format', 'ascii_only=true,comments=false'],
                      capture_output=True, text=True)
if proc.returncode != 0:
    print('terser hata:\n' + proc.stderr[-2000:]); sys.exit(1)
mini = proc.stdout.strip()
# söz dizimi kontrolü
chk = os.path.join(BLD, 'chk_itch.js'); open(chk, 'w').write(mini)
subprocess.run(['node', '--check', chk], check=True)

# HTML'i yeniden kur: oyun scripti küçültülmüş, sw/manifest çıkarıldı
def css_min(m):
    css = m.group(1)
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)      # yorumları at
    css = re.sub(r'\s+', ' ', css)                        # boşlukları daralt
    css = re.sub(r'\s*([{}:;,>])\s*', r'\1', css)
    return '<style>' + css.strip() + '</style>'
page = re.sub(r'<style>(.*?)</style>', css_min, html, flags=re.S)
page = page.replace('<script>' + game + '</script>', '<script>' + mini + '</script>')
# itch iframe: service worker + PWA manifest gereksiz (ve iframe'de kayıt çalışmaz)
page = re.sub(r'<script>if\(.*?serviceWorker.*?</script>', '', page, flags=re.S)
page = re.sub(r'<link rel="manifest"[^>]*>\n?', '', page)
page = re.sub(r'<!--.*?-->', '', page, flags=re.S)       # HTML yorumları
banner = '<!-- Nabız Çemberi · © Hüseyin · tüm hakları saklıdır · izinsiz kopyalanamaz / dağıtılamaz -->\n'
page = page.replace('<!doctype html>', '<!doctype html>\n' + banner, 1)

if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)
shutil.copytree(os.path.join(R, 'sf'), os.path.join(OUT, 'sf'))
for f in ('icon-192.png', 'icon-512.png'):
    shutil.copy(os.path.join(R, 'assets', f), os.path.join(OUT, f))

zpath = os.path.join(BLD, 'nabiz-cemberi-itch.zip')
with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for root, _, files in os.walk(OUT):
        for fn in files:
            fp = os.path.join(root, fn)
            z.write(fp, os.path.relpath(fp, OUT))   # index.html en üstte
total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs)
print('oyun kodu: %d → %d bayt (%%%d)' % (nin, len(mini), 100 - round(100 * len(mini) / nin)))
print('paket: %s · %.1f MB (%d dosya)' % (zpath, os.path.getsize(zpath) / 1e6, len(os.listdir(OUT)) + len(os.listdir(os.path.join(OUT, 'sf')))))
print('index.html: %.0f KB' % (os.path.getsize(os.path.join(OUT, 'index.html')) / 1024))
