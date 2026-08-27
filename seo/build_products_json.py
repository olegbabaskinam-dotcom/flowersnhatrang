#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_products_json.py — ЕДИНЫЙ ИСТОЧНИК товаров для сайта И Telegram-витрины.

Читает seo/products.csv (мастер) + сканирует img/products/<slug>/ (все фото)
→ пишет new-site/products.json.

Категории/цвет считаются ТОЧНО так же, как build_site.py (product_cat/product_color),
чтобы витрина в Telegram и каталог на сайте всегда совпадали.

Добавил товар в products.csv → запусти этот скрипт → products.json обновился.
Ничего на живом сайте не трогает.
"""
import csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)               # .../new-site
CSV  = os.path.join(HERE, "products.csv")
OUT  = os.path.join(ROOT, "products.json")

# ---- цена: "500 000 донгов" -> 500000 ----
def price_num(price):
    return int(re.sub(r"[^\d]", "", price) or "0")

# ---- категории: 1:1 с build_site.py product_cat ----
def product_cats(slug, name_ru):
    s = slug.lower()
    n = (name_ru or "").lower()
    cats = []
    for num in re.findall(r'(\d+)\s*[а-яё-]*\s*роз', n):
        v = int(num)
        c = "r101" if v >= 101 else ("r51" if v == 51 else ("r25" if v == 25 else None))
        if c and c not in cats:
            cats.append(c)
    has_balloons = ("shar" in s) or ("шар" in n)
    has_cake     = s.startswith("tort") or s.startswith("cake") or ("торт" in n) or ("cake" in s)
    is_nabor     = s.startswith("podarochnyy-nabor") or s.startswith("podarok-nabor")
    is_prazdnik  = s.startswith("nabor-prazdnik") or ("prazdnik" in s)
    if has_balloons and "balloons" not in cats: cats.append("balloons")
    if has_cake and "cakes" not in cats:        cats.append("cakes")
    if s == "yarkiy-sbornyy-buket-tort-happy-birthday" and "mixed" not in cats:
        cats.insert(0, "mixed")
    if is_nabor and "nabory" not in cats:       cats.insert(0, "nabory")
    if is_prazdnik and "prazdnik" not in cats:  cats.insert(0, "prazdnik")
    if not cats:
        cats = ["mixed"]
    return cats

# ---- цвет роз: 1:1 с build_site.py product_color ----
def product_color(slug):
    s = slug.lower()
    if s == "151-krasnaya-roza-belaya-upakovka-101-belo-rozovaya-korzina":
        return "red"
    if s.startswith("podarochnyy-nabor") or s.startswith("podarok-nabor") or s.startswith("tort"):
        return ""
    if s.startswith("151-rozovaya-roza-fioletovyy-ottenok"):
        return "pink"
    if s == "151-nezhno-rozovaya-roza-belaya-upakovka":
        return "pink"  # цветы нежно-розовые, «belaya» упаковка не должна давать white
    if "belo-rozov" in s: return "pink"
    if "kras" in s:       return "red"
    if "bel" in s:        return "white"
    if "rozov" in s:      return "pink"
    if "fiolet" in s:     return "purple"
    return ""

# ---- все фото товара: 1.webp главное + 2..40.webp ----
def product_imgs(slug, main_img):
    imgs = [main_img]
    for i in range(2, 41):
        cand = os.path.join(ROOT, "img", "products", slug, f"{i}.webp")
        if os.path.exists(cand):
            imgs.append(f"img/products/{slug}/{i}.webp")
    return imgs

def main():
    if not os.path.exists(CSV):
        print("НЕТ products.csv:", CSV); sys.exit(1)
    items = []
    with open(CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            slug = row["slug"].strip()
            if not slug:
                continue
            items.append({
                "id":        int(row["id"]),
                "slug":      slug,
                "name":      row["name_ru"].strip(),
                "desc":      row["desc_ru"].strip(),
                "alt":       row["alt_ru"].strip(),
                "price_vnd": price_num(row["price"]),
                "price":     row["price"].strip(),        # "500 000 донгов"
                "price_sub": row["price_sub"].strip(),    # "≈ $20 · 1 800 ₽"
                "cats":      product_cats(slug, row["name_ru"]),
                "color":     product_color(slug),
                "images":    product_imgs(slug, row["img"].strip()),
            })
    # витрина-вкладки (порядок = как показываем в боте)
    categories = [
        {"key": "all",      "label": "Все"},
        {"key": "r101",     "label": "101 роза"},
        {"key": "r51",      "label": "51 роза"},
        {"key": "r25",      "label": "25 роз"},
        {"key": "mixed",    "label": "Сборные букеты"},
        {"key": "balloons", "label": "Шары"},
        {"key": "nabory",   "label": "Наборы"},
        {"key": "prazdnik", "label": "Праздничные наборы"},
        {"key": "cakes",    "label": "Торты"},
    ]
    data = {
        "generated": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"),
        "count": len(items),
        "categories": categories,
        "products": items,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    # сводка
    from collections import Counter
    cc = Counter()
    for it in items:
        for c in it["cats"]:
            cc[c] += 1
    print(f"OK → {OUT}")
    print(f"товаров: {len(items)}")
    print("по категориям:", dict(cc))
    multi = sum(1 for it in items if len(it["images"]) > 1)
    print(f"с несколькими фото: {multi}/{len(items)}")

if __name__ == "__main__":
    main()
