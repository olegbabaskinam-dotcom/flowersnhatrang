# -*- coding: utf-8 -*-
"""
Генератор страниц сайта из seo/products.csv.
Создаёт:
  catalog/<slug>-{ru,en,ko}.html   — страницы товаров (галерея 7-8 фото готова)
  catalog-{ru,en,ko}.html          — витрина каталога (все товары)
  blog-{ru,en,ko}.html             — витрина блога (пока пусто)
Шапка/подвал/стили берутся из общего шаблона, совпадают с index.html.
Запуск:  python3 seo/build_site.py
"""
import os, csv, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PRODUCTS = os.path.join(HERE, "products.csv")
CATALOG_DIR = os.path.join(ROOT, "catalog")
os.makedirs(CATALOG_DIR, exist_ok=True)

WA = "https://wa.me/37443529162"
TG = "https://t.me/babaskin_o"
DOMAIN = "https://flowers-nha-trang.online"

HOTELS = [
    "Muong Thanh Luxury", "Sheraton Nha Trang", "InterContinental", "Novotel",
    "Mercure", "Sunrise Nha Trang", "Havana Nha Trang", "Diamond Bay",
    "Liberty Central", "Premier Havana", "Galina Hotel", "Ariyana",
    "Potique Hotel", "Selectum Noa Resort", "Mövenpick", "Radisson Blu",
    "Alma Resort", "Fusion Resort", "The Anam", "Duyen Ha Resort", "Cam Ranh Riviera",
]

# SVG-иконки мессенджеров (как в index.html)
WA_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="1em" height="1em" style="display:inline-block;vertical-align:-.125em"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>'
TG_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="1em" height="1em" style="display:inline-block;vertical-align:-.125em"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>'

# Иконки (FontAwesome-пути, как на сайте)
IC_CHECK = '<svg viewBox="0 0 448 512" fill="currentColor" width="1em" height="1em"><path d="M438.6 105.4c12.5 12.5 12.5 32.8 0 45.3l-256 256c-12.5 12.5-32.8 12.5-45.3 0l-128-128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0L160 338.7 393.4 105.4c12.5-12.5 32.8-12.5 45.3 0z"/></svg>'
IC_TRUCK = '<svg viewBox="0 0 640 512" fill="currentColor" width="1em" height="1em"><path d="M112 0C85.5 0 64 21.5 64 48V96H16c-8.8 0-16 7.2-16 16s7.2 16 16 16H64 272c8.8 0 16 7.2 16 16s-7.2 16-16 16H64 48c-8.8 0-16 7.2-16 16s7.2 16 16 16H64 240c8.8 0 16 7.2 16 16s-7.2 16-16 16H64V416c0 53 43 96 96 96s96-43 96-96H384c0 53 43 96 96 96s96-43 96-96h32c17.7 0 32-14.3 32-32V288 256 237.3c0-17-6.7-33.3-18.7-45.3L512 114.7c-12-12-28.3-18.7-45.3-18.7H416V48c0-26.5-21.5-48-48-48H112zM544 237.3V256H416V160h50.7L544 237.3zM160 368a48 48 0 1 1 0 96 48 48 0 1 1 0-96zm272 48a48 48 0 1 1 96 0 48 48 0 1 1 -96 0z"/></svg>'
IC_CLOCK = '<svg viewBox="0 0 512 512" fill="currentColor" width="1em" height="1em"><path d="M256 0a256 256 0 1 1 0 512A256 256 0 1 1 256 0zM232 120V256c0 8 4 15.5 10.7 20l96 64c11 7.4 25.9 4.4 33.3-6.7s4.4-25.9-6.7-33.3L280 243.2V120c0-13.3-10.7-24-24-24s-24 10.7-24 24z"/></svg>'
IC_CARD = '<svg viewBox="0 0 576 512" fill="currentColor" width="1em" height="1em"><path d="M64 32C28.7 32 0 60.7 0 96v32H576V96c0-35.3-28.7-64-64-64H64zM576 224H0V416c0 35.3 28.7 64 64 64H512c35.3 0 64-28.7 64-64V224zM112 352h64c8.8 0 16 7.2 16 16s-7.2 16-16 16H112c-8.8 0-16-7.2-16-16s7.2-16 16-16z"/></svg>'
IC_HOTEL = '<svg viewBox="0 0 512 512" fill="currentColor" width="1em" height="1em"><path d="M0 64C0 46.3 14.3 32 32 32H480c17.7 0 32 14.3 32 32s-14.3 32-32 32V448c17.7 0 32 14.3 32 32s-14.3 32-32 32H304V464c0-26.5-21.5-48-48-48s-48 21.5-48 48v48H32c-17.7 0-32-14.3-32-32s14.3-32 32-32V96C14.3 96 0 81.7 0 64zm128 80v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V144c0-8.8-7.2-16-16-16H144c-8.8 0-16 7.2-16 16zm160-16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V144c0-8.8-7.2-16-16-16H288zM128 240v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V240c0-8.8-7.2-16-16-16H144c-8.8 0-16 7.2-16 16zm160-16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V240c0-8.8-7.2-16-16-16H288z"/></svg>'
IC_FLOWER = '<svg viewBox="0 0 512 512" fill="currentColor" width="1em" height="1em"><path d="M256 96a64 64 0 1 1 128 0 64 64 0 1 1 -128 0zm0 320a64 64 0 1 1 128 0 64 64 0 1 1 -128 0zM128 256a64 64 0 1 1 0 128 64 64 0 1 1 0-128zm256 0a64 64 0 1 1 0 128 64 64 0 1 1 0-128zM256 224a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/><path d="M192 96a64 64 0 1 1 128 0A64 64 0 1 1 192 96z"/></svg>'
IC_STAR = '<svg viewBox="0 0 576 512" fill="currentColor" width="1em" height="1em"><path d="M316.9 18C311.6 7 300.4 0 288.1 0s-23.4 7-28.8 18L195 150.3 51.4 171.5c-12 1.8-22 10.2-25.7 21.7s-.7 24.2 7.9 32.7L137.8 329 113.2 474.7c-2 12 3 24.2 12.9 31.3s23 8 33.8 2.3l128.3-68.5 128.3 68.5c10.8 5.7 23.9 4.9 33.8-2.3s14.9-19.3 12.9-31.3L438.5 329 542.7 225.9c8.6-8.5 11.7-21.2 7.9-32.7s-13.7-19.9-25.7-21.7L381.2 150.3 316.9 18z"/></svg>'

