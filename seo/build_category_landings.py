#!/usr/bin/env python3
# Красивые страницы категорий (01.10.2026): Цветы / Шары / Подарки / Оформление × RU/EN/KO.
# Шаблон — balloons{,-en,-kr}.html (шапка, hero, доверие, доставка, отзывы, статьи, подвал).
# Карточки берутся из catalog-{ru,en,ko}.html (там уже width/height, «Продано» и т.п.).
# Запуск: python3 seo/build_category_landings.py   (после добавления товаров в каталог)
import re, os, sys, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SUF = {"ru": ".html", "en": "-en.html", "ko": "-kr.html"}
CAT = {"ru": "catalog-ru.html", "en": "catalog-en.html", "ko": "catalog-ko.html"}
SITE = "https://flowers-nha-trang.online/"
GRID_A = '        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">\n'

# ---------- карточки из каталога ----------
def cards_from_catalog(lang):
    s = open(CAT[lang], encoding="utf-8").read()
    i = s.index(GRID_A) + len(GRID_A)
    out = []; pos = i
    rx = re.compile(r'<div class="reveal product-card')
    while True:
        m = rx.search(s, pos)
        if not m: break
        # сбалансированный разбор div
        depth = 0; j = m.start()
        for t in re.finditer(r'<div\b|</div>', s[m.start():]):
            depth += 1 if t.group(0) == '<div' else -1
            if depth == 0:
                j = m.start() + t.end(); break
        card = s[m.start():j]
        cats = re.search(r'data-cat="([^"]*)"', card).group(1).split()
        slug = re.search(r'href="catalog/([^"]+)-(ru|en|ko)\.html"', card).group(1)
        pm = re.search(r'<p class="[^"]*font-bold[^"]*"[^>]*>([^<]*)', card)
        price = int(re.sub(r'[^0-9]', '', pm.group(1)) or 0) if pm else 0
        sold = 'sold-badge' in card
        out.append(dict(html=card, cats=cats, slug=slug, price=price, sold=sold))
        pos = j
    return out

def has(c, x): return x in c["cats"]
def toks(c): return c["slug"].split("-")
def flowerSlug(c): return any(re.match(r'^(roz|roza|rozy|buket|korzina|korzine|liliy|eustom|eustomy)$', t) for t in toks(c))
def isFlower(c): return has(c,"r25") or has(c,"r51") or has(c,"r101") or has(c,"mixed") or (has(c,"balloons") and flowerSlug(c))
def bCombo(c): return has(c,"balloons") and (isFlower(c) or has(c,"cakes"))
# шары с резиновыми (латексными) шарами — проверено по фото 01.10.2026 (тот же список в catalog-*.html, build_site.py, tg/app.js)
LATEX = ['nabor-sharov-s-2-cifry-10-sharov', '101-belaya-roza-korzina-shary-serdca', '101-belaya-roza-rozovaya-upakovka-cifry-25-sharov', '35-serebristo-chernyh-gelievyh-sharov-pod-potolok', '101-rozovaya-roza-korzina-25-persikovyh-roz-15-sharov', 'yarkaya-sbornaya-korzina-15-rozovyh-sharov', '27-cherno-belyh-rezinovyh-geliyevyh-sharov-svyazka']
LATEX_ONLY = ['35-serebristo-chernyh-gelievyh-sharov-pod-potolok', '27-cherno-belyh-rezinovyh-geliyevyh-sharov-svyazka']
def bLatex(c): return has(c,"balloons") and c["slug"] in LATEX
def isCombo(c): return len([x for x in c["cats"] if x not in ("nabory","prazdnik")]) > 1

M = {
 "r101": lambda c: has(c,"r101"), "r51": lambda c: has(c,"r51"), "r25": lambda c: has(c,"r25"),
 "mixed": lambda c: isFlower(c),
 "b-helium": lambda c: has(c,"balloons") and not bCombo(c) and c["slug"] not in LATEX_ONLY,
 "b-latex": bLatex, "b-combo": bCombo,
 "nabory": lambda c: has(c,"nabory"), "cakes": lambda c: has(c,"cakes"),
 "decor": lambda c: has(c,"prazdnik"),
}

