#!/usr/bin/env python3
# SEO KO: title + description под Naver (больше кликов).
# Товары: категорийный ключ в title + инъекция ключа в описание.
import re, glob, json, sys, os

products = json.load(open('products.json', encoding='utf-8'))['products']
slug_cats = {p['slug']: (p.get('cats') or []) for p in products}

def kwd_for(cats):
    if 'cakes' in cats:   return '케이크 주문'      # торты — топ-спрос
    if any(c in cats for c in ('r25','r51','r101','mixed')): return '꽃배달'
    if 'prazdnik' in cats or 'nabory' in cats: return '선물세트 배달'
    if 'balloons' in cats: return '풍선배달'
    return '꽃배달'

def set_title_desc(s, title=None, desc=None):
    if title is not None:
        s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, s, count=1, flags=re.S)
        s = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1)+title+m.group(2), s, count=1)
    if desc is not None:
        s = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1)+desc+m.group(2), s, count=1)
        s = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1)+desc+m.group(2), s, count=1)
    return s

def cur(s):
    t = re.search(r'<title>(.*?)</title>', s, re.S)
    d = re.search(r'<meta name="description" content="(.*?)"', s, re.S)
    return (t.group(1) if t else ''), (d.group(1) if d else '')

def product_title(name, kwd):
    return '%s — 나트랑 %s·당일배달' % (name, kwd)

def transform_product(f, apply=False):
    slug = os.path.basename(f)[:-len('-ko.html')]
    cats = slug_cats.get(slug, [])
    kwd = kwd_for(cats)
    s = open(f, encoding='utf-8').read()
    t, d = cur(s)
    # имя = title до " — 나트랑 배달"
    m = re.match(r'^(.*?)\s*—\s*나트랑 배달(?:\s*\|\s*NhaTrang Flowers)?\s*$', t)
    name = m.group(1) if m else re.sub(r'\s*\|\s*NhaTrang Flowers\s*$','',t)
    new_t = product_title(name, kwd)
    # описание: первую "나트랑 당일 배달" → "나트랑 {kwd} 당일 배달"
    new_d = d.replace('나트랑 당일 배달', '나트랑 %s 당일 배달' % kwd, 1) if '나트랑 당일 배달' in d else d
    if apply:
        s = set_title_desc(s, new_t, new_d if new_d!=d else None)
        open(f,'w',encoding='utf-8').write(s)
    return t, new_t, kwd

if __name__ == '__main__':
    apply = '--apply' in sys.argv
    files = sorted(glob.glob('catalog/*-ko.html'))
    from collections import Counter
    kc = Counter()
    shown = 0
    for f in files:
        old_t, new_t, kwd = transform_product(f, apply)
        kc[kwd]+=1
        if shown < 14:
            print('  [%s]' % kwd)
            print('   OLD:', old_t)
            print('   NEW:', new_t)
            shown += 1
    print()
    print('APPLIED' if apply else 'DRY', 'товаров:', sum(kc.values()), dict(kc))
