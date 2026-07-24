#!/usr/bin/env python3
# Пере-вставка блока отзывов (REVIEWS-START..</section>) во все страницы.
import re, os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, reviews_data
importlib.reload(reviews_data)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT = re.compile(r'<!--REVIEWS-START-->.*?</section>', re.S)
LANGPAT = re.compile(r'rvTrack-(ru|en|ko)')
only = sys.argv[1] if len(sys.argv) > 1 else None
files = [only] if only else glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)
n = 0
for fn in files:
    s = open(fn, encoding='utf-8').read()
    if '<!--REVIEWS-START-->' not in s: continue
    m = LANGPAT.search(s)
    lang = m.group(1) if m else 'ru'
    rel = os.path.relpath(fn, ROOT)
    depth = rel.count(os.sep)
    base = '../' * depth
    block = reviews_data.carousel_section(lang, base)
    s2 = PAT.sub(lambda _: block, s, count=1)
    if s2 != s:
        open(fn, 'w', encoding='utf-8').write(s2); n += 1
print('обновлено файлов:', n)