# ---------- таймер «срочно до 17:00» (время Нячанга) ----------
CD_RX = re.compile(r"\(function\(\)\{\s*var el = document\.getElementById\('countdown'\);.*?update\(\); setInterval\(update,1000\);\s*\}\)\(\);", re.S)
CD_TXT = {'ru': ('⏱ срочный заказ на сегодня — осталось ', '⏱ срочный приём на сегодня закрыт — онлайн-заказ на завтра'), 'en': ('⏱ urgent order for today — time left ', '⏱ urgent orders for today are closed — order online for tomorrow'), 'ko': ('⏱ 오늘 긴급 주문 마감까지 ', '⏱ 오늘 긴급 주문은 마감되었습니다 — 내일 배송은 온라인 주문')}
def countdown_js(lang):
    a, b = CD_TXT[lang]
    return ("(function(){\n    var el = document.getElementById('countdown');\n    if(!el) return;\n"
      "    // время Нячанга (Asia/Ho_Chi_Minh): срочно на сегодня — через оператора до 17:00\n"
      "    function nt(){try{var f=new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Ho_Chi_Minh',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false});var p={};f.formatToParts(new Date()).forEach(function(x){p[x.type]=x.value;});return {h:+p.hour%24,m:+p.minute,s:+p.second};}catch(e){var d=new Date();return {h:d.getHours(),m:d.getMinutes(),s:d.getSeconds()};}}\n"
      "    function update(){\n        var t=nt(), sec=t.h*3600+t.m*60+t.s;\n        if(sec<7*3600||sec>=21*3600){ el.style.display='none'; return; }\n        el.style.display='';\n"
      "        if(sec>=17*3600){ el.textContent='" + b + "'; return; }\n"
      "        var diff=17*3600-sec, p=function(n){return('0'+n).slice(-2);};\n"
      "        el.textContent='" + a + "'+p(Math.floor(diff/3600))+':'+p(Math.floor(diff%3600/60))+':'+p(diff%60);\n    }\n    update(); setInterval(update,1000);\n})();")

# ---------- тексты ----------
L = {}
L["ru"] = dict(
 hours="🕐 работаем ежедневно с 07:00 до 21:00",
 sub="Онлайн-заказы доставляем со следующего дня. Срочно на сегодня — через оператора до 17:00.",
 deliv_old=["онлайн-доставка со следующего дня при заказе до 20:00."],
 deliv_new="онлайн-доставка со следующего дня; срочно на сегодня — через оператора до 17:00.",
 nav_title="Категории", all_cat="🌸 Весь каталог",
 chips={"cvety":"💐 Цветы","balloons":"🎈 Шары","podarki":"🎁 Подарки","prazdnik":"🎉 Оформление"},
 sold_note="", count=lambda n: f"{n} поз.",
)
L["en"] = dict(
 hours="🕐 open daily from 07:00 to 21:00",
 sub="Online orders are delivered from the next day. Urgent delivery today — via an operator until 17:00.",
 deliv_old=["online delivery from the next day when ordered before 20:00."],
 deliv_new="online delivery from the next day; urgent delivery today — via an operator until 17:00.",
 nav_title="Categories", all_cat="🌸 Full catalog",
 chips={"cvety":"💐 Flowers","balloons":"🎈 Balloons","podarki":"🎁 Gifts","prazdnik":"🎉 Party décor"},
 sold_note="", count=lambda n: f"{n} items",
)
L["ko"] = dict(
 hours="🕐 영업시간 07:00 ~ 21:00",
 sub="온라인 주문은 다음 날부터 배달합니다. 오늘 긴급 배송 — 17:00까지 상담원 주문.",
 deliv_old=["20:00 전 주문 시 주문 다음 날부터 배달."],
 deliv_new="온라인 주문은 다음 날부터 배달, 오늘 긴급 배송은 17:00까지 상담원 주문.",
 nav_title="카테고리", all_cat="🌸 전체 카탈로그",
 chips={"cvety":"💐 꽃","balloons":"🎈 풍선","podarki":"🎁 선물","prazdnik":"🎉 파티 데코"},
 sold_note="", count=lambda n: f"{n}개",
)

