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

def nav_links(lang):
    t = B.T[lang]
    d = (f'\n                <a href="catalog-{lang}.html" class="px-3 py-1.5 rounded-lg text-stone-500 hover:text-[#c0687a] hover:bg-stone-50 transition">{t["nav_catalog"]}</a>'
         f'\n                <a href="blog-{lang}.html" class="px-3 py-1.5 rounded-lg text-stone-500 hover:text-[#c0687a] hover:bg-stone-50 transition">{t["nav_articles"]}</a>')
    m = (f'\n            <a href="catalog-{lang}.html" class="px-3 py-1.5 rounded-lg text-stone-500 whitespace-nowrap hover:text-[#c0687a] transition">{t["nav_catalog"]}</a>'
         f'\n            <a href="blog-{lang}.html" class="px-3 py-1.5 rounded-lg text-stone-500 whitespace-nowrap hover:text-[#c0687a] transition">{t["nav_articles"]}</a>')
    return d, m

def catalog_section(lang):
    t = B.T[lang]
    cards = "\n            ".join(B.product_card(p, lang, "", t) for p in products[:6])
    return f'''<section id="catalog" class="py-16 px-4 max-w-5xl mx-auto flex-grow">
        <h2 class="reveal font-serif text-3xl md:text-4xl font-bold text-center mb-12" style="color:#1a1a1a;">{CAT_H2[lang]}</h2>
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

    # 1. nav links (по маркеру, чтобы не дублировать)
    if "MARK-NAV" not in s:
        d, m = nav_links(lang)
        s = s.replace(
            '<nav class="hidden md:flex items-center gap-1 text-xs font-medium">',
            '<nav class="hidden md:flex items-center gap-1 text-xs font-medium"><!--MARK-NAV-->' + d, 1)
        s = s.replace(
            '<div class="md:hidden border-t border-stone-100 px-4 py-2 flex gap-1 text-xs font-medium overflow-x-auto justify-center">',
            '<div class="md:hidden border-t border-stone-100 px-4 py-2 flex gap-1 text-xs font-medium overflow-x-auto justify-center"><!--MARK-NAVM-->' + m, 1)

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

    # 3. каталог: 6 товаров + кнопка
    if is_home and "MARK-CATALOG" not in s:
        new = catalog_section(lang).replace('id="catalog"', 'id="catalog" data-mark="MARK-CATALOG"', 1)
        s = re.sub(r'<section id="catalog".*?</section>', lambda mo: new, s, count=1, flags=re.S)

    open(path, "w", encoding="utf-8").write(s)
    print(f"  патч ок: {fname}")

def main():
    for fname, (lang, is_home) in FILES.items():
        patch(fname, lang, is_home)
    print("Готово.")

if __name__ == "__main__":
    main()
