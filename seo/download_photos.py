# -*- coding: utf-8 -*-
"""
Скачивание бесплатных стоковых фото к статьям из registry.csv.
Источник: Pexels (бесплатно, лицензия позволяет коммерческое использование, ссылка
на автора не обязательна, но желательна). Конвертация в webp + ресайз + SEO-имя.

КАК ПОЛЬЗОВАТЬСЯ:
  1. Получить бесплатный API-ключ: https://www.pexels.com/api/ (1 мин, нужен email)
  2. Вставить ключ в PEXELS_KEY ниже (или передать переменной окружения PEXELS_KEY)
  3. Запустить:  python3 download_photos.py 4      (4 = сколько статей обработать за раз)
  Фото лягут в ../img/blog/<slug>.webp, готовые к вставке в страницу.

Зависимости: requests, Pillow
  pip install requests pillow --break-system-packages
"""
import os, sys, csv, io, time
import requests
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

# автозагрузка ключа из seo/.env
_envf = os.path.join(HERE, ".env")
if os.path.exists(_envf):
    for _line in open(_envf, encoding="utf-8"):
        if _line.strip().startswith("PEXELS_KEY="):
            os.environ.setdefault("PEXELS_KEY", _line.split("=", 1)[1].strip())

PEXELS_KEY = os.environ.get("PEXELS_KEY", "ВСТАВЬ_СВОЙ_КЛЮЧ")

REGISTRY = os.path.join(HERE, "registry.csv")
IMG_DIR = os.path.join(HERE, "..", "img", "blog")
TARGET_W = 1200            # ширина обложки статьи
THUMB_W = 600             # ширина карточки в витрине блога
QUALITY = 80

os.makedirs(IMG_DIR, exist_ok=True)

def search_photo(query, seed=0):
    # берём пул из 15 фото и выбираем разное по seed (id статьи),
    # чтобы у статей с одинаковым запросом были разные картинки
    r = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": 15, "orientation": "landscape"},
        timeout=30,
    )
    r.raise_for_status()
    photos = r.json().get("photos", [])
    if not photos:
        return None, None
    p = photos[seed % len(photos)]
    return p["src"]["large2x"], p.get("photographer", "")

def save_webp(img_bytes, out_path, width):
    im = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    w, h = im.size
    if w > width:
        im = im.resize((width, int(h * width / w)), Image.LANCZOS)
    im.save(out_path, "WEBP", quality=QUALITY, method=6)

def main(limit):
    rows = list(csv.DictReader(open(REGISTRY, encoding="utf-8")))
    done = 0
    attempts = 0
    for row in rows:
        if done >= limit or attempts >= limit:
            break
        slug = row["slug"]
        cover = os.path.join(IMG_DIR, f"{slug}.webp")
        if os.path.exists(cover):
            continue  # уже скачано
        query = row["photo_query_en"]
        attempts += 1
        try:
            url, author = search_photo(query, seed=int(row["id"]))
            if not url:
                print(f"  нет фото для: {query}")
                continue
            img = requests.get(url, timeout=60).content
            save_webp(img, cover, TARGET_W)
            save_webp(img, os.path.join(IMG_DIR, f"{slug}-thumb.webp"), THUMB_W)
            print(f"OK [{row['id']}] {slug}.webp  (фото: {author or 'Pexels'})")
            done += 1
            time.sleep(1)   # вежливо к API
        except Exception as e:
            print(f"  ошибка {slug}: {e}")
    print(f"\nГотово. Скачано: {done}")

if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    if PEXELS_KEY == "ВСТАВЬ_СВОЙ_КЛЮЧ":
        print("Сначала вставь PEXELS_KEY (см. инструкцию вверху файла).")
        sys.exit(1)
    main(limit)
