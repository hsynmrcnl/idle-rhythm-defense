# Üçüncü taraf lisansları

## Örnek sesler (sf/*.json)
- **FluidR3 GM soundfont** — Frank Wen, MIT lisansı. Kayıtlar WebAudioFont veri paketinden alındı ve `tools/build_sf.py` ile küçük JSON paketlerine dönüştürüldü.
- **WebAudioFont data** — Sergey Surikov, MIT lisansı (https://github.com/surikov/webaudiofontdata).

MIT lisansı: yazılımın kopyalanması, değiştirilmesi, satılması serbesttir; tek koşul telif ve izin notunun kopyalarda kalmasıdır. Bu dosya o notu taşır:

    Copyright (c) 2017 Srgy Surkv (webaudiofontdata)
    FluidR3 GM soundfont, Copyright (c) 2000-2002, 2008 Frank Wen
    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
    documentation files (the "Software"), to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
    and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all copies or substantial portions
    of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

## Yeni kayıt seti (sf/c_*.json) — CC0 / kamu malı
`tools/build_sf_cc0.py` bu kütüphanelerden seçilen notaları kırpıp küçük paketlere dönüştürür. Hepsi CC0 1.0 (kamu malı adanması) ya da Unlicense: kaynak göstermek gerekmez, yine de teşekkür olarak burada duruyor.

| Paket | Kaynak | Lisans |
|---|---|---|
| c_keman, c_harp, c_trompet, c_tuba, c_flut | VSCO 2 Community Edition — Versilian Studios (https://github.com/sgossner/VSCO-2-CE) | CC0 1.0 |
| c_piyano, c_klavsen, c_kalimba, c_didger; c_drums içinde el çırpma, shaker, klave, darbuka, çerçeve davul, gong | Versilian Community Sample Library — Versilian Studios (https://github.com/sgossner/VCSL) | CC0 1.0 |
| c_drums: kick, trampet, hi-hat, tomlar, crash | Virtuosity Drums — Versilian Studios × Karoryfer Samples (https://github.com/sfzinstruments/virtuosity_drums) | CC0 1.0 |
| c_bas | Black And Blue Basses — Karoryfer Samples (https://github.com/sfzinstruments/karoryfer.black-and-blue-basses) | CC0 1.0 |
| c_cello | Karoryfer Samples × Bigcat Instruments Cello (https://github.com/sfzinstruments/karoryfer-bigcat.cello) | CC0 1.0 |
| c_sakso | Weresax — Karoryfer Samples (https://github.com/sfzinstruments/karoryfer.weresax) | CC0 1.0 |
| c_steel | Steel Drum — Jeff Learman (https://github.com/sfzinstruments/jlearman.SteelDrum) | Unlicense |

## Yazı tipleri
Google Fonts üzerinden yüklenir (Unbounded, Instrument Sans, JetBrains Mono, Chakra Petch, Rubik Dirt, Courier Prime, Fraunces, Monoton, Righteous) — hepsi SIL Open Font License.

## Oyunun kendisi
Oyun kodu, verisi ve tasarımı: Hüseyin Mercanlı. Lisans kararı sana ait (örneğin “All rights reserved” ya da MIT); karar verince kök dizine bir `LICENSE` dosyası ekle.
