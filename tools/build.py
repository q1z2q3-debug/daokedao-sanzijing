# -*- coding: utf-8 -*-
"""润泽说·少儿启蒙国学读本《三字经》页面装配器。

用法：
    python3 tools/build.py

职责：
  1. 从既有样张（三字经·第五课样张.html）读取版式 CSS，保证纸墨语言不漂移；
  2. 按 lessons_06_10.py 的内容，生成第 6–10 课样张（少儿页 + 成人页）；
  3. 把第 1–5 课既有页面与新生成的 5 课拼成《十课合览》，并同步 docs/。
"""
import base64
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, '三字经·第五课样张.html')
BOOK_5 = os.path.join(ROOT, '三字经·样书·五课合览.html')
DOCS = os.path.join(ROOT, 'docs')
ASSETS = os.path.join(ROOT, 'assets')

FAV = "<link rel=\"icon\" type=\"image/svg+xml\" href=\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' fill='%23A2503B'/%3E%3Ctext x='32' y='45' font-size='28' text-anchor='middle' fill='%23F8F3E6' font-family='serif'%3E{ch}%3C/text%3E%3C/svg%3E\">"
FONTS = "<link rel=\"stylesheet\" href=\"https://miaoda.feishu.cn/fonts/css2?family=Noto+Serif+SC:wght@400;500;600;700&family=Noto+Sans+SC:wght@300;400;500&display=swap\">"

EXTRA_CSS = ("\n.grid-cols.tight{gap:34px}\n"
             ".tight .grid{width:74px;height:74px}\n"
             ".tight .grid .ch{font-size:44px}\n"
             ".tight .colhead{margin-bottom:0}\n"
             ".tight + .readnote{margin-top:12px}")

CROSS = ('<svg class="cross" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">'
         '<line x1="0" y1="50" x2="100" y2="50"/><line x1="50" y1="0" x2="50" y2="100"/></svg>')


def read_css():
    src = open(REF, encoding='utf-8').read()
    css = re.search(r'<style>\n(.+?)\n</style>', src, re.S).group(1)
    return css


def head(title, fav_char, css):
    return ('<!DOCTYPE html>\n<html lang="zh-Hans">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<title>%s</title>\n%s\n%s\n<style>\n%s%s\n</style>\n</head>\n<body>\n<div class="book">\n'
            % (title, FAV.format(ch=fav_char), FONTS, css, EXTRA_CSS))



TAIL = '\n</div>\n\n</body>\n</html>\n'


def img_tag(fname, alt, cap):
    path = os.path.join(ASSETS, fname)
    data = base64.b64encode(open(path, 'rb').read()).decode()
    return ('<figure>\n      <img src="data:image/jpeg;base64,%s" alt="%s">\n      <figcaption>%s</figcaption>\n    </figure>'
            % (data, alt, cap))


def grid_col(idx, words):
    cells = []
    for (py, ch, strokes) in words:
        cells.append(
            '<div class="cellwrap"><div class="py">%s</div><div class="grid">%s<span class="ch">%s</span></div>'
            '<div class="strokes">%s</div></div>' % (py, CROSS, ch, strokes))
    return ('  <div class="col"><div class="colhead">%s</div>\n    %s\n  </div>'
            % (idx, ''.join(cells)))


def kid_page(d, folio):
    cols = []
    if d.get('col_r'):
        cols = [grid_col('① 先读右列', d['col_r']),
                grid_col('② 再读左列', d['col_l'])]
    body = []
    for block in d['kid']:
        kind = block[0]
        if kind == 'p':
            body.append('    <p>%s</p>' % block[1])
        elif kind == 'lead':
            body.append('    <p class="lead">%s</p>' % block[1])
        elif kind == 'fig':
            body.append('    ' + img_tag(block[1], block[2], block[3]))
    cards = ''.join(
        '    <div class="card">\n      <div class="ch2">%s<span>%s</span></div>\n      <p>%s</p>\n    </div>\n'
        % (c[0], c[1], c[2]) for c in d['cards'])
    takes = ''.join('      <li>%s</li>\n' % t for t in d['takeaways'])
    tips = ''.join('    <p%s>%s</p>\n' % (' style="margin-top:%s"' % s if s else '', t)
                   for (s, t) in d['tips'])
    note2 = ''
    if d.get('note2'):
        note2 = ('\n    <div class="note" style="font-size:12.5px;color:#6B6157">%s</div>'
                 % d['note2'])

    if d.get('grid_split'):
        segs = []
        for i, (rk, r, lk, l, rn) in enumerate(d['grid_split']):
            mt = ' style="margin-top:26px"' if i else ''
            segs.append('  <div class="grid-cols tight"%s>\n%s\n%s\n  </div>\n'
                        '  <div class="readnote">%s</div>' % (mt, grid_col(rk, r), grid_col(lk, l), rn))
        grid_html = ('\n'.join(segs) + '\n    <div class="note">%s</div>%s' % (d['note'], note2))
    else:
        grid_html = ('<div class="grid-cols">\n%s\n%s\n</div>\n'
                     '    <div class="readnote">\n      <span class="ord">先 <b>↓</b> 右列　再 <b>←</b> 左列</span>\n'
                     '      <span>%s</span>\n    </div>\n'
                     '    <div class="note">%s</div>%s'
                     % (cols[0], cols[1], d['readnote'], d['note'], note2))
    return f"""<div class="page">
  <div class="runhead"><span>润泽少儿启蒙国学 · 三字经</span><span class="c">{d['runhead']}</span></div>
  <div class="lesson-no">{d['no_cn']}</div>
  <h1>{d['line']}</h1>
  <div class="sub">{d['pinyin_line']}</div>

  <div class="grid-block">
    {grid_html}
  </div>

  <div class="band"><span class="tag">少儿共读</span><span class="rule"></span><span class="en">读给孩子听</span></div>

  <div class="kid">
{chr(10).join(body)}
  </div>

  <div class="two">
{cards}  </div>

  <div class="takeaway">
    <div class="t">成 长 小 启 示</div>
    <ul>
{takes}    </ul>
  </div>

  <div class="parent-tip">
    <div class="t">{d['tip_title']}</div>
{tips}  </div>

  <div class="folio">— {folio} —</div>
</div>
"""


