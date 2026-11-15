# -*- coding: utf-8 -*-
"""第十一至十二课装配器。

沿用 tools/build.py 的版式与函数，把第 11–12 课并进十课合览，重拼为十二课合览，并同步 docs/。
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as B          # noqa: E402
import lessons_11_12 as L  # noqa: E402

ROOT = B.ROOT
DOCS = B.DOCS

COVER = """<div class="page cover">
  <div class="s">润 泽 少 儿 启 蒙 国 学</div>
  <h1>三 字 经</h1>
  <div class="t2">一句一故事 · 一图一世界</div>
  <div class="line"></div>
  <div class="info">第一课至第十二课　·　人之初　至　玉不琢<br>亲子共读 4–9 岁　·　每课双页：少儿读本 ／ 成人研学<br>样书　v1.0　·　二〇二六年十一月</div>
</div>"""


def main():
    css = B.read_css()
    pages = []

    for d in L.LESSONS:
        n = int(d['n'])
        folio = 2 * n
        kid = B.kid_page(d, folio)
        adult = B.adult_page(d, folio + 1)
        pages.append(kid + adult)

        single = (B.head('三字经·%s｜%s（样张）' % (d['no_short'], d['line_plain']), d['fav'], css)
                  + kid + adult + B.TAIL)
        fn = os.path.join(ROOT, '三字经·%s样张.html' % d['no_short'])
        open(fn, 'w', encoding='utf-8').write(single)
        open(os.path.join(DOCS, 'lesson%02d.html' % n), 'w', encoding='utf-8').write(single)
        print('written', os.path.basename(fn), 'and docs/lesson%02d.html' % n)

    # 以十课合览的既有页面为底，替换封面，续接第 11–12 课
    base = open(os.path.join(ROOT, '三字经·样书·十课合览.html'), encoding='utf-8').read()
    start = base.index('<div class="page cover">')
    end = base.rindex('</body>')
    seg = base[start:end]
    marker = '</div>\n\n<div class="page">'
    cut = seg.index(marker) + len('</div>')
    rest = seg[cut:].rstrip()

    body = COVER + '\n' + rest + ''.join(
        '\n<!-- 第 %s 课 -->\n%s' % (d['n'], p) for d, p in zip(L.LESSONS, pages))

    for path, title in [(os.path.join(ROOT, '三字经·样书·十二课合览.html'), '三字经·十二课合览（样书 v1.0）'),
                        (os.path.join(DOCS, 'book.html'), '三字经·十二课合览（样书 v1.0）')]:
        open(path, 'w', encoding='utf-8').write(B.head(title, '三', css) + body + B.TAIL)
        print('written', os.path.relpath(path, ROOT))


if __name__ == '__main__':
    main()
