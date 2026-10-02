#!/usr/bin/env python3
# Переделка кнопок связи на KO-страницах:
# убрать WhatsApp, добавить прямой чат KakaoTalk (open.kakao) + канал (pf.kakao).
# Итог везде: [Онлайн-заказ] [Kakao напрямую] [Kakao канал] [Instagram]
import re, glob, sys, os

DIRECT = "https://open.kakao.com/o/seD8jkli"   # прямой чат 1-на-1
CHANNEL = "http://pf.kakao.com/_zbwKX"          # канал
WA = "https://wa.me/37443529162"
TG = "https://t.me/babaskin_o"

KSVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" '
        'width="1em" height="1em" style="display:inline-block;vertical-align:-.125em">'
        '<path d="M12 3C6.477 3 2 6.477 2 10.5c0 2.666 1.574 5.01 3.95 6.37-.174.617-.63 2.24-.722 '
        '2.586-.112.435.159.43.335.313.138-.09 2.19-1.48 3.076-2.077.437.06.885.091 1.361.091 5.523 '
        '0 10-3.477 10-7.783S17.523 3 12 3z"/></svg>')

T_DIRECT = "카카오톡으로 주문"   # заказать напрямую в KakaoTalk
T_CHANNEL = "카카오톡 채널"      # канал KakaoTalk

def ko_files():
    fs = []
    for p in ['index-kr.html','balloons-kr.html','torty-kr.html','nabory-kr.html',
              'prazdnik-kr.html','katalog-kr.html','catalog-ko.html','blog-ko.html']:
        if os.path.exists(p): fs.append(p)
    fs += glob.glob('catalog/*-ko.html') + glob.glob('blog/*-ko.html')
    return fs

def repl_btn(s, href, new_href, new_text):
    """Заменить одну btn-rose CTA-кнопку (по href), сохранив class."""
    pat = r'<a href="%s" target="_blank" (class="btn-rose[^"]*")[^>]*>.*?</a>' % re.escape(href)
    def f(m):
        return '<a href="%s" target="_blank" %s>%s %s</a>' % (new_href, m.group(1), KSVG, new_text)
    return re.sub(pat, f, s, flags=re.S, count=1)

def split_kakao_to_two(s, href):
    """Pattern A: pf.kakao btn -> direct + вставить канал после."""
    pat = r'<a href="%s" target="_blank" (class="btn-rose[^"]*")[^>]*>.*?</a>' % re.escape(href)
    def f(m):
        cls = m.group(1)
        direct = '<a href="%s" target="_blank" %s>%s %s</a>' % (DIRECT, cls, KSVG, T_DIRECT)
        channel = '<a href="%s" target="_blank" %s>%s %s</a>' % (CHANNEL, cls, KSVG, T_CHANNEL)
        return direct + '\n                    ' + channel
    return re.sub(pat, f, s, flags=re.S, count=1)

def transform(f):
    s = open(f, encoding='utf-8').read()
    orig = s

    # 1) HEADER: иконка WhatsApp -> иконка Kakao (прямой чат). Ключ: aria-label="WhatsApp".
    s = re.sub(
        r'<a href="https://wa\.me/37443529162" target="_blank" aria-label="WhatsApp"( style="[^"]*")>.*?</a>',
        lambda m: '<a href="%s" target="_blank" aria-label="KakaoTalk"%s>%s</a>' % (DIRECT, m.group(1), KSVG),
        s, flags=re.S, count=1)

    has_kakao = bool(re.search(r'<a href="http://pf\.kakao\.com/_zbwKX" target="_blank" class="btn-rose', s))
    has_wa    = bool(re.search(r'<a href="https://wa\.me/37443529162" target="_blank" class="btn-rose', s))
    has_tg    = bool(re.search(r'<a href="https://t\.me/babaskin_o" target="_blank" class="btn-rose', s))

    if has_kakao and not has_wa:
        # Pattern A — лендинг: [order, pf.kakao, insta] -> добавить прямой + канал
        s = split_kakao_to_two(s, CHANNEL)
        kind = 'A-landing'
    elif has_wa and has_tg:
        # Pattern B — листинг: [order, WhatsApp, Telegram, insta]
        s = repl_btn(s, WA, DIRECT, T_DIRECT)
        s = repl_btn(s, TG, CHANNEL, T_CHANNEL)
        kind = 'B-listing'
    elif has_kakao and has_wa:
        # Pattern C — товар/статья: [order, pf.kakao, WhatsApp, insta]
        s = repl_btn(s, CHANNEL, DIRECT, T_DIRECT)   # pf.kakao -> прямой
        s = repl_btn(s, WA, CHANNEL, T_CHANNEL)      # WhatsApp -> канал
        kind = 'C-product'
    else:
        kind = 'header-only'

    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
    return kind

if __name__ == '__main__':
    dry = '--apply' not in sys.argv
    from collections import Counter
    c = Counter()
    for f in ko_files():
        if dry:
            # только классификация, без записи
            s = open(f, encoding='utf-8').read()
            has_kakao = bool(re.search(r'pf\.kakao\.com/_zbwKX" target="_blank" class="btn-rose', s))
            has_wa    = bool(re.search(r'wa\.me/37443529162" target="_blank" class="btn-rose', s))
            has_tg    = bool(re.search(r't\.me/babaskin_o" target="_blank" class="btn-rose', s))
            k = 'A-landing' if (has_kakao and not has_wa) else 'B-listing' if (has_wa and has_tg) else 'C-product' if (has_kakao and has_wa) else 'header-only'
        else:
            k = transform(f)
        c[k]+=1
    print('DRY RUN' if dry else 'APPLIED', dict(c), 'total', sum(c.values()))
