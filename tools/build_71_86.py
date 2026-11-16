# -*- coding: utf-8 -*-
"""第七十一至八十六课单课样张装配器（16 课，全段收束）。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B
from lessons_71_74 import LESSONS as L1
from lessons_75_78 import LESSONS as L2
from lessons_79_82 import LESSONS as L3
from lessons_83_86 import LESSONS as L4

LESSONS = L1 + L2 + L3 + L4
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    css = B.read_css()
    for d in LESSONS:
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