LANGS = ["ru", "en", "ko"]
# имя файла главной для каждого языка
HOME = {"ru": "index.html", "en": "index-en.html", "ko": "index-kr.html"}
# имя файла страницы шаров для каждого языка (ru = balloons.html)
BALLOONS = {"ru": "balloons.html", "en": "balloons-en.html", "ko": "balloons-kr.html"}
HREFLANG = {"ru": "ru", "en": "en", "ko": "ko"}
HTML_LANG = {"ru": "ru", "en": "en", "ko": "ko"}

# Подписи интерфейса
T = {
    "ru": {
        "site_sub": "Доставка цветов и<br>гелиевых шаров в Нячанге",
        "nav_home": "Главная", "nav_catalog": "Каталог", "nav_articles": "Статьи", "nav_balloons": "🎈 Шары",
        "catalog_h1": "Каталог букетов",
        "catalog_sub": "Свежие букеты и гелиевые шары с доставкой по Нячангу день в день.",
        "order_wa": "заказать в WhatsApp", "order_tg": "заказать в Telegram",
        "composition": "Описание", "delivery": "Доставка и оплата",
        "related": "Похожие букеты", "faq": "Частые вопросы",
        "back": "← весь каталог", "details": "подробнее",
        "blog_h1": "Статьи", "blog_sub": "Полезные статьи о цветах, поводах и традициях Вьетнама.",
        "blog_soon": "Скоро здесь появятся статьи. Загляните позже 🌸",
        "del_text": "Бесплатная доставка по Нячангу. День в день при заказе до 18:00. Камрань — доставка от 51 розы (600 000 донгов оплачивается отдельно). Оплата: донги, рубли, доллары, USDT, наличные.",
        "hotel_text": "Доставим букет прямо в номер — {hotel} и другие отели Нячанга и Камрани.",
        "faq_q1": "Можно ли доставить букет в отель?",
        "faq_a1": "Да, доставляем прямо в номер или на ресепшн отелей Нячанга и Камрани, включая {hotel}.",
        "faq_q2": "Доставите день в день?",
        "faq_a2": "Да, при заказе до 18:00 доставим в тот же день. По Нячангу доставка бесплатная.",
        "faq_q3": "Как оплатить?",
        "faq_a3": "Принимаем донги, рубли, доллары, USDT и наличные. Напишите в WhatsApp или Telegram — подскажем удобный способ.",
    },
    "en": {
        "site_sub": "Flower & balloon delivery<br>in Nha Trang",
        "nav_home": "Home", "nav_catalog": "Catalog", "nav_articles": "Articles", "nav_balloons": "🎈 Balloons",
        "catalog_h1": "Bouquet catalog",
        "catalog_sub": "Fresh bouquets and helium balloons with same-day delivery in Nha Trang.",
        "order_wa": "order on WhatsApp", "order_tg": "order on Telegram",
        "composition": "Description", "delivery": "Delivery & payment",
        "related": "Similar bouquets", "faq": "FAQ",
        "back": "← back to catalog", "details": "details",
        "blog_h1": "Articles", "blog_sub": "Helpful articles about flowers, occasions and Vietnamese traditions.",
        "blog_soon": "Articles are coming soon. Check back later 🌸",
        "del_text": "Free delivery across Nha Trang. Same-day delivery for orders before 6 PM. Cam Ranh — delivery from 51 roses (600,000 VND charged separately). Payment: VND, USD, RUB, USDT, cash.",
        "hotel_text": "We deliver straight to your room — {hotel} and other hotels in Nha Trang and Cam Ranh.",
        "faq_q1": "Can you deliver to a hotel?",
        "faq_a1": "Yes, we deliver directly to the room or front desk of Nha Trang and Cam Ranh hotels, including {hotel}.",
        "faq_q2": "Do you offer same-day delivery?",
        "faq_a2": "Yes, order before 6 PM and we deliver the same day. Delivery within Nha Trang is free.",
        "faq_q3": "How can I pay?",
        "faq_a3": "We accept VND, USD, RUB, USDT and cash. Message us on WhatsApp or Telegram and we'll suggest the easiest option.",
    },
    "ko": {
        "site_sub": "나트랑 꽃 & 풍선<br>배달 서비스",
        "nav_home": "홈", "nav_catalog": "카탈로그", "nav_articles": "블로그", "nav_balloons": "🎈 풍선",
        "catalog_h1": "꽃다발 카탈로그",
        "catalog_sub": "나트랑 당일 배달, 신선한 꽃다발과 헬륨 풍선.",
        "order_wa": "WhatsApp으로 주문", "order_tg": "Telegram으로 주문",
        "composition": "상품 설명", "delivery": "배송 및 결제",
        "related": "비슷한 꽃다발", "faq": "자주 묻는 질문",
        "back": "← 카탈로그로", "details": "자세히",
        "blog_h1": "블로그", "blog_sub": "꽃, 기념일, 베트남 문화에 대한 유용한 글.",
        "blog_soon": "곧 블로그 글이 올라옵니다. 다시 방문해 주세요 🌸",
        "del_text": "나트랑 시내 무료 배송. 오후 6시 이전 주문 시 당일 배송. 깜라인 — 51송이부터 배송(60만 동 별도). 결제: 동, 달러, 루블, USDT, 현금.",
        "hotel_text": "객실로 직접 배달해 드립니다 — {hotel} 및 나트랑·깜라인의 호텔.",
        "faq_q1": "호텔로 배달 가능한가요?",
        "faq_a1": "네, {hotel}을 포함한 나트랑·깜라인 호텔의 객실 또는 프런트로 직접 배달합니다.",
        "faq_q2": "당일 배송 되나요?",
        "faq_a2": "네, 오후 6시 이전에 주문하시면 당일 배송됩니다. 나트랑 시내 배송은 무료입니다.",
        "faq_q3": "결제는 어떻게 하나요?",
        "faq_a3": "동, 달러, 루블, USDT, 현금을 받습니다. WhatsApp 또는 Telegram으로 문의해 주세요.",
    },
}

