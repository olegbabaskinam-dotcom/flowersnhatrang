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
    if s == "svyazka-9-rozovo-krasnyh-serdec-25-rozovyh-roz" and "balloons" not in cats: cats.append("balloons")  # id167
    if has_cake and "cakes" not in cats:        cats.append("cakes")
    if s == "yarkiy-sbornyy-buket-tort-happy-birthday" and "mixed" not in cats:
        cats.insert(0, "mixed")
    if s == "yarkaya-sbornaya-korzina-15-rozovyh-sharov" and "mixed" not in cats:
        cats.insert(0, "mixed")  # id142: сборная корзина + шары = комбо
    if s in ("prazdnichnyy-sbornyy-buket-i-shokoladnyy-tort", "sbornyy-buket-belaya-upakovka-7-sharov") and "mixed" not in cats:
        cats.insert(0, "mixed")  # 01.10: id69/id104 — в составе сборный букет (аудит матрицы)
    if s == "25-belyh-roz-pirozhnoe-otkrytka" and "cakes" not in cats:
        cats.append("cakes")  # 01.10: id188 — пирожное = раздел Торты (аудит матрицы)
    if s in ("yarkaya-sbornaya-korzina-nabor-sharov-l-cifry-29", "stilnaya-sbornaya-korzina-101-rozovaya-25-rozovaya-eustoma", "sbornyy-buket-51-belaya-roza-evkalipt-eustomy-25-rozovyh-roz-tort") and "mixed" not in cats:
        cats.insert(0, "mixed")  # id157/id160: сборная корзина в комбо
    # 22.10.2026 (Олег): несколько букетов в одном товаре = КОМБО. В разделах 25/51/101 — только одиночные букеты,
    # всё составное — только в «Комбо-наборах» (иначе люди путаются). 'multi' = несколько букетов одной категории.
    if "сборн" in n and any(c in cats for c in ("r25", "r51", "r101")) and "mixed" not in cats:
        cats.insert(0, "mixed")
    if len(re.findall(r'(\d+)\s*[а-яё-]*\s*роз', n)) >= 2 and len(cats) == 1:
        cats.append("multi")
    if is_nabor and "nabory" not in cats:       cats.insert(0, "nabory")
    if is_prazdnik and "prazdnik" not in cats:  cats.insert(0, "prazdnik")
    if not cats:
        cats = ["mixed"]
    return cats

