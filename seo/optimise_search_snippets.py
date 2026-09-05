#!/usr/bin/env python3
"""Improve search-result titles and snippets without rebuilding the site.

The script is intentionally limited to tracked, indexable HTML. It:
* applies evidence-based overrides to the main RU/EN/KO commercial pages;
* applies query/page overrides to product URLs already ranking around positions 4–10;
* restores complete Article/Product metadata that was previously cut with a literal ellipsis;
* keeps title, Open Graph and Twitter metadata in sync.

Run from anywhere inside the repository. The operation is idempotent.
"""

from __future__ import annotations

import html
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


CORE: dict[str, tuple[str, str, str | None]] = {
    "index.html": (
        "Доставка цветов в Нячанге — букеты от 500 000 ₫",
        "Купить и заказать цветы в Нячанге: розы, букеты и корзины от 500 000 ₫. Бесплатная доставка по городу со следующего дня, заказ онлайн.",
        "Доставка цветов и шаров в Нячанге",
    ),
    "index-en.html": (
        "Flower Delivery Nha Trang — Bouquets from 500,000₫",
        "Order roses and fresh bouquets in Nha Trang from 500,000₫. Free city delivery from the next day; English support via WhatsApp and Instagram.",
        "Flower Delivery in Nha Trang",
    ),
    "index-kr.html": (
        "나트랑 꽃배달·꽃집 — 장미 꽃다발 500,000동부터",
        "나트랑 꽃배달 전문점. 장미·꽃다발·꽃바구니 500,000동부터, 시내 무료 배달. 온라인 주문은 다음 날부터 가능하며 카카오톡으로 상담합니다.",
        "나트랑 꽃배달·꽃집",
    ),
    "catalog-ru.html": (
        "Каталог цветов в Нячанге — цены на букеты и доставку",
        "Каталог цветов и букетов в Нячанге с ценами от 500 000 ₫. Розы, корзины, шары и наборы; бесплатная онлайн-доставка со следующего дня.",
        "Каталог цветов и букетов в Нячанге",
    ),
    "catalog-en.html": (
        "Flower & Bouquet Catalog Nha Trang — Prices & Delivery",
        "Browse flowers and bouquets in Nha Trang with prices from 500,000₫. Roses, baskets, balloons and gifts; free city delivery from the next day.",
        "Flower & Bouquet Catalog in Nha Trang",
    ),
    "catalog-ko.html": (
        "나트랑 꽃배달 카탈로그 — 장미·꽃다발 가격",
        "나트랑 꽃배달 상품과 가격을 한눈에 확인하세요. 장미·꽃다발·꽃바구니 500,000동부터, 시내 무료 배달은 온라인 주문 다음 날부터 가능합니다.",
        "나트랑 꽃배달 카탈로그",
    ),
    "balloons.html": (
        "Гелиевые шары в Нячанге — наборы с доставкой",
        "Заказать гелиевые шары в Нячанге: наборы S, M и L, цифры, сердца и комбо с цветами. Бесплатная доставка по городу со следующего дня.",
        "Гелиевые шары с доставкой в Нячанге",
    ),
    "balloons-en.html": (
        "Helium Balloon Delivery Nha Trang — S, M & L Sets",
        "Order helium balloons in Nha Trang: S, M and L sets, number balloons, hearts and flower combos. Free city delivery from the next day.",
        "Helium Balloon Delivery in Nha Trang",
    ),
    "balloons-kr.html": (
        "나트랑 풍선 배달 — 헬륨풍선 S·M·L 세트",
        "나트랑 헬륨풍선 배달: S·M·L 세트, 숫자·하트 풍선과 꽃 콤보. 시내 무료 배달은 온라인 주문 다음 날부터, 카카오톡으로 상담합니다.",
        "나트랑 헬륨풍선 배달",
    ),
    "torty.html": (
        "Торты на заказ в Нячанге — от 500 000 ₫",
        "Торты на заказ в Нячанге от 500 000 ₫ и пирожные от 100 000 ₫. Доставка со следующего дня только вместе с букетом, шарами или подарочным набором.",
        "Торты на заказ в Нячанге",
    ),
    "torty-en.html": (
        "Cakes in Nha Trang — Order from 500,000₫",
        "Order cakes in Nha Trang from 500,000₫ or pastries from 100,000₫. Next-day delivery only with flowers, balloons or a gift set.",
        "Cakes to Order in Nha Trang",
    ),
    "torty-kr.html": (
        "나트랑 케이크 주문·배달 — 생일 케이크 500,000동부터",
        "나트랑 생일·기념일 케이크 500,000동부터, 디저트 100,000동부터. 실제 사진 확인 후 카카오톡으로 주문하고 꽃다발·풍선과 함께 다음 날 배달합니다. 구글 리뷰 다수.",
        "나트랑 생일 케이크 주문·배달",
    ),
    "nabory.html": (
        "Подарочные наборы в Нячанге — цветы, шары и торт",
        "Подарочные наборы в Нячанге: цветы, гелиевые шары, торт и подарки в одном заказе. Бесплатная онлайн-доставка по городу со следующего дня.",
        None,
    ),
    "nabory-en.html": (
        "Gift Sets in Nha Trang — Flowers, Balloons & Cake",
        "Gift sets in Nha Trang with flowers, helium balloons, cake and gifts in one order. Free online delivery across the city from the next day.",
        None,
    ),
    "nabory-kr.html": (
        "나트랑 선물세트 배달 — 꽃·풍선·케이크",
        "나트랑 선물세트: 꽃다발, 헬륨풍선, 케이크와 선물을 한 번에 주문하세요. 시내 무료 배달은 온라인 주문 다음 날부터 가능합니다.",
        None,
    ),
    "prazdnik.html": (
        "Наборы для праздника в Нячанге — шары, торт и декор",
        "Готовые наборы для праздника в Нячанге: стойки и цифры из шаров, фотозона, торт, посуда и декор. Доставка со следующего дня.",
        None,
    ),
    "prazdnik-en.html": (
        "Party Sets in Nha Trang — Balloons, Cake & Decor",
        "Ready party sets in Nha Trang with balloon stands, number balloons, a photo zone, cake, tableware and decor. Delivery from the next day.",
        None,
    ),
    "prazdnik-kr.html": (
        "나트랑 파티세트 배달 — 생일 풍선·케이크·장식",
        "나트랑 준비된 파티세트: 풍선 스탠드, 숫자 풍선, 포토존, 케이크, 식기와 장식. 온라인 주문 다음 날부터 배달합니다.",
        None,
    ),
    "blog-ru.html": (
        "Статьи о цветах, подарках и Нячанге",
        "Полезные статьи о цветах, подарках, праздниках и жизни во Вьетнаме. Практические советы туристам и доставка букетов по Нячангу.",
        None,
    ),
    "blog-en.html": (
        "Nha Trang Flower, Gift & Vietnam Guides",
        "Practical guides to flowers, gifts, celebrations and life in Vietnam, with local tips for visitors and flower delivery in Nha Trang.",
        None,
    ),
    "blog-ko.html": (
        "나트랑 꽃·선물·베트남 여행 가이드",
        "꽃과 선물, 기념일, 베트남 생활에 관한 실용 가이드. 나트랑 여행 정보와 꽃배달 선택 팁을 한국어로 확인하세요.",
        None,
    ),
}


