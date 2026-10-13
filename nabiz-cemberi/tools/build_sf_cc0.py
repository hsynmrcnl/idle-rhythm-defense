"""CC0 örnek ses paketleri: VSCO 2 CE, VCSL ve sfzinstruments kütüphanelerinden sf/c_*.json üretir.

    python tools/build_sf_cc0.py            → hepsi
    python tools/build_sf_cc0.py c_keman    → yalnız biri

Gerekenler: git, curl, ffmpeg (libmp3lame), numpy. Kaynak depolar ses dosyası indirmeden klonlanır
(git --filter=blob:none), örnekler raw.githubusercontent.com'dan tek tek iner; ikisi de tools/.cache/ altında tutulur.
Paket biçimi FluidR3 paketleriyle aynı (nbsf1): bölge = tuş aralığı + kök perde (cent) + loop + rms (ilk 0,5 sn) + pk + mp3.
Bazı kütüphaneler oktavı farklı numaralar (orta Do = C3); 'oct' bunu düzeltir, perdeler ölçülerek doğrulandı (iki yöntem: en alçak güçlü
kısmi + YIN). 'drop': iki yöntemde de etiketiyle uyuşmayan örnekler (kalimba 75, 83; steel 78). Timpani perdesi güvenilir ölçülemediği için
timbal klasik (FluidR3) pakette kalır.
"""
import os, re, sys, json, base64, subprocess, urllib.parse, functools
import numpy as np

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFD = os.path.join(R, 'sf')
CACHE = os.environ.get('NB_SRC_CACHE') or os.path.join(R, 'tools', '.cache')
os.makedirs(os.path.join(CACHE, 'files'), exist_ok=True)
SR = 44100

REPOS = {  # yerel ad: (GitHub deposu, dal, lisans)
    'vsco': ('sgossner/VSCO-2-CE', 'master', 'CC0'),
    'vcsl': ('sgossner/VCSL', 'master', 'CC0'),
    'virtuosity_drums': ('sfzinstruments/virtuosity_drums', 'master', 'CC0'),
    'karoryfer.black-and-blue-basses': ('sfzinstruments/karoryfer.black-and-blue-basses', 'main', 'CC0'),
    'karoryfer-bigcat.cello': ('sfzinstruments/karoryfer-bigcat.cello', 'master', 'CC0'),
    'karoryfer.weresax': ('sfzinstruments/karoryfer.weresax', 'master', 'CC0'),
    'jlearman.SteelDrum': ('sfzinstruments/jlearman.SteelDrum', 'main', 'Unlicense'),
}

@functools.lru_cache(None)
def tree(local):
    d = os.path.join(CACHE, local)
    if not os.path.isdir(os.path.join(d, '.git')):
        subprocess.run(['git', '-c', 'gc.auto=0', 'clone', '-q', '--filter=blob:none', '--no-checkout', '--depth', '1',
                        'https://github.com/' + REPOS[local][0], d], check=True, env=dict(os.environ, GIT_LFS_SKIP_SMUDGE='1'))
    return subprocess.run(['git', '-C', d, 'ls-tree', '-r', '--name-only', 'HEAD'], capture_output=True, text=True, check=True).stdout.splitlines()

def fetch(local, path):
    repo, br, _ = REPOS[local]
    dst = os.path.join(CACHE, 'files', re.sub(r'[^A-Za-z0-9._-]', '_', repo + '_' + path))
    if not os.path.exists(dst):
        subprocess.run(['curl', '-sSfL', '--retry', '3', '-o', dst, 'https://raw.githubusercontent.com/%s/%s/%s' % (repo, br, urllib.parse.quote(path))], check=True)
    return dst

def decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()

NOTE = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
def midi_of(tok):
    m = re.fullmatch(r'([A-Ga-g])(#|b)?(-?\d)', tok)
    if not m: return None
    return 12 * (int(m.group(3)) + 1) + NOTE[m.group(1).lower()] + (1 if m.group(2) == '#' else -1 if m.group(2) == 'b' else 0)

def files(local, inc):
    rx = re.compile(inc); out = [p for p in tree(local) if rx.search(p)]
    assert out, (local, inc)
    return sorted(out)

