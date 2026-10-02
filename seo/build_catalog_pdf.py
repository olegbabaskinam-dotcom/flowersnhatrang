#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Премиум PDF-каталог (журнальный вид) для RU/EN/KO.
Источник: seo/products.csv + img/products/<slug>/. Движок: reportlab.
Содержание с диапазоном страниц, категории (дубли по тегам + Комбо), 3 фото (1,3,5 или 1,2,3).
Запуск: python3 seo/build_catalog_pdf.py <ru|en|ko> <out.pdf> [версия]
"""
import sys, os, csv, re, glob, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site as B
from PIL import Image, ImageOps
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

ROOT = B.ROOT
PW, PH = A4                       # 595 x 842 pt
M = 42                            # поля
CW = PW - 2 * M                   # ширина контента

# ---------- палитра ----------
ROSE   = (0.659, 0.337, 0.416)   # #A8566A
ROSE_D = (0.560, 0.275, 0.353)
BLUSH  = (0.972, 0.929, 0.937)   # #F8EDEF
BLUSH2 = (0.988, 0.965, 0.969)
INK    = (0.129, 0.102, 0.110)   # #211A1C
GREY   = (0.478, 0.439, 0.463)
LINE   = (0.902, 0.847, 0.867)
GOLD   = (0.788, 0.639, 0.420)
WHITE  = (1, 1, 1)

# ---------- шрифты ----------
def dejavu_dir():
    candidates = [
        "/usr/share/fonts/truetype/dejavu",
        os.path.expanduser(
            "~/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/"
            "libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype"
        ),
        "/Library/Fonts",
    ]
    required = ("DejaVuSerif.ttf", "DejaVuSerif-Bold.ttf", "DejaVuSerif-Italic.ttf",
                "DejaVuSans.ttf", "DejaVuSans-Bold.ttf")
    for directory in candidates:
        if all(os.path.isfile(os.path.join(directory, name)) for name in required):
            return directory
    raise FileNotFoundError("Не найдены шрифты DejaVu, необходимые для каталога")

def register_fonts(lang):
    d = dejavu_dir()
    pdfmetrics.registerFont(TTFont("Serif",  os.path.join(d, "DejaVuSerif.ttf")))
    pdfmetrics.registerFont(TTFont("SerifB", os.path.join(d, "DejaVuSerif-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("SerifI", os.path.join(d, "DejaVuSerif-Italic.ttf")))
    pdfmetrics.registerFont(TTFont("Sans",   os.path.join(d, "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("SansB",  os.path.join(d, "DejaVuSans-Bold.ttf")))
    if lang == "ko":
        korean_ttf = next((path for path in (
            "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
            "/Library/Fonts/AppleGothic.ttf",
        ) if os.path.isfile(path)), None)
        if korean_ttf:
            # Встраиваем шрифт в PDF: корейский текст будет виден даже без CMap-пакетов.
            pdfmetrics.registerFont(TTFont("Korean", korean_ttf))
            return {"serif": "Korean", "serifb": "Korean", "serifi": "Korean",
                    "sans": "Korean", "sansb": "Korean"}
        pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))
        pdfmetrics.registerFont(UnicodeCIDFont("HYGothic-Medium"))
        return {"serif": "HYSMyeongJo-Medium", "serifb": "HYSMyeongJo-Medium",
                "serifi": "HYSMyeongJo-Medium", "sans": "HYGothic-Medium", "sansb": "HYGothic-Medium"}
    return {"serif": "Serif", "serifb": "SerifB", "serifi": "SerifI", "sans": "Sans", "sansb": "SansB"}

# ---------- локализация ----------
L = {
    "ru": {
        "title": "КАТАЛОГ", "sub": "Русскоязычная доставка цветов,\nшаров и подарков в Нячанге",
        "toc": "Содержание", "items": "товаров", "pages": "стр.",
        "site": "flowers-nha-trang.online", "price_cur": "₫",
        "cats": {"r25":"25 роз","r51":"51 роза","r101":"101 роза","mixed":"Сборные букеты",
                 "nabory":"Подарочные наборы","prazdnik":"Готовые наборы для праздника",
                 "cakes":"Торты","balloons":"Гелиевые шары","combo":"Комбо-наборы","addon":"Дополнения к заказу"},
        "brand":"Цветы Нячанг", "made":"День в день — при заказе до 17:00",
    },
    "en": {
        "title": "CATALOG", "sub": "Flowers, balloons & gifts\ndelivery in Nha Trang",
        "toc": "Contents", "items": "items", "pages": "pp.",
        "site": "flowers-nha-trang.online", "price_cur": "₫",
        "cats": {"r25":"25 Roses","r51":"51 Roses","r101":"101 Roses","mixed":"Mixed Bouquets",
                 "nabory":"Gift Sets","prazdnik":"Festive Ready Sets",
                 "cakes":"Cakes","balloons":"Helium Balloons","combo":"Combo Sets","addon":"Order Add-ons"},
        "brand":"NhaTrang Flowers", "made":"Same-day delivery — order by 17:00",
    },
    "ko": {
        "title": "카탈로그", "sub": "나트랑 꽃·풍선·선물 배달",
        "toc": "목차", "items": "개", "pages": "페이지",
        "site": "flowers-nha-trang.online", "price_cur": "₫",
        "cats": {"r25":"장미 25송이","r51":"장미 51송이","r101":"장미 101송이","mixed":"믹스 꽃다발",
                 "nabory":"선물 세트","prazdnik":"축하 세트",
                 "cakes":"케이크","balloons":"헬륨 풍선","combo":"콤보 세트","addon":"추가 상품"},
        "brand":"NhaTrang Flowers", "made":"당일 배달 — 17:00까지 주문",
    },
}

# ---------- Каталог 4.5: страница «Основная информация» ----------
INFO = {
    "ru": {"cover_line": "ДОСТАВКА ЦВЕТОВ, ШАРОВ И ПОДАРКОВ В НЯЧАНГЕ",
           "title": "Основная информация",
           "boxes": [("Время работы", "07:00 – 21:00", "ежедневно · Камрань 07:00–20:00"),
                     ("Заказ на сегодня", "до 17:00", "день в день · все зоны")],
           "pos_h": "Основные позиции",
           "pos": ["25 роз", "51 роза", "101 роза", "Сборные букеты", "Гелиевые шары", "Подарки", "Оформление праздников"],
           "zones_h": "Зоны доставки",
           "zones": {"center": "Центр Нячанга", "north": "Крайний север", "west": "Запад",
                     "south": "Ближний юг", "camranh": "Камрань"},
           "free": "бесплатно",
           "notes": ["Фольгированные шары — летают в среднем 7 дней.",
                     "Резиновые шары — летают в среднем 12 часов.",
                     "В платные зоны — заказ от 1 000 000 ₫.",
                     "В аэропорт Камрань и южнее аэропорта не доставляем.",
                     "На острова (Vinpearl, Hòn Tre) не возим — передадим заказ в порту на материке."]},
    "en": {"cover_line": "FLOWERS, BALLOONS & GIFTS DELIVERY IN NHA TRANG",
           "title": "Key information",
           "boxes": [("Working hours", "07:00 – 21:00", "daily · Cam Ranh 07:00–20:00"),
                     ("Same-day orders", "until 17:00", "same day · all zones")],
           "pos_h": "Main products",
           "pos": ["25 roses", "51 roses", "101 roses", "Mixed bouquets", "Helium balloons", "Gifts", "Party decor"],
           "zones_h": "Delivery zones",
           "zones": {"center": "Nha Trang center", "north": "Far north", "west": "West",
                     "south": "Near south", "camranh": "Cam Ranh"},
           "free": "free",
           "notes": ["Foil balloons — float for about 7 days on average.",
                     "Latex balloons — float for about 12 hours on average.",
                     "Paid zones: minimum order 1,000,000 ₫.",
                     "No delivery to Cam Ranh airport or south of it.",
                     "No delivery to islands (Vinpearl, Hon Tre) — we hand over the order at the mainland port."]},
    "ko": {"cover_line": "나트랑 꽃 · 풍선 · 선물 배달",
           "title": "기본 안내",
           "boxes": [("영업시간", "07:00 – 21:00", "매일 / 깜라인 07:00–20:00"),
                     ("당일 주문", "17:00까지", "당일 배달 · 전 지역")],
           "pos_h": "주요 상품",
           "pos": ["장미 25송이", "장미 51송이", "장미 101송이", "믹스 꽃다발", "헬륨 풍선", "선물", "파티 데코"],
           "zones_h": "배달 지역",
           "zones": {"center": "나트랑 중심", "north": "최북단", "west": "서쪽",
                     "south": "남쪽 인근", "camranh": "깜라인"},
           "free": "무료",
           "notes": ["호일 풍선 — 평균 약 7일 동안 떠 있습니다.",
                     "라텍스 풍선 — 평균 약 12시간 동안 떠 있습니다.",
                     "유료 지역은 1,000,000동 이상 주문 시 배달합니다.",
                     "깜라인 공항 및 공항 남쪽은 배달하지 않습니다.",
                     "섬(빈펄, 혼째)은 배달하지 않으며 본토 항구에서 전달해 드립니다."]},
}
ZONE_ORDER = ["center", "north", "west", "south", "camranh"]
ZONE_COL = {"center": (0.55, 0.77, 0.60), "north": (0.93, 0.76, 0.42), "west": (0.98, 0.86, 0.55),
            "south": (0.93, 0.60, 0.52), "camranh": (0.66, 0.34, 0.42)}

def load_zones():
    """Полигоны и доплаты — ровно как в cart.html (DZONES), без выдумок."""
    import ast
    s = open(os.path.join(ROOT, "cart.html"), encoding="utf-8").read()
    t = re.search(r"var DZONES=(\{.*?\});", s, re.S).group(1)
    z = {}
    for k, fee, mn, poly in re.findall(r"(\w+):\{fee:(\d+),slots:\d+,min:(\d+),label:\"[^\"]*\",poly:(\[\[.*?\]\])", t):
        z[k] = {"fee": int(fee), "min": int(mn), "poly": ast.literal_eval(poly)}
    return z

def fmt_vnd(v, lang):
    return (f"{v:,}" if lang == "en" else f"{v:,}".replace(",", " ")) + " ₫"

def chips_centered(c, items, font, size, y, maxw, pad=10, h=22, gap=8):
    rows, cur, curw = [], [], 0
    for it in items:
        w = pdfmetrics.stringWidth(it, font, size) + 2*pad
        if cur and curw + gap + w > maxw:
            rows.append((cur, curw)); cur, curw = [], 0
        curw = curw + (gap if cur else 0) + w; cur.append((it, w))
    if cur: rows.append((cur, curw))
    for row, rw in rows:
        x = (PW - rw) / 2
        for it, w in row:
            c.setFillColor(BLUSH); c.setStrokeColor(LINE); c.setLineWidth(0.7)
            c.roundRect(x, y - h + 6, w, h, h/2, stroke=1, fill=1)
            c.setFillColor(ROSE_D); c.setFont(font, size)
            c.drawCentredString(x + w/2, y - h/2 + 2.5, it)
            x += w + gap
        y -= h + 8
    return y

def draw_info(c, F, t, lang):
    I = INFO[lang]
    c.setFillColor(WHITE); c.rect(0, 0, PW, PH, stroke=0, fill=1)
    c.setFillColor(BLUSH); c.rect(0, PH-128, PW, 128, stroke=0, fill=1)
    c.setFillColor(ROSE); c.setFont(F["sans"], 9)
    c.drawCentredString(PW/2, PH-52, t["brand"] + "  |  " + t["site"])
    c.setFillColor(INK); c.setFont(F["serifb"], 30)
    c.drawCentredString(PW/2, PH-90, I["title"])
    c.setStrokeColor(GOLD); c.setLineWidth(1.2); c.line(PW/2-50, PH-106, PW/2+50, PH-106)
    # два блока: время / заказ на сегодня
    bw, bh, top = (CW-16)/2, 104, PH-150
    for i, (lab, val, sub) in enumerate(I["boxes"]):
        x = M + i*(bw+16)
        c.setFillColor(WHITE); c.setStrokeColor(LINE); c.setLineWidth(1)
        c.roundRect(x, top-bh, bw, bh, 12, stroke=1, fill=1)
        c.setFillColor(ROSE); c.roundRect(x+bw/2-18, top-6, 36, 4, 2, stroke=0, fill=1)
        c.setFillColor(GREY); c.setFont(F["sans"], 10.5); c.drawCentredString(x+bw/2, top-30, lab)
        vf = "SerifB" if lang != "ko" or val[0].isdigit() and "까지" not in val else F["serifb"]
        c.setFillColor(ROSE); c.setFont(vf, 26); c.drawCentredString(x+bw/2, top-64, val)
        c.setFillColor(INK); c.setFont(F["sans"], 10); c.drawCentredString(x+bw/2, top-86, sub)
    # основные позиции
    y = top - bh - 34
    c.setFillColor(INK); c.setFont(F["serifb"], 16); c.drawCentredString(PW/2, y, I["pos_h"])
    y = chips_centered(c, I["pos"], F["sansb"], 10.5, y - 18, CW)
    # зоны
    y -= 16
    c.setFillColor(INK); c.setFont(F["serifb"], 16); c.drawCentredString(PW/2, y, I["zones_h"])
    c.setStrokeColor(GOLD); c.setLineWidth(1); c.line(PW/2-40, y-9, PW/2+40, y-9)
    # карта зон: реальная подложка Google Maps + зоны/подписи (seo/_catalog_map/map_<lang>.jpg)
    map_img = os.path.join(ROOT, "seo", "_catalog_map", f"map_{lang}.jpg")
    box_top = y - 22
    notes_h = 70
    side = min(box_top - 52 - notes_h, CW)
    mx = (PW - side) / 2; my = box_top - side
    c.saveState(); pth = c.beginPath(); pth.roundRect(mx, my, side, side, 12); c.clipPath(pth, stroke=0, fill=0)
    c.drawImage(map_img, mx, my, side, side); c.restoreState()
    c.setStrokeColor(LINE); c.setLineWidth(1); c.roundRect(mx, my, side, side, 12, stroke=1, fill=0)
    ny = my - 16
    for note in I["notes"]:
        for ln in wrap(c, note, F["sans"], 9, CW):
            c.setFillColor(GREY); c.setFont(F["sans"], 9); c.drawCentredString(PW/2, ny, ln); ny -= 12
    c.setFillColor(GREY); c.setFont("Sans", 8)
    c.drawCentredString(PW/2, 26, t["brand"] + "  ·  " + t["site"])
    c.showPage()

CAT_ORDER = ["r25","r51","r101","mixed","nabory","prazdnik","cakes","balloons","combo","addon"]
# Каталог 5.0: стр.3 «Основная информация» — категории, по 3 главных фото разных позиций
INFO_CATS = ["r25","r51","r101","mixed","balloons","cakes","nabory","prazdnik"]
INFO2 = {"ru": {"title": "Основная информация", "sub": "Что мы доставляем — основные категории"},
         "en": {"title": "Key information", "sub": "What we deliver — main categories"},
         "ko": {"title": "기본 안내", "sub": "배달 상품 — 주요 카테고리"}}

# стр.3: вручную выбранные позиции — 3 РАЗНЫХ цвета в каждой категории (решение Олега 26.09)
INFO_PICK = {"r25": ["2","1","3"], "r51": ["25","19","58"], "r101": ["49","18","33"],
             "mixed": ["16","14","56"], "balloons": ["57","55","163"]}

def pick_info_items(items, k=3, cat=None):
    if cat in INFO_PICK:
        byid = {p["id"]: p for p in items}
        sel = [byid[i] for i in INFO_PICK[cat] if i in byid]
        if len(sel) == k:
            return sel
    """3 разные позиции категории: только чистые (не комбо), равномерно по списку; главное фото = первое."""
    pure = [p for p in items if not B.is_combo(B.product_cat(p))] or list(items)
    pure = [p for p in pure if sorted(glob.glob(os.path.join(ROOT, f"img/products/{p['slug']}/*.webp")))]
    n = len(pure)
    if n <= k:
        return pure
    idx = sorted(set(round(i * (n - 1) / (k - 1)) for i in range(k)))
    return [pure[i] for i in idx]

def draw_info_cats(c, F, t, lang, by, ranges):
    I = INFO2[lang]
    c.setFillColor(WHITE); c.rect(0, 0, PW, PH, stroke=0, fill=1)
    c.setFillColor(BLUSH); c.rect(0, PH-128, PW, 128, stroke=0, fill=1)
    c.setFillColor(ROSE); c.setFont(F["sans"], 9)
    c.drawCentredString(PW/2, PH-52, t["brand"] + "  |  " + t["site"])
    c.setFillColor(INK); c.setFont(F["serifb"], 30)
    c.drawCentredString(PW/2, PH-90, I["title"])
    c.setStrokeColor(GOLD); c.setLineWidth(1.2); c.line(PW/2-50, PH-106, PW/2+50, PH-106)
    c.setFillColor(GREY); c.setFont(F["sans"], 10.5)
    c.drawCentredString(PW/2, PH-122, I["sub"])
    colw = (CW - 16) / 2
    top = PH - 146
    rowh = (top - 44) / 4
    gap = 6
    for i, cat in enumerate(INFO_CATS):
        col, row = i % 2, i // 2
        x = M + col * (colw + 16)
        yt = top - row * rowh
        c.setFillColor(WHITE); c.setStrokeColor(LINE); c.setLineWidth(1)
        c.roundRect(x, yt - rowh + 8, colw, rowh - 8, 10, stroke=1, fill=1)
        c.setFillColor(ROSE); c.roundRect(x, yt - 30, 5, 22, 2, stroke=0, fill=1)
        name = t["cats"][cat]
        fs = 13.5
        while pdfmetrics.stringWidth(name, F["serifb"], fs) > colw - 78 and fs > 8:
            fs -= 0.5
        c.setFillColor(INK); c.setFont(F["serifb"], fs)
        c.drawString(x + 14, yt - 25, name)
        a, b, n = ranges[cat]
        pg = f"{t['pages']} {a}–{b}" if b > a else f"{t['pages']} {a}"
        c.setFillColor(GREY); c.setFont(F["sans"], 8.5)
        c.drawRightString(x + colw - 10, yt - 24, pg)
        its = pick_info_items(by[cat], cat=cat)
        iw = (colw - 20 - gap * 2) / 3
        ih = rowh - 8 - 44
        iy = yt - rowh + 8 + 10
        for j, p in enumerate(its):
            ph = sorted(glob.glob(os.path.join(ROOT, f"img/products/{p['slug']}/*.webp")))[0]
            draw_rounded_image(c, ph, x + 10 + j * (iw + gap), iy, iw, ih, r=7)
    c.setFillColor(GREY); c.setFont("Sans", 8)
    c.drawCentredString(PW/2, 26, t["brand"] + "  ·  " + t["site"])
    c.showPage()

# ---------- данные ----------
def load_products():
    return list(csv.DictReader(open(os.path.join(ROOT, "seo/products.csv"), encoding="utf-8")))

def members_by_cat(prods):
    by = {c: [] for c in CAT_ORDER}
    for p in prods:
        tags = B.product_cat(p).split()
        for t in tags:
            if t in by:
                by[t].append(p)
        if len(tags) >= 2:
            by["combo"].append(p)
    # Каталог 4.2: внутри каждой категории сначала ЧИСТЫЕ одиночные позиции,
    # затем комбо-наборы (где эта позиция лишь входит в набор). Сортировка стабильная.
    for cat in CAT_ORDER:
        if cat == "combo":
            continue
        by[cat] = sorted(by[cat], key=lambda p: 1 if B.is_combo(B.product_cat(p)) else 0)
    return by

def combo_line(p, lang):
    """Текст пометки «В наборе: …» для комбо-карточки в PDF (без emoji — их нет в DejaVu)."""
    cat = B.product_cat(p)
    if not B.is_combo(cat):
        return None
    parts = [B.COMBO_PARTS.get(lang, B.COMBO_PARTS["ru"]).get(c) for c in cat.split()]
    parts = [x for x in parts if x]
    if not parts:
        return None
    # KO-шрифт (AppleGothic) не содержит «·» (U+00B7) → для корейского безопасный « + ».
    sep = " + " if lang == "ko" else " · "
    return B.COMBO_LABEL.get(lang, B.COMBO_LABEL["ru"]) + ": " + sep.join(parts)

def pick_photos(slug):
    files = sorted(glob.glob(os.path.join(ROOT, f"img/products/{slug}/*.webp")))
    n = len(files)
    if n >= 5:
        idx = [0, 2, 4]
    else:
        idx = [0, 1, 2]
    return [files[i] for i in idx if i < n]

_CACHE = {}
def jpg_crop(path, aspect, tw=440, q=80):
    """webp → JPEG, кроп-заливка под соотношение aspect (w/h), центр. tw = ширина в px. Кэш."""
    key = (path, round(aspect, 3), tw, q)
    if key in _CACHE:
        return _CACHE[key]
    out = os.path.join(TMP, re.sub(r"[^a-zA-Z0-9]", "_", path) + f"_{round(aspect,3)}_{tw}.jpg")
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    w, h = im.size
    cur = w / h
    if cur > aspect:                       # слишком широкое → режем по бокам
        nw = int(round(h * aspect)); x = (w - nw) // 2; im = im.crop((x, 0, x + nw, h))
    else:                                  # слишком высокое → режем сверху/снизу
        nh = int(round(w / aspect)); y = (h - nh) // 2; im = im.crop((0, y, w, y + nh))
    im = im.resize((tw, max(1, int(round(tw / aspect)))), Image.LANCZOS)
    im.save(out, "JPEG", quality=q, optimize=True)
    _CACHE[key] = out
    return out

def short_desc(text, limit=150):
    t = (text or "").strip()
    # берём фразу до первого « — » (тире), иначе обрезаем по слову
    cut = re.split(r"\s[—–-]\s", t, 1)[0].strip()
    if len(cut) < 30 or len(cut) > limit + 40:
        cut = t
    if len(cut) > limit:
        cut = cut[:limit].rsplit(" ", 1)[0].rstrip(",;: ") + "…"
    return cut[:1].upper() + cut[1:] if cut else cut

def price_main(p):
    digits = re.sub(r"[^\d]", " ", p["price"]).strip()
    digits = re.sub(r"\s+", " ", digits)
    return digits

# ---------- текстовые утилиты ----------
def wrap(c, text, font, size, maxw):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(test, font, size) <= maxw:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_rounded_image(c, path, x, y, w, h, r=7):
    c.saveState()
    pth = c.beginPath()
    pth.roundRect(x, y, w, h, r)
    c.clipPath(pth, stroke=0, fill=0)
    c.setFillColor(BLUSH2); c.rect(x, y, w, h, stroke=0, fill=1)
    tw = min(1100, max(360, int(w * 2.2)))     # разрешение под реальный размер на странице
    try:
        c.drawImage(jpg_crop(path, w / h, tw), x, y, w, h, mask='auto')
    except Exception:
        pass
    c.restoreState()
    c.setStrokeColor(LINE); c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, r, stroke=1, fill=0)

# ---------- страницы ----------
def draw_footer(c, F, t, page_no, cat_name):
    c.setFillColor(GREY)
    c.setFont("Sans", 7.5)                                  # латиница — DejaVu (есть «·»)
    c.drawString(M, 26, t["brand"] + "  ·  " + t["site"])
    c.setFont(F["sans"], 7.5)                               # категория может быть на KO
    c.drawRightString(PW - M, 26, cat_name)
    c.setFillColor(ROSE)
    c.setFont(F["serifb"], 8.5)
    c.drawCentredString(PW/2, 24, str(page_no))
    c.setStrokeColor(LINE); c.setLineWidth(0.6)
    c.line(M, 38, PW - M, 38)

def draw_cover(c, F, t, hero, version):
    c.setFillColor(BLUSH); c.rect(0, 0, PW, PH, stroke=0, fill=1)
    # верхняя тонкая рамка
    c.setStrokeColor(ROSE); c.setLineWidth(1.2)
    c.rect(24, 24, PW-48, PH-48, stroke=1, fill=0)
    c.setStrokeColor(GOLD); c.setLineWidth(0.6)
    c.rect(30, 30, PW-60, PH-60, stroke=1, fill=0)
    # герой-изображение по центру
    heroes = hero if isinstance(hero, (list, tuple)) else [hero]
    line = INFO.get(t.get("_lang", "ru"), INFO["ru"])["cover_line"]
    c.setFillColor(ROSE); c.setFont(F["sansb"], 11.5)
    c.drawCentredString(PW/2, PH-72, line)
    c.setStrokeColor(GOLD); c.setLineWidth(0.8); c.line(PW/2-60, PH-84, PW/2+60, PH-84)
    ih = 300; iy = PH-110-ih
    if len(heroes) >= 3:
        cw_, sw_ = 200, 140
        draw_rounded_image(c, heroes[1], PW/2-cw_/2-sw_-10, iy+30, sw_, ih-60, r=10)
        draw_rounded_image(c, heroes[2], PW/2+cw_/2+10, iy+30, sw_, ih-60, r=10)
        draw_rounded_image(c, heroes[0], PW/2-cw_/2, iy, cw_, ih, r=12)
    elif heroes and os.path.exists(heroes[0]):
        draw_rounded_image(c, heroes[0], 70, iy, PW-140, ih, r=10)
    # заголовок
    c.setFillColor(INK); c.setFont(F["serifb"], 60)
    c.drawCentredString(PW/2, iy-95, t["title"])
    c.setFillColor(ROSE); c.setFont(F["serifb"], 26)
    c.drawCentredString(PW/2, iy-130, version)
    # разделитель
    c.setStrokeColor(GOLD); c.setLineWidth(1)
    c.line(PW/2-70, iy-150, PW/2+70, iy-150)
    # подзаголовок
    c.setFillColor(GREY); c.setFont(F["serif"], 13)
    yy = iy-178
    for ln in t["sub"].split("\n"):
        c.drawCentredString(PW/2, yy, ln); yy -= 18
    # низ
    c.setFillColor(ROSE); c.setFont(F["serifb"], 12)
    c.drawCentredString(PW/2, 70, t["site"])
    c.setFillColor(GREY); c.setFont(F["sans"], 9)
    c.drawCentredString(PW/2, 54, t["made"])
    c.showPage()

def draw_toc(c, F, t, ranges):
    c.setFillColor(WHITE); c.rect(0, 0, PW, PH, stroke=0, fill=1)
    # шапка
    c.setFillColor(BLUSH); c.rect(0, PH-150, PW, 150, stroke=0, fill=1)
    c.setFillColor(INK); c.setFont(F["serifb"], 34)
    c.drawString(M, PH-95, t["toc"])
    c.setStrokeColor(GOLD); c.setLineWidth(1.2)
    c.line(M, PH-110, M+90, PH-110)
    # строки
    y = PH-200
    for cat in CAT_ORDER:
        a, b, n = ranges[cat]
        name = t["cats"][cat]
        c.setFillColor(INK); c.setFont(F["serifb"], 15)
        c.drawString(M+4, y, name)
        cnt = f"{n} {t['items']}"
        c.setFillColor(GREY); c.setFont(F["sans"], 9.5)
        c.drawString(M+4, y-15, cnt)
        pg = f"{t['pages']} {a}–{b}" if b > a else f"{t['pages']} {a}"
        c.setFillColor(ROSE); c.setFont(F["serifb"], 13)
        c.drawRightString(PW-M-4, y, pg)
        # пунктирный лидер
        c.setStrokeColor(LINE); c.setLineWidth(0.5); c.setDash(1, 3)
        c.line(M+4+pdfmetrics.stringWidth(name, F["serifb"], 15)+12, y+3,
               PW-M-4-pdfmetrics.stringWidth(pg, F["serifb"], 13)-12, y+3)
        c.setDash()
        y -= 56
    c.setFillColor(GREY); c.setFont("Sans", 8)
    c.drawCentredString(PW/2, 40, t["brand"] + "  ·  " + t["site"])
    c.showPage()

def draw_card(c, F, t, p, lang, x, y_top, w):
    """Рисует карточку товара; возвращает высоту блока."""
    photos = pick_photos(p["slug"])
    gap = 9
    n = max(1, len(photos))
    iw = (w - gap*(n-1)) / n if n > 1 else w*0.62
    ih = 176
    iy = y_top - ih
    for i, ph in enumerate(photos):
        draw_rounded_image(c, ph, x + i*(iw+gap), iy, iw, ih, r=8)
    # текст
    ty = iy - 22
    name = p[f"name_{lang}"]
    c.setFillColor(INK); c.setFont(F["serifb"], 14)
    for ln in wrap(c, name, F["serifb"], 14, w)[:2]:
        c.drawString(x, ty, ln); ty -= 17
    ty -= 2
    # Каталог 4.2: пометка «В наборе: …» на комбо-карточках (розовый чип)
    cline = combo_line(p, lang)
    if cline:
        cf = F["sansb"]   # языковой bold-шрифт (для KO — корейский, иначе DejaVu Sans Bold)
        cl = wrap(c, cline, cf, 8.4, w - 16)[:1][0]
        cw = pdfmetrics.stringWidth(cl, cf, 8.4) + 14
        ch = 15
        c.setFillColor(BLUSH); c.roundRect(x, ty - ch + 5, min(cw, w), ch, 4, stroke=0, fill=1)
        c.setFillColor(ROSE); c.setFont(cf, 8.4)
        c.drawString(x + 7, ty - 5, cl)
        ty -= ch + 3
    desc = short_desc(p[f"desc_{lang}"])
    c.setFillColor(GREY); c.setFont(F["sans"], 8.6)
    for ln in wrap(c, desc, F["sans"], 8.6, w)[:2]:
        c.drawString(x, ty, ln); ty -= 12
    ty -= 6
    pm = price_main(p) + " " + t["price_cur"]
    c.setFillColor(ROSE); c.setFont("SansB", 14)          # DejaVu Sans: есть ₫ ₽ $
    c.drawString(x, ty, pm)
    sub = p["price_sub"]
    c.setFillColor(GREY); c.setFont("Sans", 9)
    c.drawString(x + pdfmetrics.stringWidth(pm, "SansB", 14) + 12, ty+1, sub)
    ty -= 10
    return y_top - ty

def draw_cat_header(c, F, t, cat, n):
    band_h = 66
    top = PH - M - band_h
    c.setFillColor(BLUSH); c.roundRect(M, top, CW, band_h, 10, stroke=0, fill=1)
    c.setFillColor(ROSE); c.roundRect(M, top, 6, band_h, 3, stroke=0, fill=1)
    c.setFillColor(INK); c.setFont(F["serifb"], 22)
    c.drawString(M+22, top+band_h/2-4, t["cats"][cat])
    c.setFillColor(GREY); c.setFont(F["sans"], 10)
    c.drawRightString(PW-M-18, top+band_h/2-3, f"{n} {t['items']}")
    return top - 16   # y для первой карточки

def build(lang, out_path, version="2.0"):
    global TMP
    TMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_catalog_tmp")
    os.makedirs(TMP, exist_ok=True)
    t = L[lang]
    F = register_fonts(lang)
    prods = load_products()
    by = members_by_cat(prods)

    # ---- пагинация (обложка=1, содержание=2, контент с 3) ----
    PER = 2
    ranges = {}
    pg = 5
    for cat in CAT_ORDER:
        n = len(by[cat])
        pages = max(1, math.ceil(n / PER))
        ranges[cat] = (pg, pg + pages - 1, n)
        pg += pages
    total = pg - 1

    hero = [os.path.join(ROOT, f"img/products/{x}/1.webp") for x in (
        "101-belo-rozovaya-roza-korzina-rozovaya-lenta",
        "51-krasnaya-roza-belaya-upakovka-krasnaya-lenta",
        "yarkaya-sbornaya-korzina-nabor-sharov-l-cifry-29")]
    t = dict(t, _lang=lang)
    c = canvas.Canvas(out_path, pagesize=A4)
    c.setTitle(f"Каталог {version}")
    draw_cover(c, F, t, hero, version)
    draw_info(c, F, t, lang)
    draw_info_cats(c, F, t, lang, by, ranges)
    draw_toc(c, F, t, ranges)

    page_no = 5
    for cat in CAT_ORDER:
        items = by[cat]
        chunks = [items[i:i+PER] for i in range(0, len(items), PER)] or [[]]
        for ci, chunk in enumerate(chunks):
            if ci == 0:
                y = draw_cat_header(c, F, t, cat, len(items))
            else:
                # тонкая плашка-продолжение
                c.setFillColor(GREY); c.setFont(F["serifi"], 11)
                c.drawString(M, PH-M-6, t["cats"][cat])
                c.setStrokeColor(LINE); c.setLineWidth(0.6); c.line(M, PH-M-14, PW-M, PH-M-14)
                y = PH - M - 30
            for p in chunk:
                used = draw_card(c, F, t, p, lang, M, y, CW)
                y -= used + 30
            draw_footer(c, F, t, page_no, t["cats"][cat])
            c.showPage()
            page_no += 1

    c.save()
    return total, out_path

if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "ru"
    out = sys.argv[2] if len(sys.argv) > 2 else f"/tmp/catalog_{lang}.pdf"
    version = sys.argv[3] if len(sys.argv) > 3 else "2.0"
    total, path = build(lang, out, version)
    print(f"{lang}: {total} страниц → {path}")
