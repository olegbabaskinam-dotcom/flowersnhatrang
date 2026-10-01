#!/usr/bin/env python3
# «Мини-презентация каталога» (01.10.2026): вертикальные плитки 3:4 по категориям перед сеткой товаров
# в catalog-{ru,en,ko}.html. Блок между <!--SHOWCASE-START--> и <!--SHOWCASE-END-->; идемпотентно.
# Клик по плитке → фильтр каталога (#r25, #b-latex ...) + прокрутка к товарам.
# ⚠️ Полный build_site.render_catalog этот блок не делает — после него перезапустить этот скрипт.
import os, re, sys, json, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "seo"))
import build_category_landings as L   # cards_from_catalog, M, isFlower, isCombo, LATEX...

def baskets(c): return L.isFlower(c) and any(t in ("korzina", "korzine", "korzinoy") for t in L.toks(c))
MATCH = dict(L.M); MATCH["baskets"] = baskets
MATCH["mixed"] = lambda c: L.has(c, "mixed")
MATCH["b-latex"] = L.bLatex
MATCH["b-helium"] = lambda c: L.has(c, "balloons") and c["slug"] not in L.LATEX_ONLY

GROUPS = [
 ("flowers", ["r25", "r51", "r101", "baskets", "mixed"]),
 ("balloons", ["b-helium", "b-latex", "b-combo"]),
 ("gifts", ["cakes", "nabory"]),
 ("decor", ["decor"]),
]
# фото плиток (выбраны вручную по фото 01.10.2026)
PICK = {"r25": "25-krasnyh-roz", "r51": "51-krasnaya-roza-belaya-upakovka-krasnaya-len", "r101": "101-krasno-rozovaya-roza-rozovaya-upakovka",
        "baskets": "101-malinovaya-roza-korzina-bukva-v", "mixed": "stilnyy-sbornyy-buket-rozovyy", "b-helium": "nabor-sharov-m-cherno-zolotoy",
        "b-latex": "35-serebristo-chernyh-gelievyh-sharov-pod-potolok", "b-combo": "svyazka-9-rozovo-krasnyh-serdec-25-rozovyh-roz",
        "nabory": "podarochnyy-nabor-kofeynyy-vkus-vietnama"}
TXT = {
 "ru": {"h": "Наш каталог", "sub": "Выберите категорию — покажем все позиции", "open": "Смотреть →",
        "g": {"flowers": "💐 Цветы", "balloons": "🎈 Шары", "gifts": "🎁 Подарки", "decor": "🎉 Оформление праздников"},
        "t": {"r25": "25 роз", "r51": "51 роза", "r101": "101 роза и больше", "baskets": "Корзины с цветами", "mixed": "Сборные букеты",
              "b-helium": "Фольгированные шары", "b-latex": "Резиновые шары", "b-combo": "Шары с цветами", "cakes": "Торты", "nabory": "Подарочные наборы", "decor": "Готовое оформление"},
        "n": lambda n: f"{n} поз.", "bal": {"b-helium": "летают в среднем 7 дней", "b-latex": "летают в среднем 12 часов"}},
 "en": {"h": "Our catalog", "sub": "Pick a category — we'll show every item", "open": "View →",
        "g": {"flowers": "💐 Flowers", "balloons": "🎈 Balloons", "gifts": "🎁 Gifts", "decor": "🎉 Party décor"},
        "t": {"r25": "25 roses", "r51": "51 roses", "r101": "101 roses & more", "baskets": "Flower baskets", "mixed": "Mixed bouquets",
              "b-helium": "Foil balloons", "b-latex": "Latex balloons", "b-combo": "Balloons with flowers", "cakes": "Cakes", "nabory": "Gift sets", "decor": "Ready party décor"},
        "n": lambda n: f"{n} items", "bal": {"b-helium": "float ~7 days on average", "b-latex": "float ~12 hours on average"}},
 "ko": {"h": "카탈로그", "sub": "카테고리를 선택하면 모든 상품을 보여드립니다", "open": "보기 →",
        "g": {"flowers": "💐 꽃", "balloons": "🎈 풍선", "gifts": "🎁 선물", "decor": "🎉 파티 데코"},
        "t": {"r25": "장미 25송이", "r51": "장미 51송이", "r101": "장미 101송이 이상", "baskets": "꽃바구니", "mixed": "믹스 꽃다발",
              "b-helium": "호일 풍선", "b-latex": "라텍스 풍선", "b-combo": "꽃과 함께하는 풍선", "cakes": "케이크", "nabory": "선물 세트", "decor": "파티 데코 세트"},
        "n": lambda n: f"{n}개", "bal": {"b-helium": "평균 약 7일", "b-latex": "평균 약 12시간"}},
}
CSS = """<style id="sc-css">
.sc{max-width:64rem;margin:0 auto;padding:3rem 1rem 1rem}
.sc-h{font-family:'Cormorant Garamond',Georgia,serif;font-style:italic;font-weight:600;font-size:2.4rem;text-align:center;color:#1a1a1a;margin:0}
.sc-sub{text-align:center;color:#a8a29e;font-size:.9rem;margin:.3rem 0 2rem}
.sc-g{margin:0 0 2.2rem}
.sc-gh{font-family:'Cormorant Garamond',Georgia,serif;font-weight:600;font-size:1.6rem;color:#1a1a1a;margin:0 0 .9rem;display:flex;align-items:center;gap:.6rem}
.sc-gh:after{content:"";flex:1;height:1px;background:#f0d0d8}
.sc-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem}
@media(min-width:640px){.sc-row{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(min-width:900px){.sc-row{grid-template-columns:repeat(5,minmax(0,1fr))}}
.sc-t{position:relative;display:block;aspect-ratio:3/4;border-radius:18px;overflow:hidden;background:#fdf4f7;text-decoration:none;box-shadow:0 6px 18px rgba(28,25,23,.08);transition:transform .2s,box-shadow .2s}
.sc-t:hover{transform:translateY(-3px);box-shadow:0 12px 26px rgba(192,104,122,.22)}
.sc-t img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.sc-t:after{content:"";position:absolute;inset:0;background:linear-gradient(to top,rgba(20,10,14,.78) 0%,rgba(20,10,14,.25) 45%,rgba(20,10,14,0) 70%)}
.sc-c{position:absolute;left:0;right:0;bottom:0;z-index:2;padding:.8rem .85rem .9rem;color:#fff}
.sc-c b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-size:1.35rem;font-weight:600;line-height:1.1}
.sc-c i{display:block;font-style:normal;font-size:.72rem;opacity:.85;margin-top:.2rem;letter-spacing:.04em}
.sc-c em{display:inline-block;font-style:normal;margin-top:.35rem;font-size:.7rem;font-weight:700;background:rgba(238,246,251,.95);color:#0f3c57;border-radius:999px;padding:.15rem .5rem}
.sc-c span{display:inline-block;margin-top:.5rem;font-size:.75rem;font-weight:600;background:rgba(255,255,255,.92);color:#a8566a;border-radius:999px;padding:.25rem .7rem}
</style>
"""
JS = """<script>/*SHOWCASE-JS*/(function(){document.querySelectorAll('.sc-t[data-k]').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();var k=a.getAttribute('data-k');if(location.hash==='#'+k){window.dispatchEvent(new HashChangeEvent('hashchange'));}else{location.hash=k;}});});})();</script>"""

