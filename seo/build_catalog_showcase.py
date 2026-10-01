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
PICK = {"r25": "25-krasnyh-roz", "r51": "51-belaya-roza-v-upakovke", "r101": "101-krasno-rozovaya-roza-rozovaya-upakovka",
        "baskets": "101-malinovaya-roza-korzina-bukva-v", "mixed": "stilnyy-sbornyy-buket-rozovyy", "b-helium": "nabor-sharov-m-cherno-zolotoy",
        "b-latex": "35-serebristo-chernyh-gelievyh-sharov-pod-potolok", "b-combo": "svyazka-9-rozovo-krasnyh-serdec-25-rozovyh-roz",
        "nabory": "podarochnyy-nabor-zhenskiy"}
HEAD = {
 "ru": {"h1": "Каталог цветов, шаров и подарков в Нячанге", "t1": "<b>2000+</b> букетов доставлено", "t2": "<b>157</b> отзывов на Google", "t3": "💵 оплата при получении"},
 "en": {"h1": "Flowers, Balloons &amp; Gifts Catalog in Nha Trang", "t1": "<b>2000+</b> bouquets delivered", "t2": "<b>157</b> reviews on Google", "t3": "💵 pay on delivery"},
 "ko": {"h1": "나트랑 꽃·풍선·선물 카탈로그", "t1": "꽃다발 <b>2000+</b> 배달 완료", "t2": "Google 리뷰 <b>157</b>개", "t3": "💵 수령 시 결제"},
}
GMAPS = "https://maps.app.goo.gl/3H4ngJ1UoLrMDkiS7?g_st=ic"
ZLINK = {"ru": "Вся категория →", "en": "Whole category →", "ko": "전체 보기 →"}
ZPAGE = {"flowers": "cvety", "balloons": "balloons", "gifts": "podarki", "decor": "prazdnik"}
TXT = {
 "ru": {"h": "Наш каталог", "sub": "Выберите категорию — покажем все позиции", "open": "Смотреть →",
        "g": {"flowers": "💐 Цветы", "balloons": "🎈 Шары", "gifts": "🎁 Подарки", "decor": "🎉 Оформление"},
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
.sc{max-width:78rem;margin:0 auto;padding:.9rem 1rem .4rem}
.sc-h1{font-family:'Cormorant Garamond',Georgia,serif;font-weight:700;font-size:clamp(1.4rem,2.8vw,2.2rem);line-height:1.15;text-align:center;color:#1a1a1a;margin:0}
.sc-tr{display:flex;flex-wrap:wrap;justify-content:center;gap:.35rem .5rem;margin:.55rem 0 1rem;font-size:.8rem;color:#78716c}
.sc-tr>*{display:inline-flex;align-items:center;gap:.25rem;background:#fff;border:1px solid #f0e0e5;border-radius:999px;padding:.25rem .8rem;text-decoration:none;color:#57534e;white-space:nowrap}
.sc-tr b{color:#1a1a1a;font-size:.92rem}
.sc-tr a:hover{border-color:#c0687a;color:#a8566a}
.sc-tr .st{color:#f5b301}
.sc-zones{display:grid;grid-template-columns:minmax(0,1fr);gap:1rem}
.sc-z{min-width:0}
@media(min-width:900px){.sc-zones{grid-template-columns:minmax(0,3fr) minmax(0,2fr) minmax(0,1fr)}.sc-z.flowers{grid-column:1/-1}}
.sc-z{border-radius:24px;padding:.9rem .9rem 1rem;border:1px solid rgba(0,0,0,.04)}
.sc-z.flowers{background:linear-gradient(135deg,#fdf0f4 0%,#fff7f9 100%)}
.sc-z.balloons{background:linear-gradient(135deg,#eaf4fb 0%,#f6fbfe 100%)}
.sc-z.gifts{background:linear-gradient(135deg,#fbf1e4 0%,#fffaf3 100%)}
.sc-z.decor{background:linear-gradient(135deg,#f3edfb 0%,#fbf8fe 100%)}
.sc-zh{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:.2rem .5rem;margin:0 .15rem .7rem}
.sc-zh h2{font-family:'Cormorant Garamond',Georgia,serif;font-weight:700;font-size:clamp(1.35rem,2.2vw,1.75rem);color:#1a1a1a;margin:0;line-height:1.1}
@media(min-width:900px){.sc-z.decor .sc-zh h2{font-size:1.3rem;white-space:nowrap}.sc-z.decor .sc-zh{margin-bottom:.45rem}}
.sc-zh a{font-size:.75rem;font-weight:600;color:#a8566a;text-decoration:none;white-space:nowrap;border-bottom:1px solid rgba(168,86,106,.35)}
.sc-zh a:hover{color:#7d3a4c}
.sc-row{display:grid;gap:.6rem;grid-template-columns:repeat(2,minmax(0,1fr))}
@media(max-width:899px){.sc-row>.sc-t:last-child:nth-child(odd){grid-column:1/-1;aspect-ratio:16/10}}
@media(min-width:900px){.sc-row{grid-template-columns:repeat(3,minmax(0,1fr))}}
.sc-z.gifts .sc-row{grid-template-columns:repeat(2,minmax(0,1fr))}
.sc-z.decor .sc-row{grid-template-columns:minmax(0,1fr)}
@media(min-width:900px){.sc-z.flowers .sc-row{grid-template-columns:repeat(5,minmax(0,1fr));gap:.8rem}.sc-row{gap:.8rem}}
.sc-t{position:relative;display:block;aspect-ratio:3/4;border-radius:18px;overflow:hidden;background:#fdf4f7;text-decoration:none;box-shadow:0 6px 16px rgba(28,25,23,.10);transition:transform .2s,box-shadow .2s}
.sc-t:hover{transform:translateY(-3px);box-shadow:0 14px 28px rgba(192,104,122,.25)}
.sc-t img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .5s}
.sc-t:hover img{transform:scale(1.04)}
.sc-t:after{content:"";position:absolute;inset:0;background:linear-gradient(to top,rgba(20,10,14,.85) 0%,rgba(20,10,14,.35) 38%,rgba(20,10,14,0) 62%)}
.sc-c{position:absolute;left:0;right:0;bottom:0;z-index:2;padding:.55rem .6rem .65rem;color:#fff}
.sc-c b{display:block;font-family:'Cormorant Garamond',Georgia,serif;font-weight:700;font-size:clamp(1rem,1.35vw,1.4rem);line-height:1.08}
@media(max-width:899px){.sc-c b{font-size:1.02rem}.sc-row>.sc-t:last-child:nth-child(odd) .sc-c b{font-size:1.3rem}}
.sc-c i{display:block;font-style:normal;font-size:.7rem;opacity:.85;margin-top:.15rem}
.sc-c em{display:inline-block;font-style:normal;margin-top:.3rem;font-size:.66rem;font-weight:700;line-height:1.2;background:rgba(238,246,251,.95);color:#0f3c57;border-radius:8px;padding:.15rem .4rem}
.sc-c span{display:inline-block;margin-top:.4rem;font-size:.7rem;font-weight:700;background:rgba(255,255,255,.93);color:#a8566a;border-radius:999px;padding:.2rem .65rem}

</style>
"""
JS = """<script>/*SHOWCASE-JS*/(function(){document.querySelectorAll('.sc-t[data-k]').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();var k=a.getAttribute('data-k');if(location.hash==='#'+k){window.dispatchEvent(new HashChangeEvent('hashchange'));}else{location.hash=k;}});});})();</script>"""

STAR = '<svg viewBox="0 0 576 512" fill="currentColor" width="1em" height="1em"><path d="M316.9 18C311.6 7 300.4 0 288.1 0s-23.4 7-28.8 18L195 150.3 51.4 171.5c-12 1.8-22 10.2-25.7 21.7s-.7 24.2 7.9 32.7L137.8 329 113.2 474.7c-2 12 3 24.2 12.9 31.3s23 8 33.8 2.3l128.3-68.5 128.3 68.5c10.8 5.7 23.9 4.9 33.8-2.3s14.9-19.3 12.9-31.3L438.5 329 542.7 225.9c8.6-8.5 11.7-21.2 7.9-32.7s-13.7-19.9-25.7-21.7L381.2 150.3 316.9 18z"/></svg>'

def build(lang):
    fn = L.CAT[lang]; s = open(fn, encoding="utf-8").read()
    cards = L.cards_from_catalog(lang); T = TXT[lang]; Hd = HEAD[lang]
    # 01.10.2026: убираем старые «шапку» (h1+абзац) и полосу доверия — всё в компактном первом экране
    s = re.sub(r'    <section class="py-12 px-4 max-w-5xl mx-auto text-center">\s*<h1.*?</section>\n\n?', '', s, count=1, flags=re.S)
    s = re.sub(r'    <section class="reveal py-8 px-4 border-b border-stone-100">\s*<div class="max-w-4xl mx-auto">\s*<div class="grid grid-cols-3 divide-x divide-stone-100">.*?</section>\n\n?', '', s, count=1, flags=re.S)
    h = ['<!--SHOWCASE-START-->\n', CSS, '<section class="sc">\n',
         f'  <h1 class="sc-h1">{Hd["h1"]}</h1>\n',
         f'  <div class="sc-tr"><span>{Hd["t1"]}</span><a href="{GMAPS}" target="_blank" rel="noopener noreferrer"><span class="st">{STAR}</span>{Hd["t2"]}</a><span>{Hd["t3"]}</span></div>\n',
         '  <div class="sc-zones">\n']
    for g, keys in GROUPS:
        h.append(f'  <div class="sc-z {g}"><div class="sc-zh"><h2>{T["g"][g]}</h2><a href="{L.fname(ZPAGE[g], lang)}">{ZLINK[lang]}</a></div><div class="sc-row">\n')
        for k in keys:
            allc = [c for c in cards if MATCH[k](c)]
            lst = [c for c in allc if not c["sold"]]
            if not lst: continue
            pure = [c for c in lst if not L.isCombo(c)] or lst
            want = PICK.get(k)
            pic = next((c for c in lst if want and c["slug"].startswith(want)), None) or pure[0]
            img = re.search(r'src="(img/products/[^"]+)"', pic["html"]).group(1)
            bal = f'<em>{T["bal"][k]}</em>' if k in T["bal"] else ""
            h.append(f'    <a class="sc-t" href="#{k}" data-k="{k}"><img src="{img}" alt="{html.escape(T["t"][k])}" decoding="async" width="900" height="1200">'
                     f'<div class="sc-c"><b>{T["t"][k]}</b><i>{T["n"](len(allc))}</i>{bal}<span>{T["open"]}</span></div></a>\n')
        h.append('  </div></div>\n')
    h.append('  </div>\n</section>\n' + JS + '\n<!--SHOWCASE-END-->\n')
    block = "".join(h)
    if "<!--SHOWCASE-START-->" in s:
        s = re.sub(r"<!--SHOWCASE-START-->.*?<!--SHOWCASE-END-->\n", lambda m: block, s, flags=re.S)
    else:
        anchor = '    <section class="pb-16 px-4 max-w-5xl mx-auto pt-6">\n        <div class="sort-bar">'
        assert anchor in s, fn
        s = s.replace(anchor, block + anchor, 1)
    keys = [k for g, ks in GROUPS for k in ks]
    miss = [k for k in keys if f'id="{k}"' not in s]
    if miss:
        s = s.replace('<span id="flowers" class="cat-anchor"></span>', "".join(f'<span id="{k}" class="cat-anchor"></span>' for k in miss) + '<span id="flowers" class="cat-anchor"></span>', 1)
    open(fn, "w", encoding="utf-8").write(s)
    print("showcase →", fn, s.count("<h1"))

if __name__ == "__main__":
    for lang in ("ru", "en", "ko"): build(lang)
