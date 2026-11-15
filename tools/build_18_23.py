# -*- coding: utf-8 -*-
"""第 13–17 课装配。图位缺图时渲染为占位框（图先留空版）。

用法：
  python3 tools/build_13_17.py            仅出五课单课样张（本地，不碰合册）
  python3 tools/build_13_17.py --full     出单课样张 + docs/lesson13-17 + 十七课合册
"""
import os, sys, html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B
from lessons_18_23 import LESSONS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')

PH_CSS = """
figure.ph .phbox{width:100%;aspect-ratio:4/3;border:1px dashed #D6C9AE;background:#FBF7EC;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px}
figure.ph .phbox .k{font-family:"Noto Sans SC",sans-serif;font-size:11px;letter-spacing:.28em;color:#BCAF93}
figure.ph .phbox .f{font-family:"Noto Serif SC",serif;font-size:15px;color:#8C7F63;letter-spacing:.12em}
"""

COVER = """<div class="page cover">
  <div class="s">润 泽 少 儿 启 蒙 国 学</div>
  <h1>三 字 经</h1>
  <div class="t2">一句一故事 · 一图一世界</div>
  <div class="line"></div>
  <div class="info">第一课至第二十三课　·　人之初　至　千而万<br>亲子共读 4–9 岁　·　每课双页：少儿读本 ／ 成人研学<br>样书　v1.2.1　·　二〇二六年十一月</div>
</div>"""


ORIG = B.img_tag


def img_or_ph(fname, alt, cap):
    path = os.path.join(B.ASSETS, fname)
    if os.path.exists(path):
        return ORIG(fname, alt, cap)
    return ('<figure class="ph">\n      <div class="phbox" role="img" aria-label="%s">'
            '<span class="k">插 图 待 补</span><span class="f">%s</span></div>\n'
            '      <figcaption>%s</figcaption>\n    </figure>'
            % (html.escape(alt), html.escape(fname.rsplit('.', 1)[0]), cap))


def render(d):
    css = B.read_css() + PH_CSS
    folio = 2 * int(d['n'])
    # 复用母版渲染，仅替换取图函数
    orig = B.img_tag
    B.img_tag = img_or_ph
    try:
        kid = B.kid_page(d, folio)
        adult = B.adult_page(d, folio + 1)
    finally:
        B.img_tag = orig
    page = (B.head('%s　%s——润泽说·少儿启蒙国学读本' % (d['no_short'], d['line_plain']), d['fav'], css)
            + kid + '\n' + adult + B.TAIL)
    return page


def build_book(css):
    """以十七课合览为底，换封面、续接 18–23 课，重拼二十三课合册。"""
    base = open(os.path.join(ROOT, '三字经·样书·十七课合览.html'), encoding='utf-8').read()
    start = base.index('<div class="page cover">')
    seg = base[start:base.rindex('</body>')]
    rest = seg[seg.index('<div class="page">'):].rstrip()

    pages = []
    B.img_tag = img_or_ph          # 缺图的课在本册同样走占位框
    try:
        for d in LESSONS:
            folio = 2 * int(d['n'])
            pages.append(B.kid_page(d, folio) + B.adult_page(d, folio + 1))
    finally:
        B.img_tag = ORIG
    body = COVER + '\n' + rest + ''.join(
        '\n<!-- 第 %s 课 -->\n%s' % (d['n'], p) for d, p in zip(LESSONS, pages))

    for path, title in [(os.path.join(ROOT, '三字经·样书·二十三课合览.html'), '三字经·二十三课合览（样书 v1.2.1）'),
                        (os.path.join(DOCS, 'book.html'), '三字经·二十三课合览（样书 v1.2.1）')]:
        open(path, 'w', encoding='utf-8').write(B.head(title, '三', css) + body + B.TAIL)
        print('%-46s %8.1f MB' % (os.path.relpath(path, ROOT), os.path.getsize(path) / 1048576))


def main():
    full = '--full' in sys.argv
    made = []
    for d in LESSONS:
        page = render(d)
        out = os.path.join(ROOT, '三字经·%s样张.html' % d['no_short'])
        open(out, 'w', encoding='utf-8').write(page)
        made.append(out)
        if full:
            open(os.path.join(DOCS, 'lesson%s.html' % d['n']), 'w', encoding='utf-8').write(page)
    for p in made:
        print('%-46s %8.1f KB' % (os.path.basename(p), os.path.getsize(p) / 1024))
    if full:
        build_book(B.read_css() + PH_CSS)


if __name__ == '__main__':
    main()
