# -*- coding: utf-8 -*-
"""Авторские статьи (автор — Оксана Яснова). Запуск из корня репо: python3 seo/build_author_articles.py
Делает: 1) страницу статьи «Веранда» RU/EN/KO из шаблона статьи кафе X.O; 2) во ВСЕХ авторских статьях —
подпись под заголовком, «Автор: …», блок «Об авторе», «Читайте также», JSON-LD с автором-Person;
3) страницу автора blog/avtor-oksana-yasnova-{ru,en,ko}.html со списком всех статей из REG.
Новая авторская статья: добавить запись в REG (и модуль с контентом) → запустить → карточка на blog-*, sitemap — вручную.
Фото автора: положить img/blog/avtor-oksana-yasnova.webp (квадрат) → перезапустить — подставится вместо инициалов."""
import io, os, re, json, sys, html
sys.path.insert(0, os.path.dirname(__file__))
import author_veranda_content as V
SITE = "https://flowers-nha-trang.online"
XO = "gde-poest-moreprodukty-nyachang-kafe-xo"
AU = "avtor-oksana-yasnova"
LANGS = ("ru", "en", "ko")
NAME = {"ru": "Оксана Яснова", "en": "Oksana Yasnova", "ko": "옥사나 야스노바"}
BIO = {"ru": "Меня зовут Оксана Яснова. Я живу в Нячанге, занимаюсь бизнесом и люблю открывать для себя новые места. Посещаю рестораны, останавливаюсь в отелях, изучаю город и делюсь своими впечатлениями, фотографиями и наблюдениями.",
       "en": "My name is Oksana Yasnova. I live in Nha Trang, run a business and love discovering new places. I visit restaurants, stay in hotels, explore the city and share my impressions, photos and observations.",
       "ko": "제 이름은 옥사나 야스노바입니다. 나트랑에 살며 사업을 하고, 새로운 장소를 발견하는 것을 좋아합니다. 레스토랑을 찾아가고, 호텔에 묵고, 도시를 둘러보며 느낀 점과 사진, 관찰한 것들을 나눕니다."}
TX = {"by": {"ru": "Автор", "en": "Author", "ko": "글쓴이"}, "about": {"ru": "Об авторе", "en": "About the author", "ko": "글쓴이 소개"},
      "more": {"ru": "Читайте также", "en": "Read also", "ko": "함께 읽어 보세요"}, "all": {"ru": "Все статьи автора →", "en": "All articles by the author →", "ko": "글쓴이의 모든 글 →"},
      "page_t": {"ru": "Оксана Яснова — автор статей", "en": "Oksana Yasnova — author of the articles", "ko": "옥사나 야스노바 — 글쓴이"},
      "page_d": {"ru": "Оксана Яснова — автор статей о ресторанах, отелях и местах Нячанга на сайте Surprise Service Nha Trang. Личный опыт, живые фото, честные впечатления.",
                 "en": "Oksana Yasnova writes first-hand articles about restaurants, hotels and places in Nha Trang for Surprise Service Nha Trang. Personal experience, real photos, honest impressions.",
                 "ko": "옥사나 야스노바 — Surprise Service Nha Trang 사이트에 나트랑의 레스토랑, 호텔, 명소에 대한 글을 씁니다. 직접 경험, 직접 찍은 사진, 솔직한 후기."},
      "list": {"ru": "Авторские статьи", "en": "Articles by the author", "ko": "글쓴이의 글"}, "crumb": {"ru": "Статьи", "en": "Articles", "ko": "블로그"},
      "badge": {"ru": "✍️ Автор", "en": "✍️ Author", "ko": "✍️ 글쓴이"}}
