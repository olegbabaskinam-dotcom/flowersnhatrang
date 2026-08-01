# -*- coding: utf-8 -*-
"""Создаёт лёгкую 1.jpg рядом с 1.webp у каждого товара — для отправки фото в Telegram
(Telegram не принимает webp как фото). Запуск: python3 seo/make_tg_jpg.py"""
import glob,os
from PIL import Image
n=0; miss=0
for webp in glob.glob("img/products/*/1.webp"):
    jpg=webp[:-5]+".jpg"
    if os.path.exists(jpg): continue
    try:
        im=Image.open(webp).convert("RGB")
        im.thumbnail((900,900),Image.LANCZOS)
        im.save(jpg,"JPEG",quality=82,optimize=True)
        n+=1
    except Exception as e:
        print("ERR",webp,e); miss+=1
print(f"создано jpg: {n}, ошибок: {miss}, всего товаров: {len(glob.glob('img/products/*/1.webp'))}")
