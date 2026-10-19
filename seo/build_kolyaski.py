#!/usr/bin/env python3
"""build_kolyaski.py — лендинг «Аренда детских колясок» RU/EN/KO (19.10.2026).

kolyaski*.html — ГЛАВНАЯ раздела (как torty/balloons): сетка позиций (коляски, манежи…) + условия.
catalog/<slug>-<ru|en|ko>.html — страница каждой позиции (фото, цены, характеристики, условия).
Шапка/подвал: раздел — из podarki*.html, позиция — из catalog/25-rozovyh-roz-*.html.
Новая позиция: добавить словарь в STROLLERS (+ фото в img/products/<slug>/) и перезапустить скрипт.
Цены аренды — PRICES (VND), ₽/$ считаются по правилам сайта (₽ курс 270 вверх до 100, $ = /25000).
"""
import os, re, math, json, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://flowers-nha-trang.online"
PRICES = [(1, 300000), (2, 400000), (3, 500000), (4, 650000), (5, 750000), (6, 900000), (7, 1000000)]

STROLLERS = [{
    "slug": "arenda-detskoy-kolyaski-capella",
    "photos": 14,
    "prices": PRICES,
    "cover": 2,   # обложка раздела/карточки — полубоком (порядок фото: сбоку, полубоком, … сложенная последней)
    "name": {"ru": "Прогулочная коляска Capella (бирюзовая)",
             "en": "Capella stroller (turquoise)",
             "ko": "카펠라 유모차 (청록색)"},
}]

def rub(v): return math.ceil(v / 270 / 100) * 100
def usd(v): return round(v / 25000)
def vnd(v): return f"{v:,}".replace(",", " ")

FILES = {"ru": "kolyaski.html", "en": "kolyaski-en.html", "ko": "kolyaski-kr.html"}
SRC = {"ru": "podarki.html", "en": "podarki-en.html", "ko": "podarki-kr.html"}