def build(lang):
    fn = L.CAT[lang]; s = open(fn, encoding="utf-8").read()
    cards = L.cards_from_catalog(lang); T = TXT[lang]
    h = ['<!--SHOWCASE-START-->\n', CSS, '<section class="sc" aria-label="' + T["h"] + '">\n',
         f'  <h2 class="sc-h">{T["h"]}</h2>\n  <p class="sc-sub">{T["sub"]}</p>\n']
    for g, keys in GROUPS:
        h.append(f'  <div class="sc-g"><h3 class="sc-gh">{T["g"][g]}</h3><div class="sc-row">\n')
        for k in keys:
            allc = [c for c in cards if MATCH[k](c)]
            lst = [c for c in allc if not c["sold"]]
            if not lst: continue
            pure = [c for c in lst if not L.isCombo(c)] or lst
            want = PICK.get(k)
            pic = next((c for c in lst if want and c["slug"].startswith(want)), None) or pure[0]
            img = re.search(r'src="(img/products/[^"]+)"', pic["html"]).group(1)
            bal = f'<em>{T["bal"][k]}</em>' if k in T["bal"] else ""
            h.append(f'    <a class="sc-t" href="#{k}" data-k="{k}"><img src="{img}" alt="{html.escape(T["t"][k])}" loading="lazy" decoding="async" width="900" height="1200">'
                     f'<div class="sc-c"><b>{T["t"][k]}</b><i>{T["n"](len(allc))}</i>{bal}<span>{T["open"]}</span></div></a>\n')
        h.append('  </div></div>\n')
    h.append('</section>\n' + JS + '\n<!--SHOWCASE-END-->\n')
    block = "".join(h)
    if "<!--SHOWCASE-START-->" in s:
        s = re.sub(r"<!--SHOWCASE-START-->.*?<!--SHOWCASE-END-->\n", lambda m: block, s, flags=re.S)
    else:
        anchor = '    <section class="pb-16 px-4 max-w-5xl mx-auto pt-12">\n        <div class="sort-bar">'
        assert anchor in s, fn
        s = s.replace(anchor, block + anchor, 1)
    # ensure anchors: у каждого хэша плитки есть <span id=… class="cat-anchor"> (для audit_links и прокрутки)
    keys = [k for g, ks in GROUPS for k in ks]
    miss = [k for k in keys if f'id="{k}"' not in s]
    if miss:
        s = s.replace('<span id="flowers" class="cat-anchor"></span>', "".join(f'<span id="{k}" class="cat-anchor"></span>' for k in miss) + '<span id="flowers" class="cat-anchor"></span>', 1)
    open(fn, "w", encoding="utf-8").write(s)
    print("showcase →", fn, "anchors+", miss)

if __name__ == "__main__":
    for lang in ("ru", "en", "ko"): build(lang)