PRIORITY_PRODUCTS: dict[str, tuple[str, str]] = {
    "catalog/101-roza-v-korzine-ru.html": (
        "101 роза в корзине — 2 000 000 ₫, доставка в Нячанге",
        "Закажите корзину из 101 розы за 2 000 000 ₫. Бесплатная доставка по Нячангу со следующего дня, фото композиции перед отправкой.",
    ),
    "catalog/7-vetok-liliy-ru.html": (
        "7 веток лилий — 600 000 ₫, доставка в Нячанге",
        "Букет из 7 веток лилий за 600 000 ₫. Бесплатная доставка по Нячангу со следующего дня, заказ онлайн или через оператора.",
    ),
    "catalog/nabor-sharov-s-7-sharov-ru.html": (
        "7 гелиевых шаров в Нячанге — набор S за 1 000 000 ₫",
        "Набор S из 7 гелиевых шаров за 1 000 000 ₫. Бесплатная доставка по Нячангу со следующего дня; цвета согласуем перед заказом.",
    ),
    "catalog/25-rozovyh-roz-en.html": (
        "25 Pink Roses in Nha Trang — 500,000₫ Delivery",
        "Order 25 fresh pink roses for 500,000₫. Free Nha Trang delivery from the next day, with a bouquet photo before dispatch and English support.",
    ),
    "catalog/nabor-sharov-s-en.html": (
        "7 Helium Balloons in Nha Trang — Set S, 1,000,000₫",
        "Order a Set S of 7 helium balloons for 1,000,000₫. Free Nha Trang delivery from the next day; choose colours with our English-speaking operator.",
    ),
    "catalog/101-roza-v-korzine-en.html": (
        "101 Roses in a Basket — Nha Trang Delivery, 2,000,000₫",
        "Order 101 roses arranged in a basket for 2,000,000₫. Free Nha Trang delivery from the next day, with a photo before dispatch.",
    ),
    "catalog/nabor-sharov-l-ko.html": (
        "나트랑 풍선 세트 L — 헬륨풍선 2,000,000동",
        "나트랑 헬륨풍선 L 세트 2,000,000동. 시내 무료 배달은 온라인 주문 다음 날부터 가능하며 색상은 카카오톡으로 상담합니다.",
    ),
    "catalog/nabor-sharov-m-cifry-3-shara-ko.html": (
        "나트랑 숫자 풍선 세트 M — 1,500,000동",
        "대형 숫자 2개와 헬륨풍선 3개로 구성한 나트랑 풍선 세트 M, 1,500,000동. 시내 무료 배달, 카카오톡 주문 상담.",
    ),
    "catalog/101-fioletovaya-roza-v-upakovke-ko.html": (
        "나트랑 보라 장미 101송이 — 1,500,000동 꽃배달",
        "보라 장미 101송이 꽃다발 1,500,000동. 나트랑 시내 무료 꽃배달은 온라인 주문 다음 날부터, 카카오톡으로 주문합니다.",
    ),
    "catalog/101-krasnaya-roza-v-upakovke-ko.html": (
        "나트랑 빨간 장미 101송이 — 1,500,000동 꽃배달",
        "화이트 포장 빨간 장미 101송이 1,500,000동. 나트랑 시내 무료 꽃배달은 온라인 주문 다음 날부터, 카카오톡으로 주문합니다.",
    ),
    "catalog/25-rozovyh-roz-ko.html": (
        "나트랑 핑크 장미 25송이 — 500,000동 꽃배달",
        "핑크 장미 25송이 꽃다발 500,000동. 나트랑 시내 무료 꽃배달은 온라인 주문 다음 날부터, 카카오톡으로 주문합니다.",
    ),
}