# Реестр авторских статей (новые — в начало)
REG = [
 dict(slug=V.SLUG, img="img/blog/%s.webp" % V.SLUG, date=V.DATE, iso=V.DATE_ISO, title={l: V.META[l]["h1"] for l in LANGS}),
 dict(slug=XO, img="img/blog/%s.webp" % XO, date={"ru": "26 сентября 2026", "en": "26 September 2026", "ko": "2026년 9월 26일"}, iso="2026-09-29",
      title={"ru": "Где поесть морепродукты в Нячанге: местное недорогое кафе на юге города.", "en": "Where to eat seafood in Nha Trang: a local budget café in the south of the city.", "ko": "나트랑에서 해산물 먹을 곳: 시내 남쪽의 저렴한 현지 식당"}),
]
CSS = """<style id="au-css">.xo-art h2{font-family:'Playfair Display',serif;font-size:1.7rem;font-weight:700;color:#1a1a1a;margin:2.6rem 0 1rem;}
.xo-by{font-size:.9rem!important;color:#7a7a7a!important;margin:-.9rem 0 1.6rem!important;}.xo-by a,.au-sign a{color:#c0687a;font-weight:600;text-decoration:underline;}
.au-wrap{max-width:48rem;margin:0 auto;padding:0 1.5rem 1rem;}.au-sign{font-weight:600;color:#1a1a1a;margin:0 0 1rem;font-size:1rem;}
.au-box{display:flex;gap:1.1rem;align-items:flex-start;background:#fdf4f7;border:1px solid #f0d0d8;border-radius:1.25rem;padding:1.2rem 1.3rem;}
.au-ph{flex:0 0 84px;width:84px;height:84px;border-radius:50%;object-fit:cover;background:#c0687a;color:#fff;display:flex;align-items:center;justify-content:center;font:700 1.7rem 'Playfair Display',serif;}
.au-box .au-k{font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:#c0687a;font-weight:700;}.au-box .au-n{display:block;font:700 1.25rem 'Playfair Display',serif;color:#1a1a1a;text-decoration:none;margin:.1rem 0 .35rem;}
.au-box p{margin:0;font-size:.92rem;line-height:1.65;color:#4a4a4a;}.au-box .au-all{display:inline-block;margin-top:.6rem;font-size:.85rem;color:#c0687a;font-weight:600;}
.au-h{font:700 1.4rem 'Playfair Display',serif;color:#1a1a1a;margin:2rem 0 .9rem;}.au-rel{display:flex;gap:.9rem;align-items:center;background:#fff;border:1px solid #f0e0e5;border-radius:1rem;padding:.6rem;text-decoration:none;margin-bottom:.7rem;transition:border-color .2s;}
.au-rel:hover{border-color:#c0687a;}.au-rel img{flex:0 0 112px;width:112px;height:80px;object-fit:cover;border-radius:.7rem;}.au-rel b{display:block;font:700 1rem/1.35 'Playfair Display',serif;color:#1a1a1a;}.au-rel span{font-size:.75rem;color:#8a8a8a;}
@media(max-width:480px){.au-box{gap:.8rem;padding:1rem}.au-ph{flex-basis:60px;width:60px;height:60px;font-size:1.2rem}.au-rel img{flex-basis:88px;width:88px;height:66px}}</style>"""
def rd(p): return io.open(p, encoding="utf-8").read()
def wr(p, s): io.open(p, "w", encoding="utf-8", newline="\n").write(s)
def e(t): return html.escape(t, quote=True)
def photo(pref):
    if os.path.exists("img/blog/%s.webp" % AU):
        return '<img class="au-ph" src="%simg/blog/%s.webp" alt="%s" width="168" height="168" loading="lazy">' % (pref, AU, "{n}")
    return '<div class="au-ph" aria-hidden="true">ОЯ</div>'
def author_box(L, pref="../", link=True):
    href = "%s-%s.html" % (AU, L)
    return ('<div class="au-box">' + photo(pref).replace("{n}", e(NAME[L])) + '<div><span class="au-k">%s</span><a class="au-n" href="%s">%s</a><p>«%s»</p>%s</div></div>'
            % (TX["about"][L], href, NAME[L], BIO[L], ('<a class="au-all" href="%s">%s</a>' % (href, TX["all"][L])) if link else ""))
def rel_card(a, L, pref=""):
    return '<a class="au-rel" href="%s%s-%s.html"><img src="../%s" alt="%s" width="112" height="80" loading="lazy"><div><b>%s</b><span>%s</span></div></a>' % (pref, a["slug"], L, a["img"], e(a["title"][L]), a["title"][L], a["date"][L])
def extras(slug, L):
    others = [a for a in REG if a["slug"] != slug][:3]
    h = '<!--AUTHOR-EXTRAS-START--><section class="au-wrap"><p class="au-sign">%s: <a href="%s-%s.html">%s</a></p>%s' % (TX["by"][L], AU, L, NAME[L], author_box(L))
    if others: h += '<h2 class="au-h">%s</h2>' % TX["more"][L] + "".join(rel_card(a, L) for a in others)
    return h + "</section><!--AUTHOR-EXTRAS-END-->"
