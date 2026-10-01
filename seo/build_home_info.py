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
