"""tests/ içindeki bütün *_test.py dosyalarını çalıştırır; varsayılan 3 paralel süreç, çıktılar sırayla yazılır.

    python build.py && python tests/run_all.py          # paralel (NB_JOBS=3)
    NB_JOBS=1 python tests/run_all.py                   # sırayla (eski davranış)
    python tests/run_all.py v41 v44                     # yalnız adında bunlar geçen testler

Zamanlamaya duyarlı test (mobile_ui: ses saatiyle ölçü sayar) yükten etkilenmesin diye en sonda tek başına koşar.
"""
import os, sys, glob, subprocess, time
from concurrent.futures import ThreadPoolExecutor

here = os.path.dirname(os.path.abspath(__file__))
files = sorted(glob.glob(os.path.join(here, '*_test.py')))
if len(sys.argv) > 1:
    files = [f for f in files if any(a in os.path.basename(f) for a in sys.argv[1:])]
SOLO = {'mobile_ui_test.py'}
jobs = max(1, int(os.environ.get('NB_JOBS', '3')))

def run(f):
    t0 = time.time()
    p = subprocess.run([sys.executable, f], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return os.path.basename(f), p.returncode, p.stdout, time.time() - t0

par = [f for f in files if os.path.basename(f) not in SOLO]
solo = [f for f in files if os.path.basename(f) in SOLO]
bad, t0 = [], time.time()
with ThreadPoolExecutor(max_workers=jobs) as ex:
    results = list(ex.map(run, par))
results += [run(f) for f in solo]
for name, code, out, dt in results:
    print('== %s (%.0f sn)' % (name, dt), flush=True)
    print(out, end='' if out.endswith('\n') else '\n', flush=True)
    if code != 0:
        bad.append(name)
print('süre: %.0f sn' % (time.time() - t0))
print('BAŞARISIZ: ' + ', '.join(bad) if bad else 'bütün takımlar geçti')
sys.exit(1 if bad else 0)
