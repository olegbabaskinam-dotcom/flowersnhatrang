# -*- coding: utf-8 -*-
"""
АУДИТ ССЫЛОК И НАВИГАЦИИ (seo/audit_links.py) — с 05.07.2026.
Прошерстивает ВСЕ .html: проверяет, что каждая внутренняя ссылка (href) и картинка (src)
ведут на существующий файл; что языковой переключатель ведёт на верный файл-сосед;
что якорь-фильтр (#cakes и т.п.) реально есть на целевой странице каталога.
Ловит «тупые» логические баги навигации. Только читает, ничего не меняет.
Запуск из new-site:  python3 seo/audit_links.py
"""
import os, re, glob, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

HTML = sorted(p for p in subprocess.check_output(["git", "ls-files", "-z", "*.html"]).decode().split("\0") if p)
EXIST = set(os.path.normpath(f) for f in glob.glob("**/*", recursive=True))

def is_ext(u):
    return u.startswith(("http://","https://","mailto:","tel:","javascript:","data:"))

errors, warns = [], []

# 1) все href и src → существует ли цель
for f in HTML:
    base = os.path.dirname(f)
    s = open(f, encoding="utf-8").read()
    for attr in ("href", "src"):
        for m in re.finditer(r'(?<![\w-])' + attr + r'="([^"]+)"', s):
            u = m.group(1).strip()
            if not u or is_ext(u) or u.startswith("#") or "'+" in u or u.startswith("href_"):
                continue
            page = u.split("#")[0].split("?")[0]
            if not page:
                continue
            tgt = os.path.normpath(page.lstrip("/") if page.startswith("/") else os.path.join(base, page))
            if tgt not in EXIST and not os.path.exists(tgt):
                errors.append(f"[БИТАЯ {attr}] {f} → {u}  (нет файла {tgt})")

# 2) якорь-фильтр (#cakes/#balloons/...) — есть ли такой data-val на целевой странице каталога
FILTER_HASHES = {"cakes","balloons","nabory","r25","r51","r101","mixed","red","white","pink","purple"}
for f in HTML:
    base = os.path.dirname(f)
    s = open(f, encoding="utf-8").read()
    for m in re.finditer(r'href="([^"]+)#([a-z0-9]+)"', s):
        page, frag = m.group(1), m.group(2)
        if frag not in FILTER_HASHES:
            continue
        tgt = os.path.normpath(os.path.join(base, page))
        if os.path.exists(tgt):
            t = open(tgt, encoding="utf-8").read()
            if f'data-val="{frag}"' not in t:
                errors.append(f"[ЯКОРЬ-ФИЛЬТР] {f} → {page}#{frag}, но на целевой странице НЕТ фильтра data-val=\"{frag}\"")

# 3) языковой переключатель: на *-ru есть ссылки на верные *-en / *-ko (и наоборот)
# спец-имена главной и шаров (RU без суффикса, KO = -kr)
SPECIAL = {
    "index.html": {"ru":"index.html","en":"index-en.html","ko":"index-kr.html"},
    "index-en.html": {"ru":"index.html","en":"index-en.html","ko":"index-kr.html"},
    "index-kr.html": {"ru":"index.html","en":"index-en.html","ko":"index-kr.html"},
    "balloons.html": {"ru":"balloons.html","en":"balloons-en.html","ko":"balloons-kr.html"},
    "balloons-en.html": {"ru":"balloons.html","en":"balloons-en.html","ko":"balloons-kr.html"},
    "balloons-kr.html": {"ru":"balloons.html","en":"balloons-en.html","ko":"balloons-kr.html"},
    "torty.html": {"ru":"torty.html","en":"torty-en.html","ko":"torty-kr.html"},
    "torty-en.html": {"ru":"torty.html","en":"torty-en.html","ko":"torty-kr.html"},
    "torty-kr.html": {"ru":"torty.html","en":"torty-en.html","ko":"torty-kr.html"},
    "nabory.html": {"ru":"nabory.html","en":"nabory-en.html","ko":"nabory-kr.html"},
    "nabory-en.html": {"ru":"nabory.html","en":"nabory-en.html","ko":"nabory-kr.html"},
    "nabory-kr.html": {"ru":"nabory.html","en":"nabory-en.html","ko":"nabory-kr.html"},
    "prazdnik.html": {"ru":"prazdnik.html","en":"prazdnik-en.html","ko":"prazdnik-kr.html"},
    "prazdnik-en.html": {"ru":"prazdnik.html","en":"prazdnik-en.html","ko":"prazdnik-kr.html"},
    "prazdnik-kr.html": {"ru":"prazdnik.html","en":"prazdnik-en.html","ko":"prazdnik-kr.html"},
}
def sibling(f, want):
    """Ожидаемый файл-сосед на другом языке."""
    b = os.path.basename(f); d = os.path.dirname(f)
    if b in SPECIAL:
        return os.path.join(d, SPECIAL[b][want])
    for suf, other in [("-ru.html",{"en":"-en.html","ko":"-ko.html"}),
                       ("-en.html",{"ru":"-ru.html","ko":"-ko.html"}),
                       ("-ko.html",{"ru":"-ru.html","en":"-en.html"})]:
        if b.endswith(suf):
            return os.path.join(d, b[:-len(suf)] + other[want]) if want in other else None
    return None

