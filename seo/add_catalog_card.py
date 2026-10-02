#!/usr/bin/env python3
# Вставка карточки товара ПЕРВОЙ в сетку catalog-{ru,en,ko}.html
# usage: add_catalog_card.py <slug> [color_override]
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site as b

SLUG = sys.argv[1]
COLOR = sys.argv[2] if len(sys.argv) > 2 else None
ANCHOR = '        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">\n'
ROOT = b.ROOT

products = list(csv.DictReader(open(b.PRODUCTS, encoding="utf-8")))
p = next(x for x in products if x["slug"] == SLUG)

for lang in ["ru", "en", "ko"]:
    fn = os.path.join(ROOT, f"catalog-{lang}.html")
    src = open(fn, encoding="utf-8").read()
    if f"{SLUG}-{lang}.html" in src:
        print(f"[{lang}] уже есть, пропуск"); continue
    card = b.product_card(p, lang, "", b.T[lang])
    if COLOR:
        card = card.replace('data-color=""', f'data-color="{COLOR}"')
    assert ANCHOR in src, f"[{lang}] якорь сетки не найден"
    new = src.replace(ANCHOR, ANCHOR + "            " + card + "\n", 1)
    open(fn, "w", encoding="utf-8").write(new)
    print(f"[{lang}] карточка добавлена первой в сетку")
