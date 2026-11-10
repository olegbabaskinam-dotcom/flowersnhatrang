#!/usr/bin/env python3
"""Переводит все опубликованные рублёвые цены со старого курса на новый.

Формула нового курса: ceil(VND / RATE / STEP) × STEP (всегда вверх).
Запуск из корня new-site:
  python3 seo/update_rub_rate.py <новый курс> <новый шаг> <старый курс> <старый шаг>
  10.11.2026: python3 seo/update_rub_rate.py 280 100 295 50
Старые ₽ на сайте сопоставляются с ценой в ₫ (цены из products.csv, аренды колясок,
доп-товаров и все суммы, кратные 50 000 ₫, до 60 млн) и пересчитываются.
Неоднозначные старые суммы не трогаются и печатаются для ручной проверки.
"""
import csv, math, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "seo" / "products.csv"
RATE, STEP, OLD_RATE, OLD_STEP = (int(x) for x in sys.argv[1:5])
RUB_RE = re.compile(r"(?<![\d$])(\d{1,3}(?:[  ]\d{3})*|\d+) ₽")

def digits(v): return int(re.sub(r"\D", "", v) or "0")
def new_rub(vnd): return math.ceil(vnd / RATE / STEP) * STEP
def old_rub(vnd): return math.ceil(vnd / OLD_RATE / OLD_STEP) * OLD_STEP
def spaced(v): return f"{v:,}".replace(",", " ")

rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
fieldnames = list(rows[0].keys())
cands = {digits(r["price"]) for r in rows}
cands |= set(range(50_000, 60_000_001, 50_000))
rent = [300000, 400000, 500000, 650000, 750000, 900000, 1000000]
cands |= set(rent) | {1000000 + 130000 * k for k in range(1, 24)}
cands |= {100_000, 150_000, 300_000}

buckets = {}
for v in cands:
    buckets.setdefault(old_rub(v), set()).add(new_rub(v))
price_map = {o: n.pop() for o, n in buckets.items() if len(n) == 1}
ambig = sorted(o for o, n in buckets.items() if len(n) > 1)

for r in rows:
    r["price_sub"] = re.sub(r"\d[\d ]* ₽$", f"{spaced(new_rub(digits(r['price'])))} ₽", r["price_sub"])
with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n"); w.writeheader(); w.writerows(rows)

tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
untracked = subprocess.check_output(["git", "ls-files", "-z", "--others", "--exclude-standard"], cwd=ROOT).decode().split("\0")
skip_left = {}
files = changes = 0
for rel in tracked + untracked:
    if not rel or rel.startswith(("seo/", "_to_delete/", "_removed")):
        continue
    p = ROOT / rel
    if p.suffix.lower() not in {".html", ".js", ".json"} or not p.exists():
        continue
    src = p.read_text(encoding="utf-8")
    cnt = [0]
    def rep(m):
        o = digits(m.group(1))
        if o in price_map:
            cnt[0] += 1
            return f"{spaced(price_map[o])} ₽"
        skip_left[o] = skip_left.get(o, 0) + 1
        return m.group(0)
    out = RUB_RE.sub(rep, src)
    if out != src:
        p.write_text(out, encoding="utf-8"); files += 1; changes += cnt[0]
print(f"Курс: 1 ₽ = {RATE} ₫, шаг {STEP} ₽ (был {OLD_RATE}/{OLD_STEP})")
print(f"products.csv: {len(rows)} товаров; замен {changes} в {files} файлах")
print("неоднозначные старые суммы:", ambig[:30])
print("не распознаны (сумма: раз):", sorted(skip_left.items())[:60])