# Self-consistent visible copy and LocalBusiness data for the four commercial
# landing-page families. Several non-balloon pages were originally copied from
# balloons.html and still described balloons in their header and JSON-LD.
LANDINGS: dict[str, tuple[str, str, str]] = {
    "balloons.html": (
        "Доставка гелиевых шаров в Нячанге: наборы S, M и L, цифры, сердца и комбо с цветами. Онлайн-доставка со следующего дня.",
        "Гелиевые шары<br>с доставкой в Нячанге",
        "Бесплатная доставка по городу. Онлайн-заказы доставляем со следующего дня.",
    ),
    "balloons-en.html": (
        "Helium balloon delivery in Nha Trang: S, M and L sets, number balloons, hearts and flower combos. Online delivery from the next day.",
        "Helium Balloon<br>Delivery in Nha Trang",
        "Free city delivery. Online orders are delivered from the next day.",
    ),
    "balloons-kr.html": (
        "나트랑 헬륨풍선 배달: S·M·L 세트, 숫자·하트 풍선과 꽃 콤보. 온라인 주문은 다음 날부터 배달합니다.",
        "나트랑 헬륨풍선<br>배달 서비스",
        "나트랑 시내 무료 배달. 온라인 주문은 다음 날부터 가능합니다.",
    ),
    "torty.html": (
        "Торты и пирожные с доставкой в Нячанге. Торты заказываются только вместе с букетом, шарами или подарочным набором; доставка со следующего дня.",
        "Торты и пирожные<br>с доставкой в Нячанге",
        "Торты — только вместе с букетом, шарами или подарочным набором. Онлайн-доставка со следующего дня.",
    ),
    "torty-en.html": (
        "Cakes and pastries delivered in Nha Trang. Cakes are available only with flowers, balloons or a gift set; delivery from the next day.",
        "Cakes & Pastries<br>Delivery in Nha Trang",
        "Cakes are delivered only with flowers, balloons or a gift set. Online delivery starts the next day.",
    ),
    "torty-kr.html": (
        "나트랑 생일·기념일 케이크와 디저트 배달. 실제 사진 확인 후 카카오톡으로 주문하고, 꽃다발·풍선·선물세트와 함께 다음 날부터 배달합니다.",
        "나트랑 생일 케이크<br>주문·배달",
        "실제 사진 확인 후 카카오톡 주문. 꽃다발·풍선과 함께 다음 날 배달.",
    ),
    "nabory.html": (
        "Подарочные наборы в Нячанге: цветы, гелиевые шары, торт и подарки в одном заказе. Онлайн-доставка со следующего дня.",
        "Подарочные наборы<br>с доставкой в Нячанге",
        "Бесплатная доставка по городу. Онлайн-заказы доставляем со следующего дня.",
    ),
    "nabory-en.html": (
        "Gift set delivery in Nha Trang with flowers, helium balloons, cake and gifts in one order. Online delivery from the next day.",
        "Gift Set Delivery<br>in Nha Trang",
        "Free city delivery. Online orders are delivered from the next day.",
    ),
    "nabory-kr.html": (
        "나트랑 선물세트 배달: 꽃다발, 헬륨풍선, 케이크와 선물을 한 번에. 온라인 주문은 다음 날부터 배달합니다.",
        "나트랑 선물세트<br>배달 서비스",
        "나트랑 시내 무료 배달. 온라인 주문은 다음 날부터 가능합니다.",
    ),
    "prazdnik.html": (
        "Готовые наборы для праздника в Нячанге: шары, цифры, фотозона, торт, посуда и декор. Онлайн-доставка со следующего дня.",
        "Наборы для праздника<br>с доставкой в Нячанге",
        "Бесплатная доставка по городу. Онлайн-заказы доставляем со следующего дня.",
    ),
    "prazdnik-en.html": (
        "Ready party sets delivered in Nha Trang with balloons, number figures, a photo zone, cake, tableware and decor. Delivery from the next day.",
        "Ready Party Sets<br>Delivery in Nha Trang",
        "Free city delivery. Online orders are delivered from the next day.",
    ),
    "prazdnik-kr.html": (
        "나트랑 파티세트 배달: 풍선, 숫자 장식, 포토존, 케이크, 식기와 데코. 온라인 주문은 다음 날부터 배달합니다.",
        "나트랑 파티세트<br>배달 서비스",
        "나트랑 시내 무료 배달. 온라인 주문은 다음 날부터 가능합니다.",
    ),
}


