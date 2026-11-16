# -*- coding: utf-8 -*-
"""第六十二至六十六课单课样张装配器。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B
from lessons_62_63 import LESSONS as A
from lessons_64_66 import LESSONS as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    css = B.read_css()
    for d in A + C:
        n = int(d['n'])
        title = '三字经·%s样张' % d['no_short']
        html = (B.head(title, d['fav'], css)
                + B.kid_page(d, 2 * n)
                + B.adult_page(d, 2 * n + 1)
                + B.TAIL)
        path = os.path.join(ROOT, title + '.html')
        open(path, 'w', encoding='utf-8').write(html)
        print('%-30s %6.1f KB' % (os.path.basename(path), len(html.encode()) / 1024))


if __name__ == '__main__':
    main()