def onset_trim(x, pre=0.003):
    """baştaki sessizliği at: tepe değerin %2'sini ilk geçen yerden 3 ms önce başla"""
    thr = 0.02 * np.max(np.abs(x)); i = int(np.argmax(np.abs(x) > thr))
    return x[max(0, i - int(pre * SR)):]

def low_peak(x, thr=0.12):
    x = x * np.hanning(len(x)); n = 1 << 17; X = np.abs(np.fft.rfft(x, n)); fr = np.fft.rfftfreq(n, 1 / SR)
    X[fr < 25] = 0; X[fr > 4000] = 0; mx = X.max()
    for i in range(2, len(X) - 2):
        if X[i] > thr * mx and X[i] >= X[i - 1] and X[i] >= X[i + 1]: return fr[i]

def shape(x, length, sustain, loop=None):
    """uzunluğa kırp, tutulan seslerde ortadaki bölgeye çapraz geçişli loop yerleştir, sonu yumuşat"""
    x = onset_trim(x)
    n = min(len(x), int(length * SR)); x = x[:n].copy()
    ls = le = 0
    if sustain and loop and n > int(loop[1] * SR):
        ls, le = int(loop[0] * SR), int(loop[1] * SR)
        # sıfır geçişlerine hizala
        def zc(i):
            w = x[i - 400:i + 400]; z = np.where(np.diff(np.signbit(w)))[0]
            return i - 400 + int(z[np.argmin(np.abs(z - 400))]) if len(z) else i
        ls, le = zc(ls), zc(le)
        N = min(int(0.12 * SR), (le - ls) // 3)
        w = np.linspace(0, 1, N)
        x[le - N:le] = x[le - N:le] * np.sqrt(1 - w) + x[ls - N:ls] * np.sqrt(w)   # loop sonu, loop başının öncesine akar
        x = x[:le + int(0.02 * SR)]
    else:
        f = min(len(x), int(0.08 * SR)); x[-f:] *= np.linspace(1, 0, f) ** 2
    x = x / max(1e-6, np.max(np.abs(x))) * 0.98
    return x, ls, le

def mp3(x):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '96k', '-f', 'mp3', '-'],
                       input=x.astype(np.float32).tobytes(), capture_output=True, check=True)
    return base64.b64encode(p.stdout).decode()

def zone(x, root, lo, hi, ls=0, le=0):
    return dict(lo=int(lo), hi=int(hi), pitch=int(round(root * 100)), loopStart=int(ls), loopEnd=int(le), sr=SR, coarse=0, fine=0,
                rms=round(float(np.sqrt(np.mean(x[:int(0.5 * SR)] ** 2))), 4), pk=round(float(np.max(np.abs(x))), 3), mp3=mp3(x))

def spread(roots):
    """her kök komşularıyla arasındaki yarıya kadar çalar; uçlar 0 ve 127'ye uzar"""
    out = []
    for i, r in enumerate(roots):
        lo = 0 if i == 0 else (roots[i - 1] + r) // 2 + 1
        hi = 127 if i == len(roots) - 1 else (r + roots[i + 1]) // 2
        out.append((r, lo, hi))
    return out