PAGES = {
 "cvety": dict(base="cvety", hero="img/products/101-krasnaya-roza-chernaya-upakovka/1.webp",
  order=["r25","r51","r101","mixed"], assign=["r101","r51","r25","mixed"],
  ru=dict(title="Цветы с доставкой в Нячанге — розы, букеты и корзины",
          desc="Букеты из 25, 51, 101 и более роз, сборные букеты и корзины с доставкой по Нячангу. Онлайн-заказ со следующего дня, срочно сегодня — через оператора до 17:00.",
          h1="Цветы с доставкой в Нячанге", wa="Здравствуйте,%20хочу%20заказать%20цветы", h2="цветы",
          sec={"r25":"25 роз","r51":"51 роза","r101":"101 роза и больше","mixed":"Сборные букеты и корзины"}),
  en=dict(title="Flower Delivery in Nha Trang — Roses, Bouquets & Baskets",
          desc="Bouquets of 25, 51, 101 and more roses, mixed bouquets and flower baskets delivered across Nha Trang. Online orders from the next day, urgent today via an operator until 17:00.",
          h1="Flower Delivery in Nha Trang", wa="Hello,%20I'd%20like%20to%20order%20flowers", h2="flowers",
          sec={"r25":"25 roses","r51":"51 roses","r101":"101 roses and more","mixed":"Mixed bouquets & baskets"}),
  ko=dict(title="나트랑 꽃 배달 — 장미 꽃다발·바구니",
          desc="장미 25·51·101송이 이상 꽃다발, 믹스 꽃다발과 꽃바구니를 나트랑 전역에 배달합니다. 온라인 주문은 다음 날부터, 오늘 긴급 배송은 17:00까지 상담원 주문.",
          h1="나트랑 꽃 배달", wa="", h2="꽃",
          sec={"r25":"장미 25송이","r51":"장미 51송이","r101":"장미 101송이 이상","mixed":"믹스 꽃다발·꽃바구니"})),
 "balloons": dict(base="balloons", hero="img/products/nabor-sharov-m-cherno-zolotoy/1.webp",
  order=["b-helium","b-latex","b-combo"], assign=["b-combo","b-latex","b-helium"], multi=True,
  ru=dict(title=None, desc=None, h1="Шары с доставкой в Нячанге", wa="Здравствуйте,%20хочу%20заказать%20шары", h2="шары",
          sec={"b-helium":"Наборы из фольгированных шаров","b-latex":"Резиновые шары","b-combo":"Шары вместе с цветами и тортом"}),
  en=dict(title=None, desc=None, h1="Balloon Delivery in Nha Trang", wa="Hello,%20I'd%20like%20to%20order%20balloons", h2="balloons",
          sec={"b-helium":"Foil balloon sets","b-latex":"Latex balloons","b-combo":"Balloons with flowers and cake"}),
  ko=dict(title=None, desc=None, h1="나트랑 풍선 배달", wa="", h2="풍선",
          sec={"b-helium":"호일 풍선 세트","b-latex":"라텍스 풍선","b-combo":"꽃·케이크와 함께하는 풍선"})),
 "podarki": dict(base="podarki", hero="img/products/podarochnyy-nabor-kofeynyy-vkus-vietnama/1.webp",
  order=["nabory","cakes"], assign=["nabory","cakes"],
  ru=dict(title="Подарки с доставкой в Нячанге — подарочные наборы и торты",
          desc="Подарочные наборы с вьетнамскими товарами и торты с доставкой по Нячангу. Онлайн-заказ со следующего дня, срочно сегодня — через оператора до 17:00.",
          h1="Подарки с доставкой в Нячанге", wa="Здравствуйте,%20хочу%20заказать%20подарок", h2="подарки",
          sec={"nabory":"Подарочные наборы","cakes":"Торты"}, note={"cakes":"Торты — только вместе с букетом, шарами или подарочным набором."}),
  en=dict(title="Gift Delivery in Nha Trang — Gift Sets & Cakes",
          desc="Gift sets with Vietnamese goods and cakes delivered across Nha Trang. Online orders from the next day, urgent today via an operator until 17:00.",
          h1="Gift Delivery in Nha Trang", wa="Hello,%20I'd%20like%20to%20order%20a%20gift", h2="gifts",
          sec={"nabory":"Gift sets","cakes":"Cakes"}, note={"cakes":"Cakes are available only together with a bouquet, balloons or a gift set."}),
  ko=dict(title="나트랑 선물 배달 — 선물 세트·케이크",
          desc="베트남 제품으로 구성한 선물 세트와 케이크를 나트랑 전역에 배달합니다. 온라인 주문은 다음 날부터, 오늘 긴급 배송은 17:00까지 상담원 주문.",
          h1="나트랑 선물 배달", wa="", h2="선물",
          sec={"nabory":"선물 세트","cakes":"케이크"}, note={"cakes":"케이크는 꽃다발, 풍선 또는 선물 세트와 함께만 주문 가능합니다."})),
 "prazdnik": dict(base="prazdnik", hero="img/site/prazdnik-banner.webp",
  order=["decor"], assign=["decor"],
  ru=dict(title=None, desc=None, h1="Оформление праздника в Нячанге", wa="Здравствуйте,%20хочу%20заказать%20готовый%20набор", h2="оформление праздника",
          sec={"decor":"Готовые наборы для оформления праздника"}),
  en=dict(title=None, desc=None, h1="Party Décor in Nha Trang", wa="Hello,%20I'd%20like%20to%20order%20a%20party%20set", h2="party décor",
          sec={"decor":"Ready-made party décor sets"}),
  ko=dict(title=None, desc=None, h1="나트랑 파티 데코", wa="", h2="파티 데코",
          sec={"decor":"파티 데코 세트"})),
}

