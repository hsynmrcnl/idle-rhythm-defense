#!/usr/bin/env bash
# guncelle.sh — oyun testçisi skill'ini ortak depodan (hsynmrcnl/play-test) bu oyunun deposuna kopyalar ya da yeniler.
# Oyunun deposunun kökünden koş:  bash .claude/skills/oyun-testcisi/guncelle.sh
# İlk kurulumda (klasör yokken):  git clone --depth 1 https://github.com/hsynmrcnl/play-test.git /tmp/play-test && bash /tmp/play-test/guncelle.sh
# Yalnız skill dosyalarını yazar (SKILL.md, personalar.md, surucu.js, guncelle.sh); oyunun PROFİLİNE (oyun-profil.js) dokunmaz.
# Bulut oturumunda depo özelse önce oturuma eklenmeli (add_repo hsynmrcnl/play-test).
set -euo pipefail
KAYNAK="${OT_KAYNAK:-https://github.com/hsynmrcnl/play-test.git}"
HEDEF="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.claude/skills/oyun-testcisi"
GEC="$(mktemp -d)"; trap 'rm -rf "$GEC"' EXIT
git clone -q --depth 1 "$KAYNAK" "$GEC/ot"
mkdir -p "$HEDEF"
for f in SKILL.md personalar.md surucu.js guncelle.sh; do cp "$GEC/ot/$f" "$HEDEF/$f"; done
echo "oyun-testcisi: $(git -C "$GEC/ot" log -1 --format='%h %ad' --date=short) → $HEDEF"
echo "Profil yoksa: README'deki 'Yeni oyuna ekleme' adımları (örnek: ornek-profil.js)."
