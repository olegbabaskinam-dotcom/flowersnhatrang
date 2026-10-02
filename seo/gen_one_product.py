#!/usr/bin/env python3
# Генерация 3 страниц товара для ОДНОГО товара (slug из argv[1]) + подмена живых блоков.
import sys, os, html, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site as b

SLUG = sys.argv[1]
LANGS = ["ru", "en", "ko"]

products = list(csv.DictReader(open(b.PRODUCTS, encoding="utf-8")))
p = next(x for x in products if x["slug"] == SLUG)

GEN_ARROW = ".pcard-arrow{position:absolute;top:50%;transform:translateY(-50%);background:rgba(255,255,255,.9);border:none;width:2rem;height:2rem;border-radius:999px;font-size:1.2rem;line-height:1;color:#a8566a;cursor:pointer;display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity .2s;z-index:2;box-shadow:0 1px 4px rgba(0,0,0,.12);}"
LIVE_ARROW = ".pcard-arrow{position:absolute;top:50%;transform:translateY(-50%);background:rgba(255,255,255,.96);border:none;width:2.5rem;height:2.5rem;border-radius:999px;font-size:1.6rem;line-height:1;color:#a8566a;cursor:pointer;display:flex;align-items:center;justify-content:center;opacity:1;transition:opacity .2s,background .2s,transform .15s;z-index:5;box-shadow:0 2px 8px rgba(0,0,0,.22);}"

CSS_REPL = [
    (".pcard-slide.active{opacity:1;}\n",
     ".pcard-slide.active{opacity:1;}\n        .gallery-slider{height:24rem;}\n        @media(min-width:768px){.gallery-slider{height:30rem;}}\n        .gallery-slider .pcard-slide{object-fit:contain;padding:.75rem;}\n"),
    (GEN_ARROW, LIVE_ARROW),
    (".pcard-slider:hover .pcard-arrow{opacity:1;}", ".pcard-arrow:hover{opacity:1;background:#fff;}"),
    (".pcard-dots{position:absolute;bottom:.55rem;left:0;right:0;display:flex;gap:.3rem;justify-content:center;z-index:2;}",
     ".pcard-dots{position:absolute;bottom:.55rem;left:0;right:0;display:flex;gap:.3rem;justify-content:center;z-index:3;}"),
    (".pcard-dot{width:.4rem;height:.4rem;border-radius:999px;background:rgba(255,255,255,.55);transition:background .2s;}",
     ".pcard-dot{width:.45rem;height:.45rem;border-radius:999px;background:rgba(255,255,255,.6);box-shadow:0 0 2px rgba(0,0,0,.3);transition:background .2s;}"),
    ("        @media (max-width:767px){.pcard-arrow{opacity:1;}}\n", ""),
    (".filt-group{display:flex;gap:.5rem;flex-wrap:wrap;justify-content:center;}",
     ".filt-group{display:flex;gap:.5rem;flex-wrap:wrap;justify-content:center;}\n        .filt-group.color-hidden{display:none;}"),
]

def live_gallery(p, base, alt):
    imgs = b.product_imgs(p)
    slides = "".join(
        f'<img src="{base}{im}" alt="{html.escape(alt)} {i+1}" loading="{"eager" if i==0 else "lazy"}" class="pcard-slide{" active" if i==0 else ""}">'
        for i, im in enumerate(imgs))
    dots = "".join(f'<span class="pcard-dot{" active" if i==0 else ""}"></span>' for i in range(len(imgs)))
    return (f'<div class="pcard-slider gallery-slider rounded-2xl border border-stone-100">\n'
            f'            {slides}\n'
            f'            <button type="button" class="pcard-arrow pcard-prev" aria-label="prev">‹</button>'
            f'<button type="button" class="pcard-arrow pcard-next" aria-label="next">›</button>'
            f'<div class="pcard-dots">{dots}</div>\n'
            f'        </div>')

for lang in LANGS:
    alt = p[f"alt_{lang}"]
    h = b.render_product(p, lang, products)
    for a, c in CSS_REPL:
        assert a in h, f"[{lang}] CSS-фрагмент не найден: {a[:40]}"
        h = h.replace(a, c)
    gen_g = b.gallery(p, "../", alt)
    assert gen_g in h, f"[{lang}] gallery-блок генератора не найден"
    h = h.replace(gen_g, live_gallery(p, "../", alt))
    out = os.path.join(b.CATALOG_DIR, f"{SLUG}-{lang}.html")
    open(out, "w", encoding="utf-8").write(h)
    print("written:", os.path.basename(out), "| gallery-slides:", h.count('gallery-slider'))
print("done")
