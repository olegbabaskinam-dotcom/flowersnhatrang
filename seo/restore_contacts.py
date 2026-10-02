#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Восстановление онлайн-заказа и всех контактов, убранных коммитом f5cff0e9
(«Полная очистка сайта по аудиту», 22.08.2026). Правит ТОЛЬКО блоки контактов,
ничего больше не трогает (build_site.py разошёлся с задеплоенными страницами,
поэтому полную пересборку не используем).

Что делает (идемпотентно):
  Страницы товара RU/EN — CTA-блок заказа: добавляет «Оформить онлайн заказ»
    (../order.html) ПЕРВОЙ кнопкой и Instagram — ПОСЛЕДНЕЙ. KO не трогает (там уже
    онлайн + Kakao + Instagram).
  Шапка (ряд иконок) страниц товара и каталогов-списков:
    RU/EN — добавляет иконку Корзины (cart.html) и Instagram (flowers_vietnam_inst);
    KO — добавляет только Корзину (Instagram уже есть).
Футер, главные, лендинги, статьи — не затрагиваются.
"""
import re, os, sys, glob
import build_site as b

ORDER_SVG = b.ORDER_SVG
IG_SVG = b.IG_SVG
IG_RU = "https://instagram.com/flowers_vietnam_inst"

CART_ARIA = {"ru": "Корзина", "en": "Cart", "ko": "장바구니"}
ONLINE_LABEL = {"ru": "Оформить онлайн заказ", "en": "Order online"}

BTN_CLS = "btn-rose flex items-center justify-center gap-2 font-medium py-2.5 px-4 rounded-xl text-xs w-full"
ICON_CLS = "text-stone-400 hover:text-[#c0687a] transition"

HDR_RE = re.compile(r'(<div class="hidden md:flex gap-4 text-xl">)(.*?)(</div>)', re.S)
CTA_RE = re.compile(r'(<div class="flex flex-col gap-4">)(.*?)(</div>)', re.S)


def lang_of(fn):
    base = os.path.basename(fn)
    if base.endswith("-ru.html") or base == "catalog-ru.html":
        return "ru"
    if base.endswith("-en.html") or base == "catalog-en.html":
        return "en"
    if base.endswith("-ko.html") or base == "catalog-ko.html":
        return "ko"
    return None


def patch_header(s, lang, base):
    def repl(m):
        open_tag, inner, close = m.group(1), m.group(2), m.group(3)
        add_cart = ""
        if "cart.html" not in inner:
            add_cart = (f'<a href="{base}cart.html" class="{ICON_CLS}" '
                        f'aria-label="{CART_ARIA[lang]}">{ORDER_SVG}</a>')
        add_ig = ""
        if lang in ("ru", "en") and "flowers_vietnam_inst" not in inner:
            add_ig = (f'<a href="{IG_RU}" target="_blank" rel="noopener noreferrer" '
                      f'class="{ICON_CLS}" aria-label="Instagram">{IG_SVG}</a>')
        return open_tag + add_cart + inner + add_ig + close
    return HDR_RE.sub(repl, s, count=1)


def patch_cta(s, lang):
    if lang not in ("ru", "en"):
        return s

    def repl(m):
        open_tag, inner, close = m.group(1), m.group(2), m.group(3)
        if "order.html" in inner:          # уже восстановлено
            return m.group(0)
        online = (f'\n                    <a href="../order.html" class="{BTN_CLS}">'
                  f'{ORDER_SVG} {ONLINE_LABEL[lang]}</a>')
        ig = (f'\n                    <a href="{IG_RU}" target="_blank" rel="noopener noreferrer" '
              f'class="{BTN_CLS}">{IG_SVG} Instagram</a>')
        return open_tag + online + inner.rstrip() + ig + "\n                " + close
    return CTA_RE.sub(repl, s, count=1)


def process(fn):
    lang = lang_of(fn)
    if not lang:
        return None
    is_product = ("catalog" + os.sep) in fn or "/catalog/" in fn.replace(os.sep, "/")
    base = "../" if is_product else ""
    s0 = open(fn, encoding="utf-8").read()
    s = patch_header(s0, lang, base)
    if is_product:
        s = patch_cta(s, lang)
    if s != s0:
        open(fn, "w", encoding="utf-8").write(s)
        return True
    return False


def main():
    root = b.ROOT
    files = sorted(glob.glob(os.path.join(root, "catalog", "*.html")))
    files += [os.path.join(root, f"catalog-{l}.html") for l in ("ru", "en", "ko")]
    changed = 0
    for fn in files:
        if process(fn):
            changed += 1
    print(f"изменено файлов: {changed} из {len(files)}")


if __name__ == "__main__":
    main()