T = {
 "ru": {
  "title": "Аренда детских колясок в Нячанге с доставкой в отель",
  "desc": "Аренда детской коляски в Нячанге без залога: привезём в отель в центре Нячанга и заберём обратно. От 300 000 ₫ в день, 7 дней — 1 000 000 ₫.",
  "eyebrow": "Нячанг · Вьетнам",
  "h1": "Аренда детских колясок в Нячанге",
  "h1s": "с доставкой в отель в центре Нячанга",
  "lead": "Привезём коляску к вашему отелю и заберём обратно. Без залога и депозита.",
  "btn": "Заказать в", "wa_text": "Здравствуйте, хочу арендовать детскую коляску",
  "feat_h": "Что умеет коляска",
  "feat": ["🔄 Перекидная ручка: малыш едет лицом к вам или лицом вперёд",
           "🛏 Спинка опускается: можно сидеть или спать лёжа",
           "☂️ Большой капюшон со смотровым окошком",
           "🔒 5-точечные ремни безопасности и защитный бампер",
           "📦 Компактно складывается и стоит в сложенном виде",
           "🛞 Двойные колёса — 8 колёс"],
  "price_h": "Цены аренды", "days": ["1 день", "2 дня", "3 дня", "4 дня", "5 дней", "6 дней", "7 дней"],
  "col": ["Срок", "Цена", "≈ за день"],
  "rules_h": "Условия аренды",
  "rules": [
   "<b>Без залога и депозита.</b>",
   "<b>Доставка и забор — бесплатно, только по центру Нячанга</b> (зона «Центр» на нашей карте). Привозим к отелю и забираем из отеля — или в любое удобное для вас место в центре.",
   "<b>Оплата — 100% суммы, когда мы привозим коляску.</b>",
   "<b>При получении сообщите нам:</b> название отеля, номер комнаты, имя и фамилию на английском (как при заселении). Залога нет — эти данные нужны, чтобы мы знали, где находится коляска.",
   "<b>Вернуть можно через ресепшен.</b> Если вам неудобно встречаться с нами — оставьте коляску на ресепшене отеля и пришлите нам фото. Мы приедем и заберём её. Для этого нужны номер комнаты и имя-фамилия — мы покажем их на ресепшене.",
  ],
  "map_alt": "Карта: центр Нячанга — зона бесплатной доставки колясок",
  "map_cap": "Зона доставки колясок — центр Нячанга",
  "how_h": "Как заказать",
  "how": ["Напишите нам в WhatsApp, Telegram или Instagram", "Укажите даты, отель и номер комнаты, имя и фамилию на английском", "Привезём коляску к отелю — оплата при получении"],
  "gal": "фото", "back": "Весь каталог",
  "chip": "👶 Коляски",
 },
 "en": {
  "title": "Baby Stroller Rental in Nha Trang with Hotel Delivery",
  "desc": "Baby stroller rental in Nha Trang with no deposit: we deliver to your hotel in central Nha Trang and pick it up. From 300,000 VND per day, 7 days — 1,000,000 VND.",
  "eyebrow": "Nha Trang · Vietnam",
  "h1": "Baby Stroller Rental in Nha Trang",
  "h1s": "with delivery to your hotel in central Nha Trang",
  "lead": "We bring the stroller to your hotel and pick it up afterwards. No deposit.",
  "btn": "Order via", "wa_text": "Hello, I'd like to rent a baby stroller",
  "feat_h": "Stroller features",
  "feat": ["🔄 Reversible handle: baby faces you or faces forward",
           "🛏 Reclining backrest: sit up or sleep lying down",
           "☂️ Large canopy with a peek-a-boo window",
           "🔒 5-point safety harness and bumper bar",
           "📦 Folds compactly and stands when folded",
           "🛞 Double wheels — 8 wheels"],
  "price_h": "Rental prices", "days": ["1 day", "2 days", "3 days", "4 days", "5 days", "6 days", "7 days"],
  "col": ["Period", "Price", "≈ per day"],
  "rules_h": "Rental terms",
  "rules": [
   "<b>No deposit.</b>",
   "<b>Free delivery and pick-up — central Nha Trang only</b> (the “Center” zone on our map). We deliver to and collect from your hotel — or any convenient place in the center.",
   "<b>Payment — 100% of the amount when we deliver the stroller.</b>",
   "<b>When you receive it, please tell us:</b> your hotel name, room number, and your first and last name in English (as at check-in). There is no deposit, so we need this to know where the stroller is.",
   "<b>You can return it via the reception.</b> If it’s not convenient to meet us, leave the stroller at the hotel reception and send us a photo. We will come and pick it up. For this we need your room number and name — we show them at the reception.",
  ],
  "map_alt": "Map: central Nha Trang — free stroller delivery zone",
  "map_cap": "Stroller delivery zone — central Nha Trang",
  "how_h": "How to order",
  "how": ["Message us on WhatsApp, Telegram or Instagram", "Tell us your dates, hotel, room number and your name in English", "We bring the stroller to your hotel — pay on delivery"],
  "gal": "photos", "back": "Full catalog",
  "chip": "👶 Strollers",
 },
 "ko": {
  "title": "나트랑 유모차 대여 — 시내 호텔로 배달",
  "desc": "나트랑 유모차 대여, 보증금 없음: 나트랑 시내 호텔로 배달하고 다시 수거합니다. 1일 300,000동부터, 7일 1,000,000동.",
  "eyebrow": "나트랑 · 베트남",
  "h1": "나트랑 유모차 대여",
  "h1s": "나트랑 시내 호텔로 배달",
  "lead": "유모차를 호텔로 가져다 드리고 다시 수거합니다. 보증금이 없습니다.",
  "btn": "주문하기", "wa_text": "",
  "feat_h": "유모차 특징",
  "feat": ["🔄 양대면 핸들: 아기가 부모를 보거나 앞을 보고 탑니다",
           "🛏 등받이 조절: 앉거나 누워서 잘 수 있습니다",
           "☂️ 확인 창이 있는 넓은 차양",
           "🔒 5점식 안전벨트와 안전바",
           "📦 컴팩트하게 접히고 접은 상태로 세워집니다",
           "🛞 더블 바퀴 — 바퀴 8개"],
  "price_h": "대여 요금", "days": ["1일", "2일", "3일", "4일", "5일", "6일", "7일"],
  "col": ["기간", "요금", "≈ 1일당"],
  "rules_h": "대여 조건",
  "rules": [
   "<b>보증금이 없습니다.</b>",
   "<b>배달과 수거는 무료 — 나트랑 시내만 가능합니다</b> (지도의 ‘시내’ 구역). 호텔로 배달하고 호텔에서 수거합니다 — 또는 시내의 편한 장소에서.",
   "<b>결제 — 유모차를 배달할 때 전액(100%) 결제합니다.</b>",
   "<b>받으실 때 알려 주세요:</b> 호텔 이름, 객실 번호, 영문 이름과 성(체크인 시와 동일). 보증금이 없기 때문에 유모차의 위치를 알기 위해 필요합니다.",
   "<b>리셉션을 통해 반납할 수 있습니다.</b> 만나기 어려우시면 호텔 리셉션에 유모차를 맡기고 사진을 보내 주세요. 저희가 가서 수거합니다. 이를 위해 객실 번호와 이름이 필요합니다 — 리셉션에 보여 드립니다.",
  ],
  "map_alt": "지도: 나트랑 시내 — 유모차 무료 배달 구역",
  "map_cap": "유모차 배달 구역 — 나트랑 시내",
  "how_h": "주문 방법",
  "how": ["카카오톡 또는 인스타그램으로 메시지를 보내 주세요", "날짜, 호텔, 객실 번호, 영문 이름을 알려 주세요", "호텔로 유모차를 가져다 드립니다 — 받을 때 결제"],
  "gal": "사진", "back": "전체 카탈로그",
  "chip": "👶 유모차",
 },
}