def adult_page(d, folio):
    secs = []
    for (num, paras) in d['adult']:
        secs.append('  <span class="num">%s</span>\n' % num)
        for p in paras:
            secs.append('  <p>%s</p>\n' % p)
    doubts = ''.join('    <p>%s</p>\n' % x for x in d['doubt'])
    return f"""<div class="adult">
  <div class="runhead" style="border-bottom-color:#DCD0B4"><span>成人研学 · 古今汇观</span><span class="c">{d['no_short']} · 深度页</span></div>
  <h2>{d['h2']}</h2>
  <div class="meta">{d['meta']}</div>

{''.join(secs)}
  <div class="doubt">
    <div class="t">存 疑 · 留 待 深 究</div>
{doubts}  </div>

  <div class="folio" style="color:#B4A88F">— {folio} —</div>
</div>
"""


COVER = """<div class="page cover">
  <div class="s">润 泽 少 儿 启 蒙 国 学</div>
  <h1>三 字 经</h1>
  <div class="t2">一句一故事 · 一图一世界</div>
  <div class="line"></div>
  <div class="info">第一课至第十课　·　人之初　至　子不学<br>亲子共读 4–9 岁　·　每课双页：少儿读本 ／ 成人研学<br>样书　v0.9　·　二〇二六年十一月</div>
</div>
"""


def main(lessons):
    css = read_css()
    new_pages = []
    for i, d in enumerate(lessons):
        folio = 2 * (int(d['n']) )  # 少儿页
        kid = kid_page(d, folio)
        adult = adult_page(d, folio + 1)
        new_pages.append(kid + adult)

        single = head('三字经·%s｜%s（样张）' % (d['no_short'], d['line_plain']), d['fav'], css) + kid + adult + TAIL
        fn = os.path.join(ROOT, '三字经·%s样张.html' % d['no_short'])
        open(fn, 'w', encoding='utf-8').write(single)
        open(os.path.join(DOCS, 'lesson%02d.html' % int(d['n'])), 'w', encoding='utf-8').write(single)
        print('written', os.path.basename(fn))

    # 合册：第 1–5 课直接取各自样张（避免自旧合册转抄造成失同步），第 6–10 课用本次生成页
    first_pages = []
    for cn in ('一', '二', '三', '四', '五'):
        fp = os.path.join(ROOT, '三字经·第%s课样张.html' % cn)
        src = open(fp, encoding='utf-8').read()
        start = src.index('<div class="page">')
        end = src.rindex('</body>')
        seg = src[start:end].rstrip()
        if seg.endswith('</div>'):
            seg = seg[:-len('</div>')].rstrip()
        first_pages.append(seg)

    body = COVER + '\n' + '\n'.join(first_pages) + '\n' + ''.join(
        '\n<!-- 第 %s 课 -->\n%s' % (d['n'], p) for d, p in zip(lessons, new_pages))

    for path, title in [(os.path.join(ROOT, '三字经·样书·十课合览.html'), '三字经·十课合览（样书 v0.9）'),
                        (os.path.join(DOCS, 'book.html'), '三字经·十课合览（样书 v0.9）')]:
        open(path, 'w', encoding='utf-8').write(head(title, '三', css) + body + TAIL)
        print('written', os.path.relpath(path, ROOT))


if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import lessons_06_10 as L
    main(L.LESSONS)