# ---------- notalı paketler ----------
NOTE_RX = r'_([A-G]#?\d)_'
PITCHED = {
 'c_piyano':  dict(name='Piyano · Steinway B (VCSL, CC0)', src='vcsl', inc=r'Grand Piano, Steinway B/NoSus/JHPiano_NoSus_Close_[A-G]#?\d_vl3_rr1\.wav$', note=NOTE_RX, oct=0, rng=(28, 100), step=4, length=3.2),
 'c_klavsen': dict(name='Klavsen · Fransız (VCSL, CC0)', src='vcsl', inc=r'Harpsichord, French/Sustains/Harpsi2_Normal_[A-G]#?\d_rr1_Main\.wav$', note=NOTE_RX, oct=12, rng=(36, 96), step=3, length=1.8),
 'c_keman':   dict(name='Keman · solo, vibrato (VSCO 2 CE, CC0)', src='vsco', inc=r'Solo Violin/.*LLVln_ArcoVib_[A-G]#?\d_f\.wav$', note=NOTE_RX, oct=0, rng=(55, 100), step=3, length=2.8, sustain=True),
 'c_cello':   dict(name='Çello · Karoryfer × Bigcat (CC0)', src='karoryfer-bigcat.cello', inc=r'Samples/sus/[A-G]#?\d_mf_d\.wav$', note=r'^([A-G]#?\d)_', oct=12, rng=(36, 80), step=1, length=2.8, sustain=True),
 'c_harp':    dict(name='Arp · konser (VSCO 2 CE, CC0)', src='vsco', inc=r'Strings/Harp/KSHarp_[A-G]#?\d_mf\.wav$', note=NOTE_RX, oct=0, rng=(24, 100), step=1, length=2.8),
 'c_bas':     dict(name='Bas gitar · Black And Blue Basses (Karoryfer, CC0)', src='karoryfer.black-and-blue-basses', inc=r'Samples/darkblack/reg/darkblack_[a-g]#?\d_f_rr1\.wav$', note=r'darkblack_([a-g]#?\d)_', oct=-12, rng=(28, 64), step=3, length=1.8),
 'c_trompet': dict(name='Trompet · vibrato (VSCO 2 CE, CC0)', src='vsco', inc=r'Trumpet/susvib/Sum_SHTrumpet_susvib_[A-G]#?\d_v2_rr1\.wav$', note=NOTE_RX, oct=12, rng=(50, 88), step=1, length=2.6, sustain=True),
 'c_tuba':    dict(name='Tuba (VSCO 2 CE, CC0)', src='vsco', inc=r'Tuba/sus/Tuba\d_sus_[A-G]#?\d_v2_rr1_Mid\.wav$', note=NOTE_RX, oct=12, rng=(24, 64), step=1, length=2.6, sustain=True),
 'c_flut':    dict(name='Flüt · vibrato (VSCO 2 CE, CC0)', src='vsco', inc=r'Flute/expvib/LDFlute_expvib_[A-G]#?\d_v1_1\.wav$', note=NOTE_RX, oct=12, rng=(58, 100), step=1, length=2.6, sustain=True),
 'c_sakso':   dict(name='Alto saksafon · Weresax (Karoryfer, CC0)', src='karoryfer.weresax', inc=r'Samples/alto/[a-g]#?\d_f_rr1_cnd\.wav$', note=r'^([a-g]#?\d)_', oct=12, rng=(48, 84), step=3, length=2.6, sustain=True),
 'c_kalimba': dict(name='Kalimba · Kenya (VCSL, CC0)', src='vcsl', inc=r'Kalimba, Kenya/.*_vl3_rr2\.wav$', note=NOTE_RX, oct=12, rng=(40, 90), step=1, length=1.6, drop=(75, 83)),
 'c_steel':   dict(name='Steel drum · tenor (Jeff Learman, Unlicense)', src='jlearman.SteelDrum', inc=r'flac/SteelDrum_\d+_+[A-G]b?\d_4\.flac$', note=r'_([A-G]b?\d)_4\.flac', oct=0, rng=(60, 96), step=3, length=2.0, drop=(78,)),
}
SUS_LOOP = (1.1, 2.3)  # tutulan seslerde loop bölgesi (sn, ataktan sonra)

def build_pitched(key, c):
    roots = {}
    for p in files(c['src'], c['inc']):
        m = re.search(c['note'], os.path.basename(p)); r = midi_of(m.group(1)) if m else None
        if r is None: continue
        r += c['oct']
        if c['rng'][0] <= r <= c['rng'][1] and r not in c.get('drop', ()): roots.setdefault(r, p)
    keep = []
    for r in sorted(roots):  # en az 'step' yarım ses arayla
        if not keep or r - keep[-1] >= c['step']: keep.append(r)
    zones = []
    for r, lo, hi in spread(keep):
        x, ls, le = shape(decode(fetch(c['src'], roots[r])), c['length'], c.get('sustain'), SUS_LOOP)
        zones.append(zone(x, r, lo, hi, ls, le))
    return zones

# ---------- tek örnekli notalı paketler (perde ölçülür) ----------
def build_measured(src, paths, length, sustain, rng):
    out = []
    for p in paths:
        x = decode(fetch(src, p)); f = low_peak(onset_trim(x)[int(0.15 * SR):int(0.9 * SR)])
        r = 69 + 12 * np.log2(f / 440)
        assert rng[0] <= r <= rng[1], (p, r)
        out.append((r, p))
    out.sort(); roots = [round(r) for r, _ in out]
    zones = []
    for (r, p), (_, lo, hi) in zip(out, spread(roots)):
        x, ls, le = shape(decode(fetch(src, p)), length, sustain, (1.0, 3.0))
        zones.append(zone(x, r, lo, hi, ls, le))
    return zones