ICON = {}
def icons(src):
    for k, pat in (("wa", r'<svg[^>]*viewBox="0 0 24 24"[^>]*><path d="M17\.472.*?</svg>'),
                   ("tg", r'<svg[^>]*viewBox="0 0 24 24"[^>]*><path d="M11\.944.*?</svg>'),
                   ("ig", r'<svg[^>]*viewBox="0 0 24 24"[^>]*><path d="M12 2\.163.*?</svg>')):
        m = re.search(pat, src, re.S)
        if m: ICON[k] = m.group(0)

def buttons(lang, t):
    if lang == "ko":
        items = [("http://pf.kakao.com/_zbwKX", "💬 KakaoTalk"), ("https://instagram.com/nhatrang.kkot", ICON.get("ig", "") + " Instagram")]
    else:
        q = t["wa_text"].replace(" ", "%20")
        items = [(f"https://wa.me/37443529162?text={q}", ICON.get("wa", "") + " WhatsApp"),
                 (f"https://t.me/babaskin_o?text={q}", ICON.get("tg", "") + " Telegram"),
                 ("https://instagram.com/flowers_vietnam_inst", ICON.get("ig", "") + " Instagram")]
    return "".join(f'<a href="{u}" target="_blank" rel="noopener noreferrer" class="kl-btn">{l}</a>' for u, l in items)