def person(L): return {"@type": "Person", "name": NAME[L], "url": "%s/blog/%s-%s.html" % (SITE, AU, L)}
def apply_common(s, slug, L, date):
    s = re.sub(r'<style id="au-css">.*?</style>', "", s, flags=re.S).replace("</head>", CSS + "</head>", 1)
    s = re.sub(r"<!--AUTHOR-EXTRAS-START-->.*?<!--AUTHOR-EXTRAS-END-->\s*", "", s, flags=re.S)
    s = re.sub(r'\s*<p class="xo-by">.*?</p>', "", s, flags=re.S)
    by = '\n        <p class="xo-by">%s: <a href="%s-%s.html">%s</a> · %s</p>' % (TX["by"][L], AU, L, NAME[L], date)
    s = re.sub(r'(<article class="xo-art[^>]*>.*?</h1>)', lambda m: m.group(1) + by, s, count=1, flags=re.S)
    s = s.replace("</article>", "</article>\n    " + extras(slug, L), 1)
    def ld(m):
        try: d = json.loads(m.group(1))
        except Exception: return m.group(0)
        if d.get("@type") in ("Article", "BlogPosting"):
            d["@type"] = "BlogPosting"; d["author"] = person(L)
        return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + "</script>"
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', ld, s, flags=re.S)
def block_html(t, v, L):
    P = "../img/blog/%s/" % V.SLUG
    if t == "p": return "<p>%s</p>" % v
    if t == "b": return '<p class="xo-pt">%s</p>' % v
    if t in ("h2", "h3"): return "<%s>%s</%s>" % (t, v, t)
    if t == "note": return '<div class="xo-note">%s</div>' % v
    if t == "pill": return '<div class="xo-pill">%s</div>' % v
    if t == "rec": return '<p class="xo-rec">%s</p>' % v
    if t == "card": return '<div class="xo-card">' + "".join("<p><b>%s:</b> %s</p>" % kv for kv in v) + "</div>"
    if t == "g":
        from PIL import Image
        im = []
        for i in v:
            w, h = Image.open("img/blog/%s/v%s.webp" % (V.SLUG, i)).size
            im.append('<img src="%sv%s.webp" data-full="%sv%s.webp" alt="%s" loading="lazy" decoding="async" width="%d" height="%d">' % (P, i, P, i, e(V.ALT[i][LANGS.index(L)]), w, h))
        cls = "xo-one" if len(v) == 1 else ("xo-g odd" if len(v) == 3 else "xo-g")
        return '<div class="%s">%s</div>' % (cls, "".join(im))
    raise ValueError(t)
CTA = {"ru": ("Планируете день рождения или романтический сюрприз в Нячанге?", "Мы поможем организовать праздник: цветы, торты, подарки, воздушные шары и оформление.", "Оформление праздников", "../prazdnik.html"),
       "en": ("Planning a birthday or a romantic surprise in Nha Trang?", "We will help you organise the celebration: flowers, cakes, gifts, balloons and decoration.", "Party decoration", "../prazdnik-en.html"),
       "ko": ("나트랑에서 생일이나 로맨틱한 서프라이즈를 계획하고 계신가요?", "꽃, 케이크, 선물, 풍선과 장식까지 — 파티 준비를 도와드립니다.", "파티 장식 보기", "../prazdnik-kr.html")}
def build_veranda(L):
    s = rd("blog/%s-%s.html" % (XO, L))
    old_title = re.search(r"<title>(.*?)</title>", s, flags=re.S).group(1)
    old_desc = re.search(r'<meta name="description" content="(.*?)">', s, flags=re.S).group(1)
    old_h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, flags=re.S).group(1)
    M = V.META[L]
    s = s.replace(XO, V.SLUG).replace(old_title, e(M["title"])).replace(old_desc, e(M["desc"])).replace(old_h1, M["h1"])
    s = s.replace('"datePublished": "2026-09-29"', '"datePublished": "%s"' % V.DATE_ISO)
    url = "%s/blog/%s-%s.html" % (SITE, V.SLUG, L)
    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": M["title"], "description": M["desc"], "image": "%s/img/blog/%s.webp" % (SITE, V.SLUG),
          "datePublished": V.DATE_ISO, "dateModified": V.DATE_ISO, "inLanguage": L, "author": person(L), "publisher": {"@type": "Organization", "name": "Surprise Service Nha Trang"},
          "mainEntityOfPage": url, "about": {"@type": "Restaurant", "name": "Veranda", "address": {"@type": "PostalAddress", "addressLocality": "Nha Trang", "addressCountry": "VN"}, "servesCuisine": ["Russian", "European"]}}
    n = [0]
    def ldrep(m):
        if '"headline"' in m.group(1): n[0] += 1; return '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>"
        return m.group(0)
    s = re.sub(r'<script type="application/ld\+json">(.*?)</script>', ldrep, s, flags=re.S); assert n[0] == 1
    a = s.index("<article"); a2 = s.index(">", a) + 1; b = s.index("</article>")
    head = s[a2:s.index("</h1>", a2) + 5]
    head = re.sub(r"(<span class=\"xo-badge\">[^<]*</span><span>)[^<]*(</span>)", lambda m: m.group(1) + V.DATE[L] + m.group(2), head)
    body = "\n        ".join(block_html(t, v, L) for t, v in V.B[L])
    s = s[:a2] + head + "\n        " + body + "\n    " + s[b:]
    s = re.sub(r'(<img src="\.\./img/blog/%s\.webp" alt=")[^"]*' % re.escape(V.SLUG), lambda m: m.group(1) + e(V.ALT[V.HERO][LANGS.index(L)]), s, count=1)
    # CTA после статьи: праздник под ключ
    c = s.index('<section class="reveal py-12 px-4">', s.index("</article>")); c2 = s.index("</section>", c)
    seg = s[c:c2]
    seg = re.sub(r"(<h2[^>]*>).*?(</h2>)", lambda m: m.group(1) + CTA[L][0] + m.group(2), seg, count=1, flags=re.S)
    seg = re.sub(r'(<p class="text-stone-600[^>]*>).*?(</p>)', lambda m: m.group(1) + CTA[L][1] + m.group(2), seg, count=1, flags=re.S)
    seg = re.sub(r'<a href="[^"]*"( class="btn-rose-filled[^>]*>)(<svg.*?</svg>)[^<]*</a>', lambda m: '<a href="%s"%s%s %s</a>' % (CTA[L][3], m.group(1), m.group(2), CTA[L][2]), seg, count=1, flags=re.S)
    s = s[:c] + seg + s[c2:]
    wr("blog/%s-%s.html" % (V.SLUG, L), apply_common(s, V.SLUG, L, V.DATE[L]))