for f in HTML:
    if f in {"cart.html", "order.html", "checkout.html", "zakaz.html", "Dialog.html", "buh/index.html", "tg/index.html"}:
        continue
    if os.path.basename(f) not in SPECIAL and not re.search(r'-(ru|en|ko)\.html$', f):
        continue
    s = open(f, encoding="utf-8").read()
    for want in ("en","ko","ru"):
        sib = sibling(f, want)
        if sib and not os.path.exists(sib):
            warns.append(f"[ЯЗЫК] {f}: нет файла-соседа {want.upper()} → ожидался {sib}")

# 4) нав-консистентность: набор пунктов меню (внутри <nav>) одинаков по всем страницам одного языка
def nav_items(s):
    m = re.search(r'<nav[^>]*>(.*?)</nav>', s, re.S)
    if not m: return None
    return tuple(re.findall(r'>([^<>]{1,20})</a>', m.group(1)))

navsets = {}
for f in HTML:
    if f in {"cart.html", "order.html", "checkout.html", "zakaz.html", "Dialog.html"}:
        continue
    lang = "ru" if (f in ("index.html",) or f.endswith("-ru.html") or f in ("catalog-ru.html","blog-ru.html","balloons.html","torty.html","nabory.html","prazdnik.html")) else ("en" if "-en" in f or f.endswith("index-en.html") else "ko")
    s = open(f, encoding="utf-8").read()
    ni = nav_items(s)
    if ni: navsets.setdefault(lang, {}).setdefault(ni, []).append(f)

# 5) кросс-язык: не-переключательные внутренние ссылки должны оставаться в своём языке
SPLANG = {"index.html":"ru","index-en.html":"en","index-kr.html":"ko",
          "balloons.html":"ru","balloons-en.html":"en","balloons-kr.html":"ko","torty.html":"ru","torty-en.html":"en","torty-kr.html":"ko",
          "nabory.html":"ru","nabory-en.html":"en","nabory-kr.html":"ko","prazdnik.html":"ru","prazdnik-en.html":"en","prazdnik-kr.html":"ko"}
def page_lang(path):
    b = os.path.basename(path)
    if b in SPLANG: return SPLANG[b]
    if b.endswith("-en.html"): return "en"
    if b.endswith("-ko.html"): return "ko"
    if b.endswith("-ru.html"): return "ru"
    return None