UI = {
    "ru": {"b_fresh": "свежие цветы", "b_day": "день в день",
           "chip_free": "бесплатно по Нячангу", "chip_day": "доставка день в день", "chip_pay": "оплата картой/нал.",
           "f1t": "Свежесть", "f1d": "Срезаем и собираем букет в день доставки",
           "f2t": "День в день", "f2d": "Доставим до 18:00 в день заказа",
           "f3t": "В отель и на виллу", "f3d": "Привезём прямо в номер по Нячангу и Камрани",
           "dl_free": "Бесплатная доставка по всему Нячангу",
           "dl_day": "Доставка в тот же день при заказе до 18:00",
           "dl_cam": "Камрань — доставка от 51 розы (600 000 донгов отдельно)",
           "dl_pay": "Оплата: донги, рубли, доллары, USDT, наличные",
           "st1": "букетов доставлено", "st2": "отзыва на Google", "st3": "оплата при получении",
           "rev_h": "отзывы на Google", "rev_cta": "читать отзывы на Google Maps"},
    "en": {"b_fresh": "fresh flowers", "b_day": "same-day",
           "chip_free": "free in Nha Trang", "chip_day": "same-day delivery", "chip_pay": "card / cash",
           "f1t": "Freshness", "f1d": "Cut and arranged on the delivery day",
           "f2t": "Same day", "f2d": "Delivered by 6 PM on your order day",
           "f3t": "To hotel & villa", "f3d": "Straight to your room in Nha Trang & Cam Ranh",
           "dl_free": "Free delivery across Nha Trang",
           "dl_day": "Same-day delivery for orders before 6 PM",
           "dl_cam": "Cam Ranh — delivery from 51 roses (600,000 VND separately)",
           "dl_pay": "Payment: VND, USD, RUB, USDT, cash",
           "st1": "bouquets delivered", "st2": "Google reviews", "st3": "pay on delivery",
           "rev_h": "Google reviews", "rev_cta": "read reviews on Google Maps"},
    "ko": {"b_fresh": "신선한 꽃", "b_day": "당일 배송",
           "chip_free": "나트랑 무료 배송", "chip_day": "당일 배송", "chip_pay": "카드 / 현금",
           "f1t": "신선함", "f1d": "배송 당일에 꽃을 손질하고 제작합니다",
           "f2t": "당일 배송", "f2d": "주문 당일 오후 6시 이전 배송",
           "f3t": "호텔·빌라 배송", "f3d": "나트랑·깜라인 객실로 직접 배달",
           "dl_free": "나트랑 전역 무료 배송",
           "dl_day": "오후 6시 이전 주문 시 당일 배송",
           "dl_cam": "깜라인 — 51송이부터 배송(60만 동 별도)",
           "dl_pay": "결제: 동, 달러, 루블, USDT, 현금",
           "st1": "꽃다발 배달 완료", "st2": "Google 리뷰", "st3": "수령 시 결제",
           "rev_h": "Google 리뷰", "rev_cta": "Google 지도에서 리뷰 보기"},
}

def price_num(price):
    digits = re.sub(r"[^\d]", "", price)
    return digits or "0"

# валюта «донгов» (только в RU-данных products.csv) → корректная для языка
CUR = {"ru": "донгов", "en": "VND", "ko": "동"}
def price_loc(price, lang):
    return price.replace("донгов", CUR[lang])

