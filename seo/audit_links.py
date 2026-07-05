# -*- coding: utf-8 -*-
"""
АУДИТ ССЫЛОК И НАВИГАЦИИ (seo/audit_links.py) — с 05.07.2026.
Прошерстивает ВСЕ .html: проверяет, что каждая внутренняя ссылка (href) и картинка (src)
ведут на существующий файл; что языковой переключатель ведёт на верный файл-сосед;
что якорь-фильтр (#cakes и т.п.) реально есть на целевой странице каталога.
Ловит «тупые» логические баги навигации. Только читает, ничего не меняет.
Запуск из new-site:  python3 seo/audit_links.py
"""
import os, re, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

HTML = sorted(glob.glob("*.html") + glob.glob("catalog/*.html") + glob.glob("blog/*.html"))
EXIST = set(os.path.normpath(f) for f in glob.glob("**/*", recursive=True))

def is_ext(u):
    return u.startswith(("http://","https://","mailto:","tel:","javascript:","data:"))

errors, warns = [], []

# 1) все href и src → существует ли цель
for f in HTML:
    base = os.path.dirname(f)
    s = open(f, encoding="utf-8").read()
    for attr in ("href", "src"):
        for m in re.finditer(attr + r'="([^"]+)"', s):
            u = m.group(1).strip()
            if not u or is_ext(u) or u.startswith("#"):
                continue
            page = u.split("#")[0].split("?")[0]
            if not page:
                continue
            tgt = os.path.normpath(os.path.join(base, page))
            if tgt not in EXIST and not os.path.exists(tgt):
                errors.append(f"[БИТАЯ {attr}] {f} → {u}  (нет файла {tgt})")

# 2) якорь-фильтр (#cakes/#balloons/...) — есть ли такой data-val на целевой странице каталога
FILTER_HASHES = {"cakes","balloons","r25","r51","r101","mixed","red","white","pink","purple"}
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
    lang = "ru" if (f in ("index.html",) or f.endswith("-ru.html") or f in ("catalog-ru.html","blog-ru.html","balloons.html")) else ("en" if "-en" in f or f.endswith("index-en.html") else "ko")
    s = open(f, encoding="utf-8").read()
    ni = nav_items(s)
    if ni: navsets.setdefault(lang, {}).setdefault(ni, []).append(f)

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
