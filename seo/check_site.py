#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПРОВЕРКА САЙТА flowers-nha-trang.online — автоматический чекер.
Запуск из папки new-site:  python3 seo/check_site.py
Олег говорит «проверка сайта» → Claude запускает этот скрипт + проходит по
визуальному чек-листу seo/CHECK-SITE.md.

Ничего не меняет, только читает и печатает отчёт:
  ❌ ERROR   — обязательно исправить (битая ссылка, пропавшее фото, несимметрия)
  ⚠️ WARN    — проверить глазами / возможно некрасиво
  ℹ️ INFO    — справочно
"""
import os, re, csv, sys, subprocess, glob
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
DOMAIN = "https://flowers-nha-trang.online/"

errors, warns, infos = [], [], []
def E(m): errors.append(m)
def W(m): warns.append(m)
def I(m): infos.append(m)

def read(p):
    try:
        return open(p, encoding="utf-8").read()
    except Exception as e:
        return ""

# ---- собрать все html ----
TOP_HTML = sorted(glob.glob("*.html"))
BLOG_HTML = sorted(glob.glob("blog/*.html"))
CAT_HTML  = sorted(glob.glob("catalog/*.html"))
ALL_HTML  = TOP_HTML + BLOG_HTML + CAT_HTML
# страницы-верификаторы поисковиков — игнорируем в части проверок
VERIFY = [f for f in TOP_HTML if re.match(r"(naver|yandex|google)", f)]

# =====================================================================
# 1. СИММЕТРИЯ ЯЗЫКОВ (ru/en/ko трио)
# =====================================================================
def trio_ok(ru, en, ko, label):
    miss = [f for f in (ru, en, ko) if not os.path.exists(f)]
    if miss:
        E(f"[Симметрия] {label}: нет файлов {miss}")

trio_ok("index.html", "index-en.html", "index-kr.html", "Главная")
trio_ok("balloons.html", "balloons-en.html", "balloons-kr.html", "Шары")
trio_ok("catalog-ru.html", "catalog-en.html", "catalog-ko.html", "Каталог-витрина")
trio_ok("blog-ru.html", "blog-en.html", "blog-ko.html", "Блог-витрина")

# статьи: каждый slug должен иметь -ru/-en/-ko
def slugs_from(globpat, suffixes=("-ru","-en","-ko")):
    """вернуть {slug: set(найденные суффиксы)} из blog/ или catalog/"""
    d = defaultdict(set)
    for f in glob.glob(globpat):
        base = os.path.basename(f)[:-5]  # без .html
        for s in suffixes:
            if base.endswith(s):
                d[base[:-len(s)]].add(s)
                break
    return d

for name, pat in (("Статья", "blog/*.html"), ("Товар", "catalog/*.html")):
    for slug, found in sorted(slugs_from(pat).items()):
        miss = set(("-ru","-en","-ko")) - found
        if miss:
            E(f"[Симметрия] {name} '{slug}': не хватает языков {sorted(miss)}")

# одинаковое число карточек в витринах на 3 языках
def count_cards(f, hrefpat):
    return len(set(re.findall(hrefpat, read(f))))

blog_counts = {f: count_cards(f, r'href="blog/[^"]*-(?:ru|en|ko)\.html"') for f in ("blog-ru.html","blog-en.html","blog-ko.html")}
if len(set(blog_counts.values())) > 1:
    E(f"[Симметрия] Разное число карточек статей в витринах: {blog_counts}")
else:
    I(f"Карточек статей в каждой витрине: {list(blog_counts.values())[0]}")

cat_counts = {f: count_cards(f, r'href="catalog/[^"]*-(?:ru|en|ko)\.html"') for f in ("catalog-ru.html","catalog-en.html","catalog-ko.html")}
if len(set(cat_counts.values())) > 1:
    E(f"[Симметрия] Разное число карточек товаров в каталогах: {cat_counts}")
else:
    I(f"Карточек товаров в каждом каталоге: {list(cat_counts.values())[0]}")

# =====================================================================
# 2. БИТЫЕ ССЫЛКИ И ПРОПАВШИЕ ФОТО
# =====================================================================
def is_local(u):
    if not u: return False
    if u.startswith(("http://","https://","#","mailto:","tel:","javascript:","data:")): return False
    return True

missing_links, missing_imgs = set(), set()
for f in ALL_HTML:
    base = os.path.dirname(f)
    html = read(f)
    for u in re.findall(r'href="([^"]+)"', html):
        u2 = u.split("#")[0].split("?")[0]
        if is_local(u2):
            tgt = os.path.normpath(os.path.join(base, u2))
            if not os.path.exists(tgt):
                missing_links.add(f"{f} → {u}")
    for u in re.findall(r'src="([^"]+)"', html):
        u2 = u.split("?")[0]
        if is_local(u2):
            tgt = os.path.normpath(os.path.join(base, u2))
            if not os.path.exists(tgt):
                missing_imgs.add(f"{f} → {u}")
for m in sorted(missing_links): E(f"[Битая ссылка] {m}")
for m in sorted(missing_imgs):  E(f"[Нет фото] {m}")

# =====================================================================
# 3. SITEMAP
# =====================================================================
if not os.path.exists("sitemap.xml"):
    E("[Sitemap] sitemap.xml отсутствует")
else:
    r = subprocess.run(["xmllint","--noout","sitemap.xml"], capture_output=True, text=True)
    if r.returncode != 0:
        E(f"[Sitemap] невалидный XML: {r.stderr.strip()}")
    sm = read("sitemap.xml")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    # каждый URL → существующий файл
    for loc in locs:
        path = loc.replace(DOMAIN, "").strip("/")
        if path == "": path = "index.html"
        if not path.endswith(".html") and not path.endswith(".xml") and "." not in os.path.basename(path):
            path = path + ".html"
        if not os.path.exists(path):
            E(f"[Sitemap] URL без файла: {loc}")
    # каждая страница (кроме верификаторов и -en/-kr дублей главной учтены) должна быть в sitemap
    indexed = set()
    for loc in locs:
        p = loc.replace(DOMAIN, "").strip("/")
        indexed.add(p if p else "index.html")
    for f in ALL_HTML:
        if f in VERIFY: continue
        # sitemap может хранить index.html как корень
        variants = {f, f.replace("index.html","")}
        if not (indexed & variants) and f not in indexed:
            W(f"[Sitemap] страница не в sitemap: {f}")
    # hreflang
    nbl = sm.count("hreflang=")
    I(f"Sitemap: {len(locs)} URL, {nbl} hreflang-ссылок")

# =====================================================================
# 4. РЕЕСТР vs ОПУБЛИКОВАНО + правило ротации
# =====================================================================
if os.path.exists("seo/registry.csv"):
    reg = list(csv.DictReader(open("seo/registry.csv", encoding="utf-8")))
    done = [r for r in reg if r.get("status_ru")=="done"]
    blog_trios = len(slugs_from("blog/*.html"))
    if len(done) != blog_trios:
        W(f"[Реестр] done в registry={len(done)}, а статей-трио в blog/={blog_trios} — не совпадает")
    # ротация: не две одинаковые категории подряд (по дате/порядку done)
    cats = [r.get("category","?") for r in sorted(done, key=lambda x: x.get("date",""))]
    I(f"Опубликованные категории по порядку: {cats}")
    for a,b in zip(cats, cats[1:]):
        if a==b:
            W(f"[Ротация] две статьи подряд одной категории: '{a}' — Олег это запрещал")

# =====================================================================
# 5. ЗАПРЕЩЁННЫЕ ФРАЗЫ (оплата картой — терминалов нет)
# =====================================================================
BAD = [r"оплат[аы]?\s+картой", r"оплатить\s+картой", r"картой\s+при\s+получени",
       r"pay\s+by\s+card", r"card\s+payment", r"신용카드", r"카드\s*결제"]
for f in ALL_HTML:
    html = read(f)
    for pat in BAD:
        if re.search(pat, html, re.I):
            E(f"[Запретная фраза] '{pat}' в {f} — у нас НЕТ оплаты картой")

# =====================================================================
# 6. FEATURED.JS (ротация на главной) vs products.csv
# =====================================================================
if os.path.exists("seo/products.csv") and os.path.exists("js/featured.js"):
    prods = list(csv.DictReader(open("seo/products.csv", encoding="utf-8")))
    fjs = read("js/featured.js")
    not_in = [p["slug"] for p in prods if p["slug"] not in fjs]
    if not_in:
        W(f"[Главная] товары НЕ в js/featured.js (не попадут в ротацию): {not_in}")
    else:
        I(f"Все {len(prods)} товаров есть в ротации главной")

# =====================================================================
# 7. ФОТО СТАТЕЙ: должны быть горизонтальные (карточки фикс-высоты)
# =====================================================================
try:
    from PIL import Image
    for f in glob.glob("img/blog/*.webp"):
        if f.endswith("-thumb.webp"): continue
        w,h = Image.open(f).size
        if h > w:
            W(f"[Фото статьи] вертикальное {os.path.basename(f)} ({w}×{h}) — в карточке обрежется, нужен горизонт ~1200×760")
except Exception:
    I("Pillow не установлен — пропустил проверку пропорций фото (pip install pillow)")

# =====================================================================
# 8. ALT / lang атрибуты
# =====================================================================
for f in ALL_HTML:
    if f in VERIFY: continue
    html = read(f)
    m = re.search(r'<html[^>]*lang="([^"]+)"', html)
    if not m:
        W(f"[lang] нет атрибута lang в <html>: {f}")
    noalt = len(re.findall(r'<img(?![^>]*\balt=)[^>]*>', html))
    if noalt:
        W(f"[alt] {noalt} <img> без alt в {f}")

# =====================================================================
# ОТЧЁТ
# =====================================================================
def block(title, items, icon):
    print(f"\n{icon} {title}: {len(items)}")
    for x in items: print(f"   {icon} {x}")

print("="*64)
print("  ПРОВЕРКА САЙТА flowers-nha-trang.online")
print("="*64)
block("ОШИБКИ (исправить)", errors, "❌")
block("ПРЕДУПРЕЖДЕНИЯ (проверить)", warns, "⚠️")
block("ИНФО", infos, "ℹ️")
print("\n" + "="*64)
print(f"  ИТОГО: ❌ {len(errors)}   ⚠️ {len(warns)}   ℹ️ {len(infos)}")
print("="*64)
print("Дальше — визуальная проверка по seo/CHECK-SITE.md (глазами).")
sys.exit(1 if errors else 0)