# цифра в блоке доверия (01.10.2026, данные Олега)
TRUST = {
 "cvety":    {"n": "2000+", "ru": "букетов доставлено", "en": "bouquets delivered", "ko": "꽃다발 배달 완료"},
 "balloons": {"n": "300+",  "ru": "наборов доставлено", "en": "balloon sets delivered", "ko": "풍선 세트 배달 완료"},
 "podarki":  {"n": "300+",  "ru": "наборов и тортов доставлено", "en": "gift sets &amp; cakes delivered", "ko": "선물 세트·케이크 배달 완료"},
 "prazdnik": {"n": "25+",   "ru": "оформлений праздников", "en": "parties decorated", "ko": "파티 데코 완료"},
}
TRUST_RX = re.compile(r'(<div class="text-2xl md:text-3xl font-bold" style="color:#1a1a1a;">)[^<]*(</div>\s*<div class="text-stone-400 text-xs font-medium mt-1">)[^<]*(</div>)')

def fname(key, lang): return PAGES[key]["base"] + SUF[lang]

BAL_INFO = {
 "ru": [("🎈 Фольгированные шары", "летают в среднем 7 дней"), ("🎈 Резиновые шары", "летают в среднем 12 часов")],
 "en": [("🎈 Foil balloons", "float for about 7 days on average"), ("🎈 Latex balloons", "float for about 12 hours on average")],
 "ko": [("🎈 호일 풍선", "평균 약 7일 동안 떠 있습니다"), ("🎈 라텍스 풍선", "평균 약 12시간 동안 떠 있습니다")],
}
BAL_SEC = {"b-helium": 0, "b-latex": 1}

def section_html(key, lang, cards):
    P = PAGES[key]; T = P[lang]; Lg = L[lang]
    buckets = {k: [] for k in P["order"]}
    for c in cards:
        for k in P["assign"]:
            if M[k](c):
                buckets[k].append(c)
                if not P.get("multi"): break
    chips = []
    for k in P["order"]:
        if buckets[k]: chips.append(f'<a href="#sec-{k}" class="lnd-chip">{html.escape(T["sec"][k])}</a>')
    h = []
    h.append('    <section id="catalog" class="py-16 px-4 max-w-5xl mx-auto flex-grow">\n')
    h.append(f'        <h2 class="reveal font-serif text-3xl md:text-4xl font-bold text-center mb-6" style="color:#1a1a1a;">{html.escape(T["h2"])}</h2>\n')
    if key == "balloons":
        h.append('        <div class="lnd-bal">' + "".join('<div class="lnd-bal-i"><b>' + a + '</b><span>' + b + '</span></div>' for a, b in BAL_INFO[lang]) + '</div>\n')
    if len(chips) > 1:
        h.append('        <div class="lnd-chips">' + "".join(chips) + '</div>\n')
    for k in P["order"]:
        lst = buckets[k]
        if not lst: continue
        # чистые вперёд, потом комбо; внутри — по цене; проданные в конце
        lst.sort(key=lambda c: (c["sold"], isCombo(c) if k not in ("nabory","cakes","decor") else False, c["price"]))
        h.append(f'        <div id="sec-{k}" class="lnd-sec">\n')
        h.append(f'            <h3 class="lnd-h">{html.escape(T["sec"][k])} <span>{Lg["count"](len(lst))}</span></h3>\n')
        note = T.get("note", {}).get(k)
        if key == "balloons" and k in BAL_SEC:
            a, b = BAL_INFO[lang][BAL_SEC[k]]
            h.append('            <p class="lnd-bal-s">' + a + ' — ' + b + '</p>\n')
        if note: h.append(f'            <p class="lnd-note">{html.escape(note)}</p>\n')
        h.append(GRID_A)
        for c in lst: h.append("            " + c["html"] + "\n")
        h.append('        </div>\n        </div>\n')
    h.append('        <div class="text-center mt-10"><a href="' + CAT[lang] + '" class="lnd-all">' + Lg["all_cat"] + ' →</a></div>\n')
    h.append('    </section>\n\n')
    return "".join(h)