def build_author_page(L):
    s = rd("blog/%s-%s.html" % (XO, L))
    old_title = re.search(r"<title>(.*?)</title>", s, flags=re.S).group(1)
    old_desc = re.search(r'<meta name="description" content="(.*?)">', s, flags=re.S).group(1)
    s = s.replace("%s/img/blog/%s.webp" % (SITE, XO), "%s/img/blog/%s.webp" % (SITE, REG[0]["slug"]))
    s = s.replace("blog/%s-" % XO, "blog/%s-" % AU).replace(old_title, e(TX["page_t"][L])).replace(old_desc, e(TX["page_d"][L]))
    s = s.replace('<meta property="og:type" content="article">', '<meta property="og:type" content="profile">')
    url = "%s/blog/%s-%s.html" % (SITE, AU, L)
    ld = {"@context": "https://schema.org", "@type": "ProfilePage", "mainEntity": {"@type": "Person", "name": NAME[L], "description": BIO[L], "url": url, "homeLocation": {"@type": "Place", "name": "Nha Trang, Vietnam"}},
          "hasPart": [{"@type": "BlogPosting", "headline": a["title"][L], "url": "%s/blog/%s-%s.html" % (SITE, a["slug"], L), "datePublished": a["iso"]} for a in REG]}
    s = re.sub(r'<script type="application/ld\+json">(.*?)</script>', lambda m: ('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>") if '"headline"' in m.group(1) else m.group(0), s, flags=re.S)
    s = re.sub(r"<script>/\*XO-VIEWS\*/.*?</script>", "", s, flags=re.S)
    s = re.sub(r'<style id="au-css">.*?</style>', "", s, flags=re.S).replace("</head>", CSS + "</head>", 1)
    a = s.index("<main"); a2 = s.index(">", a) + 1; b = s.index("</main>")
    back = re.search(r'<section class="max-w-3xl mx-auto px-6 pb-16 text-center">.*?</section>', s[a:b], flags=re.S).group(0)
    main = ('\n    <nav class="max-w-4xl mx-auto px-6 pt-8 pb-2 text-xs text-stone-400"><a href="../blog-%s.html">%s</a> / <span style="color:#1a1a1a;">%s</span></nav>'
            '\n    <section class="au-wrap" style="padding-top:1.5rem"><div class="xo-meta"><span class="xo-badge">%s</span></div><h1 class="font-serif text-3xl md:text-4xl font-bold mt-2 mb-6 leading-tight" style="color:#1a1a1a;">%s</h1>%s'
            '<h2 class="au-h">%s</h2>%s</section>\n    %s\n    ') % (L, TX["crumb"][L], NAME[L], TX["badge"][L], TX["page_t"][L], author_box(L, link=False), TX["list"][L], "".join(rel_card(x, L) for x in REG), back)
    wr("blog/%s-%s.html" % (AU, L), s[:a2] + main + s[b:])
if __name__ == "__main__":
    for L in LANGS:
        build_veranda(L)
        p = "blog/%s-%s.html" % (XO, L); wr(p, apply_common(rd(p), XO, L, REG[1]["date"][L]))
        build_author_page(L)
    print("ok")
