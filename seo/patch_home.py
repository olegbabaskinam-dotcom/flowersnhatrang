# -*- coding: utf-8 -*-
"""
Патчит существующие страницы (index/balloons ×3 языка):
  1. добавляет в меню ссылки Каталог / Статьи (desktop + mobile)
  2. вставляет сквозной блок «Статьи» (после Hero на главных, после header на шарах)
  3. на главных: оставляет 6 витринных товаров + кнопка «больше товаров» → каталог
Идемпотентно: повторный запуск не дублирует вставки (метка-маркер).
Запуск: python3 seo/patch_home.py
"""
import os, re, csv
import build_site as B

ROOT = B.ROOT
products = list(csv.DictReader(open(B.PRODUCTS, encoding="utf-8")))

CAT_H2 = {"ru": "наш каталог", "en": "our catalog", "ko": "카탈로그"}
MORE = {"ru": "больше товаров", "en": "more products", "ko": "더 많은 상품"}

# файл -> (lang, is_home)
FILES = {
    "index.html": ("ru", True), "index-en.html": ("en", True), "index-kr.html": ("ko", True),
    "balloons.html": ("ru", False), "balloons-en.html": ("en", False), "balloons-kr.html": ("ko", False),
}

FLAGS = {"ru": "🇷🇺 RU", "en": "🇬🇧 EN", "ko": "🇰🇷 KR"}

def build_nav(lang):
    """Полная навигация (как в build_site.header): Главная, Каталог, Статьи, Шары, | RU EN KR.
    Языково-корректные ссылки. Возвращает (desktop_nav, mobile_nav)."""
    t = B.T[lang]
    def lk(href, label, ind):
        return f'\n{ind}<a href="{href}" class="px-3 py-1.5 rounded-lg text-stone-500 hover:text-[#c0687a] hover:bg-stone-50 transition">{label}</a>'
    def lkm(href, label, ind):
        return f'\n{ind}<a href="{href}" class="px-3 py-1.5 rounded-lg text-stone-500 whitespace-nowrap hover:text-[#c0687a] transition">{label}</a>'
    # переключатели языка
    def flag(l):
        if l == lang:
            return f'\n                <span class="px-3 py-1.5 rounded-lg text-white text-xs font-medium" style="background:#c0687a;">{FLAGS[l]}</span>'
        return f'\n                <a href="{B.HOME[l]}" class="px-3 py-1.5 rounded-lg text-stone-500 hover:text-[#c0687a] hover:bg-stone-50 transition">{FLAGS[l]}</a>'
    def flagm(l):
        if l == lang:
            return f'\n            <span class="px-3 py-1.5 rounded-lg text-white whitespace-nowrap" style="background:#c0687a;">{FLAGS[l]}</span>'
        return f'\n            <a href="{B.HOME[l]}" class="px-3 py-1.5 rounded-lg text-stone-500 whitespace-nowrap hover:text-[#c0687a] transition">{FLAGS[l]}</a>'
    I = "                "
    d = ('<nav class="hidden md:flex items-center gap-1 text-xs font-medium"><!--MARK-NAV-->'
         + lk(B.HOME[lang], t["nav_home"], I)
         + lk(f"catalog-{lang}.html", t["nav_catalog"], I)
         + lk(f"blog-{lang}.html", t["nav_articles"], I)
         + lk(B.BALLOONS[lang], t["nav_balloons"], I)
         + f'\n{I}<span class="w-px h-4 bg-stone-200 mx-1"></span>'
         + "".join(flag(l) for l in B.LANGS)
         + '\n            </nav>')
    Im = "            "
    m = ('<div class="md:hidden border-t border-stone-100 px-4 py-2 flex gap-1 text-xs font-medium overflow-x-auto justify-center"><!--MARK-NAVM-->'
         + lkm(B.HOME[lang], t["nav_home"], Im)
         + lkm(f"catalog-{lang}.html", t["nav_catalog"], Im)
         + lkm(f"blog-{lang}.html", t["nav_articles"], Im)
         + lkm(B.BALLOONS[lang], t["nav_balloons"], Im)
         + f'\n{Im}<span class="w-px h-4 bg-stone-200 mx-1"></span>'
         + "".join(flagm(l) for l in B.LANGS)
         + '\n        </div>')
    return d, m

# витрина на главной: 6 товаров из РАЗНЫХ категорий (для разнообразия)
# 25 роз · лилии · 51 роза · набор шаров · 101 роза в корзине · 151 роза
FEATURED_IDS = ["1", "5", "6", "8", "9", "12"]

def featured_products():
    by_id = {p["id"]: p for p in products}
    sel = [by_id[i] for i in FEATURED_IDS if i in by_id]
    # добор, если каких-то id нет
    if len(sel) < 6:
        for p in products:
            if p not in sel:
                sel.append(p)
            if len(sel) == 6:
                break
    return sel[:6]

