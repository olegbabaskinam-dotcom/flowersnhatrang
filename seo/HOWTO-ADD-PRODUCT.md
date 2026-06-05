# 🌸 SOP — как Claude быстро добавляет товар на flowers-nha-trang.online

> Это инструкция Claude для себя. Открывать ВМЕСТЕ с КОНТЕКСТ_Олег_цветы.md в начале задачи «добавить товар».
> Цель: добавить товар за минимум шагов, ничего не сломав на живом сайте.
> Последнее обновление: 5 июня 2026 (после добавления «Стильный сборный букет в белой упаковке», id 14).

---

## ⚠️ ГЛАВНОЕ, ЧТО НЕЛЬЗЯ ЗАБЫВАТЬ
1. **Первое фото = главное** (1.webp = hero + обложка карточки). Порядок остальных = как дал Олег.
2. **Работать ТОЛЬКО с фото Олега.** Не искать в `_src/` наугад, не брать чужое.
2a. **Каждый присланный набор фото = ВСЕГДА НОВЫЙ отдельный товар.** Даже если похоже на существующее (ещё один «101 роза», ещё один «набор шаров») — это РАЗНАЯ позиция. НЕ спрашивать «это к существующему?», НЕ добавлять к старой карточке. Новый id, новый slug, новая карточка. Позиций будет очень много.
3. **Цены ₽ округлять до красивых сумм** (до 100/500/1000). Пример: 3 960 → **4 000**. $ — до десятков. Курс ориентир: ~25 000 ₫ = $1, ~310 ₫ = 1 ₽.
4. **НЕ запускать полный `build_site.py`** — он затирает ручные доработки каталога (фильтр «Фиолетовые», умное скрытие цвета, крупная галерея) И блог (статьи не лежат в `articles/*.json`).
5. **Перед коммитом всегда `git diff --stat`** — убедиться, что изменились только нужные файлы.
6. **Деплой**: `git fetch` → если local позади `git reset --hard origin/main` → `git add <только нужные>` → commit → push. НИКОГДА `git add -A` со старой папки.
7. **После — записать** в `seo/PUBLISH-LOG.md` и в `КОНТЕКСТ_Олег_цветы.md`.

---

## ШАГ 0. Спросить/подготовить
- Создать папку-приёмник: `img/_src/<краткое-имя>-new/` и сказать Олегу ТОЧНЫЙ путь куда кидать фото
  (Documents → Claude → Projects → Flowers New SAIT → new-site → img → _src → …).
- Дождаться «готово», проверить папку.
- Узнать у Олега (или из скрина): название, цену в ₫, особенности.

## ШАГ 1. Параметры товара
- `id` = следующий по products.csv.
- `slug` = транслит-латиница. ВАЖНО для фильтров (см. build_site.py):
  - категория: начинается с `25-`→r25, `51-`→r51, `101-`/`151-`→r101, есть `shar`→balloons, иначе **mixed**.
  - цвет: `belo-rozov`→pink, `kras`→red, `bel`→white, `rozov`→pink, иначе пусто.
  - → хочешь mixed+pink: slug без «25/51/...» и со словом `rozov` (напр. `...-rozovyy`), без `bel`.
- `price` = «1 250 000 донгов» (слово «донгов» обязательно — генератор сам меняет на VND/동).
- `price_sub` = «≈ $50 · 4 000 ₽» — ₽ ОКРУГЛИТЬ.

## ШАГ 2. Фото → webp
```python
from PIL import Image, ImageOps
import glob, os
SRC="img/_src/<имя>-new"; DST="img/products/<slug>"
os.makedirs(DST, exist_ok=True)
for i,f in enumerate(sorted(glob.glob(SRC+"/*.jpg")), 1):   # sorted = порядок Олега, [0]=главное
    im=ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    im.thumbnail((1200,1200), Image.LANCZOS)
    im.save(f"{DST}/{i}.webp","WEBP",quality=82,method=6)
```

## ШАГ 3. Строка в products.csv (csv-writer, НЕ руками — запятые в описаниях)
Колонки: `id,name_ru,slug,img,alt_ru,desc_ru,price,price_sub,order_ru,name_en,desc_en,alt_en,name_ko,desc_ko,alt_ko`
- `img` = `img/products/<slug>/1.webp`
- `alt_*` = «<название> Нячанг доставка» (RU), «… delivery Nha Trang» (EN), «나트랑 … 배달» (KO)
- `desc_*` — стиль как у соседних: со строчной, через « — », без точки в конце для карточки.
- `order_ru` = повтор названия.