# ---------- davul seti: GM davul notalarına ----------
def hit(src, inc, length=1.5, mix=None):
    x = decode(fetch(src, files(src, inc)[0]))
    if mix:
        y = decode(fetch(mix[0], files(mix[0], mix[1])[0])); n = max(len(x), len(y))
        x = np.pad(x, (0, n - len(x))) * mix[2] + np.pad(y, (0, n - len(y))) * mix[3]
    x, _, _ = shape(x, length, False)
    return x

V = 'virtuosity_drums'
DRUMS = {  # GM notası: (kaynak, desen, uzunluk, karışım)
    36: (V, r'kickmic/kick/kickmic_kick_snoff_vl3_rr1\.flac$', 0.9, (V, r'mid/kick/mid_kick_snoff_vl3_rr1\.flac$', 0.8, 0.5)),
    38: (V, r'snaremic/snare/snaremic_snare_center_vl14\.flac$', 0.9, (V, r'mid/snare/mid_snare_center_vl14\.flac$', 0.8, 0.5)),
    42: (V, r'mid/hh/mid_hh_closed_vl3_rr1\.flac$', 0.5, None),
    46: (V, r'mid/hh/mid_hh_open_vl3_rr1\.flac$', 1.4, None),
    45: (V, r'mid/ltom/mid_ltom_center_vl12\.flac$', 1.4, None),
    47: (V, r'mid/htom/mid_htom_center_vl12\.flac$', 1.2, None),
    49: (V, r'mid/crash/mid_crash_crash_vl2_rr1\.flac$', 2.8, None),
    39: ('vcsl', r'Claps/Clap_rr1\.wav$', 0.6, None),
    70: ('vcsl', r'Shaker, Small/.*\.wav$', 0.5, None),
    75: ('vcsl', r'Claves/Claves1_Hit_v2_rr1_Mid\.wav$', 0.5, None),
    61: ('vcsl', r'Darbuka/Darbuka_1_hit_vl2_rr1\.wav$', 1.0, None),   # düm
    60: ('vcsl', r'Darbuka/Darbuka_3_hit_vl2_rr1\.wav$', 0.6, None),   # tek
    41: ('vcsl', r'Frame Drum/HDrumL_Hit_v3_rr1_Sum\.wav$', 1.4, None),  # bendir
    52: ('vcsl', r'Gong 1/gong_f\.wav$', 4.0, None),
}

def build_drums():
    zones = []
    for n, (src, inc, length, mix) in sorted(DRUMS.items()):
        x = hit(src, inc, length, mix and (mix[0], mix[1], mix[2], mix[3]))
        zones.append(zone(x, n, n, n))
    return zones

PACKS = dict(PITCHED)
EXTRA = {
    'c_didger': ('Didgeridoo (VCSL, CC0)', lambda: build_measured('vcsl', files('vcsl', r'Didgeridoo/Didgeridoo1_Sus2_Main\.wav$'), 4.2, True, (30, 52))),
    'c_drums': ('Davul seti · Virtuosity Drums + VCSL (CC0)', build_drums),
}

def write(key, name, zones):
    h = dict(id=key, name=name, fmt='nbsf1', zones=zones)
    s = json.dumps(h, separators=(',', ':'))
    open(os.path.join(SFD, key + '.json'), 'w').write(s)
    idx_p = os.path.join(SFD, 'index.json'); idx = json.load(open(idx_p))
    idx[key] = dict(name=name, bytes=len(s), zones=len(zones), all=len(zones))
    json.dump(idx, open(idx_p, 'w'), ensure_ascii=False, separators=(',', ':'))
    print('%-10s %2d bölge  %4d KB  %s' % (key, len(zones), len(s) // 1024, name), flush=True)

if __name__ == '__main__':
    only = set(sys.argv[1:])
    for k, c in PITCHED.items():
        if not only or k in only: write(k, c['name'], build_pitched(k, c))
    for k, (name, fn) in EXTRA.items():
        if not only or k in only: write(k, name, fn())