# ---- цвет роз: 1:1 с build_site.py product_color ----
NEW_BALLOONS_223 = ("nabor-sharov-s-rozovye-zvezdy-golubye-serdca", "nabor-sharov-l-raduzhnye-cifry-30-15-rozovyh", "nabor-sharov-l-serebryanye-cifry-39-serdca", "svyazka-15-rezinovyh-sharov-rozovye-belye-serebryanye", "nabor-sharov-s-sirenevo-goluboy-happy-birthday", "svyazka-15-hromirovannyh-rezinovyh-sharov-rozovoe-zoloto", "nabor-sharov-s-happy-birthday-7-serebristo-bezhevyh", "nabor-sharov-s-7-rozovo-bezhevyh-sharov", "svyazka-9-rozovo-krasnyh-serdec", "nabor-sharov-s-zolotye-cifry-45", "nabor-sharov-s-rozovye-i-malinovye-zvezdy", "nabor-sharov-l-zolotye-cifry-40-sinie-zolotye", "nabor-sharov-m-bezhevye-cifry-22", "svyazka-belyh-rezinovyh-sharov-zhemchuzhnye-serdca", "nabor-sharov-s-7-rozovyh-serdec-i-zvezd", "nabor-sharov-l-zolotye-cifry-52-serdca")
def product_color(slug):
    s = slug.lower()
    if s in NEW_BALLOONS_223:
        return ""  # id223–id242: наборы шаров — фильтра цвета роз нет
    if s in ("101-rozovaya-roza-belaya-upakovka-plastikovaya-tara",
             "25-nezhno-rozovaya-roza-belaya-upakovka-otkrytka"):
        return "pink"  # id145/id146: розы розовые, «belaya» упаковка не должна давать white
    if s in ("51-rozovaya-roza-belaya-upakovka-shokoladnyy-tort-dollary", "51-rozovaya-roza-belaya-upakovka-tort-klubnika-svechi"):
        return "pink"  # id154: розы розовые, «belaya» упаковка не должна давать white
    if s in ("27-cherno-belyh-rezinovyh-geliyevyh-sharov-svyazka", "25-oranzhevaya-roza-belaya-upakovka", "nabor-sharov-s-7-rozovo-fioletovyh", "51-korallovaya-roza-belaya-upakovka-rozovaya-lenta"):
        return ""  # id156 шары, id159 оранжевые — фильтра нет, «bel» не должно давать white
    if s == "151-krasnaya-roza-belaya-upakovka-101-belo-rozovaya-korzina":
        return "red"
    if s == "svyazka-9-rozovo-krasnyh-serdec-25-rozovyh-roz":
        return "pink"  # id167
    if s.startswith("podarochnyy-nabor") or s.startswith("podarok-nabor") or s.startswith("tort"):
        return ""
    if s.startswith("151-rozovaya-roza-fioletovyy-ottenok"):
        return "pink"
    if s == "151-nezhno-rozovaya-roza-belaya-upakovka":
        return "pink"  # цветы нежно-розовые, «belaya» упаковка не должна давать white
    if s in ("101-rozovaya-roza-25-belyh-roz-2-tary-shar", "25-rozovyh-roz-belaya-upakovka-shokoladnyy-tort"):
        return "pink"  # id216/id220: розы розовые, «bel» не должно давать white
    if s == "101-pokrashennaya-roza-korzina-serdce":
        return ""  # id219: окрашенные голубые/синие, «pokrashennaya» содержит «kras»
    if s == "101-sinyaya-okrashennaya-roza-korzina":
        return ""  # id190: синие окрашенные, «okrashennaya» содержит «kras» — не red
    if s == "101-malinovaya-roza-korzina-bukva-v":
        return "pink"  # id187: малиновые розы, в слаге нет rozov
    if s == "51-malinovaya-roza-belaya-upakovka-prazdnichnyy-tort":
        return "pink"  # id134: коралово-малиновые розы, «belaya» упаковка не должна давать white
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
            if slug.startswith("dop-"):
                continue  # доп-товары не в общей витрине/каталоге — только апселл в оформлении
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
    # 19.10.2026: аренда детских колясок — НЕ товар корзины (заказ через оператора), только витрина бота.
    # Цены/условия — как на kolyaski.html (seo/build_kolyaski.py).
    items.append({
        "id": 9001, "slug": "arenda-detskoy-kolyaski-capella", "rent": True,
        "name": "Аренда коляски Capella (бирюзовая)",
        "desc": "Перекидная ручка (малыш лицом к вам или вперёд), спинка опускается — можно сидеть или спать лёжа, капюшон со смотровым окошком, 5-точечные ремни, компактно складывается.",
        "alt": "Аренда детской коляски в Нячанге",
        "price_vnd": 300000, "price": "от 300 000 донгов / день", "price_sub": "7 дней — 1 000 000 ₫",
        "rent_prices": [[1, 300000], [2, 400000], [3, 500000], [4, 650000], [5, 750000], [6, 900000], [7, 1000000]],
        "rent_rules": ["Без залога и депозита.",
                       "Доставка и забор бесплатно — только по центру Нячанга (зона «Центр»): к отелю или в удобное место в центре.",
                       "Оплата 100% — когда привозим коляску.",
                       "Сообщите отель, номер комнаты, имя и фамилию на английском (как при заселении) — залога нет, так мы знаем, где коляска.",
                       "Вернуть можно через ресепшен: оставьте коляску и пришлите фото — мы приедем и заберём."],
        "cats": ["kolyaski"], "color": "",
        "images": ["img/products/arenda-detskoy-kolyaski-capella/2.webp"] + [x for x in product_imgs("arenda-detskoy-kolyaski-capella", "img/products/arenda-detskoy-kolyaski-capella/1.webp") if not x.endswith("/2.webp")],
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
        {"key": "kolyaski", "label": "Аренда колясок"},
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