def catalog_section(lang):
    t = B.T[lang]
    cards = "\n            ".join(B.product_card(p, lang, "", t) for p in featured_products())
    return f'''<section id="catalog" class="py-16 px-4 max-w-5xl mx-auto flex-grow">
        <a href="catalog-{lang}.html" class="block text-center mb-12 group">
            <h2 class="reveal font-serif text-3xl md:text-4xl font-bold group-hover:text-[#c0687a] transition" style="color:#1a1a1a;">{CAT_H2[lang]}</h2>
            <span class="inline-block mt-3 text-sm font-medium" style="color:#c0687a;">{MORE[lang]} →</span>
        </a>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            {cards}
        </div>
        <div class="text-center mt-10">
            <a href="catalog-{lang}.html" class="btn-rose inline-block font-medium py-3 px-8 rounded-xl text-sm">{MORE[lang]} →</a>
        </div>
    </section>'''

def patch(fname, lang, is_home):
    path = os.path.join(ROOT, fname)
    if not os.path.exists(path):
        print(f"  пропуск (нет файла): {fname}"); return
    s = open(path, encoding="utf-8").read()

    # 0. недостающий стиль кнопки (есть только в сгенерированных страницах)
    if ".btn-rose-filled {" not in s:
        css = ('        .btn-rose-filled { background: var(--rose); color:#fff; border:1.5px solid var(--rose); '
               'transition: background .22s ease, transform .15s ease; }\n'
               '        .btn-rose-filled:hover { background: var(--rose-hover); transform: translateY(-1px); }\n    </style>')
        s = s.replace("    </style>", css, 1)

    # 0b. og:image → абсолютный URL (для превью при шеринге)
    s = re.sub(r'(<meta property="og:image" content=")(?!https?:)([^"]*)(">)',
               lambda mo: f'{mo.group(1)}{B.DOMAIN}/{mo.group(2)}{mo.group(3)}', s)

    # 1. nav — полностью перестраиваем (детерминированно, языково-корректно, идемпотентно)
    d, m = build_nav(lang)
    s = re.sub(r'<nav class="hidden md:flex items-center gap-1 text-xs font-medium">.*?</nav>',
               lambda mo: d, s, count=1, flags=re.S)
    s = re.sub(r'<div class="md:hidden border-t border-stone-100 px-4 py-2 flex gap-1 text-xs font-medium overflow-x-auto justify-center">.*?</div>',
               lambda mo: m, s, count=1, flags=re.S)

    # 2. сквозной блок Статьи (баннер с фото) — после блока «Гелиевые шары»
    # сначала убираем старую вставку, если была (идемпотентность)
    s = re.sub(r'<!--MARK-ARTICLES-->.*?<!--/MARK-ARTICLES-->\s*', '', s, flags=re.S)
    block = '<!--MARK-ARTICLES-->' + B.articles_block(lang, "") + '<!--/MARK-ARTICLES-->\n'
    m = re.search(r'class="block rounded-3xl[^"]*"[^>]*style="height: 340px;"', s)
    if m:  # есть баннер шаров → вставляем после его секции
        j = s.index("</section>", m.end()) + len("</section>")
        s = s[:j] + "\n" + block + s[j:]
    else:  # на страницах шаров — перед футером
        s = s.replace("<footer", block + "\n    <footer", 1)

    # 3. каталог: 6 товаров + кнопка (всегда перестраиваем — секция детерминирована)
    if is_home:
        new = catalog_section(lang).replace('id="catalog"', 'id="catalog" data-mark="MARK-CATALOG"', 1)
        s = re.sub(r'<section id="catalog".*?</section>', lambda mo: new, s, count=1, flags=re.S)

    # 3b. мобайл: скрыть верхний ряд (лого + соцыконки-контакты), оставить тонкое меню
    s = s.replace(
        '<div class="max-w-5xl mx-auto px-4 py-3 flex justify-between items-center">',
        '<div class="max-w-5xl mx-auto px-4 py-3 hidden md:flex justify-between items-center">', 1)

    # 4. часы работы в футер (перед копирайтом), идемпотентно
    s = re.sub(r'<div class="text-center text-xs mt-8" style="color:#a8566a;"><!--MARK-HOURS-->.*?</div>\s*', '', s, flags=re.S)
    hours_div = (f'<div class="text-center text-xs mt-8" style="color:#a8566a;"><!--MARK-HOURS-->'
                 f'\U0001F552 {B.HOURS.get(lang, B.HOURS["ru"])}</div>\n        ')
    s = re.sub(r'(<div class="text-center text-xs mt-10 pt-6")', hours_div + r'\1', s, count=1)

    open(path, "w", encoding="utf-8").write(s)
    print(f"  патч ок: {fname}")

def main():
    for fname, (lang, is_home) in FILES.items():
        patch(fname, lang, is_home)
    print("Готово.")

if __name__ == "__main__":
    main()
