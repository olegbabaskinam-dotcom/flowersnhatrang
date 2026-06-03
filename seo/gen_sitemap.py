# -*- coding: utf-8 -*-
"""Пересобирает sitemap.xml: главные, шары, каталог/блог витрины, страницы товаров."""
import os, csv, datetime
import build_site as B

ROOT = B.ROOT
DOMAIN = B.DOMAIN
TODAY = datetime.date.today().isoformat()
products = list(csv.DictReader(open(B.PRODUCTS, encoding="utf-8")))

def url(loc, alts, pr="0.8", freq="weekly"):
    lines = [f"  <url>", f"    <loc>{loc}</loc>"]
    for code, href in alts:
        lines.append(f'    <xhtml:link rel="alternate" hreflang="{code}" href="{href}"/>')
    lines += [f"    <lastmod>{TODAY}</lastmod>", f"    <changefreq>{freq}</changefreq>",
              f"    <priority>{pr}</priority>", "  </url>"]
    return "\n".join(lines)

def trio(ru, en, ko):
    return [("ru", ru), ("en", en), ("ko", ko), ("x-default", ru)]

blocks = []
# главные
blocks.append(url(f"{DOMAIN}/", trio(f"{DOMAIN}/", f"{DOMAIN}/index-en.html", f"{DOMAIN}/index-kr.html"), "1.0"))
blocks.append(url(f"{DOMAIN}/index-en.html", trio(f"{DOMAIN}/", f"{DOMAIN}/index-en.html", f"{DOMAIN}/index-kr.html"), "1.0"))
blocks.append(url(f"{DOMAIN}/index-kr.html", trio(f"{DOMAIN}/", f"{DOMAIN}/index-en.html", f"{DOMAIN}/index-kr.html"), "1.0"))
# шары
blocks.append(url(f"{DOMAIN}/balloons.html", trio(f"{DOMAIN}/balloons.html", f"{DOMAIN}/balloons-en.html", f"{DOMAIN}/balloons-kr.html"), "0.8"))
blocks.append(url(f"{DOMAIN}/balloons-en.html", trio(f"{DOMAIN}/balloons.html", f"{DOMAIN}/balloons-en.html", f"{DOMAIN}/balloons-kr.html"), "0.8"))
blocks.append(url(f"{DOMAIN}/balloons-kr.html", trio(f"{DOMAIN}/balloons.html", f"{DOMAIN}/balloons-en.html", f"{DOMAIN}/balloons-kr.html"), "0.8"))
# каталог + блог витрины
for base in ("catalog", "blog"):
    alts = trio(f"{DOMAIN}/{base}-ru.html", f"{DOMAIN}/{base}-en.html", f"{DOMAIN}/{base}-ko.html")
    for l in B.LANGS:
        blocks.append(url(f"{DOMAIN}/{base}-{l}.html", alts, "0.9"))
# товары
for p in products:
    s = p["slug"]
    alts = trio(f"{DOMAIN}/catalog/{s}-ru.html", f"{DOMAIN}/catalog/{s}-en.html", f"{DOMAIN}/catalog/{s}-ko.html")
    for l in B.LANGS:
        blocks.append(url(f"{DOMAIN}/catalog/{s}-{l}.html", alts, "0.7"))
# статьи (только языки, которые реально есть в JSON)
for art in B.load_articles():
    s = art["slug"]
    langs = [l for l in B.LANGS if l in art]
    alts = [(l, f"{DOMAIN}/blog/{s}-{l}.html") for l in langs]
    if "ru" in langs:
        alts.append(("x-default", f"{DOMAIN}/blog/{s}-ru.html"))
    for l in langs:
        blocks.append(url(f"{DOMAIN}/blog/{s}-{l}.html", alts, "0.7"))

xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
       '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n\n'
       + "\n\n".join(blocks) + "\n\n</urlset>\n")
open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(xml)
print(f"sitemap.xml: {len(blocks)} URL")