CSS = """<style id="kl-css">
.kl-hero{background:linear-gradient(180deg,#fff 0%,#fdf4f7 100%);padding:28px 16px 36px}
.kl-in{max-width:64rem;margin:0 auto}
.kl-top{display:grid;grid-template-columns:1fr 1fr;gap:28px;align-items:start}
.kl-eb{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:#c0687a;margin:0 0 10px}
.kl-h1{font-family:Georgia,'Playfair Display',serif;font-style:italic;font-weight:500;font-size:clamp(30px,4vw,46px);line-height:1.12;color:#1a1a1a;margin:0 0 10px}
.kl-h1 span{display:block;font-size:.55em;color:#a8566a;margin-top:10px;line-height:1.25}
.kl-lead{color:#57534e;font-size:15px;line-height:1.5;margin:0 0 16px}
.kl-badges{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 18px}
.kl-badges span{background:#fff;border:1px solid #f0d0d8;color:#a8566a;border-radius:999px;padding:6px 12px;font-size:13px;font-weight:600}
.kl-btns{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px}
.kl-btn{display:flex;align-items:center;justify-content:center;gap:6px;border:1.5px solid #c0687a;color:#c0687a;background:#fff;border-radius:12px;padding:12px 10px;font-weight:600;font-size:14px;text-decoration:none;transition:.2s}
.kl-btn:hover{background:#c0687a;color:#fff}
.kl-gal{position:relative;border-radius:20px;overflow:hidden;background:#fff;border:1px solid #f0d0d8;box-shadow:0 6px 24px rgba(192,104,122,.08)}
.kl-track{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;aspect-ratio:3/4}
.kl-track::-webkit-scrollbar{display:none}
.kl-track img{flex:0 0 100%;width:100%;height:100%;object-fit:cover;scroll-snap-align:start}
.kl-arr{position:absolute;top:50%;transform:translateY(-50%);width:40px;height:40px;border-radius:50%;border:none;background:rgba(255,255,255,.95);color:#a8566a;font-size:24px;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.2)}
.kl-prev{left:8px}.kl-next{right:8px}
.kl-cnt{position:absolute;top:10px;right:10px;background:rgba(0,0,0,.45);color:#fff;font-size:12px;border-radius:999px;padding:3px 9px}
.kl-name{text-align:center;font-weight:600;color:#1a1a1a;padding:10px;font-size:15px}
.kl-sec{max-width:64rem;margin:0 auto;padding:36px 16px 8px}
.kl-h2{font-family:'Cormorant Garamond',Georgia,serif;font-style:italic;font-weight:600;font-size:2rem;text-align:center;color:#1a1a1a;margin:0 0 18px}
.kl-feat{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px;list-style:none;padding:0;margin:0}
.kl-feat li{background:#fff;border:1px solid #f0e0e5;border-radius:14px;padding:12px 14px;font-size:14px;color:#44403c}
.kl-tbl{width:100%;max-width:34rem;margin:0 auto;border-collapse:separate;border-spacing:0;background:#fff;border:1px solid #f0d0d8;border-radius:16px;overflow:hidden;font-size:15px}
.kl-tbl th{background:#fce8ee;color:#a8566a;font-weight:600;padding:10px;text-align:left}
.kl-tbl td{padding:10px;border-top:1px solid #f5ecee;color:#44403c}
.kl-tbl td b{color:#1a1a1a}.kl-tbl td small{color:#a8a29e;display:block;font-size:12px}
.kl-rules{list-style:none;counter-reset:r;padding:0;margin:0 auto;max-width:46rem;display:flex;flex-direction:column;gap:10px}
.kl-rules li{counter-increment:r;position:relative;background:#fff;border:1px solid #f0e0e5;border-radius:14px;padding:12px 14px 12px 50px;font-size:14px;line-height:1.5;color:#44403c}
.kl-rules li:before{content:counter(r);position:absolute;left:14px;top:12px;width:24px;height:24px;border-radius:50%;background:#c0687a;color:#fff;font-weight:700;font-size:13px;display:flex;align-items:center;justify-content:center}
.kl-map{max-width:22rem;margin:18px auto 0;text-align:center}
.kl-map img{width:100%;height:auto;border-radius:14px;border:1px solid #f0d0d8}
.kl-map p{font-size:13px;color:#a8566a;margin:6px 0 0}
.kl-how{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;list-style:none;padding:0;margin:0 0 18px}
.kl-how li{background:#fdf4f7;border-radius:14px;padding:14px;font-size:14px;color:#44403c;text-align:center}
.kl-how li b{display:block;color:#c0687a;font-size:20px;margin-bottom:4px}
@media(max-width:820px){.kl-top{grid-template-columns:1fr}.kl-gal{order:-1}.kl-hero{padding-top:14px}}
</style>"""

JS = """<script>
(function(){var g=document.querySelector('.kl-gal');if(!g)return;var t=g.querySelector('.kl-track'),c=g.querySelector('.kl-cnt'),n=t.children.length;
function i(){return Math.round(t.scrollLeft/t.clientWidth);}function go(k){k=(k+n)%n;t.scrollTo({left:k*t.clientWidth,behavior:'smooth'});}
t.addEventListener('scroll',function(){c.textContent=(i()+1)+' / '+n;},{passive:true});
g.querySelector('.kl-prev').onclick=function(){go(i()-1);};g.querySelector('.kl-next').onclick=function(){go(i()+1);};})();
</script>"""