CSS = """<style id="lnd-css">
.lnd-chips{display:flex;flex-wrap:wrap;gap:.5rem;justify-content:center;margin:0 0 2.5rem}
.lnd-chip{display:inline-flex;align-items:center;border:1px solid #f0d0d8;background:#fff;color:#a8566a;border-radius:999px;padding:.45rem 1rem;font-size:.85rem;font-weight:500;text-decoration:none;transition:background .2s}
.lnd-chip:hover{background:#fdf4f7}
.lnd-sec{scroll-margin-top:90px;margin:0 0 3.5rem}
.lnd-h{font-family:'Cormorant Garamond',Georgia,serif;font-style:italic;font-size:1.9rem;font-weight:600;color:#1a1a1a;text-align:center;margin:0 0 .4rem;line-height:1.2}
.lnd-h span{display:block;font-family:inherit;font-style:normal;font-size:.8rem;font-weight:500;color:#a8a29e;letter-spacing:.08em;text-transform:uppercase;margin-top:.25rem}
.lnd-bal{display:flex;flex-wrap:wrap;gap:.75rem;justify-content:center;max-width:44rem;margin:-.25rem auto 2rem}
.lnd-bal-i{flex:1 1 15rem;background:#eef6fb;border:1.5px solid #9cc7df;border-radius:16px;padding:1rem 1.1rem;text-align:center;color:#1f4a63}
.lnd-bal-i b{display:block;font-size:1.05rem;font-weight:700;margin-bottom:.2rem}
.lnd-bal-i span{display:block;font-size:1.25rem;font-weight:800;color:#0f3c57}
.lnd-bal-s{text-align:center;margin:0 auto 1rem;display:table;background:#eef6fb;border:1px solid #9cc7df;color:#0f3c57;border-radius:999px;padding:.4rem 1rem;font-size:.9rem;font-weight:700}
.lnd-note{text-align:center;color:#a8566a;font-size:.85rem;margin:0 0 1.25rem}
.lnd-sec .grid{margin-top:1.25rem}
.lnd-all{display:inline-flex;align-items:center;gap:.4rem;background:#c0687a;color:#fff;border-radius:999px;padding:.8rem 1.6rem;font-weight:600;font-size:.95rem;text-decoration:none;box-shadow:0 6px 18px rgba(192,104,122,.25)}
.lnd-all:hover{background:#a8566a}
.lnd-cats{display:flex;flex-wrap:wrap;gap:.5rem;justify-content:center}
.lnd-cats a{display:inline-flex;align-items:center;border:1px solid #e7e5e4;border-radius:999px;padding:.45rem 1rem;font-size:.8rem;font-weight:500;color:#57534e;background:#fff;text-decoration:none}
.lnd-cats a.on{border-color:#c0687a;background:#c0687a;color:#fff}
.lnd-cats a:hover{border-color:#c0687a}
</style>
"""