def head(lang, title, desc, canonical, alts, base, og_image):
    links = [f'<link rel="canonical" href="{canonical}">']
    for l in LANGS:
        links.append(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{alts[l]}">')
    links.append(f'<link rel="alternate" hreflang="x-default" href="{alts["ru"]}">')
    links_str = "\n    ".join(links)
    return f'''<!DOCTYPE html>
<html lang="{HTML_LANG[lang]}" class="scroll-smooth">
<head><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <meta name="description" content="{html.escape(desc)}">
    <meta property="og:title" content="{html.escape(title)}">
    <meta property="og:description" content="{html.escape(desc)}">
    <meta property="og:type" content="website">
    <meta property="og:image" content="{DOMAIN}/{og_image}">
    {links_str}
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-NNYC00Y4EB"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', 'G-NNYC00Y4EB');
        gtag('config', 'AW-18183091777');
    </script>
    <link rel="stylesheet" href="{base}styles.css">
    <style>
        :root {{ --rose: #c0687a; --rose-light: #fce8ee; --rose-hover: #a8566a; }}
        body {{ font-family: 'Montserrat', sans-serif; background-color: #ffffff; color: #1a1a1a; }}
        h1, h2, h3, .font-serif {{ font-family: 'Playfair Display', serif; }}
        .reveal {{ opacity: 0; transform: translateY(24px); transition: opacity 0.6s ease, transform 0.6s ease; }}
        .reveal.visible {{ opacity: 1; transform: translateY(0); }}
        .card-img-wrap {{ overflow: hidden; }}
        .card-img-wrap img {{ transition: transform 0.45s ease; }}
        .card-img-wrap:hover img {{ transform: scale(1.04); }}
        .product-card {{ border: 1px solid #f0e0e5; transition: border-color 0.25s ease, box-shadow 0.25s ease; }}
        .product-card:hover {{ border-color: var(--rose); box-shadow: 0 4px 24px rgba(192, 104, 122, 0.1); }}
        .btn-rose {{ border: 1.5px solid var(--rose); color: var(--rose); background: transparent; transition: background 0.22s ease, color 0.22s ease, transform 0.15s ease; }}
        .btn-rose:hover {{ background: var(--rose); color: #ffffff; transform: translateY(-1px); }}
        .btn-rose:active {{ transform: scale(0.97); }}
        .btn-rose-filled {{ background: var(--rose); color:#fff; border:1.5px solid var(--rose); transition: background .22s ease, transform .15s ease; }}
        .btn-rose-filled:hover {{ background: var(--rose-hover); transform: translateY(-1px); }}
        .gallery-thumb {{ cursor:pointer; opacity:.6; transition:opacity .2s ease, border-color .2s ease; border:2px solid transparent; }}
        .gallery-thumb.active, .gallery-thumb:hover {{ opacity:1; border-color: var(--rose); }}
        /* утилиты, которых нет в purged styles.css */
        .max-w-3xl {{ max-width: 48rem; }}
        .max-w-xl {{ max-width: 36rem; }}
        .px-6 {{ padding-left: 1.5rem; padding-right: 1.5rem; }}
        .pt-12 {{ padding-top: 3rem; }}
        .pb-2 {{ padding-bottom: .5rem; }}
        .pb-16 {{ padding-bottom: 4rem; }}
        .pb-24 {{ padding-bottom: 6rem; }}
        .p-12 {{ padding: 3rem; }}
        .mt-5 {{ margin-top: 1.25rem; }}
        .gap-10 {{ gap: 2.5rem; }}
        .items-start {{ align-items: flex-start; }}
        .leading-relaxed {{ line-height: 1.625; }}
        .inline-block {{ display: inline-block; }}
        .w-auto {{ width: auto; }}
        .space-y-3 > * + * {{ margin-top: .75rem; }}
        .gallery-main-img {{ max-height: 360px; width: auto; max-width: 100%; }}
        @media (min-width: 768px) {{
            .md\\:grid-cols-2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        }}
        /* красивые компоненты страницы товара */
        .badge {{ display:inline-flex; align-items:center; gap:.4rem; background:var(--rose-light); color:var(--rose-hover); font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; padding:.4rem .85rem; border-radius:999px; }}
        .price-box {{ background:#fdf4f7; border:1px solid #f0d0d8; border-radius:1rem; padding:1.25rem 1.5rem; }}
        .chip {{ display:inline-flex; align-items:center; gap:.45rem; background:#fff; border:1px solid #f0e0e5; border-radius:999px; padding:.5rem .9rem; font-size:.76rem; color:#6b6b6b; font-weight:500; }}
        .chip svg {{ color:var(--rose); }}
        .icon-badge {{ width:2.9rem; height:2.9rem; border-radius:.9rem; background:var(--rose-light); color:var(--rose); display:flex; align-items:center; justify-content:center; font-size:1.15rem; flex:0 0 auto; }}
        .sec-card {{ background:#fff; border:1px solid #f0e0e5; border-radius:1.25rem; padding:1.75rem; }}
        .feature {{ background:#fff; border:1px solid #f0e0e5; border-radius:1rem; padding:1.4rem 1rem; text-align:center; transition:border-color .2s ease, box-shadow .2s ease; }}
        .feature:hover {{ border-color:var(--rose); box-shadow:0 4px 20px rgba(192,104,122,.08); }}
        .faq-item {{ background:#fff; border:1px solid #f0e0e5; border-radius:1rem; padding:1.1rem 1.3rem; transition:border-color .2s ease, box-shadow .2s ease; }}
        .faq-item:hover {{ border-color:var(--rose); box-shadow:0 4px 20px rgba(192,104,122,.08); }}
        .check-li {{ display:flex; gap:.6rem; align-items:flex-start; color:#6b6b6b; font-size:.9rem; line-height:1.55; }}
        .check-li svg {{ color:var(--rose); flex:0 0 auto; margin-top:.2rem; }}
        .accent-bar {{ border-left:3px solid var(--rose); padding-left:1rem; }}
    </style>
</head>
<body class="antialiased flex flex-col min-h-screen">
'''

def header(lang, base, lang_urls=None):
    t = T[lang]
    # куда ведут переключатели языка (по умолчанию — главная этого языка).
    # для страниц товара/каталога/блога передаётся эквивалент той же страницы.
    if lang_urls is None:
        lang_urls = {l: f"{base}{HOME[l]}" for l in LANGS}
    def navlink(l, label, code):
        if l == lang:
            return f'<span class="px-3 py-1.5 rounded-lg text-white text-xs font-medium" style="background:#c0687a;">{label}</span>'
        return f'<a href="{lang_urls[l]}" class="px-3 py-1.5 rounded-lg text-stone-500 hover:text-[#c0687a] hover:bg-stone-50 transition">{label}</a>'
    flags = {"ru": "🇷🇺 RU", "en": "🇬🇧 EN", "ko": "🇰🇷 KR"}
    nav_langs = "\n                ".join(navlink(l, flags[l], l) for l in LANGS)
    nav_langs_m = "\n            ".join(
        (f'<span class="px-3 py-1.5 rounded-lg text-white whitespace-nowrap" style="background:#c0687a;">{flags[l]}</span>'
         if l == lang else
         f'<a href="{lang_urls[l]}" class="px-3 py-1.5 rounded-lg text-stone-500 whitespace-nowrap hover:text-[#c0687a] transition">{flags[l]}</a>')
        for l in LANGS)
    return f'''    <div style="background:#fce8ee; color:#a8566a;" class="text-xs py-2 text-center tracking-widest font-medium uppercase">
        NhaTrang Flowers
    </div>
    <header class="bg-white/90 backdrop-blur-md sticky top-0 z-50 border-b border-stone-100">
        <div class="max-w-5xl mx-auto px-4 py-3 flex justify-between items-center">
            <a href="{base}{HOME[lang]}" class="flex items-center gap-3">
                <img src="{base}img/dqRu8.webp" alt="NhaTrang Flowers" class="h-12 w-12 rounded-xl object-cover">
                <span class="font-medium text-xs leading-tight text-stone-600 tracking-wide">{t["site_sub"]}</span>
            </a>
            <nav class="hidden md:flex items-center gap-1 text-xs font-medium">
                <a href="{base}{HOME[lang]}" class="px-3 py-1.5 rounded-lg text-stone-500 hover:text-[#c0687a] hover:bg-stone-50 transition">{t["nav_home"]}</a>
                <a href="{base}catalog-{lang}.html" class="px-3 py-1.5 rounded-lg text-stone-500 hover:text-[#c0687a] hover:bg-stone-50 transition">{t["nav_catalog"]}</a>
                <a href="{base}blog-{lang}.html" class="px-3 py-1.5 rounded-lg text-stone-500 hover:text-[#c0687a] hover:bg-stone-50 transition">{t["nav_articles"]}</a>
                <a href="{base}{BALLOONS[lang]}" class="px-3 py-1.5 rounded-lg text-stone-500 hover:text-[#c0687a] hover:bg-stone-50 transition">{t["nav_balloons"]}</a>
                <span class="w-px h-4 bg-stone-200 mx-1"></span>
                {nav_langs}
            </nav>
            <div class="flex gap-4 text-xl">
                <a href="{WA}" target="_blank" class="text-stone-400 hover:text-[#c0687a] transition" aria-label="WhatsApp">{WA_SVG}</a>
                <a href="{TG}" target="_blank" class="text-stone-400 hover:text-[#c0687a] transition" aria-label="Telegram">{TG_SVG}</a>
            </div>
        </div>
        <div class="md:hidden border-t border-stone-100 px-4 py-2 flex gap-1 text-xs font-medium overflow-x-auto justify-center">
            <a href="{base}{HOME[lang]}" class="px-3 py-1.5 rounded-lg text-stone-500 whitespace-nowrap hover:text-[#c0687a] transition">{t["nav_home"]}</a>
            <a href="{base}catalog-{lang}.html" class="px-3 py-1.5 rounded-lg text-stone-500 whitespace-nowrap hover:text-[#c0687a] transition">{t["nav_catalog"]}</a>
            <a href="{base}blog-{lang}.html" class="px-3 py-1.5 rounded-lg text-stone-500 whitespace-nowrap hover:text-[#c0687a] transition">{t["nav_articles"]}</a>
            <a href="{base}{BALLOONS[lang]}" class="px-3 py-1.5 rounded-lg text-stone-500 whitespace-nowrap hover:text-[#c0687a] transition">{t["nav_balloons"]}</a>
            <span class="w-px h-4 bg-stone-200 mx-1"></span>
            {nav_langs_m}
        </div>
    </header>
'''

def footer(base):
    return f'''    <footer class="py-12 px-4 mt-auto" style="background:#fce8ee;">
        <div class="max-w-5xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
            <div class="text-center md:text-left">
                <div class="font-serif font-bold text-2xl mb-1" style="color:#1a1a1a;">NhaTrang Flowers</div>
                <div class="text-xs font-medium tracking-widest uppercase" style="color:#a8566a;">Качество · Ответственность · Пунктуальность</div>
            </div>
            <div class="flex gap-6 text-2xl">
                <a href="{WA}" target="_blank" style="color:#c0a0a8;" class="hover:text-[#c0687a] transition" aria-label="WhatsApp">{WA_SVG}</a>
                <a href="{TG}" target="_blank" style="color:#c0a0a8;" class="hover:text-[#c0687a] transition" aria-label="Telegram">{TG_SVG}</a>
            </div>
        </div>
        <div class="text-center text-xs mt-10 pt-6" style="border-top: 1px solid #f0d0d8; color:#b08090;">
            &copy; 2026 NhaTrang Flowers.
        </div>
    </footer>
'''

SCRIPTS = '''<script>
document.querySelectorAll('a[href*="wa.me"], a[href*="t.me"]').forEach(function(el) {
    el.addEventListener('click', function() {
        gtag('event', 'conversion', {'send_to': 'AW-18183091777/YJxbCLWUtbIcEMHsr95D','value': 1.0,'currency': 'VND'});
    });
});
</script>
<script>
(function(){
    var els = document.querySelectorAll('.reveal');
    var io = new IntersectionObserver(function(entries){
        entries.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('visible'); io.unobserve(e.target); } });
    }, { threshold: 0.1 });
    els.forEach(function(el){ io.observe(el); });
})();
</script>
<script>
(function(){
    var thumbs = document.querySelectorAll('.gallery-thumb');
    var main = document.getElementById('gallery-main');
    if(!main) return;
    thumbs.forEach(function(t){
        t.addEventListener('click', function(){
            main.src = t.dataset.full;
            thumbs.forEach(function(x){ x.classList.remove('active'); });
            t.classList.add('active');
        });
    });
})();
</script>
</body>
</html>
'''

def order_buttons(name, t, size="full"):
    msg = name.replace(" ", "%20")
    return f'''<div class="flex flex-col gap-2">
                    <a href="{WA}?text={msg}" target="_blank" class="btn-rose flex items-center justify-center gap-2 font-medium py-2.5 px-4 rounded-xl text-xs w-full">{WA_SVG} {t["order_wa"]}</a>
                    <a href="{TG}?text={msg}" target="_blank" class="btn-rose flex items-center justify-center gap-2 font-medium py-2.5 px-4 rounded-xl text-xs w-full">{TG_SVG} {t["order_tg"]}</a>
                </div>'''

def product_card(p, lang, base, t):
    name = p[f"name_{lang}"]
    desc = p[f"desc_{lang}"]
    alt = p[f"alt_{lang}"]
    url = f"{base}catalog/{p['slug']}-{lang}.html"
    return f'''<a href="{url}" class="reveal product-card bg-white rounded-2xl overflow-hidden flex flex-col group">
                <div class="card-img-wrap">
                    <img src="{base}{p['img']}" alt="{html.escape(alt)}" loading="lazy" class="w-full h-64 object-cover">
                </div>
                <div class="p-5 flex flex-col flex-grow">
                    <h3 class="font-serif text-xl font-bold mb-1" style="color:#1a1a1a;">{html.escape(name)}</h3>
                    <p class="text-stone-600 text-xs mb-3 flex-grow">{html.escape(desc)}</p>
                    <p class="font-bold text-base mb-0.5" style="color:#1a1a1a;">{html.escape(price_loc(p['price'], lang))}</p>
                    <p class="text-stone-500 text-xs mb-4">{html.escape(p['price_sub'])}</p>
                    <span class="btn-rose-filled text-center font-medium py-2.5 px-4 rounded-xl text-xs w-full">{t["details"]} →</span>
                </div>
            </a>'''

def gallery(p, base, alt):
    # Галерея на 7-8 фото: сейчас 1 фото, доп. ищутся как <slug>-2.webp ... -8.webp
    imgs = [p["img"]]
    for n in range(2, 9):
        cand = os.path.join(ROOT, "img", f"{p['slug']}-{n}.webp")
        if os.path.exists(cand):
            imgs.append(f"img/{p['slug']}-{n}.webp")
    main = imgs[0]
    thumbs = ""
    if len(imgs) > 1:
        cells = "\n            ".join(
            f'<img src="{base}{im}" data-full="{base}{im}" alt="{html.escape(alt)} {i+1}" class="gallery-thumb w-20 h-20 object-cover rounded-lg{" active" if i==0 else ""}">'
            for i, im in enumerate(imgs))
        thumbs = f'<div class="flex gap-2 mt-3 flex-wrap">\n            {cells}\n        </div>'
    return f'''<div class="rounded-2xl overflow-hidden border border-stone-100 flex items-center justify-center p-3" style="background:#fdf4f7;">
            <img id="gallery-main" src="{base}{main}" alt="{html.escape(alt)}" class="gallery-main-img object-contain rounded-xl">
        </div>
        {thumbs}'''

def render_product(p, lang, products):
    t = T[lang]
    base = "../"
    name = p[f"name_{lang}"]
    desc = p[f"desc_{lang}"]
    alt = p[f"alt_{lang}"]
    hotel = HOTELS[int(p["id"]) % len(HOTELS)]
    slug = p["slug"]
    canonical = f"{DOMAIN}/catalog/{slug}-{lang}.html"
    alts = {l: f"{DOMAIN}/catalog/{slug}-{l}.html" for l in LANGS}
    if lang == "ru":
        title = f"{name} — доставка в Нячанге | NhaTrang Flowers"
        meta = f"{name} с доставкой по Нячангу день в день. {desc}. Цена {p['price']}. Заказ в WhatsApp и Telegram."
    elif lang == "en":
        title = f"{name} — delivery in Nha Trang | NhaTrang Flowers"
        meta = f"{name} with same-day delivery in Nha Trang. {desc}. Price {price_loc(p['price'], lang)}. Order via WhatsApp or Telegram."
    else:
        title = f"{name} — 나트랑 배달 | NhaTrang Flowers"
        meta = f"{name} 나트랑 당일 배달. {desc}. 가격 {price_loc(p['price'], lang)}. WhatsApp·Telegram 주문."
    meta = meta[:300]

    # похожие — 3 следующих по кругу
    idx = products.index(p)
    related = [products[(idx + k) % len(products)] for k in range(1, 4)]
    rel_cards = "\n            ".join(product_card(r, lang, base, t) for r in related)

    hotel_text = t["hotel_text"].format(hotel=hotel)
    faq = [(t["faq_q1"], t["faq_a1"].format(hotel=hotel)),
           (t["faq_q2"], t["faq_a2"]),
           (t["faq_q3"], t["faq_a3"])]
    faq_html = "\n            ".join(
        f'<div class="faq-item reveal"><h3 class="font-bold text-sm mb-2 flex items-start gap-2" style="color:#1a1a1a;"><span style="color:var(--rose);">Q</span> {html.escape(q)}</h3><p class="text-stone-600 text-sm leading-relaxed">{html.escape(a)}</p></div>'
        for q, a in faq)
    faq_schema = ",".join(
        '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
        % (jstr(q), jstr(a)) for q, a in faq)

    schema = (
        '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Product",'
        '"name":%s,"image":%s,"description":%s,'
        '"brand":{"@type":"Brand","name":"NhaTrang Flowers"},'
        '"offers":{"@type":"Offer","price":"%s","priceCurrency":"VND","availability":"https://schema.org/InStock","url":%s}}</script>'
        % (jstr(name), jstr(f"{DOMAIN}/{p['img']}"), jstr(desc), price_num(p["price"]), jstr(canonical))
    )
    faqschema = '<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}</script>' % faq_schema

    u = UI[lang]
    body = f'''    <main class="flex-grow">
    <nav class="max-w-5xl mx-auto px-6 pt-8 pb-2 text-xs text-stone-400">
        <a href="{base}catalog-{lang}.html" class="hover:text-[#c0687a]">{t["nav_catalog"]}</a> / <span style="color:#1a1a1a;">{html.escape(name)}</span>
    </nav>
    <section class="max-w-5xl mx-auto px-6 py-8 grid md:grid-cols-2 gap-10 items-start">
        <div class="reveal">
        {gallery(p, base, alt)}
        </div>
        <div class="reveal flex flex-col">
            <div class="flex gap-2 mb-4">
                <span class="badge">{IC_FLOWER} {u["b_fresh"]}</span>
                <span class="badge">{IC_CLOCK} {u["b_day"]}</span>
            </div>
            <h1 class="font-serif text-3xl md:text-4xl font-bold mb-4 leading-tight" style="color:#1a1a1a;">{html.escape(name)}</h1>
            <p class="text-stone-600 mb-6 leading-relaxed">{html.escape(desc)}.</p>
            <div class="price-box mb-6">
                <p class="font-bold text-3xl mb-1" style="color:#1a1a1a;">{html.escape(price_loc(p['price'], lang))}</p>
                <p class="text-stone-500 text-sm">{html.escape(p['price_sub'])}</p>
            </div>
            {order_buttons(name, t)}
            <div class="flex flex-wrap gap-2 mt-5">
                <span class="chip">{IC_TRUCK} {u["chip_free"]}</span>
                <span class="chip">{IC_CLOCK} {u["chip_day"]}</span>
                <span class="chip">{IC_CARD} {u["chip_pay"]}</span>
            </div>
        </div>
    </section>
    {trust_bar(lang, base)}

    <section class="max-w-5xl mx-auto px-6 py-6">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="feature reveal"><div class="icon-badge mx-auto mb-3">{IC_FLOWER}</div><h3 class="font-bold text-sm mb-1" style="color:#1a1a1a;">{u["f1t"]}</h3><p class="text-stone-500 text-xs leading-relaxed">{u["f1d"]}</p></div>
            <div class="feature reveal"><div class="icon-badge mx-auto mb-3">{IC_CLOCK}</div><h3 class="font-bold text-sm mb-1" style="color:#1a1a1a;">{u["f2t"]}</h3><p class="text-stone-500 text-xs leading-relaxed">{u["f2d"]}</p></div>
            <div class="feature reveal"><div class="icon-badge mx-auto mb-3">{IC_HOTEL}</div><h3 class="font-bold text-sm mb-1" style="color:#1a1a1a;">{u["f3t"]}</h3><p class="text-stone-500 text-xs leading-relaxed">{u["f3d"]}</p></div>
        </div>
    </section>

    <section class="max-w-3xl mx-auto px-6 py-8">
        <div class="sec-card reveal mb-6">
            <div class="flex items-center gap-3 mb-4">
                <div class="icon-badge">{IC_FLOWER}</div>
                <h2 class="font-serif text-2xl font-bold" style="color:#1a1a1a;">{t["composition"]}</h2>
            </div>
            <p class="text-stone-600 leading-relaxed accent-bar">{html.escape(name)} — {html.escape(desc)}. {html.escape(hotel_text)}</p>
        </div>
        <div class="sec-card reveal">
            <div class="flex items-center gap-3 mb-4">
                <div class="icon-badge">{IC_TRUCK}</div>
                <h2 class="font-serif text-2xl font-bold" style="color:#1a1a1a;">{t["delivery"]}</h2>
            </div>
            <ul class="space-y-3">
                <li class="check-li">{IC_CHECK}<span>{u["dl_free"]}</span></li>
                <li class="check-li">{IC_CHECK}<span>{u["dl_day"]}</span></li>
                <li class="check-li">{IC_CHECK}<span>{u["dl_cam"]}</span></li>
                <li class="check-li">{IC_CARD}<span>{u["dl_pay"]}</span></li>
            </ul>
        </div>
    </section>

    <section class="max-w-3xl mx-auto px-6 py-8">
        <h2 class="font-serif text-2xl font-bold mb-6 text-center" style="color:#1a1a1a;">{t["faq"]}</h2>
        <div class="space-y-3">
            {faq_html}
        </div>
    </section>

    {reviews_block(lang, base)}

    <section class="max-w-5xl mx-auto px-6 py-12">
        <h2 class="font-serif text-2xl font-bold mb-8 text-center" style="color:#1a1a1a;">{t["related"]}</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            {rel_cards}
        </div>
        <div class="text-center mt-10">
            <a href="{base}catalog-{lang}.html" class="btn-rose inline-block font-medium py-2.5 px-6 rounded-xl text-sm">{t["back"]}</a>
        </div>
    </section>
    </main>
'''
    lang_urls = {l: f"{p['slug']}-{l}.html" for l in LANGS}
    return (head(lang, title, meta, canonical, alts, base, p["img"])
            + schema + faqschema + header(lang, base, lang_urls) + body + footer(base) + SCRIPTS)

def jstr(s):
    import json
    return json.dumps(s, ensure_ascii=False)

ARTICLES_BANNER_IMG = "img/photo-1615182787503-08365d1e7fae.avif"
ARTICLES_KICKER = {"ru": "читайте", "en": "read", "ko": "읽어보기"}
ARTICLES_CTA = {"ru": "смотреть статьи →", "en": "view articles →", "ko": "블로그 보기 →"}

def articles_block(lang, base):
    """Сквозной блок 'Статьи' — баннер с фото в стиле блока «Гелиевые шары»."""
    t = T[lang]
    return f'''
    <!-- Сквозной блок: Статьи -->
    <section class="reveal py-10 px-4 max-w-5xl mx-auto w-full">
        <a href="{base}blog-{lang}.html" class="block rounded-3xl overflow-hidden relative group" style="height: 340px;">
            <img src="{base}{ARTICLES_BANNER_IMG}" alt="{t["blog_h1"]}" class="w-full h-full object-cover transition-transform duration-700 ease-in-out group-hover:scale-105">
            <div class="absolute inset-0 transition-opacity duration-500" style="background: linear-gradient(to right, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.15) 100%);"></div>
            <div class="absolute inset-0 flex flex-col justify-center px-10 md:px-14">
                <p class="text-xs tracking-widest uppercase mb-3 font-medium" style="color:#fce8ee; opacity:0.85;">{ARTICLES_KICKER[lang]}</p>
                <h2 class="font-serif text-4xl md:text-5xl font-medium italic text-white mb-4 leading-tight">{t["blog_h1"]}</h2>
                <p class="text-white/80 text-sm mb-6 max-w-xs">{t["blog_sub"]}</p>
                <span class="inline-flex items-center gap-2 text-sm font-medium text-white border border-white/50 rounded-xl px-5 py-2.5 self-start transition-all duration-300 group-hover:bg-white group-hover:text-stone-800">{ARTICLES_CTA[lang]}</span>
            </div>
        </a>
    </section>
'''

GMAPS = "https://maps.app.goo.gl/3H4ngJ1UoLrMDkiS7?g_st=ic"
REVIEW_IMGS = ["img/dqj8G.webp", "img/dqj8P.webp", "img/dqj8o.webp"]

def trust_bar(lang, base):
    """Полоса доверия: 500+ доставлено · 5.0 / отзывы Google · оплата при получении."""
    u = UI[lang]
    return f'''
    <section class="reveal py-8 px-4 border-b border-stone-100">
        <div class="max-w-4xl mx-auto">
            <div class="grid grid-cols-3 divide-x divide-stone-100">
                <div class="flex flex-col items-center px-4 py-2 text-center">
                    <div class="text-2xl md:text-3xl font-bold" style="color:#1a1a1a;">500+</div>
                    <div class="text-stone-400 text-xs font-medium mt-1">{u["st1"]}</div>
                </div>
                <div class="flex flex-col items-center px-4 py-2 text-center">
                    <div class="flex items-center justify-center gap-1">
                        <span class="text-2xl md:text-3xl font-bold" style="color:#1a1a1a;">5.0</span>
                        <span style="color:#f5b301;">{IC_STAR}</span>
                    </div>
                    <div class="text-stone-400 text-xs font-medium mt-1">104 {u["st2"]}</div>
                </div>
                <div class="flex flex-col items-center px-4 py-2 text-center">
                    <div class="text-2xl md:text-3xl font-bold" style="color:#1a1a1a;">💵</div>
                    <div class="text-stone-400 text-xs font-medium mt-1">{u["st3"]}</div>
                </div>
            </div>
            <div class="text-center mt-4">
                <a href="{GMAPS}" target="_blank" class="inline-flex items-center gap-2 font-medium text-xs hover:underline transition" style="color:#c0687a;">
                    <span style="color:#f5b301;">{IC_STAR}</span> {u["rev_cta"]}
                </a>
            </div>
        </div>
    </section>
'''

def reviews_block(lang, base):
    """Блок из 3 скриншотов Google-отзывов."""
    u = UI[lang]
    cells = "\n                ".join(
        f'''<div class="rounded-2xl overflow-hidden border border-stone-100 bg-white">
                    <div class="h-[280px] flex items-center justify-center p-2">
                        <img src="{base}{im}" alt="{u["rev_h"]}" loading="lazy" class="max-h-full max-w-full object-contain">
                    </div>
                </div>''' for im in REVIEW_IMGS)
    return f'''
    <section class="reveal py-10 px-4 border-b border-stone-100">
        <div class="max-w-4xl mx-auto">
            <h2 class="font-serif text-2xl font-bold text-center mb-6" style="color:#1a1a1a;">{u["rev_h"]}</h2>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {cells}
            </div>
            <div class="text-center mt-6">
                <a href="{GMAPS}" target="_blank" class="btn-rose inline-block font-medium py-2.5 px-6 rounded-xl text-sm">{u["rev_cta"]} →</a>
            </div>
        </div>
    </section>
'''

def render_catalog(lang, products):
    t = T[lang]
    base = ""
    canonical = f"{DOMAIN}/catalog-{lang}.html"
    alts = {l: f"{DOMAIN}/catalog-{l}.html" for l in LANGS}
    if lang == "ru":
        title = "Каталог букетов — доставка цветов в Нячанге | NhaTrang Flowers"
        meta = "Каталог свежих букетов и гелиевых шаров с доставкой по Нячангу день в день. Розы, лилии, корзины. Оплата рублями, донгами, долларами."
    elif lang == "en":
        title = "Bouquet catalog — flower delivery in Nha Trang | NhaTrang Flowers"
        meta = "Catalog of fresh bouquets and helium balloons with same-day delivery in Nha Trang. Roses, lilies, baskets. Pay in USD, VND, RUB."
    else:
        title = "꽃다발 카탈로그 — 나트랑 꽃 배달 | NhaTrang Flowers"
        meta = "나트랑 당일 배달 신선한 꽃다발과 헬륨 풍선 카탈로그. 장미, 백합, 바구니. 달러·동·루블 결제."
    cards = "\n            ".join(product_card(p, lang, base, t) for p in products)
    body = f'''    <main class="flex-grow">
    <section class="py-12 px-4 max-w-5xl mx-auto text-center">
        <h1 class="font-serif text-3xl md:text-4xl font-bold mb-3" style="color:#1a1a1a;">{t["catalog_h1"]}</h1>
        <p class="text-stone-500 text-sm max-w-xl mx-auto">{t["catalog_sub"]}</p>
    </section>
    {trust_bar(lang, base)}
    <section class="pb-16 px-4 max-w-5xl mx-auto pt-12">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            {cards}
        </div>
    </section>
    {reviews_block(lang, base)}
    {articles_block(lang, base)}
    </main>
'''
    lang_urls = {l: f"catalog-{l}.html" for l in LANGS}
    return head(lang, title, meta, canonical, alts, base, products[0]["img"]) + header(lang, base, lang_urls) + body + footer(base) + SCRIPTS

def render_blog(lang):
    t = T[lang]
    base = ""
    canonical = f"{DOMAIN}/blog-{lang}.html"
    alts = {l: f"{DOMAIN}/blog-{l}.html" for l in LANGS}
    if lang == "ru":
        title = "Статьи о цветах и поводах — NhaTrang Flowers"
        meta = "Полезные статьи о цветах, поводах для подарка и традициях Вьетнама. Доставка букетов по Нячангу."
    elif lang == "en":
        title = "Articles about flowers & occasions — NhaTrang Flowers"
        meta = "Helpful articles about flowers, gift occasions and Vietnamese traditions. Bouquet delivery in Nha Trang."
    else:
        title = "꽃과 기념일 블로그 — NhaTrang Flowers"
        meta = "꽃, 선물 기념일, 베트남 문화에 대한 유용한 글. 나트랑 꽃다발 배달."
    body = f'''    <main class="flex-grow">
    <section class="py-12 px-4 max-w-5xl mx-auto text-center">
        <h1 class="font-serif text-3xl md:text-4xl font-bold mb-3" style="color:#1a1a1a;">{t["blog_h1"]}</h1>
        <p class="text-stone-500 text-sm max-w-xl mx-auto">{t["blog_sub"]}</p>
    </section>
    <section class="pb-24 px-4 max-w-5xl mx-auto">
        <div class="bg-white rounded-2xl border border-stone-100 p-12 text-center text-stone-400">
            {t["blog_soon"]}
        </div>
    </section>
    </main>
'''
    lang_urls = {l: f"blog-{l}.html" for l in LANGS}
    return head(lang, title, meta, canonical, alts, base, "img/dSXDj.webp") + header(lang, base, lang_urls) + body + footer(base) + SCRIPTS

def main():
    products = list(csv.DictReader(open(PRODUCTS, encoding="utf-8")))
    n = 0
    for lang in LANGS:
        for p in products:
            out = os.path.join(CATALOG_DIR, f"{p['slug']}-{lang}.html")
            open(out, "w", encoding="utf-8").write(render_product(p, lang, products))
            n += 1
        open(os.path.join(ROOT, f"catalog-{lang}.html"), "w", encoding="utf-8").write(render_catalog(lang, products))
        open(os.path.join(ROOT, f"blog-{lang}.html"), "w", encoding="utf-8").write(render_blog(lang))
        n += 2
    print(f"Готово. Создано файлов: {n}")
    print(f"  товары: {len(products)*3}, каталог: 3, блог: 3")

if __name__ == "__main__":
    main()