## ШАГ 4. Страницы товара (генерить + подменять 3 блока)
НЕ копировать руками. Скрипт: импортировать `build_site`, для каждого lang
`b.render_product(new, lang, products)`, затем заменить на ЖИВЫЕ версии:
- **CSS-A**: добавить `.gallery-slider{height:24rem;}` + media 30rem + `.gallery-slider .pcard-slide{object-fit:contain;padding:.75rem;}`, увеличить стрелки (2.5rem, opacity:1, z-index:5).
- **CSS-B**: dots z-index:3, dot .45rem + box-shadow.
- **CSS-C**: добавить `.filt-group.color-hidden{display:none;}`.
- **Галерея**: заменить блок `gallery-main + thumbs` на `<div class="pcard-slider gallery-slider …">` с N слайдами (1-й `active`,`eager`; alt = «<alt> N»), стрелками и точками.
- JS трогать НЕ нужно (на странице товара фильтр — мёртвый код).
Точные строки замен — см. историю/коммит d1585d5 или живую страницу-эталон с 8 фото
(`catalog/151-krasnyh-roz-korzina-i-nabor-sharov-l-ru.html` или `7-vetok-liliy-ru.html`).
Проверка: `diff` CSS-региона (стр. ~82-101) новой страницы с эталоном → почти пусто.

## ШАГ 5. Карточки в каталог (РУКАМИ, не генератором)
В `catalog-ru/en/ko.html` вставить карточку ПЕРЕД закрытием грида
(якорь: `</div>\n    </section>\n\n    <section class="reveal py-10 px-4 border-b border-stone-100">`).
Шаблон карточки = как у 151 (полная карусель N фото):
`data-cat="mixed" data-color="pink"`, slider с N слайдами+стрелки+точки, затем `<a href="catalog/<slug>-<lang>.html">` с h3/desc/price/sub/кнопка.
Кнопка: RU «подробнее →», EN «details →», KO «자세히 →». Валюта: RU «донгов», EN «VND», KO «동».

## ШАГ 5b. Ротация на главной (`js/featured.js`)
Главная (`index.html`/`index-en.html`/`index-kr.html`) показывает 6 товаров, которые сами меняются каждый час (рандом из всего каталога, сид = UTC-час). Список товаров живёт в `js/featured.js` в массиве `PRODUCTS`.
**Надо: добавить новый товар в `PRODUCTS`** (объект `{slug, cat, color, ru:{name,desc,alt,price,sub}, en:{...}, ko:{...}}`), иначе он не попадёт в ротацию. `cat`/`color` — те же правила, что в build_site (`product_cat`/`product_color`). price: «N донгов»/«N VND»/«N 동», sub одинаковый. Проще всего перегенерить массив из products.csv тем же скриптом, что создавал файл (см. коммит 8bd591d). Файлы index НЕ трогаем — они уже подключают featured.js, статические 6 карточек оставлены как фолбэк для SEO.

## ШАГ 6. Sitemap
В `sitemap.xml` перед `</urlset>` добавить 3 блока `<url>` (ru/en/ko) с 4 hreflang (ru/en/ko/x-default), lastmod=сегодня, changefreq weekly, priority 0.7. Проверить `xmllint --noout sitemap.xml`.

## ШАГ 7. Деплой + запись
```bash
git fetch origin
git rev-list --left-right --count HEAD...origin/main   # 0 0 — ок; иначе reset --hard origin/main и переделать
git add seo/products.csv catalog-{ru,en,ko}.html sitemap.xml js/featured.js \
        catalog/<slug>-{ru,en,ko}.html img/products/<slug>/
git diff --cached --stat        # глазами: только нужное
git commit -m "Новый товар: <название> (<цена>), N фото, RU/EN/KO + каталог + sitemap"
git push origin main
```
Затем дописать `seo/PUBLISH-LOG.md` (+1 к счётчику букетов) и `КОНТЕКСТ_Олег_цветы.md`.

## Чек-лист «не забыл?»
- [ ] 1.webp = главное; ₽ округлено
- [ ] 3 страницы товара: карусель N фото, цена/мета/JSON-LD верны
- [ ] 3 карточки в каталоге (правильные data-cat/data-color)
- [ ] товар добавлен в `js/featured.js` PRODUCTS (ротация на главной)
- [ ] sitemap +3 url, xmllint ок
- [ ] git diff --stat чистый → push
- [ ] PUBLISH-LOG + КОНТЕКСТ обновлены