def build(key, lang):
    P = PAGES[key]; T = P[lang]; Lg = L[lang]
    tpl = open("balloons" + SUF[lang], encoding="utf-8").read()
    s = tpl
    out = fname(key, lang)
    if key != "balloons":
        for lg in ("ru", "en", "ko"):
            s = s.replace("balloons" + SUF[lg], fname(key, lg))
    # head
    if key in ("prazdnik",):
        old = open(out, encoding="utf-8").read()
        title = re.search(r"<title>(.*?)</title>", old, re.S).group(1)
        desc = re.search(r'name="description" content="([^"]*)"', old).group(1)
        ttl_raw, desc_raw = title, desc
    elif T["title"]:
        ttl_raw, desc_raw = html.escape(T["title"], quote=True), html.escape(T["desc"], quote=True)
    else:
        ttl_raw = re.search(r"<title>(.*?)</title>", s, re.S).group(1)
        desc_raw = re.search(r'name="description" content="([^"]*)"', s).group(1)
    s = re.sub(r"<title>.*?</title>", "<title>" + ttl_raw + "</title>", s, 1, flags=re.S)
    for attr in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
        s = re.sub(r'(<meta ' + attr + r' content=")[^"]*', lambda m: m.group(1) + desc_raw, s, 1)
    for attr in ('property="og:title"', 'name="twitter:title"'):
        s = re.sub(r'(<meta ' + attr + r' content=")[^"]*', lambda m: m.group(1) + ttl_raw, s, 1)
    s = re.sub(r'("description": ")[^"]*(")', lambda m: m.group(1) + html.unescape(desc_raw).replace('"', "'") + m.group(2), s, 1)
    # stale: доставка «со следующего дня» в JSON-LD/описании оставляем — это про онлайн.
    # hero
    a = s.index("<h1"); b = s.index("</h1>", a)
    h1open = s[a:s.index(">", a) + 1]
    s = s[:a] + h1open + "\n                    " + html.escape(T["h1"]) + "\n                " + s[b:]
    s = re.sub(r'(<p class="text-stone-700 text-sm md:text-base mb-2 hero-animate-delay">)[^<]*(</p>)', lambda m: m.group(1) + Lg["sub"] + m.group(2), s, 1)
    s = re.sub(r'(<p class="text-xs mb-1 hero-animate-delay" style="color:#c0687a;">)\s*[^<]*?(\s*</p>)', lambda m: m.group(1) + "\n                    " + Lg["hours"] + m.group(2), s, 1)
    hi = s.index('<div class="md:w-1/2 h-64 md:h-auto overflow-hidden">')
    im = re.compile(r'<img [^>]*>').search(s, hi)
    alt = html.escape(T["h1"], quote=True)
    newimg = f'<img src="{P["hero"]}" alt="{alt}" class="w-full h-full object-cover" width="900" height="1200" fetchpriority="high" decoding="async">'
    s = s[:im.start()] + newimg + s[im.end():]
    s = re.sub(r'<link rel="preload" as="image" href="[^"]*" fetchpriority="high">', f'<link rel="preload" as="image" href="{P["hero"]}" fetchpriority="high">', s, 1)
    # текст для WhatsApp/Telegram
    if T["wa"]:
        s = re.sub(r"text=(Здравствуйте|Hello)[^\"&]*", "text=" + T["wa"], s)
    # якоря → навигация по категориям
    ci = s.index('<section id="catalog"')
    ai = s.rfind('<div class="py-4 px-4 border-b border-stone-100">', 0, ci)
    links = "".join(f'<a href="{fname(k, lang)}"' + (' class="on"' if k == key else "") + f'>{Lg["chips"][k]}</a>' for k in ("cvety", "balloons", "podarki", "prazdnik"))
    links += f'<a href="{CAT[lang]}">{Lg["all_cat"]}</a>'
    nav = '<div class="py-4 px-4 border-b border-stone-100">\n        <nav class="max-w-4xl mx-auto lnd-cats" aria-label="' + Lg["nav_title"] + '">' + links + '</nav>\n    </div>\n\n    '
    s = s[:ai] + nav + s[ci:]
    # каталог
    ci = s.index('<section id="catalog"')
    di = s.index('<section id="delivery"', ci)
    di = s.rfind("\n", 0, di) + 1
    # оставить комментарий «Доставка и оплата», если он стоял перед секцией
    pre = s[ci:di]
    cm = pre.rfind("<!--")
    keep = pre[cm:] if cm > pre.rfind("</section>") else ""
    s = s[:ci] + section_html(key, lang, cards_from_catalog(lang)) + keep + s[di:]
    # доставка
    for o in Lg["deliv_old"]: s = s.replace(o, Lg["deliv_new"])
    s = CD_RX.sub(lambda m: countdown_js(lang), s, 1)
    tr = TRUST[key]
    s = TRUST_RX.sub(lambda m: m.group(1) + tr["n"] + m.group(2) + tr[lang] + m.group(3), s, 1)
    # css
    s = re.sub(r'<style id="lnd-css">.*?</style>\n', '', s, flags=re.S)
    s = s.replace("</head>", CSS + "</head>", 1)
    open(out, "w", encoding="utf-8").write(s)
    return out

if __name__ == "__main__":
    # balloons* — шаблон и одновременно результат; генератор идемпотентный, поэтому balloons строим ПОСЛЕДНИМ.
    for key in ("cvety", "podarki", "prazdnik", "balloons"):
        for lang in ("ru", "en", "ko"):
            print("written", build(key, lang))
