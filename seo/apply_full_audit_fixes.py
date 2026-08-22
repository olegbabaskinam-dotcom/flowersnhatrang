#!/usr/bin/env python3
"""Идемпотентная массовая чистка по «Полному аудиту сайта 2.0» (21.08.2026).

Скрипт трогает только отслеживаемые Git файлы. Он нужен после пересборки
старых статических страниц, чтобы единообразно:
  * убирать устаревшие same-day/24×7-обещания;
  * укорачивать перегруженные title/description;
  * добавлять noopener и размеры локальных изображений;
  * чинить hreflang страниц наборов;
  * синхронизировать фактически опубликованные статьи с registry.csv.
"""

from __future__ import annotations

import csv
import html as html_lib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://flowers-nha-trang.online"


def tracked_files() -> list[Path]:
    out = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / p.decode("utf-8") for p in out.split(b"\0") if p]


def replace_business_copy(text: str) -> str:
    replacements = [
        ("Когда можна ближайшая доставка?", "Когда возможна ближайшая доставка?"),
        ("доставим по Нячангу в день заказа", "доставка по Нячангу со следующего дня"),
        ("Доставка день в день", "Онлайн-доставка со следующего дня"),
        ("доставка день в день", "онлайн-доставка со следующего дня"),
        ("День в день", "Со следующего дня"),
        ("день в день", "со следующего дня"),
        ("Same-day delivery", "Online delivery from the next day"),
        ("same-day delivery", "online delivery from the next day"),
        ("Same-day", "Next-day"),
        ("same-day", "next-day"),
        ("당일 배송", "주문 다음 날부터 배송"),
        ("당일 꽃배달", "주문 다음 날부터 꽃배달"),
        ("당일배달", "익일배달"),
        ("당일배송", "익일배송"),
        ("나트랑 당일 배달", "나트랑 주문 다음 날부터 배달"),
        ("당일 배달", "주문 다음 날부터 배달"),
        ("당일입니다", "주문 다음 날부터입니다"),
        ("Доставим оба букета по Нячангу в день заказа", "Онлайн-доставка обоих букетов по Нячангу со следующего дня"),
        ("Доставим по Нячангу в день заказа", "Онлайн-доставка по Нячангу со следующего дня"),
        ("доставим по Нячангу в день заказа", "онлайн-доставка по Нячангу со следующего дня"),
        ("доставим и аккуратно расставим по Нячангу в день заказа", "онлайн-доставка со следующего дня и аккуратная расстановка по Нячангу"),
        ("we deliver and set them up across Nha Trang the same day", "online delivery from the next day with careful setup across Nha Trang"),
        ("привезём и расставим по Нячангу в день заказа", "привезём и расставим по Нячангу со следующего дня"),
        ("привезём и запустим по Нячангу в день заказа", "привезём и запустим по Нячангу со следующего дня"),
        ("Доставка по Нячангу бесплатная и в день заказа", "Доставка по Нячангу бесплатная, со следующего дня"),
        ("Fresh bouquets same day", "Fresh bouquets from the next day"),
        ("same day delivery", "delivery from the next day"),
        ("receive the same day", "receive from the next day"),
        ("the day you order", "from the next day"),
        ("Usually the same day for requests by 6 p.m.", "Online delivery is available from the next day."),
        ("Same day for orders before 6 p.m.", "Online delivery is available from the next day."),
        ("Timing: same day and morning surprises", "Timing: next-day delivery and morning surprises"),
        ("For orders before 6 p.m. we deliver the same day", "Online orders are available for delivery from the next day"),
        ("Yes, for orders before 6 p.m., but", "Online delivery is available from the next day, but"),
        ("Open ежедневно 06:00–22:00", "Open daily 06:00–22:00"),
        ("Free city delivery, same day", "Free city delivery from the next day"),
        ("Within Nha Trang — same day for orders before 8 PM, usually in 1–2 hours.", "Within Nha Trang, online delivery is available from the next day. A specific time is possible by arrangement."),
        ("по Нячангу и Камрани, в день заказа", "по Нячангу и северной части Камрани со следующего дня"),
        ("주문 당일", "주문 다음 날부터"),
        ("당일 가능합니다", "주문 다음 날부터 가능합니다"),
        ("same day delivery flowers", "next day delivery flowers"),
        ("next-day freshness", "same-day freshness"),
        ("Бесплатная доставка по городу. Закажи до 18:00 — привезём сегодня.", "Бесплатная доставка по городу. Онлайн-заказы доставляем со следующего дня."),
        ("Бесплатная доставка по городу. Закажи до 20:00 — привезём сегодня.", "Бесплатная доставка по городу. Онлайн-заказы доставляем со следующего дня."),
        ("Free delivery across the city. Order before 18:00 — delivered today.", "Free delivery across the city. Online orders are delivered from the next day."),
        ("Free delivery across the city. Order before 20:00 — delivered today.", "Free delivery across the city. Online orders are delivered from the next day."),
        ("sets S, M, L and combos with flowers — same day delivery until 20:00", "sets S, M, L and flower combos — online delivery from the next day"),
        ("по всему Нячангу и Камрани", "по Нячангу и северной части Камрани"),
        ("по Нячангу и Камрани", "по Нячангу и северной части Камрани"),
        ("across Nha Trang and Cam Ranh", "across Nha Trang and northern Cam Ranh"),
        ("throughout Nha Trang and Cam Ranh", "throughout Nha Trang and northern Cam Ranh"),
        ("나트랑과 깜라인 전역", "나트랑과 깜라인 북부"),
        ("24/7", "ежедневно 06:00–22:00"),
        ("24×7", "ежедневно 06:00–22:00"),
        ("24 hours a day", "daily from 06:00 to 22:00"),
        ("24 hours", "daily 06:00–22:00"),
        ("24시간 운영", "매일 06:00~22:00 운영"),
        ("연중무휴", "매일 운영"),
        ("63 провинции объединили в 34", "63 единицы провинциального уровня реорганизовали в 34"),
        ("63 provinces were merged into 34", "63 provincial-level units were reorganised into 34"),
        ("63개 성을 34개로 통합", "63개 성급 행정단위를 34개로 개편"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    # Оставляем исторические упоминания «в тот же день» в статьях, но убираем
    # их из коммерческих обещаний рядом со словами delivery/deliver/доставка.
    text = re.sub(
        r"((?:deliver(?:y|ed|s|ing)?)[^<\n\"]{0,220}?)(?:on )?(?:the )?same day",
        lambda m: m.group(1) + "from the next day",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"((?:достав\w*|привез\w*)[^<\n\"]{0,220}?)в (?:тот же )?день заказа",
        lambda m: m.group(1) + "со следующего дня",
        text,
        flags=re.I,
    )
    text = re.sub(r"당일(?=[^<\n\"]{0,70}(?:꽃?배달|배송))", "주문 다음 날부터", text)
    return text.replace("\x02", "")


def limit_operator_sameday_to_home(path: Path, text: str) -> str:
    """Срочная доставка через оператора рекламируется только на трёх главных."""
    if path.parent == ROOT and path.name in {"index.html", "index-en.html", "index-kr.html"}:
        return text
    replacements = [
        ("онлайн-заказы — со следующего дня; срочная доставка сегодня — через оператора до 18:00.", "онлайн-доставка со следующего дня."),
        ("online orders start next day; urgent delivery today is available via an operator until 18:00.", "online delivery starts from the next day."),
        ("온라인 주문은 다음 날부터; 오늘 긴급 배송은 18:00까지 상담원을 통해 주문할 수 있습니다.", "온라인 주문은 다음 날부터 배달합니다."),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def fix_ko_payment_copy(text: str) -> str:
    replacements = [
        ("결제: 동, 달러, 루블, USDT, 현금", "결제: 수령 시 현금 또는 암호화폐 송금"),
        ("동, 달러, 루블, USDT, 현금", "수령 시 현금 또는 암호화폐 송금"),
        ("동, 루블, 달러, USDT 또는 현금", "수령 시 현금 또는 암호화폐 송금"),
        ("동·달러·루블 결제", "현금·암호화폐 결제"),
        ("루블(SBP), 동, USDT(TRC-20) 또는 Kaspi 카드", "수령 시 현금 또는 암호화폐 송금"),
        ("WhatsApp 또는 Telegram으로 문의해 주세요", "카카오톡으로 문의해 주세요"),
        ("WhatsApp이나 Telegram 또는 KakaoTalk", "카카오톡"),
        ("WhatsApp, Telegram 또는 KakaoTalk", "카카오톡"),
        ("WhatsApp이나 Telegram", "카카오톡"),
        ("WhatsApp 또는 Telegram", "카카오톡"),
        ("결제는 여행자에게 편리합니다: 동, 달러, 루블, USDT, 현금.", "결제는 수령 시 현금 또는 암호화폐 송금입니다."),
        ("결제는 여행자에게 편리합니다: 동, 루블, 달러, USDT, 현금.", "결제는 수령 시 현금 또는 암호화폐 송금입니다."),
        ("결제는 편리합니다: 동·루블·달러·USDT·현금.", "결제는 수령 시 현금 또는 암호화폐 송금입니다."),
        ("결제는 동·루블·달러·USDT·현금으로 편리합니다.", "결제는 수령 시 현금 또는 암호화폐 송금입니다."),
        ("나트랑 꽃값 결제: 루블·동·달러", "나트랑 꽃 배달 결제 안내: 현금·암호화폐"),
        ("여행자에게 편리한 모든 결제 방법: 루블·동·달러·USDT·현금 — 다른 나라에서 원격으로도 편하게 결제하세요.", "한국 고객은 수령 시 현금 또는 암호화폐 송금으로 결제할 수 있습니다."),
        ("동, 루블, 달러, USDT, 착불 현금", "수령 시 현금 또는 암호화폐 송금"),
        ("동·루블·달러·USDT·현금", "수령 시 현금 또는 암호화폐 송금"),
        ("루블·동·달러·USDT·현금", "수령 시 현금 또는 암호화폐 송금"),
        ("루블·동·달러 결제 가능", "수령 시 현금 또는 암호화폐 송금 가능"),
        ("카카오톡 또는 KakaoTalk", "카카오톡"),
        ("카카오톡, KakaoTalk", "카카오톡"),
        ("카카오톡, 카카오톡", "카카오톡"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    forbidden = r"(?:루블|러시아 카드|카자흐|Kaspi|SBP)"
    text = re.sub(
        rf"결제[^<\n\"]{{0,180}}{forbidden}[^.<\n\"]*[.。]?",
        "결제는 수령 시 현금 또는 암호화폐 송금입니다.",
        text,
        flags=re.I,
    )
    text = re.sub(
        rf"{forbidden}[^<\n\"]{{0,140}}결제[^.<\n\"]*[.。]?",
        "결제는 수령 시 현금 또는 암호화폐 송금입니다.",
        text,
        flags=re.I,
    )
    return text


def fix_ko_language_leaks(path: Path, text: str) -> str:
    """Убирает русские служебные слова и нелогичные дедлайны из KO-интерфейса."""
    lang_match = re.search(r'<html\b[^>]*\blang=["\']([^"\']+)', text, re.I)
    if not lang_match or not lang_match.group(1).lower().startswith("ko"):
        return text
    replacements = [
        ("나트랑 꽃집·꽃배달 — 장미 꽃다발 익일배달 ежедневно 06:00–22:00", "나트랑 꽃집·꽃배달 — 장미·꽃다발, 매일 06:00–22:00"),
        ("나트랑 꽃 배달 ежедневно 06:00–22:00 — 꽃다발·장미 | NhaTrang Flowers", "나트랑 꽃 배달 — 꽃다발·장미, 매일 06:00–22:00"),
        ("ежедневно 06:00–22:00", "매일 06:00–22:00"),
        (" донгов", "동"),
        ('aria-label="Корзина" title="Корзина"', 'aria-label="장바구니" title="장바구니"'),
        ('aria-label="Меню"', 'aria-label="메뉴"'),
        ("냐짱 무료 배달. 18:00 전 주문 시 주문 다음 날부터 배달.", "냐짱 시내 무료 배달. 온라인 주문은 다음 날부터 배달합니다."),
        ("냐짱 꽃과 헬륨 풍선 주문 다음 날부터 배달. 시내 무료 배달. 18:00 전 주문 시 주문 다음 날부터 배달.", "냐짱 꽃과 헬륨 풍선은 온라인 주문 다음 날부터 배달합니다. 시내 배달은 무료입니다."),
        ("S, M, L 세트 및 꽃과의 콤보 — 20:00 전 주문 시 주문 다음 날부터 배달", "S, M, L 세트 및 꽃과의 콤보 — 온라인 주문은 다음 날부터 배달"),
        ("모든 기념일을 위한 케이크와 디저트 — 식기 포함, 예쁜 상자에 담아 주문 다음 날부터 배달", "모든 기념일을 위한 케이크와 디저트 — 식기 포함, 예쁜 상자에 담아 온라인 주문 다음 날부터 배달"),
        ("완성된 선물 — 베트남 화장품과 커피, 예쁘게 포장, 주문 다음 날부터 배달", "완성된 선물 — 베트남 화장품과 커피, 예쁘게 포장해 온라인 주문 다음 날부터 배달"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def add_noopener(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        if re.search(r"\brel\s*=", tag, re.I):
            current = re.search(r"\brel\s*=\s*([\"'])(.*?)\1", tag, re.I)
            if current and "noopener" not in current.group(2).lower():
                value = (current.group(2) + " noopener noreferrer").strip()
                tag = tag[: current.start(2)] + value + tag[current.end(2) :]
            return tag
        # Одинарные кавычки безопасны и для обычного HTML, и для HTML-фрагментов
        # внутри JavaScript-строк, которые в проекте ограничены двойными кавычками.
        return tag[:-1] + " rel='noopener noreferrer'>"

    return re.sub(r"<a\b[^>]*\btarget\s*=\s*([\"'])_blank\1[^>]*>", repl, text, flags=re.I)


def shorten(value: str, limit: int) -> str:
    plain = html_lib.unescape(value).strip()
    if len(plain) <= limit:
        return value
    for suffix in (" | NhaTrang Flowers", " — NhaTrang Flowers"):
        if plain.endswith(suffix):
            plain = plain[: -len(suffix)].rstrip()
    if len(plain) > limit:
        cut = plain[: limit - 1].rsplit(" ", 1)[0].rstrip(" .,—-:;")
        plain = (cut or plain[: limit - 1]).rstrip() + "…"
    return html_lib.escape(plain, quote=True)


def fix_metadata(text: str) -> str:
    text = re.sub(
        r"(<title>)(.*?)(</title>)",
        lambda m: m.group(1) + shorten(m.group(2), 60) + m.group(3),
        text,
        count=1,
        flags=re.I | re.S,
    )

    def meta_repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        cm = re.search(r'\bcontent\s*=\s*"([^"]*)"', tag, re.I)
        if not cm:
            return tag
        limit = 60 if re.search(r'(?:og:title|twitter:title)', tag, re.I) else 160
        return tag[: cm.start(1)] + shorten(cm.group(1), limit) + tag[cm.end(1) :]

    return re.sub(
        r'<meta\b[^>]*(?:name\s*=\s*"description"|property\s*=\s*"og:(?:title|description)"|name\s*=\s*"twitter:(?:title|description)")[^>]*>',
        meta_repl,
        text,
        flags=re.I,
    )


def fix_nabory_hreflang(path: Path, text: str) -> str:
    if path.name not in {"nabory.html", "nabory-en.html", "nabory-kr.html"}:
        return text
    block = "\n".join(
        [
            f'    <link rel="alternate" hreflang="ru" href="{DOMAIN}/nabory.html">',
            f'    <link rel="alternate" hreflang="en" href="{DOMAIN}/nabory-en.html">',
            f'    <link rel="alternate" hreflang="ko" href="{DOMAIN}/nabory-kr.html">',
            f'    <link rel="alternate" hreflang="x-default" href="{DOMAIN}/nabory.html">',
        ]
    )
    start_tag = text.find('<link rel="alternate"')
    start = text.rfind("\n", 0, start_tag) + 1 if start_tag != -1 else -1
    end = text.find('<meta name="description"', start_tag)
    if start_tag != -1 and end != -1:
        text = text[:start] + block + "\n    " + text[end:]
    return text


def resolve_image(html_path: Path, src: str) -> Path | None:
    src = unquote(src.split("?", 1)[0].split("#", 1)[0])
    if not src or src.startswith(("http://", "https://", "data:", "//")):
        return None
    candidate = (ROOT / src.lstrip("/")) if src.startswith("/") else (html_path.parent / src).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def fix_images(path: Path, text: str) -> str:
    image_index = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal image_index
        tag = match.group(0)
        current_index = image_index
        image_index += 1
        sm = re.search(r'\bsrc\s*=\s*(["\'])(.*?)\1', tag, re.I | re.S)
        if not sm:
            return tag
        image_path = resolve_image(path, sm.group(2))
        additions: list[str] = []
        if image_path and (not re.search(r"\bwidth\s*=", tag, re.I) or not re.search(r"\bheight\s*=", tag, re.I)):
            try:
                with Image.open(image_path) as im:
                    width, height = im.size
                if not re.search(r"\bwidth\s*=", tag, re.I):
                    additions.append(f'width="{width}"')
                if not re.search(r"\bheight\s*=", tag, re.I):
                    additions.append(f'height="{height}"')
            except Exception:
                pass
        if current_index > 0 and not re.search(r"\bloading\s*=", tag, re.I):
            additions.append('loading="lazy"')
        if not re.search(r"\bdecoding\s*=", tag, re.I):
            additions.append('decoding="async"')
        if not additions:
            return tag
        return tag[:-1].rstrip() + " " + " ".join(additions) + ">"

    return re.sub(r"<img\b[^>]*>", repl, text, flags=re.I | re.S)


def swap_duplicate_covers(text: str) -> str:
    swaps = {
        "img/blog/buket-kollege-delovoy-podarok-nyachang.webp": "img/blog/buket-kollege-delovoy-podarok-nyachang/scene39.webp",
        "img/blog/cvety-izvineniya-pomiritsya-nyachang.webp": "img/blog/cvety-izvineniya-pomiritsya-nyachang/scene11.webp",
        "img/blog/buket-na-8-marta-nyachang.webp": "img/blog/buket-na-8-marta-nyachang/scene06.webp",
        "img/blog/cvety-na-14-fevralya-nyachang.webp": "img/blog/cvety-na-14-fevralya-nyachang/scene23.webp",
        "img/blog/idei-buketov-na-godovschinu-svadby-gid-dlya-turista-v-nyachange.webp": "img/products/101-krasnaya-roza-krasnaya-lenta/1.webp",
        "img/blog/idei-buketov-na-godovschinu-svadby-gid-dlya-turista-v-nyachange-thumb.webp": "img/products/101-krasnaya-roza-krasnaya-lenta/2.webp",
    }
    for old, new in swaps.items():
        text = text.replace(old, new)
    return text


def normalise_navigation(path: Path, text: str) -> str:
    """Единое публичное меню: главная, каталог, статьи, шары, торты, наборы."""
    if path.name in {"cart.html", "order.html", "checkout.html", "zakaz.html", "Dialog.html"}:
        return text
    lang_match = re.search(r'<html\b[^>]*\blang=["\']([^"\']+)', text, re.I)
    if not lang_match or not re.search(r"<nav\b[^>]*>.*?</nav>", text, re.I | re.S):
        return text
    lang = lang_match.group(1).lower()
    code = "ko" if lang.startswith("ko") else ("en" if lang.startswith("en") else "ru")
    base = "../" if path.parent != ROOT else ""
    pages = {
        "ru": ("index.html", "catalog-ru.html", "blog-ru.html", "balloons.html", "torty.html", "nabory.html"),
        "en": ("index-en.html", "catalog-en.html", "blog-en.html", "balloons-en.html", "torty-en.html", "nabory-en.html"),
        "ko": ("index-kr.html", "catalog-ko.html", "blog-ko.html", "balloons-kr.html", "torty-kr.html", "nabory-kr.html"),
    }
    labels = {
        "ru": ("🏠 Главная", "💐 Каталог", "📖 Статьи", "🎈 Шары", "🎂 Торты", "🎁 Наборы"),
        "en": ("🏠 Home", "💐 Catalog", "📖 Articles", "🎈 Balloons", "🎂 Cakes", "🎁 Gift sets"),
        "ko": ("🏠 홈", "💐 카탈로그", "📖 블로그", "🎈 풍선", "🎂 케이크", "🎁 선물 세트"),
    }
    items = "\n".join(
        f'                <a href="{base}{page}" class="px-3 py-1.5 rounded-lg text-stone-500 hover:text-[#c0687a] hover:bg-stone-50 transition">{label}</a>'
        for page, label in zip(pages[code], labels[code])
    )
    nav = '<nav class="hidden lg:flex items-center gap-1 text-xs font-medium">\n' + items + "\n            </nav>"
    text = re.sub(r"<nav\b[^>]*>.*?</nav>", nav, text, count=1, flags=re.I | re.S)
    mobile_items = "".join(
        f'<a href="{base}{page}" style="display:block;padding:10px 8px;border-radius:8px;color:#57534e;text-decoration:none">{label}</a>'
        for page, label in zip(pages[code], labels[code])
    )
    mobile = '<div id="mnav" class="hidden" style="border-top:1px solid #f5f5f4;padding:8px;background:#fff;font-size:14px;font-weight:500;max-width:64rem;margin:0 auto">' + mobile_items + "</div>"
    return re.sub(r'<div\s+id=["\']mnav["\'][^>]*>.*?</div>', mobile, text, count=1, flags=re.I | re.S)


def remove_unverified_social_proof(text: str) -> str:
    text = re.sub(r'\s*"aggregateRating"\s*:\s*\{[^{}]*\},\s*', "\n      ", text)
    text = re.sub(r',\s*"aggregateRating"\s*:\s*\{[^{}]*\}', "", text)
    replacements = {
        ">1000+</div>": ">💐</div>",
        ">букетов доставлено</div>": ">свежие букеты</div>",
        ">bouquets delivered</div>": ">fresh bouquets</div>",
        ">배달 완료</div>": ">신선한 꽃다발</div>",
        ">5.0</span>": ">Google</span>",
        ">148 отзывов на Google</div>": ">отзывы на Google</div>",
        ">148 Google reviews</div>": ">reviews on Google</div>",
        ">구글 148 Google 리뷰</div>": ">Google 리뷰</div>",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def ensure_utility_noindex(path: Path, text: str) -> str:
    utilities = {
        "Dialog.html", "SEO_АУДИТ_17-06-2026.html", "РЕКЛАМА_запуск_WhatsApp.html",
        "cart.html", "order.html", "checkout.html", "zakaz.html", "buh/index.html", "tg/index.html",
    }
    relative = path.relative_to(ROOT).as_posix()
    if relative not in utilities or re.search(r'<meta\s+name=["\']robots["\']', text, re.I):
        return text
    viewport = re.search(r'<meta\s+name=["\']viewport["\'][^>]*>', text, re.I)
    marker = viewport.end() if viewport else text.lower().find("</head>")
    if marker == -1:
        return text
    return text[:marker] + '\n    <meta name="robots" content="noindex,nofollow">' + text[marker:]


def neutralise_static_reviews(path: Path, text: str) -> str:
    if path.name == "cart.html":
        text = re.sub(r"<!--REVIEWS-START-->.*?</section>", "", text, count=1, flags=re.I | re.S)
    lang_match = re.search(r'<html\b[^>]*\blang=["\']([^"\']+)', text, re.I)
    lang = (lang_match.group(1).lower() if lang_match else "ru")
    if lang.startswith("ko"):
        sections = list(re.finditer(r"<section\b[^>]*>.*?</section>", text, re.I | re.S))
        for section in reversed(sections):
            if 'class="rv-wrap"' in section.group(0) or "class='rv-wrap'" in section.group(0):
                text = text[: section.start()] + text[section.end() :]
        return text
    label = "Google 리뷰" if lang.startswith("ko") else ("review on Google" if lang.startswith("en") else "отзыв на Google")
    text = re.sub(
        r'(<div\s+class=["\']rv-date["\']>).*?(</div>)',
        lambda m: m.group(1) + label + m.group(2),
        text,
        flags=re.I | re.S,
    )
    text = re.sub(
        r'(<div\s+class=["\']rv-rate["\']>\s*<span\s+class=["\']s["\']>★{5}</span>)\s*<span>.*?</span>(</div>)',
        lambda m: m.group(1) + m.group(2),
        text,
        flags=re.I | re.S,
    )
    return text


def fix_korean_payment_article() -> None:
    """Корейская версия предлагает только реально доступные для неё способы оплаты."""
    path = ROOT / "seo/articles/oplata-cvetov-rublyami-dongami-i-dollarami-v-nyachange.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["ko"] = {
        "title": "나트랑 꽃 배달 결제 안내: 현금·암호화폐",
        "h1": "나트랑 꽃 배달 결제 방법",
        "meta": "한국 고객을 위한 나트랑 꽃 배달 결제 안내. 수령 시 현금 또는 암호화폐 송금으로 결제하며 카카오톡에서 금액과 방법을 확정합니다.",
        "excerpt": "한국 고객은 수령 시 현금 또는 암호화폐 송금으로 결제할 수 있습니다. 주문 전에 카카오톡으로 정확한 금액과 방법을 안내합니다.",
        "intro": "한국 고객의 주문은 간단합니다. 카카오톡에서 상품과 배달 정보를 확인한 뒤 수령 시 현금 또는 안내받은 암호화폐 지갑으로 결제합니다. 주문 확정 전에 최종 금액과 결제 절차를 명확히 알려드립니다.",
        "sections": [
            {
                "h2": "이용 가능한 결제 수단",
                "html": "<p class=\"text-stone-600 leading-relaxed mb-4\">한국 고객은 <b>수령 시 현금</b> 또는 <b>암호화폐 송금</b>으로 결제할 수 있습니다.</p><p class=\"text-stone-600 leading-relaxed\">암호화폐를 선택하면 주문 확정 전에 담당자가 정확한 지갑 주소와 네트워크를 안내합니다. 안내를 확인하기 전에는 송금하지 마세요.</p>",
            },
            {
                "h2": "가격은 어떻게 확인하나요",
                "html": "<p class=\"text-stone-600 leading-relaxed mb-4\">기본 가격은 베트남 동(VND) 기준이며, 사이트의 원화 표시는 비교를 위한 참고 금액입니다.</p><p class=\"text-stone-600 leading-relaxed\">최종 결제 금액은 주문 확정 전에 카카오톡으로 다시 안내해 드립니다.</p>",
            },
            {
                "h2": "다른 나라에서 주문하는 경우",
                "html": "<p class=\"text-stone-600 leading-relaxed mb-4\">해외에서도 나트랑에 있는 가족이나 친구에게 꽃을 주문할 수 있습니다. 카카오톡으로 상품, 받는 분 정보와 날짜를 보내 주세요.</p><p class=\"text-stone-600 leading-relaxed\">배달 전 완성된 꽃다발 사진을 보내드립니다.</p>",
            },
            {
                "h2": "주문 확정과 배달",
                "html": "<p class=\"text-stone-600 leading-relaxed mb-4\">온라인 주문은 다음 날부터 배달할 수 있습니다. 나트랑 시내는 무료이며, 남부 외곽은 300,000동, 바이다이·깜라인 북부는 600,000동입니다.</p><p class=\"text-stone-600 leading-relaxed\">섬 지역, 깜라인 공항 및 공항 남쪽 지역은 배달하지 않습니다. 주문은 카카오톡에서 최종 확인 후 확정됩니다.</p>",
            },
        ],
        "faq": [
            ["한국 카드로 결제할 수 있나요?", "현재 한국 고객은 수령 시 현금 또는 암호화폐 송금으로 결제할 수 있습니다."],
            ["암호화폐는 어디로 보내나요?", "주문 확정 전에 카카오톡 담당자가 정확한 지갑 주소와 네트워크를 안내합니다."],
            ["원화 가격이 최종 금액인가요?", "사이트의 원화 표시는 참고용입니다. 최종 금액은 주문 확정 전에 카카오톡으로 안내합니다."],
            ["배달은 언제부터 가능한가요?", "온라인 주문은 다음 날부터 가능하며 나트랑 시내 배달은 무료입니다."],
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def optimise_product_images(files: list[Path]) -> int:
    changed = 0
    for path in files:
        if path.suffix.lower() != ".webp" or "img/products/" not in path.as_posix():
            continue
        # В индексе репозитория есть несколько исторических фото, удалённых из
        # рабочей копии до аудита. Они не используются сайтом и не должны останавливать чистку.
        if not path.exists():
            continue
        try:
            with Image.open(path) as original:
                if max(original.size) <= 1200:
                    continue
                image = ImageOps.exif_transpose(original).copy()
            image.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            temp = path.with_suffix(".audit-tmp.webp")
            image.save(temp, "WEBP", quality=88, method=6)
            temp.replace(path)
            changed += 1
        except Exception as exc:
            raise RuntimeError(f"Не удалось оптимизировать {path}: {exc}") from exc
    return changed


def sync_registry() -> tuple[int, int]:
    path = ROOT / "seo/registry.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    for row in rows:
        for key, value in row.items():
            row[key] = value.strip() if isinstance(value, str) else value
    published = {p.name[: -len("-ru.html")] for p in (ROOT / "blog").glob("*-ru.html")}
    by_slug = {row["slug"]: row for row in rows}
    updated = 0
    added = 0
    for slug in sorted(published):
        row = by_slug.get(slug)
        placeholder_row = row is None or row.get("category") in {"", "Опубликовано"}
        article_path = ROOT / "blog" / f"{slug}-ru.html"
        article_text = article_path.read_text(encoding="utf-8") if article_path.exists() else ""
        category_match = re.search(r'<span class="text-xs font-medium"[^>]*>([^<·]+?)\s*·', article_text)
        date_match = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})"', article_text)
        title_match = re.search(r'"headline"\s*:\s*"([^"]+)"', article_text)
        if row is None:
            row = {field: "" for field in fields}
            row.update(
                {
                    "id": str(max([int(r["id"]) for r in rows if r.get("id", "").isdigit()] + [0]) + 1),
                    "type": "article",
                    "category": "Опубликовано",
                    "keyword_ru": slug.replace("-", " "),
                    "title_ru": slug.replace("-", " ").capitalize(),
                    "slug": slug,
                    "status_ru": "done",
                    "status_en": "done",
                    "status_ko": "done",
                }
            )
            rows.append(row)
            by_slug[slug] = row
            added += 1
        if row.get("category") in {"", "Опубликовано"} and category_match:
            row["category"] = html_lib.unescape(category_match.group(1)).strip()
        if not row.get("date") and date_match:
            row["date"] = date_match.group(1)
        if (not row.get("title_ru") or placeholder_row) and title_match:
            row["title_ru"] = html_lib.unescape(title_match.group(1)).strip()
        if any(row.get(key) != "done" for key in ("status_ru", "status_en", "status_ko")):
            row["status_ru"] = row["status_en"] = row["status_ko"] = "done"
            updated += 1
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return updated, added


def main() -> None:
    fix_korean_payment_article()
    files = tracked_files()
    resized = optimise_product_images(files)
    changed = 0
    changed_paths: list[str] = []
    for path in files:
        # Python-сценарии не прогоняем через текстовые замены: иначе скрипт
        # может переписать собственные шаблоны и правила проверки.
        if path.suffix.lower() not in {".html", ".js", ".json", ".csv", ".xml", ".txt", ".md"}:
            continue
        try:
            old = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new = fix_ko_payment_copy(replace_business_copy(old))
        new = limit_operator_sameday_to_home(path, new)
        if path.suffix.lower() == ".html":
            new = fix_ko_language_leaks(path, new)
            new = ensure_utility_noindex(path, new)
            new = remove_unverified_social_proof(new)
            new = fix_nabory_hreflang(path, new)
            new = swap_duplicate_covers(new)
            new = neutralise_static_reviews(path, new)
            new = normalise_navigation(path, new)
            new = add_noopener(new)
            new = fix_metadata(new)
            new = fix_images(path, new)
        new = re.sub(r"[ \t]+(?=\r?$)", "", new, flags=re.M)
        if new != old:
            path.write_text(new, encoding="utf-8")
            changed += 1
            changed_paths.append(path.relative_to(ROOT).as_posix())
    registry_updated, registry_added = sync_registry()
    print(
        f"updated_text_files={changed} resized_webp={resized} "
        f"registry_updated={registry_updated} registry_added={registry_added}"
    )
    if changed_paths:
        print("updated: " + ", ".join(changed_paths[:20]))


if __name__ == "__main__":
    main()
