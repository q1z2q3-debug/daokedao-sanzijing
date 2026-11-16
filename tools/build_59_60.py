# -*- coding: utf-8 -*-
"""第五十九至六十课单课样张装配器。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B
from lessons_59_60 import LESSONS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CN = ['〇', '一', '二', '三', '四', '五', '六', '七', '八', '九']


def cn_num(n):
    if n < 10:
        return CN[n]
    if n < 20:
        return '十' + (CN[n % 10] if n % 10 else '')
    return CN[n // 10] + '十' + (CN[n % 10] if n % 10 else '')


def main():
    css = B.read_css()
    for d in LESSONS:
        n = int(d['n'])
        title = '三字经·第%s课样张' % cn_num(n)
        html = (B.head(title, d['fav'], css)
                + B.kid_page(d, 2 * n)
                + B.adult_page(d, 2 * n + 1)
                + B.TAIL)
        path = os.path.join(ROOT, title + '.html')
        open(path, 'w', encoding='utf-8').write(html)
        print('%-30s %6.1f KB' % (os.path.basename(path), len(html.encode()) / 1024))


if __name__ == '__main__':
    main()