def tracked_html() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z", "*.html"], cwd=ROOT)
    return [ROOT / item.decode() for item in raw.split(b"\0") if item]


def ld_object(source: str, kind: str) -> dict | None:
    for match in re.finditer(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', source, re.I | re.S):
        try:
            value = json.loads(html.unescape(match.group(1)))
        except (json.JSONDecodeError, TypeError):
            continue
        values = value if isinstance(value, list) else [value]
        for item in values:
            if isinstance(item, dict) and item.get("@type") == kind:
                return item
    return None


def meta_value(source: str, pattern: str) -> str:
    match = re.search(pattern, source, re.I | re.S)
    return html.unescape(match.group(1).strip()) if match else ""


def set_title(source: str, title: str) -> str:
    escaped = html.escape(title, quote=False)
    return re.sub(r"(<title>).*?(</title>)", rf"\g<1>{escaped}\g<2>", source, count=1, flags=re.I | re.S)


def set_meta(source: str, selector: str, value: str, after: str) -> str:
    escaped = html.escape(value, quote=True)
    if selector.startswith("og:"):
        pattern = rf'<meta\b[^>]*property=["\']{re.escape(selector)}["\'][^>]*>'
        tag = f'<meta property="{selector}" content="{escaped}">'
    else:
        pattern = rf'<meta\b[^>]*name=["\']{re.escape(selector)}["\'][^>]*>'
        tag = f'<meta name="{selector}" content="{escaped}">'
    match = re.search(pattern, source, re.I)
    if match:
        return source[: match.start()] + tag + source[match.end() :]
    anchor = re.search(after, source, re.I)
    if not anchor:
        raise RuntimeError(f"Cannot insert {selector}: anchor not found")
    return source[: anchor.end()] + "\n    " + tag + source[anchor.end() :]


def set_snippet(source: str, title: str, description: str) -> str:
    source = set_title(source, title)
    source = set_meta(source, "description", description, r"</title>")
    source = set_meta(source, "og:title", title, r'<meta\b[^>]*name=["\']description["\'][^>]*>')
    source = set_meta(source, "og:description", description, r'<meta\b[^>]*property=["\']og:title["\'][^>]*>')
    source = set_meta(source, "twitter:title", title, r'<meta\b[^>]*name=["\']twitter:card["\'][^>]*>')
    source = set_meta(source, "twitter:description", description, r'<meta\b[^>]*name=["\']twitter:title["\'][^>]*>')
    return source


def set_first_h1(source: str, text: str) -> str:
    escaped = html.escape(text, quote=False)
    return re.sub(
        r"(<h1\b[^>]*>).*?(</h1>)",
        rf"\g<1>\n                    {escaped}\n                \g<2>",
        source,
        count=1,
        flags=re.I | re.S,
    )


def optimise_landing(rel: str, source: str) -> str:
    if rel not in LANDINGS:
        return source
    description, header, hero = LANDINGS[rel]
    canonical = f"https://flowers-nha-trang.online/{rel}"

    def schema_repl(match: re.Match[str]) -> str:
        try:
            data = json.loads(html.unescape(match.group(2)))
        except json.JSONDecodeError:
            return match.group(0)
        if not isinstance(data, dict) or data.get("@type") != "LocalBusiness":
            return match.group(0)
        data["@id"] = canonical
        data["description"] = description
        data["url"] = canonical
        data["image"] = "https://flowers-nha-trang.online/img/site/og-default.webp"
        return match.group(1) + "\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n    " + match.group(3)

    source = re.sub(
        r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
        schema_repl,
        source,
        count=1,
        flags=re.I | re.S,
    )
    source = re.sub(
        r'(<span class="font-medium text-xs leading-tight text-stone-600 tracking-wide">).*?(</span>)',
        rf"\g<1>{header}\g<2>",
        source,
        count=1,
        flags=re.S,
    )
    source = re.sub(
        r'(<span style="font-weight:500;font-size:11px;line-height:1\.2;color:#57534e">).*?(</span>)',
        rf"\g<1>{header}\g<2>",
        source,
        count=1,
        flags=re.S,
    )
    source = re.sub(
        r'(<p class="text-stone-700 text-sm md:text-base mb-2 hero-animate-delay">).*?(</p>)',
        rf"\g<1>{html.escape(hero, quote=False)}\g<2>",
        source,
        count=1,
        flags=re.S,
    )
    if rel.endswith("-kr.html"):
        source = source.replace("냐짱 · 베트남", "나트랑 · 베트남", 1)
    return source


def product_snippet(path: Path, source: str) -> tuple[str, str] | None:
    product = ld_object(source, "Product")
    if not product or not isinstance(product.get("name"), str):
        return None
    name = product["name"].strip()
    offers = product.get("offers") if isinstance(product.get("offers"), dict) else {}
    price = str(offers.get("price", ""))
    formatted = f"{int(price):,}".replace(",", " ") if price.isdigit() else price
    lang = meta_value(source, r'<html\b[^>]*lang=["\']([^"\']+)')
    lowered = name.lower()
    is_cake = path.name.startswith(("tort-", "pirozhn")) or any(word in lowered for word in ("cake", "pastry", "케이크", "디저트", "торт", "пирож"))
    is_balloon_only = (
        any(word in lowered for word in ("balloon", "풍선", "шар"))
        and not any(word in lowered for word in ("rose", "flower", "bouquet", "장미", "꽃", "부케", "роза", "цвет", "букет"))
        and not is_cake
    )
    if lang.startswith("en"):
        title = f"{name} — Nha Trang Delivery"
        description = f"{name}. Price {formatted}₫. Free Nha Trang delivery from the next day; order online or via WhatsApp."
    elif lang.startswith("ko"):
        service = "케이크 배달" if is_cake else "풍선 배달" if is_balloon_only else "꽃배달"
        title = f"{name} — 나트랑 {service}"
        description = f"{name}. 가격 {formatted}동. 나트랑 시내 무료 배달, 온라인 주문은 다음 날부터; 카카오톡 상담."
    else:
        title = f"{name} — доставка в Нячанге"
        description = f"{name}. Цена {formatted} ₫. Бесплатная доставка по Нячангу со следующего дня; заказ онлайн или через оператора."
    return title, description


def fix_korean_balloon_label(path: Path, source: str) -> str:
    """Correct older recovered pure-balloon titles that said flower delivery."""
    if not path.name.endswith("-ko.html"):
        return source
    product = ld_object(source, "Product")
    if not product or not isinstance(product.get("name"), str):
        return source
    lowered = product["name"].lower()
    is_balloon_only = (
        any(word in lowered for word in ("balloon", "풍선", "шар"))
        and not any(word in lowered for word in ("rose", "flower", "bouquet", "장미", "꽃", "부케", "роза", "цвет", "букет"))
        and not any(word in lowered for word in ("cake", "pastry", "케이크", "디저트", "торт", "пирож"))
    )
    if is_balloon_only:
        source = source.replace("— 나트랑 꽃배달", "— 나트랑 풍선 배달")
    return source


def recovered_snippet(path: Path, source: str) -> tuple[str, str] | None:
    title = meta_value(source, r"<title>(.*?)</title>")
    description = meta_value(source, r'<meta\b[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)')
    if not title.endswith("…") and not description.endswith("…"):
        return None
    if path.parent.name == "blog":
        article = ld_object(source, "Article")
        if article and isinstance(article.get("headline"), str) and isinstance(article.get("description"), str):
            return article["headline"].strip(), article["description"].strip()
    if path.parent.name == "catalog":
        return product_snippet(path, source)
    return None


def main() -> None:
    changed: list[str] = []
    unresolved: list[str] = []
    for path in tracked_html():
        if not path.exists():
            continue
        rel = path.relative_to(ROOT).as_posix()
        old = path.read_text(encoding="utf-8")
        new = old
        if rel in CORE:
            title, description, h1 = CORE[rel]
            new = set_snippet(new, title, description)
            if h1:
                new = set_first_h1(new, h1)
        elif rel in PRIORITY_PRODUCTS:
            new = set_snippet(new, *PRIORITY_PRODUCTS[rel])
        else:
            recovered = recovered_snippet(path, new)
            if recovered:
                new = set_snippet(new, *recovered)
            else:
                title = meta_value(new, r"<title>(.*?)</title>")
                description = meta_value(new, r'<meta\b[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)')
                if title.endswith("…") or description.endswith("…"):
                    unresolved.append(rel)
        if path.parent.name == "catalog":
            new = fix_korean_balloon_label(path, new)
        new = optimise_landing(rel, new)
        if new != old:
            path.write_text(new, encoding="utf-8")
            changed.append(rel)
    if unresolved:
        raise RuntimeError("Unresolved truncated metadata: " + ", ".join(unresolved))
    print(f"updated={len(changed)}")
    if changed:
        print("\n".join(changed))


if __name__ == "__main__":
    main()
