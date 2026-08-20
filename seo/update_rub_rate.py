#!/usr/bin/env python3
"""Обновляет все опубликованные рублёвые цены по products.csv.

Формула: цена VND / курс, затем всегда вверх до ближайших 100 ₽.
Запуск из корня new-site: python3 seo/update_rub_rate.py 280
"""

import csv
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "seo" / "products.csv"
RATE = int(sys.argv[1]) if len(sys.argv) > 1 else 280
RUB_RE = re.compile(r"(?<!\d)(\d[\d ]{0,8}) ₽")


def digits(value):
    return int(re.sub(r"\D", "", value) or "0")


def rub_price(vnd):
    return math.ceil((vnd / RATE) / 100) * 100


def spaced(value):
    return f"{value:,}".replace(",", " ")


with CSV_PATH.open(newline="", encoding="utf-8") as source:
    reader = csv.DictReader(source)
    fieldnames = reader.fieldnames
    rows = list(reader)

price_map = {}
for row in rows:
    old_rub = digits(row["price_sub"].rsplit("·", 1)[-1])
    new_rub = rub_price(digits(row["price"]))
    if old_rub:
        price_map[old_rub] = new_rub
    row["price_sub"] = re.sub(r"\d[\d ]* ₽$", f"{spaced(new_rub)} ₽", row["price_sub"])

# Старые карточки, где рублёвый эквивалент когда-то считался по другому курсу.
for old_rub, vnd in {
    650: 200_000,
    1900: 600_000,
    5400: 1_700_000,
    6300: 2_000_000,
    9500: 3_000_000,
    10500: 3_250_000,
    14900: 4_700_000,
}.items():
    price_map.setdefault(old_rub, rub_price(vnd))

with CSV_PATH.open("w", newline="", encoding="utf-8") as target:
    writer = csv.DictWriter(target, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
changed_files = 0
changed_prices = 0
for rel in tracked:
    if not rel or rel == "seo/products.csv" or rel == "seo/PUBLISH-LOG.md":
        continue
    path = ROOT / rel
    if path.suffix.lower() not in {".html", ".js", ".json"}:
        continue
    original = path.read_text(encoding="utf-8")
    count = 0

    def replace(match):
        nonlocal_count[0] += 1
        old = digits(match.group(1))
        return f"{spaced(price_map[old])} ₽" if old in price_map else match.group(0)

    nonlocal_count = [0]
    updated = RUB_RE.sub(replace, original)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        changed_files += 1
        changed_prices += nonlocal_count[0]

print(f"Курс: 1 ₽ = {RATE} ₫")
print(f"products.csv: {len(rows)} товаров")
print(f"Статические цены: {changed_prices} замен в {changed_files} файлах")