EXTRA = {
 "ru": {"items_h": "Коляски и манежи в аренду", "more": "Подробнее →", "per_day": "/ день", "from": "от", "home": "Главная", "cat": "Аренда колясок", "order_h": "Заказать"},
 "en": {"items_h": "Strollers & playpens for rent", "more": "Details →", "per_day": "/ day", "from": "from", "home": "Home", "cat": "Stroller rental", "order_h": "Order"},
 "ko": {"items_h": "대여 유모차·놀이울", "more": "자세히 →", "per_day": "/ 1일", "from": "", "home": "홈", "cat": "유모차 대여", "order_h": "주문하기"},
}
CSS2 = """<style id="kl-css2">
.kl-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:18px;max-width:64rem;margin:0 auto}
.kl-card{display:block;background:#fff;border:1px solid #f0e0e5;border-radius:18px;overflow:hidden;text-decoration:none;color:#1a1a1a;transition:.2s}
.kl-card:hover{border-color:#c0687a;box-shadow:0 6px 24px rgba(192,104,122,.12)}
.kl-card img{width:100%;aspect-ratio:3/4;object-fit:cover;display:block}
.kl-card div{padding:12px 14px 14px}.kl-card b{display:block;font-size:15px;margin-bottom:4px}
.kl-card i{display:block;font-style:normal;color:#c0687a;font-weight:700;margin-bottom:10px}
.kl-card span{display:block;text-align:center;border:1.5px solid #c0687a;color:#c0687a;border-radius:12px;padding:9px;font-weight:600;font-size:14px}
.kl-crumbs{max-width:64rem;margin:0 auto;padding:12px 16px 0;font-size:12px;color:#a8a29e}.kl-crumbs a{color:#a8566a;text-decoration:none}
.kl-hero-img{border-radius:20px;overflow:hidden;border:1px solid #f0d0d8}.kl-hero-img img{width:100%;aspect-ratio:3/4;object-fit:cover;display:block}
</style>"""

def price_rows(lang, t, prices):
    out = ""
    for d, v in prices:
        per = round(v / d / 1000) * 1000
        if lang == "ru":
            out += f'<tr><td><b>{t["days"][d-1]}</b></td><td><b>{vnd(v)} ₫</b><small>≈ ${usd(v)} · {vnd(rub(v))} ₽</small></td><td>{vnd(per)} ₫</td></tr>'
        else:
            out += f'<tr><td><b>{t["days"][d-1]}</b></td><td><b>{v:,} ₫</b><small>≈ ${usd(v)}</small></td><td>{per:,} ₫</td></tr>'
    return out

def money(lang, v): return f"{vnd(v)} ₫" if lang == "ru" else f"{v:,} ₫"

def parts(srcfile):
    src = open(os.path.join(ROOT, srcfile), encoding="utf-8").read()
    icons(src)
    head = src[:src.index("</head>")]
    b = src.index("<body")
    header = src[b:src.index("</header>", b) + len("</header>")]
    footer = src[src.index('<footer class="sf"'):]
    return head, header, footer

def fix_head(head, title, desc, url, img, ld, pre, cleanup_urls):
    head = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", head, flags=re.S)
    head = re.sub(r'(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*', lambda m: m.group(1) + html.escape(desc), head)
    head = re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*', lambda m: m.group(1) + html.escape(title), head)
    head = re.sub(r'(<meta (?:property="og:image"|name="twitter:image") content=")[^"]*', lambda m: m.group(1) + img, head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, head)
    for a, b2 in cleanup_urls:
        head = head.replace(a, b2)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', "", head, flags=re.S)
    head = re.sub(r'<link rel="preload" as="image"[^>]*>', "", head)
    head = re.sub(r'<style id="lnd-css">.*?</style>', "", head, flags=re.S)
    return head + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>\n" + pre + CSS + "\n" + CSS2 + "\n"

PFILES = lambda slug: {l: f"catalog/{slug}-{l}.html" for l in ("ru", "en", "ko")}

def rules_block(t, zimg):
    return (f'<section class="kl-sec"><h2 class="kl-h2">{t["rules_h"]}</h2><ol class="kl-rules">' + "".join(f"<li>{r}</li>" for r in t["rules"]) + "</ol>"
            + (f'<div class="kl-map"><img src="{zimg}" alt="{t["map_alt"]}" width="900" height="1040" loading="lazy" decoding="async"><p>{t["map_cap"]}</p></div>' if zimg else "") + "</section>")

