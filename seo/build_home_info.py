#!/usr/bin/env python3
# 01.10.2026: блок «Основная информация» (из order.html, section#flwInfo) дублируется внизу главных
# index.html / index-en.html / index-kr.html — статичным текстом на языке страницы.
# Источник правды — order.html (словарь i18n + разметка). Идемпотентно: <!--HOME-INFO-START--> … <!--HOME-INFO-END-->.
import re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
src = open("order.html", encoding="utf-8").read()
D = {m.group(1): {"ru": m.group(2), "en": m.group(3), "ko": m.group(4)}
     for m in re.finditer(r'^\s*(\w+):\{ru:"(.*?)",en:"(.*?)",ko:"(.*?)"\},?\s*$', src, re.M)}
a = src.index('<section id="flwInfo"'); b = src.index("</section>", a) + len("</section>")
BLOCK = src[a:b]
BLOCK = re.sub(r"<script>.*?</script>\n?", "", BLOCK, flags=re.S)
ZOOM = """<script>function openZoneImg(src){var o=document.createElement('div');o.style.cssText='position:fixed;inset:0;background:rgba(20,10,14,.82);z-index:9999;display:flex;align-items:center;justify-content:center;padding:16px;cursor:zoom-out';o.innerHTML='<img src="'+src+'" alt="" style="max-width:100%;max-height:100%;border-radius:14px">';o.onclick=function(){o.remove();};document.body.appendChild(o);}</script>"""
PAY_H = {"ru": "способы оплаты", "en": "payment methods", "ko": "결제 방법"}

def localized(lang):
    def rep(m):
        tag, attrs, key, inner, close = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        val = D.get(key, {}).get(lang)
        return f"<{tag}{attrs} data-i18n=\"{key}\">{val if val is not None else inner}</{close}>"
    h = re.sub(r'<(\w+)([^>]*?) data-i18n="(\w+)"([^>]*)>(.*?)</(\1)>',
               lambda m: f"<{m.group(1)}{m.group(2)}{m.group(4)}>{D.get(m.group(3),{}).get(lang, m.group(5))}</{m.group(6)}>", BLOCK, flags=re.S)
    h = h.replace('id="flwInfo"', 'id="info"')
    h = h.replace("img/site/zones/map-ru.webp", f"img/site/zones/map-{lang}.webp")
    return h

for fn, lang in (("index.html", "ru"), ("index-en.html", "en"), ("index-kr.html", "ko")):
    s = open(fn, encoding="utf-8").read()
    blk = "<!--HOME-INFO-START-->\n" + localized(lang) + "\n" + ZOOM + "\n<!--HOME-INFO-END-->\n"
    if "<!--HOME-INFO-START-->" in s:
        s = re.sub(r"<!--HOME-INFO-START-->.*?<!--HOME-INFO-END-->\n", lambda m: blk, s, flags=re.S)
    else:
        i = s.index('<section id="delivery"')
        s = s[:i] + blk + "    " + s[i:]
        # в старом блоке «доставка и оплата» оставляем только способы оплаты
        j = s.index('<section id="delivery"'); k = s.index("</section>", j)
        part = s[j:k]
        part = re.sub(r'(<h2[^>]*>)[^<]*(</h2>)', lambda m: m.group(1) + PAY_H[lang] + m.group(2), part, 1)
        x = part.index('<div class="space-y-8">') + len('<div class="space-y-8">')
        y = part.index('<div class="border-t border-stone-100 pt-8">')
        part = part[:x] + "\n                " + part[y:].replace('<div class="border-t border-stone-100 pt-8">', '<div>', 1)
        # дубль заголовка «способы оплаты» внутри
        part = re.sub(r'<div class="flex gap-5 mb-6">\s*<div class="text-2xl"[^>]*>.*?</div>\s*<h4[^>]*>[^<]*</h4>\s*</div>', '', part, 1, flags=re.S)
        s = s[:j] + part + s[k:]
        s = s.replace('href="#delivery"', 'href="#info"', 1)
    open(fn, "w", encoding="utf-8").write(s)
    print("home info →", fn)

# ===== 22.10.2026: блок «🎁 Подарки к заказу» — на главных (сразу после «Основной информации»)
# и в каталогах catalog-ru/en/ko (перед товарами, после витрины SHOWCASE). Идемпотентно: <!--GIFTS-START--> … <!--GIFTS-END-->.
# Тексты = страница 3 PDF-каталога 6.0 (GIFTS в build_catalog_pdf.py), фото 25/51/101 = INFO_PICK (белые/розовые/красные).
import csv, sys
sys.path.insert(0, os.path.join(ROOT, "seo"))
from build_catalog_pdf import GIFTS, INFO_PICK, GIFT_PICK
_SLUG = {r["id"]: r["slug"] for r in csv.DictReader(open("seo/products.csv", encoding="utf-8"))}
_KICK = {"ru": "чем больше заказ — тем больше подарков", "en": "the bigger the order — the more gifts", "ko": "주문이 클수록 선물도 더 많아져요"}
_PR = {"ru": lambda v: f"{v:,}".replace(",", " ") + " ₫", "en": lambda v: f"{v:,}" + " ₫", "ko": lambda v: f"{v:,}".replace(",", " ") + " ₫"}
_CART = {"ru": "Подарки выбираются в корзине при оформлении заказа", "en": "Choose your gifts in the cart when placing the order", "ko": "선물은 장바구니에서 주문 시 선택해요"}

