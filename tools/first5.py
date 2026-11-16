# -*- coding: utf-8 -*-
"""前五课：从合册原页切出单课页，并抽其正文为 md（供 201 制合册收录）。

前五课成稿最早，存于 docs/book.html 的原页（不重排）；本脚本把它切出来，
一是补 docs/lesson01–05.html（原先是 v0.1 样张），二是给合册补正文。
"""
import os, re, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, 'docs')
BOOK = os.path.join(DOCS, 'book.html')
CN = '一二三四五'


def chunks():
    h = open(BOOK, encoding='utf-8').read()
    marks = [m.start() for m in re.finditer(r'<div class="lesson-no">', h)]
    out = []
    for i in range(min(5, len(marks))):
        a = marks[i]
        b = marks[i + 1] if i + 1 < len(marks) else h.rindex('</body>')
        out.append(h[a:b].rstrip())
    return h, out


def standalone(book_html, block, no, name):
    head = book_html[:book_html.index('<body')]
    head = re.sub(r'<title>.*?</title>', '<title>三字经·第%s课 %s（201 制）</title>' % (no, name), head, count=1)
    body = '<body>\n<div class="book">\n' + block + '\n</div>\n</body>\n</html>\n'
    return head + body


def grid_md(block):
    labs = re.findall(r'<div class="colhead">([^<]*)</div>', block)
    cells = re.findall(r'<div class="cellwrap"><div class="py">([^<]*)</div>.*?<span class="ch">([^<]*)</span>.*?<div class="strokes">([^<]*)</div>', block, re.S)
    if not labs or not cells:
        return ''
    n = len(cells) // len(labs)
    lines = ['## 田字格（古法竖排，自右向左，先下右列，先右后左）']
    for i, lab in enumerate(labs):
        grp = cells[i * n:(i + 1) * n]
        w = ' · '.join(c[1] for c in grp)
        py = ' '.join(c[0] for c in grp)
        st = '、'.join(re.sub('画$', '', c[2]) for c in grp)
        side = '右列' if '右' in lab else '左列'
        lines.append('%s：%s（%s）｜笔画：%s' % (side, w, py, st))
    return '\n'.join(lines)


def md_block(block):
    grid = grid_md(block)
    block = re.sub(r'<div class="cellwrap">.*?</div>\s*</div>\s*</div>', '', block, flags=re.S)
    p = re.sub(r'<(script|style|svg).*?</\1>', '', block, flags=re.S)
    p = re.sub(r'<div class="band"><span class="tag">([^<]*)</span>.*?</div>', r'\n\n## \1\n\n', p, flags=re.S)
    p = re.sub(r'<div class="t">([^<]*)</div>', r'\n\n## \1\n\n', p)
    p = re.sub(r'<div class="h3sub">([^<]*)</div>', r'\n*（\1）*\n', p)
    p = re.sub(r'<div class="gn">([^<]*)</div>', r'\n**\1**', p)
    p = re.sub(r'<h3>([^<]*)</h3>', r'\n\n### \1\n\n', p)
    p = re.sub(r'<h2>([^<]*)</h2>', r'\n\n## \1\n\n', p)
    p = re.sub(r'<h1>([^<]*)</h1>', r'\n\n# \1\n\n', p)
    p = re.sub(r'<figcaption>([^<]*)</figcaption>', r'\n（图：\1）\n', p)
    p = re.sub(r'<li>', '\n- ', p)
    p = re.sub(r'<div class="colhead">([^<]*)</div>', r'', p)
    p = re.sub(r'</div>|</p>|</li>|<br\s*/?>|</tr>|</table>', '\n', p)
    p = re.sub(r'<[^>]+>', '', p)
    p = html.unescape(p)
    out = []
    for ln in p.split('\n'):
        s = re.sub(r'\s+', ' ', ln).strip()
        if not s:
            if out and out[-1] != '':
                out.append('')
            continue
        if s.startswith('润泽少儿启蒙国学'):
            continue
        if re.match(r'第 [一二三四五] 课$', s):
            continue
        if s.startswith('先') and '右列' in s and '左列' in s and len(s) < 24:
            continue
        if re.match(r'—\s*\d+\s*—$', s):
            continue
        s = re.sub(r'^([一二三四五]) · ', r'### \1 · ', s)
        out.append(s)
    t = '\n'.join(out).strip()
    t = re.sub(r'\n{3,}', '\n\n', t)
    t = re.sub(r'##\s*存 疑 · 留 待 深 究', '## 存疑', t)
    t = grid + '\n\n' + t
    t = re.sub(r'\n\n成人研学 · 古今汇观(.{0,20})', '\n\n## 成人研学 · 古今汇观\n', t)
    return t


def run():
    book_html, cs = chunks()
    mds = []
    for i, c in enumerate(cs, 1):
        no = CN[i - 1]
        m = re.search(r'<h1>([^<]*)</h1>', c)
        name = m.group(1).rstrip('。') if m else ''
        page = standalone(book_html, c, no, name)
        out = os.path.join(DOCS, 'lesson%02d.html' % i)
        open(out, 'w', encoding='utf-8').write(page)
        md = md_block(c)
        title = '# 第%s课 %s' % (['一', '二', '三', '四', '五'][i - 1], name)
        m = re.search(r'(?m)^# [^\n]*$', md)
        if m:
            grid = md[:m.start()].strip()
            rest = md[m.end():].lstrip('\n')
            rest = re.sub(r'^[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜüńňǹ ]+[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜüńňǹ ]*\n+', '', rest, count=1)
            md = title + '\n\n' + grid + '\n\n' + rest
        else:
            md = title + '\n\n' + md
        mds.append(md)
    return mds


if __name__ == '__main__':
    for m in run():
        print(m[:60], '...')