def how_block(lang, t):
    return (f'<section class="kl-sec" style="padding-bottom:48px"><h2 class="kl-h2">{t["how_h"]}</h2><ol class="kl-how">'
            + "".join(f"<li><b>{i}</b>{h}</li>" for i, h in enumerate(t["how"], 1)) + f'</ol><div class="kl-btns" style="max-width:34rem;margin:0 auto">{buttons(lang, t)}</div></section>')

def category(lang):
    t, x = T[lang], EXTRA[lang]
    head, header, footer = parts(SRC[lang])
    fn = FILES[lang]; url = f"{DOMAIN}/{fn}"
    for l2 in ("ru", "en", "ko"):
        header = header.replace(f'href="{SRC[l2]}" style="padding:3px', f'href="{FILES[l2]}" style="padding:3px')
    bal = {"ru": "balloons.html", "en": "balloons-en.html", "ko": "balloons-kr.html"}[lang]
    header = re.sub(r'href="podarki(?:-en|-kr)?\.html"((?: class| style)="[^"]*">🎈)', lambda m: f'href="{bal}"' + m.group(1), header)
    s0 = STROLLERS[0]
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": t["h1"], "url": url,
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{DOMAIN}/{PFILES(s['slug'])[lang]}", "name": s["name"][lang]} for i, s in enumerate(STROLLERS)]}
    cl = [(f'/{SRC[lang]}"', f'/{fn}"')] + [(f'{DOMAIN}/{SRC[l2]}"', f'{DOMAIN}/{FILES[l2]}"') for l2 in ("ru", "en", "ko")]
    head = fix_head(head, t["title"], t["desc"], url, f"{DOMAIN}/img/products/{s0['slug']}/1.jpg", ld,
                    f'<link rel="preload" as="image" href="img/products/{s0["slug"]}/{s0.get("cover",1)}.webp" fetchpriority="high">\n', cl)
    p1 = money(lang, min(v for s in STROLLERS for _, v in s["prices"]))
    badges = {"ru": ["✅ Без залога", "🏨 Доставка в отель", "💵 Оплата при получении", f"от {p1} / день"],
              "en": ["✅ No deposit", "🏨 Hotel delivery", "💵 Pay on delivery", f"from {p1} / day"],
              "ko": ["✅ 보증금 없음", "🏨 호텔 배달", "💵 받을 때 결제", f"1일 {p1}부터"]}[lang]
    cards = ""
    for s in STROLLERS:
        pv = money(lang, s["prices"][0][1])
        price = f"{x['from']} {pv} {x['per_day']}".strip()
        cards += (f'<a class="kl-card" href="{PFILES(s["slug"])[lang]}"><img src="img/products/{s["slug"]}/{s.get("cover",1)}.webp" alt="{html.escape(s["name"][lang])}" width="960" height="1280" loading="lazy" decoding="async">'
                  f'<div><b>{html.escape(s["name"][lang])}</b><i>{price}</i><span>{x["more"]}</span></div></a>')
    content = f"""
<main>
<section class="kl-hero"><div class="kl-in kl-top">
  <div>
    <p class="kl-eb">{t['eyebrow']}</p>
    <h1 class="kl-h1">{t['h1']}<span>{t['h1s']}</span></h1>
    <p class="kl-lead">{t['lead']}</p>
    <div class="kl-badges">{''.join(f'<span>{b}</span>' for b in badges)}</div>
    <div class="kl-btns">{buttons(lang, t)}</div>
  </div>
  <a class="kl-hero-img" href="#items"><img src="img/products/{s0['slug']}/{s0.get('cover',1)}.webp" alt="{html.escape(t['h1'])}" width="960" height="1280" fetchpriority="high" decoding="async"></a>
</div></section>
<section class="kl-sec" id="items"><h2 class="kl-h2">{x['items_h']}</h2><div class="kl-grid">{cards}</div></section>
{rules_block(t, f"img/site/zones/zone-center-{lang}.webp")}
{how_block(lang, t)}
</main>
"""
    out = head + "</head>\n" + header + "\n" + content + "\n    " + footer
    open(os.path.join(ROOT, fn), "w", encoding="utf-8").write(out); print("OK", fn)