def gifts_html(lang):
    G, P = GIFTS[lang], _PR[lang]
    chip = lambda t: f'<span style="display:inline-block;background:#fce8ee;color:#8f4659;font-weight:700;font-size:13px;border-radius:999px;padding:4px 12px;white-space:nowrap">{t}</span>'
    li = lambda e, t: f'<li style="display:flex;gap:9px;align-items:flex-start;margin:7px 0;font-size:15px;color:#1a1a1a;line-height:1.35"><span style="font-size:18px;line-height:1.1">{e}</span><span>{t}</span></li>'
    def ph(cat, ids=None, alt=None):
        return '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:8px">' + "".join(
            f'<img src="img/products/{_SLUG[i]}/1.webp" alt="{alt or G[cat]}" loading="lazy" decoding="async" width="900" height="1200" style="width:100%;aspect-ratio:3/4;object-fit:cover;border-radius:14px">'
            for i in (ids or INFO_PICK[cat]) if i in _SLUG) + '</div>'
    def row(cat, price):
        return f'<div style="margin-top:14px"><div style="display:flex;justify-content:space-between;align-items:center;gap:8px"><b style="font-size:15px;color:#57534e">{G[cat]}</b>{chip(P(price))}</div>{ph(cat)}</div>'
    card = 'background:#fff;border:1px solid #f0e0e5;border-radius:22px;padding:20px 20px 16px;'
    h = lambda e, t: f'<h3 class="font-serif" style="font-size:21px;font-weight:700;color:#1a1a1a;margin:0;display:flex;gap:8px;align-items:center"><span>{e}</span>{t}</h3>'
    ul = lambda items: '<ul style="list-style:none;padding:0;margin:12px 0 0">' + "".join(li(e, t) for e, t in items) + '</ul>'
    inn = f'<div style="color:#a94f63;font-weight:700;font-size:13px;letter-spacing:.06em;text-transform:uppercase;margin-top:16px">{G["in"]}</div>'
    c1 = f'<div style="{card}">{h("🌹", G["t1"])}{row("r25",500000)}{row("r51",1000000)}{inn}{ul([("💌",G["card"]),("💎",G["cry"])])}</div>'
    c2 = (f'<div style="{card}">{h("🌹", G["t2"])}{row("r101",1500000)}'
          f'<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:14px"><b style="font-size:15px;color:#57534e">💐 {G["mixed"]}</b>{chip(P(1500000))}</div>{ph("mixed", GIFT_PICK["mixed"], G["mixed"])}'
          f'{inn}{ul([("💌",G["card"]),("💎",G["cry"]),("🎈",G["bal"])])}</div>')
    c3 = f'<div style="{card}">{h("🎈", G["t3"])}<div style="color:#78716c;font-size:13.5px;margin-top:4px">{G["t3s"]}</div>{ph("t3", GIFT_PICK["t3"], G["t3"])}{inn}{ul([("💌",G["card"]),("💎",G["cry"]),("🏺",G["tara"])])}</div>'
    c4 = (f'<div style="{card}background:linear-gradient(160deg,#fff7f9,#fdecf1);border:1.5px solid #c0687a;">{h("👑", G["t4"])}{ph("t4", GIFT_PICK["t4"], G["t4"])}'
          f'{inn}{ul([("💌",G["card"]),("💎",G["cry"]),("🎈",G["bt"]),("🧸",G["toy"])])}</div>')
    return ('<section id="gifts" style="padding:10px 16px 40px;max-width:1024px;margin:0 auto;width:100%;">'
            '<div style="background:linear-gradient(180deg,#fdf3f5 0%,#fff 60%);border:1px solid #f3e4e8;border-radius:28px;padding:clamp(22px,4vw,40px);">'
            f'<p style="text-align:center;font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#a94f63;margin:0 0 8px;">{_KICK[lang]}</p>'
            f'<h2 class="font-serif" style="text-align:center;font-size:clamp(28px,4.6vw,40px);font-weight:700;color:#1a1a1a;margin:0;">🎁 {G["title"]}</h2>'
            '<div style="width:90px;height:2px;background:#c9a36b;margin:14px auto 26px;"></div>'
            f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,400px),1fr));gap:16px;align-items:start">{c1}{c2}{c3}{c4}</div>'
            f'<p style="text-align:center;color:#8f4659;font-weight:600;font-size:15px;margin:22px 0 0">🧸 {G["toys"]}</p>'
            f'<p style="text-align:center;color:#78716c;font-size:13.5px;margin:6px 0 0">{_CART[lang]}</p>'
            '</div></section>')

def put_gifts(fn, lang, after):
    s = open(fn, encoding="utf-8").read()
    blk = "<!--GIFTS-START-->\n" + gifts_html(lang) + "\n<!--GIFTS-END-->\n"
    if "<!--GIFTS-START-->" in s:
        s = re.sub(r"<!--GIFTS-START-->.*?<!--GIFTS-END-->\n", lambda m: blk, s, flags=re.S)
    else:
        i = s.index(after) + len(after)
        s = s[:i] + "\n" + blk + s[i:]
    open(fn, "w", encoding="utf-8").write(s)

for fn, lang in (("index.html", "ru"), ("index-en.html", "en"), ("index-kr.html", "ko")):
    put_gifts(fn, lang, "<!--HOME-INFO-END-->\n")
for fn, lang in (("catalog-ru.html", "ru"), ("catalog-en.html", "en"), ("catalog-ko.html", "ko")):
    put_gifts(fn, lang, "<!--SHOWCASE-END-->")
print("gifts: главные + каталоги ✓")
