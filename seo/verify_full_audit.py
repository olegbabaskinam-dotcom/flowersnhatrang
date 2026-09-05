#!/usr/bin/env python3
"""Финальная автоматическая проверка правил полного аудита сайта."""

from __future__ import annotations

import csv
import html
import json
import math
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
NODE = Path("/Users/olegbabaskin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node")


def tracked(suffix: str | None = None) -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    paths = [ROOT / item.decode() for item in raw.split(b"\0") if item]
    return [path for path in paths if suffix is None or path.suffix.lower() == suffix]


def local_target(page: Path, value: str) -> Path | None:
    value = unquote(value.split("?", 1)[0].split("#", 1)[0])
    if not value or value.startswith(("http://", "https://", "//", "data:", "mailto:", "tel:", "javascript:")):
        return None
    return (ROOT / value.lstrip("/")) if value.startswith("/") else (page.parent / value).resolve()


def main() -> int:
    errors: list[str] = []
    inline_scripts: list[dict[str, str | int]] = []
    html_files = [path for path in tracked(".html") if path.exists()]
    title_over = desc_over = image_tags = 0

    commercial_same_day = [
        re.compile(r"(?:deliver\w*|delivery)[^<\n\"]{0,220}(?:same[ -]day)", re.I),
        re.compile(r"(?:same[ -]day)[^<\n\"]{0,220}(?:deliver\w*|delivery)", re.I),
        re.compile(r"(?:достав\w*|привез\w*)[^<\n\"]{0,220}(?:день в день|в (?:тот же )?день заказа)", re.I),
        re.compile(r"당일[^<\n\"]{0,40}(?:꽃?배달|배송)"),
        re.compile(r"(?:привез\w* сегодня|delivered today)", re.I),
    ]
    forbidden_ko_payment = re.compile(r"결제[^<\n\"]{0,160}(?:루블|러시아 카드|카자흐|Kaspi|SBP)|(?:루블|러시아 카드|카자흐|Kaspi|SBP)[^<\n\"]{0,160}결제", re.I)

    for path in html_files:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        title = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
        title_value = html.unescape(title.group(1)).strip() if title else ""
        if title_value and len(title_value) > 60:
            title_over += 1
        description = re.search(r'<meta\b[^>]*name=["\']description["\'][^>]*content=(["\'])(.*?)\1', text, re.I | re.S)
        description_value = html.unescape(description.group(2)).strip() if description else ""
        if description_value and len(description_value) > 160:
            desc_over += 1
        # Google truncates to the device width and does not define a fixed
        # character limit. A literal source ellipsis, however, means our own
        # generator removed meaning before the crawler saw the page.
        if title_value.endswith("…") or description_value.endswith("…"):
            errors.append(f"искусственно обрезанные метаданные: {rel}")
        is_noindex = bool(re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', text, re.I))
        if '<link rel="canonical"' in text and not is_noindex and (not title_value or not description_value):
            errors.append(f"нет title/description у индексируемой страницы: {rel}")
        if rel.endswith("-en.html") or rel in {"index-en.html", "catalog-en.html", "blog-en.html"}:
            if re.search(r"[А-Яа-яЁё]", title_value + " " + description_value):
                errors.append(f"кириллица в EN-метаданных: {rel}")

        for tag in re.findall(r"<img\b[^>]*>", text, re.I | re.S):
            image_tags += 1
            source = re.search(r'\bsrc=["\']([^"\']+)', tag, re.I)
            if not source:
                continue
            target = local_target(path, source.group(1))
            if target is not None and target.exists() and (not re.search(r"\bwidth=", tag, re.I) or not re.search(r"\bheight=", tag, re.I)):
                errors.append(f"img без width/height: {rel} → {source.group(1)}")

        for tag in re.findall(r"<a\b[^>]*\btarget=[" + "\"'" + r"]_blank[" + "\"'" + r"][^>]*>", text, re.I | re.S):
            if not re.search(r'\brel=["\'][^"\']*noopener', tag, re.I):
                errors.append(f"target=_blank без noopener: {rel}")

        if any(pattern.search(text) for pattern in commercial_same_day):
            errors.append(f"коммерческое обещание доставки день-в-день: {rel}")
        if re.search(r'aggregateRating|>1000\+</div>|>5\.0</span>|148 (?:отзыв|Google review)', text, re.I):
            errors.append(f"неподтверждённый счётчик/рейтинг: {rel}")
        if (rel.endswith("-ko.html") or rel.endswith("-kr.html") or rel in {"catalog-ko.html", "blog-ko.html", "index-kr.html"}):
            if forbidden_ko_payment.search(text):
                errors.append(f"запрещённая оплата в KO: {rel}")
            # KO-отзывы теперь НАМЕРЕННО показываются на корейском (реальные корейцы
            # помечены отдельно, зарубежные — с пометкой «번역»). Блок rv-wrap на KO
            # больше не считается ошибкой; вместо этого запрещаем русские виджеты-рейтинги
            # (их ловит проверка aggregateRating/1000+/5.0 выше).
            if re.search(r"ежедневно|донгов|aria-label=[\"'](?:Корзина|Меню)[\"']", text):
                errors.append(f"русский интерфейсный текст в KO: {rel}")

        for script_index, match in enumerate(re.finditer(r"<script\b([^>]*)>(.*?)</script>", text, re.I | re.S), 1):
            attrs, source = match.groups()
            if re.search(r"\bsrc\s*=", attrs, re.I) or re.search(r"(?:ld\+json|application/json)", attrs, re.I):
                continue
            if source.strip():
                inline_scripts.append({"file": rel, "index": script_index, "code": source})

    large_products: list[str] = []
    for path in tracked(".webp"):
        if not path.exists() or "img/products/" not in path.as_posix():
            continue
        with Image.open(path) as image:
            if max(image.size) > 1200:
                large_products.append(path.relative_to(ROOT).as_posix())
    errors.extend(f"товарное фото > 1200px: {name}" for name in large_products)

    registry = list(csv.DictReader((ROOT / "seo/registry.csv").open(encoding="utf-8")))
    done = {row["slug"] for row in registry if row.get("status_ru") == row.get("status_en") == row.get("status_ko") == "done"}
    published = {path.name.removesuffix("-ru.html") for path in (ROOT / "blog").glob("*-ru.html")}
    if done != published:
        errors.append(f"реестр статей расходится: done={len(done)}, опубликовано={len(published)}")

    products = list(csv.DictReader((ROOT / "seo/products.csv").open(encoding="utf-8")))
    for row in products:
        vnd = int(re.sub(r"\D", "", row["price"]) or "0")
        expected = math.ceil((vnd / 275) / 100) * 100
        rub_match = re.search(r"(\d[\d ]*) ₽$", row["price_sub"])
        actual = int(re.sub(r"\D", "", rub_match.group(1))) if rub_match else -1
        if actual != expected:
            errors.append(f"курс 275 нарушен в products.csv: ID {row['id']} — {actual}, ожидается {expected}")
        product_page = ROOT / "catalog" / f"{row['slug']}-ru.html"
        expected_text = f"{expected:,} ₽".replace(",", " ")
        if product_page.exists() and expected_text not in product_page.read_text(encoding="utf-8"):
            errors.append(f"неактуальная рублёвая цена: {product_page.relative_to(ROOT)} — ожидается {expected_text}")

    cart_text = (ROOT / "cart.html").read_text(encoding="utf-8")
    if "for(let h=start;h<=21;h++)" not in cart_text or re.search(r"timeHint_(?:morning|day).*?22:00", cart_text):
        errors.append("слоты доставки в cart.html должны заканчиваться в 21:00")

    home_rules = {
        "index.html": ("Онлайн-заказ — со следующего дня", "срочная доставка сегодня", "через оператора до 18:00"),
        "index-en.html": ("Online orders start next day", "urgent delivery today", "via an operator until 18:00"),
        "index-kr.html": ("온라인 주문은 다음 날부터", "오늘 긴급 배송", "18:00까지 상담원"),
    }
    for filename, required in home_rules.items():
        source = (ROOT / filename).read_text(encoding="utf-8")
        if not all(phrase.lower() in source.lower() for phrase in required):
            errors.append(f"не разделены онлайн/срочные заказы на главной: {filename}")
        if 'id="countdown"' not in source or "window.__renderOperatorCountdown=render" not in source or "Asia/Ho_Chi_Minh" not in source:
            errors.append(f"нет рабочего таймера оператора до 18:00: {filename}")

    website_source = (ROOT / "index.html").read_text(encoding="utf-8")
    if '"@type": "WebSite"' not in website_source or '"name": "NhaTrang Flowers"' not in website_source:
        errors.append("на главной нет WebSite-разметки с единым названием сайта")

    for stem in ("balloons", "torty", "nabory", "prazdnik"):
        for suffix in ("", "-en", "-kr"):
            filename = f"{stem}{suffix}.html"
            source = (ROOT / filename).read_text(encoding="utf-8")
            expected = f'https://flowers-nha-trang.online/{filename}'
            first_schema = re.search(
                r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>\s*(\{.*?\})\s*</script>',
                source,
                re.I | re.S,
            )
            try:
                schema = json.loads(first_schema.group(1)) if first_schema else {}
            except json.JSONDecodeError:
                schema = {}
            if schema.get("@type") != "LocalBusiness" or schema.get("@id") != expected or schema.get("url") != expected:
                errors.append(f"LocalBusiness не соответствует посадочной странице: {filename}")
            if stem != "balloons" and re.match(r"Доставка гелиевых шаров|Helium balloon delivery|냐짱 헬륨.?풍선", str(schema.get("description", "")), re.I):
                errors.append(f"чужое описание шаров в JSON-LD: {filename}")

    if NODE.exists() and inline_scripts:
        checker = r"""
const fs=require('fs');
const scripts=JSON.parse(fs.readFileSync(0,'utf8'));
const bad=[];
for(const item of scripts){
  try{ new Function(item.code); }
  catch(error){ bad.push({file:item.file,index:item.index,message:error.message}); }
}
process.stdout.write(JSON.stringify(bad));
"""
        checked = subprocess.run(
            [str(NODE), "-e", checker], input=json.dumps(inline_scripts), text=True,
            capture_output=True, check=False,
        )
        if checked.returncode:
            errors.append("не удалось проверить встроенный JavaScript: " + checked.stderr.strip())
        else:
            for item in json.loads(checked.stdout or "[]"):
                errors.append(f"ошибка JavaScript: {item['file']} script#{item['index']} — {item['message']}")

    print(f"Проверено HTML: {len(html_files)}")
    print(f"Проверено img-тегов: {image_tags}")
    print(f"Title > 60: {title_over}; description > 160: {desc_over}")
    print(f"Товарных WebP > 1200px: {len(large_products)}")
    print(f"Опубликованных статей в реестре: {len(done)}")
    print(f"Проверено встроенных JavaScript-блоков: {len(inline_scripts)}")
    print(f"Цены проверены по курсу 275: {len(products)}")
    print(f"Ошибок полного аудита: {len(errors)}")
    for error in errors[:80]:
        print("  - " + error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