def product(lang, s):
    t, x = T[lang], EXTRA[lang]
    srcp = f"catalog/25-rozovyh-roz-{lang}.html"
    head, header, footer = parts(srcp)
    header = re.sub(r'<script type="application/ld\+json">.*?</script>', "", header, flags=re.S)
    files = PFILES(s["slug"]); fn = files[lang]; url = f"{DOMAIN}/{fn}"
    for l2 in ("ru", "en", "ko"):
        header = header.replace(f'href="25-rozovyh-roz-{l2}.html"', f'href="{s["slug"]}-{l2}.html"')
    cl = [(f"{DOMAIN}/catalog/25-rozovyh-roz-{l2}.html\"", f"{DOMAIN}/{files[l2]}\"") for l2 in ("ru", "en", "ko")]
    name = s["name"][lang]
    title = f"{name} — {t['h1']}"
    desc = f"{name}. " + t["desc"]
    ld = {"@context": "https://schema.org", "@type": "Product", "name": name, "brand": {"@type": "Brand", "name": s.get("brand", "Capella")},
          "image": [f"{DOMAIN}/img/products/{s['slug']}/{i}.webp" for i in range(1, 4)], "description": desc, "url": url,
          "offers": {"@type": "AggregateOffer", "priceCurrency": "VND", "lowPrice": s["prices"][0][1], "highPrice": s["prices"][-1][1], "offerCount": len(s["prices"]),
                     "availability": "https://schema.org/InStock", "seller": {"@type": "Organization", "name": "Surprise Service Nha Trang"}}}
    head = fix_head(head, title, desc, url, f"{DOMAIN}/img/products/{s['slug']}/1.jpg", ld,
                    f'<link rel="preload" as="image" href="../img/products/{s["slug"]}/1.webp" fetchpriority="high">\n', cl)
    imgs = "".join(f'<img src="../img/products/{s["slug"]}/{i}.webp" alt="{html.escape(name)} — {i}" width="960" height="1280" loading="{"eager" if i == 1 else "lazy"}" decoding="async">' for i in range(1, s["photos"] + 1))
    gal = (f'<div class="kl-gal"><div class="kl-track">{imgs}</div><button type="button" class="kl-arr kl-prev" aria-label="‹">‹</button>'
           f'<button type="button" class="kl-arr kl-next" aria-label="›">›</button><span class="kl-cnt">1 / {s["photos"]}</span></div>')
    catf = "../" + FILES[lang]; homef = "../" + {"ru": "index.html", "en": "index-en.html", "ko": "index-kr.html"}[lang]
    pv = money(lang, s["prices"][0][1])
    content = f"""
<main>
<nav class="kl-crumbs"><a href="{homef}">{x['home']}</a> › <a href="{catf}">{x['cat']}</a> › {html.escape(name)}</nav>
<section class="kl-hero"><div class="kl-in kl-top">
  {gal}
  <div>
    <p class="kl-eb">{t['eyebrow']}</p>
    <h1 class="kl-h1" style="font-size:clamp(26px,3.2vw,38px)">{html.escape(name)}<span>{t['h1s']}</span></h1>
    <p class="kl-lead" style="font-size:22px;font-weight:700;color:#c0687a">{(x['from'] + ' ' + pv + ' ' + x['per_day']).strip()}</p>
    <ul class="kl-feat" style="grid-template-columns:1fr;margin-bottom:16px">{''.join(f'<li>{f}</li>' for f in t['feat'])}</ul>
    <div class="kl-btns">{buttons(lang, t)}</div>
  </div>
</div></section>
<section class="kl-sec"><h2 class="kl-h2">{t['price_h']}</h2>
<table class="kl-tbl"><thead><tr>{''.join(f'<th>{c}</th>' for c in t['col'])}</tr></thead><tbody>{price_rows(lang, t, s['prices'])}</tbody></table></section>
{rules_block(t, f"../img/site/zones/zone-center-{lang}.webp")}
{how_block(lang, t)}
</main>
"""
    out = head + "</head>\n" + header + "\n" + content + "\n    " + footer
    out = out.replace("</body>", JS + "\n</body>", 1)
    open(os.path.join(ROOT, fn), "w", encoding="utf-8").write(out); print("OK", fn)

if __name__ == "__main__":
    for l in ("ru", "en", "ko"):
        category(l)
        for s in STROLLERS:
            product(l, s)