FLAGS = ("🇷🇺","🇬🇧","🇰🇷")
for f in HTML:
    L = page_lang(f)
    if not L: continue
    base = os.path.dirname(f)
    s = open(f, encoding="utf-8").read()
    for m in re.finditer(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', s, re.S):
        u, inner = m.group(1), m.group(2)
        if is_ext(u) or u.startswith("#") or any(fl in inner for fl in FLAGS):
            continue  # внешние, якоря, переключатель языка — пропуск
        page = u.split("#")[0].split("?")[0]
        if not page: continue
        tgt = os.path.normpath(os.path.join(base, page))
        TL = page_lang(tgt)
        if TL and TL != L:
            warns.append(f"[КРОСС-ЯЗЫК] {f} ({L}) → {u} ({TL}) — ссылка на другой язык (не переключатель)")

# 6) внутристраничные якоря (#delivery, #catalog…) — есть ли элемент с таким id
for f in HTML:
    base = os.path.dirname(f)
    s = open(f, encoding="utf-8").read()
    ids = set(re.findall(r'id="([^"]+)"', s))
    for m in re.finditer(r'href="([^"]*)#([a-zA-Z][\w\-]*)"', s):
        page, frag = m.group(1), m.group(2)
        if frag in FILTER_HASHES: continue  # это JS-фильтры каталога, не id
        tgt = f if page=="" else os.path.normpath(os.path.join(base, page))
        if not os.path.exists(tgt): continue
        tids = ids if tgt==f else set(re.findall(r'id="([^"]+)"', open(tgt,encoding="utf-8").read()))
        if frag not in tids:
            warns.append(f"[ЯКОРЬ] {f} → {page}#{frag}: нет элемента id=\"{frag}\" на цели")

# 7) мёртвые фильтры каталога: у каждой кнопки data-val есть ≥1 товар с таким data-cat
for f in ["catalog-ru.html","catalog-en.html","catalog-ko.html"]:
    if not os.path.exists(f): continue
    s = open(f, encoding="utf-8").read()
    cats = set()
    for dc in re.findall(r'data-cat="([^"]*)"', s):
        for part in dc.split(): cats.add(part)
    for val in re.findall(r'data-filter="cat"[^>]*>(.*?)</div>', s, re.S):
        for fv in re.findall(r'data-val="([^"]+)"', val):
            if fv and fv not in cats:
                errors.append(f"[МЁРТВЫЙ ФИЛЬТР] {f}: кнопка data-val=\"{fv}\" — нет ни одного товара этой категории")

# 8) паритет баннеров главной по языкам (Шары/Торты/Статьи должны быть на всех 3)
HOMES = {"ru":"index.html","en":"index-en.html","ko":"index-kr.html"}
def btype(h):
    if "torty" in h or "#cakes" in h: return "торты"
    if "balloons" in h: return "шары"
    if "blog" in h: return "статьи"
    return None
def home_banners(s):
    hs = re.findall(r'<a href="([^"]+)" class="block rounded-3xl[^"]*" style="height: 340px;">', s)
    return set(t for t in (btype(h) for h in hs) if t)
hb = {lang: home_banners(open(hp,encoding="utf-8").read()) for lang,hp in HOMES.items() if os.path.exists(hp)}
allb = set().union(*hb.values()) if hb else set()
for lang, ts in hb.items():
    miss = allb - ts
    if miss:
        errors.append(f"[ГЛАВНАЯ {lang}] нет баннеров: {', '.join(sorted(miss))} (есть на других языках)")

print("="*64); print("  АУДИТ ССЫЛОК И НАВИГАЦИИ"); print("="*64)
print(f"\nПроверено HTML-страниц: {len(HTML)}")
print(f"\n❌ ОШИБКИ: {len(errors)}")
for e in errors[:60]: print("   "+e)
print(f"\n⚠️ ПРЕДУПРЕЖДЕНИЯ: {len(warns)}")
for w in warns[:40]: print("   "+w)
print("\nℹ️ Наборы меню по языкам (разные варианты = возможная рассинхронизация):")
for lang, variants in navsets.items():
    print(f"   {lang}: вариантов меню — {len(variants)}")
    if len(variants) > 1:
        for ni, files in variants.items():
            print(f"      {ni}  ← {len(files)} стр. (напр. {files[0]})")
print("\n" + "="*64)
print(f"ИТОГО: ❌ {len(errors)}  ⚠️ {len(warns)}")
print("="*64)
