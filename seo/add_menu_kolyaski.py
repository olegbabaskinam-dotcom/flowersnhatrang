#!/usr/bin/env python3
"""19.10.2026: в меню всех страниц (десктоп + мобильное) добавлены «🎂 Торты» (после Шаров) и «👶 Коляски» (после Оформления).
Идемпотентно. Заодно чинит ссылку «🎈 Шары», которая на podarki/prazdnik вела на саму страницу."""
import re, subprocess, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
L = {"": ("🎂 Торты", "👶 Коляски", "", "🎈 Шары"), "-en": ("🎂 Cakes", "👶 Strollers", "-en", "🎈 Balloons"), "-kr": ("🎂 케이크", "👶 유모차", "-kr", "🎈 풍선")}
files = subprocess.check_output(["git", "ls-files", "*.html"], text=True).split() + ["kolyaski.html", "kolyaski-en.html", "kolyaski-kr.html"]
pat = re.compile(r'<a href="((?:\.\./)?)prazdnik(-en|-kr)?\.html" (class="px-3[^"]*"|style="display:block[^"]*")>[^<]*</a>')
balpat = re.compile(r'<a href="((?:\.\./)?)(?:podarki|prazdnik)(-en|-kr)?\.html" (class="px-3[^"]*"|style="display:block[^"]*")>(🎈 [^<]*)</a>')
changed = 0
for f in sorted(set(files)):
    if not os.path.exists(f) or f.startswith(("_to_delete/", "_removed")): continue
    s = open(f, encoding="utf-8").read(); o = s
    s = balpat.sub(lambda m: f'<a href="{m.group(1)}balloons{m.group(2) or ""}.html" {m.group(3)}>{m.group(4)}</a>', s)
    def rep(m):
        pre, suf, attr = m.group(1), m.group(2) or "", m.group(3)
        cake, kol = L[suf][0], L[suf][1]
        out = m.group(0)
        if f'kolyaski{suf}.html" {attr}' not in s:
            out += f'<a href="{pre}kolyaski{suf}.html" {attr}>{kol}</a>'
        return out
    s = pat.sub(rep, s)
    # Торты после Шаров (если ещё нет)
    def rep_b(m):
        pre, suf, attr = m.group(1), m.group(2) or "", m.group(3)
        if f'torty{suf}.html" {attr}' in s: return m.group(0)
        return m.group(0) + f'<a href="{pre}torty{suf}.html" {attr}>{L[suf][0]}</a>'
    s = re.sub(r'<a href="((?:\.\./)?)balloons(-en|-kr)?\.html" (class="px-3[^"]*"|style="display:block[^"]*")>🎈[^<]*</a>', rep_b, s)
    if s != o:
        open(f, "w", encoding="utf-8").write(s); changed += 1
print("changed", changed)
