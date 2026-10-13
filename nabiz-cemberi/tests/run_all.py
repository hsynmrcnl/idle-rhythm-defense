"""tests/ içindeki bütün *_test.py dosyalarını sırayla çalıştırır.

    python build.py && python tests/run_all.py
"""
import os, sys, glob, subprocess

here = os.path.dirname(os.path.abspath(__file__))
bad = []
for f in sorted(glob.glob(os.path.join(here, '*_test.py'))):
    name = os.path.basename(f)
    print('== ' + name, flush=True)
    if subprocess.call([sys.executable, f]) != 0:
        bad.append(name)
print('BAŞARISIZ: ' + ', '.join(bad) if bad else 'bütün takımlar geçti')
sys.exit(1 if bad else 0)
